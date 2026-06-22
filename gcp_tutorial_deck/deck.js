/* MGVaovao — Tutoriel GCP DÉTAILLÉ (step-by-step)
 * Fichier généré : MGVaovao_Tutoriel_GCP_FR.pptx
 * Contenu : toute l'information du README + doc officielle de chaque service.
 * Chaque composant : concepts + configuration pas-à-pas + service accounts.
 */
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" x 7.5"
pres.author = "MGVaovao";
pres.title = "Tutoriel GCP détaillé — MGVaovao";

const W = 13.33, H = 7.5;
const INK = "1B2A4A", INK2 = "26365C", BG = "F4F6FB", TEXT = "202124", MUTED = "5F6368";
const CARD = "FFFFFF", CODEBG = "0E1A33", CODET = "DCE3F2", CMT = "7F8CA8", TINT = "EEF2FB";
const A = {
  blue:   { s: "4285F4", l: "8AB4F8", d: "1A73E8" },
  red:    { s: "EA4335", l: "F28B82", d: "C5221F" },
  green:  { s: "34A853", l: "81C995", d: "1E8E3E" },
  purple: { s: "9334E6", l: "C58AF9", d: "8430CE" },
  amber:  { s: "F9AB00", l: "FDD663", d: "B06000" },
  teal:   { s: "12B5CB", l: "78D9E6", d: "0E7C8B" },
  slate:  { s: "5B6B8C", l: "C7D0E4", d: "3C4A66" },
};
const L = {
  run: "01_cloud_run.png", gpu: "02_cloud_run_gpu.png", storage: "03_cloud_storage.png",
  vertex: "04_vertex_ai.png", build: "05_cloud_build.png", artifact: "06_artifact_registry.png",
  pubsub: "07_pubsub.png", logging: "08_cloud_logging.png", monitoring: "09_cloud_monitoring.png",
  iam: "10_iam.png", compute: "11_compute_engine.png", secret: "12_secret_manager.png",
};
const GCPLOGO = "00_gcp.png";
const MDN = "logo_mdn.png";
const NAME = "Tsantaniaina Rakotonjanahary Ambaorasoa Guillaume";
const LOGO = (f) => `logos/${f}`;
const shadow = () => ({ type: "outer", color: "8A94AD", blur: 7, offset: 3, angle: 90, opacity: 0.26 });

// ---------- primitives ----------
// --- watermark anti-collision : un seul, horizontal, dans une zone VIDE ---
const SLIDES = [];
// bbox réaliste d'un bloc de texte (largeur selon contenu + alignement, hauteur selon lignes)
function bboxText(t, o) {
  const fs = (Array.isArray(t) && t[0] && t[0].options && t[0].options.fontSize) || o.fontSize || 13;
  const cw = fs / 72 * 0.52;
  let lines, w;
  if (Array.isArray(t)) { lines = Math.max(1, t.filter((r) => r && r.options && r.options.breakLine).length + 1); w = o.w || 3; }
  else { const usable = Math.max(8, (o.w || 4) / cw); lines = Math.max(1, Math.ceil(String(t).length / usable)); w = lines > 1 ? (o.w || 4) : Math.min(o.w || 99, String(t).length * cw + 0.12); }
  const h = Math.min(o.h || 9, Math.max(0.24, lines * (fs / 72 * 1.6) + 0.1));
  let x = o.x;
  if (o.align === "center") x = o.x + ((o.w || w) - w) / 2;
  else if (o.align === "right") x = o.x + ((o.w || w) - w);
  return { x, y: o.y, w, h };
}
// enregistre la bbox de chaque élément ajouté à la slide
function track(s) {
  s.__boxes = [];
  const _t = s.addText.bind(s); s.addText = (t, o) => { if (o && typeof o.x === "number") s.__boxes.push(bboxText(t, o)); return _t(t, o); };
  const _sh = s.addShape.bind(s); s.addShape = (ty, o) => { if (o && typeof o.x === "number") s.__boxes.push({ x: o.x, y: o.y, w: o.w || 0.3, h: o.h || 0.3 }); return _sh(ty, o); };
  const _im = s.addImage.bind(s); s.addImage = (o) => { if (o && typeof o.x === "number") s.__boxes.push({ x: o.x, y: o.y, w: o.w || 0.5, h: o.h || 0.5 }); return _im(o); };
  const _tb = s.addTable.bind(s); s.addTable = (r, o) => { if (o) s.__boxes.push({ x: o.x, y: o.y, w: o.w || 4, h: o.h || (r ? r.length * 0.4 + 0.1 : 1) }); return _tb(r, o); };
}
function slide(theme) {
  const s = pres.addSlide();
  s.background = { color: theme === "dark" ? INK : BG };
  track(s);
  SLIDES.push({ s, theme });
  return s;
}
// place le filigrane dans une BANDE HORIZONTALE entièrement vide (sa propre ligne)
const WM_W = 3.3, WM_H = 0.16;
function placeWatermark(s, idx) {
  const Y0 = 1.26, Y1 = 7.0;
  // intervalles en Y occupés par le contenu (le badge en bas à droite est exclu : hors zone du filigrane)
  let iv = s.__boxes
    .filter((b) => b.x < 11.5 && b.w >= 0.3 && b.h <= 5)   // ignore barres fines/pleine hauteur (déco) & badge
    .map((b) => [Math.max(Y0, b.y), Math.min(Y1, b.y + b.h)])
    .filter(([a, b]) => b > a)
    .sort((p, q) => p[0] - q[0]);
  const merged = [];
  for (const [a, b] of iv) {
    if (merged.length && a <= merged[merged.length - 1][1] + 0.02) merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b);
    else merged.push([a, b]);
  }
  const gaps = []; let cur = Y0;
  for (const [a, b] of merged) { if (a - cur > 0.02) gaps.push([cur, a]); cur = Math.max(cur, b); }
  if (Y1 - cur > 0.02) gaps.push([cur, Y1]);
  // on choisit TOUJOURS la plus grande bande vide (clairance maximale) ; la position varie via le slot x
  const g = gaps.reduce((m, x) => (x[1] - x[0] > m[1] - m[0] ? x : m), gaps[0] || [Y1 - WM_H, Y1]);
  const wy = (g[0] + g[1]) / 2 - WM_H / 2;                                    // centré verticalement dans la bande
  const xslots = [0.6, 2.3, 4.0, 5.7].filter((x) => x + WM_W <= 11.3);
  const wx = xslots[idx % xslots.length];                                     // position horizontale variable
  return [wx, wy];
}
function stampLogos() {
  // dessinés EN DERNIER => au-dessus du contenu, dans une zone vide, sur chaque page
  SLIDES.forEach(({ s, theme }, idx) => {
    const [wx, wy] = placeWatermark(s, idx);
    s.addText(NAME, { x: wx, y: wy, w: 3.5, h: 0.2, fontFace: "Calibri", fontSize: 8.5, bold: true, color: theme === "dark" ? "8190AE" : "97A1B5", margin: 0 });
    // badge Maison du Numérique (agrandi)
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 12.18, y: 6.4, w: 1.0, h: 1.0, rectRadius: 0.1, fill: { color: "FFFFFF" }, line: { color: "D6DEEC", width: 1 }, shadow: shadow() });
    s.addImage({ path: LOGO(MDN), x: 12.29, y: 6.51, w: 0.78, h: 0.78 });
  });
}
function gcpChip(s, x, y, w) {
  const ww = w || 2.4, hh = ww * 149 / 960;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: ww + 0.34, h: hh + 0.28, rectRadius: 0.06, fill: { color: "FFFFFF" }, shadow: shadow() });
  s.addImage({ path: LOGO(GCPLOGO), x: x + 0.17, y: y + 0.14, w: ww, h: hh });
}
function header(s, title, sub, acc, logoFile, part) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.16, h: H, fill: { color: acc.s } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.16, y: 0, w: W - 0.16, h: 1.18, fill: { color: INK } });
  s.addText((sub || "").toUpperCase(), { x: 0.6, y: 0.2, w: 10.5, h: 0.32, fontFace: "Calibri", fontSize: 12, bold: true, color: acc.l, charSpacing: 1.5, margin: 0 });
  s.addText(title, { x: 0.58, y: 0.48, w: 10.6, h: 0.62, fontFace: "Georgia", fontSize: 27, bold: true, color: "FFFFFF", margin: 0 });
  if (part) s.addText(part, { x: 9.0, y: 0.2, w: 2.0, h: 0.3, fontFace: "Calibri", fontSize: 10.5, bold: true, color: "8FA0C4", align: "right", charSpacing: 1, margin: 0 });
  if (logoFile) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 11.95, y: 0.26, w: 0.66, h: 0.66, rectRadius: 0.08, fill: { color: "FFFFFF" } });
    s.addImage({ path: LOGO(logoFile), x: 12.02, y: 0.33, w: 0.52, h: 0.52 });
  }
  return s;
}
function lbl(s, x, y, text, acc, w, size) {
  s.addText(text, { x, y, w: w || 6, h: 0.3, fontFace: "Calibri", fontSize: size || 13, bold: true, color: acc.d, charSpacing: 1, margin: 0 });
}
function para(s, x, y, w, h, text, size) {
  s.addText(text, { x, y, w, h, fontFace: "Calibri", fontSize: size || 13.5, color: TEXT, valign: "top", margin: 0 });
}
function bullets(s, x, y, w, h, arr, size) {
  s.addText(arr.map((t) => ({ text: t, options: { bullet: { indent: 15 }, breakLine: true, paraSpaceAfter: 6, fontFace: "Calibri", fontSize: size || 13, color: TEXT } })),
    { x, y, w, h, valign: "top", margin: 0 });
}
function codeBox(s, x, y, w, h, code, size) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: CODEBG }, shadow: shadow() });
  const runs = code.split("\n").map((line) => {
    const isCmt = line.trim().startsWith("#");
    return { text: line.length ? line : " ", options: { breakLine: true, fontFace: "Consolas", fontSize: size || 10, color: isCmt ? CMT : CODET } };
  });
  s.addText(runs, { x: x + 0.18, y: y + 0.12, w: w - 0.36, h: h - 0.24, valign: "top", margin: 0 });
}
function callout(s, x, y, w, h, heading, text, acc) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: TINT } });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.1, h, fill: { color: acc.s } });
  s.addText([
    { text: heading + "   ", options: { fontFace: "Calibri", fontSize: 11, bold: true, color: acc.d } },
    { text: text, options: { fontFace: "Calibri", fontSize: 12, color: TEXT } },
  ], { x: x + 0.26, y: y + 0.08, w: w - 0.42, h: h - 0.16, valign: "middle", margin: 0 });
}
function steps(s, x, y, w, items, acc, gap, size) {
  const g = gap || 0.92;
  items.forEach((it, i) => {
    const yy = y + i * g;
    s.addShape(pres.shapes.OVAL, { x, y: yy, w: 0.42, h: 0.42, fill: { color: acc.s } });
    s.addText(String(it.n != null ? it.n : i + 1), { x, y: yy, w: 0.42, h: 0.42, fontFace: "Calibri", fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
    s.addText([
      { text: it.t + (it.d ? "\n" : ""), options: { fontFace: "Calibri", fontSize: size || 13.5, bold: true, color: TEXT, breakLine: !!it.d } },
      it.d ? { text: it.d, options: { fontFace: "Calibri", fontSize: 11.5, color: MUTED } } : { text: "" },
    ], { x: x + 0.58, y: yy - 0.06, w: w - 0.58, h: g, valign: "top", margin: 0 });
  });
}
function footer(s, text) {
  s.addText(text, { x: 0.6, y: 7.12, w: 12.2, h: 0.3, fontFace: "Calibri", fontSize: 9.5, italic: true, color: MUTED, margin: 0 });
}
function table(s, x, y, w, headers, rows, acc, colW, fs) {
  const head = headers.map((h) => ({ text: h, options: { fill: { color: acc.d }, color: "FFFFFF", bold: true, fontFace: "Calibri", fontSize: (fs || 11) + 0.5, valign: "middle", align: "left" } }));
  const body = rows.map((r, ri) => r.map((c) => ({ text: String(c), options: { fill: { color: ri % 2 ? "FFFFFF" : "EDF1FA" }, color: TEXT, fontFace: "Calibri", fontSize: fs || 11, valign: "middle" } })));
  s.addTable([head, ...body], { x, y, w, colW, border: { type: "solid", pt: 0.5, color: "D6DEEC" }, align: "left", valign: "middle", margin: 4 });
}
function divider(num, title, sub, acc, logoFiles) {
  const s = slide("dark");
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.16, fill: { color: acc.s } });
  s.addText(num, { x: 0.85, y: 1.55, w: 4, h: 1.8, fontFace: "Georgia", fontSize: 120, bold: true, color: INK2, margin: 0 });
  s.addText(sub.toUpperCase(), { x: 0.95, y: 3.55, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: acc.l, charSpacing: 3, margin: 0 });
  s.addText(title, { x: 0.9, y: 3.95, w: 11.5, h: 1.2, fontFace: "Georgia", fontSize: 40, bold: true, color: "FFFFFF", margin: 0 });
  gcpChip(s, 10.3, 0.55, 2.4);
  if (logoFiles && logoFiles.length) {
    const startX = 0.95, box = 0.7, lg = 0.48, cell = 0.95;
    logoFiles.forEach((f, i) => {
      const cx = startX + i * cell;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.5, w: box, h: box, rectRadius: 0.08, fill: { color: "FFFFFF" } });
      s.addImage({ path: LOGO(f), x: cx + (box - lg) / 2, y: 5.5 + (box - lg) / 2, w: lg, h: lg });
    });
  }
  return s;
}

