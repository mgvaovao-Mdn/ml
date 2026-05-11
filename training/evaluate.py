#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluate fine-tuned models for a specific dialect.

Metrics:
  - NLLB: chrF++ (word_order=2) on reference set
  - TTS:  reconstructed audio → play back / save to WAV for listening test
          UTMOS requires a separate model — outputs a mock score for now

Usage:
    python scripts/05_evaluate.py --dialect plt_latn
    python scripts/05_evaluate.py --dialect betsileo --checkpoint best
    python scripts/05_evaluate.py --all
"""
import sys, os, json, csv, argparse, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "eval_results.csv"
)


def parse_args():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dialect",    choices=["plt_latn","betsileo","betsimisaraka","sakalava"])
    g.add_argument("--all",        action="store_true")
    p.add_argument("--checkpoint", default="final",
                   choices=["final","best"], help="Which checkpoint to evaluate")
    p.add_argument("--n-samples",  type=int, default=100,
                   help="Max samples to evaluate (chrF++)")
    return p.parse_args()


def eval_nllb(dialect: str, checkpoint: str, n_samples: int) -> dict:
    from mgvaovao.core.config import settings, DIALECT_META, SRC_LANGS
    import torch

    cfg   = DIALECT_META[dialect]
    paths = {**{k: str(v) for k, v in settings.nllb_paths(dialect).items()},
             **{k: str(v) for k, v in settings.tts_paths(dialect).items()}}
    ckpt  = os.path.join(paths["ckpt"], checkpoint)

    if not os.path.isdir(ckpt):
        log.warning(f"  NLLB checkpoint not found: {ckpt} — skipping")
        return {}

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from peft import PeftModel
    import evaluate

    log.info(f"  Loading NLLB checkpoint: {ckpt}")
    base_name = settings.nllb_model_name
    tokenizer = AutoTokenizer.from_pretrained(ckpt)
    base      = AutoModelForSeq2SeqLM.from_pretrained(
        base_name, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model = PeftModel.from_pretrained(base, ckpt)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model  = model.to(device).eval()

    ref_path = paths["reference"]
    if not os.path.isfile(ref_path):
        ref_path = paths["val"]
        log.warning(f"  Reference file not found, using val: {ref_path}")

    pairs = []
    try:
        with open(ref_path, encoding="utf-8") as f:
            if ref_path.endswith(".csv"):
                reader = csv.DictReader(f)
                pairs  = list(reader)[:n_samples]
            else:
                pairs = [json.loads(l) for l in f if l.strip()][:n_samples]
    except Exception as e:
        log.error(f"  Failed to load ref data: {e}")
        return {}

    chrf_metric = evaluate.load("chrf")
    preds, refs = [], []
    max_len = settings.nllb_max_tgt_len

    for item in pairs:
        src_lang_code = SRC_LANGS.get(item.get("src_lang","fr"), "fra_Latn")
        tokenizer.src_lang = src_lang_code
        inputs = tokenizer(
            item["source"], return_tensors="pt",
            truncation=True, max_length=settings.nllb_max_src_len,
        ).to(device)
        with torch.no_grad():
            tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(cfg["nllb_target"]),
                max_length=max_len, num_beams=4,
            )
        pred = tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
        preds.append(pred)
        refs.append([item["target"]])

    score = chrf_metric.compute(predictions=preds, references=refs, word_order=2)
    result = {
        "dialect":    dialect,
        "checkpoint": checkpoint,
        "n_samples":  len(preds),
        "chrf_pp":    round(score["score"], 2),
        "threshold":  settings.nllb_chrf_threshold,
        "alert":      score["score"] < (42 - settings.nllb_chrf_threshold),
    }
    log.info(f"  chrF++ : {result['chrf_pp']} "
             f"({'⚠ BELOW THRESHOLD' if result['alert'] else 'OK'})")

    # Show a few examples
    for i in range(min(3, len(preds))):
        log.info(f"    [{pairs[i].get('src_lang','?')}] {pairs[i]['source'][:50]}")
        log.info(f"      Pred: {preds[i]}")
        log.info(f"      Ref : {refs[i][0]}")

    return result


def eval_tts(dialect: str, checkpoint: str) -> dict:
    """Synthesize a few sentences and save as WAV for listening test."""
    from mgvaovao.core.config import settings, DIALECT_META
    import torch, scipy.io.wavfile

    cfg   = DIALECT_META[dialect]
    paths = {**{k: str(v) for k, v in settings.nllb_paths(dialect).items()},
             **{k: str(v) for k, v in settings.tts_paths(dialect).items()}}
    ckpt  = os.path.join(paths["ckpt"], checkpoint)

    if not os.path.isdir(ckpt):
        log.warning(f"  TTS checkpoint not found: {ckpt} — skipping")
        return {}

    from transformers import VitsModel, AutoTokenizer

    log.info(f"  Loading TTS checkpoint: {ckpt}")
    tokenizer = AutoTokenizer.from_pretrained(ckpt)
    model     = VitsModel.from_pretrained(ckpt, torch_dtype=torch.float32)
    device    = "cuda" if torch.cuda.is_available() else "cpu"
    model     = model.to(device).eval()
    sr        = model.config.sampling_rate

    # Sample sentences for listening test
    sample_texts = [
        "Manao ahoana ianao ?",
        "Misaotra be noho ny fanampianao.",
        "Tia an'i Madagasikara aho.",
    ]

    eval_dir = os.path.join(paths["ckpt"], "eval_audio")
    os.makedirs(eval_dir, exist_ok=True)

    for i, text in enumerate(sample_texts):
        inputs = tokenizer(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**inputs)
        wav = out.waveform[0].cpu().float().numpy()
        out_path = os.path.join(eval_dir, f"{dialect}_eval_{i:02d}.wav")
        scipy.io.wavfile.write(out_path, sr, (wav * 32767).astype("int16"))
        log.info(f"  Audio → {out_path}")

    log.info(f"  Listen to the WAV files to assess TTS quality")
    log.info(f"  (UTMOS automated scoring requires separate model)")

    return {
        "dialect":    dialect,
        "checkpoint": checkpoint,
        "eval_audio": eval_dir,
        "n_samples":  len(sample_texts),
    }


def save_results(results: list):
    """Append results to eval_results.csv."""
    from datetime import datetime
    exists = os.path.isfile(RESULTS_FILE)
    with open(RESULTS_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp","dialect","checkpoint","metric","value","alert"])
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        for r in results:
            if "chrf_pp" in r:
                writer.writerow([ts, r["dialect"], r["checkpoint"],
                                 "chrF++", r["chrf_pp"], r.get("alert", "")])
    log.info(f"Results appended → {RESULTS_FILE}")


def evaluate_dialect(dialect: str, checkpoint: str, n_samples: int):
    from mgvaovao.core.config import DIALECT_META
    cfg = DIALECT_META[dialect]
    log.info(f"\n{'═'*60}")
    log.info(f"  Evaluating: {cfg['name']} ({dialect})")
    log.info(f"{'═'*60}")

    results = []
    r_nllb = eval_nllb(dialect, checkpoint, n_samples)
    r_tts  = eval_tts(dialect, checkpoint)
    if r_nllb: results.append(r_nllb)
    if r_tts:  results.append(r_tts)
    return results


def main():
    args = parse_args()
    from mgvaovao.core.config import DIALECTS

    targets = DIALECTS if args.all else [args.dialect]
    all_results = []

    for d in targets:
        res = evaluate_dialect(d, args.checkpoint, args.n_samples)
        all_results.extend(res)

    save_results(all_results)

    log.info("\n" + "═" * 60)
    log.info("  Summary")
    log.info("─" * 60)
    for r in all_results:
        if "chrf_pp" in r:
            alert = " ⚠ " if r.get("alert") else " ✓ "
            log.info(f"  {alert} {r['dialect']:15s} chrF++ = {r['chrf_pp']}")
    log.info("═" * 60)


if __name__ == "__main__":
    main()
