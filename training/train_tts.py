#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MMS-TTS-MLG (VITS) fine-tuning for a specific Malagasy dialect.
One separate model checkpoint per dialect.

Strategy:
  - plt_latn      → fine-tune from facebook/mms-tts-mlg directly
  - betsileo      → fine-tune from plt_latn checkpoint (or base if unavailable)
  - betsimisaraka → same
  - sakalava      → same

Usage:
    python scripts/04_finetune_tts.py --dialect plt_latn
    python scripts/04_finetune_tts.py --dialect betsileo --epochs 50
    python scripts/04_finetune_tts.py --dialect plt_latn --from-base
"""
import sys, os, csv, time, argparse, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dialect", required=True,
                   choices=["plt_latn","betsileo","betsimisaraka","sakalava"])
    p.add_argument("--epochs",    type=int,   default=None)
    p.add_argument("--lr",        type=float, default=None)
    p.add_argument("--from-base", action="store_true",
                   help="Always start from facebook/mms-tts-mlg (ignore plt_latn checkpoint)")
    p.add_argument("--no-cuda",   action="store_true")
    return p.parse_args()


class MalagasyTTSDataset:
    """TTS dataset compatible with ylacombe/finetune-hf-vits format."""

    HEADER = ["file_name", "text", "speaker_id", "duration_s", "dialect"]

    def __init__(self, metadata_path: str, audio_dir: str, tokenizer, target_sr: int = 16000):
        import torchaudio
        self.audio_dir = audio_dir
        self.tok       = tokenizer
        self.target_sr = target_sr
        self._load    = torchaudio.load

        self.samples = []
        with open(metadata_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="|")
            header = next(reader)
            for row in reader:
                if len(row) >= 2:
                    self.samples.append({"file": row[0].strip(), "text": row[1].strip()})

        if len(self.samples) == 0:
            raise ValueError(f"No samples found in {metadata_path}")
        log.info(f"Dataset loaded: {len(self.samples)} samples")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        import torchaudio, torchaudio.functional as AF
        import torch

        s = self.samples[idx]
        wav_path = os.path.join(self.audio_dir, s["file"])

        waveform, sr = self._load(wav_path)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(0, keepdim=True)
        if sr != self.target_sr:
            waveform = AF.resample(waveform, sr, self.target_sr)

        tok_out = self.tok(s["text"], return_tensors="pt", padding=False)
        return {
            "input_ids":      tok_out["input_ids"].squeeze(0),
            "attention_mask": tok_out["attention_mask"].squeeze(0),
            "waveform":       waveform.squeeze(0),
            "text":           s["text"],
        }


def collate_fn(batch):
    """Pad input_ids/attention_mask; keep waveforms as list (variable length)."""
    import torch
    from torch.nn.utils.rnn import pad_sequence

    input_ids      = pad_sequence([b["input_ids"] for b in batch],      batch_first=True)
    attention_mask = pad_sequence([b["attention_mask"] for b in batch], batch_first=True)
    waveforms = [b["waveform"] for b in batch]  # kept as list (pad separately if needed)
    texts     = [b["text"] for b in batch]

    return {
        "input_ids":      input_ids,
        "attention_mask": attention_mask,
        "waveforms":      waveforms,
        "texts":          texts,
    }


def resolve_base_model(dialect: str, force_base: bool, paths: dict) -> str:
    """
    Return the model ID/path to start fine-tuning from:
    - plt_latn: always facebook/mms-tts-mlg
    - others: plt_latn final checkpoint if available, else base
    """
    from mgvaovao.core.config import settings
    base = settings.tts_model_name

    if dialect == "plt_latn" or force_base:
        return base

    plt_ckpt = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "checkpoints", "tts_plt_latn", "final"
    )
    if os.path.isdir(plt_ckpt):
        log.info(f"Using plt_latn checkpoint as base: {plt_ckpt}")
        return plt_ckpt
    else:
        log.warning(f"plt_latn checkpoint not found at {plt_ckpt}")
        log.warning("Fine-tuning from base facebook/mms-tts-mlg instead")
        return base


def main():
    args  = parse_args()
    from mgvaovao.core.config import settings, DIALECT_META
    import torch
    from torch.utils.data import DataLoader

    cfg   = DIALECT_META[args.dialect]
    paths = {k: str(v) for k, v in settings.tts_paths(args.dialect).items()}
    tc = {
        "model_name":            settings.tts_model_name,
        "num_train_epochs":      settings.tts_train_epochs,
        "per_device_batch_size": settings.tts_batch_size,
        "learning_rate":         settings.tts_lr,
        "save_steps":            settings.tts_save_steps,
        "logging_steps":         settings.tts_logging_steps,
        "save_total_limit":      settings.tts_save_total_limit,
        "min_samples":           settings.tts_min_samples,
        "utmos_threshold":       settings.tts_utmos_threshold,
    }

    if args.epochs: tc["num_train_epochs"]    = args.epochs
    if args.lr:     tc["learning_rate"]        = args.lr

    use_cuda = torch.cuda.is_available() and not args.no_cuda
    device   = "cuda" if use_cuda else "cpu"

    log.info("=" * 60)
    log.info(f"  TTS Fine-Tuning — {cfg['name']} ({args.dialect})")
    log.info(f"  Device  : {'CUDA '+torch.cuda.get_device_name(0) if use_cuda else 'CPU'}")
    log.info(f"  Epochs  : {tc['num_train_epochs']}")
    log.info(f"  LR      : {tc['learning_rate']}")
    log.info("=" * 60)

    # ── Verify dataset ────────────────────────────────────────────
    if not os.path.isfile(paths["metadata"]):
        log.error(f"metadata.csv not found: {paths['tts_metadata']}")
        log.error("Run: python scripts/02b_preprocess.py --dialect " + args.dialect)
        sys.exit(1)

    n_samples = sum(1 for _ in open(paths["metadata"])) - 1  # -1 header
    log.info(f"Dataset: {n_samples} samples")
    if n_samples < tc["min_samples"]:
        log.warning(f"Only {n_samples} samples (min recommended: {tc['min_samples']})")
        log.warning("Results will be poor — collect more audio from native speakers")

    # ── Load model ────────────────────────────────────────────────
    from transformers import VitsModel, AutoTokenizer

    base_model = resolve_base_model(args.dialect, args.from_base, paths)
    log.info(f"Loading model from: {base_model}")

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model     = VitsModel.from_pretrained(base_model, torch_dtype=torch.float32)
    model     = model.to(device).train()
    TTS_SR    = model.config.sampling_rate
    log.info(f"Model loaded — sample rate: {TTS_SR} Hz, params: ~83M")

    # ── Dataset ───────────────────────────────────────────────────
    dataset = MalagasyTTSDataset(
        metadata_path=paths["metadata"],
        audio_dir=paths["processed_audio"],
        tokenizer=tokenizer,
        target_sr=TTS_SR,
    )

    n_val   = max(1, int(len(dataset) * 0.1))
    n_train = len(dataset) - n_val
    train_ds, val_ds = torch.utils.data.random_split(
        dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(42)
    )

    train_loader = DataLoader(
        train_ds, batch_size=tc["per_device_batch_size"],
        collate_fn=collate_fn, shuffle=True, num_workers=0,
    )
    val_loader = DataLoader(
        val_ds, batch_size=1,
        collate_fn=collate_fn, shuffle=False, num_workers=0,
    )
    log.info(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

    # ── Optimizer ─────────────────────────────────────────────────
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=tc["learning_rate"],
        betas=(0.8, 0.99),
        eps=1e-9,
    )
    scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9998)

    # ── Train loop ────────────────────────────────────────────────
    os.makedirs(paths["ckpt"], exist_ok=True)
    best_val_loss = float("inf")
    global_step   = 0
    t0 = time.time()

    for epoch in range(1, tc["num_train_epochs"] + 1):
        model.train()
        epoch_loss, n_batches = 0.0, 0

        for batch in train_loader:
            ids  = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)

            optimizer.zero_grad()
            try:
                out = model(input_ids=ids, attention_mask=mask)
                wav_pred = out.waveform.float()  # (B, T_pred)

                # L1 reconstruction loss vs target waveform
                losses = []
                for i, wav_tgt in enumerate(batch["waveforms"]):
                    wav_tgt = wav_tgt.to(device).float()
                    tl = min(wav_pred[i].shape[-1], wav_tgt.shape[-1])
                    losses.append(
                        torch.nn.functional.l1_loss(wav_pred[i, :tl], wav_tgt[:tl])
                    )
                loss = torch.stack(losses).mean()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()

                epoch_loss += loss.item()
                n_batches  += 1
                global_step += 1

            except Exception as e:
                log.warning(f"Step {global_step} skipped: {e}")
                continue

            if global_step % tc["logging_steps"] == 0:
                lr_now = scheduler.get_last_lr()[0]
                log.info(f"  step {global_step:5d} | loss {epoch_loss/n_batches:.4f} | lr {lr_now:.2e}")

        # ── Validation ────────────────────────────────────────────
        model.eval()
        val_loss, n_val_b = 0.0, 0
        with torch.no_grad():
            for batch in val_loader:
                ids  = batch["input_ids"].to(device)
                mask = batch["attention_mask"].to(device)
                try:
                    out = model(input_ids=ids, attention_mask=mask)
                    wav_pred = out.waveform.float()
                    wav_tgt  = batch["waveforms"][0].to(device).float()
                    tl = min(wav_pred[0].shape[-1], wav_tgt.shape[-1])
                    val_loss += torch.nn.functional.l1_loss(
                        wav_pred[0, :tl], wav_tgt[:tl]
                    ).item()
                    n_val_b += 1
                except Exception:
                    pass

        avg_train = epoch_loss / max(n_batches, 1)
        avg_val   = val_loss   / max(n_val_b,  1)
        elapsed   = time.time() - t0
        log.info(f"Epoch {epoch:3d}/{tc['num_train_epochs']} | "
                 f"train {avg_train:.4f} | val {avg_val:.4f} | {elapsed:.0f}s")

        # ── Checkpoint ────────────────────────────────────────────
        if global_step % tc["save_steps"] == 0 or epoch % 10 == 0:
            ckpt = os.path.join(paths["ckpt"], f"epoch_{epoch:04d}")
            model.save_pretrained(ckpt)
            tokenizer.save_pretrained(ckpt)
            log.info(f"  Checkpoint → {ckpt}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            best_dir = os.path.join(paths["ckpt"], "best")
            model.save_pretrained(best_dir)
            tokenizer.save_pretrained(best_dir)

    # ── Save final ────────────────────────────────────────────────
    final_dir = os.path.join(paths["ckpt"], "final")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
    log.info(f"Final checkpoint → {final_dir}")
    log.info(f"Best val loss    : {best_val_loss:.4f}")

    log.info("=" * 60)
    log.info(f"  Done. Test with:")
    log.info(f"  python scripts/06_run_pipeline.py --dialect {args.dialect}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