// =====================================================================
// PARTIE 0 — INTRODUCTION
// =====================================================================

// --- 1. TITRE ---
(function () {
  const s = slide("dark");
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.18, fill: { color: A.blue.s } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.18, w: W, h: 0.06, fill: { color: A.green.s } });
  s.addText("GUIDE TECHNIQUE · DÉPLOIEMENT GOOGLE CLOUD PLATFORM", { x: 0.9, y: 1.0, w: 9.2, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: A.blue.l, charSpacing: 2, margin: 0 });
  s.addText("Guide Technique GCP\ndu projet MGVaovao", { x: 0.9, y: 1.5, w: 11.6, h: 1.8, fontFace: "Georgia", fontSize: 44, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("Destiné aux techniciens — développeurs · ML engineers · Cloud architects · DevOps. Pas-à-pas, service par service : du projet et des comptes de service à l'inférence GPU, au pipeline Vertex AI et au MLOps.", { x: 0.9, y: 3.4, w: 11.3, h: 1.0, fontFace: "Calibri", fontSize: 16, color: "CBD5EE", margin: 0 });
  gcpChip(s, 10.2, 0.5, 2.4);
  const files = Object.values(L);
  const n = files.length, startX = 0.9, span = 11.55, cell = span / n, box = 0.8, lg = 0.54;
  files.forEach((f, i) => {
    const cx = startX + i * cell + (cell - box) / 2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.2, w: box, h: box, rectRadius: 0.1, fill: { color: "FFFFFF" }, shadow: shadow() });
    s.addImage({ path: LOGO(f), x: cx + (box - lg) / 2, y: 5.2 + (box - lg) / 2, w: lg, h: lg });
  });
  s.addText([
    { text: "Préparé par : ", options: { fontFace: "Calibri", fontSize: 13, color: "8FA0C4" } },
    { text: NAME, options: { fontFace: "Calibri", fontSize: 13, bold: true, color: "CBD5EE" } },
  ], { x: 0.9, y: 6.12, w: 11.5, h: 0.32, margin: 0 });
  s.addText("Projet : mgvaovao-ia · Région : us-central1 · Traduction vocale temps réel anglais/français → malgache (dialectes)", { x: 0.9, y: 6.5, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 12, italic: true, color: "8A97B8", margin: 0 });
})();

// --- 2. LE PROJET (cascade pipeline) ---
(function () {
  const s = header(slide(), "Le projet MGVaovao", "Ce que fait le système", A.blue);
  para(s, 0.6, 1.45, 12.1, 0.9, "MGVaovao traduit automatiquement de l'audio en langue étrangère (vidéos, podcasts, parole en direct) vers du malgache parlé, spécifique au dialecte choisi — sans cliquer sur un bouton. L'utilisateur choisit la langue source et le dialecte cible ; le système détecte la parole, la transcrit, la traduit puis la synthétise.", 13.5);
  lbl(s, 0.6, 2.6, "LE PIPELINE EN CASCADE — 4 ÉTAGES INDÉPENDANTS", A.blue, 11);
  const stages = [
    { t: "VAD", m: "Silero VAD v5", d: "Détection de parole\n32 ms · CPU · MIT", acc: A.amber },
    { t: "ASR", m: "Whisper large-v3-turbo", d: "Transcription\nINT8 · 99 langues · Apache", acc: A.blue },
    { t: "MT", m: "NLLB-200-distilled-600M", d: "Traduction → plt_Latn\nLoRA r=16 · CC-BY-NC", acc: A.green },
    { t: "TTS", m: "MMS-TTS-MLG (VITS)", d: "Synthèse vocale dialecte\n16 kHz · CC-BY-NC", acc: A.purple },
  ];
  const cw = 2.78, cardy = 3.05, ch = 1.95, gap = 0.42;
  stages.forEach((st, i) => {
    const x = 0.6 + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: cardy, w: cw, h: ch, fill: { color: CARD }, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: cardy, w: cw, h: 0.5, fill: { color: st.acc.s } });
    s.addText(`Étage ${i} — ${st.t}`, { x: x + 0.15, y: cardy, w: cw - 0.3, h: 0.5, fontFace: "Georgia", fontSize: 14, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
    s.addText(st.m, { x: x + 0.15, y: cardy + 0.62, w: cw - 0.3, h: 0.5, fontFace: "Calibri", fontSize: 13, bold: true, color: TEXT, margin: 0 });
    s.addText(st.d, { x: x + 0.15, y: cardy + 1.12, w: cw - 0.3, h: 0.7, fontFace: "Calibri", fontSize: 11, color: MUTED, margin: 0 });
    if (i < 3) s.addText("→", { x: x + cw - 0.04, y: cardy + 0.6, w: gap + 0.08, h: 0.6, fontFace: "Calibri", fontSize: 26, bold: true, color: A.slate.d, align: "center", valign: "middle", margin: 0 });
  });
  callout(s, 0.6, 5.35, 12.1, 1.5, "POURQUOI EN CASCADE ?", "Modularité : chaque composant est remplaçable/affinable indépendamment. Fine-tuning ciblé du maillon le plus faible. Extension dialecte à bas coût (1 checkpoint TTS/dialecte). Empreinte totale ~6,2 Go sur GPU L4 (24 Go). Aucun système end-to-end S2S pour le malgache n'existait publiquement en 2026.", A.blue);
  footer(s, "Source : README §1, §3, §6 — Audio in → [VAD] → [ASR] → [NLLB MT] → [TTS] → WAV out");
})();

// --- 3. DIALECTES & MODÈLES (tables) ---
(function () {
  const s = header(slide(), "Dialectes & pile de modèles", "Ce que le système couvre", A.green);
  lbl(s, 0.6, 1.4, "DIALECTES MALGACHES SUPPORTÉS", A.green, 8, 12);
  table(s, 0.6, 1.75, 6.0, ["Clé", "Nom", "Région", "Locuteurs"], [
    ["plt_latn", "Malagasy Officiel", "Antananarivo", "Référence"],
    ["betsileo", "Betsileo", "Fianarantsoa", "~1,5 M"],
    ["betsimisaraka", "Betsimisaraka", "Toamasina", "~1,5 M"],
    ["sakalava", "Sakalava", "Mahajanga", "~1 M"],
    ["antandroy", "Antandroy", "Ambovombe", "~800 K"],
    ["merina", "Merina", "Imerina", "~4 M"],
  ], A.green, [1.5, 1.7, 1.6, 1.2], 10.5);
  s.addText("Langues sources : fr · en · de · es · it · pt (auto-détectées par Whisper)", { x: 0.6, y: 4.85, w: 6.0, h: 0.4, fontFace: "Calibri", fontSize: 11, italic: true, color: MUTED, margin: 0 });

  lbl(s, 7.0, 1.4, "PILE DE MODÈLES IA & VRAM (NVIDIA L4 24 GB)", A.green, 6, 12);
  table(s, 7.0, 1.75, 5.7, ["Étage", "Modèle", "VRAM", "Fine-tune"], [
    ["VAD", "Silero VAD v5", "0 (CPU)", "Non requis"],
    ["ASR", "Whisper turbo INT8", "1,7 GB", "Optionnel"],
    ["MT", "NLLB-200-600M INT8", "0,7 GB", "Oui (haut)"],
    ["TTS", "MMS-TTS-MLG ×6", "3,0 GB", "Oui /dialecte"],
    ["—", "Overhead CUDA", "0,8 GB", "—"],
    ["—", "TOTAL utilisé", "6,2 GB", "17,8 GB libre"],
  ], A.green, [1.0, 2.3, 1.2, 1.2], 10.5);
  callout(s, 7.0, 4.85, 5.7, 1.9, "À RETENIR", "3 à 5 sessions WebRTC/WebSocket simultanées par instance. L4 Spot ~0,28 $/h. NLLB et MMS-TTS sous CC-BY-NC 4.0 — usage ONG/recherche autorisé. Whisper Apache 2.0, Silero MIT.", A.green);
  footer(s, "Source : README §2, §3 — pile de modèles et allocation VRAM");
})();

