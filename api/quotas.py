# -*- coding: utf-8 -*-
"""
Quotas d'usage de la demonstration publique.

Le service tourne sur un GPU L4 facture a la seconde d'instance. Une session
WebSocket occupe une place de concurrence jusqu'a sa fermeture, et le
deploiement autorise jusqu'a deux instances : sans garde-fou, huit connexions
maintenues ouvertes suffisent a faire tourner deux GPU en continu, pour un cout
qui court tant que personne ne regarde. Le delai de Cloud Run etant regle a une
heure, une seule vague d'ouvertures repetees y parvient sans effort.

Les limites posees ici repondent a trois abus distincts :

- l'ouverture en rafale, qui epuise les places de concurrence (`RAFALE`) ;
- la session maintenue ouverte sans rien envoyer, qui occupe une place sans
  produire quoi que ce soit (`SILENCE_MAX_S`, `DUREE_MAX_SESSION_S`) ;
- l'usage massif mais licite en apparence, qui epuise le budget (`BUDGET_*`).

Tout est reglable par variable d'environnement : une limite ecrite en dur
oblige a reconstruire l'image pour laisser passer une demonstration devant des
partenaires, et c'est le genre de friction qui finit par faire desactiver le
garde-fou.

**Portee des compteurs.** Ils vivent en memoire, dans le processus. Avec deux
instances, chacune tient les siens : le budget global effectif peut donc
atteindre le double de `BUDGET_QUOTIDIEN_S`. C'est assume — un compteur partage
demanderait un Redis ou une base, soit une dependance de plus a maintenir et a
payer pour proteger une demonstration. L'ordre de grandeur suffit a empecher la
facture de deraper, ce qui est le but.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

# ── Reglages ──────────────────────────────────────────────────────────────


def _entier(nom: str, defaut: int) -> int:
    """Lit un entier d'environnement, en retombant sur le defaut si illisible."""
    try:
        valeur = int(os.getenv(nom, defaut))
    except (TypeError, ValueError):
        return defaut
    return valeur if valeur > 0 else defaut


@dataclass(frozen=True)
class Limites:
    # Sessions simultanees pour une meme adresse. Au-dela, c'est un script, pas
    # quelqu'un qui essaie la demonstration.
    sessions_par_ip: int = field(default_factory=lambda: _entier("QUOTA_SESSIONS_PAR_IP", 2))

    # Ouvertures autorisees par adresse sur une fenetre glissante. Vise la
    # rafale : reconnexions en boucle pour saturer les places de concurrence.
    rafale: int = field(default_factory=lambda: _entier("QUOTA_RAFALE", 10))
    rafale_fenetre_s: int = field(default_factory=lambda: _entier("QUOTA_RAFALE_FENETRE_S", 60))

    # Duree maximale d'une session. Le delai Cloud Run est d'une heure ; une
    # demonstration en dure quelques minutes.
    duree_max_session_s: int = field(default_factory=lambda: _entier("QUOTA_DUREE_SESSION_S", 600))

    # Une session qui n'envoie plus d'audio occupe une place pour rien.
    silence_max_s: int = field(default_factory=lambda: _entier("QUOTA_SILENCE_S", 120))

    # Budget de temps de session, par jour. Celui par adresse borne un
    # utilisateur, le global borne la facture.
    budget_ip_s: int = field(default_factory=lambda: _entier("QUOTA_BUDGET_IP_S", 1800))
    budget_global_s: int = field(default_factory=lambda: _entier("QUOTA_BUDGET_GLOBAL_S", 28800))

    # Requetes REST par adresse et par fenetre. Le pipeline tourne aussi sur
    # GPU : sans limite, /translate est la meme porte ouverte que le WebSocket.
    rest_par_fenetre: int = field(default_factory=lambda: _entier("QUOTA_REST", 30))
    rest_fenetre_s: int = field(default_factory=lambda: _entier("QUOTA_REST_FENETRE_S", 60))


LIMITES = Limites()

JOUR_S = 86_400


# ── Motifs de refus ───────────────────────────────────────────────────────
#
# Le message part au client : il doit dire quoi faire, pas seulement que c'est
# refuse. Le code sert aux journaux et au test de bout en bout.

REFUS = {
    "trop_de_sessions": (
        "Trop de sessions ouvertes depuis cette connexion. "
        "Fermez les autres onglets de la demonstration, puis reessayez."
    ),
    "rafale": (
        "Trop de tentatives de connexion en peu de temps. "
        "Patientez une minute avant de reessayer."
    ),
    "budget_ip": (
        "Vous avez atteint la duree d'essai quotidienne de la demonstration. "
        "Elle se reinitialise dans la journee ; ecrivez-nous pour un acces prolonge."
    ),
    "budget_global": (
        "La demonstration a atteint son quota d'utilisation pour aujourd'hui. "
        "Elle rouvre demain."
    ),
    "trop_de_requetes": (
        "Trop de requetes en peu de temps. Patientez une minute avant de reessayer."
    ),
}


class Refus(Exception):
    """Une limite a ete atteinte. `motif` est une cle de REFUS."""

    def __init__(self, motif: str):
        self.motif = motif
        self.message = REFUS.get(motif, "Quota atteint.")
        super().__init__(self.message)


# ── Compteurs ─────────────────────────────────────────────────────────────


