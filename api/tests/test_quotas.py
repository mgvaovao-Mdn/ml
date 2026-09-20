# -*- coding: utf-8 -*-
"""
Tests des quotas de la demonstration.

    python -m unittest discover -s api/tests -t .

`unittest` plutot que pytest : le depot n'a pas de dependance de test, et en
ajouter une pour verifier un compteur obligerait a l'installer partout ou l'on
veut lancer ces tests, y compris dans l'image de deploiement.

Ce qui est verifie ici, ce n'est pas que le compteur compte, mais que chaque
limite refuse bien l'abus qu'elle vise, et surtout qu'aucune ne refuse un usage
normal : un garde-fou qui ferme la porte a un partenaire en demonstration sera
desactive dans l'heure, et ne protegera plus rien.
"""
import unittest

from api.quotas import Compteurs, Limites, Refus, adresse


def limites(**remplacements) -> Limites:
    """Limites par defaut, avec les champs indiques remplaces."""
    base = dict(
        sessions_par_ip=2,
        rafale=10,
        rafale_fenetre_s=60,
        duree_max_session_s=600,
        silence_max_s=120,
        budget_ip_s=1800,
        budget_global_s=28800,
        rest_par_fenetre=30,
        rest_fenetre_s=60,
    )
    base.update(remplacements)
    return Limites(**base)


class UsageNormal(unittest.TestCase):
    def test_une_session_passe(self):
        c = Compteurs(limites())
        c.ouvrir_session("1.1.1.1")
        self.assertEqual(c.etat()["sessions_ouvertes"], 1)

    def test_deux_onglets_passent(self):
        # Ouvrir la demonstration dans deux onglets est courant, notamment pour
        # comparer deux dialectes. Le refuser serait une gene, pas une garde.
        c = Compteurs(limites())
        c.ouvrir_session("1.1.1.1")
        c.ouvrir_session("1.1.1.1")
        self.assertEqual(c.etat()["sessions_ouvertes"], 2)

    def test_la_place_est_rendue_a_la_fermeture(self):
        c = Compteurs(limites(sessions_par_ip=1))
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", 12.0)
        c.ouvrir_session("1.1.1.1")  # ne doit pas lever
        self.assertEqual(c.etat()["sessions_ouvertes"], 1)

    def test_deux_adresses_ne_se_genent_pas(self):
        c = Compteurs(limites(sessions_par_ip=1))
        c.ouvrir_session("1.1.1.1")
        c.ouvrir_session("2.2.2.2")
        self.assertEqual(c.etat()["adresses_actives"], 2)


class SessionsSimultanees(unittest.TestCase):
    def test_refus_au_dela_de_la_limite(self):
        c = Compteurs(limites(sessions_par_ip=2))
        c.ouvrir_session("1.1.1.1")
        c.ouvrir_session("1.1.1.1")
        with self.assertRaises(Refus) as ctx:
            c.ouvrir_session("1.1.1.1")
        self.assertEqual(ctx.exception.motif, "trop_de_sessions")

    def test_le_refus_porte_un_message_utile(self):
        # Le message part au navigateur : il doit dire quoi faire.
        c = Compteurs(limites(sessions_par_ip=1))
        c.ouvrir_session("1.1.1.1")
        with self.assertRaises(Refus) as ctx:
            c.ouvrir_session("1.1.1.1")
        self.assertIn("onglets", ctx.exception.message)


class Rafale(unittest.TestCase):
    def test_reconnexions_en_boucle_refusees(self):
        # L'abus vise : ouvrir et fermer sans cesse pour occuper les places de
        # concurrence. Fermer ne doit pas remettre le compteur de rafale a zero.
        c = Compteurs(limites(rafale=5, sessions_par_ip=10))
        for _ in range(5):
            c.ouvrir_session("1.1.1.1")
            c.fermer_session("1.1.1.1", 0.1)
        with self.assertRaises(Refus) as ctx:
            c.ouvrir_session("1.1.1.1")
        self.assertEqual(ctx.exception.motif, "rafale")

    def test_la_rafale_est_comptee_par_adresse(self):
        c = Compteurs(limites(rafale=2, sessions_par_ip=10))
        c.ouvrir_session("1.1.1.1")
        c.ouvrir_session("1.1.1.1")
        c.ouvrir_session("2.2.2.2")  # ne doit pas lever
        with self.assertRaises(Refus):
            c.ouvrir_session("1.1.1.1")