// --- 4. ARCHITECTURE GCP (flow) ---
(function () {
  const s = header(slide(), "Architecture GCP de production", "Vue d'ensemble de bout en bout", A.teal);
  const cardW = 1.95, cardH = 1.45, lg = 0.74;
  function node(x, y, logoFile, label, sub, accent) {
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cardW, h: cardH, fill: { color: CARD }, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cardW, h: 0.09, fill: { color: accent } });
    if (logoFile) s.addImage({ path: LOGO(logoFile), x: x + (cardW - lg) / 2, y: y + 0.2, w: lg, h: lg });
    else s.addText("●", { x, y: y + 0.18, w: cardW, h: 0.7, fontSize: 28, color: A.blue.d, align: "center", margin: 0 });
    s.addText([{ text: label, options: { breakLine: true, fontFace: "Calibri", fontSize: 10.5, bold: true, color: TEXT } }, { text: sub || "", options: { fontFace: "Calibri", fontSize: 8.5, color: MUTED } }],
      { x: x + 0.05, y: y + cardH - 0.52, w: cardW - 0.1, h: 0.48, align: "center", valign: "top", margin: 0 });
  }
  const arrow = (x, y) => s.addText("→", { x, y, w: 0.62, h: 0.6, fontSize: 26, bold: true, color: A.teal.d, align: "center", valign: "middle", margin: 0 });
  s.addText("①  TEMPS RÉEL — INFÉRENCE", { x: 0.6, y: 1.45, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 12, bold: true, color: A.blue.d, charSpacing: 1, margin: 0 });
  let ax = 0.6, ay = 1.78; const gA = 0.66;
  node(ax, ay, null, "Client Web", "WebRTC / WS", A.blue.s); ax += cardW; arrow(ax, ay + 0.42); ax += gA;
  node(ax, ay, L.run, "Cloud Run", "Signaling CPU", A.blue.s); ax += cardW; arrow(ax, ay + 0.42); ax += gA;
  node(ax, ay, L.gpu, "Cloud Run GPU", "VAD·ASR·MT·TTS", A.red.s); ax += cardW; arrow(ax, ay + 0.42); ax += gA;
  node(ax, ay, L.storage, "Cloud Storage", "Modèles", A.green.s);
  s.addText("②  COLLECTE → ENTRAÎNEMENT → DÉPLOIEMENT", { x: 0.6, y: 3.55, w: 9, h: 0.3, fontFace: "Calibri", fontSize: 12, bold: true, color: A.purple.d, charSpacing: 1, margin: 0 });
  let bx = 0.6, by = 3.88; const gB = 0.355;
  node(bx, by, L.storage, "Kozy (Frontend)", "Collecte audio/CSV", A.teal.s); bx += cardW; arrow(bx, by + 0.42); bx += gB;
  node(bx, by, L.storage, "Cloud Storage", "Dataset", A.green.s); bx += cardW; arrow(bx, by + 0.42); bx += gB;
  node(bx, by, L.pubsub, "Pub/Sub", "Événement", A.red.s); bx += cardW; arrow(bx, by + 0.42); bx += gB;
  node(bx, by, L.vertex, "Vertex AI", "Fine-tuning T4", A.purple.s); bx += cardW; arrow(bx, by + 0.42); bx += gB;
  node(bx, by, L.build, "Cloud Build", "Blue/Green", A.amber.s);
  s.addText("La chaîne ② réinjecte le modèle validé dans Cloud Run GPU (chaîne ①) via un déploiement Blue/Green.", { x: 0.6, y: 5.42, w: 12.1, h: 0.32, fontFace: "Calibri", fontSize: 10.5, italic: true, color: MUTED, margin: 0 });
  const ty = 5.85;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ty, w: 12.13, h: 1.05, fill: { color: "E9EDF6" } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ty, w: 0.12, h: 1.05, fill: { color: A.teal.s } });
  s.addText("TRANSVERSAUX", { x: 0.82, y: ty + 0.1, w: 2.3, h: 0.85, fontFace: "Calibri", fontSize: 11, bold: true, color: A.teal.d, charSpacing: 1, valign: "middle", margin: 0 });
  const trans = [[L.artifact, "Artifact Registry"], [L.iam, "IAM"], [L.logging, "Logging"], [L.monitoring, "Monitoring"], [L.compute, "Compute Engine"]];
  const tStart = 3.0, tSlot = 1.95, tLogo = 0.46;
  trans.forEach((m, i) => {
    const tx = tStart + i * tSlot;
    s.addImage({ path: LOGO(m[0]), x: tx, y: ty + 0.3, w: tLogo, h: tLogo });
    s.addText(m[1], { x: tx + tLogo + 0.08, y: ty + 0.3, w: tSlot - tLogo - 0.12, h: 0.46, fontFace: "Calibri", fontSize: 10.5, bold: true, color: TEXT, valign: "middle", margin: 0 });
  });
  footer(s, "Source : README §5.2 — Cloud Run CPU+GPU · GCS · Vertex AI · Cloud Build · Pub/Sub · Scheduler · STUN/TURN Cloudflare");
})();

// --- 5. FLUX & LATENCE ---
(function () {
  const s = header(slide(), "Flux d'architecture & latence", "Comment les services s'enchaînent", A.teal);
  lbl(s, 0.6, 1.4, "LES 6 FLUX DE L'ARCHITECTURE", A.teal, 8, 12);
  table(s, 0.6, 1.75, 7.2, ["Flux", "Chemin", "Composants clés"], [
    ["2a", "Connexion WebRTC", "Client → Cloud Run CPU"],
    ["2b", "Pipeline d'inférence", "Cloud Run CPU → Cloud Run GPU L4"],
    ["2c", "Stockage modèles", "Cloud Run GPU ↔ Cloud Storage"],
    ["2d", "Déclencheur training", "GCS → Pub/Sub → Vertex Pipeline"],
    ["2e", "Cycle de vie modèle", "Vertex → Registry → Build → Deploy"],
    ["2f", "Monitoring de drift", "Scheduler → Monitoring → Pub/Sub"],
  ], A.teal, [0.8, 2.6, 3.8], 10.5);
  lbl(s, 8.1, 1.4, "LATENCE (L4, À CHAUD)", A.teal, 5, 12);
  table(s, 8.1, 1.75, 4.6, ["Étage", "Latence"], [
    ["Silero VAD", "1–50 ms"],
    ["Whisper INT8 (3 s)", "250–500 ms"],
    ["NLLB-200 INT8", "80–350 ms"],
    ["MMS-TTS VITS", "150–450 ms"],
    ["WebRTC transport", "50–150 ms"],
    ["TOTAL (à chaud)", "~700–1500 ms"],
  ], A.teal, [2.6, 2.0], 10.5);
  callout(s, 0.6, 5.5, 12.1, 1.25, "OPTIMISATIONS ACTIVES", "vad_filter=True (VAD + ASR en parallèle) · num_beams=2 · checkpoints TTS préchargés en VRAM · chunks de 32 ms · quantification INT8 (CTranslate2) : −50 % VRAM, ×2 vitesse.", A.teal);
  footer(s, "Source : README §5.3, §7 — tableau des flux et décomposition de la latence");
})();

// --- KOZY 1 — application de collecte de données ---
(function () {
  const s = header(slide(), "Kozy — application de collecte de données", "Frontend · gestion des datasets d'entraînement", A.teal, L.storage, "ÉCOSYSTÈME");
  para(s, 0.6, 1.45, 12.1, 0.9, "Kozy (dépôt Frontend) est l'application web qui alimente le projet en données. Elle collecte et cure des échantillons audio par dialecte et des jeux CSV de traduction, stockés sur Cloud Storage — la matière première du fine-tuning NLLB et TTS.", 13.5);
  lbl(s, 0.6, 2.5, "PILE TECHNIQUE", A.teal, 6);
  bullets(s, 0.6, 2.85, 6.0, 1.7, [
    "Frontend : React 19 · Vite · Tailwind CSS",
    "Backend : Node.js · Express · TypeScript",
    "Auth : Google OAuth 2.0 (google-auth-library)",
    "Upload : Multer · CSV : Papa Parse · validation Zod",
  ], 12.5);
  lbl(s, 0.6, 4.75, "DONNÉES PRODUITES", A.teal, 6);
  codeBox(s, 0.6, 5.1, 6.0, 1.55, "# Bucket : gs://kozy-dataset\ncsv/        # source,target,\n            #   src_lang,dialecte\naudio/{dialect}/{fichier}.wav", 10);
  lbl(s, 6.9, 2.5, "COMPOSANTS GCP UTILISÉS", A.teal, 6);
  const comps = [[L.storage, "Cloud Storage", "bucket kozy-dataset"], [L.iam, "Google OAuth 2.0", "authentification"], [L.run, "Cloud Run", "hébergement · port 8080"], [L.build, "Cloud Build", "CI/CD"], [L.artifact, "Artifact Registry", "image kozy"], [L.secret, "Secret Manager", "GOOGLE_CLIENT_ID"]];
  const gx = 6.9, gy = 2.85, cw = 2.85, ch = 1.13, gpx = 0.15, gpy = 0.11;
  comps.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = gx + col * (cw + gpx), y = gy + row * (ch + gpy);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ path: LOGO(c[0]), x: x + 0.12, y: y + (ch - 0.55) / 2, w: 0.55, h: 0.55 });
    s.addText([{ text: c[1] + "\n", options: { breakLine: true, fontFace: "Calibri", fontSize: 11, bold: true, color: TEXT } }, { text: c[2], options: { fontFace: "Calibri", fontSize: 9, color: MUTED } }], { x: x + 0.78, y: y + 0.1, w: cw - 0.88, h: ch - 0.2, valign: "middle", margin: 0 });
  });
  footer(s, "Source : dépôt Frontend (Kozy) — gcsService.ts · cloudbuild.yaml · Dockerfile · DEPLOY.md");
})();

