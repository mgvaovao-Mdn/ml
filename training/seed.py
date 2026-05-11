#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_download_data.py  —  Seed the dataset folder with example data.

This script creates the exact folder structure and file format that data
collectors must follow, populated with 5 example entries per dialect so
the team can see precisely what to provide.

Replace the example files with real collected data — DO NOT modify the
folder structure or the file format (column names, JSON keys, delimiter).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FOLDER STRUCTURE  (created by this script)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  dataset/
  ├── nllb_finetune/
  │   └── {dialect}/
  │       └── raw/
  │           ├── fr/
  │           │   └── data.jsonl       <- French  -> Malagasy dialect pairs
  │           └── en/
  │               └── data.jsonl       <- English -> Malagasy dialect pairs
  │
  └── tts_finetune/
      └── {dialect}/
          └── raw_audio/
              ├── transcripts.csv      <- file_name | text | speaker_id
              ├── example_001.wav      <- speaker recording (16kHz mono WAV)
              ├── example_002.wav
              └── ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HOW DATA COLLECTORS ADD REAL DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  NLLB (text translation pairs):
    Add .jsonl files alongside examples.jsonl in raw/fr/ and raw/en/.
    Each line: {"source": "...", "target": "...", "src_lang": "fr", "dialect": "betsileo"}

  TTS (audio recordings):
    Add WAV files (16kHz mono) to raw_audio/.
    Add their filenames + transcripts to transcripts.csv (append rows).

  Then run:
    python scripts/02b_preprocess.py --dialect betsileo
    python scripts/03_finetune_nllb.py --dialect betsileo
    python scripts/04_finetune_tts.py  --dialect betsileo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usage:
    python scripts/02_download_data.py               # all 4 dialects
    python scripts/02_download_data.py --dialect betsileo