class Budgets(unittest.TestCase):
    def test_budget_par_adresse(self):
        c = Compteurs(limites(budget_ip_s=60, sessions_par_ip=10))
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", 61.0)
        with self.assertRaises(Refus) as ctx:
            c.ouvrir_session("1.1.1.1")
        self.assertEqual(ctx.exception.motif, "budget_ip")

    def test_une_adresse_epuisee_ne_bloque_pas_les_autres(self):
        c = Compteurs(limites(budget_ip_s=60, sessions_par_ip=10))
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", 61.0)
        c.ouvrir_session("2.2.2.2")  # ne doit pas lever

    def test_budget_global_ferme_a_tout_le_monde(self):
        # C'est le garde-fou qui borne la facture : il doit tenir meme face a
        # des adresses toutes differentes, donc a une adresse falsifiee.
        c = Compteurs(limites(budget_global_s=100, budget_ip_s=10_000, sessions_par_ip=10))
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", 101.0)
        with self.assertRaises(Refus) as ctx:
            c.ouvrir_session("9.9.9.9")
        self.assertEqual(ctx.exception.motif, "budget_global")

    def test_le_budget_global_coupe_aussi_le_rest(self):
        c = Compteurs(limites(budget_global_s=100))
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", 101.0)
        with self.assertRaises(Refus) as ctx:
            c.requete("5.5.5.5")
        self.assertEqual(ctx.exception.motif, "budget_global")

    def test_une_duree_negative_ne_rend_pas_de_budget(self):
        # Une horloge qui recule ne doit pas devenir une facon de se recharger.
        c = Compteurs(limites())
        c.ouvrir_session("1.1.1.1")
        c.fermer_session("1.1.1.1", -500.0)
        self.assertEqual(c.etat()["budget_global_consomme_s"], 0.0)


class QuotaRest(unittest.TestCase):
    def test_refus_au_dela_de_la_fenetre(self):
        c = Compteurs(limites(rest_par_fenetre=3))
        for _ in range(3):
            c.requete("1.1.1.1")
        with self.assertRaises(Refus) as ctx:
            c.requete("1.1.1.1")
        self.assertEqual(ctx.exception.motif, "trop_de_requetes")

    def test_compte_par_adresse(self):
        c = Compteurs(limites(rest_par_fenetre=1))
        c.requete("1.1.1.1")
        c.requete("2.2.2.2")  # ne doit pas lever


class Journal(unittest.TestCase):
    def test_les_refus_sont_distingues_par_motif(self):
        # Un pic de « rafale » est une attaque ; un pic de « budget_global »
        # est un succes. Les confondre ferait durcir la mauvaise limite.
        c = Compteurs(limites(sessions_par_ip=1, rest_par_fenetre=1))
        c.ouvrir_session("1.1.1.1")
        with self.assertRaises(Refus):
            c.ouvrir_session("1.1.1.1")
        c.requete("1.1.1.1")
        with self.assertRaises(Refus):
            c.requete("1.1.1.1")
        self.assertEqual(c.etat()["refus"]["trop_de_sessions"], 1)
        self.assertEqual(c.etat()["refus"]["trop_de_requetes"], 1)

    def test_etat_annonce_les_limites_en_vigueur(self):
        # Le test de bout en bout lit cet etat pour verifier que le service
        # deploye tourne bien avec les valeurs voulues.
        c = Compteurs(limites(sessions_par_ip=7))
        self.assertEqual(c.etat()["limites"]["sessions_par_ip"], 7)


class AdresseAppelant(unittest.TestCase):
    class _Faux:
        def __init__(self, entetes=None, host=None):
            self.headers = entetes or {}
            self.client = type("C", (), {"host": host})() if host else None

    def test_prend_la_premiere_adresse_transmise(self):
        # Cloud Run termine TLS en amont : sans cet en-tete, tout le monde
        # partagerait le compteur du proxy.
        faux = self._Faux({"x-forwarded-for": "41.188.1.2, 10.0.0.1"}, host="10.0.0.1")
        self.assertEqual(adresse(faux), "41.188.1.2")

    def test_retombe_sur_l_adresse_directe(self):
        faux = self._Faux(host="127.0.0.1")
        self.assertEqual(adresse(faux), "127.0.0.1")

    def test_sans_rien_ne_leve_pas(self):
        self.assertEqual(adresse(self._Faux()), "inconnu")


if __name__ == "__main__":
    unittest.main()
