/**
 * MGVaovao — real-time audio streaming client.
 *
 * Architecture:
 *   getUserMedia → AudioContext (16 kHz) → AudioWorklet
 *   → accumulate 512-sample chunks → WebSocket binary frames
 *   ← VAD state JSON ← processing JSON ← result JSON
 */

"use strict";

// ── Config ────────────────────────────────────────────────────────────────────
const CHUNK_SAMPLES = 512;   // Silero VAD requirement
const TARGET_SR     = 16000; // Hz — must match server

// ── State ─────────────────────────────────────────────────────────────────────
let ws        = null;
let audioCtx  = null;
let micStream = null;
let worklet   = null;
let recording = false;
let sampleBuf = new Float32Array(0); // inter-chunk accumulator

// ── Inactivity timeout ────────────────────────────────────────────────────────
const INACTIVITY_MS  = 5 * 60 * 1000; // 5 min sans parole → déconnexion + modal
let lastSpeechTime   = 0;
let inactivityTimer  = null;
let disconnectReason = "manual"; // "manual" | "inactivity"

// ── DOM refs (populated in init()) ───────────────────────────────────────────
let btnToggle, selDialect, selSrcLang, selAge, selGender;
let elVariantNotice;
let elState, elProb, elTranscript, elTranslation, elLatency, elLog;
let elLoadingOverlay, elLoadingMsg, elProcessingBanner, elSpeakerAnim;
let elWelcomeModal, elWelcomeBody, elBtnStart;

// ── WebSocket ──────────────────────────────────────────────────────────────────

// Plateforme de collecte : le lien de retour depuis la demonstration.
const COLLECTE_URL = "https://kozy.mg";

/**
 * URL de session, portant la combinaison choisie.
 *
 * Les quatre axes voyagent ensemble : dialecte de sortie, langue d'entree,
 * tranche d'age et sexe de la voix. C'est la combinaison, et non le dialecte
 * seul, qui designe ce qu'une entreprise commanderait.
 */
function wsUrl(dialect, srcLang, age, gender) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const q = new URLSearchParams();
  if (srcLang !== "auto") q.set("src_lang", srcLang);
  if (age) q.set("age_range", age);
  if (gender) q.set("gender", gender);
  const suffixe = q.toString() ? `?${q.toString()}` : "";
  return `${proto}://${location.host}/ws/stream/${dialect}${suffixe}`;
}

function connect() {
  const dialect = selDialect.value;
  const srcLang = selSrcLang.value;
  const age     = selAge ? selAge.value : "";
  const gender  = selGender ? selGender.value : "";

  log(`Connexion [dialecte=${dialect} entree=${srcLang} age=${age || "tous"} sexe=${gender || "tous"}]…`);
  ws = new WebSocket(wsUrl(dialect, srcLang, age, gender));

  ws.onopen    = () => { log("Connecté"); startMic(); };
  ws.onmessage = (e) => handleMessage(JSON.parse(e.data));
  ws.onclose   = (e) => {
    log(`Déconnecté (${e.code})`);
    stopMic();
    setBtn(false);
    elProcessingBanner.classList.remove("visible");
    elSpeakerAnim.classList.remove("active");
    // Sans cette remise a zero, une deconnexion survenue pendant la lecture
    // laissait le drapeau leve : la session suivante s'ouvrait en se croyant
    // en train de parler, et n'affichait plus jamais « En ecoute… ».
    enLecture = false;
    if (disconnectReason === "inactivity") {
      showWelcomeModal(true);
      disconnectReason = "manual";
    }
  };
  ws.onerror   = ()  => log("Erreur WebSocket");
}

function disconnect() {
  ws?.close();
}

// ── Message handler ───────────────────────────────────────────────────────────

/**
 * Vrai tant que le serveur joue sa réponse et n'écoute donc pas.
 *
 * Il suit le message `turn` du serveur, qui fait autorité : l'interface le
 * devinait de son côté, et se trompait.
 */
let enLecture = false;