// --- KOZY 2 — déploiement & sécurité ---
(function () {
  const s = header(slide(), "Kozy — déploiement & sécurité", "Cloud Build · Cloud Run · Secret Manager · OAuth", A.amber, L.secret, "ÉCOSYSTÈME");
  lbl(s, 0.6, 1.45, "PIPELINE CLOUD BUILD (cloudbuild.yaml)", A.amber, 7);
  codeBox(s, 0.6, 1.8, 6.1, 3.0, "# 1. build (VITE_GOOGLE_CLIENT_ID injecté)\ndocker build -t .../mgvaovao/kozy .\n# 2. push -> Artifact Registry\n# 3. deploy -> Cloud Run\ngcloud run deploy kozy \\\n  --image .../mgvaovao/kozy \\\n  --region us-central1 --port 8080 \\\n  --min-instances 0 --max-instances 5 \\\n  --set-secrets=GOOGLE_CLIENT_ID=\\\n    GOOGLE_CLIENT_ID:latest", 9.5);
  lbl(s, 0.6, 5.0, "COMPTE DE SERVICE DÉDIÉ (MOINDRE PRIVILÈGE)", A.amber, 7);
  codeBox(s, 0.6, 5.35, 6.1, 1.3, "storage-kozy@PROJECT.iam.gserviceaccount.com\n  roles/storage.objectAdmin\n  roles/secretmanager.secretAccessor", 9.5);
  lbl(s, 6.9, 1.45, "SECRET MANAGER", A.amber, 6);
  para(s, 6.9, 1.8, 5.85, 1.15, "Coffre-fort managé pour les secrets (clés, identifiants). Le GOOGLE_CLIENT_ID OAuth y est stocké puis injecté à l'exécution dans Cloud Run via --set-secrets — jamais en clair dans l'image ni le code.", 12.5);
  bullets(s, 6.9, 3.05, 5.85, 1.45, ["Versions de secrets + rotation", "Accès contrôlé par IAM (secretAccessor)", "Injecté comme variable d'environnement au runtime"], 12);
  callout(s, 6.9, 4.65, 5.85, 1.95, "SÉCURITÉ — BONNES PRATIQUES", "Identifiants via Application Default Credentials (ADC), aucune clé de SA embarquée. OAuth 2.0 pour authentifier les utilisateurs. Secrets dans Secret Manager. Compte de service dédié au strict minimum de rôles.", A.amber);
  footer(s, "Source : dépôt Frontend (Kozy) — cloudbuild.yaml (--set-secrets) · DEPLOY.md · doc : cloud.google.com/secret-manager/docs");
})();

// =====================================================================
// PARTIE 1 — FONDATIONS
// =====================================================================
divider("01", "Fondations GCP", "Partie 1 — Pré-requis & configuration du projet", A.blue, [L.iam, L.artifact, L.storage]);

// --- Pré-requis ---
(function () {
  const s = header(slide(), "Pré-requis", "Avant de commencer", A.blue, null, "PARTIE 1");
  lbl(s, 0.6, 1.45, "CÔTÉ POSTE DE TRAVAIL", A.blue, 6);
  bullets(s, 0.6, 1.8, 5.9, 2.0, [
    "gcloud CLI installé et authentifié",
    "git",
    "Python 3.10+ (pour les scripts utilitaires)",
    "Docker (optionnel — le build se fait dans le cloud)",
  ], 13);
  lbl(s, 0.6, 3.9, "CÔTÉ GOOGLE CLOUD", A.blue, 6);
  bullets(s, 0.6, 4.25, 5.9, 2.2, [
    "Un projet GCP avec la facturation activée",
    "Quota GPU L4 approuvé (Cloud Run + Vertex)",
    "10 APIs à activer (slide suivante)",
    "Droits IAM pour créer des comptes de service",
  ], 13);
  lbl(s, 6.9, 1.45, "LES 10 APIs REQUISES", A.blue, 6);
  codeBox(s, 6.9, 1.8, 5.85, 4.65,
    "run.googleapis.com            # Cloud Run\nartifactregistry.googleapis.com  # Artifact Reg.\ncloudbuild.googleapis.com     # Cloud Build\nstorage.googleapis.com        # Cloud Storage\naiplatform.googleapis.com     # Vertex AI\npubsub.googleapis.com         # Pub/Sub\ncloudscheduler.googleapis.com # Scheduler\nlogging.googleapis.com        # Cloud Logging\nmonitoring.googleapis.com     # Cloud Monitoring\niam.googleapis.com            # IAM", 11);
  footer(s, "Source : README §9, §18.1 — pré-requis et liste des APIs");
})();

// --- gcloud setup ---
(function () {
  const s = header(slide(), "Installer & configurer gcloud", "Configuration unique du projet", A.blue, null, "PARTIE 1");
  steps(s, 0.6, 1.5, 6.0, [
    { n: 1, t: "Installer & s'authentifier", d: "gcloud auth login + application-default login" },
    { n: 2, t: "Créer ou sélectionner le projet", d: "projet mgvaovao-ia" },
    { n: 3, t: "Activer la facturation", d: "Console → Billing → lier un compte" },
    { n: 4, t: "Noter le numéro de projet", d: "nécessaire pour les bindings IAM" },
    { n: 5, t: "Enregistrer un profil gcloud nommé", d: "évite de retaper projet/région" },
  ], A.blue, 1.0);
  codeBox(s, 6.9, 1.5, 5.85, 5.0,
    "# 1. Authentification\ngcloud auth login\ngcloud auth application-default login\n\n# 2-3. Projet + facturation (Console)\ngcloud projects create mgvaovao-ia \\\n  --name=\"MGVaovao IA\"\ngcloud config set project mgvaovao-ia\n\n# 4. Numéro de projet\ngcloud projects describe mgvaovao-ia \\\n  --format=\"value(projectNumber)\"\n# -> 97374817504\n\n# 5. Profil nommé\ngcloud config configurations create mgvaovao\ngcloud config set compute/region us-central1\ngcloud config set compute/zone us-central1-a", 9.5);
  footer(s, "Source : README §18.1 — Steps 1, 2, 3, 8");
})();

// --- Activer les APIs ---
(function () {
  const s = header(slide(), "Activer les APIs", "Une seule commande", A.blue, null, "PARTIE 1");
  para(s, 0.6, 1.45, 12.1, 0.6, "Activez les 10 services en une commande. L'opération prend 1 à 3 minutes. Chaque API doit être active avant d'utiliser le service correspondant.", 13.5);
  codeBox(s, 0.6, 2.2, 7.6, 3.0,
    "gcloud services enable \\\n  run.googleapis.com \\\n  artifactregistry.googleapis.com \\\n  cloudbuild.googleapis.com \\\n  storage.googleapis.com \\\n  aiplatform.googleapis.com \\\n  pubsub.googleapis.com \\\n  cloudscheduler.googleapis.com \\\n  logging.googleapis.com \\\n  monitoring.googleapis.com \\\n  iam.googleapis.com \\\n  --project=mgvaovao-ia", 11);
  lbl(s, 8.4, 2.2, "VÉRIFIER", A.blue, 4);
  codeBox(s, 8.4, 2.55, 4.35, 1.7, "gcloud services list \\\n  --enabled \\\n  --project=mgvaovao-ia \\\n  | grep -E \\\n  \"run|build|aiplatform\"", 9.5);
  callout(s, 8.4, 4.5, 4.35, 1.7, "ASTUCE", "Réactiver une API déjà active est sans effet (idempotent). Sautez les étapes déjà faites lors d'une migration.", A.blue);
  footer(s, "Source : README §18.1 — Step 4");
})();

// =====================================================================
// PARTIE 2 — LES SERVICES, UN PAR UN
// =====================================================================
divider("02", "Les services, un par un", "Partie 2 — Concepts + configuration pas-à-pas", A.amber,
  [L.iam, L.artifact, L.storage, L.compute, L.build, L.run, L.gpu, L.vertex, L.pubsub, L.logging]);

// ---------------- IAM ----------------
(function () {
  const s = header(slide(), "IAM — concepts", "Sécurité · Gestion des accès", A.amber, L.iam, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "Identity and Access Management contrôle « qui peut faire quoi, sur quelle ressource ». On accorde des RÔLES (ensembles de permissions) à des PRINCIPALS (utilisateurs ou comptes de service) via des bindings sur une ressource.", 13.5);
  lbl(s, 0.6, 2.5, "CONCEPTS CLÉS", A.amber, 6);
  bullets(s, 0.6, 2.85, 6.0, 2.4, [
    "Principals : utilisateurs, groupes, comptes de service",
    "Rôles : prédéfinis, personnalisés, ou basiques",
    "Permission = service.resource.verb (ex. run.services.create)",
    "Binding = (principal + rôle) sur une ressource",
    "Moindre privilège + héritage par la hiérarchie",
  ], 12.5);
  lbl(s, 6.9, 2.5, "LES 2 COMPTES DE SERVICE DU PROJET", A.amber, 6);
  table(s, 6.9, 2.85, 5.85, ["Compte de service", "Rôles"], [
    ["cloudbuild-runner", "run.admin · iam.serviceAccountUser · artifactregistry.writer · storage.objectAdmin"],
    ["N-compute@developer (défaut)", "storage.objectAdmin · artifactregistry.reader"],
  ], A.amber, [2.4, 3.45], 10);
  callout(s, 0.6, 5.5, 12.1, 1.25, "POURQUOI UN COMPTE DÉDIÉ ?", "Cloud Build doit déployer sur Cloud Run et pousser des images : on lui crée un compte de service dédié avec le strict minimum de rôles, plutôt que d'utiliser un compte trop permissif. C'est l'application du principe de moindre privilège.", A.amber);
  footer(s, "Source : README §18.1 Step 7, §18.10 — doc : cloud.google.com/iam/docs");
})();

(function () {
  const s = header(slide(), "IAM — créer le service account", "Génération du compte Cloud Build (pas-à-pas)", A.amber, L.iam, "PARTIE 2");
  steps(s, 0.6, 1.5, 6.0, [
    { n: 1, t: "Créer le compte de service", d: "cloudbuild-runner" },
    { n: 2, t: "Cloud Run Admin", d: "créer / mettre à jour les services" },
    { n: 3, t: "Service Account User", d: "exécuter Cloud Run en tant que SA" },
    { n: 4, t: "Artifact Registry Writer", d: "pousser les images Docker" },
    { n: 5, t: "Storage Object Admin", d: "lire/écrire les checkpoints" },
  ], A.amber, 1.0);
  codeBox(s, 6.9, 1.5, 5.85, 5.0,
    "PROJECT_NUMBER=97374817504\nSA=cloudbuild-runner@mgvaovao-ia\\\n.iam.gserviceaccount.com\n\n# 1. Créer le compte de service\ngcloud iam service-accounts create \\\n  cloudbuild-runner \\\n  --display-name=\"Cloud Build deploy\"\n\n# 2-5. Accorder les rôles\nfor R in run.admin \\\n  iam.serviceAccountUser \\\n  artifactregistry.writer \\\n  storage.objectAdmin; do\n  gcloud projects \\\n    add-iam-policy-binding mgvaovao-ia \\\n    --member=\"serviceAccount:$SA\" \\\n    --role=\"roles/$R\"\ndone", 9);
  footer(s, "Source : README §18.1 — Step 7 (création SA + 4 bindings de rôles)");
})();

