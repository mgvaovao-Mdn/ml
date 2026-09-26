# -*- coding: utf-8 -*-
"""
Affine les modeles d'une declinaison, puis rend la main.

Ce script est le corps du job Cloud Run `kozy-finetune`. Il est execute avec
des variables d'environnement fournies a chaque lancement — une seule
definition de job sert donc toutes les declinaisons :

    VARIANT_ID      betsileo__en__18_25__female
    DATASET_URI     gs://kozy-dataset/variants/<id>/dataset.csv
    OUTPUT_PREFIX   gs://mgvaovao-ia-checkpoints/variants/<id>
    BRICKS          mt,tts

Pourquoi un job Cloud Run et non une machine virtuelle
──────────────────────────────────────────────────────
Une tache de job detruit son instance quand elle se termine. Il n'y a donc
rien a eteindre, et rien qui puisse rester allume par oubli. Une VM coute
moins cher a l'heure mais se facture tant qu'on ne l'a pas supprimee : c'est
exactement le risque qu'on ecarte ici.

Comment l'entrainement est reellement lance
───────────────────────────────────────────
`training/train_nllb.py` sait deja affiner NLLB, mais attend l'arborescence
`dataset/nllb_finetune/<id>/processed/*.jsonl`. Plutot que de dupliquer sa
logique — deux entrainements qui divergeraient en silence — ce script lui
prepare ses fichiers a partir du jeu de donnees de la declinaison, puis
l'appelle avec l'identifiant de la declinaison en guise de corpus.

Les repertoires de travail sont rediriges vers le disque local de l'instance
par `MGVAOVAO_DATASET_DIR` et `MGVAOVAO_CHECKPOINTS_DIR` : tout ce qui doit
survivre part dans le stockage objet avant la sortie, le reste disparait avec
l'instance.

Ce que ce script garantit
─────────────────────────
- il sort en code non nul des qu'une etape echoue, pour que Cloud Run marque la
  tache en echec et que le registre le voie ;
- il depose ses points de controle AVANT de sortir ;
- il refuse un corpus trop maigre : entrainer sur quelques dizaines de phrases
  produit un modele moins bon que la base, pour le prix d'un GPU.
"""
from __future__ import annotations

import csv
import io
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

# Corpus minimal. En deca, l'affinage degrade le modele de base : le lancer
# serait depenser un GPU pour obtenir moins bien que gratuitement.
MIN_LIGNES = int(os.environ.get("FINETUNE_MIN_LIGNES", "200"))

# Part reservee a la validation. Sans jeu de validation, l'entrainement ne sait
# pas quand il commence a surapprendre.
PART_VALIDATION = 0.1

RACINE = Path(__file__).resolve().parent.parent


def journal(message: str) -> None:
    print(message, flush=True)


def gcloud_storage(*args: str) -> None:
    subprocess.run(["gcloud", "storage", *args], check=True)


def lire_env(nom: str, obligatoire: bool = True, defaut: str = "") -> str:
    valeur = os.environ.get(nom, defaut).strip()
    if obligatoire and not valeur:
        journal(f"Variable {nom} absente — le job ne peut pas savoir quoi entrainer.")
        sys.exit(2)
    return valeur


def telecharger_dataset(uri: str, destination: Path) -> list[dict]:
    journal(f"Lecture du corpus : {uri}")
    gcloud_storage("cp", uri, str(destination))
    with io.open(destination, encoding="utf-8", newline="") as f:
        lignes = [
            r
            for r in csv.DictReader(f)
            if (r.get("source") or "").strip() and (r.get("target") or "").strip()
        ]
    journal(f"  {len(lignes)} paire(s) utilisable(s)")
    return lignes


