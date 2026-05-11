#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02b_preprocess.py  —  Convert raw annotator data into training-ready format.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHERE DATA COLLECTORS DROP THEIR WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  NLLB (text translation pairs)
  ├── dataset/nllb_finetune/{dialect}/raw/fr/*.jsonl   ← French → Malagasy
  └── dataset/nllb_finetune/{dialect}/raw/en/*.jsonl   ← English → Malagasy

  Each line of the JSONL must have:
    {"source": "Bonjour", "target": "Manahoana", "src_lang": "fr", "dialect": "betsileo"}

  TTS (audio recordings)
  ├── dataset/tts_finetune/{dialect}/raw_audio/transcripts.csv
  │     Format: file_name|text|speaker_id
  │     Example: rec_001.wav|Manahoana ianao ?|spk_001
  └── dataset/tts_finetune/{dialect}/raw_audio/*.wav   ← any sample rate, mono/stereo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHAT THIS SCRIPT PRODUCES  (fine-tuning scripts read from here)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  NLLB training data  →  read by scripts/03_finetune_nllb.py
  ├── dataset/nllb_finetune/{dialect}/processed/train.jsonl   (80 %)
  ├── dataset/nllb_finetune/{dialect}/processed/val.jsonl     (10 %)
  ├── dataset/nllb_finetune/{dialect}/processed/test.jsonl    (10 %)
  └── dataset/nllb_finetune/{dialect}/reference/eval_fixed_200.csv

  TTS training data  →  read by scripts/04_finetune_tts.py
  ├── dataset/tts_finetune/{dialect}/metadata.csv
  └── dataset/tts_finetune/{dialect}/processed_audio/*.wav    (16kHz mono)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHERE FINE-TUNED MODELS ARE SAVED  (inference reads from here)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  checkpoints/nllb_{dialect}/final/   ← LoRA adapters  (NLLB translation)
  checkpoints/tts_{dialect}/final/    ← VITS model      (TTS audio synthesis)

  scripts/06_run_pipeline.py automatically loads these checkpoints.
  If they don't exist yet it falls back to the base HuggingFace model.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Usage:
    python scripts/02b_preprocess.py --dialect betsileo
    python scripts/02b_preprocess.py --all
    python scripts/02b_preprocess.py --all --generate-demo
"""

import sys, os, json, csv, glob, shutil, argparse, logging, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Demo sentences used when --generate-demo is passed ─────────────────────
# These are shown on the projector as examples of what data collectors
# should provide (format, vocabulary level, length).

DEMO_SENTENCES = {
    "plt_latn": [
        ("Bonjour, comment allez-vous ?",               "Manao ahoana ianao ?",                        "fr"),
        ("L'eau est essentielle à la vie.",              "Ilaina ho an'ny fiainana ny rano.",            "fr"),
        ("Madagascar est une grande île.",               "Nosy lehibe ny Madagasikara.",                 "fr"),
        ("Les enfants vont à l'école chaque matin.",    "Mandeha am-pianarana ny ankizy isan'andro.",   "fr"),
        ("Je voudrais apprendre le malgache.",           "Te hianatra ny teny malagasy aho.",            "fr"),
        ("Hello, how are you?",                          "Manao ahoana ianao ?",                        "en"),
        ("Water is essential for life.",                 "Ilaina ho an'ny fiainana ny rano.",            "en"),
        ("Madagascar is a beautiful island.",            "Nosy tsara tarehy ny Madagasikara.",           "en"),
        ("Children go to school every morning.",         "Mandeha am-pianarana ny ankizy isan'andro.",   "en"),
        ("I would like to learn Malagasy.",              "Te hianatra ny teny malagasy aho.",            "en"),
    ],
    "betsileo": [
        ("Bonjour, comment allez-vous ?",               "Manahoana ianao ?",                            "fr"),
        ("Merci beaucoup pour votre aide.",              "Misaotra be noho ny fanampianao.",              "fr"),
        ("Je veux aller au marché demain.",              "Te handeha any am-tsena rahampitso aho.",      "fr"),
        ("Il fait beau aujourd'hui à Fianarantsoa.",    "Tsara ny andro androany ao Fianarantsoa.",      "fr"),
        ("La vie est belle ici dans les montagnes.",    "Tsara ny fiainana eto an-tendrombohitra.",      "fr"),
        ("Hello, how are you?",                          "Manahoana ianao ?",                            "en"),
        ("Thank you very much.",                         "Misaotra be.",                                 "en"),
        ("I want to go to the market tomorrow.",        "Te handeha any am-tsena rahampitso aho.",      "en"),
        ("The weather is nice today in Fianarantsoa.",  "Tsara ny andro androany ao Fianarantsoa.",      "en"),
        ("Life is beautiful here in the mountains.",    "Tsara ny fiainana eto an-tendrombohitra.",      "en"),
    ],
    "betsimisaraka": [
        ("Bonjour, comment allez-vous ?",               "Manahoana ianao ?",                            "fr"),
        ("La mer est belle ce matin.",                  "Tsara ny ranomasina amin'ity maraina ity.",    "fr"),
        ("Je travaille sur le port de Toamasina.",      "Miasa amin'ny seranan-tsambo ao Toamasina aho.","fr"),
        ("Le poisson frais est délicieux.",              "Matsiro ny hazandrano vaovao.",                "fr"),
        ("Nous aimons vivre près de la côte.",           "Tia miaina eo amoron'ny ranomasina izahay.",   "fr"),
        ("Hello, how are you?",                          "Manahoana ianao ?",                            "en"),
        ("The sea is beautiful this morning.",           "Tsara ny ranomasina amin'ity maraina ity.",    "en"),
        ("I work at the port of Toamasina.",            "Miasa amin'ny seranan-tsambo ao Toamasina aho.","en"),
        ("Fresh fish is delicious.",                     "Matsiro ny hazandrano vaovao.",                "en"),
        ("We love living near the coast.",               "Tia miaina eo amoron'ny ranomasina izahay.",   "en"),
    ],
    "sakalava": [
        ("Bonjour, comment allez-vous ?",               "Manahoana ianao ?",                            "fr"),
        ("Le soleil brille fort à Mahajanga.",           "Mahery ny masoandro ao Mahajanga.",            "fr"),
        ("Les zébus paissent dans la savane.",           "Mihanina ao an-tsaha ny omby.",                "fr"),
        ("J'aime la côte ouest de Madagascar.",         "Tia ny moron-dranomasina andrefana aho.",      "fr"),
        ("La saison sèche commence en avril.",           "Manomboka amin'ny volana aprily ny ririnina.", "fr"),
        ("Hello, how are you?",                          "Manahoana ianao ?",                            "en"),
        ("The sun shines bright in Mahajanga.",         "Mahery ny masoandro ao Mahajanga.",            "en"),
        ("The zebus graze in the savanna.",              "Mihanina ao an-tsaha ny omby.",                "en"),
        ("I love the west coast of Madagascar.",        "Tia ny moron-dranomasina andrefana aho.",      "en"),
        ("The dry season starts in April.",             "Manomboka amin'ny volana aprily ny ririnina.", "en"),
    ],
}

# TTS-only sentences (what is spoken in the recordings)
TTS_DEMO_SENTENCES = {
    "plt_latn": [
        "Manao ahoana ianao ?",
        "Misaotra be noho ny fanampianao.",
        "Ilaina ho an'ny fiainana ny rano.",
        "Nosy tsara tarehy ny Madagasikara.",
        "Mandeha am-pianarana ny ankizy isan'andro.",
    ],
    "betsileo": [
        "Manahoana ianao ?",
        "Misaotra be noho ny fanampianao.",
        "Te handeha any am-tsena rahampitso aho.",
        "Tsara ny andro androany ao Fianarantsoa.",
        "Tsara ny fiainana eto an-tendrombohitra.",
    ],
    "betsimisaraka": [
        "Manahoana ianao ?",
        "Tsara ny ranomasina amin'ity maraina ity.",
        "Miasa amin'ny seranan-tsambo ao Toamasina aho.",
        "Matsiro ny hazandrano vaovao.",
        "Tia miaina eo amoron'ny ranomasina izahay.",
    ],
    "sakalava": [
        "Manahoana ianao ?",
        "Mahery ny masoandro ao Mahajanga.",
        "Mihanina ao an-tsaha ny omby.",
        "Tia ny moron-dranomasina andrefana aho.",
        "Manomboka amin'ny volana aprily ny ririnina.",
    ],
}


def parse_args():
    p = argparse.ArgumentParser(
        description="Preprocess raw annotator data into fine-tuning datasets"
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dialect", choices=["plt_latn","betsileo","betsimisaraka","sakalava"])
    g.add_argument("--all", action="store_true")
    p.add_argument(
        "--generate-demo", action="store_true",
        help="Generate demo WAV + JSONL examples using MMS-TTS (shows collectors the expected format)"
    )
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


# ── NLLB preprocessing ──────────────────────────────────────────────────────

def load_raw_nllb(paths: dict, dialect: str) -> list:
    """Read all *.jsonl files from raw/fr/ and raw/en/."""
    all_pairs = []
    for lang_dir in [paths["raw_fr"], paths["raw_en"]]:
        for fpath in sorted(glob.glob(os.path.join(lang_dir, "*.jsonl"))):
            with open(fpath, encoding="utf-8") as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    # Normalise to the required keys
                    pair = {
                        "source":   obj.get("source", ""),
                        "target":   obj.get("target", ""),
                        "src_lang": obj.get("src_lang", "fr"),
                        "dialect":  obj.get("dialect", dialect),
                    }
                    if pair["source"] and pair["target"]:
                        all_pairs.append(pair)
                        count += 1
            log.info(f"  Read {count} pairs from {os.path.relpath(fpath)}")
    return all_pairs


def write_nllb_splits(all_pairs: list, paths: dict, dialect: str, seed: int):
    """Shuffle and split 80 / 10 / 10, write JSONL + reference CSV."""
    random.seed(seed)
    random.shuffle(all_pairs)

    n       = len(all_pairs)
    n_val   = max(1, int(n * 0.10))
    n_test  = max(1, int(n * 0.10))
    splits  = {
        "train": all_pairs[: n - n_val - n_test],
        "val":   all_pairs[n - n_val - n_test : n - n_test],
        "test":  all_pairs[n - n_test :],
    }

    os.makedirs(paths["processed"], exist_ok=True)
    for split_name, data in splits.items():
        out = os.path.join(paths["processed"], f"{split_name}.jsonl")
        with open(out, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        log.info(f"  [{dialect}] {split_name:5s} : {len(data):4d} pairs  →  {out}")

    # Reference set (fixed 200 — used by 05_evaluate.py for drift monitoring)
    ref_dir = os.path.dirname(paths["reference"])
    os.makedirs(ref_dir, exist_ok=True)
    ref_data = all_pairs[: min(200, n)]
    with open(paths["reference"], "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "src_lang"])
        for item in ref_data:
            w.writerow([item["source"], item["target"], item["src_lang"]])
    log.info(f"  [{dialect}] reference: {len(ref_data)} pairs  →  {paths['nllb_ref']}")


def preprocess_nllb(dialect: str, paths: dict, seed: int):
    log.info(f"\n  -- NLLB text pairs for [{dialect}] --")
    pairs = load_raw_nllb(paths, dialect)
    if not pairs:
        log.warning(f"  No raw JSONL found in raw/fr/ or raw/en/ for {dialect}.")
        log.warning(f"  Add .jsonl files there and re-run, or use --generate-demo first.")
        return 0
    log.info(f"  Total raw pairs: {len(pairs)}")
    write_nllb_splits(pairs, paths, dialect, seed)
    return len(pairs)


# ── TTS preprocessing ───────────────────────────────────────────────────────

def load_transcripts(raw_audio_dir: str) -> list:
    """
    Read raw_audio/transcripts.csv  (pipe-separated: file_name|text|speaker_id).
    Returns list of dicts with keys: file, text, speaker_id.
    """
    tc_path = os.path.join(raw_audio_dir, "transcripts.csv")
    if not os.path.isfile(tc_path):
        log.warning(f"  No transcripts.csv found in {raw_audio_dir}")
        log.warning("  Create it with columns: file_name|text|speaker_id")
        return []
    rows = []
    with open(tc_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            fn = row.get("file_name", "").strip()
            tx = row.get("text", "").strip()
            sp = row.get("speaker_id", "spk_001").strip()
            if fn and tx:
                rows.append({"file": fn, "text": tx, "speaker_id": sp})
    log.info(f"  Found {len(rows)} entries in transcripts.csv")
    return rows


def process_audio_file(src_path: str, dst_path: str, target_sr: int = 16000) -> float:
    """Load audio, convert to mono 16kHz WAV, return duration in seconds."""
    import torchaudio
    import torchaudio.functional as AF
    import torch
    import scipy.io.wavfile

    wf, sr = torchaudio.load(src_path)
    if wf.shape[0] > 1:                        # stereo → mono
        wf = wf.mean(0, keepdim=True)
    if sr != target_sr:                         # resample
        wf = AF.resample(wf, sr, target_sr)
    wav_np = (wf.squeeze().numpy() * 32767).astype("int16")
    import scipy.io.wavfile
    scipy.io.wavfile.write(dst_path, target_sr, wav_np)
    return len(wav_np) / target_sr


def preprocess_tts(dialect: str, paths: dict):
    import torchaudio  # import early to catch missing dep
    log.info(f"\n  -- TTS audio for [{dialect}] --")

    raw_dir = paths["raw_audio"]
    out_dir = paths["processed_audio"]
    os.makedirs(out_dir, exist_ok=True)

    transcripts = load_transcripts(raw_dir)
    if not transcripts:
        return 0

    rows = [["file_name", "text", "speaker_id", "duration_s", "dialect"]]
    processed = 0
    for entry in transcripts:
        src = os.path.join(raw_dir, entry["file"])
        if not os.path.isfile(src):
            log.warning(f"  Missing audio file: {src} — skipped")
            continue
        out_name = f"{dialect}_{processed:04d}.wav"
        dst      = os.path.join(out_dir, out_name)
        try:
            dur = process_audio_file(src, dst)
            rows.append([out_name, entry["text"], entry["speaker_id"], f"{dur:.2f}", dialect])
            processed += 1
            log.info(f"  {entry['file']}  →  {out_name}  ({dur:.1f}s)")
        except Exception as e:
            log.warning(f"  Failed to process {src}: {e}")

    # Write metadata.csv
    with open(paths["metadata"], "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter="|").writerows(rows)
    log.info(f"  [{dialect}] {processed} files → {out_dir}")
    log.info(f"  [{dialect}] metadata.csv → {paths['tts_metadata']}")
    return processed


# ── Demo data generation ─────────────────────────────────────────────────────

def generate_demo_nllb(dialect: str, paths: dict):
    """Write example JSONL files into raw/fr/ and raw/en/ if they are empty."""
    sentences = DEMO_SENTENCES.get(dialect, [])
    if not sentences:
        return

    fr_sentences = [(s, t, l) for s, t, l in sentences if l == "fr"]
    en_sentences = [(s, t, l) for s, t, l in sentences if l == "en"]

    for lang, pairs in [("fr", fr_sentences), ("en", en_sentences)]:
        out_dir  = paths["raw_fr"] if lang == "fr" else paths["raw_en"]
        out_path = os.path.join(out_dir, "demo_examples.jsonl")

        # Don't overwrite real annotator files — only write if file is absent
        if os.path.isfile(out_path):
            log.info(f"  demo_examples.jsonl already exists for {dialect}/{lang} — skipping")
            continue

        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for source, target, _ in pairs:
                obj = {
                    "source":   source,
                    "target":   target,
                    "src_lang": lang,
                    "dialect":  dialect,
                    "note":     "DEMO — validate with native speaker before production",
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        log.info(f"  Demo JSONL → {out_path}  ({len(pairs)} pairs)")


def generate_demo_audio(dialect: str, paths: dict):
    """
    Use MMS-TTS to synthesise demo WAV files → raw_audio/.
    This shows data collectors the expected audio format and quality.
    """
    import torch
    from transformers import VitsModel, AutoTokenizer
    import scipy.io.wavfile

    sentences = TTS_DEMO_SENTENCES.get(dialect, [])
    if not sentences:
        return

    raw_dir = paths["raw_audio"]
    os.makedirs(raw_dir, exist_ok=True)
    tc_path = os.path.join(raw_dir, "transcripts.csv")

    # Don't overwrite existing transcripts (real annotator data)
    if os.path.isfile(tc_path):
        log.info(f"  transcripts.csv already exists for {dialect} raw_audio — skipping demo audio")
        return

    log.info(f"  Generating {len(sentences)} demo WAVs for [{dialect}] using MMS-TTS...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = "facebook/mms-tts-mlg"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = VitsModel.from_pretrained(model_id, torch_dtype=torch.float32).to(device).eval()
    sr  = mdl.config.sampling_rate

    tc_rows = [["file_name", "text", "speaker_id"]]
    for i, text in enumerate(sentences):
        inputs = tok(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = mdl(**inputs)
        wav = (out.waveform[0].cpu().float().numpy() * 32767).astype("int16")
        fname = f"demo_{dialect}_{i+1:03d}.wav"
        fpath = os.path.join(raw_dir, fname)
        scipy.io.wavfile.write(fpath, sr, wav)
        dur = len(wav) / sr
        tc_rows.append([fname, text, "spk_demo"])
        log.info(f"    [{i+1}/{len(sentences)}] {fname}  ({dur:.1f}s)  — \"{text}\"")

    with open(tc_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter="|").writerows(tc_rows)
    log.info(f"  transcripts.csv → {tc_path}")
    log.info(f"  NOTE: These are MMS-TTS baseline audio — replace with native speaker recordings for production.")


# ── Main ─────────────────────────────────────────────────────────────────────

def process_dialect(dialect: str, seed: int, generate_demo: bool):
    from mgvaovao.core.config import settings, DIALECT_META

    cfg   = DIALECT_META[dialect]
    paths = {**{k: str(v) for k, v in settings.nllb_paths(dialect).items()},
             **{k: str(v) for k, v in settings.tts_paths(dialect).items()}}

    log.info("")
    log.info("=" * 62)
    log.info(f"  Dialect : {cfg['name']}  ({dialect})")
    log.info(f"  Region  : {cfg['region']}")
    log.info("=" * 62)

    # 1. Optionally seed raw/ with demo examples
    if generate_demo:
        log.info("\n  [DEMO] Generating example data for projector presentation...")
        generate_demo_nllb(dialect, paths)
        generate_demo_audio(dialect, paths)

    # 2. NLLB: raw/fr/*.jsonl + raw/en/*.jsonl  →  processed/
    n_nllb = preprocess_nllb(dialect, paths, seed)

    # 3. TTS: raw_audio/*.wav + transcripts.csv  →  processed_audio/ + metadata.csv
    n_tts = preprocess_tts(dialect, paths)

    # 4. Summary
    log.info("")
    log.info(f"  RESULT for [{dialect}]")
    log.info(f"    NLLB pairs   : {n_nllb}  (train/val/test in dataset/nllb_finetune/{dialect}/processed/)")
    log.info(f"    TTS files    : {n_tts}   (16kHz WAV in dataset/tts_finetune/{dialect}/processed_audio/)")
    log.info("")
    log.info("  NEXT STEPS:")
    log.info(f"    python scripts/03_finetune_nllb.py --dialect {dialect}")
    log.info(f"    python scripts/04_finetune_tts.py  --dialect {dialect}")
    log.info("")
    log.info("  FINE-TUNED MODEL WILL BE SAVED TO:")
    log.info(f"    checkpoints/nllb_{dialect}/final/   ← NLLB translation model (LoRA)")
    log.info(f"    checkpoints/tts_{dialect}/final/    ← TTS synthesis model (VITS)")
    log.info("")
    log.info("  INFERENCE (reads from those checkpoints automatically):")
    log.info(f"    python scripts/06_run_pipeline.py --dialect {dialect} --text \"Bonjour\" --src-lang fr")
    log.info("=" * 62)


def main():
    args    = parse_args()
    from mgvaovao.core.config import DIALECTS
    targets = DIALECTS if args.all else [args.dialect]

    log.info("MGVaovao — Preprocessing raw annotator data")
    log.info(f"Dialects : {targets}")
    log.info(f"Demo mode: {args.generate_demo}")

    for d in targets:
        process_dialect(d, args.seed, args.generate_demo)

    log.info("")
    log.info("All done.")


if __name__ == "__main__":
    main()
