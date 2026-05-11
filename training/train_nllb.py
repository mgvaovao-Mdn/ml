#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLLB-200 LoRA fine-tuning for a specific Malagasy dialect.
Optimised for GTX 1050 (4 GB VRAM): fp16, gradient_checkpointing, batch=1.

Usage:
    python scripts/03_finetune_nllb.py --dialect plt_latn
    python scripts/03_finetune_nllb.py --dialect betsileo --epochs 10
    python scripts/03_finetune_nllb.py --dialect plt_latn --resume
"""
import sys, os, json, argparse, logging, time
import transformers
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
    p.add_argument("--dialect",  required=True,
                   choices=["plt_latn","betsileo","betsimisaraka","sakalava"])
    p.add_argument("--epochs",   type=int,   default=None,
                   help="Override num_train_epochs from config")
    p.add_argument("--batch",    type=int,   default=None,
                   help="Override per_device_batch_size")
    p.add_argument("--lr",       type=float, default=None,
                   help="Override learning_rate")
    p.add_argument("--resume",   action="store_true",
                   help="Resume from last checkpoint if available")
    p.add_argument("--no-fp16",  action="store_true",
                   help="Disable fp16 (use on CPU or if fp16 errors)")
    return p.parse_args()


def load_jsonl(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def build_hf_dataset(train_path: str, val_path: str):
    from datasets import Dataset
    train_data = load_jsonl(train_path)
    val_data   = load_jsonl(val_path)
    return Dataset.from_list(train_data), Dataset.from_list(val_data)


def make_tokenize_fn(tokenizer, src_langs: dict, nllb_target: str,
                     max_src: int, max_tgt: int):
    def tokenize(batch):
        src_lang = src_langs.get(batch["src_lang"], "fra_Latn")

        # Tokenize source
        tokenizer.src_lang = src_lang
        model_inputs = tokenizer(
            batch["source"],
            max_length=max_src,
            truncation=True,
            padding="max_length",
        )

        # Tokenize target — switch to target lang mode manually (as_target_tokenizer deprecated)
        tokenizer.src_lang = nllb_target
        label_enc = tokenizer(
            batch["target"],
            max_length=max_tgt,
            truncation=True,
            padding="max_length",
        )
        tokenizer.src_lang = src_lang  # restore

        # mask padding tokens in labels (-100 = ignored by CrossEntropyLoss)
        model_inputs["labels"] = [
            (l if l != tokenizer.pad_token_id else -100)
            for l in label_enc["input_ids"]
        ]
        return model_inputs
    return tokenize


def main():
    args = parse_args()

    from mgvaovao.core.config import settings, DIALECT_META, SRC_LANGS
    import torch

    cfg   = DIALECT_META[args.dialect]
    paths = {k: str(v) for k, v in settings.nllb_paths(args.dialect).items()}

    # Build a mutable config dict from settings (CLI overrides applied below)
    tc = {
        "model_name":             settings.nllb_model_name,
        "lora_r":                 settings.nllb_lora_r,
        "lora_alpha":             settings.nllb_lora_alpha,
        "lora_target_modules":    settings.nllb_lora_target_modules,
        "lora_dropout":           settings.nllb_lora_dropout,
        "max_src_len":            settings.nllb_max_src_len,
        "max_tgt_len":            settings.nllb_max_tgt_len,
        "num_train_epochs":       settings.nllb_train_epochs,
        "per_device_batch_size":  settings.nllb_batch_size,
        "gradient_accumulation":  settings.nllb_grad_accum,
        "learning_rate":          settings.nllb_lr,
        "warmup_ratio":           settings.nllb_warmup_ratio,
        "fp16":                   settings.nllb_fp16,
        "gradient_checkpointing": settings.nllb_gradient_checkpointing,
        "save_total_limit":       settings.nllb_save_total_limit,
        "eval_steps":             settings.nllb_eval_steps,
        "logging_steps":          settings.nllb_logging_steps,
        "num_beams":              settings.nllb_num_beams,
        "chrf_threshold":         settings.nllb_chrf_threshold,
    }

    # Apply CLI overrides
    if args.epochs: tc["num_train_epochs"]       = args.epochs
    if args.batch:  tc["per_device_batch_size"]  = args.batch
    if args.lr:     tc["learning_rate"]           = args.lr
    use_fp16 = tc["fp16"] and torch.cuda.is_available() and not args.no_fp16

    log.info("=" * 60)
    log.info(f"  NLLB Fine-Tuning — {cfg['name']} ({args.dialect})")
    log.info(f"  Device      : {'CUDA '+torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    log.info(f"  Base model  : {tc['model_name']}")
    log.info(f"  LoRA rank   : {tc['lora_r']}")
    log.info(f"  NLLB target : {cfg['nllb_target']}")
    log.info(f"  Epochs      : {tc['num_train_epochs']}")
    log.info(f"  Batch       : {tc['per_device_batch_size']} × {tc['gradient_accumulation']} grad_accum")
    log.info(f"  fp16        : {use_fp16}")
    log.info(f"  Checkpoint  : {paths['ckpt']}")
    log.info("=" * 60)

    # ── Verify dataset ────────────────────────────────────────────
    if not os.path.isfile(paths["train"]):
        log.error(f"Train file not found: {paths['train']}")
        log.error("Run: python -m training.preprocess --dialect " + args.dialect)
        sys.exit(1)

    # ── Tokenizer ─────────────────────────────────────────────────
    from transformers import AutoTokenizer
    log.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(tc["model_name"])

    # ── Dataset ───────────────────────────────────────────────────
    log.info("Building datasets...")
    train_ds_raw, val_ds_raw = build_hf_dataset(paths["train"], paths["val"])

    tokenize_fn = make_tokenize_fn(
        tokenizer, SRC_LANGS, cfg["nllb_target"],
        tc["max_src_len"], tc["max_tgt_len"]
    )

    train_ds = train_ds_raw.map(tokenize_fn, remove_columns=train_ds_raw.column_names)
    val_ds   = val_ds_raw.map(tokenize_fn,   remove_columns=val_ds_raw.column_names)
    train_ds.set_format("torch")
    val_ds.set_format("torch")
    log.info(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

    # ── Model + LoRA ─────────────────────────────────────────────
    from transformers import AutoModelForSeq2SeqLM
    from peft import LoraConfig, get_peft_model, TaskType

    log.info("Loading base model...")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        tc["model_name"],
        torch_dtype=torch.float16 if use_fp16 else torch.float32,
        low_cpu_mem_usage=True,
    )

    if tc["gradient_checkpointing"]:
        # use_reentrant=False is required when combining LoRA (frozen base) + gradient checkpointing
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})

    lora_cfg = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=tc["lora_r"],
        lora_alpha=tc["lora_alpha"],
        target_modules=tc["lora_target_modules"],
        lora_dropout=tc["lora_dropout"],
        bias="none",
        inference_mode=False,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    # Set forced BOS token so generation targets the correct dialect language code
    model.config.forced_bos_token_id = tokenizer.convert_tokens_to_ids(cfg["nllb_target"])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    # ── Trainer ───────────────────────────────────────────────────
    from transformers import (
        Seq2SeqTrainingArguments, Seq2SeqTrainer,
        DataCollatorForSeq2Seq,
    )

    os.makedirs(paths["ckpt"], exist_ok=True)
    resume_from = paths["ckpt"] if args.resume and os.listdir(paths["ckpt"]) else None

    # Cap eval_steps so at least 1 evaluation happens even with small datasets
    steps_per_epoch = max(1, len(train_ds) // (tc["per_device_batch_size"] * tc["gradient_accumulation"]))
    eff_eval_steps  = min(tc["eval_steps"], steps_per_epoch)
    log.info(f"  steps/epoch={steps_per_epoch}  eval_steps={eff_eval_steps}")

    train_args = Seq2SeqTrainingArguments(
        output_dir=paths["ckpt"],
        num_train_epochs=tc["num_train_epochs"],
        per_device_train_batch_size=tc["per_device_batch_size"],
        per_device_eval_batch_size=tc["per_device_batch_size"],
        gradient_accumulation_steps=tc["gradient_accumulation"],
        learning_rate=tc["learning_rate"],
        warmup_ratio=tc["warmup_ratio"],
        predict_with_generate=True,
        generation_max_length=tc["max_tgt_len"],
        eval_strategy="steps",
        eval_steps=eff_eval_steps,
        save_steps=eff_eval_steps,
        logging_steps=tc["logging_steps"],
        save_total_limit=tc["save_total_limit"],
        fp16=use_fp16,
        report_to="none",
        label_names=["labels"],
        dataloader_pin_memory=(device == "cuda"),
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )

    collator = DataCollatorForSeq2Seq(
        tokenizer, model=model,
        padding=True,
        label_pad_token_id=-100,
    )

    # processing_class= was introduced in transformers 4.46; fall back to tokenizer= for older builds
    _trainer_tok_kwarg = (
        {"processing_class": tokenizer}
        if int(transformers.__version__.split(".")[1]) >= 46
        else {"tokenizer": tokenizer}
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=train_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        **_trainer_tok_kwarg,
    )

    # ── Train ─────────────────────────────────────────────────────
    log.info("Starting training...")
    t0 = time.time()
    result = trainer.train(resume_from_checkpoint=resume_from)
    elapsed = time.time() - t0

    log.info(f"Training complete — {elapsed:.0f}s")
    log.info(f"  Train loss : {result.training_loss:.4f}")

    # ── Save final ────────────────────────────────────────────────
    final_dir = os.path.join(paths["ckpt"], "final")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
    log.info(f"Checkpoint saved → {final_dir}")

    # ── Quick chrF++ check ────────────────────────────────────────
    log.info("Running quick chrF++ evaluation on val set...")
    model.eval()
    try:
        import evaluate
        chrf = evaluate.load("chrf")
        preds, refs = [], []
        for item in load_jsonl(paths["val"])[:20]:
            tokenizer.src_lang = SRC_LANGS.get(item["src_lang"], "fra_Latn")
            inputs = tokenizer(
                item["source"], return_tensors="pt",
                truncation=True, max_length=tc["max_src_len"],
            ).to(device)
            with torch.no_grad():
                tokens = model.generate(
                    **inputs,
                    forced_bos_token_id=tokenizer.convert_tokens_to_ids(cfg["nllb_target"]),
                    max_length=tc["max_tgt_len"], num_beams=4,
                )
            pred = tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
            preds.append(pred)
            refs.append([item["target"]])
        score = chrf.compute(predictions=preds, references=refs, word_order=2)
        log.info(f"  chrF++ : {score['score']:.2f}  (baseline 42–52 for plt_Latn)")
    except Exception as e:
        log.warning(f"chrF++ eval skipped: {e}")

    log.info("=" * 60)
    log.info(f"  Done. To run inference:")
    log.info(f"  python scripts/06_run_pipeline.py --dialect {args.dialect}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
