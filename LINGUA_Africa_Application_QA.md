# CANDIDATURE LINGUA AFRICA 2026
**Organisation :** Madagasikara Vaovao — Maison du Numérique  
**Ville :** Antananarivo, Madagascar  
**Date limite :** 15 juin 2026  
**Catégories :** 1 — Création de données / 2 — Modèles et outils / 3 — Applications sectorielles

---

## Question 1(a) — Catégorie(s) de candidature

Catégories cochées : **Catégorie 1 — Création de données**, **Catégorie 2 — Développement de modèles et d'outils** et **Catégorie 3 — Applications sectorielles**

Ce projet porté par MGVaovao - Maison du Numérique ne relève pas d'une catégorie principale unique car il constitue un pipeline complet et indissociable dans lequel les trois dimensions sont de poids égal. La Catégorie 1 correspond à la constitution systématique des premiers corpus vocaux ouverts pour 18 dialectes malgaches, sans lesquels aucun affinement n'est possible. La Catégorie 2 correspond à l'affinement des modèles fondationnaux NLLB-200 et MMS-TTS-MLG pour chacun de ces dialectes, ce qui constitue le cœur technique du projet. La Catégorie 3 correspond au déploiement de l'ensemble dans une application réelle au service de communautés, ce qui donne un sens et une légitimité à toute la démarche. Ces trois dimensions se conditionnent mutuellement : créer des données sans entraîner de modèles ne produit aucun impact, entraîner des modèles sans les intégrer dans une application ne rejoint pas les bénéficiaires, et déployer une application sans données ni modèles de qualité n'est pas crédible. C'est précisément la force de cette candidature que de couvrir l'intégralité du pipeline, de la collecte communautaire jusqu'à l'usage en production.

---

## Question 1(b) — Titre du projet et résumé (300 mots max)

**Titre du projet :**
Traduction multilingue parole-vers-parole en temps réel vers 18 dialectes malgaches — une infrastructure d'IA ouverte au service de l'inclusion linguistique

**Résumé :**

Madagascar est une île-continent où 28 millions d'habitants parlent un malgache profondément pluriel : 18 dialectes régionaux vivants, porteurs d'identités et de cultures distinctes, qui n'ont jusqu'ici bénéficié d'aucune représentation dans les systèmes d'intelligence artificielle modernes. Ce vide prive des millions de locuteurs d'un accès équitable à l'éducation numérique, aux services de santé et aux ressources civiques.

MGVaovao - Maison du Numérique est l'organisation qui porte ce projet. Elle développe, depuis Antananarivo, un système de traduction parole-vers-parole en temps réel conçu pour convertir automatiquement la parole en six langues internationales — le français, l'anglais, l'allemand, l'espagnol, l'italien et le portugais — en parole malgache naturelle dans le dialecte choisi par l'utilisateur.

Un premier proof of concept couvrant quatre dialectes est fonctionnel depuis avril 2026, avec une latence inférieure à cinq secondes, sur Cloud Run GPU. Ce prototype démontre la faisabilité technique de l'approche mais constitue un premier résultat en cours d'amélioration, non un système finalisé ni une solution pleinement déployée en production. Depuis le lancement du projet en fin 2025, l'équipe a déjà constitué environ 1 000 paires de données, dont des paires texte-texte pour la traduction neuronale et des paires texte-audio pour la synthèse vocale, ce qui confirme la faisabilité opérationnelle de la collecte.

Le soutien de LINGUA Africa permettra d'étendre la couverture aux 14 dialectes restants, de constituer les premières ressources linguistiques vocales ouvertes pour l'ensemble du malgache dialectal, et de déployer ce service dans les programmes d'éducation, de santé et d'inclusion civique de MGVaovao - Maison du Numérique, un centre communautaire qui accueille plus de 550 personnes par mois et a formé plus de 5 000 individus depuis son inauguration en février 2024.

*(~285 mots)*

---

## Question 2 — Justification de la proposition et objectifs (750 mots max)

Le malgache compte parmi les quarante langues africaines les plus parlées au monde. Mais derrière cette reconnaissance globale se dissimule une réalité bien plus complexe. Madagascar est une île-continent où coexistent dix-huit dialectes régionaux, dont certains diffèrent phonologiquement et lexicalement au point de constituer de véritables barrières de communication entre communautés. Le malgache officiel, à savoir la variété Merina, est la langue administrative et médiatique, mais des millions de Malgaches dans les régions betsileo, betsimisaraka, sakalava, antandroy et bien d'autres n'accèdent aux services numériques, éducatifs et sanitaires qu'à travers une langue qui n'est pas la leur, ou n'y accèdent tout simplement pas.

Ce déséquilibre est amplifié par une fracture numérique persistante. Lorsqu'un agriculteur betsileo cherche des informations sur des semences résistantes à la sécheresse, lorsqu'une mère betsimisaraka souhaite comprendre les consignes de santé maternelle, ou lorsqu'un citoyen sakalava veut accéder à un service administratif en ligne, les outils numériques disponibles fonctionnent soit en malgache officiel, soit dans une langue coloniale. Aucun système d'intelligence artificielle existant ne parle leur dialecte. C'est précisément ce vide documenté et mesurable que MGVaovao s'est donné pour mission de combler.

Le projet poursuit trois objectifs interconnectés. Le premier est de constituer les premières ressources linguistiques ouvertes pour dix-huit dialectes malgaches, notamment des corpus audio annotés, des poids de modèles affinés et des benchmarks d'évaluation reproductibles, publiés intégralement sous licences Apache 2.0 et Creative Commons BY 4.0. Le deuxième est de déployer un outil concret et immédiatement utilisable, c'est-à-dire un système de traduction parole-vers-parole accessible depuis la Maison du Numérique et via une API publique, permettant à des services d'éducation, de santé et d'administration de s'adresser en malgache dialectal à leurs bénéficiaires. Le troisième est d'ancrer ce projet dans une dynamique communautaire vérifiable et durable, où les locuteurs natifs participent à la collecte, à la validation et à l'évaluation, et sont les premiers bénéficiaires du déploiement.

La pertinence de ce projet pour LINGUA Africa est directe et documentée. À ce jour, moins de dix travaux académiques publiés traitent du traitement automatique du langage malgache dans sa diversité dialectale. Les grandes bases de données multilingues telles que Common Voice, FLORES-200 et OPUS contiennent des données pour le malgache officiel, mais aucune pour ses variétés dialectales. MGVaovao - Maison du Numérique crée ces ressources pour la première fois, avec rigueur, dans un cadre communautaire et sous licences entièrement ouvertes.

Les bénéficiaires directs sont les locuteurs de dialectes malgaches sous-représentés, soit une population estimée à plus de quinze millions de personnes, qui pourront pour la première fois interagir avec des systèmes numériques dans leur propre variété linguistique. Les bénéficiaires indirects incluent les prestataires de services éducatifs, sanitaires et civiques qui souhaitent atteindre ces communautés mais se heurtent à des barrières linguistiques. L'ambition inclusive de la Maison du Numérique va encore plus loin : parmi ses programmes actifs figure l'inclusion numérique des enfants atteints de trisomie 21, une initiative qui illustre concrètement que la mission de l'organisation embrasse toutes les formes d'exclusion, y compris le handicap. Au-delà de Madagascar, les ressources produites enrichiront l'écosystème global des langues africaines à faibles ressources.