function handleMessage(msg) {
  switch (msg.type) {
    case "vad":
      updateVAD(msg.state, msg.prob);
      break;

    case "processing":
      elState.textContent = "Traitement…";
      elState.className   = "state processing";
      elProcessingBanner.classList.add("visible");
      break;

    case "result":
      elProcessingBanner.classList.remove("visible");
      elTranscript.textContent  = msg.source_text  || "—";
      elTranslation.textContent = msg.malagasy_text || "—";
      renderLatency(msg.latency_ms);
      playAudio(msg.audio_b64);
      ["box-transcript", "box-translation"].forEach((id) => {
        const el = document.getElementById(id);
        el.classList.add("updated");
        setTimeout(() => el.classList.remove("updated"), 1500);
      });
      // Surtout pas « En écoute… » ici : le serveur passe en SPEAKING dès
      // qu'il envoie ce résultat, et ignore tout l'audio jusqu'à la fin de la
      // lecture. L'annoncer à l'écoute invitait à parler dans le vide.
      enLecture = true;
      elState.textContent = "Réponse en cours de lecture…";
      elState.className   = "state speaking";
      log(`Résultat — ${msg.latency_ms.total} ms total`);
      break;

    // Le serveur annonce lui-même son tour de parole. S'en remettre à lui
    // plutôt que de le deviner : l'interface et le serveur se contredisaient,
    // et c'est l'interface qui avait tort.
    case "turn":
      enLecture = msg.state === "speaking";
      if (msg.state === "listening") {
        elState.textContent = "En écoute…";
        elState.className   = "state listening";
      } else if (msg.state === "speaking") {
        elState.textContent = "Réponse en cours de lecture…";
        elState.className   = "state speaking";
      } else if (msg.state === "processing") {
        elState.textContent = "Traitement…";
        elState.className   = "state processing";
      }
      break;

    // Le serveur previent qu'il charge encore ses modeles sur le GPU. Sans ce
    // cas, la session restait muette une quarantaine de secondes au demarrage
    // a froid et donnait l'impression que rien n'etait envoye.
    // Le serveur confirme la combinaison qu'il sert. C'est lui qui fait foi :
    // il elargit la demande quand la combinaison exacte n'existe pas, et
    // l'ecran doit montrer ce qui repond, pas ce qui a ete demande.
    case "variant":
      log(
        `Declinaison servie : ${msg.id || "inconnue"}` +
          (msg.modele_propre ? " (modele propre)" : " (modele general)")
      );
      if (elVariantNotice && !msg.modele_propre) {
        elVariantNotice.textContent =
          "Aucun modele n'est encore entraine pour cette combinaison : le modele general repond, " +
          "la voix ne sera donc ni de cette tranche d'age ni de ce sexe.";
      }
      break;

    case "loading":
      log(msg.message || "Chargement des modeles…");
      elState.textContent = "Chargement des modèles…";
      elState.className   = "state";
      break;

    case "error":
      log(`Error: ${msg.message}`);
      elState.textContent = "Error";
      elState.className   = "state error";
      break;
  }
}

// ── VAD indicator ─────────────────────────────────────────────────────────────

function updateVAD(state, prob) {
  elProb.style.width = `${Math.round(prob * 100)}%`;
  elProb.style.background = prob > 0.5 ? "#22c55e" : "#64748b";

  switch (state) {
    case "speaking":
      elState.textContent = "Parole détectée";
      elState.className   = "state speaking";
      lastSpeechTime = Date.now();
      break;
    case "trailing":
      elState.textContent = "Fin de parole…";
      elState.className   = "state trailing";
      break;
    default:
      // Pendant la lecture de la réponse, le serveur ignore l'audio : repasser
      // l'affichage à « En écoute… » sur une trame VAD contredirait le tour en
      // cours et ramènerait le défaut que l'on vient de corriger.
      //
      // Un drapeau, et non la classe CSS : « state speaking » sert aussi à
      // l'indicateur VAD quand c'est la PERSONNE qui parle. S'appuyer dessus
      // aurait figé l'indicateur dès le premier mot prononcé.
      if (elState.className !== "state processing" && !enLecture) {
        elState.textContent = "En écoute…";
        elState.className   = "state listening";
      }
  }
}

// ── Microphone / AudioWorklet ─────────────────────────────────────────────────

async function startMic() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
      video: false,
    });

    // Request 16 kHz; browser may not honour it — server handles resampling if needed
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: TARGET_SR });

    await audioCtx.audioWorklet.addModule("/live/audio-processor.js");
    worklet = new AudioWorkletNode(audioCtx, "mgvaovao-audio-processor");

    worklet.port.onmessage = (e) => sendChunk(new Float32Array(e.data));

    const source = audioCtx.createMediaStreamSource(micStream);
    source.connect(worklet);
    // Do NOT connect worklet to destination — avoid mic feedback

    recording = true;
    setBtn(true);
    elState.textContent = "En écoute…";
    elState.className   = "state listening";
    log(`Micro actif (${audioCtx.sampleRate} Hz)`);
    startInactivityTimer();
  } catch (err) {
    log(`Erreur micro : ${err.message}`);
    disconnect();
  }
}