def preparer_splits(lignes: list[dict], base: Path, graine: int = 42) -> None:
    """
    Ecrit train/val/test au format attendu par `train_nllb.py`.

    Le decoupage est deterministe : relancer un entrainement sur le meme corpus
    doit donner les memes ensembles, sinon les scores ne sont pas comparables
    d'une execution a l'autre.
    """
    processed = base / "processed"
    processed.mkdir(parents=True, exist_ok=True)

    melange = list(lignes)
    random.Random(graine).shuffle(melange)
    coupe = max(1, int(len(melange) * PART_VALIDATION))
    ensembles = {
        "val": melange[:coupe],
        "test": melange[coupe : coupe * 2],
        "train": melange[coupe * 2 :],
    }

    for nom, contenu in ensembles.items():
        chemin = processed / f"{nom}.jsonl"
        with io.open(chemin, "w", encoding="utf-8") as f:
            for r in contenu:
                f.write(
                    json.dumps(
                        {
                            "source": r.get("source", ""),
                            "target": r.get("target", ""),
                            "src_lang": r.get("src_lang", "fr"),
                            "dialect": r.get("dialecte", ""),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        journal(f"  {nom:5} : {len(contenu)} ligne(s) → {chemin}")


def entrainer_traduction(variant: str) -> None:
    """Appelle le script d'affinage NLLB sur le corpus prepare."""
    journal("Affinage de la traduction (NLLB + LoRA)…")
    subprocess.run(
        [sys.executable, str(RACINE / "training" / "train_nllb.py"), "--dialect", variant],
        check=True,
        cwd=str(RACINE),
    )


def preparer_synthese(lignes: list[dict], base: Path) -> int:
    """
    Prepare le corpus de synthese vocale.

    Seules les lignes disposant d'un audio comptent : la synthese apprend une
    voix, pas un texte. Une declinaison riche en traductions mais sans
    enregistrement ne peut pas produire de voix propre, et c'est une
    information utile plutot qu'un echec.
    """
    avec_audio = [r for r in lignes if (r.get("audio_path") or "").strip()]
    base.mkdir(parents=True, exist_ok=True)
    with io.open(base / "metadata.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["audio_path", "text"])
        for r in avec_audio:
            w.writerow([r["audio_path"], r.get("target", "")])
    journal(f"Synthese — {len(avec_audio)} ligne(s) avec audio")
    return len(avec_audio)


def deposer(local: Path, uri: str) -> None:
    if not local.is_dir() or not any(local.iterdir()):
        journal(f"  rien a deposer dans {uri}")
        return
    journal(f"Depot : {uri}")
    gcloud_storage("cp", "-r", f"{local}/.", uri)


def main() -> int:
    variant = lire_env("VARIANT_ID")
    dataset_uri = lire_env("DATASET_URI")
    sortie_uri = lire_env("OUTPUT_PREFIX").rstrip("/")
    briques = [b.strip() for b in lire_env("BRICKS", False, "mt,tts").split(",") if b.strip()]

    journal(f"=== Declinaison {variant} ===")
    journal(f"  briques : {', '.join(briques) or 'aucune'}")

    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp)
        # Les chemins de travail vivent sur le disque de l'instance, qui
        # disparait avec elle. Seul le depot dans le stockage objet survit.
        os.environ["MGVAOVAO_DATASET_DIR"] = str(racine / "dataset")
        os.environ["MGVAOVAO_CHECKPOINTS_DIR"] = str(racine / "checkpoints")

        lignes = telecharger_dataset(dataset_uri, racine / "dataset.csv")
        if len(lignes) < MIN_LIGNES:
            journal(
                f"Corpus trop maigre ({len(lignes)} < {MIN_LIGNES}) : un modele affine "
                "la-dessus serait moins bon que le modele de base. Rien n'est entraine."
            )
            return 3

        if "mt" in briques:
            preparer_splits(lignes, racine / "dataset" / "nllb_finetune" / variant)
            entrainer_traduction(variant)
            deposer(racine / "checkpoints" / f"nllb_{variant}", f"{sortie_uri}/mt")

        if "tts" in briques:
            corpus_tts = racine / "dataset" / "tts_finetune" / variant
            if preparer_synthese(lignes, corpus_tts) == 0:
                journal("  aucune voix disponible : la synthese reste sur le modele de base")
            else:
                subprocess.run(
                    [
                        sys.executable,
                        str(RACINE / "training" / "train_tts.py"),
                        "--dialect",
                        variant,
                    ],
                    check=True,
                    cwd=str(RACINE),
                )
                deposer(racine / "checkpoints" / f"tts_{variant}", f"{sortie_uri}/tts")

    journal("=== termine — l'instance va etre detruite ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
