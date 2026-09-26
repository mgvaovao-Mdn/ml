# -*- coding: utf-8 -*-
"""
Acces au stockage objet depuis un job, sans CLI.

Le script d'affinage appelait `gcloud storage`. L'image d'inference ne
contient pas le CLI : le job demarrait un GPU, echouait sur
« FileNotFoundError: gcloud », et sortait. Supposer qu'un outil en ligne de
commande est present dans une image que l'on n'a pas construite pour cela est
une dependance invisible — celle-ci a coute deux lancements.

On passe donc par l'API REST de Cloud Storage avec `requests`, deja dans les
dependances du projet, et par le jeton du serveur de metadonnees, toujours
disponible sur Cloud Run.
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

import requests

METADATA = "http://metadata.google.internal/computeMetadata/v1"
API = "https://storage.googleapis.com/storage/v1"
UPLOAD = "https://storage.googleapis.com/upload/storage/v1"

DELAI_S = 60


def _jeton() -> str:
    """
    Jeton d'acces du compte de service de la tache.

    Trois voies, dans cet ordre :

    1. `GCS_ACCESS_TOKEN`, pour eprouver le module hors production sans
       installer de dependance — c'est ce qui manquait quand le job a echoue
       deux fois de suite sur un stockage que personne n'avait teste ;
    2. le serveur de metadonnees, toujours present sur Cloud Run ;
    3. les identifiants applicatifs par defaut, si `google-auth` est la.
    """
    explicite = os.environ.get("GCS_ACCESS_TOKEN", "").strip()
    if explicite:
        return explicite

    try:
        r = requests.get(
            f"{METADATA}/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"},
            timeout=5,
        )
        r.raise_for_status()
        return r.json()["access_token"]
    except Exception:
        pass

    try:
        import google.auth
        import google.auth.transport.requests

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/devstorage.read_write"]
        )
        creds.refresh(google.auth.transport.requests.Request())
        return creds.token
    except Exception as exc:
        raise RuntimeError(
            "Aucun jeton d'acces au stockage : ni serveur de metadonnees, "
            f"ni identifiants applicatifs par defaut ({exc})."
        ) from None


def decouper(uri: str) -> tuple[str, str]:
    """« gs://seau/chemin/objet » -> (« seau », « chemin/objet »)."""
    if not uri.startswith("gs://"):
        raise ValueError(f"URI de stockage attendue en gs:// — recu : {uri}")
    reste = uri[5:]
    seau, _, objet = reste.partition("/")
    if not seau or not objet:
        raise ValueError(f"URI incomplete : {uri}")
    return seau, objet


def telecharger(uri: str, destination: Path) -> Path:
    """Copie un objet vers un fichier local."""
    seau, objet = decouper(uri)
    url = f"{API}/b/{seau}/o/{quote(objet, safe='')}?alt=media"
    r = requests.get(url, headers={"Authorization": f"Bearer {_jeton()}"}, timeout=DELAI_S)
    if r.status_code == 404:
        raise FileNotFoundError(f"Objet introuvable : {uri}")
    r.raise_for_status()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(r.content)
    return destination


def televerser(source: Path, uri: str) -> None:
    """Copie un fichier local vers un objet."""
    seau, objet = decouper(uri)
    url = f"{UPLOAD}/b/{seau}/o?uploadType=media&name={quote(objet, safe='')}"
    with io_ouvrir(source) as f:
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {_jeton()}",
                "Content-Type": "application/octet-stream",
            },
            data=f,
            timeout=DELAI_S * 10,
        )
    r.raise_for_status()


def io_ouvrir(chemin: Path):
    return open(chemin, "rb")


def deposer_repertoire(local: Path, prefixe_uri: str) -> int:
    """
    Copie un repertoire entier, en conservant son arborescence.

    Renvoie le nombre de fichiers deposes. Zero n'est pas une erreur : une
    brique qui n'a rien produit — faute de corpus audio, par exemple — doit le
    dire sans faire echouer le reste.
    """
    if not local.is_dir():
        return 0
    deposes = 0
    for fichier in sorted(local.rglob("*")):
        if not fichier.is_file():
            continue
        relatif = fichier.relative_to(local).as_posix()
        televerser(fichier, f"{prefixe_uri.rstrip('/')}/{relatif}")
        deposes += 1
    return deposes