function stopMic() {
  stopInactivityTimer();
  recording = false;
  worklet?.disconnect();
  worklet = null;
  micStream?.getTracks().forEach((t) => t.stop());
  micStream = null;
  audioCtx?.close();
  audioCtx  = null;
  sampleBuf = new Float32Array(0);
  elState.textContent = "Arrêté";
  elState.className   = "state idle";
}

// ── Audio chunking ────────────────────────────────────────────────────────────

function sendChunk(samples) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  // Append to accumulator
  const merged = new Float32Array(sampleBuf.length + samples.length);
  merged.set(sampleBuf);
  merged.set(samples, sampleBuf.length);

  let offset = 0;
  while (offset + CHUNK_SAMPLES <= merged.length) {
    const chunk = merged.slice(offset, offset + CHUNK_SAMPLES);
    ws.send(chunk.buffer);
    offset += CHUNK_SAMPLES;
  }
  sampleBuf = merged.slice(offset); // keep remainder
}

// ── Audio playback ────────────────────────────────────────────────────────────

/**
 * Joue la reponse synthetisee, puis rend la parole au serveur.
 *
 * Le protocole attend `playback_finished` a la fin de la lecture : tant qu'il
 * ne l'a pas recu, le serveur reste en SPEAKING et jette tout l'audio entrant,
 * pour ne pas reprendre dans le micro la voix qu'il est en train de jouer.
 *
 * Ce message n'etait jamais envoye. Le serveur attendait alors son delai de
 * garde — soixante secondes — avant de reecouter, pendant que l'interface
 * affichait « En ecoute… ». La deuxieme phrase de la personne partait donc
 * dans le vide, sans que rien ne l'indique.
 *
 * Il est envoye sur les trois issues possibles, y compris les echecs : une
 * lecture qui n'aboutit pas ne doit pas rendre la session sourde. Un drapeau
 * garantit un envoi unique, `onended` et `onerror` pouvant se suivre.
 */
function playAudio(b64) {
  const bytes  = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const blob   = new Blob([bytes], { type: "audio/wav" });
  const url    = URL.createObjectURL(blob);
  const player = new Audio(url);

  let rendu = false;
  const rendreLaParole = () => {
    if (rendu) return;
    rendu = true;
    URL.revokeObjectURL(url);
    elSpeakerAnim.classList.remove("active");
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "playback_finished" }));
    }
  };

  elSpeakerAnim.classList.add("active");
  player.onended = rendreLaParole;
  player.onerror = () => {
    log("Lecture de la reponse impossible.");
    rendreLaParole();
  };
  player.play().catch((e) => {
    log(`Erreur lecture : ${e.message}`);
    rendreLaParole();
  });
}

// ── Latency table ─────────────────────────────────────────────────────────────

function renderLatency(lms) {
  const rows = [
    ["VAD",         lms.vad],
    ["ASR",         lms.asr],
    ["Translation", lms.translation],
    ["TTS",         lms.tts],
    ["Total",       lms.total],
  ];
  elLatency.innerHTML = rows
    .filter(([, v]) => v != null)
    .map(([k, v]) => `<tr><td>${k}</td><td>${v} ms</td></tr>`)
    .join("");
}

// ── Button & log helpers ──────────────────────────────────────────────────────

function setBtn(active) {
  btnToggle.textContent = active ? "⏹ Arrêter l'écoute" : "🎙 Reprendre l'écoute";
  btnToggle.classList.toggle("active", active);
  selDialect.disabled = active;
  // Les axes de la declinaison sont figes pendant l'enregistrement : les
  // changer en cours de session ne changerait rien au modele deja charge, et
  // l'ecran mentirait sur ce qui repond.
  if (selSrcLang) selSrcLang.disabled = active;
  if (selAge) selAge.disabled = active;
  if (selGender) selGender.disabled = active;
  selSrcLang.disabled = active;
}

function log(msg) {
  const ts = new Date().toLocaleTimeString();
  elLog.textContent = `[${ts}] ${msg}\n` + elLog.textContent.slice(0, 2000);
}

// ── Dialect list fetch ────────────────────────────────────────────────────────

async function loadDialects() {
  try {
    const res  = await fetch("/dialects/");
    const list = await res.json();
    window.__dialects = list;

    // « no model » ne disait pas ce qui se passait quand on le choisissait
    // quand meme. Chaque dialecte reste selectionnable, mais l'intitule dit
    // desormais quel modele repond reellement — sans quoi la demonstration
    // ferait passer du malgache officiel pour du dialecte.
    selDialect.innerHTML = list.map((d) => {
      const suffixe = d.model_ready ? "" : " — modele generique";
      return `<option value="${d.code}">${d.name}${suffixe}</option>`;
    }).join("");

    majAvertissementModele();
  } catch {
    // keep hardcoded fallback options already in HTML
  }
}