class Compteurs:
    """
    Etat d'usage du processus.

    Aucune synchronisation : FastAPI sert les WebSockets sur une seule boucle
    d'evenements, et les appels ci-dessous ne rendent jamais la main au milieu
    d'une mise a jour. Un verrou n'ajouterait ici qu'une illusion de surete.
    """

    def __init__(self, limites: Limites = LIMITES):
        self.limites = limites
        self._sessions: dict[str, int] = defaultdict(int)
        self._ouvertures: dict[str, deque[float]] = defaultdict(deque)
        self._requetes: dict[str, deque[float]] = defaultdict(deque)
        self._consomme_ip: dict[str, float] = defaultdict(float)
        self._consomme_global: float = 0.0
        self._debut_jour: float = time.time()
        # Refus cumules depuis le demarrage, par motif. Un pic sur `rafale`
        # signale une attaque ; un pic sur `budget_global` signale seulement
        # que la demonstration a du succes. Les distinguer evite de durcir les
        # limites pour la mauvaise raison.
        self.refus: dict[str, int] = defaultdict(int)

    # ── remise a zero quotidienne ─────────────────────────────────────────

    def _tourner_le_jour(self, maintenant: float) -> None:
        if maintenant - self._debut_jour < JOUR_S:
            return
        self._consomme_ip.clear()
        self._consomme_global = 0.0
        self._debut_jour = maintenant

    @staticmethod
    def _elaguer(horodatages: deque[float], maintenant: float, fenetre: int) -> None:
        while horodatages and maintenant - horodatages[0] > fenetre:
            horodatages.popleft()

    # ── WebSocket ─────────────────────────────────────────────────────────

    def ouvrir_session(self, ip: str) -> None:
        """Enregistre une ouverture, ou leve Refus. A appeler avant d'accepter."""
        maintenant = time.time()
        self._tourner_le_jour(maintenant)
        lim = self.limites

        if self._consomme_global >= lim.budget_global_s:
            self._refuser("budget_global")
        if self._consomme_ip[ip] >= lim.budget_ip_s:
            self._refuser("budget_ip")

        ouvertures = self._ouvertures[ip]
        self._elaguer(ouvertures, maintenant, lim.rafale_fenetre_s)
        if len(ouvertures) >= lim.rafale:
            self._refuser("rafale")

        if self._sessions[ip] >= lim.sessions_par_ip:
            self._refuser("trop_de_sessions")

        ouvertures.append(maintenant)
        self._sessions[ip] += 1

    def fermer_session(self, ip: str, duree_s: float) -> None:
        """Libere la place et impute la duree aux budgets."""
        self._sessions[ip] = max(0, self._sessions[ip] - 1)
        if self._sessions[ip] == 0:
            self._sessions.pop(ip, None)
        duree = max(0.0, duree_s)
        self._consomme_ip[ip] += duree
        self._consomme_global += duree

    # ── REST ──────────────────────────────────────────────────────────────

    def requete(self, ip: str) -> None:
        """Compte un appel REST, ou leve Refus."""
        maintenant = time.time()
        self._tourner_le_jour(maintenant)
        lim = self.limites

        if self._consomme_global >= lim.budget_global_s:
            self._refuser("budget_global")

        recentes = self._requetes[ip]
        self._elaguer(recentes, maintenant, lim.rest_fenetre_s)
        if len(recentes) >= lim.rest_par_fenetre:
            self._refuser("trop_de_requetes")
        recentes.append(maintenant)

    # ── lecture ───────────────────────────────────────────────────────────

    def _refuser(self, motif: str):
        self.refus[motif] += 1
        raise Refus(motif)

    def etat(self) -> dict:
        """Vue d'ensemble, pour la supervision et le test de bout en bout."""
        maintenant = time.time()
        self._tourner_le_jour(maintenant)
        lim = self.limites
        return {
            "sessions_ouvertes": sum(self._sessions.values()),
            "adresses_actives": len(self._sessions),
            "budget_global_s": lim.budget_global_s,
            "budget_global_consomme_s": round(self._consomme_global, 1),
            "budget_global_restant_s": round(
                max(0.0, lim.budget_global_s - self._consomme_global), 1
            ),
            "secondes_avant_remise_a_zero": round(
                max(0.0, JOUR_S - (maintenant - self._debut_jour)), 1
            ),
            "refus": dict(self.refus),
            "limites": {
                "sessions_par_ip": lim.sessions_par_ip,
                "rafale": lim.rafale,
                "rafale_fenetre_s": lim.rafale_fenetre_s,
                "duree_max_session_s": lim.duree_max_session_s,
                "silence_max_s": lim.silence_max_s,
                "budget_ip_s": lim.budget_ip_s,
                "rest_par_fenetre": lim.rest_par_fenetre,
                "rest_fenetre_s": lim.rest_fenetre_s,
            },
        }


COMPTEURS = Compteurs()


# ── Identification de l'appelant ──────────────────────────────────────────


def adresse(requete_ou_ws) -> str:
    """
    Adresse de l'appelant.

    Cloud Run termine TLS en amont : `client.host` est celui du proxy, identique
    pour tout le monde, et compter dessus reviendrait a n'avoir qu'un seul
    compteur pour la planete. La premiere adresse de `X-Forwarded-For` est celle
    du client.

    Elle est falsifiable par un en-tete force, mais l'infrastructure de Google
    reecrit cet en-tete en y ajoutant l'adresse reelle en derniere position
    avant la sienne ; surtout, la falsification ne contourne pas le budget
    global, qui est le garde-fou qui compte pour la facture.
    """
    entetes = getattr(requete_ou_ws, "headers", {}) or {}
    transmis = entetes.get("x-forwarded-for") or entetes.get("X-Forwarded-For")
    if transmis:
        premiere = transmis.split(",")[0].strip()
        if premiere:
            return premiere
    client = getattr(requete_ou_ws, "client", None)
    return getattr(client, "host", None) or "inconnu"
