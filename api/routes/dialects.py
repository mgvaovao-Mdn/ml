"""
Liste des dialectes proposes par la demonstration.

La source de verite est la plateforme de collecte : c'est son CRUD qui porte
les dialectes et leur configuration de modele. Les lire en direct evite deux
derives que la table figee de `config.py` rendait inevitables — un dialecte
ajoute la-bas n'apparaissait jamais ici, et un dialecte renomme y gardait son
ancien nom jusqu'au prochain deploiement.

La lecture distante ne doit jamais empecher la demonstration de fonctionner :
si la plateforme est injoignable, on retombe sur la table locale. Une demo qui
tombe en panne parce qu'un autre service est lent serait pire que des libelles
un peu datés.
"""
from __future__ import annotations

import os
import threading
import time

import requests
from fastapi import APIRouter, Request

from mgvaovao.core.config import DIALECTS, DIALECT_META
from mgvaovao.core.schemas import DialectInfo

router = APIRouter()

# Plateforme de collecte. Configurable : elle change d'URL avec le domaine.
COLLECTION_URL = os.environ.get(
    "MGVAOVAO_COLLECTION_URL", "https://kozy.mg"
).rstrip("/")

# Duree de vie du cache. Assez court pour qu'un dialecte ajoute apparaisse dans
# la minute, assez long pour ne pas interroger la plateforme a chaque clic.
CACHE_TTL_SECONDS = 60

# Au-dela, on renonce et on sert le repli : la demonstration doit repondre.
FETCH_TIMEOUT_SECONDS = 4

# Dialecte qui repond quand aucun modele propre n'est encore entraine. C'est le
# malgache officiel : le seul dont le corpus suffit aujourd'hui.
BASE_DIALECT = "plt_latn"

_cache: dict = {"at": 0.0, "data": None}
_lock = threading.Lock()


def _fetch_remote() -> list[dict] | None:
    """Lit les dialectes de la plateforme. `None` si elle est injoignable."""
    try:
        response = requests.get(
            f"{COLLECTION_URL}/api/public/dialects",
            timeout=FETCH_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        entries = payload.get("dialects")
        # Une reponse vide n'est pas une reponse valide : elle ferait
        # disparaitre tous les dialectes de la demonstration.
        if isinstance(entries, list) and entries:
            return entries
    except Exception:
        pass
    return None


def _remote_dialects() -> list[dict] | None:
    """Version mise en cache de `_fetch_remote`."""
    now = time.time()
    with _lock:
        if _cache["data"] is not None and now - _cache["at"] < CACHE_TTL_SECONDS:
            return _cache["data"]

    entries = _fetch_remote()
    if entries is not None:
        with _lock:
            _cache["at"] = now
            _cache["data"] = entries
    return entries


def _local_dialects() -> list[dict]:
    """Repli : la table embarquee, telle que l'entrainement la connait."""
    return [
        {
            "id": code,
            "name": DIALECT_META[code].get("name", code),
            "enregistrements": 0,
            "traductions": 0,
        }
        for code in DIALECTS
    ]


@router.get(
    "/",
    response_model=list[DialectInfo],
    summary="Dialectes disponibles et etat des modeles",
)
def list_dialects(request: Request):
    # `pipelines` contient un pipeline pour CHAQUE dialecte, avec ou sans
    # modele fine-tune : s'y fier annoncerait un modele dedie partout. C'est
    # `finetuned` qui dit si un checkpoint propre au dialecte a ete trouve au
    # demarrage.
    finetuned = getattr(request.app.state, "finetuned", {})
    entries = _remote_dialects() or _local_dialects()

    resultats: list[DialectInfo] = []
    for entry in entries:
        code = entry.get("id")
        if not code:
            continue

        # Region et population sont des libelles de presentation : ils vivent
        # ici, pas dans la base de collecte. Un dialecte cree recemment n'en a
        # donc pas encore, et c'est sans consequence.
        meta = DIALECT_META.get(code, {})

        # Un dialecte n'est « pret » que si la traduction ET la synthese ont
        # leur propre modele. Avec l'un des deux seulement, la restitution
        # n'est pas dialectale de bout en bout, et l'annoncer comme dediee
        # serait trompeur.
        etat = finetuned.get(code) or {}
        pret = bool(etat.get("nllb")) and bool(etat.get("tts"))

        resultats.append(
            DialectInfo(
                code=code,
                name=entry.get("name") or meta.get("name", code),
                region=meta.get("region", ""),
                population=meta.get("population", ""),
                phase=meta.get("phase", 4),
                model_ready=pret,
                # Tant qu'aucun modele propre n'existe, c'est le modele de base
                # qui repond. Le dire permet a l'interface d'etre franche
                # plutot que de faire passer du malgache officiel pour du
                # dialecte.
                served_by=code if pret else BASE_DIALECT,
                recordings=int(entry.get("enregistrements", 0) or 0),
                translations=int(entry.get("traductions", 0) or 0),
            )
        )

    return resultats