/**
 * Dit, sous le selecteur, ce que le modele choisi sait reellement faire.
 *
 * Aucun modele dialectal n'est encore entraine : tous les dialectes sont
 * servis par le modele de malgache officiel. Le taire donnerait l'impression
 * que la restitution entendue est ce que le projet produira, alors qu'elle
 * ne reflete que le point de depart.
 */
function majAvertissementModele() {
  const zone = document.getElementById("model-notice");
  if (!zone) return;
  const liste = window.__dialects || [];
  const d = liste.find((x) => x.code === selDialect.value);
  if (!d) { zone.textContent = ""; return; }

  const volume = (d.recordings || 0) + (d.translations || 0);
  const collecte = volume
    ? `${volume.toLocaleString("fr-FR")} contributions deja collectees pour ce dialecte.`
    : "Aucune contribution collectee pour ce dialecte a ce jour.";

  if (d.model_ready) {
    zone.innerHTML = `<strong>Modele dedie.</strong> ${collecte} ` +
      `La qualite continuera de progresser a mesure que le corpus grandit.`;
  } else {
    zone.innerHTML = `<strong>Modele generique.</strong> Aucun modele propre a ce ` +
      `dialecte n'est encore entraine : c'est le modele de malgache officiel qui ` +
      `repond, la restitution ne sera donc pas dialectale. ${collecte} ` +
      `<a href="${COLLECTE_URL}" target="_blank" rel="noopener">Contribuer</a> ` +
      `accelere directement l'entrainement.`;
  }
}

// ── Inactivity watchdog ───────────────────────────────────────────────────────

function startInactivityTimer() {
  lastSpeechTime = Date.now();
  stopInactivityTimer();
  inactivityTimer = setInterval(() => {
    if (!recording) return;
    if (Date.now() - lastSpeechTime >= INACTIVITY_MS) {
      log("5 min sans parole — déconnexion automatique pour économiser Cloud Run.");
      disconnectReason = "inactivity";
      disconnect();
    }
  }, 30_000); // vérification toutes les 30 s
}

function stopInactivityTimer() {
  if (inactivityTimer) {
    clearInterval(inactivityTimer);
    inactivityTimer = null;
  }
}

// ── Welcome modal ─────────────────────────────────────────────────────────────

function showWelcomeModal(isInactivity = false) {
  if (isInactivity) {
    elWelcomeBody.innerHTML =
      "Aucune parole détectée depuis <strong>5 minutes</strong>.<br>" +
      "L'écoute a été suspendue pour économiser les ressources.";
    elBtnStart.textContent = "🎙️ Reprendre";
  } else {
    elWelcomeBody.innerHTML =
      "Parlez en français, anglais, espagnol ou allemand.<br>" +
      "L'IA traduit automatiquement en <strong>malgache</strong> en temps réel.";
    elBtnStart.textContent = "🎙️ Commencer";
  }
  elWelcomeModal.classList.remove("hidden");
}

function hideWelcomeModal() {
  elWelcomeModal.classList.add("hidden");
}

// ── Ready polling ─────────────────────────────────────────────────────────────

async function checkReady() {
  try {
    const res = await fetch("/ready");
    if (res.ok) {
      elLoadingOverlay.classList.add("hidden");
      btnToggle.disabled = false;
      log("Modèles chargés — prêt.");
      showWelcomeModal(false);
    } else {
      elLoadingMsg.textContent = "Chargement des modèles en cours…";
      setTimeout(checkReady, 3000);
    }
  } catch {
    setTimeout(checkReady, 3000);
  }
}

// ── Declinaisons ──────────────────────────────────────────────────────────────

/** Registre des combinaisons, tel que la plateforme de collecte le publie. */
let declinaisons = { axes: {}, variants: [] };

const LIBELLE_SEXE = { FEMALE: "Feminine", MALE: "Masculine" };

/**
 * Peuple les selecteurs d'age et de sexe depuis le registre.
 *
 * Les valeurs ne sont pas ecrites dans la page : ce sont les categories du
 * CRUD de collecte qui les decident, et en figer une liste ici la ferait
 * diverger au premier ajout.
 */