(function () {
  const s = header(slide(), "IAM — comptes & vérification", "SA par défaut de Cloud Build & de Vertex", A.amber, L.iam, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.7, "Deux comptes de service gérés par Google reçoivent aussi des rôles : celui utilisé par « gcloud builds submit » et le compte Compute par défaut utilisé par les jobs Vertex AI.", 13);
  lbl(s, 0.6, 2.3, "SA PAR DÉFAUT DE CLOUD BUILD", A.amber, 6);
  codeBox(s, 0.6, 2.65, 6.0, 2.5,
    "# Utilisé par: gcloud builds submit\nSA=$PROJECT_NUMBER@cloudbuild\\\n.gserviceaccount.com\n\ngcloud projects add-iam-policy-binding \\\n  mgvaovao-ia --member=\"serviceAccount:$SA\" \\\n  --role=\"roles/run.admin\"\n\ngcloud projects add-iam-policy-binding \\\n  mgvaovao-ia --member=\"serviceAccount:$SA\" \\\n  --role=\"roles/iam.serviceAccountUser\"", 9);
  lbl(s, 6.9, 2.3, "SA COMPUTE (VERTEX AI)", A.amber, 6);
  codeBox(s, 6.9, 2.65, 5.85, 2.5,
    "# Utilisé par les jobs Vertex AI\nSA=$PROJECT_NUMBER-compute@\\\ndeveloper.gserviceaccount.com\n\n# Accès GCS (checkpoints/datasets)\n--role=\"roles/storage.objectAdmin\"\n\n# Lecture des images Docker\n--role=\"roles/artifactregistry.reader\"", 9);
  callout(s, 0.6, 5.4, 12.1, 1.05, "VÉRIFIER", "gcloud iam service-accounts list --project=mgvaovao-ia  →  doit lister cloudbuild-runner et le compte compute par défaut.", A.amber);
  footer(s, "Source : README §18.1 Step 7, §18.6, §18.10");
})();

// ---------------- ARTIFACT REGISTRY ----------------
(function () {
  const s = header(slide(), "Artifact Registry — concepts", "Registre d'images de conteneurs", A.teal, L.artifact, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.8, "Registre managé pour packages et images de conteneurs (successeur de Container Registry). Les images Docker du projet y sont stockées, puis tirées par Cloud Run (inférence) et Vertex AI (training).", 13.5);
  lbl(s, 0.6, 2.45, "CONCEPTS CLÉS", A.teal, 6);
  bullets(s, 0.6, 2.8, 6.0, 2.3, [
    "Dépôts régionaux multi-formats (Docker, Python, npm…)",
    "Contrôle d'accès via IAM (writer / reader)",
    "Analyse de vulnérabilités (Artifact Analysis)",
    "Cible des builds, source des déploiements",
  ], 13);
  lbl(s, 6.9, 2.45, "LES 2 IMAGES DU PROJET", A.teal, 6);
  codeBox(s, 6.9, 2.8, 5.85, 2.5,
    "# Dépôt : us-central1 · format docker\n\n# Image d'inférence (Cloud Run GPU)\n.../mgvaovao/inference:latest\n.../mgvaovao/inference:{SHORT_SHA}\n\n# Image CUDA (training Vertex)\n.../mgvaovao/mgvaovao:cuda-latest", 10);
  callout(s, 0.6, 5.45, 12.1, 1.05, "CONVENTION DE TAG", "Chaque commit produit un tag immuable {SHORT_SHA} + un tag mobile latest. Le déploiement utilise le tag immuable pour la traçabilité et le rollback.", A.teal);
  footer(s, "Source : README §18.1 Step 5, §18.10 — doc : cloud.google.com/artifact-registry/docs");
})();

(function () {
  const s = header(slide(), "Artifact Registry — créer le dépôt", "Configuration pas-à-pas", A.teal, L.artifact, "PARTIE 2");
  steps(s, 0.6, 1.55, 6.0, [
    { n: 1, t: "Créer le dépôt Docker", d: "nom mgvaovao · région us-central1" },
    { n: 2, t: "Vérifier la création", d: "repositories list" },
    { n: 3, t: "Authentifier Docker (si push local)", d: "configure-docker" },
  ], A.teal, 1.0);
  codeBox(s, 6.9, 1.55, 5.85, 4.0,
    "# 1. Créer le dépôt\ngcloud artifacts repositories create \\\n  mgvaovao \\\n  --repository-format=docker \\\n  --location=us-central1 \\\n  --description=\"MGVaovao images\" \\\n  --project=mgvaovao-ia\n\n# 2. Vérifier\ngcloud artifacts repositories list \\\n  --project=mgvaovao-ia\n\n# 3. Auth Docker (push local)\ngcloud auth configure-docker \\\n  us-central1-docker.pkg.dev", 9.5);
  footer(s, "Source : README §18.1 — Step 5");
})();

// ---------------- CLOUD STORAGE ----------------
(function () {
  const s = header(slide(), "Cloud Storage — concepts", "Stockage objet : modèles & datasets", A.green, L.storage, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.8, "Stockage objet scalable. Conserve les checkpoints fine-tunés (tirés par Cloud Run à froid) et les datasets d'entraînement/évaluation. Backend natif de Vertex AI.", 13.5);
  lbl(s, 0.6, 2.4, "CONCEPTS CLÉS", A.green, 6);
  bullets(s, 0.6, 2.75, 6.0, 2.4, [
    "Objets rangés dans des buckets (régional/multi-régional)",
    "Classes Standard / Nearline / Coldline / Archive",
    "Versioning d'objets (récupération, audit)",
    "Accès fin via IAM, chiffrement par défaut",
  ], 13);
  lbl(s, 6.9, 2.4, "LES 2 BUCKETS DU PROJET", A.green, 6);
  table(s, 6.9, 2.75, 5.85, ["Bucket", "Rôle"], [
    ["mgvaovao-ia-checkpoints", "Checkpoints modèles (tirés à froid)"],
    ["mgvaovao-ia_cloudbuild", "Archives source Cloud Build (auto)"],
  ], A.green, [2.7, 3.15], 10);
  callout(s, 0.6, 5.45, 12.1, 1.05, "AU DÉMARRAGE À FROID", "Cloud Run exécute pull_checkpoints.py qui télécharge uniquement les checkpoints absents en local. Si le bucket est vide, les modèles de base (intégrés à l'image) sont utilisés.", A.green);
  footer(s, "Source : README §18.1 Step 6, §18.5 — doc : cloud.google.com/storage/docs");
})();

(function () {
  const s = header(slide(), "Cloud Storage — buckets & checkpoints", "Création, arborescence et upload", A.green, L.storage, "PARTIE 2");
  codeBox(s, 0.6, 1.5, 6.0, 2.2,
    "# 1. Créer le bucket de checkpoints\ngcloud storage buckets create \\\n  gs://mgvaovao-ia-checkpoints \\\n  --location=us-central1 \\\n  --project=mgvaovao-ia\n# (le bucket cloudbuild est auto-créé)", 9.5);
  lbl(s, 0.6, 3.85, "ARBORESCENCE GCS", A.green, 6);
  codeBox(s, 0.6, 4.2, 6.0, 2.35,
    "gs://mgvaovao-ia-checkpoints/\n  tts_{dialect}/final/      # VITS\n    config.json model.safetensors\n  nllb_{dialect}/final/     # LoRA\n    adapter_config.json\n    adapter_model.safetensors", 9.5);
  lbl(s, 6.9, 1.5, "UPLOADER UN CHECKPOINT FINE-TUNÉ", A.green, 6);
  codeBox(s, 6.9, 1.85, 5.85, 2.6,
    "# Script du projet\npython scripts/push_checkpoint.py \\\n  tts betsileo \\\n  ./checkpoints/tts_betsileo/final\n\n# Ou directement avec gsutil\ngsutil -m cp -r \\\n  ./checkpoints/tts_betsileo/final \\\n  gs://mgvaovao-ia-checkpoints/tts_betsileo/", 9.5);
  callout(s, 6.9, 4.7, 5.85, 1.85, "PRENDRE EN COMPTE LE NOUVEAU MODÈLE", "Les checkpoints ne sont tirés qu'au démarrage à froid. Forcer un redémarrage :\ngcloud run services update mgvaovao-inference --region=us-central1", A.green);
  footer(s, "Source : README §18.1 Step 6, §17, §18.5");
})();

// ---------------- COMPUTE ENGINE ----------------
(function () {
  const s = header(slide(), "Compute Engine — concepts", "Infrastructure · les GPU sous-jacents", A.teal, L.compute, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "IaaS de Google Cloud : machines virtuelles configurables. C'est le socle des accélérateurs GPU utilisés par Vertex AI (training) et Cloud Run (inférence). On n'y déploie pas de VM manuellement ici, mais on en consomme les GPU et on demande le quota.", 13.5);
  lbl(s, 0.6, 2.6, "CONCEPTS CLÉS", A.teal, 6);
  bullets(s, 0.6, 2.95, 6.0, 2.4, [
    "Familles de machines (n1, n2, accelerator-optimized…)",
    "Accélérateurs GPU : NVIDIA T4 (training), L4 (inférence)",
    "Persistent Disk / Local SSD · images Linux/Windows",
    "Spot VMs : −60 % à −91 % vs on-demand",
    "Régions & zones (us-central1 / us-central1-a)",
  ], 12.5);
  lbl(s, 6.9, 2.6, "LES GPU DU PROJET", A.teal, 6);
  table(s, 6.9, 2.95, 5.85, ["Usage", "Machine + GPU"], [
    ["Training (Vertex)", "n1-standard-8 + NVIDIA_TESLA_T4"],
    ["Inférence (Run)", "g2-standard-8 + NVIDIA L4 24 GB"],
    ["Coût L4 Spot", "~0,28 $/h"],
  ], A.teal, [2.0, 3.85], 10.5);
  callout(s, 0.6, 5.55, 12.1, 1.1, "QUOTA GPU", "Cloud Run GPU L4 est GA depuis juin 2025. Le quota GPU doit être approuvé pour votre projet/région avant déploiement : Console → IAM & Admin → Quotas → filtrer « L4 ».", A.teal);
  footer(s, "Source : README §5.2, §18.3, §23 — doc : cloud.google.com/compute/docs");
})();

// ---------------- CLOUD BUILD ----------------
(function () {
  const s = header(slide(), "Cloud Build — concepts", "CI/CD : build → push → deploy", A.amber, L.build, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "Service qui exécute vos builds sur Google Cloud. Pour MGVaovao : il construit l'image d'inférence (les 4 modèles sont intégrés à l'image, ~8 Go), la pousse dans Artifact Registry, puis déploie sur Cloud Run GPU — sans interruption (Blue/Green).", 13.5);
  lbl(s, 0.6, 2.55, "CONCEPTS CLÉS", A.amber, 6);
  bullets(s, 0.6, 2.9, 6.0, 2.3, [
    "Config déclarative cloudbuild-inference.yaml (étapes)",
    "Chaque étape = un conteneur (builder)",
    "Substitutions de variables ($SHORT_SHA, $PROJECT_ID)",
    "Déclencheurs (push GitHub) + cache de couches Docker",
  ], 13);
  lbl(s, 6.9, 2.55, "TEMPS DE BUILD", A.amber, 6);
  table(s, 6.9, 2.9, 5.85, ["Build", "Durée"], [
    ["1er build (téléch. modèles)", "~45–60 min"],
    ["Builds suivants (cache)", "~5–10 min"],
    ["Taille de l'image", "~8 GB"],
  ], A.amber, [3.4, 2.45], 10.5);
  callout(s, 0.6, 5.45, 12.1, 1.05, "3 FICHIERS IMPLIQUÉS", "Dockerfile.cloudrun (image multi-stage) · cloudbuild-inference.yaml (pipeline build→push→deploy) · scripts/download_models.py (télécharge les 4 modèles au build).", A.amber);
  footer(s, "Source : README §18.2 — doc : cloud.google.com/build/docs");
})();

