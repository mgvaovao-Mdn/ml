# MGVaovao — Traduction parole-vers-parole en temps réel en dialectes malgaches
## Description du projet

### Vue d'ensemble

MGVaovao - Maison du Numérique (programme de l'association Madagasikara Vaovao) développe, depuis Antananarivo, une infrastructure d'intelligence artificielle ouverte permettant la traduction automatique parole-vers-parole en temps réel à destination de dix-huit dialectes malgaches. Ce projet constitue la première initiative au monde à créer des ressources linguistiques vocales ouvertes pour l'ensemble du continuum dialectal du malgache, une langue parlée par plus de 28 millions de personnes.

---

### Contexte et problème adressé

Madagascar est une île-continent d'une richesse linguistique exceptionnelle. Si le malgache compte parmi les quarante langues africaines les plus parlées, cette réalité dissimule une fragmentation dialectale profonde : dix-huit dialectes régionaux vivants — betsileo, betsimisaraka, sakalava, antandroy, tsimihety, vezo, bara, sihanaka, antakarana, makoa, antaisaka et sept autres — coexistent sur l'ensemble du territoire national. Ces variétés diffèrent phonologiquement et lexicalement au point de constituer de véritables barrières de communication entre communautés.

Le malgache officiel (variété Merina) est la seule forme disposant d'une présence minimale dans les systèmes d'intelligence artificielle existants. Aucun des dix-sept dialectes régionaux n'est représenté dans les grandes bases de données multilingues telles que Common Voice, FLORES-200 ou OPUS. Cette absence prive des millions de locuteurs d'un accès équitable aux services éducatifs, sanitaires et civiques disponibles sous forme numérique. Lorsqu'un agriculteur betsileo cherche des informations sur des semences résistantes à la sécheresse, ou qu'une mère betsimisaraka souhaite comprendre des consignes de santé maternelle, les outils numériques disponibles ne parlent pas leur langue.

À ce jour, moins de dix travaux académiques publiés traitent du traitement automatique du malgache dans sa diversité dialectale.

---

### Solution développée

Le système développé par MGVaovao est un pipeline de traduction parole-vers-parole en cascade, composé de quatre modules complémentaires et optimisés pour les contraintes du contexte africain — latence minimale, coût de calcul maîtrisé, adaptabilité aux données en faible volume.

**Module 1 — Détection d'activité vocale**
Basé sur Silero VAD v5, ce modèle léger de 2 Mo fonctionne en CPU sur des fenêtres de 32 millisecondes. Il filtre les segments de silence avant traitement et réduit les coûts de calcul de 30 à 50 % sur des enregistrements réels.

**Module 2 — Reconnaissance automatique de la parole (ASR)**
Fondé sur Whisper large-v3-turbo quantifié en INT8 via CTranslate2, ce module prend en charge 99 langues d'entrée, dont le français, l'anglais, l'allemand, l'espagnol, l'italien et le portugais. La quantification INT8 offre une vitesse deux fois supérieure au modèle FP16 original pour une empreinte VRAM d'environ 1,7 Go.

**Module 3 — Traduction neuronale**
Basé sur NLLB-200-distilled-600M, affiné par apprentissage par transfert via LoRA (rang 16, PEFT) pour chaque paire de langues source vers le malgache officiel (plt_Latn). L'affinement est conduit sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot, produisant une amélioration mesurée de 2 à 8 points de chrF++ par rapport au modèle de base.

**Module 4 — Synthèse vocale dialectale (TTS)**
Basé sur MMS-TTS-MLG VITS de Meta, affiné par dialecte à partir de 80 à 150 échantillons audio de haute qualité, en une à deux heures sur GPU, via le framework ylacombe/finetune-hf-vits. Chaque checkpoint dialectal est versionné avec ses métadonnées d'évaluation.

L'ensemble du pipeline est exposé via une API FastAPI déployée sur Google Cloud Run GPU (NVIDIA L4, 24 Go), avec une latence de bout en bout inférieure à cinq secondes et une empreinte VRAM totale de 6,2 Go permettant trois à cinq sessions concurrentes par instance.

**État d'avancement actuel :** Un premier proof of concept couvrant quatre dialectes (malgache officiel, betsileo, betsimisaraka, sakalava) est opérationnel depuis avril 2026. Environ 1 000 paires de données ont déjà été constituées depuis le lancement fin 2025.

---

### Données et ressources linguistiques

La composante de création de données est au cœur du projet. Pour chaque dialecte cible, le protocole vise la constitution d'un corpus initial de 150 à 200 heures de parole naturelle et 10 000 paires audio-transcription de haute qualité. Les données sont collectées par des coordinateurs locaux recrutés au sein des communautés elles-mêmes, de préférence des femmes, formés au protocole de collecte et rémunérés équitablement.

Toutes les ressources produites sont publiées intégralement sous licences ouvertes : Apache 2.0 pour les modèles et le code, Creative Commons BY 4.0 pour les données audio et les transcriptions. Elles sont déposées sur HuggingFace et dans Mozilla Common Voice, garantissant leur réutilisation par l'ensemble de la communauté de recherche en NLP africain.

---

### Impact communautaire et ancrage local

MGVaovao - Maison du Numérique est un centre numérique communautaire physique, inauguré en février 2024 à Ambatonakanga, Antananarivo, sur un modèle philanthropique unique : financé exclusivement sur les fonds propres du fondateur, l'accès à l'ensemble des programmes est entièrement gratuit (0 ariary) pour tous les bénéficiaires.

Depuis son inauguration, le centre a accueilli plus de **5 500 bénéficiaires uniques** (48 % de femmes, de 7 à 65 ans) et a accompagné **2 366 personnes formées** à travers ses programmes partenaires :
- **e-jery** — programme d'inclusion numérique pour les enfants vulnérables (1 483 personnes formées)
- **ANKY** — formation en développement personnel et entrepreneuriat (472 personnes formées)
- **Madagascar DataCamp** — formation Excel de base pour les étudiants (411 personnes formées)
- **YAS Madagascar** — programme Ampela Online pour l'entrepreneuriat féminin en ligne
- **Down Syndrome Madagascar** — programme d'inclusion numérique pour 28 enfants porteurs de trisomie 21

Le centre s'appuie sur une communauté de plus de 26 bénévoles actifs et dispose de partenariats établis sur l'ensemble du territoire national.

MGVaovao - Maison du Numérique a été **nominée au prix RSE de l'Année 2026** lors de la 2e édition du CEO Summit Indian Ocean (avril 2026), une reconnaissance externe de l'impact social de l'organisation.

---

### Cas d'usage concrets

**Éducation** — Le système permet aux formateurs de s'adresser aux apprenants dans leur variété linguistique maternelle, améliorant la compréhension et l'engagement dans les programmes d'alphabétisation numérique et d'éducation spécialisée. Une borne interactive déployée dans les locaux de la Maison du Numérique permet à toute personne de s'exprimer en français, anglais ou autre langue prise en charge, et de recevoir immédiatement une réponse audio dans son dialecte.

**Inclusion civique** — Des citoyens non locuteurs du malgache officiel peuvent accéder à des informations sur les services publics, les droits civiques et les procédures administratives dans leur dialecte. Ce besoin est particulièrement aigu dans les zones rurales où les barrières linguistiques constituent le premier obstacle à l'accès à l'information.

**API publique** — Une API documentée et accessible permet à des partenaires institutionnels — services de santé communautaire, associations d'alphabétisation, ONG, organisations d'appui social — d'intégrer la capacité de communication dialectale dans leurs propres outils.

---

### Ouverture et reproductibilité

L'intégralité du code source, des scripts d'affinement et de la documentation technique est publiée sous licence Apache 2.0 sur :
- **github.com/mgvaovao-Mdn/ml** — pipeline ML, modèles, scripts d'affinement
- **github.com/mgvaovao-Mdn/backend_ia** — API, documentation technique

Les corpus audio dialectaux seront déposés sur HuggingFace et dans Mozilla Common Voice sous Creative Commons BY 4.0, constituant les premières ressources linguistiques vocales ouvertes pour le malgache dialectal.

---

### Organisation

**Nom légal :** Madagasikara Vaovao  
**Nom commercial :** Maison du Numérique / MGVaovao  
**Type :** Association à but non lucratif  
**Siège :** Antananarivo, Madagascar  
**Site web :** https://mgvaovao.com  
**Email :** contact@mgvaovao.com