async function chargerDeclinaisons() {
  try {
    const res = await fetch("/variants/");
    if (!res.ok) throw new Error(String(res.status));
    declinaisons = await res.json();
  } catch (e) {
    log("Registre des declinaisons indisponible — axes de voix desactives.");
    return;
  }

  const remplir = (el, valeurs, libelleTout) => {
    if (!el) return;
    el.innerHTML = "";
    const tout = document.createElement("option");
    tout.value = "";
    tout.textContent = libelleTout;
    el.appendChild(tout);
    for (const v of valeurs) {
      const o = document.createElement("option");
      o.value = v.id;
      o.textContent = v.nom;
      el.appendChild(o);
    }
  };

  remplir(selAge, declinaisons.axes?.tranchesAge || [], "Toutes");
  remplir(
    selGender,
    (declinaisons.axes?.sexes || []).map((s) => ({
      id: s.id,
      nom: LIBELLE_SEXE[s.id] || s.nom,
    })),
    "Tous"
  );
  majAvertissementDeclinaison();
}

/** La combinaison actuellement selectionnee, si le registre la connait. */
function declinaisonChoisie() {
  const dialecte = selDialect?.value;
  const langue = selSrcLang?.value === "auto" ? null : selSrcLang?.value;
  const age = selAge?.value || null;
  const sexe = selGender?.value || null;
  return (declinaisons.variants || []).find(
    (v) =>
      v.dialecte === dialecte &&
      (!langue || v.langue === langue) &&
      v.trancheAge === age &&
      v.sexe === sexe
  );
}

/**
 * Dit ce que la combinaison choisie vaut aujourd'hui.
 *
 * Deux informations, et les deux comptent : le corpus reellement collecte
 * pour cette combinaison, et si un modele lui est propre. Aucun ne l'est
 * encore — le dire evite de faire passer une demonstration generique pour une
 * voix sur mesure, ce qui se verrait a la premiere ecoute.
 */
function majAvertissementDeclinaison() {
  if (!elVariantNotice) return;
  const v = declinaisonChoisie();
  if (!v) {
    elVariantNotice.textContent =
      "Cette combinaison n'est pas encore enregistree : la demonstration repondra avec le modele general.";
    return;
  }
  const c = v.corpus || {};
  const minutes = Math.round((c.secondesAudio || 0) / 60);
  const corpus =
    (c.traductions || 0) === 0 && minutes === 0
      ? "Aucune donnee collectee pour cette combinaison a ce jour."
      : `${(c.traductions || 0).toLocaleString("fr-FR")} traductions et ${minutes} min de voix collectees pour cette combinaison.`;
  elVariantNotice.textContent = v.modele?.propre
    ? `Modele propre a cette combinaison. ${corpus}`
    : `Aucun modele n'est encore entraine pour cette combinaison : le modele general repond, la voix ne sera donc ni de cette tranche d'age ni de ce sexe. ${corpus}`;
}

// ── Init ──────────────────────────────────────────────────────────────────────

function init() {
  btnToggle        = document.getElementById("btn-toggle");
  selDialect       = document.getElementById("sel-dialect");
  selSrcLang       = document.getElementById("sel-src-lang");
  selAge           = document.getElementById("sel-age");
  selGender        = document.getElementById("sel-gender");
  elVariantNotice  = document.getElementById("variant-notice");
  elState          = document.getElementById("el-state");
  elProb           = document.getElementById("el-prob");
  elTranscript     = document.getElementById("el-transcript");
  elTranslation    = document.getElementById("el-translation");
  elLatency        = document.getElementById("el-latency");
  elLog            = document.getElementById("el-log");
  elLoadingOverlay   = document.getElementById("loading-overlay");
  elLoadingMsg       = document.getElementById("loading-msg");
  elProcessingBanner = document.getElementById("processing-banner");
  elSpeakerAnim      = document.getElementById("speaker-anim");
  elWelcomeModal     = document.getElementById("welcome-modal");
  elWelcomeBody      = document.getElementById("welcome-body");
  elBtnStart         = document.getElementById("btn-start");

  // L'avertissement suit le dialecte choisi : sans cet ecouteur, il resterait
  // celui du premier dialecte et mentirait des le second clic.
  selDialect.addEventListener("change", majAvertissementModele);

  // Les quatre axes decrivent une seule combinaison : changer l'un d'eux
  // change ce que vaut la declinaison, donc ce qu'il faut afficher.
  [selDialect, selSrcLang, selAge, selGender].forEach((el) => {
    if (el) el.addEventListener("change", majAvertissementDeclinaison);
  });
  void chargerDeclinaisons();

  elBtnStart.addEventListener("click", () => {
    hideWelcomeModal();
    connect();
  });

  btnToggle.addEventListener("click", () => {
    if (!recording) {
      hideWelcomeModal();
      connect();
    } else {
      disconnect();
    }
  });

  loadDialects();
  checkReady();
}

document.addEventListener("DOMContentLoaded", init);