(function () {
  const s = header(slide(), "Cloud Build — le pipeline étape par étape", "Ce que fait cloudbuild-inference.yaml", A.amber, L.build, "PARTIE 2");
  steps(s, 0.6, 1.5, 6.0, [
    { n: 1, t: "build-inference", d: "docker build -f Dockerfile.cloudrun, tags {SHA}+latest, --cache-from" },
    { n: 2, t: "push-sha", d: "pousse inference:{SHORT_SHA}" },
    { n: 3, t: "push-latest", d: "pousse inference:latest" },
    { n: 4, t: "deploy", d: "gcloud run deploy avec GPU L4 (tag immuable)" },
  ], A.amber, 1.15);
  codeBox(s, 6.9, 1.5, 5.85, 5.0,
    "# Étape 1 — build\ndocker build -f Dockerfile.cloudrun \\\n  --tag inference:{SHORT_SHA} \\\n  --tag inference:latest \\\n  --cache-from inference:latest\n\n# Étape 2-3 — push vers Artifact Registry\npush inference:{SHORT_SHA}\npush inference:latest\n\n# Étape 4 — déploiement Cloud Run\ngcloud run deploy mgvaovao-inference \\\n  --image inference:{SHORT_SHA} \\\n  --gpu 1 --gpu-type nvidia-l4 \\\n  --cpu 8 --memory 32Gi \\\n  --min-instances 0 --max-instances 2", 9.5);
  footer(s, "Source : README §18.2 — décomposition de cloudbuild-inference.yaml");
})();

(function () {
  const s = header(slide(), "Cloud Build — lancer & suivre", "Build manuel et monitoring", A.amber, L.build, "PARTIE 2");
  lbl(s, 0.6, 1.45, "LANCER UN BUILD MANUEL", A.amber, 6);
  codeBox(s, 0.6, 1.8, 6.0, 2.2,
    "# Linux / macOS / WSL\ngcloud builds submit \\\n  --config=cloudbuild-inference.yaml \\\n  --project=mgvaovao-ia \\\n  --substitutions=SHORT_SHA=$(git \\\n    rev-parse --short HEAD) .", 9.5);
  codeBox(s, 0.6, 4.15, 6.0, 1.6,
    "# PowerShell (Windows)\n$SHA = git rev-parse --short HEAD\ngcloud builds submit `\n  --config=cloudbuild-inference.yaml `\n  \"--substitutions=SHORT_SHA=$SHA\" .", 9.5);
  lbl(s, 6.9, 1.45, "SUIVRE UN BUILD", A.amber, 6);
  codeBox(s, 6.9, 1.8, 5.85, 1.85,
    "gcloud builds list --limit=5 \\\n  --project=mgvaovao-ia\n\ngcloud builds log BUILD_ID \\\n  --project=mgvaovao-ia --stream", 9.5);
  callout(s, 6.9, 3.85, 5.85, 1.9, "PIÈGE — SHORT_SHA VIDE", "$SHORT_SHA n'est rempli automatiquement que par un déclencheur. En build manuel il est vide → erreur « invalid image name ». Toujours le passer explicitement (sur PowerShell, via une variable intermédiaire).", A.amber);
  footer(s, "Source : README §18.2, §18.9 (Bug 3) — build manuel & monitoring");
})();

// ---------------- CLOUD RUN ----------------
(function () {
  const s = header(slide(), "Cloud Run — concepts", "Calcul serverless (CPU + GPU)", A.blue, L.run, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "Plateforme serverless pour conteneurs, sans gérer de serveurs. Deux services dans MGVaovao : un service CPU léger (signaling WebRTC, ~2 $/mois) et un service GPU L4 (pipeline d'inférence complet, ~33 $/mois). Les deux passent à l'échelle zéro.", 13.5);
  lbl(s, 0.6, 2.55, "CONCEPTS CLÉS", A.blue, 6);
  bullets(s, 0.6, 2.9, 6.0, 2.3, [
    "Conteneurs serverless, autoscaling à la demande",
    "Scale-to-zero (0 € à l'idle) — même avec GPU",
    "Facturation à l'usage · HTTP/2, gRPC, WebSockets",
    "Cloud Run écoute toujours sur le port 8080",
  ], 13);
  lbl(s, 6.9, 2.55, "LES 2 SERVICES", A.blue, 6);
  table(s, 6.9, 2.9, 5.85, ["Service", "Rôle / coût"], [
    ["Cloud Run CPU", "Signaling WebRTC · ~2 $/mois"],
    ["Cloud Run GPU L4", "VAD+ASR+MT+TTS · ~33 $/mois"],
  ], A.blue, [2.5, 3.35], 10.5);
  callout(s, 0.6, 5.45, 12.1, 1.05, "GPU SANS PILOTE À INSTALLER", "Les pilotes NVIDIA sont montés automatiquement (/usr/local/nvidia). L4 exige au minimum 8 vCPU et 32 Gio de RAM sur Cloud Run, et 1 seul GPU par instance.", A.blue);
  footer(s, "Source : README §5.2, §18.3 — doc : cloud.google.com/run/docs");
})();

(function () {
  const s = header(slide(), "Cloud Run GPU — la commande de déploiement", "Chaque flag expliqué", A.blue, L.gpu, "PARTIE 2");
  codeBox(s, 0.6, 1.45, 6.1, 3.95,
    "gcloud run deploy mgvaovao-inference \\\n  --image=.../inference:{SHA} \\\n  --region=us-central1 \\\n  --platform=managed \\\n  --gpu=1 \\\n  --gpu-type=nvidia-l4 \\\n  --cpu=8 \\\n  --memory=32Gi \\\n  --no-cpu-throttling \\\n  --no-gpu-zonal-redundancy \\\n  --concurrency=1 \\\n  --min-instances=0 \\\n  --max-instances=2 \\\n  --timeout=300 \\\n  --port=8080 \\\n  --set-env-vars=MGVAOVAO_DEVICE=cuda \\\n  --allow-unauthenticated", 9.5);
  table(s, 6.9, 1.45, 5.85, ["Flag", "Pourquoi"], [
    ["--gpu-type nvidia-l4", "24 GB VRAM, GA 2025"],
    ["--cpu 8 / --memory 32Gi", "minimum L4 sur Run"],
    ["--no-cpu-throttling", "CPU pour scheduling GPU"],
    ["--concurrency 1", "1 session WS / instance"],
    ["--min/--max 0 / 2", "scale-to-zero, max 2"],
    ["--timeout 300", "sessions WS longues"],
    ["--port 8080", "port fixe Cloud Run"],
  ], A.blue, [2.55, 3.3], 10);
  footer(s, "Source : README §18.3 — commande de déploiement + tableau des flags");
})();

(function () {
  const s = header(slide(), "Cloud Run — vérifier & démarrage à froid", "Tester le service et comprendre le cold start", A.blue, L.run, "PARTIE 2");
  lbl(s, 0.6, 1.45, "VÉRIFIER LE DÉPLOIEMENT", A.blue, 6);
  codeBox(s, 0.6, 1.8, 6.0, 2.5,
    "# URL du service\ngcloud run services describe \\\n  mgvaovao-inference \\\n  --region=us-central1 \\\n  --format=\"value(status.url)\"\n\n# Santé / disponibilité\ncurl $URL/health   # {\"status\":\"ok\"}\ncurl $URL/ready    # 503 puis 200\n# UI temps réel : $URL/live", 9.5);
  lbl(s, 6.9, 1.45, "DÉMARRAGE À FROID (60–120 s)", A.blue, 6);
  steps(s, 6.9, 1.85, 5.85, [
    { n: 1, t: "Conteneur + CUDA", d: "init driver (~10–15 s)" },
    { n: 2, t: "Port 8080 ouvert", d: "/health répond aussitôt" },
    { n: 3, t: "Chargement modèles", d: "pull GCS + VAD/ASR/MT/TTS" },
    { n: 4, t: "/ready → 200", d: "l'UI se débloque, micro auto" },
  ], A.blue, 0.92);
  callout(s, 0.6, 5.6, 12.1, 1.05, "ANTI COLD-START", "min-instances=0 éteint l'instance après ~15 min d'inactivité. Cloud Scheduler envoie un ping toutes les 15 min pendant les heures actives pour garder une instance chaude ; scale-to-zero la nuit/week-end.", A.blue);
  footer(s, "Source : README §18.3, §20 — vérification + comportement cold start");
})();

// ---------------- VERTEX AI ----------------
(function () {
  const s = header(slide(), "Vertex AI — concepts", "MLOps : entraînement, pipelines, registry", A.purple, L.vertex, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "Plateforme ML unifiée. Pour MGVaovao : exécute le fine-tuning NLLB (LoRA) et TTS (VITS) sur GPU cloud, orchestre le cycle via un pipeline Kubeflow, versionne les modèles (Model Registry) et surveille le drift (Model Monitoring).", 13.5);
  lbl(s, 0.6, 2.55, "COMPOSANTS UTILISÉS", A.purple, 6);
  bullets(s, 0.6, 2.9, 6.0, 2.3, [
    "Custom Training Jobs : votre code sur T4/L4",
    "Pipelines : DAG Kubeflow (6 étapes) — $0,03/run",
    "Model Registry : candidate → staging → prod (gratuit)",
    "Model Monitoring : drift chrF++ & UTMOS (~3 $/mois)",
    "Experiments : comparaison des runs (gratuit)",
  ], 12.5);
  lbl(s, 6.9, 2.55, "COÛT DU FINE-TUNING (T4 SPOT)", A.purple, 6);
  table(s, 6.9, 2.9, 5.85, ["Job", "Durée", "Coût"], [
    ["NLLB LoRA (5 ép.)", "4–6 h", "~1,7–2,5 $"],
    ["TTS VITS (50 ép.)", "2–3 h", "~0,84–1,3 $"],
  ], A.purple, [2.6, 1.6, 1.65], 10.5);
  callout(s, 0.6, 5.5, 12.1, 1.15, "SPOT + CHECKPOINTS", "Ajouter --scheduling=spot (~60 % moins cher, mais préemptible). Toujours sauvegarder un checkpoint vers GCS toutes les 30 min ; pull_checkpoints.py gère la reprise.", A.purple);
  footer(s, "Source : README §18.6, §20 — doc : cloud.google.com/vertex-ai/docs");
})();

