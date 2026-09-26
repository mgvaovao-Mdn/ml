# -*- coding: utf-8 -*-
"""
Resolution d'une declinaison depuis les axes demandes.

    python -m unittest discover -s api/tests -t .

Ce qui est verifie : qu'une combinaison demandee trouve la declinaison la plus
proche, et surtout qu'elle n'en trouve pas une qui serait fausse. Servir la
voix masculine a qui a demande la feminine serait pire que ne rien servir : la
demonstration donnerait une impression de produit sur mesure la ou il n'y en a
pas, et le client s'en apercevrait au moment de l'achat.
"""
import unittest

from api.routes import variants


def registre(entrees):
    """Remplace le registre distant par une liste connue, cache compris."""
    variants._cache["data"] = {"axes": {}, "variants": entrees}
    variants._cache["at"] = float("inf")


def declinaison(dialecte, langue, age=None, sexe=None, theme=None, propre=False):
    cle = f"{dialecte}__{langue}__{age or 'tousages'}__{(sexe or 'tous').lower()}"
    return {
        "id": cle + (f"__{theme}" if theme else ""),
        "dialecte": dialecte,
        "langue": langue,
        "trancheAge": age,
        "sexe": sexe,
        "thematique": theme,
        "corpus": {"traductions": 0, "enregistrements": 0, "secondesAudio": 0},
        "modele": {
            "propre": propre,
            "statut": "TRAINED" if propre else "BASELINE",
            "briques": {
                "asr": "BASELINE",
                "mt": "TRAINED" if propre else "BASELINE",
                "tts": "BASELINE",
            },
        },
    }


class Resolution(unittest.TestCase):
    def setUp(self):
        registre([
            declinaison("betsileo", "en"),
            declinaison("betsileo", "en", "18_25"),
            declinaison("betsileo", "en", "18_25", "FEMALE"),
            declinaison("betsileo", "fr"),
            declinaison("sakalava", "en"),
        ])

    def tearDown(self):
        variants._cache["data"] = None
        variants._cache["at"] = 0.0

    def test_correspondance_exacte(self):
        # Le cas commercial : « voix betsileo, jeune, feminine, entree anglaise ».
        v = variants.resoudre("betsileo", "en", "18_25", "FEMALE")
        self.assertEqual(v["id"], "betsileo__en__18_25__female")

    def test_elargit_le_sexe_a_defaut(self):
        # Pas de declinaison masculine enregistree : on elargit plutot que de
        # refuser, puisque le modele servi serait de toute facon le meme.
        v = variants.resoudre("betsileo", "en", "18_25", "MALE")
        self.assertEqual(v["trancheAge"], "18_25")
        self.assertIsNone(v["sexe"])

    def test_elargit_l_age_a_defaut(self):
        v = variants.resoudre("betsileo", "en", "56_plus", "FEMALE")
        self.assertIsNone(v["trancheAge"])
        self.assertIsNone(v["sexe"])

    def test_ne_change_jamais_de_dialecte(self):
        # Le dialecte de sortie est le produit : l'elargir reviendrait a livrer
        # autre chose que ce qui a ete demande.
        self.assertIsNone(variants.resoudre("merina", "en"))

    def test_ne_change_jamais_de_langue_d_entree(self):
        # Servir l'entree francaise a qui parle anglais rendrait la
        # demonstration incomprehensible sans dire pourquoi.
        self.assertIsNone(variants.resoudre("sakalava", "de"))

    def test_sans_langue_prend_la_premiere_du_dialecte(self):
        # Detection automatique de la langue : aucun axe de langue impose.
        v = variants.resoudre("betsileo", None)
        self.assertEqual(v["dialecte"], "betsileo")

    def test_registre_vide_ne_leve_pas(self):
        registre([])
        self.assertIsNone(variants.resoudre("betsileo", "en"))


class AxeThematique(unittest.TestCase):
    def setUp(self):
        registre([
            declinaison("betsileo", "en"),
            declinaison("betsileo", "en", theme="sante"),
            declinaison("betsileo", "en", "18_25", "FEMALE", "sante"),
        ])

    def tearDown(self):
        variants._cache["data"] = None
        variants._cache["at"] = 0.0

    def test_combinaison_complete(self):
        # Le cas commercial complet : centre d'appels sante, voix de jeune
        # femme betsileo, entree anglaise.
        v = variants.resoudre("betsileo", "en", "18_25", "FEMALE", "sante")
        self.assertEqual(v["id"], "betsileo__en__18_25__female__sante")

    def test_elargit_la_voix_avant_la_thematique(self):
        # Le domaine prime sur la voix : un centre d'appels sante servi avec
        # un corpus sport serait hors sujet, alors qu'une voix d'un autre age
        # reste comprehensible.
        v = variants.resoudre("betsileo", "en", "46_55", "MALE", "sante")
        self.assertEqual(v["thematique"], "sante")
        self.assertIsNone(v["trancheAge"])

    def test_retombe_sur_toutes_thematiques(self):
        v = variants.resoudre("betsileo", "en", None, None, "politique")
        self.assertIsNone(v["thematique"])

    def test_sans_thematique_ne_prend_pas_une_thematique(self):
        # Demander « toutes thematiques » doit donner le corpus large, pas
        # celui d'une thematique choisie au hasard.
        v = variants.resoudre("betsileo", "en")
        self.assertIsNone(v["thematique"])


class Repli(unittest.TestCase):
    def tearDown(self):
        variants._cache["data"] = None
        variants._cache["at"] = 0.0

    def test_plateforme_injoignable_rend_un_registre_vide(self):
        # Le repli n'invente pas de combinaisons : une declinaison ecrite en
        # dur ici ne correspondrait a aucun jeu de donnees, et la demonstration
        # proposerait un produit qui n'existe pas.
        variants._cache["data"] = None
        variants._cache["at"] = 0.0
        original = variants._fetch
        variants._fetch = lambda: None
        try:
            self.assertEqual(variants.registre()["variants"], [])
        finally:
            variants._fetch = original


if __name__ == "__main__":
    unittest.main()