"""

import sys, os, json, csv, argparse, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE DATA  --  5 pairs per dialect per language + 5 audio sentences
#
# These are realistic examples showing the expected format and vocabulary
# level. Replace with real collected data from native speakers.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES = {

    # ── Malagasy Officiel (Merina / Plateau) ──────────────────────────
    # Standard written and broadcast Malagasy, spoken in Antananarivo.
    # Reference dialect for all fine-tuning -- replace with field-collected
    # conversational data covering everyday topics.

    "plt_latn": {
        "fr": [
            {
                "source":  "Bonjour, comment allez-vous aujourd'hui ?",
                "target":  "Manao ahoana ianao androany ?",
                "note":    "Salutation quotidienne -- registre courant"
            },
            {
                "source":  "L'eau potable est essentielle pour la sante.",
                "target":  "Ilaina ho an'ny fahasalamana ny rano fisotro madio.",
                "note":    "Theme sante publique"
            },
            {
                "source":  "Les enfants vont a l'ecole chaque matin.",
                "target":  "Mandeha any am-pianarana ny ankizy isan'andro maraina.",
                "note":    "Theme education -- vie quotidienne"
            },
            {
                "source":  "Le marche ouvre tot le matin et ferme a midi.",
                "target":  "Misokatra maraina koa ny tsena ary mihidy amin'ny antoandro.",
                "note":    "Theme commerce -- horaires"
            },
            {
                "source":  "Je voudrais reserver une chambre pour deux nuits.",
                "target":  "Te hisintona efitrano roa alina aho.",
                "note":    "Theme tourisme -- hotellerie"
            },
        ],
        "en": [
            {
                "source":  "Good morning, how are you today?",
                "target":  "Manao ahoana ianao androany ?",
                "note":    "Daily greeting -- common register"
            },
            {
                "source":  "Clean drinking water is essential for good health.",
                "target":  "Ilaina ho an'ny fahasalamana ny rano fisotro madio.",
                "note":    "Topic: public health"
            },
            {
                "source":  "Children go to school every morning.",
                "target":  "Mandeha any am-pianarana ny ankizy isan'andro maraina.",
                "note":    "Topic: education -- daily life"
            },
            {
                "source":  "The market opens early and closes at noon.",
                "target":  "Misokatra maraina koa ny tsena ary mihidy amin'ny antoandro.",
                "note":    "Topic: commerce -- schedules"
            },
            {
                "source":  "I would like to book a room for two nights.",
                "target":  "Te hisintona efitrano roa alina aho.",
                "note":    "Topic: tourism -- hotel"
            },
        ],
        "tts": [
            "Manao ahoana ianao androany ?",
            "Ilaina ho an'ny fahasalamana ny rano fisotro madio.",
            "Mandeha any am-pianarana ny ankizy isan'andro maraina.",
            "Misokatra maraina koa ny tsena ary mihidy amin'ny antoandro.",
            "Te hisintona efitrano roa alina aho.",
        ],
    },

    # ── Betsileo (Fianarantsoa -- Hautes Terres Sud) ───────────────────
    # Betsileo dialect differs from standard Malagasy in vocabulary and
    # some phonology. Key differences: "manahoana" (greeting), "afaka"
    # (please/excuse me), verb forms may vary.
    # Collect from native speakers in Fianarantsoa, Ambalavao, Ambositra.

    "betsileo": {
        "fr": [
            {
                "source":  "Bonjour, comment allez-vous ?",
                "target":  "Manahoana ianao ?",
                "note":    "Salutation -- forme Betsileo, differente du standard"
            },
            {
                "source":  "Je vais au marche acheter du riz.",
                "target":  "Handeha any am-tsena hividy vary aho.",
                "note":    "Activite quotidienne -- marche, nourriture"
            },
            {
                "source":  "Il fait froid ce matin dans les montagnes.",
                "target":  "Mangatsiaka amin'ity maraina ity any an-tendrombohitra.",
                "note":    "Meteo -- specifique region montagneuse Betsileo"
            },
            {
                "source":  "Nous cultivons le riz dans les rizieres en terrasses.",
                "target":  "Mamboly vary any amin'ny tanimbary an-tsaha izahay.",
                "note":    "Agriculture -- riziculture en terrasses, Fianarantsoa"
            },
            {
                "source":  "Pouvez-vous me montrer le chemin vers l'hopital ?",
                "target":  "Afaka asehonao ahy ny lalana mankany am-pitsaboana ve ?",
                "note":    "Sante -- orientation -- utilisation de afaka (Betsileo)"
            },
        ],
        "en": [
            {
                "source":  "Hello, how are you?",
                "target":  "Manahoana ianao ?",
                "note":    "Greeting -- Betsileo form"
            },
            {
                "source":  "I am going to the market to buy rice.",
                "target":  "Handeha any am-tsena hividy vary aho.",
                "note":    "Daily activity -- market, food"
            },
            {
                "source":  "It is cold this morning in the mountains.",
                "target":  "Mangatsiaka amin'ity maraina ity any an-tendrombohitra.",
                "note":    "Weather -- mountain region specific"
            },
            {
                "source":  "We grow rice in terraced rice fields.",
                "target":  "Mamboly vary any amin'ny tanimbary an-tsaha izahay.",
                "note":    "Agriculture -- terraced rice farming, Fianarantsoa"
            },
            {
                "source":  "Can you show me the way to the hospital?",
                "target":  "Afaka asehonao ahy ny lalana mankany am-pitsaboana ve ?",
                "note":    "Health -- directions -- uses afaka (Betsileo)"
            },
        ],
        "tts": [
            "Manahoana ianao ?",
            "Handeha any am-tsena hividy vary aho.",
            "Mangatsiaka amin'ity maraina ity any an-tendrombohitra.",
            "Mamboly vary any amin'ny tanimbary an-tsaha izahay.",
            "Afaka asehonao ahy ny lalana mankany am-pitsaboana ve ?",
        ],
    },

    # ── Betsimisaraka (Cote Est -- Toamasina / Tamatave) ──────────────
    # Spoken along the entire east coast. Vocabulary influenced by the
    # sea, fishing, and port trade. Distinct from plateau Malagasy.
    # Collect from native speakers in Toamasina, Fenerive-Est, Maroantsetra.

    "betsimisaraka": {
        "fr": [
            {
                "source":  "Bonjour, comment allez-vous ?",
                "target":  "Manahoana ianao ?",
                "note":    "Salutation -- forme Betsimisaraka cotiere"
            },
            {
                "source":  "Les pecheurs partent tot le matin en mer.",
                "target":  "Mivoaka any an-dranomasina maraina koa ny mpanjono.",
                "note":    "Peche -- activite principale cote est"
            },
            {
                "source":  "Le port de Toamasina est le plus grand de Madagascar.",
                "target":  "Ny seranan-tsambo ao Toamasina no lehibe indrindra eto Madagasikara.",
                "note":    "Commerce -- port, reference geographique locale"
            },
            {
                "source":  "Il pleut souvent sur la cote est en decembre.",
                "target":  "Matetika ny orana eny amoron-dranomasina atsinanana amin'ny volana desambra.",
                "note":    "Meteo -- pluies abondantes cote est"
            },
            {
                "source":  "Nous mangeons du poisson frais avec du riz chaque jour.",
                "target":  "Mihinana trondro vaovao sy vary isan'andro izahay.",
                "note":    "Alimentation -- nourriture locale cotiere"
            },
        ],
        "en": [
            {
                "source":  "Hello, how are you?",
                "target":  "Manahoana ianao ?",
                "note":    "Greeting -- Betsimisaraka coastal form"
            },
            {
                "source":  "Fishermen go out to sea early in the morning.",
                "target":  "Mivoaka any an-dranomasina maraina koa ny mpanjono.",
                "note":    "Fishing -- main activity on east coast"
            },
            {
                "source":  "The port of Toamasina is the largest in Madagascar.",
                "target":  "Ny seranan-tsambo ao Toamasina no lehibe indrindra eto Madagasikara.",
                "note":    "Commerce -- port, local geographic reference"
            },
            {
                "source":  "It rains often on the east coast in December.",
                "target":  "Matetika ny orana eny amoron-dranomasina atsinanana amin'ny volana desambra.",
                "note":    "Weather -- heavy rains on east coast"
            },
            {
                "source":  "We eat fresh fish with rice every day.",
                "target":  "Mihinana trondro vaovao sy vary isan'andro izahay.",
                "note":    "Food -- local coastal diet"
            },
        ],
        "tts": [
            "Manahoana ianao ?",
            "Mivoaka any an-dranomasina maraina koa ny mpanjono.",
            "Ny seranan-tsambo ao Toamasina no lehibe indrindra eto Madagasikara.",
            "Matetika ny orana eny amoron-dranomasina atsinanana amin'ny volana desambra.",
            "Mihinana trondro vaovao sy vary isan'andro izahay.",
        ],
    },

    # ── Sakalava (Cote Ouest -- Mahajanga / Toliara) ───────────────────
    # Spoken along the western coast and the Menabe region. Influenced
    # by cattle herding, savanna life, and trade with the Arab world.
    # Collect from native speakers in Mahajanga, Morondava, Toliara.

    "sakalava": {
        "fr": [
            {
                "source":  "Bonjour, comment allez-vous ?",
                "target":  "Manahoana ianao ?",
                "note":    "Salutation -- forme Sakalava cote ouest"
            },
            {
                "source":  "Les zebus paissent dans la savane pendant la saison seche.",
                "target":  "Mihanina ao amin'ny savoka ny omby raha ririnina.",
                "note":    "Elevage -- zebus, saison seche, specifique ouest"
            },
            {
                "source":  "La saison des pluies commence en novembre a Mahajanga.",
                "target":  "Manomboka amin'ny volana novambra ny fahavaratra ao Mahajanga.",
                "note":    "Meteo -- saison des pluies, reference Mahajanga"
            },
            {
                "source":  "Nous allons au puits chercher de l'eau chaque matin.",
                "target":  "Mandeha any amin'ny lavaka rano hitondra rano isan'andro maraina izahay.",
                "note":    "Acces a l'eau -- vie rurale cote ouest"
            },
            {
                "source":  "Le baobab est l'arbre symbole de notre region.",
                "target":  "Ny renala no hazo embleme amin'ny faritra aminay.",
                "note":    "Identite regionale -- baobab, Menabe"
            },
        ],
        "en": [
            {
                "source":  "Hello, how are you?",
                "target":  "Manahoana ianao ?",
                "note":    "Greeting -- Sakalava west coast form"
            },
            {
                "source":  "Zebu cattle graze in the savanna during the dry season.",
                "target":  "Mihanina ao amin'ny savoka ny omby raha ririnina.",
                "note":    "Livestock -- zebu, dry season, west coast specific"
            },
            {
                "source":  "The rainy season starts in November in Mahajanga.",
                "target":  "Manomboka amin'ny volana novambra ny fahavaratra ao Mahajanga.",
                "note":    "Weather -- rainy season, Mahajanga reference"
            },
            {
                "source":  "We go to the well to fetch water every morning.",
                "target":  "Mandeha any amin'ny lavaka rano hitondra rano isan'andro maraina izahay.",
                "note":    "Water access -- rural life, west coast"
            },
            {
                "source":  "The baobab is the symbol tree of our region.",
                "target":  "Ny renala no hazo embleme amin'ny faritra aminay.",
                "note":    "Regional identity -- baobab, Menabe"
            },
        ],
        "tts": [
            "Manahoana ianao ?",
            "Mihanina ao amin'ny savoka ny omby raha ririnina.",
            "Manomboka amin'ny volana novambra ny fahavaratra ao Mahajanga.",
            "Mandeha any amin'ny lavaka rano hitondra rano isan'andro maraina izahay.",
            "Ny renala no hazo embleme amin'ny faritra aminay.",
        ],
    },
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Writers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def write_nllb_examples(dialect: str, paths: dict):
    """Write examples.jsonl into raw/fr/ and raw/en/."""
    data = EXAMPLES[dialect]
    for lang in ("fr", "en"):
        out_dir  = paths["raw_fr"] if lang == "fr" else paths["raw_en"]
        out_path = os.path.join(out_dir, "data.jsonl")
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for entry in data[lang]:
                obj = {
                    "source":   entry["source"],
                    "target":   entry["target"],
                    "src_lang": lang,
                    "dialect":  dialect,
                    "note":     entry["note"],
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        log.info(f"  [{dialect}] {lang} -> {out_path}  ({len(data[lang])} pairs)")


def write_tts_examples(dialect: str, paths: dict):
    """
    Generate example WAV files using MMS-TTS and write transcripts.csv.
    These are baseline audio -- replace WAVs with native speaker recordings.
    """
    import torch
    from transformers import VitsModel, AutoTokenizer
    import scipy.io.wavfile

    raw_dir   = paths["raw_audio"]
    os.makedirs(raw_dir, exist_ok=True)
    sentences = EXAMPLES[dialect]["tts"]
    device    = "cuda" if torch.cuda.is_available() else "cpu"

    log.info(f"  [{dialect}] Generating {len(sentences)} example WAVs using MMS-TTS ({device})...")
    tok = AutoTokenizer.from_pretrained("facebook/mms-tts-mlg")
    mdl = VitsModel.from_pretrained("facebook/mms-tts-mlg").to(device).eval()
    sr  = mdl.config.sampling_rate

    # Naming convention: {dialect}_{speaker_id}_{utterance_id}.wav
    # speaker_id = spk001 (replace with real speaker code, e.g. spk_rakoto)
    # utterance_id = u0001, u0002, ... (sequential per speaker per session)
    tc_rows = [["file_name", "text", "speaker_id"]]
    for i, text in enumerate(sentences):
        fname  = f"{dialect}_spk001_u{i+1:04d}.wav"
        fpath  = os.path.join(raw_dir, fname)
        inputs = tok(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = mdl(**inputs)
        wav = (out.waveform[0].cpu().float().numpy() * 32767).astype("int16")
        scipy.io.wavfile.write(fpath, sr, wav)
        dur = len(wav) / sr
        tc_rows.append([fname, text, "spk001"])
        log.info(f"    {fname}  {dur:.1f}s  -- \"{text}\"")

    tc_path = os.path.join(raw_dir, "transcripts.csv")
    with open(tc_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter="|").writerows(tc_rows)

    log.info(f"  [{dialect}] transcripts.csv -> {tc_path}")
    log.info(f"  [{dialect}] Replace WAV files with real native speaker recordings.")


def seed_dialect(dialect: str):
    from mgvaovao.core.config import settings, DIALECT_META
    cfg   = DIALECT_META[dialect]
    paths = {**{k: str(v) for k, v in settings.nllb_paths(dialect).items()},
             **{k: str(v) for k, v in settings.tts_paths(dialect).items()}}

    log.info("")
    log.info("=" * 62)
    log.info(f"  {cfg['name']}  ({dialect})")
    log.info(f"  Region : {cfg['region']}")
    log.info(f"  Note   : {cfg['data_note']}")
    log.info("=" * 62)

    write_nllb_examples(dialect, paths)
    write_tts_examples(dialect, paths)

    log.info("")
    log.info("  Structure created:")
    log.info(f"    dataset/nllb_finetune/{dialect}/raw/fr/data.jsonl")
    log.info(f"    dataset/nllb_finetune/{dialect}/raw/en/data.jsonl")
    log.info(f"    dataset/tts_finetune/{dialect}/raw_audio/transcripts.csv")
    log.info(f"    dataset/tts_finetune/{dialect}/raw_audio/{dialect}_spk001_u*.wav")
    log.info("")
    log.info("  To add real data:")
    log.info(f"    1. Add .jsonl files to dataset/nllb_finetune/{dialect}/raw/fr/ and raw/en/")
    log.info(f"    2. Add WAV recordings to dataset/tts_finetune/{dialect}/raw_audio/")
    log.info(f"    3. Append rows to transcripts.csv")
    log.info(f"    4. Run: python scripts/02b_preprocess.py --dialect {dialect}")


def parse_args():
    p = argparse.ArgumentParser(description="Seed dataset folder with example data")
    p.add_argument("--dialect", choices=["plt_latn","betsileo","betsimisaraka","sakalava"],
                   default=None, help="Single dialect (default: all 4)")
    return p.parse_args()


def main():
    args = parse_args()
    from mgvaovao.core.config import DIALECTS

    targets = [args.dialect] if args.dialect else DIALECTS

    log.info("MGVaovao -- Seeding dataset with example data")
    log.info(f"Dialects : {targets}")
    log.info("Replace examples with real collected data before production fine-tuning.")

    for d in targets:
        seed_dialect(d)

    log.info("")
    log.info("=" * 62)
    log.info("  All example data created.")
    log.info("")
    log.info("  NEXT -- after adding real data:")
    log.info("    python scripts/02b_preprocess.py --all")
    log.info("    python scripts/03_finetune_nllb.py --dialect <name>")
    log.info("    python scripts/04_finetune_tts.py  --dialect <name>")
    log.info("=" * 62)


if __name__ == "__main__":
    main()