(function () {
  const s = header(slide(), "Vertex AI — lancer un job de training", "Custom training pas-à-pas (NLLB / TTS)", A.purple, L.vertex, "PARTIE 2");
  steps(s, 0.6, 1.5, 5.7, [
    { n: 1, t: "Donner accès GCS au SA compute", d: "roles/storage.objectAdmin" },
    { n: 2, t: "Donner accès Artifact Registry", d: "roles/artifactregistry.reader" },
    { n: 3, t: "Lancer le custom-job", d: "machine + GPU + image + module" },
    { n: 4, t: "Suivre les logs", d: "stream-logs / Console" },
  ], A.purple, 1.05);
  codeBox(s, 6.6, 1.5, 6.15, 5.0,
    "# 3. Fine-tuning NLLB (dialecte betsileo)\ngcloud ai custom-jobs create \\\n  --region=us-central1 \\\n  --project=mgvaovao-ia \\\n  --display-name=\"nllb-ft-betsileo\" \\\n  --worker-pool-spec=\"\n      machine-type=n1-standard-8,\n      replica-count=1,\n      accelerator-type=NVIDIA_TESLA_T4,\n      accelerator-count=1,\n      executor-image-uri=\n        .../mgvaovao:cuda-latest,\n      local-package-path=.,\n      python-module=training.train_nllb\" \\\n  --args=\"--dialect=betsileo\"\n\n# 4. Suivre les logs\ngcloud ai custom-jobs stream-logs JOB_ID \\\n  --region=us-central1", 8.5);
  footer(s, "Source : README §18.6 — setup IAM Vertex + lancement custom-job (NLLB & TTS)");
})();

(function () {
  const s = header(slide(), "Vertex AI Pipeline — le DAG Kubeflow", "6 étapes : validate → fine-tune → eval → register → deploy", A.purple, L.vertex, "PARTIE 2");
  const stepsData = [
    { n: "1", t: "data_validation", d: "Cloud Run · $0", acc: A.blue },
    { n: "2", t: "nllb_finetune", d: "LoRA r=16 · L4 Spot", acc: A.green },
    { n: "3", t: "tts_finetune", d: "par dialecte · L4 Spot", acc: A.green },
    { n: "4", t: "evaluate", d: "Candidate vs Champion\nchrF++ · UTMOS", acc: A.amber },
    { n: "5", t: "register", d: "Model Registry · gratuit", acc: A.purple },
    { n: "6", t: "deploy", d: "Cloud Build → Run GPU", acc: A.red },
  ];
  const cw = 1.92, ch = 1.5, gap = 0.12, y = 1.7;
  stepsData.forEach((st, i) => {
    const x = 0.6 + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARD }, shadow: shadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.12, y: y + 0.12, w: 0.4, h: 0.4, fill: { color: st.acc.s } });
    s.addText(st.n, { x: x + 0.12, y: y + 0.12, w: 0.4, h: 0.4, fontFace: "Calibri", fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
    s.addText(st.t, { x: x + 0.6, y: y + 0.14, w: cw - 0.66, h: 0.4, fontFace: "Consolas", fontSize: 10, bold: true, color: TEXT, valign: "middle", margin: 0 });
    s.addText(st.d, { x: x + 0.12, y: y + 0.62, w: cw - 0.24, h: 0.8, fontFace: "Calibri", fontSize: 9.5, color: MUTED, valign: "top", margin: 0 });
    if (i < 5) s.addText("→", { x: x + cw - 0.06, y: y + 0.45, w: gap + 0.12, h: 0.5, fontFace: "Calibri", fontSize: 16, bold: true, color: A.slate.d, align: "center", valign: "middle", margin: 0 });
  });
  s.addText("Déclencheur : dataset validé dans GCS → Pub/Sub (topic dataset-ready) → le pipeline démarre", { x: 0.6, y: 3.4, w: 12.1, h: 0.4, fontFace: "Calibri", fontSize: 12, italic: true, color: MUTED, margin: 0 });
  lbl(s, 0.6, 3.95, "DÉCISION APRÈS ÉVALUATION", A.purple, 6);
  bullets(s, 0.6, 4.3, 6.0, 1.6, [
    "Régression détectée → ROLLBACK auto + alerte e-mail",
    "Pas de régression → register puis deploy (Blue/Green)",
    "Tous les runs comparés dans Vertex AI Experiments",
  ], 12.5);
  callout(s, 6.9, 4.0, 5.85, 2.0, "COÛT & SÉCURITÉ", "Pipeline ~0,03 $/run. Le déploiement est Blue/Green (zéro downtime) avec rollback automatique en cas de régression chrF++/UTMOS. Model Registry et Experiments sont gratuits.", A.purple);
  footer(s, "Source : README §20 — pipeline MLOps automatisé (Kubeflow DAG)");
})();

// ---------------- PUB/SUB ----------------
(function () {
  const s = header(slide(), "Pub/Sub — concepts & rôle", "Messagerie événementielle", A.red, L.pubsub, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.85, "Service de messagerie asynchrone qui découple producteurs et consommateurs. Dans MGVaovao, c'est le bus d'événements qui relie l'arrivée d'un dataset (ou la détection d'un drift) au démarrage du pipeline d'entraînement Vertex AI.", 13.5);
  lbl(s, 0.6, 2.55, "CONCEPTS CLÉS", A.red, 6);
  bullets(s, 0.6, 2.9, 6.0, 2.3, [
    "Topics & subscriptions (publishers / subscribers)",
    "Livraison push ou pull, au moins une fois",
    "Découplage & scalabilité, latence ~100 ms",
    "Topic du projet : dataset-ready",
  ], 13);
  lbl(s, 6.9, 2.55, "LES 2 DÉCLENCHEURS", A.red, 6);
  codeBox(s, 6.9, 2.9, 5.85, 1.85,
    "# Flux 2d — nouveau dataset\nGCS (upload) -> Pub/Sub\n  -> Vertex AI Pipeline\n\n# Flux 2f — drift détecté\nScheduler -> Monitoring\n  -> Pub/Sub -> re-fine-tuning", 10);
  callout(s, 0.6, 5.45, 12.1, 1.1, "POURQUOI UN BUS D'ÉVÉNEMENTS ?", "Le producteur (GCS / Monitoring) n'a pas besoin de connaître le consommateur (Vertex). On peut ajouter de nouveaux abonnés (alertes, logs) sans toucher au producteur — architecture découplée et robuste.", A.red);
  footer(s, "Source : README §5.2, §7 (flux 2d/2f), §20 — doc : cloud.google.com/pubsub/docs");
})();

// ---------------- CLOUD LOGGING ----------------
(function () {
  const s = header(slide(), "Cloud Logging — concepts & debug", "Journalisation centralisée", A.blue, L.logging, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.7, "Gestion de logs temps réel : stockage, recherche, analyse. Les builds (CLOUD_LOGGING_ONLY) et les services Cloud Run y envoient leurs logs, consultables en CLI ou dans Logs Explorer.", 13);
  lbl(s, 0.6, 2.35, "LIRE LES LOGS CLOUD RUN", A.blue, 6);
  codeBox(s, 0.6, 2.7, 6.1, 2.6,
    "gcloud logging read \\\n \"resource.type=cloud_run_revision \\\n  AND resource.labels.service_name=\\\n  mgvaovao-inference \\\n  AND severity>=ERROR\" \\\n  --project=mgvaovao-ia \\\n  --limit=20 --freshness=1h", 9.5);
  lbl(s, 6.9, 2.35, "MOTIFS DE LOG À CONNAÎTRE", A.blue, 6);
  table(s, 6.9, 2.7, 5.85, ["Ligne de log", "Sens"], [
    ["Model loading started…", "cold start, port ouvert"],
    ["All pipelines loaded", "/ready = 200"],
    ["WS open — dialect=…", "session WebSocket"],
    ["VAD state=speaking", "parole détectée"],
    ["KeyError: 'bytes'", "BUG (voir fixes)"],
  ], A.blue, [2.85, 3.0], 9.5);
  callout(s, 0.6, 5.6, 12.1, 1.0, "CONSOLE", "Pour explorer visuellement : console.cloud.google.com/run → service → onglet Logs. Filtres par sévérité, requêtes sauvegardées, et trace associée aux entrées.", A.blue);
  footer(s, "Source : README §18.4 — lecture des logs + motifs courants");
})();

// ---------------- CLOUD MONITORING ----------------
(function () {
  const s = header(slide(), "Cloud Monitoring — supervision & drift", "Métriques, alertes et seuils", A.green, L.monitoring, "PARTIE 2");
  para(s, 0.6, 1.45, 12.1, 0.7, "Observabilité : métriques, dashboards, uptime checks et politiques d'alertes. Combiné à Vertex AI Monitoring, il surveille la santé du service ET la qualité des modèles (drift) en production.", 13);
  lbl(s, 0.6, 2.3, "SEUILS DE DRIFT & ACTIONS AUTOMATIQUES", A.green, 8);
  table(s, 0.6, 2.65, 12.1, ["Métrique", "Seuil d'alerte", "Action automatique"], [
    ["chrF++ (200 phrases de référence)", "Baisse > 2 points", "Re-fine-tuning NLLB via Pub/Sub"],
    ["UTMOS (50 phrases audio)", "Baisse > 0,3", "Re-fine-tuning TTS via Pub/Sub"],
    ["Taux d'erreur WebRTC", "> 5 %", "Alerte e-mail + investigation infra"],
    ["Latence P95 du pipeline", "> 2000 ms", "Alerte e-mail + Cloud Monitoring"],
  ], A.green, [4.5, 2.8, 4.8], 11);
  callout(s, 0.6, 5.6, 12.1, 1.0, "PRÉ-CHAUFFAGE & SUIVI", "Cloud Scheduler ping Cloud Run GPU toutes les 15 min (anti cold-start). Évaluation de drift hebdomadaire. Tous les runs d'entraînement sont tracés dans Vertex AI Experiments (gratuit).", A.green);
  footer(s, "Source : README §20 — seuils de drift + stratégie de pré-chauffage · doc : cloud.google.com/monitoring/docs");
})();

// =====================================================================
// PARTIE 3 — CYCLE DE VIE & EXPLOITATION
// =====================================================================
divider("03", "Cycle de vie & exploitation", "Partie 3 — MLOps, dépannage, coûts & migration", A.green,
  [L.vertex, L.build, L.run, L.monitoring, L.pubsub]);

