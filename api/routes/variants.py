"""
Declinaisons proposees par la demonstration.

Ce qu'une declinaison represente
────────────────────────────────
Une entreprise ne demande pas « du betsileo ». Elle demande « une voix
betsileo, jeune, feminine, qui comprend l'anglais » — une combinaison de
categories. C'est cette combinaison que la demonstration doit savoir
selectionner, sinon elle ne montre pas le produit.

D'ou elles viennent
───────────────────
De la plateforme de collecte, comme les dialectes : c'est son CRUD qui porte
les categories, et les combinaisons en sont engendrees. Ouvrir une categorie
la-bas la rend selectionnable ici, sans redeploiement.

Ce que la demonstration sert reellement
───────────────────────────────────────
Aucun modele propre a une declinaison n'existe encore. Toutes sont donc
servies par le modele de base. La reponse le dit, declinaison par declinaison,
avec `modele.propre`. Laisser croire a une voix sur mesure se retournerait
contre le projet a la premiere ecoute — et rendrait invendable ce qui le sera
vraiment le jour ou un entrainement aboutira.
"""
from __future__ import annotations

import os
import threading
import time

import requests
from fastapi import APIRouter

router = APIRouter()

COLLECTION_URL = os.environ.get("MGVAOVAO_COLLECTION_URL", "https://kozy.mg").rstrip("/")

CACHE_TTL_SECONDS = 60
FETCH_TIMEOUT_SECONDS = 4

_cache: dict = {"at": 0.0, "data": None}
_lock = threading.Lock()


def _fetch() -> dict | None:
    """Lit le registre distant. `None` si la plateforme est injoignable."""
    try:
        reponse = requests.get(
            f"{COLLECTION_URL}/api/public/variants", timeout=FETCH_TIMEOUT_SECONDS
        )
        reponse.raise_for_status()
        charge = reponse.json()
        if not charge.get("variants"):
            # Une reponse vide n'est pas une reponse : elle viderait les menus
            # de la demonstration.
            return None
        return charge
    except Exception:
        return None


def registre() -> dict:
    """
    Registre des declinaisons, avec cache.

    Le repli est un registre vide plutot qu'une table ecrite en dur : une
    combinaison inventee ici ne correspondrait a aucun jeu de donnees, et la
    demonstration proposerait un produit qui n'existe pas.
    """
    maintenant = time.time()
    with _lock:
        if _cache["data"] is not None and maintenant - _cache["at"] < CACHE_TTL_SECONDS:
            return _cache["data"]

    frais = _fetch()
    with _lock:
        if frais is not None:
            _cache["data"] = frais
            _cache["at"] = maintenant
        elif _cache["data"] is None:
            _cache["data"] = {"axes": {}, "variants": []}
            _cache["at"] = maintenant
        return _cache["data"]


def trouver(variant_id: str) -> dict | None:
    """Declinaison par son identifiant, ou `None`."""
    for v in registre().get("variants", []):
        if v.get("id") == variant_id:
            return v
    return None


def resoudre(
    dialecte: str,
    langue: str | None = None,
    tranche_age: str | None = None,
    sexe: str | None = None,
    thematique: str | None = None,
) -> dict | None:
    """
    Trouve la declinaison correspondant aux axes demandes.

    Une correspondance exacte est cherchee d'abord ; a defaut on elargit, du
    plus specifique au plus general. Refuser faute de combinaison exacte
    priverait la personne d'une demonstration qui, de toute facon, sera servie
    par le meme modele de base.

    Le dialecte de sortie et la langue d'entree ne sont jamais elargis : livrer
    un autre dialecte que celui demande serait livrer autre chose que le
    produit, et changer la langue d'entree rendrait la demonstration
    incomprehensible sans dire pourquoi.
    """
    candidats = [
        (thematique, tranche_age, sexe),
        (thematique, tranche_age, None),
        (thematique, None, sexe),
        (thematique, None, None),
        (None, tranche_age, sexe),
        (None, tranche_age, None),
        (None, None, sexe),
        (None, None, None),
    ]
    for th, age, sx in candidats:
        for v in registre().get("variants", []):
            if v.get("dialecte") != dialecte:
                continue
            if langue and v.get("langue") != langue:
                continue
            if (v.get("thematique") or None) != th:
                continue
            if v.get("trancheAge") != age:
                continue
            if v.get("sexe") != sx:
                continue
            return v
    return None


@router.get("/", summary="Combinaisons selectionnables et ce qu'elles valent")
def lister():
    return registre()
