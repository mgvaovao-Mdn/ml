# La démonstration publique : quotas et vérification

Service Cloud Run `mgvaovao-inference`, projet `mgvaovao-ia`, région
`us-central1`, GPU NVIDIA L4, `min-instances=0`.

## Pourquoi des quotas

Le GPU est facturé à la seconde d'instance, pas à la requête. Cloud Run compte
une session WebSocket comme **une** requête et la laisse ouverte jusqu'au
`--timeout`, réglé à une heure. Avec `--concurrency=4` et `--max-instances=2`,
huit connexions maintenues ouvertes suffisent à faire tourner deux GPU en
continu — et la facture court tant que personne ne regarde.

Les limites vivent dans `api/quotas.py` et répondent à trois abus distincts :

| Abus | Limite | Variable |
|---|---|---|
| Ouverture en rafale, pour épuiser les places de concurrence | 10 ouvertures / 60 s par adresse | `QUOTA_RAFALE`, `QUOTA_RAFALE_FENETRE_S` |
| Sessions simultanées d'une même adresse | 2 | `QUOTA_SESSIONS_PAR_IP` |
| Session muette qui occupe une place sans rien produire | coupée après 120 s sans audio | `QUOTA_SILENCE_S` |
| Session interminable | coupée après 600 s | `QUOTA_DUREE_SESSION_S` |
| Usage massif, par personne | 1800 s de session par jour | `QUOTA_BUDGET_IP_S` |
| Usage massif, au total | 28800 s de session par jour | `QUOTA_BUDGET_GLOBAL_S` |
| Appels REST à `/translate` | 30 / 60 s par adresse | `QUOTA_REST`, `QUOTA_REST_FENETRE_S` |

Les routes REST passent par le même compteur : elles font tourner le même
pipeline GPU, et les laisser libres reviendrait à verrouiller une porte en
laissant l'autre ouverte.

### Ce que les quotas ne font pas

**Les compteurs vivent en mémoire, dans le processus.** Avec deux instances,
chacune tient les siens : le budget global effectif peut donc atteindre le
double de `QUOTA_BUDGET_GLOBAL_S`. C'est assumé — un compteur partagé
demanderait un Redis à maintenir et à payer pour protéger une démonstration.
L'ordre de grandeur suffit à empêcher la facture de déraper, ce qui est le but.

**L'adresse vient de `X-Forwarded-For`**, donc falsifiable par un en-tête forcé.
La falsification contourne les limites par adresse, mais pas le budget global,
qui est le garde-fou qui compte pour la facture.

**`QUOTA_DUREE_SESSION_S` ne peut pas dépasser le `--timeout` de Cloud Run.**
Au-delà, c'est Cloud Run qui coupe, sans message pour la personne.

## Élargir les limites le temps d'une démonstration

Les valeurs sont des substitutions de `cloudbuild-inference.yaml`, et non des
constantes du code : une démonstration devant des partenaires s'élargit sans
reconstruire l'image.

```bash
gcloud run services update mgvaovao-inference \
  --project=mgvaovao-ia --region=us-central1 \
  --update-env-vars=QUOTA_SESSIONS_PAR_IP=10,QUOTA_BUDGET_IP_S=7200
```

Penser à remettre les valeurs ensuite, ou à les reporter dans
`cloudbuild-inference.yaml` — le prochain déploiement écrase toute la
configuration d'environnement.

## Vérifier que le service répond

Un build vert n'a jamais garanti qu'une phrase prononcée revienne traduite.

```bash
# Santé, modèles chargés, dialectes, quotas, puis un aller-retour audio complet
python scripts/verifier_demo.py --url https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app

# Sans solliciter le GPU
python scripts/verifier_demo.py --url https://... --sans-audio

# Éprouve en plus le refus au-delà de la limite de sessions
python scripts/verifier_demo.py --url https://... --quotas
```

Le script sort avec un code non nul dès qu'une vérification échoue : il sert de
sonde après déploiement comme dans une supervision périodique.

Au premier appel après une période d'inactivité, `min-instances=0` impose un
démarrage à froid d'environ quarante-cinq secondes, puis le chargement des
modèles. Le script le signale plutôt que d'échouer sans explication ; relancer
une minute après suffit.

`GET /quotas` donne l'usage courant et les limites en vigueur, ce qui permet de
vérifier de l'extérieur que le service tourne bien avec les valeurs voulues, et
de voir venir l'épuisement du budget avant qu'il ne ferme au nez d'un
partenaire.

## Tests des compteurs

```bash
python -m unittest discover -s api/tests -t .
```

Ils vérifient autant que chaque limite refuse l'abus qu'elle vise que le fait
qu'aucune ne refuse un usage normal : un garde-fou qui ferme la porte à un
partenaire en démonstration sera désactivé dans l'heure, et ne protégera plus
rien.