// --- GitHub auto-trigger ---
(function () {
  const s = header(slide(), "GitHub → Cloud Build (auto-trigger)", "Déploiement automatique à chaque push", A.amber, L.build, "PARTIE 3");
  steps(s, 0.6, 1.5, 6.0, [
    { n: 1, t: "Connecter le dépôt GitHub", d: "Console Cloud Build → Connect → autoriser" },
    { n: 2, t: "Créer le déclencheur", d: "branche ^main$ · cloudbuild-inference.yaml" },
    { n: 3, t: "Vérifier", d: "builds triggers list" },
  ], A.amber, 1.0);
  codeBox(s, 6.9, 1.5, 5.85, 3.4,
    "gcloud builds triggers create github \\\n  --project=mgvaovao-ia \\\n  --region=global \\\n  --name=\"deploy-inference-on-push\" \\\n  --repo-owner=mgvaovao-Mdn \\\n  --repo-name=ml \\\n  --branch-pattern=\"^main$\" \\\n  --build-config=\\\n    cloudbuild-inference.yaml", 9.5);
  callout(s, 0.6, 5.0, 12.1, 1.4, "AVEC LE DÉCLENCHEUR", "Chaque git push origin main : build (cache ~5–10 min) → push Artifact Registry → deploy Cloud Run GPU. $SHORT_SHA est rempli automatiquement (pas besoin de --substitutions). Sans déclencheur : toujours passer SHORT_SHA manuellement.", A.amber);
  footer(s, "Source : README §18.7 — GitHub → Cloud Build trigger");
})();

// --- Known issues ---
(function () {
  const s = header(slide(), "Problèmes connus & correctifs", "Bugs rencontrés au premier déploiement", A.red, null, "PARTIE 3");
  const bugs = [
    { t: "Bug 1 — KeyError: 'bytes' à la déconnexion", c: "# stream.py — frame disconnect sans clé bytes\nif msg.get(\"type\")==\"websocket.disconnect\":\n    break\nraw = msg.get(\"bytes\") or b\"\"" },
    { t: "Bug 2 — Silero VAD ne se déclenche jamais", c: "# config.py — seuil trop strict\nvad_threshold = 0.3            # au lieu de 0.5\nvad_stream_min_silence_ms = 400  # au lieu de 500" },
    { t: "Bug 3 — SHORT_SHA vide (build manuel)", c: "# image:  → tag vide → invalid image name\n--substitutions=SHORT_SHA=$(git \\\n  rev-parse --short HEAD)" },
  ];
  let y = 1.5;
  bugs.forEach((b) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 0.12, h: 1.55, fill: { color: A.red.s } });
    s.addText(b.t, { x: 0.85, y: y + 0.02, w: 11.8, h: 0.35, fontFace: "Calibri", fontSize: 14, bold: true, color: A.red.d, margin: 0 });
    codeBox(s, 0.85, y + 0.42, 11.85, 1.05, b.c, 10);
    y += 1.75;
  });
  footer(s, "Source : README §18.9 — correctifs appliqués (à ne pas refaire)");
})();

// --- Variables & migration ---
(function () {
  const s = header(slide(), "Variables & migration", "Tout ce qu'il faut sauvegarder", A.slate, null, "PARTIE 3");
  lbl(s, 0.6, 1.4, "VARIABLES CLÉS DU PROJET", A.slate, 8, 12);
  table(s, 0.6, 1.75, 6.3, ["Variable", "Valeur"], [
    ["GCP_PROJECT_ID", "mgvaovao-ia"],
    ["GCP_PROJECT_NUMBER", "97374817504"],
    ["GCP_REGION / ZONE", "us-central1 / -a"],
    ["AR_REPO", "mgvaovao"],
    ["GCS_BUCKET_MODELS", "mgvaovao-ia-checkpoints"],
    ["CLOUDRUN_SERVICE", "mgvaovao-inference"],
  ], A.slate, [3.0, 3.3], 10);
  lbl(s, 7.2, 1.4, "MIGRER VERS UN NOUVEAU PROJET", A.slate, 6, 12);
  steps(s, 7.2, 1.8, 5.5, [
    { n: 1, t: "Nouveau projet + facturation" },
    { n: 2, t: "Activer les APIs (§18.1)" },
    { n: 3, t: "Artifact Registry + buckets GCS" },
    { n: 4, t: "Recréer SA + rôles IAM" },
    { n: 5, t: "Transférer les checkpoints (gsutil)" },
    { n: 6, t: "1er build (~45–60 min) + vérifier" },
  ], A.slate, 0.62, 12);
  footer(s, "Source : README §18.10, §18.11 — variables & checklist de migration");
})();

// --- Coûts ---
(function () {
  const s = header(slide(), "Coûts", "Budget bêta ~42 $/mois (< 100 users/jour)", A.green, null, "PARTIE 3");
  lbl(s, 0.6, 1.4, "RÉPARTITION MENSUELLE", A.green, 8, 12);
  table(s, 0.6, 1.75, 6.3, ["Poste", "Coût/mois"], [
    ["Cloud Run GPU L4 (50 h)", "33,60 $"],
    ["Vertex AI Monitoring", "3,00 $"],
    ["Vertex Custom Training (2/mois)", "2,24 $"],
    ["Cloud Run CPU (signaling)", "2,00 $"],
    ["Cloud Storage (50 GB)", "1,00 $"],
    ["Artifact Registry", "0,50 $"],
    ["Pipelines · Registry · Build", "~0,12 $"],
    ["TOTAL", "~42 $/mois"],
  ], A.green, [4.0, 2.3], 10);
  lbl(s, 7.2, 1.4, "OPTIMISATIONS ACTIVES", A.green, 6, 12);
  bullets(s, 7.2, 1.8, 5.5, 2.6, [
    "Scale-to-zero (Cloud Run) : 0 € hors heures actives",
    "Spot instances (fine-tuning) : −60 % à −91 %",
    "INT8 (CTranslate2) : −50 % VRAM, ×2 vitesse",
    "Kaggle T4 ×2 gratuit : 30 h/semaine",
    "LoRA (vs full FT) : fraction des paramètres",
  ], 12.5);
  callout(s, 7.2, 4.6, 5.5, 1.85, "ÉVOLUTION PAR PHASE", "Bêta < 100 u/j : ~42 $. Croissance 100–500 u/j : ~100 $. Production > 500 u/j : ~500 $+ → migrer vers un Vertex AI Endpoint.", A.green);
  footer(s, "Source : README §21 — référence de coûts");
})();

// --- Roadmap ---
(function () {
  const s = header(slide(), "Feuille de route", "Où en est le projet", A.purple, null, "PARTIE 3");
  table(s, 0.6, 1.55, 12.1, ["Phase", "Statut", "Livrables clés"], [
    ["1 — Baseline", "✅ Fait", "Pipeline VAD→ASR→NLLB→TTS · WebSocket · UI temps réel · images Docker"],
    ["2 — Cloud Deploy", "🔄 En cours (Q2 2026)", "Cloud Run GPU L4 · buckets GCS · 1er pipeline Vertex · Model Registry"],
    ["3 — Fine-Tuning v1", "⏳ Q2–Q3 2026", "3 000 paires FR/EN↔MG · NLLB LoRA · 200 phrases audio · MMS-TTS Officiel"],
    ["4 — Multi-dialecte", "⏳ Q3–Q4 2026", "3 dialectes ×200 phrases · drift monitoring live · app Flutter v1"],
    ["5 — Scale", "⏳ 2027", "API REST publique · 6 dialectes · NLLB 1.3B · migration Vertex Endpoint"],
  ], A.purple, [2.0, 2.3, 7.8], 11);
  footer(s, "Source : README §22 — roadmap technique 2025–2027");
})();

// --- Ressources finale ---
(function () {
  const s = slide("dark");
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.16, fill: { color: A.blue.s } });
  s.addText("RESSOURCES & DOCUMENTATION OFFICIELLE", { x: 0.9, y: 0.55, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, bold: true, color: A.blue.l, charSpacing: 2, margin: 0 });
  s.addText("Pour aller plus loin", { x: 0.9, y: 0.95, w: 11.5, h: 0.7, fontFace: "Georgia", fontSize: 30, bold: true, color: "FFFFFF", margin: 0 });
  const items = [
    [L.run, "Cloud Run", "cloud.google.com/run/docs"],
    [L.gpu, "Cloud Run GPU", "cloud.google.com/run/docs/configuring/services/gpu"],
    [L.storage, "Cloud Storage", "cloud.google.com/storage/docs"],
    [L.compute, "Compute Engine", "cloud.google.com/compute/docs"],
    [L.vertex, "Vertex AI", "cloud.google.com/vertex-ai/docs"],
    [L.build, "Cloud Build", "cloud.google.com/build/docs"],
    [L.artifact, "Artifact Registry", "cloud.google.com/artifact-registry/docs"],
    [L.pubsub, "Pub/Sub", "cloud.google.com/pubsub/docs"],
    [L.logging, "Cloud Logging", "cloud.google.com/logging/docs"],
    [L.monitoring, "Cloud Monitoring", "cloud.google.com/monitoring/docs"],
    [L.iam, "IAM", "cloud.google.com/iam/docs"],
    [L.secret, "Secret Manager", "cloud.google.com/secret-manager/docs"],
  ];
  gcpChip(s, 10.3, 0.5, 2.4);
  const colW = 5.85, rowH = 0.62, x0 = 0.9, y0 = 1.95, lg = 0.4;
  items.forEach((m, i) => {
    const col = Math.floor(i / 6), row = i % 6;
    const x = x0 + col * (colW + 0.6), y = y0 + row * rowH;
    s.addImage({ path: LOGO(m[0]), x, y: y + 0.02, w: lg, h: lg });
    s.addText([
      { text: m[1] + "  ", options: { fontFace: "Calibri", fontSize: 12.5, bold: true, color: "FFFFFF" } },
      { text: m[2], options: { fontFace: "Consolas", fontSize: 9.5, color: "8FB4F2" } },
    ], { x: x + lg + 0.15, y, w: colW - lg - 0.18, h: rowH, valign: "middle", margin: 0 });
  });
  s.addText("Réf. README §24 : Cloud Run GPU GA (juin 2025) · Vertex AI pricing · NLLB-200 · MMS-TTS-MLG · Silero VAD · CTranslate2 · aiortc", { x: 0.9, y: 5.95, w: 11.6, h: 0.5, fontFace: "Calibri", fontSize: 10.5, color: "8FA0C4", margin: 0 });
  s.addText("MGVaovao — Maison du Numérique · Antananarivo · Projet mgvaovao-ia · Architecture Google Cloud", { x: 0.9, y: 6.85, w: 11.6, h: 0.4, fontFace: "Calibri", fontSize: 12, italic: true, color: "8A97B8", margin: 0 });
})();

stampLogos();
pres.writeFile({ fileName: "MGVaovao_Tutoriel_GCP_FR.pptx" }).then((f) => console.log("OK ->", f));
