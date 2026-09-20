# -*- coding: utf-8 -*-
"""
Verifie qu'une instance de la demonstration repond correctement.

    python scripts/verifier_demo.py                      # instance locale
    python scripts/verifier_demo.py --url https://...    # instance deployee
    python scripts/verifier_demo.py --quotas             # eprouve aussi les refus

Le deploiement etait jusqu'ici declare bon sur la seule reussite de Cloud
Build. Un build vert n'a jamais garanti qu'une phrase prononcee revienne
traduite : il faut ouvrir le WebSocket, envoyer de l'audio et attendre le
resultat. C'est ce que fait ce script.

Il sort avec un code non nul si une verification echoue, pour servir de sonde
apres deploiement comme dans une supervision periodique.

`--quotas` eprouve en plus les refus : il ouvre plus de sessions que la limite
et attend un refus motive. A n'utiliser qu'en connaissance de cause — les
sessions ouvertes pour ce test consomment quelques secondes du budget du jour.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np
import requests
import websockets

RACINE = Path(__file__).resolve().parent.parent

# Phrase servant d'essai. Courte, et dans une langue que le modele de
# reconnaissance traite bien : le but est de verifier que la chaine repond, pas
# d'evaluer sa qualite.
PHRASE_ESSAI = "Bonjour, comment allez-vous aujourd'hui ?"

# L'echantillon est produit par le service lui-meme, via /translate/text.
#
# Le depot contient bien des fichiers `test_*.wav`, mais ils sont silencieux :
# le detecteur d'activite vocale n'y trouvait aucune parole, ne signalait donc
# jamais de fin de tour, et la verification echouait sur un defaut de
# l'echantillon en accusant le service. Faire synthetiser la voix par le
# service garantit un echantillon parlant, au bon format, sans ajouter de
# fichier binaire au depot — et eprouve au passage la voie REST.
CACHE_VOIX = Path(tempfile.gettempdir()) / "mgvaovao_voix_essai.wav"

# Le pipeline complet (VAD, ASR, traduction, synthese) prend quelques secondes,
# et davantage sur une instance qui vient de demarrer a froid.
ATTENTE_RESULTAT_S = 180


class Echec(Exception):
    pass


# ── sortie ────────────────────────────────────────────────────────────────

class Journal:
    def __init__(self) -> None:
        self.echecs: list[str] = []

    def ok(self, titre: str, detail: str = "") -> None:
        print(f"  ok      {titre}{('  — ' + detail) if detail else ''}")

    def echec(self, titre: str, raison: str) -> None:
        print(f"  ECHEC   {titre}  — {raison}")
        self.echecs.append(f"{titre} : {raison}")

    def info(self, texte: str) -> None:
        print(f"          {texte}")


def verifier(journal: Journal, titre: str, fn) -> object | None:
    """Execute une verification en rapportant son issue plutot qu'en s'arretant."""
    try:
        resultat = fn()
    except Echec as exc:
        journal.echec(titre, str(exc))
        return None
    except Exception as exc:  # pragma: no cover - filet
        journal.echec(titre, f"{type(exc).__name__}: {exc}")
        return None
    detail = resultat if isinstance(resultat, str) else ""
    journal.ok(titre, detail)
    return resultat


# ── verifications HTTP ────────────────────────────────────────────────────

def http(base: str, chemin: str, attendu: int = 200) -> dict:
    reponse = requests.get(f"{base}{chemin}", timeout=60)
    if reponse.status_code != attendu:
        raise Echec(f"{chemin} a repondu {reponse.status_code}, attendu {attendu}")
    try:
        return reponse.json()
    except ValueError:
        raise Echec(f"{chemin} n'a pas renvoye du JSON") from None


def verifier_sante(base: str) -> str:
    corps = http(base, "/health")
    if corps.get("status") != "ok":
        raise Echec(f"status = {corps.get('status')!r}")
    return "service en vie"


def verifier_modeles(base: str) -> str:
    reponse = requests.get(f"{base}/ready", timeout=120)
    if reponse.status_code == 503:
        # Le demarrage a froid prend une quarantaine de secondes : ce n'est pas
        # une panne, mais il faut le dire, sinon la suite echoue sans raison
        # apparente.
        raise Echec("modeles encore en chargement (demarrage a froid ?)")
    if reponse.status_code != 200:
        raise Echec(f"/ready a repondu {reponse.status_code}")
    charges = reponse.json().get("loaded_dialects") or []
    if not charges:
        raise Echec("aucun dialecte charge")
    return f"{len(charges)} dialecte(s) : {', '.join(charges)}"


def verifier_dialectes(base: str) -> str:
    corps = http(base, "/dialects")
    dialectes = corps if isinstance(corps, list) else corps.get("dialects") or []
    if not dialectes:
        raise Echec("liste de dialectes vide")
    return f"{len(dialectes)} annonce(s)"


def verifier_quotas(base: str) -> dict:
    corps = http(base, "/quotas")
    limites = corps.get("limites") or {}
    manquantes = [
        c for c in ("sessions_par_ip", "rafale", "duree_max_session_s", "silence_max_s")
        if c not in limites
    ]
    if manquantes:
        raise Echec(f"limites absentes de la reponse : {manquantes}")
    if corps.get("budget_global_restant_s", 0) <= 0:
        raise Echec("budget global du jour epuise")
    return corps


# ── verification WebSocket ────────────────────────────────────────────────

def obtenir_voix(base: str, dialecte: str, journal: Journal) -> Path:
    """
    Rend un fichier WAV parlant, en le faisant synthetiser au besoin.

    Le resultat est garde dans le repertoire temporaire : relancer la
    verification ne refait pas travailler le GPU pour rien.
    """
    if CACHE_VOIX.is_file() and CACHE_VOIX.stat().st_size > 10_000:
        return CACHE_VOIX

    journal.info("synthese d'un echantillon de voix par le service…")
    reponse = requests.post(
        f"{base}/translate/text",
        json={"text": PHRASE_ESSAI, "dialect": dialecte, "src_lang": "fr"},
        timeout=ATTENTE_RESULTAT_S,
    )
    if reponse.status_code != 200:
        raise Echec(f"/translate/text a repondu {reponse.status_code}")
    url = (reponse.json() or {}).get("audio_url")
    if not url:
        raise Echec("/translate/text n'a pas renvoye d'audio_url")

    fichier = requests.get(url, timeout=120)
    if fichier.status_code != 200:
        raise Echec(f"audio_url a repondu {fichier.status_code}")
    CACHE_VOIX.write_bytes(fichier.content)
    return CACHE_VOIX


def charger_audio(chemin: Path) -> bytes:
    """Lit un WAV mono 16 kHz et le rend en Float32 PCM, le format attendu."""
    with wave.open(str(chemin), "rb") as w:
        if w.getframerate() != 16_000 or w.getnchannels() != 1:
            raise Echec("l'echantillon doit etre mono a 16 kHz")
        brut = w.readframes(w.getnframes())
    entiers = np.frombuffer(brut, dtype=np.int16).astype(np.float32) / 32768.0
    if float(np.abs(entiers).max()) < 0.01:
        # Un echantillon muet ferait echouer la verification pour une raison
        # qui n'a rien a voir avec le service.
        raise Echec(f"echantillon silencieux : {chemin}")
    return entiers.tobytes()


def url_ws(base: str, chemin: str) -> str:
    return base.replace("https://", "wss://").replace("http://", "ws://") + chemin


async def _un_aller_retour(base: str, dialecte: str, voix: Path, journal: Journal) -> str:
    pcm = charger_audio(voix)
    # Des trames de vingt millisecondes, comme en envoie le navigateur. Un seul
    # bloc d'un coup ne ferait pas travailler le detecteur d'activite vocale de
    # la meme facon, et ne testerait donc pas le chemin reel.
    taille = 320 * 4
    trames = [pcm[i:i + taille] for i in range(0, len(pcm), taille)]

    async with websockets.connect(
        url_ws(base, f"/ws/stream/{dialecte}"), max_size=None, open_timeout=60
    ) as ws:
        for trame in trames:
            await ws.send(trame)
            await asyncio.sleep(0.02)

        # Du silence apres la parole : c'est lui qui declenche la fin de tour.
        silence = np.zeros(320, dtype=np.float32).tobytes()
        for _ in range(60):
            await ws.send(silence)
            await asyncio.sleep(0.02)

        debut = time.time()
        vus: set[str] = set()
        while time.time() - debut < ATTENTE_RESULTAT_S:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10)
            except asyncio.TimeoutError:
                # Rien ne vient : on relance du silence pour laisser le VAD
                # conclure, plutot que d'abandonner trop tot.
                await ws.send(silence)
                continue

            if isinstance(message, bytes):
                continue
            try:
                donnees = json.loads(message)
            except ValueError:
                continue

            genre = donnees.get("type")
            vus.add(genre)

            if genre == "loading":
                journal.info("modeles en cours de chargement, patience…")
            elif genre == "error":
                raise Echec(
                    f"erreur du serveur ({donnees.get('code', 'sans code')}) : "
                    f"{donnees.get('message')}"
                )
            elif genre == "result" or donnees.get("audio_b64"):
                if not donnees.get("audio_b64"):
                    raise Echec("resultat sans audio synthetise")
                texte = donnees.get("malagasy_text") or donnees.get("text") or ""
                secondes = round(time.time() - debut, 1)
                return f"reponse en {secondes} s — « {texte[:60]} »"

        raise Echec(
            f"aucun resultat en {ATTENTE_RESULTAT_S} s "
            f"(messages recus : {sorted(vus) or 'aucun'})"
        )


async def _refus_attendu(base: str, dialecte: str, limite: int) -> str:
    """
    Ouvre une session de plus que la limite et attend un refus motive.

    Verifie ce qui compte vraiment : que le refus arrive avec un code et un
    message, et non par une coupure brute que le navigateur ne sait pas
    expliquer a la personne.
    """
    ouvertes = []
    try:
        for _ in range(limite):
            ouvertes.append(
                await websockets.connect(
                    url_ws(base, f"/ws/stream/{dialecte}"), open_timeout=60
                )
            )

        async with websockets.connect(
            url_ws(base, f"/ws/stream/{dialecte}"), open_timeout=60
        ) as excedent:
            try:
                message = await asyncio.wait_for(excedent.recv(), timeout=30)
            except asyncio.TimeoutError:
                raise Echec("la session excedentaire a ete acceptee sans refus") from None
            donnees = json.loads(message)
            if donnees.get("type") != "error":
                raise Echec(f"message inattendu : {donnees.get('type')!r}")
            if not donnees.get("code"):
                raise Echec("refus sans code exploitable")
            if not donnees.get("message"):
                raise Echec("refus sans message pour la personne")
            return f"refus « {donnees['code']} » recu comme prevu"
    finally:
        for ws in ouvertes:
            await ws.close()


# ── enchainement ──────────────────────────────────────────────────────────

def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--url", default="http://localhost:8080", help="base du service")
    analyseur.add_argument("--dialecte", default="plt_latn", help="dialecte a eprouver")
    analyseur.add_argument(
        "--quotas",
        action="store_true",
        help="eprouve aussi le refus au-dela de la limite de sessions",
    )
    analyseur.add_argument(
        "--audio",
        help="WAV mono 16 kHz a envoyer ; a defaut, le service synthetise l'echantillon",
    )
    analyseur.add_argument(
        "--sans-audio",
        action="store_true",
        help="s'en tient aux verifications HTTP, sans solliciter le GPU",
    )
    args = analyseur.parse_args()
    base = args.url.rstrip("/")

    journal = Journal()
    print(f"\nVerification de {base}\n")

    verifier(journal, "service en vie", lambda: verifier_sante(base))
    modeles = verifier(journal, "modeles charges", lambda: verifier_modeles(base))
    verifier(journal, "dialectes annonces", lambda: verifier_dialectes(base))
    etat = verifier(journal, "quotas actifs", lambda: verifier_quotas(base))

    if isinstance(etat, dict):
        limites = etat["limites"]
        journal.info(
            f"limites : {limites['sessions_par_ip']} session(s)/adresse, "
            f"{limites['rafale']} ouverture(s)/{limites['rafale_fenetre_s']} s, "
            f"session {limites['duree_max_session_s']} s, "
            f"silence {limites['silence_max_s']} s"
        )
        journal.info(
            f"budget du jour : {etat['budget_global_restant_s']:.0f} s restantes "
            f"sur {etat['budget_global_s']} s"
        )

    # L'aller-retour audio n'a de sens que si les modeles sont la : sans eux il
    # echouerait pour une raison deja rapportee plus haut.
    if args.sans_audio:
        journal.info("aller-retour audio ignore (--sans-audio)")
    elif modeles is None:
        journal.info("aller-retour audio ignore : modeles indisponibles")
    else:
        voix = (
            Path(args.audio)
            if args.audio
            else verifier(
                journal,
                "synthese d'un echantillon (voie REST)",
                lambda: obtenir_voix(base, args.dialecte, journal),
            )
        )
        if voix is None:
            journal.info("aller-retour audio ignore : pas d'echantillon")
        else:
            verifier(
                journal,
                "aller-retour audio complet",
                lambda: asyncio.run(_un_aller_retour(base, args.dialecte, voix, journal)),
            )

    if args.quotas and isinstance(etat, dict):
        limite = etat["limites"]["sessions_par_ip"]
        verifier(
            journal,
            "refus au-dela de la limite de sessions",
            lambda: asyncio.run(_refus_attendu(base, args.dialecte, limite)),
        )

    print()
    if journal.echecs:
        print(f"{len(journal.echecs)} verification(s) en echec :")
        for e in journal.echecs:
            print(f"  - {e}")
        return 1
    print("Toutes les verifications passent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
