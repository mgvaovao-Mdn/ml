# -*- coding: utf-8 -*-
"""
Resolution du dialecte a partir d'un identifiant de corpus.

    python -m unittest discover -s api/tests -t .

Ce que ce test protege : un entrainement lance sur une declinaison cherchait
son jeton cible NLLB dans la table des dialectes avec l'identifiant complet —
« plt_latn__fr__tousages__tous » — et echouait sur un KeyError. Pas au
demarrage : APRES avoir reserve un GPU, telecharge le corpus et prepare ses
ensembles. Tout le travail perdu, et le GPU facture.

Un test qui coute une milliseconde remplace un aller-retour de trois minutes
sur une machine facturee.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from mgvaovao.core.config import DIALECT_META, meta_du_corpus  # noqa: E402


class ResolutionDuCorpus(unittest.TestCase):
    def test_dialecte_seul(self):
        # Le cas historique : le corpus EST le dialecte.
        self.assertEqual(meta_du_corpus("plt_latn")["nllb_target"], "plt_Latn")

    def test_declinaison_de_voix(self):
        # Le dialecte est le premier segment ; les axes de voix ne changent que
        # le sous-ensemble de lignes, jamais la langue cible.
        self.assertEqual(
            meta_du_corpus("plt_latn__fr__tousages__tous")["nllb_target"], "plt_Latn"
        )

    def test_declinaison_avec_thematique(self):
        self.assertEqual(
            meta_du_corpus("betsileo__en__18_25__female__sante")["nllb_target"],
            "pltbts_Latn",
        )

    def test_chaque_dialecte_se_resout_sous_forme_de_declinaison(self):
        # Sans cette boucle, un dialecte ajoute plus tard pourrait echouer
        # silencieusement jusqu'au premier entrainement.
        for dialecte in DIALECT_META:
            avec_axes = f"{dialecte}__fr__18_25__female"
            self.assertEqual(
                meta_du_corpus(avec_axes)["nllb_target"],
                DIALECT_META[dialecte]["nllb_target"],
                f"declinaison de {dialecte} non resolue",
            )

    def test_corpus_inconnu_refuse_avec_un_message_utile(self):
        # Le message doit nommer ce qui a ete cherche : sans cela, on relit le
        # code pour comprendre ce que « KeyError » designe.
        with self.assertRaises(KeyError) as ctx:
            meta_du_corpus("merina__fr__tousages__tous")
        message = str(ctx.exception)
        self.assertIn("merina", message)
        self.assertIn("plt_latn", message)

    def test_ne_confond_pas_un_prefixe_partiel(self):
        # « plt » n'est pas « plt_latn » : accepter un prefixe approchant
        # entrainerait avec le mauvais jeton cible, et le defaut ne se verrait
        # qu'a l'ecoute.
        with self.assertRaises(KeyError):
            meta_du_corpus("plt__fr__tousages__tous")


if __name__ == "__main__":
    unittest.main()
