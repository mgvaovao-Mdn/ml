# -*- coding: utf-8 -*-
"""
Machine à états du tour de parole, pour une session de traduction en continu.

Le problème qu'elle résout
──────────────────────────
Sans elle, le service se met à se parler à lui-même. Le modèle synthétise une
réponse, le client la joue sur les haut-parleurs, le micro la capte, elle repart
dans le WebSocket, le VAD y détecte de la parole, le pipeline la transcrit et la
retraduit — puis synthétise à nouveau. La boucle ne s'arrête jamais et chaque
tour consomme du GPU.

Un simple verrou « une exécution à la fois » ne suffit pas : il empêche les
exécutions simultanées, mais l'audio reçu pendant le traitement continue
d'alimenter le VAD, et le tour suivant se déclenche dès le verrou relâché.

La règle appliquée ici
──────────────────────
Le microphone n'est écouté que pendant LISTENING. Dans tout autre état, les
trames reçues sont ignorées *et* le VAD est réinitialisé — sans cette
réinitialisation, le tampon accumulerait la voix du modèle et l'émettrait dès le
retour à l'écoute.

    LISTENING  ──(fin de parole détectée)──▶  PROCESSING
    PROCESSING ──(résultat envoyé)────────▶  SPEAKING
    SPEAKING   ──(le client signale la fin de lecture)──▶  LISTENING
    SPEAKING   ──(délai de garde dépassé)─▶  LISTENING

Le délai de garde existe parce qu'un client peut se fermer, planter ou oublier
d'envoyer la fin de lecture : sans lui, la session resterait sourde pour
toujours. Il vaut la durée de l'audio synthétisé plus une marge.

Interruption (barge-in)
───────────────────────
Désactivée par défaut, et c'est délibéré : pour distinguer la voix de
l'utilisateur de celle du modèle pendant la lecture, il faut une annulation
d'écho côté client. Sans elle, autoriser l'interruption rouvre exactement la
boucle qu'on vient de fermer. Un client qui implémente l'annulation d'écho peut
l'activer explicitement.
"""
from __future__ import annotations

import time
from enum import Enum


class TurnState(str, Enum):
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class TurnController:
    """
    Décide, trame par trame, si l'audio entrant doit être écouté.

    `speaking_grace_s` : marge ajoutée à la durée de l'audio synthétisé avant de
    reprendre l'écoute de force. Couvre la latence réseau et le délai de
    démarrage du lecteur côté client.
    """

    def __init__(
        self,
        *,
        allow_barge_in: bool = False,
        speaking_grace_s: float = 1.5,
        max_speaking_s: float = 60.0,
    ) -> None:
        self._state = TurnState.LISTENING
        self._allow_barge_in = allow_barge_in
        self._speaking_grace_s = speaking_grace_s
        self._max_speaking_s = max_speaking_s
        self._speaking_until: float | None = None

    # ── Lecture ──────────────────────────────────────────────────────────────

    @property
    def state(self) -> TurnState:
        return self._state

    def accepts_audio(self) -> bool:
        """Vrai si la trame entrante doit alimenter le VAD."""
        if self._state is TurnState.LISTENING:
            return True
        if self._state is TurnState.SPEAKING and self._allow_barge_in:
            return True
        return False

    def expired(self) -> bool:
        """
        Vrai si l'état SPEAKING dure au-delà du délai de garde.

        Protège contre un client qui ne signalerait jamais la fin de lecture :
        sans ce retour forcé, la session n'écouterait plus jamais.
        """
        if self._state is not TurnState.SPEAKING or self._speaking_until is None:
            return False
        return time.monotonic() >= self._speaking_until

    # ── Transitions ──────────────────────────────────────────────────────────

    def begin_processing(self) -> None:
        self._state = TurnState.PROCESSING
        self._speaking_until = None

    def begin_speaking(self, audio_duration_s: float | None) -> None:
        """
        Entre en lecture. `audio_duration_s` vient de l'audio synthétisé ; sans
        elle, on retombe sur la borne maximale plutôt que de risquer un blocage.
        """
        self._state = TurnState.SPEAKING
        if audio_duration_s is None or audio_duration_s <= 0:
            window = self._max_speaking_s
        else:
            window = min(audio_duration_s + self._speaking_grace_s, self._max_speaking_s)
        self._speaking_until = time.monotonic() + window

    def resume_listening(self) -> None:
        self._state = TurnState.LISTENING
        self._speaking_until = None