L'équipe portant ce projet est ancrée localement et compétente techniquement à un niveau international. Fenitra Ravelomanantsoa, fondateur de Madagasikara Vaovao, est Directeur des affaires juridiques et réglementaires Cloud (Head of Cloud Regulatory) au sein de Google à Zurich. À ce poste de direction, il supervise la conformité réglementaire des infrastructures cloud à l'échelle internationale. Juriste spécialisé en gouvernance des technologies numériques et protection des données, il a fondé MGVaovao - Maison du Numérique pour que son pays bénéficie concrètement de la révolution numérique. Norolala Randrianarison, connue sous le nom de Mme Noro, assure en tant que directrice locale la direction opérationnelle quotidienne et entretient la relation de proximité avec les communautés. Guillaume Rakotonjanahary Tsantaniaina et Karine Maholisoa Rajaofera dirigent chacun un volet complémentaire du projet. Guillaume est Chef de projet technique en charge du développement ML, de l'architecture du pipeline et du déploiement cloud. Titulaire d'un Master en Big Data et IA obtenu avec mention Très Bien (17,2/20 à l'ESTIA France), il a développé au cours de ses cinq années d'expérience une gamme étendue de systèmes IA en production : pipelines Speech AI complets (ASR, traduction neuronale, synthèse vocale), systèmes multi-agents LLM avec LangGraph et Google ADK, architectures RAG hybrides (vectoriel, graphe, multimodal), modèles de vision par ordinateur (YOLO V8, CLIP, SAM), plateformes de santé numérique, et infrastructures MLOps sur Vertex AI. Sa participation à IndabaX Madagascar 2023 (3e place, classification NLP médicale à 94 % de précision) et au DataTour 2025 (compétition pan-africaine, modèles de recommandation et de scoring crédit) témoignent de son engagement dans l'écosystème IA africain. Karine Maholisoa Rajaofera, Chef de projet Data, Opérations et Fonctionnel, apporte dix ans d'expérience dans les opérations de données, l'annotation et la coordination de collectes à grande échelle. Elle assure la traduction des besoins fonctionnels en spécifications opérationnelles et pilote l'interface entre les équipes terrain et le volet technique. Cette complémentarité entre expertise ML de haut niveau et maîtrise des opérations de données est ce qui rend ce projet non seulement techniquement solide, mais également ancré dans une réalité communautaire opérationnelle.

*(~720 mots)*

---

## Question 3 — Langues couvertes et justification (350 mots max)

Le projet cible le malgache dans l'intégralité de ses dix-huit dialectes régionaux. Le malgache compte plus de 28 millions de locuteurs, ce qui le place parmi les quarante langues africaines les plus parlées. Mais derrière cette unité apparente se cache une réalité dialectale d'une richesse et d'une complexité remarquables, presque entièrement absente des systèmes d'IA existants.

Le malgache officiel, désigné plt_Latn dans les systèmes NLP internationaux et correspondant à la variété Merina, est la seule forme qui dispose d'une présence, encore minimale, dans les corpus multilingues tels que FLORES-200 et Common Voice. Les dix-sept dialectes régionaux, parmi lesquels le betsileo, le betsimisaraka, le sakalava, l'antandroy, le tsimihety, le vezo, le bara, le sihanaka, l'antakarana, le makoa, l'antaisaka et d'autres encore, n'ont aucune représentation dans l'écosystème NLP mondial.

Trois raisons convergentes justifient ce choix de cibler spécifiquement Madagascar et ses dialectes.

Il s'agit d'abord d'un vide documenté et mesurable : aucun corpus vocal dialectal validé, aucun modèle NLP de production et aucun outil de synthèse vocale dialectale n'existe aujourd'hui sous licence ouverte pour ces variétés. La valeur de création pour la communauté NLP mondiale est donc maximale et immédiate.

Ce choix est ensuite ancré dans une légitimité communautaire irréfutable : l'équipe est malgache, basée à Antananarivo, locutrice native des langues ciblées, et la Maison du Numérique opère physiquement au sein de ces communautés depuis février 2024, avec des partenariats établis sur l'ensemble du territoire national.

L'impact potentiel est enfin à la fois immédiat et durable. Un système qui parle betsileo à une famille de la région Haute-Matsiatra ou sakalava à un pêcheur de Mahajanga n'est pas une ambition lointaine. C'est une réalité que notre infrastructure technique rend possible dès aujourd'hui pour quatre dialectes, et que le financement LINGUA Africa permettra d'étendre aux quatorze variétés restantes selon un plan structuré sur dix-huit mois.

*(~330 mots)*

---

## Question 4 — Domaines et sous-domaines (300 mots max)

Ce projet de traduction dialectale porté par MGVaovao - Maison du Numérique se déploie à l'intersection de trois domaines prioritaires définis par LINGUA Africa.

Le premier est l'éducation. La Maison du Numérique accueille chaque mois plus de 550 jeunes et adultes dans ses programmes de formation numérique, dont E-JERY et HOLI DEV, soutenus par Telma Madagascar. Ces programmes touchent des élèves d'écoles primaires publiques des quartiers défavorisés d'Antananarivo. De façon encore plus remarquable, la Maison du Numérique a développé un programme d'inclusion numérique spécifiquement destiné aux enfants atteints de trisomie 21, une initiative portée par ses bénévoles qui témoigne d'une conception radicalement inclusive du numérique. L'intégration d'un système de traduction dialectale dans ces programmes permettra de s'adresser aux apprenants dans leur variété linguistique maternelle, améliorant ainsi la compréhension et l'engagement. Les sous-domaines ciblés comprennent l'alphabétisation numérique, l'éducation de base et l'éducation spécialisée.

Le deuxième est la santé publique. En partenariat avec des acteurs de santé communautaire, le système permettra de diffuser des messages de prévention couvrant la santé maternelle et infantile, la vaccination et la gestion des épidémies dans les dialectes des régions concernées.

Le troisième est l'inclusion civique et numérique. Le système permettra à des citoyens non locuteurs du malgache officiel d'accéder à des informations sur les services publics, les droits civiques et les ressources gouvernementales dans leur dialecte. Ce besoin est particulièrement aigu dans les zones rurales, où les barrières linguistiques constituent le premier obstacle à l'accès à l'information.

*(~275 mots)*

---

## Question 5 — Données collectées (500 mots max — Catégorie 1)

Ce projet couvre la Catégorie 1 par sa composante substantielle de création de données, sans laquelle l'extension aux quatorze dialectes restants serait impossible.

Le type de données produit correspond à des enregistrements audio de parole naturelle et lue, en format WAV 16 kHz mono, réalisés par des locuteurs natifs de chaque dialecte cible, associés à des transcriptions orthographiques validées par un second locuteur natif. Les textes utilisés pour les lectures guidées sont adaptés aux domaines prioritaires du projet, à savoir l'éducation, la santé communautaire et les services civiques, ce qui garantit que les données sont à la fois linguistiquement représentatives et directement utiles pour les cas d'usage visés. Depuis le lancement du projet en février 2026, environ 1 000 paires de données ont déjà été constituées pour les dialectes initiaux, ce qui constitue une preuve concrète que le protocole de collecte fonctionne et que l'équipe dispose de l'expérience nécessaire pour le déployer à grande échelle.

En termes de volume, le projet vise pour chaque dialecte un corpus initial de 150 à 200 heures de parole naturelle et 10 000 paires audio-transcription de haute qualité. Les quatorze dialectes restants représentent un corpus cible d'environ 2 100 à 2 800 heures d'enregistrement et 140 000 paires audio-transcription.

La collecte sera organisée en partenariat avec des coordinateurs locaux dans chaque région linguistique. Ces coordinateurs sont recrutés au sein des communautés locutrices elles-mêmes, de préférence des femmes, formés au protocole de collecte et rémunérés équitablement. Les régions couvertes incluent Fianarantsoa pour le betsileo, Toamasina pour le betsimisaraka, Mahajanga pour le sakalava, Ambovombe pour l'antandroy, Mandritsara pour le tsimihety, et ainsi de suite pour chaque variété ciblée.

Sur le plan de l'ouverture, toutes les données produites seront publiées sous licence Creative Commons BY 4.0 sur HuggingFace et dans Common Voice, permettant leur réutilisation par l'ensemble de la communauté de recherche en NLP africain. Les transcriptions seront également disponibles en format TSV compatible avec les outils standards de la communauté Masakhane.

Le protocole respecte les standards éthiques internationaux : consentement éclairé écrit en malgache officiel et dans la variété dialectale locale, droit de retrait à tout moment avant publication, et interdiction d'enregistrement des mineurs sans consentement parental écrit.

*(~490 mots)*

---

## Question 6 — Modèles et outils développés (500 mots max — Catégorie 2)

Le pipeline de traduction parole-vers-parole développé dans ce projet s'articule en quatre étapes. Un proof of concept est fonctionnel pour quatre dialectes à ce jour et l'architecture est conçue pour être étendue à l'ensemble des dix-huit variétés dialectales du malgache.

La première composante est un module de détection d'activité vocale basé sur Silero VAD v5. Ce modèle de 2 Mo, fonctionnant exclusivement en CPU, traite le signal audio en fenêtres de 32 millisecondes et filtre les segments de silence avant transmission au module de reconnaissance vocale, réduisant ainsi les coûts de calcul de 30 à 50 % sur des enregistrements du monde réel.

La deuxième composante est le module de reconnaissance automatique de la parole, fondé sur Whisper large-v3-turbo quantifié en INT8 via CTranslate2. Ce modèle prend en charge 99 langues d'entrée, dont le français, l'anglais, l'allemand, l'espagnol, l'italien et le portugais. La quantification INT8 permet d'atteindre une vitesse deux fois supérieure au modèle FP16 original tout en maintenant une précision comparable, pour une empreinte VRAM d'environ 1,7 Go.

La troisième composante est le module de traduction neuronale, basé sur NLLB-200-distilled-600M, affiné par apprentissage par transfert via LoRA (rang 16, PEFT) pour chaque paire source vers plt_Latn. L'affinement, conduit sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot à 0,28 USD de l'heure, produit une amélioration mesurée de 2 à 8 points de chrF++ par rapport au modèle de base pour le malgache. L'empreinte VRAM est d'environ 0,7 Go en INT8. Les poids LoRA affinés sont publiés sous licence Apache 2.0.

La quatrième composante est le module de synthèse vocale dialectale, basé sur MMS-TTS-MLG VITS de Meta. Ce modèle est affiné par dialecte à partir de 80 à 150 échantillons audio de haute qualité, en une à deux heures sur GPU L4, via le framework ylacombe/finetune-hf-vits. Chaque checkpoint de dialecte est versionné dans Vertex AI Model Registry avec ses métadonnées d'évaluation, notamment les scores chrF++ et UTMOS. Les checkpoints sont publiés sous licence Apache 2.0.

L'ensemble du pipeline est exposé via une API FastAPI déployée sur Google Cloud Run GPU avec un GPU NVIDIA L4 de 24 Go, avec une latence de bout en bout inférieure à cinq secondes et une empreinte VRAM totale de 6,2 Go permettant trois à cinq sessions concurrentes par instance. Le code source complet, les scripts d'affinement et la documentation technique sont publiés sur GitHub aux adresses github.com/mgvaovao/ml et github.com/mgvaovao/backend_ia, sous licence Apache 2.0.

Ces composants correspondent aux modèles les plus performants disponibles au moment du développement du prototype. L'architecture est modulaire : si des modèles plus puissants ou mieux adaptés aux langues à très faibles ressources venaient à émerger au cours du projet, leur intégration dans le pipeline serait envisagée et évaluée selon les mêmes critères de qualité.

*(~510 mots)*

---

## Question 7 — Cas d'usage développé (500 mots max — Catégorie 3)

Le cas d'usage principal du projet est un service de traduction et d'information multilingue en dialecte malgache, accessible depuis MGVaovao - Maison du Numérique et via une API publique, destiné à des populations qui ne maîtrisent pas le malgache officiel ou les langues internationales mais qui ont besoin d'accéder à des services éducatifs, sanitaires et civiques.

Concrètement, le système se présente sous deux interfaces complémentaires. La première est une borne interactive déployée dans les locaux de la Maison du Numérique d'Ambatonakanga : une personne s'exprime en français, en anglais ou dans une autre langue prise en charge, et reçoit immédiatement une réponse audio dans son dialecte malgache. Cette borne est utilisée dans les sessions d'accueil des nouveaux apprenants, dans les ateliers de formation et dans les permanences d'information communautaire. La seconde interface est une API publique et documentée, accessible aux partenaires institutionnels, notamment les services de santé communautaire, les associations d'alphabétisation, les ONG et les structures d'aide sociale souhaitant intégrer la capacité de communication dialectale dans leurs propres outils.

L'impact attendu s'articule autour de quatre axes. En matière d'éducation, le système permet aux formateurs de la Maison du Numérique de s'adresser aux apprenants dans leur variété maternelle, en particulier pour les élèves issus de familles ayant migré des régions betsileo, betsimisaraka ou sakalava. Cela améliore la compréhension et renforce la confiance dans l'appropriation du numérique. En matière de santé, des partenaires de santé communautaire peuvent diffuser des messages de prévention dans les dialectes des régions ciblées, sans nécessiter de traducteur humain. En matière d'inclusion civique, des informations sur les droits des citoyens et les procédures administratives peuvent être rendues accessibles en dialecte. Sur le plan de la souveraineté numérique enfin, Madagascar disposera pour la première fois d'une infrastructure linguistique ouverte construite par des Malgaches pour des Malgaches, réutilisable par tout acteur souhaitant développer des services en dialecte malgache.

La Maison du Numérique constitue l'environnement de pilotage idéal : plus de 550 utilisateurs mensuels, 5 000 personnes formées depuis l'inauguration de février 2024, un réseau de partenaires établis que sont Telma, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et ANKY, ainsi qu'une communauté de plus de 26 bénévoles actifs, dont plusieurs spécialisés dans l'inclusion des publics les plus vulnérables. Ce tissu humain garantit que le système MGVaovao sera évalué par des utilisateurs réels, dans leur contexte réel, avec des besoins réels, et que le pilote documenté posera les bases d'un déploiement à l'échelle nationale.

*(~470 mots)*

---

## Question 8 — Tâches et évaluation (500 mots max)

Le projet est structuré en cinq ensembles de tâches, chacun associé à des indicateurs d'évaluation précis et mesurables.

La première tâche est la constitution des corpus vocaux dialectaux. Pour chaque dialecte non encore couvert, des sessions d'enregistrement sont organisées dans les régions d'origine des locuteurs natifs. L'évaluation porte sur le volume de données validées en heures et en paires audio-transcription, la diversité des locuteurs avec une parité de genre imposée à 50 % minimum et une diversité d'âge en trois tranches couvrant respectivement les 18 à 35 ans, les 35 à 55 ans et les 55 ans et plus, ainsi que la qualité technique des fichiers audio mesurée par le rapport signal-sur-bruit et le taux d'acceptation.

La deuxième tâche est l'affinement des modèles de traduction NLLB LoRA et de synthèse vocale MMS-TTS VITS pour chaque dialecte. L'évaluation repose sur des métriques automatiques établies, à savoir chrF++ pour la qualité de traduction avec un objectif de score supérieur ou égal à 45 et d'amélioration de 3 points minimum sur le baseline malgache officiel, et UTMOS pour la naturalité de la synthèse vocale avec un objectif de score supérieur ou égal à 3,5 sur 5. Des évaluations humaines complémentaires sont réalisées par des panels de locuteurs natifs de chaque dialecte pour valider l'intelligibilité et la naturalité des sorties.

La troisième tâche est le déploiement et l'intégration dans les services de la Maison du Numérique. L'évaluation porte sur le taux de disponibilité du système avec un objectif de 99 % sur les heures d'ouverture, la latence de bout en bout avec un objectif inférieur à cinq secondes, et la satisfaction des utilisateurs mesurée par questionnaire mensuel structuré.

La quatrième tâche est la conduite de sessions d'évaluation communautaire trimestrielles avec des locuteurs natifs de chaque dialecte. Ces sessions collectent des retours qualitatifs sur la qualité des traductions et de la synthèse et alimentent les cycles de réentraînement des modèles. Aucun dialecte n'est déployé en production avant d'avoir atteint les seuils de qualité définis.

La cinquième tâche est la publication ouverte de toutes les ressources produites. L'évaluation se mesure par le nombre de ressources publiées sur HuggingFace et GitHub, le nombre de téléchargements dans les six premiers mois et la réutilisation documentée par d'autres équipes de la communauté NLP africaine. Un tableau de bord de suivi mensuel est maintenu et partagé avec les partenaires de LINGUA Africa, comprenant l'avancement des collectes par dialecte, les scores d'évaluation automatique et humaine, et les indicateurs d'utilisation du système déployé.

*(~485 mots)*

---

## Question 9 — Méthodologie (1000 mots max)

La méthodologie de ce projet de traduction speech-to-speech en dialectes malgaches s'articule autour de quatre piliers interdépendants : une approche technique rigoureuse fondée sur l'état de l'art en speech AI, une démarche de collecte de données communautaire et éthiquement encadrée, un cycle d'évaluation continu ancré dans les retours des locuteurs natifs, et une couche d'application orientée utilisateur qui rend le service accessible en dehors de tout contexte technique.

**Premier pilier : l'architecture technique**

Le pipeline de traduction parole-vers-parole repose sur quatre modules en cascade, chacun optimisé pour les contraintes du contexte africain, à savoir la latence minimale, le coût de calcul maîtrisé et l'adaptabilité à des données en faible volume.

La détection d'activité vocale est assurée par Silero VAD v5, un modèle de 2 Mo fonctionnant en CPU sur des fenêtres de 32 ms. Ce composant filtre les segments de silence avant le passage à la reconnaissance vocale, réduisant ainsi les coûts de calcul de 30 à 50 % sur des enregistrements du monde réel, ce qui représente un gain particulièrement important dans le contexte africain où les environnements sonores sont souvent bruyants.

La reconnaissance automatique de la parole est assurée par Whisper large-v3-turbo quantifié en INT8 via CTranslate2. Ce choix résulte d'une évaluation comparative menée par l'équipe : ce modèle offre le meilleur rapport précision/vitesse/empreinte pour les six langues source visées, avec 1,7 Go de VRAM et une vitesse deux fois supérieure à la version FP16. Il prend en charge 99 langues sans affinement préalable.

La traduction neuronale est assurée par NLLB-200-distilled-600M, affiné via PEFT/LoRA (rang 16) pour chaque paire source vers plt_Latn, avec des adaptateurs supplémentaires permettant d'adapter la sortie aux particularités lexicales de chaque variété régionale. L'affinement est conduit sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot à environ 0,28 USD de l'heure, avec des runs de 6 à 12 heures par langue source. L'amélioration de chrF++ mesurée est de 2 à 8 points selon la paire de langues. L'empreinte VRAM est d'environ 0,7 Go en INT8.

La synthèse vocale dialectale est assurée par MMS-TTS-MLG VITS de Meta, affiné par dialecte via le framework ylacombe/finetune-hf-vits. Le fine-tuning de chaque dialecte nécessite 80 à 150 échantillons audio de haute qualité et une à deux heures de calcul sur GPU L4 Spot. L'ensemble du cycle de vie des modèles est orchestré via Vertex AI Pipelines selon une architecture Kubeflow DAG, avec déclenchement automatique sur nouvelles données via Pub/Sub sur GCS. Les checkpoints sont versionnés dans Vertex AI Model Registry avec les métadonnées d'évaluation associées.

L'empreinte VRAM totale du pipeline en production est de 6,2 Go sur un GPU L4 de 24 Go, permettant trois à cinq sessions WebRTC concurrentes par instance. Le coût opérationnel mensuel en régime de croisière est estimé à environ 42 USD, garantissant ainsi la pérennité et l'autonomie financière du service bien au-delà de la durée du projet.

**Deuxième pilier : la collecte de données communautaire**

La collecte de données vocales pour les quatorze dialectes non encore couverts suit un protocole structuré en quatre étapes.

L'identification et le recrutement des coordinateurs locaux constituent la première étape. Pour chaque région linguistique cible, un coordinateur est identifié au sein des communautés elles-mêmes, de préférence une femme, puis formé au protocole de collecte par l'équipe technique de la Maison du Numérique. Une rémunération équitable est versée pour chaque heure de session coordonnée.

La préparation des textes de collecte constitue la deuxième étape. Les textes sont adaptés aux domaines prioritaires, à savoir l'éducation, la santé et le civique, et validés par des locuteurs natifs pour leur représentativité culturelle et dialectale. Les listes de mots et phrases couvrent un large spectre phonologique pour maximiser l'utilité des données pour l'affinement de la synthèse vocale.

Les sessions d'enregistrement constituent la troisième étape. Elles se déroulent dans des espaces calmes tels que des salles communautaires, des centres de santé ou des antennes de la Maison du Numérique en régions. Chaque locuteur signe un formulaire de consentement éclairé disponible en malgache officiel et dans la variété dialectale de la région, expliquant l'usage des enregistrements, la licence CC BY 4.0 sous laquelle ils seront publiés, et le droit de retrait à tout moment avant la publication.

Le traitement et la validation constituent la quatrième étape. Les enregistrements sont traités automatiquement, notamment pour la normalisation du volume, la détection du silence et le découpage en segments, puis validés manuellement par un second locuteur natif qui confirme la transcription et l'authenticité dialectale. Ce double regard garantit la qualité et la cohérence du corpus.

**Troisième pilier : l'évaluation continue et l'amélioration itérative**

L'évaluation est conduite à deux niveaux complémentaires. L'évaluation automatique utilise chrF++ pour la traduction, UTMOS pour la synthèse vocale et WER pour la reconnaissance vocale, sur des jeux de test réservés dès la collecte et jamais utilisés pour l'entraînement. L'évaluation humaine est conduite trimestriellement avec des panels de locuteurs natifs recrutés via les réseaux de la Maison du Numérique et de ses partenaires régionaux.

Les résultats d'évaluation alimentent directement les décisions de réentraînement et de déploiement. Le déploiement en production utilise une stratégie blue/green sur Cloud Run GPU, avec rollback automatique en cas de régression de performance. Aucun dialecte n'est déployé en production avant d'avoir atteint les seuils de qualité définis, garantissant ainsi que les utilisateurs ne reçoivent que des traductions d'une qualité suffisante pour être utiles et dignes de confiance.

**Quatrième pilier : la couche applicative orientée utilisateur**

Le pipeline de modèles, aussi performant soit-il, ne produit d'impact que s'il est accessible à des utilisateurs non techniques. La couche applicative est le quatrième pilier de la méthodologie et constitue le point de contact direct avec les bénéficiaires.

L'API FastAPI déployée sur Cloud Run GPU expose les modèles via des endpoints REST documentés, permettant à tout partenaire institutionnel d'intégrer le service de traduction dialectale dans ses propres outils. L'API gère l'authentification, la sélection du dialecte cible, la validation des entrées audio et la remontée d'erreurs structurées. Le code source complet est publié sur github.com/mgvaovao/backend_ia sous licence Apache 2.0.

Par-dessus cette API, une interface temps réel — basée sur WebRTC pour les accès navigateur ou WebSocket pour les intégrations partenaires — permet des sessions de traduction interactive à moins de cinq secondes de latence de bout en bout. La détection automatique de fin de phrase repose sur Silero VAD, déjà intégré au cœur du pipeline, qui segmente le flux audio entrant en fenêtres de 32 ms et déclenche chaque cycle de traduction dès la fin d'une phrase, sans intervention de l'utilisateur. L'utilisateur choisit son dialecte cible depuis un menu déroulant et s'exprime dans l'une des six langues source prises en charge. Le système transcrit, traduit et synthétise vocalement la réponse en dialecte malgache en une seule requête unifiée. Cette interface est conçue pour être déployée dans les locaux de la Maison du Numérique et répliquée chez les partenaires régionaux sans coût de licence.

Le développement applicatif comprend également des outils de monitoring de la qualité en production, un tableau de bord d'utilisation permettant à l'équipe de suivre les dialectes les plus sollicités et d'identifier les erreurs fréquentes, et un mécanisme de feedback utilisateur intégré qui alimente directement les cycles de réentraînement. Cette boucle entre l'usage réel et l'amélioration des modèles est la garantie que le système progressera en conditions opérationnelles et restera utile sur la durée.

*(~1150 mots — légèrement au-dessus de la limite indicative, peut être resserré)*

---

## Question 10 — Livrables et apprentissages attendus (500 mots max)

Les livrables du projet s'articulent en trois catégories : les ressources linguistiques ouvertes, les modèles et outils open-source, et l'impact communautaire documenté.

En matière de ressources linguistiques, le projet produira et publiera dix-huit corpus audio dialectaux couvrant l'ensemble des variétés régionales du malgache, soit un total estimé de 2 500 à 3 000 heures d'enregistrement vocal transcrit et validé. Ces corpus seront publiés sur HuggingFace et déposés dans Common Voice sous licence Creative Commons BY 4.0. Ils constitueront les premières ressources vocales ouvertes pour les dialectes malgaches, immédiatement réutilisables par la communauté NLP africaine et mondiale.

En matière de modèles et d'outils, le projet publiera sur github.com/mgvaovao/ml et HuggingFace les adaptateurs LoRA affinés de NLLB-200 pour dix-huit dialectes malgaches sous licence Apache 2.0, les checkpoints MMS-TTS-MLG VITS pour dix-huit dialectes également sous Apache 2.0, les scripts d'affinement reproductibles avec documentation complète, un benchmark d'évaluation dialectal malgache avec jeux de test hold-out et métriques de référence, ainsi qu'une API publique documentée sur github.com/mgvaovao/backend_ia pour l'intégration du pipeline par des tiers.

Sur le plan de l'impact communautaire, le projet documentera le nombre de sessions d'utilisation du système à la Maison du Numérique avec un objectif de 2 000 sessions sur douze mois, le nombre de locuteurs natifs ayant participé à la collecte avec un objectif de 500 personnes réparties sur quatorze régions, ainsi que les résultats des évaluations de satisfaction et d'intelligibilité menées auprès des utilisateurs.

Les apprentissages clés porteront sur plusieurs dimensions. Le projet documentera les conditions minimales de données nécessaires pour un affinement de modèles TTS et MT de qualité déployable sur des dialectes à très faibles ressources. Il capitalisera les meilleures pratiques pour la collecte de données vocales communautaires dans des contextes ruraux africains. Il produira enfin une analyse comparative des performances des modèles sur dix-huit variétés dialectales, permettant d'identifier les facteurs linguistiques qui influencent la qualité des systèmes de parole pour des langues géographiquement variées. Toutes ces connaissances seront publiées dans un rapport technique final partagé avec la communauté Masakhane, en français et en anglais.

*(~490 mots)*

---

## Question 11 — Calendrier et jalons (400 mots max)

Le projet est planifié sur une durée de dix-huit mois, structurée en trois phases successives.

**Phase 1 : Mise en place et lancement (Mois 1 à 4)**

Cette phase couvre le recrutement et la formation des quatorze coordinateurs locaux, la finalisation des protocoles de consentement et des textes de collecte dans chaque dialecte, ainsi que l'établissement des partenariats avec les antennes régionales et les associations communautaires. Les sessions d'enregistrement démarrent pour les cinq premiers dialectes prioritaires, à savoir l'antandroy, le tsimihety, le vezo, le bara et le sihanaka. Le livrable de fin de phase est l'infrastructure de collecte opérationnelle, cinq corpus dialectaux en cours de traitement et les premiers affinements en cours sur Vertex AI.

**Phase 2 : Production principale (Mois 5 à 12)**

Cette phase concentre la collecte des données pour les neuf dialectes restants ainsi que l'affinement des modèles NLLB et MMS-TTS pour l'ensemble des dix-huit dialectes au fur et à mesure de la disponibilité des données. L'évaluation automatique et humaine est conduite pour chaque modèle dialectal, et les dialectes validés sont progressivement déployés dans le système de la Maison du Numérique. Le jalon du mois 8 est d'avoir dix premiers dialectes affinés, évalués et déployés avec des scores satisfaisant les seuils de qualité définis. Le jalon du mois 12 est d'avoir les dix-huit dialectes affinés et en cours d'évaluation communautaire, avec 1 000 sessions d'utilisation documentées à la Maison du Numérique.

**Phase 3 : Consolidation, publication et transfert (Mois 13 à 18)**

Cette phase est consacrée aux sessions d'évaluation communautaire finales pour tous les dialectes, aux réentraînements ciblés sur la base des retours, à la publication intégrale des ressources sur HuggingFace et GitHub, à l'organisation d'un atelier de restitution ouvert à la communauté NLP africaine, ainsi qu'à la rédaction du rapport technique final. Le livrable final au mois 18 est l'ensemble des dix-huit dialectes opérationnels en production, tous les corpus et modèles publiés sous licence ouverte, une documentation complète, 2 000 sessions d'utilisation documentées et le rapport technique final soumis à la communauté Masakhane.

*(~390 mots)*

---

## Question 12 — Éthique, inclusion et gouvernance des données (500 mots max)

La dimension éthique est au cœur de la conception de MGVaovao et non une considération secondaire.

Sur le consentement et la protection des locuteurs, chaque participant à la collecte de données vocales signe un formulaire de consentement éclairé disponible en malgache officiel et dans la variété dialectale de la région de collecte. Ce formulaire explique la nature des données collectées, leur usage prévu, la licence CC BY 4.0 sous laquelle elles seront publiées, ainsi que le droit de retrait à tout moment avant la publication. Les mineurs ne participent qu'avec le consentement écrit d'un parent ou tuteur.

Sur l'inclusion et la représentation, le protocole de collecte impose une parité de genre : au minimum 50 % des locuteurs enregistrés dans chaque dialecte sont des femmes. La diversité d'âge est prise en compte avec trois tranches couvrant respectivement les 18 à 35 ans, les 36 à 55 ans et les 55 ans et plus, afin de capturer la variabilité phonologique intergénérationnelle. Les coordinateurs locaux sont eux-mêmes membres des communautés ciblées, assurant ainsi une médiation culturellement appropriée. L'engagement de la Maison du Numérique pour l'inclusion va au-delà du genre et de l'âge : l'organisation conduit déjà un programme spécifique d'inclusion numérique pour les enfants atteints de trisomie 21, ce qui témoigne de façon tangible que l'équité et l'inclusion sont des pratiques quotidiennes documentées et non de simples déclarations d'intention.

Sur les licences et l'ouverture, tous les livrables produits, notamment les corpus audio, les transcriptions, les poids de modèles affinés, les scripts et la documentation, sont publiés sous des licences pleinement ouvertes : Apache 2.0 pour les modèles et le code, Creative Commons BY 4.0 pour les données. Cela garantit que les ressources créées bénéficient à l'ensemble de l'écosystème NLP africain sans restriction d'usage.

Sur l'impact environnemental, le projet optimise délibérément son empreinte de calcul via l'utilisation de modèles distillés comme NLLB-200-distilled-600M, la quantification INT8, le fine-tuning LoRA qui ne réentraîne qu'une fraction des paramètres, et une infrastructure de production à scale-to-zero éliminant la consommation d'énergie en dehors des périodes d'utilisation active.

Sur la gouvernance des données, les données collectées sont stockées sur GCS avec chiffrement au repos et accès restreint à l'équipe du projet. La Maison du Numérique est l'entité légalement responsable. Fenitra Ravelomanantsoa, en tant que juriste spécialisé en droit numérique et Directeur des affaires juridiques et réglementaires Cloud chez Google, garantit personnellement la conformité du projet avec les standards internationaux de protection des données. Cette expertise de directeur au sein d'une des principales entreprises technologiques mondiales est rare dans les projets de données africaines et constitue un atout distinctif de cette candidature.

*(~490 mots)*

---

## Question 13(a) — Candidature en consortium ?

Non. MGVaovao - Maison du Numérique (Madagasikara Vaovao) soumet cette proposition en tant qu'organisation principale. Le projet s'appuie sur un réseau de partenaires opérationnels établis, à savoir Telma Madagascar, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et ANKY, mais ceux-ci interviennent comme partenaires et non comme co-candidats formels. Des lettres de soutien peuvent être fournies sur demande.

## Question 13(b) — Détails du consortium

Sans objet.

---

## Question 14 — Lettres de soutien et documentation complémentaire

Des lettres de soutien peuvent être sollicitées auprès des partenaires opérationnels de la Maison du Numérique, notamment Telma Madagascar pour les programmes E-JERY et HOLI DEV, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et ANKY. Ces partenariats sont actifs et documentés depuis l'inauguration de la Maison du Numérique en février 2024.

La documentation complémentaire du projet est accessible directement dans les dépôts publics GitHub. Le dépôt github.com/mgvaovao/ml contient le fichier README détaillé décrivant l'architecture complète du pipeline, les instructions de reproduction de l'affinement, les métriques d'évaluation obtenues et la structure des données, ainsi qu'un fichier `MGVaovao_Architecture_Complete.md` qui documente l'ensemble des choix architecturaux, des dépendances et du flux de données. Le dépôt github.com/mgvaovao/backend_ia contient de même un README complet et la documentation de l'API. L'ensemble de ces ressources est publié sous licence Apache 2.0.

---

## Question 15 — Membres de l'équipe et rôles (400 mots max)

L'équipe du projet MGVaovao réunit des compétences complémentaires et un ancrage profond dans le contexte malgache.

**Fenitra Ravelomanantsoa, Fondateur et Directeur général de MGVaovao - Maison du Numérique**

Juriste de formation et Directeur des affaires juridiques et réglementaires Cloud (Head of Cloud Regulatory) chez Google à Zurich, Fenitra occupe un poste de direction dans l'une des principales entreprises technologiques mondiales, où il supervise la conformité réglementaire des infrastructures cloud à l'échelle internationale. Après plus de 20 ans de carrière internationale à Paris, Barcelone, Londres et Zurich, il a fondé l'association Madagasikara Vaovao et MGVaovao - Maison du Numérique en novembre 2023, convaincu que son expertise en gouvernance des technologies, protection des données et compliance cloud pouvait bénéficier directement à son pays. Il supervise la stratégie globale, les partenariats institutionnels et la gouvernance éthique du projet.

**Norolala Randrianarison, Directrice locale et Responsable des opérations**

Professionnelle du secteur des télécommunications et du numérique à Madagascar, Mme Noro assure la direction opérationnelle de la Maison du Numérique au quotidien. Elle supervise l'accueil des communautés, le déploiement des programmes, la coordination des bénévoles et la relation avec les partenaires institutionnels locaux.

**Guillaume Rakotonjanahary Tsantaniaina, Chef de projet technique — ML et Développement**

Ingénieur AI/ML avec plus de cinq ans d'expérience dans des systèmes de production en Speech AI, NLP et infrastructure cloud GCP, Guillaume est titulaire d'un Master en Big Data et IA de l'ESTIA (France), obtenu avec mention Très Bien (17,2/20). En tant que chef de projet technique, il prend en charge le volet ML et développement du pipeline : architecture des modèles, affinement NLLB et MMS-TTS, déploiement sur Cloud Run GPU et orchestration MLOps sur Vertex AI. Locuteur natif du malgache et du français, il apporte une compréhension intime des nuances dialectales indispensable à la qualité des modèles. Lauréat d'IndabaX Madagascar 2023 et participant au DataTour 2025 en compétition pan-africaine, il est actif dans l'écosystème IA africain.

**Karine Maholisoa Rajaofera, Chef de projet Data, Opérations et Fonctionnel**

Titulaire d'un Bachelor en Business Management, Karine apporte dix ans d'expérience dans les opérations de données, la collecte à grande échelle et la coordination terrain. Spécialiste des données et experte en lidar chez SmartOne.ai, elle a conduit des projets de collecte, d'annotation et de validation de données en conditions réelles sur une décennie. Elle rejoint MGVaovao - Maison du Numérique en septembre 2025 et pilote depuis lors le programme d'IA sur les dialectes malgaches en tant que chef de projet principal. Elle assume la direction du volet data, opérationnel et fonctionnel du projet : supervision du cycle complet de collecte vocale dans les quatorze régions dialectales, définition des protocoles d'annotation, contrôle qualité des transcriptions, coordination des équipes terrain et traduction des besoins métier en spécifications fonctionnelles pour le pipeline technique. Maîtrisant les outils bureautiques et collaboratifs tels que Word, Excel, Google Sheets et l'ensemble des plateformes Google, elle assure l'interface entre les réalités opérationnelles du terrain et le volet technique porté par Guillaume. Elle pilote également le programme d'inclusion numérique des enfants atteints de trisomie 21 à la Maison du Numérique.

**Chef de projet partenariats et impact (à recruter sur fonds LINGUA Africa)**

Un troisième chef de projet dédié aux partenariats institutionnels et à la mesure d'impact sera recruté en début de projet.

**Coordinateurs locaux (à recruter sur fonds LINGUA Africa)**

Un coordinateur de terrain sera recruté pour chacun des quatorze dialectes à couvrir, au sein des communautés locutrices, de préférence des femmes.

*(~400 mots)*

---

## Question 16 — Travaux antérieurs et références (300 mots max)

Ce projet s'inscrit dans une trajectoire de recherche et de développement cohérente dont les jalons antérieurs établissent à la fois sa faisabilité et son originalité.

MGVaovao - Maison du Numérique, fondée en novembre 2023, opère depuis son inauguration en février 2024. C'est sur cette base institutionnelle solide que le projet de traduction speech-to-speech en dialectes malgaches a été lancé en fin 2025, après une phase préliminaire d'évaluation des architectures ASR et TTS existantes pour les langues à faibles ressources, notamment Whisper, Chirp de Vertex AI Studio et les architectures VITS, qui a permis d'établir la méthodologie d'adaptation par transfert aujourd'hui au cœur du pipeline.

Ce prototype de traduction parole-vers-parole est opérationnel depuis avril 2026 pour quatre dialectes, à savoir le malgache officiel, le betsileo, le betsimisaraka et le sakalava, avec une latence de bout en bout inférieure à cinq secondes. Il constitue un premier résultat concret à améliorer et à étendre, non un système finalisé. Environ 1 000 paires de données ont déjà été constituées, comprenant des paires texte-texte pour la traduction neuronale et des paires texte-audio pour la synthèse vocale, ce qui démontre la capacité opérationnelle de l'équipe à collecter et traiter des données dialectales réelles.

Sur le plan académique, le projet s'appuie sur les travaux fondateurs de la communauté Masakhane, sur les publications de l'équipe NLLB de Costa-jussà et al. (2022) pour la traduction multilingue, sur les travaux de Pratap et al. (2023) sur MMS pour la synthèse vocale multilingue, et sur les avancées en reconnaissance automatique de la parole pour les langues sous-dotées.

La Maison du Numérique apporte une base communautaire documentée et vérifiable : 5 000 personnes formées depuis l'inauguration de février 2024, 550 utilisateurs mensuels actifs, et des partenariats opérationnels établis avec Telma Madagascar, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et ANKY.

*(~290 mots)*

---

## Question 17(a) — Fichier budget détaillé

Fichier Excel séparé : `LINGUA_Africa_Budget_Detaille.xlsx` (à téléverser sur Submittable)

---

## Question 17(b) — Tableau récapitulatif du budget

| Catégorie de coût | Montant (USD) |
|---|---|
| 1. Personnel — direction permanente (5 postes) | 144 900 |
| 2. Équipement et logiciels | 8 000 |
| 3. Collecte terrain — 54 collecteurs × 133 USD × 4 mois (600 000 MGA/mois) | 28 728 |
| 4. Annotation et vérification ground truth — 36 annotateurs × 200 USD × 4 mois (900 000 MGA/mois) | 28 800 |
| 5. Déplacements et terrain | 16 000 |
| 6. Ateliers, réunions et formation | 4 500 |
| 7. Communication et sensibilisation | 1 500 |
| 8. Autres coûts directs | 1 000 |
| **Total des coûts directs** | **233 428** |
| 9. Frais généraux / Coûts indirects (5 %) | 11 671 |
| **Grand Total** | **245 099** |

*Co-financement organisation (hors budget LINGUA Africa) : 8 développeurs (backend, frontend, IA, data science, DevOps) × 333 USD (1 500 000 MGA) × 18 mois = 47 952 USD.*

---

## Question 17(c) — Justification du budget (300 mots max)

Le budget proposé de 245 099 USD reflète fidèlement les activités planifiées et les coûts réels du contexte malgache, en restant en dessous du plafond de 250 000 USD prévu pour la Catégorie 3.

Le poste personnel (144 900 USD) couvre l'équipe de direction permanente sur dix-huit mois : le fondateur en conseil stratégique à mi-temps (1 250 USD × 18 = 22 500 USD), la directrice locale à temps plein (2 000 USD × 18 = 36 000 USD), le Chef de projet technique ML (1 800 USD × 18 = 32 400 USD), la Chef de projet Data et Opérations (1 800 USD × 18 = 32 400 USD) et un chef de projet partenariats démarrant au mois 7 (1 800 USD × 12 = 21 600 USD). L'équipe technique de huit développeurs — backend, frontend, développeurs IA, data scientists et DevOps — constitue un apport complémentaire de l'organisation de 47 952 USD (1 500 000 MGA par développeur par mois × 18 mois), non inclus dans la demande LINGUA Africa.

Le poste collecte terrain (28 728 USD) rémunère 54 collecteurs — trois par dialecte pour dix-huit dialectes — à 133 USD par mois (600 000 MGA) sur quatre mois actifs de collecte intensive (54 × 133 × 4 = 28 728 USD).

Le poste annotation et vérification (28 800 USD) rémunère 36 annotateurs-transcripteurs — deux par dialecte — à 200 USD par mois (900 000 MGA) sur quatre mois actifs de traitement ground truth (36 × 200 × 4 = 28 800 USD).

Le poste équipement et logiciels (8 000 USD) couvre six ordinateurs portables et le matériel d'enregistrement terrain. Les déplacements (16 000 USD) couvrent les missions dans les dix-huit régions dialectales. Les ateliers (4 500 USD) financent la formation des équipes terrain, un atelier de restitution final et une conférence régionale. Les frais généraux sont limités à 5 % (11 671 USD).

*(~275 mots)*

---

## Question 18(a) — Besoin en ressources de calcul ?

Oui.

## Question 18(b) — Montant demandé en ressources de calcul

150 000 USD en crédits de calcul GCP (sur un maximum de 400 000 USD pour la Catégorie 3).

---

## Question 18(c) — Usage des ressources de calcul (300 mots max)

Les crédits de calcul GCP demandés (150 000 USD) seront répartis sur trois composantes de l'architecture technique du projet.

La part principale, soit environ 80 000 USD, sera allouée aux travaux d'affinement des modèles sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot à environ 0,28 USD de l'heure. Ces crédits couvrent les runs de fine-tuning NLLB LoRA pour les six langues source et les dix-huit dialectes, en incluant les cycles d'expérimentation, d'optimisation des hyperparamètres et de réentraînement sur nouvelles données, ainsi que l'affinement MMS-TTS pour chaque dialecte. Le budget d'expérimentation est intentionnellement généreux pour permettre plusieurs itérations de qualité sur des dialectes peu documentés, où l'optimisation des données et des paramètres est déterminante pour atteindre les seuils de qualité requis.

Une part significative, soit environ 45 000 USD, sera allouée à l'infrastructure de production. Elle couvre Cloud Run GPU avec un NVIDIA L4 pour l'hébergement de l'API MGVaovao sur dix-huit mois, avec une capacité de trois à cinq sessions WebRTC concurrentes pendant les heures d'ouverture de la Maison du Numérique et scale-to-zero en dehors des heures d'utilisation. Cette enveloppe prévoit également la montée en charge lors des périodes d'évaluation communautaire intense.

La partie restante, environ 25 000 USD, couvrira les pipelines d'orchestration et d'évaluation automatique via Vertex AI Pipelines, le stockage GCS des corpus audio et checkpoints pour un volume d'environ 3 To au total, les services d'intégration continue et de monitoring comprenant Cloud Build, Artifact Registry et Cloud Monitoring, ainsi que le traitement des données dans les pipelines d'ingestion.

L'ensemble de l'architecture est conçu avec une philosophie de frugalité : les instances Spot réduisent le coût du fine-tuning jusqu'à 70 % par rapport aux instances à la demande, les modèles sont distillés et quantifiés pour la production, et le scale-to-zero élimine la consommation en dehors des heures d'utilisation active.

*(~295 mots)*

---

## Question 19(a) — Besoin en support technique ?

Oui.

## Question 19(b) — Nature du support technique souhaité (300 mots max)

Le soutien technique sollicité porte sur trois domaines complémentaires à l'expertise interne de l'équipe.

Le premier domaine est la linguistique computationnelle appliquée aux dialectes malgaches. La diversité dialectale du malgache soulève des questions spécialisées que l'équipe ne peut pas résoudre seule, notamment la définition des orthographes de référence pour les dialectes non standardisés, la gestion des variations phonologiques intradialectales et les protocoles d'annotation adaptés aux langues à tradition principalement orale. Un accès à des experts en linguistique descriptive des langues malagasyphones, via le réseau d'academic fellows de LINGUA Africa, serait directement utile pour structurer ces aspects dès la phase de collecte.

Le deuxième domaine est l'évaluation humaine à grande échelle. Mettre en place des panels de locuteurs natifs de dix-huit dialectes distincts avec des protocoles d'évaluation standardisés et une analyse rigoureuse des résultats est une démarche que l'équipe mène pour la première fois à cette échelle. Un accompagnement méthodologique de chercheurs ayant une expérience dans l'évaluation de systèmes de parole pour langues africaines serait très précieux pour garantir la validité et la comparabilité des résultats.

Le troisième domaine est la mise en réseau avec d'autres projets de l'écosystème LINGUA Africa travaillant sur des problématiques similaires, telles que les langues insulaires africaines, les dialectes régionaux et les langues à tradition orale. Un accès structuré aux communautés de pratique Masakhane permettrait à l'équipe de bénéficier des apprentissages d'autres projets et de contribuer en retour avec ses propres résultats sur le malgache, enrichissant ainsi l'écosystème collectif et renforçant la position de Madagascar dans le domaine du NLP africain.

*(~290 mots)*

---

## Informations sur l'organisation

**Nom légal :** Madagasikara Vaovao  
**Nom commercial :** Maison du Numérique / MGVaovao  
**Type d'organisation :** Association à but non lucratif  
**Pays du siège social :** Madagascar  
**Pays de présence :** Madagascar  
**Email de l'organisation :** contact@mgvaovao.com  
**Présence en ligne :** https://mgvaovao.com | https://github.com/mgvaovao/ml | https://github.com/mgvaovao/backend_ia | https://www.linkedin.com/company/maison-du-num%C3%A9rique-madagascar | https://www.facebook.com/profile.php?id=61552728359577  
**Candidature antérieure Masakhane :** Non  
**Projet Masakhane en cours :** Non  

---

## Personne de contact de l'organisation

**Prénom :** Fenitra  
**Nom :** Ravelomanantsoa  
**Email :** fenitra@google.com  
**Téléphone :** +261 38 37 773 93  
**Rôle dans l'organisation :** Fondateur et Directeur général  

---

*Document source en français. Version anglaise : LINGUA_Africa_Application_MGVaovao_EN.docx*  
*Budget détaillé : LINGUA_Africa_Budget_Detaille.xlsx (à téléverser séparément sur Submittable)*
