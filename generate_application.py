# -*- coding: utf-8 -*-
"""
Génère le fichier Word de candidature LINGUA Africa — MGVaovao / Maison du Numérique (Français)
Source : LINGUA_Africa_Application_QA.md (version approuvée)
"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(2.8)
    section.right_margin  = Cm(2.8)

# ── Helpers ───────────────────────────────────────────────────────────────────
def rf(run, bold=False, size=11, color=None, italic=False):
    run.bold = bold; run.italic = italic
    run.font.size = Pt(size); run.font.name = "Calibri"
    if color: run.font.color.rgb = RGBColor(*color)

def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text.upper())
    rf(run, bold=True, size=13, color=(31, 78, 121))
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '1');   bot.set(qn('w:color'), '1F4E79')
    pBdr.append(bot); pPr.append(pBdr)
    return p

def qlabel(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(3)
    rf(p.add_run(text), bold=True, size=11, color=(68, 114, 196))
    return p

def para(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.left_indent  = Cm(0.5)
    rf(p.add_run(text), size=11)
    return p

def subh(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Cm(0.5)
    rf(p.add_run(text), bold=True, size=11, color=(0, 70, 127))
    return p

def note(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.left_indent  = Cm(0.5)
    rf(p.add_run(text), size=10, italic=True, color=(150, 0, 0))
    return p

def field(doc, label, value):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Cm(0.5)
    rf(p.add_run(label + " "), bold=True, size=11)
    rf(p.add_run(value), size=11)
    return p

def btable(doc, rows):
    t = doc.add_table(rows=len(rows)+1, cols=2)
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    hdr[0].text = "Catégorie de coût"; hdr[1].text = "Montant (USD)"
    for c in hdr:
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(10)
    for i, (cat, amt) in enumerate(rows):
        row = t.rows[i+1].cells
        row[0].text = cat; row[1].text = amt
        for c in row:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = "Calibri"; r.font.size = Pt(10)
        if "Total" in cat or "Grand" in cat:
            for c in row:
                for p in c.paragraphs:
                    for r in p.runs: r.bold = True
    return t


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE DE TITRE
# ═══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(20)
rf(p.add_run("CANDIDATURE LINGUA AFRICA 2026"), bold=True, size=20, color=(31, 78, 121))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Masakhane African Languages Hub · Microsoft AI for Good Lab · Gates Foundation · Google.org"),
   size=10, color=(100, 100, 100))

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("MGVaovao — Maison du Numérique"), bold=True, size=16, color=(0, 70, 127))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Madagasikara Vaovao · Antananarivo, Madagascar"), size=12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Date limite : 15 juin 2026"), size=11, italic=True)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# INFORMATIONS SUR L'ORGANISATION
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Informations sur l'organisation")

field(doc, "Langue de candidature :", "Français")
field(doc, "Nom légal :", "Madagasikara Vaovao")
field(doc, "Nom commercial :", "Maison du Numérique / MGVaovao")
field(doc, "Type d'organisation :", "Association à but non lucratif")
field(doc, "Pays du siège social :", "Madagascar")
field(doc, "Pays de présence :", "Madagascar")
field(doc, "Email de l'organisation :", "contact@mgvaovao.com")
field(doc, "Présence en ligne :",
    "https://mgvaovao.com  |  https://github.com/mgvaovao/ml  |  "
    "https://github.com/mgvaovao/backend_ia  |  "
    "https://www.linkedin.com/company/maison-du-num%C3%A9rique-madagascar  |  "
    "https://www.facebook.com/profile.php?id=61552728359577")
field(doc, "Candidature antérieure Masakhane :", "Non")
field(doc, "Projet Masakhane en cours :", "Non")

doc.add_paragraph()
h1(doc, "Personne de contact")
field(doc, "Prénom :", "Fenitra")
field(doc, "Nom :", "Ravelomanantsoa")
field(doc, "Email :", "fenitra@google.com")
field(doc, "Téléphone :", "+261 38 37 773 93")
field(doc, "Rôle dans l'organisation :", "Fondateur et Directeur général")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# DÉTAILS DE LA PROPOSITION
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Détails de la proposition")

# ── Q1a ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 1(a) — Catégorie(s) de candidature")
para(doc,
    "Catégories cochées : Catégorie 1 — Création de données, "
    "Catégorie 2 — Développement de modèles et d'outils et "
    "Catégorie 3 — Applications sectorielles.\n\n"
    "Ce projet porté par MGVaovao - Maison du Numérique ne relève pas d'une catégorie principale "
    "unique car il constitue un pipeline complet et indissociable dans lequel les trois dimensions "
    "sont de poids égal. La Catégorie 1 correspond à la constitution systématique des premiers "
    "corpus vocaux ouverts pour 18 dialectes malgaches, sans lesquels aucun affinement n'est "
    "possible. La Catégorie 2 correspond à l'affinement des modèles fondationnaux NLLB-200 et "
    "MMS-TTS-MLG pour chacun de ces dialectes, ce qui constitue le cœur technique du projet. "
    "La Catégorie 3 correspond au déploiement de l'ensemble dans une application réelle au "
    "service de communautés. Ces trois dimensions se conditionnent mutuellement : créer des "
    "données sans entraîner de modèles ne produit aucun impact, entraîner des modèles sans les "
    "intégrer dans une application ne rejoint pas les bénéficiaires, et déployer une application "
    "sans données ni modèles de qualité n'est pas crédible. C'est précisément la force de cette "
    "candidature que de couvrir l'intégralité du pipeline, de la collecte communautaire jusqu'à "
    "l'usage en production.")

# ── Q1b ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 1(b) — Titre du projet et résumé (300 mots max)")
para(doc,
    "Titre du projet :\n"
    "Traduction multilingue parole-vers-parole en temps réel vers 18 dialectes malgaches — "
    "une infrastructure d'IA ouverte au service de l'inclusion linguistique")
para(doc,
    "Résumé :\n\n"
    "Madagascar est une île-continent où 28 millions d'habitants parlent un malgache profondément "
    "pluriel : 18 dialectes régionaux vivants, porteurs d'identités et de cultures distinctes, qui "
    "n'ont jusqu'ici bénéficié d'aucune représentation dans les systèmes d'intelligence artificielle "
    "modernes. Ce vide prive des millions de locuteurs d'un accès équitable à l'éducation numérique, "
    "aux services de santé et aux ressources civiques.\n\n"
    "MGVaovao - Maison du Numérique est l'organisation qui porte ce projet. Elle développe, "
    "depuis Antananarivo, un système de traduction parole-vers-parole en temps réel conçu pour "
    "convertir automatiquement la parole en six langues internationales — le français, l'anglais, "
    "l'allemand, l'espagnol, l'italien et le portugais — en parole malgache naturelle dans le "
    "dialecte choisi par l'utilisateur.\n\n"
    "Un premier proof of concept couvrant quatre dialectes est fonctionnel depuis avril 2026, "
    "avec une latence inférieure à cinq secondes, sur Cloud Run GPU. Ce prototype démontre la "
    "faisabilité technique de l'approche et constitue une base concrète à améliorer et à étendre. "
    "Depuis le lancement du projet fin 2025, l'équipe a déjà constitué environ 1 000 paires de "
    "données, ce qui confirme la faisabilité opérationnelle de la collecte.\n\n"
    "Le soutien de LINGUA Africa permettra d'étendre la couverture aux 14 dialectes restants, de "
    "constituer les premières ressources linguistiques vocales ouvertes pour l'ensemble du malgache "
    "dialectal, et de déployer ce service dans les programmes d'éducation, de santé et d'inclusion "
    "civique de MGVaovao - Maison du Numérique, un centre communautaire qui accueille plus de "
    "550 personnes par mois et a formé plus de 5 000 individus depuis son inauguration en "
    "février 2024.")

# ── Q2 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 2 — Justification de la proposition et objectifs (750 mots max)")
para(doc,
    "Le malgache compte parmi les quarante langues africaines les plus parlées au monde. Mais "
    "derrière cette reconnaissance globale se dissimule une réalité bien plus complexe. Madagascar "
    "est une île-continent où coexistent dix-huit dialectes régionaux, dont certains diffèrent "
    "phonologiquement et lexicalement au point de constituer de véritables barrières de "
    "communication entre communautés. Le malgache officiel, à savoir la variété Merina, est la "
    "langue administrative et médiatique, mais des millions de Malgaches dans les régions betsileo, "
    "betsimisaraka, sakalava, antandroy et bien d'autres n'accèdent aux services numériques, "
    "éducatifs et sanitaires qu'à travers une langue qui n'est pas la leur, ou n'y accèdent tout "
    "simplement pas.\n\n"
    "Ce déséquilibre est amplifié par une fracture numérique persistante. Lorsqu'un agriculteur "
    "betsileo cherche des informations sur des semences résistantes à la sécheresse, lorsqu'une "
    "mère betsimisaraka souhaite comprendre les consignes de santé maternelle, ou lorsqu'un citoyen "
    "sakalava veut accéder à un service administratif en ligne, les outils numériques disponibles "
    "fonctionnent soit en malgache officiel, soit dans une langue coloniale. Aucun système "
    "d'intelligence artificielle existant ne parle leur dialecte. C'est précisément ce vide "
    "documenté et mesurable que MGVaovao s'est donné pour mission de combler.\n\n"
    "Le projet poursuit trois objectifs interconnectés. Le premier est de constituer les premières "
    "ressources linguistiques ouvertes pour dix-huit dialectes malgaches, notamment des corpus "
    "audio annotés, des poids de modèles affinés et des benchmarks d'évaluation reproductibles, "
    "publiés intégralement sous licences Apache 2.0 et Creative Commons BY 4.0. Le deuxième est "
    "de déployer un outil concret et immédiatement utilisable, accessible depuis la Maison du "
    "Numérique et via une API publique, permettant à des services d'éducation, de santé et "
    "d'administration de s'adresser en malgache dialectal à leurs bénéficiaires. Le troisième est "
    "d'ancrer ce projet dans une dynamique communautaire vérifiable et durable, où les locuteurs "
    "natifs participent à la collecte, à la validation et à l'évaluation.\n\n"
    "À ce jour, moins de dix travaux académiques publiés traitent du traitement automatique du "
    "langage malgache dans sa diversité dialectale. Les grandes bases de données multilingues telles "
    "que Common Voice, FLORES-200 et OPUS contiennent des données pour le malgache officiel, mais "
    "aucune pour ses variétés dialectales. MGVaovao - Maison du Numérique crée ces ressources pour "
    "la première fois, avec rigueur, dans un cadre communautaire et sous licences entièrement "
    "ouvertes.\n\n"
    "Les bénéficiaires directs sont les locuteurs de dialectes malgaches sous-représentés, soit une "
    "population estimée à plus de quinze millions de personnes. Les bénéficiaires indirects "
    "incluent les prestataires de services éducatifs, sanitaires et civiques. Parmi les programmes "
    "actifs de la Maison du Numérique figure l'inclusion numérique des enfants atteints de "
    "trisomie 21, une initiative qui illustre que la mission de l'organisation embrasse toutes "
    "les formes d'exclusion.\n\n"
    "L'équipe portant ce projet est ancrée localement et compétente techniquement à un niveau "
    "international. Fenitra Ravelomanantsoa, fondateur de Madagasikara Vaovao, est Directeur des "
    "affaires juridiques et réglementaires Cloud (Head of Cloud Regulatory) au sein de Google à "
    "Zurich, où il supervise la conformité réglementaire des infrastructures cloud à l'échelle "
    "internationale. Norolala Randrianarison assure la direction opérationnelle quotidienne. "
    "Guillaume Rakotonjanahary Tsantaniaina et Karine Maholisoa Rajaofera dirigent chacun un volet "
    "complémentaire du projet. Guillaume est Chef de projet technique en charge du développement "
    "ML, de l'architecture du pipeline et du déploiement cloud. Titulaire d'un Master en Big Data "
    "et IA obtenu avec mention Très Bien (17,2/20 à l'ESTIA France), il a développé au cours de "
    "ses cinq années d'expérience une gamme étendue de systèmes IA : pipelines Speech AI complets, "
    "systèmes multi-agents LLM avec LangGraph et Google ADK, architectures RAG hybrides, modèles "
    "de vision par ordinateur et infrastructures MLOps sur Vertex AI. Sa participation à IndabaX "
    "Madagascar 2023 (3e place, classification NLP médicale à 94 % de précision) et au DataTour "
    "2025 (compétition pan-africaine) témoignent de son engagement dans l'écosystème IA africain. "
    "Karine Maholisoa Rajaofera, Chef de projet Data, Opérations et Fonctionnel, apporte dix ans "
    "d'expérience dans les opérations de données, l'annotation et la coordination de collectes à "
    "grande échelle. Cette complémentarité entre expertise ML de haut niveau et maîtrise des "
    "opérations de données rend ce projet techniquement solide et ancré dans une réalité "
    "communautaire opérationnelle.")

# ── Q3 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 3 — Langues couvertes et justification (350 mots max)")
para(doc,
    "Le projet cible le malgache dans l'intégralité de ses dix-huit dialectes régionaux. Le "
    "malgache compte plus de 28 millions de locuteurs, ce qui le place parmi les quarante langues "
    "africaines les plus parlées. Mais derrière cette unité apparente se cache une réalité "
    "dialectale d'une richesse et d'une complexité remarquables, presque entièrement absente des "
    "systèmes d'IA existants.\n\n"
    "Le malgache officiel, désigné plt_Latn dans les systèmes NLP internationaux et correspondant "
    "à la variété Merina, est la seule forme qui dispose d'une présence, encore minimale, dans les "
    "corpus multilingues tels que FLORES-200 et Common Voice. Les dix-sept dialectes régionaux, "
    "parmi lesquels le betsileo, le betsimisaraka, le sakalava, l'antandroy, le tsimihety, le "
    "vezo, le bara, le sihanaka, l'antakarana, le makoa et l'antaisaka, n'ont aucune représentation "
    "dans l'écosystème NLP mondial.\n\n"
    "Trois raisons convergentes justifient ce choix. Il s'agit d'abord d'un vide documenté et "
    "mesurable : aucun corpus vocal dialectal validé, aucun modèle NLP de production et aucun "
    "outil de synthèse vocale dialectale n'existe aujourd'hui sous licence ouverte pour ces "
    "variétés. Ce choix est ensuite ancré dans une légitimité communautaire irréfutable : l'équipe "
    "est malgache, basée à Antananarivo, locutrice native des langues ciblées, et la Maison du "
    "Numérique opère physiquement au sein de ces communautés depuis février 2024, avec des "
    "partenariats établis sur l'ensemble du territoire national. L'impact potentiel est enfin à "
    "la fois immédiat et durable. Un système qui parle betsileo à une famille de la région "
    "Haute-Matsiatra ou sakalava à un pêcheur de Mahajanga n'est pas une ambition lointaine. "
    "C'est une réalité que notre infrastructure technique rend possible dès aujourd'hui pour "
    "quatre dialectes, et que le financement LINGUA Africa permettra d'étendre aux quatorze "
    "variétés restantes selon un plan structuré sur dix-huit mois.")

# ── Q4 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 4 — Domaines et sous-domaines (300 mots max)")
para(doc,
    "Ce projet de traduction dialectale porté par MGVaovao - Maison du Numérique se déploie à "
    "l'intersection de trois domaines prioritaires définis par LINGUA Africa.\n\n"
    "Le premier est l'éducation. La Maison du Numérique accueille chaque mois plus de 550 jeunes "
    "et adultes dans ses programmes de formation numérique, dont E-JERY et HOLI DEV, soutenus par "
    "Telma Madagascar. De façon encore plus remarquable, la Maison du Numérique a développé un "
    "programme d'inclusion numérique spécifiquement destiné aux enfants atteints de trisomie 21, "
    "une initiative portée par ses bénévoles qui témoigne d'une conception radicalement inclusive "
    "du numérique. L'intégration d'un système de traduction dialectale dans ces programmes "
    "permettra de s'adresser aux apprenants dans leur variété linguistique maternelle, améliorant "
    "ainsi la compréhension et l'engagement. Les sous-domaines ciblés comprennent l'alphabétisation "
    "numérique, l'éducation de base et l'éducation spécialisée.\n\n"
    "Le deuxième est la santé publique. En partenariat avec des acteurs de santé communautaire, le "
    "système permettra de diffuser des messages de prévention couvrant la santé maternelle et "
    "infantile, la vaccination et la gestion des épidémies dans les dialectes des régions "
    "concernées.\n\n"
    "Le troisième est l'inclusion civique et numérique. Le système permettra à des citoyens non "
    "locuteurs du malgache officiel d'accéder à des informations sur les services publics, les "
    "droits civiques et les ressources gouvernementales dans leur dialecte. Ce besoin est "
    "particulièrement aigu dans les zones rurales, où les barrières linguistiques constituent le "
    "premier obstacle à l'accès à l'information.")

# ── Q5 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 5 — Données collectées (500 mots max — Catégorie 1)")
para(doc,
    "Ce projet couvre la Catégorie 1 par sa composante substantielle de création de données, "
    "sans laquelle l'extension aux quatorze dialectes restants serait impossible.\n\n"
    "Le type de données produit correspond à des enregistrements audio de parole naturelle et lue, "
    "en format WAV 16 kHz mono, réalisés par des locuteurs natifs de chaque dialecte cible, "
    "associés à des transcriptions orthographiques validées par un second locuteur natif. Les "
    "textes utilisés pour les lectures guidées sont adaptés aux domaines prioritaires du projet, "
    "à savoir l'éducation, la santé communautaire et les services civiques. Depuis le lancement "
    "du projet fin 2025, environ 1 000 paires de données ont déjà été constituées pour les "
    "dialectes initiaux, ce qui constitue une preuve concrète que le protocole de collecte "
    "fonctionne.\n\n"
    "En termes de volume, le projet vise pour chaque dialecte un corpus initial de 150 à "
    "200 heures de parole naturelle et 10 000 paires audio-transcription de haute qualité. Les "
    "quatorze dialectes restants représentent un corpus cible d'environ 2 100 à 2 800 heures "
    "d'enregistrement et 140 000 paires audio-transcription.\n\n"
    "La collecte sera organisée en partenariat avec des coordinateurs locaux dans chaque région "
    "linguistique. Ces coordinateurs sont recrutés au sein des communautés locutrices elles-mêmes, "
    "de préférence des femmes, formés au protocole de collecte et rémunérés équitablement. Les "
    "régions couvertes incluent Fianarantsoa pour le betsileo, Toamasina pour le betsimisaraka, "
    "Mahajanga pour le sakalava, Ambovombe pour l'antandroy et Mandritsara pour le tsimihety.\n\n"
    "Sur le plan de l'ouverture, toutes les données produites seront publiées sous licence Creative "
    "Commons BY 4.0 sur HuggingFace et dans Common Voice, permettant leur réutilisation par "
    "l'ensemble de la communauté de recherche en NLP africain. Les transcriptions seront également "
    "disponibles en format TSV compatible avec les outils standards de la communauté Masakhane.\n\n"
    "Le protocole respecte les standards éthiques internationaux : consentement éclairé écrit en "
    "malgache officiel et dans la variété dialectale locale, droit de retrait à tout moment avant "
    "publication, et interdiction d'enregistrement des mineurs sans consentement parental écrit.")

# ── Q6 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 6 — Modèles et outils développés (500 mots max — Catégorie 2)")
para(doc,
    "Le pipeline de traduction parole-vers-parole développé dans ce projet s'articule en quatre "
    "étapes. Un proof of concept est fonctionnel pour quatre dialectes à ce jour et l'architecture "
    "est conçue pour être étendue à l'ensemble des dix-huit variétés dialectales du malgache.\n\n"
    "La première composante est un module de détection d'activité vocale basé sur Silero VAD v5. "
    "Ce modèle de 2 Mo, fonctionnant exclusivement en CPU, traite le signal audio en fenêtres de "
    "32 millisecondes et filtre les segments de silence avant transmission au module de "
    "reconnaissance vocale, réduisant ainsi les coûts de calcul de 30 à 50 % sur des "
    "enregistrements du monde réel.\n\n"
    "La deuxième composante est le module de reconnaissance automatique de la parole, fondé sur "
    "Whisper large-v3-turbo quantifié en INT8 via CTranslate2. Ce modèle prend en charge "
    "99 langues d'entrée, dont le français, l'anglais, l'allemand, l'espagnol, l'italien et le "
    "portugais. La quantification INT8 permet d'atteindre une vitesse deux fois supérieure au "
    "modèle FP16 original tout en maintenant une précision comparable, pour une empreinte VRAM "
    "d'environ 1,7 Go.\n\n"
    "La troisième composante est le module de traduction neuronale, basé sur "
    "NLLB-200-distilled-600M, affiné par apprentissage par transfert via LoRA (rang 16, PEFT) "
    "pour chaque paire source vers plt_Latn. L'affinement, conduit sur Vertex AI Custom Training "
    "avec des GPU NVIDIA L4 Spot à 0,28 USD de l'heure, produit une amélioration mesurée de 2 à "
    "8 points de chrF++ par rapport au modèle de base pour le malgache. Les poids LoRA affinés "
    "sont publiés sous licence Apache 2.0.\n\n"
    "La quatrième composante est le module de synthèse vocale dialectale, basé sur MMS-TTS-MLG "
    "VITS de Meta, affiné par dialecte à partir de 80 à 150 échantillons audio de haute qualité, "
    "en une à deux heures sur GPU L4 Spot, via le framework ylacombe/finetune-hf-vits. Chaque "
    "checkpoint de dialecte est versionné dans Vertex AI Model Registry avec ses métadonnées "
    "d'évaluation. Les checkpoints sont publiés sous licence Apache 2.0.\n\n"
    "L'ensemble du pipeline est exposé via une API FastAPI déployée sur Google Cloud Run GPU avec "
    "un GPU NVIDIA L4 de 24 Go, avec une latence de bout en bout inférieure à cinq secondes et "
    "une empreinte VRAM totale de 6,2 Go permettant trois à cinq sessions concurrentes par "
    "instance. Le code source complet, les scripts d'affinement et la documentation technique "
    "sont publiés sur GitHub aux adresses github.com/mgvaovao/ml et "
    "github.com/mgvaovao/backend_ia, sous licence Apache 2.0.\n\n"
    "Ces composants correspondent aux modèles les plus performants disponibles au moment du "
    "développement du prototype. L'architecture est modulaire : si des modèles plus puissants "
    "ou mieux adaptés aux langues à très faibles ressources venaient à émerger au cours du "
    "projet, leur intégration dans le pipeline serait envisagée et évaluée selon les mêmes "
    "critères de qualité.")

# ── Q7 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 7 — Cas d'usage développé (500 mots max — Catégorie 3)")
para(doc,
    "Le cas d'usage principal du projet est un service de traduction et d'information multilingue "
    "en dialecte malgache, accessible depuis MGVaovao - Maison du Numérique et via une API "
    "publique, destiné à des populations qui ne maîtrisent pas le malgache officiel ou les langues "
    "internationales mais qui ont besoin d'accéder à des services éducatifs, sanitaires et civiques.\n\n"
    "Concrètement, le système se présente sous deux interfaces complémentaires. La première est "
    "une borne interactive déployée dans les locaux de la Maison du Numérique d'Ambatonakanga : "
    "une personne s'exprime en français, en anglais ou dans une autre langue prise en charge, et "
    "reçoit immédiatement une réponse audio dans son dialecte malgache. La seconde interface est "
    "une API publique et documentée, accessible aux partenaires institutionnels souhaitant intégrer "
    "la capacité de communication dialectale dans leurs propres outils.\n\n"
    "L'impact attendu s'articule autour de quatre axes. En matière d'éducation, le système permet "
    "aux formateurs de s'adresser aux apprenants dans leur variété maternelle. En matière de santé, "
    "des partenaires de santé communautaire peuvent diffuser des messages de prévention dans les "
    "dialectes des régions ciblées, sans nécessiter de traducteur humain. En matière d'inclusion "
    "civique, des informations sur les droits des citoyens et les procédures administratives "
    "peuvent être rendues accessibles en dialecte. Sur le plan de la souveraineté numérique enfin, "
    "Madagascar disposera pour la première fois d'une infrastructure linguistique ouverte "
    "construite par des Malgaches pour des Malgaches.\n\n"
    "La Maison du Numérique constitue l'environnement de pilotage idéal : plus de 550 utilisateurs "
    "mensuels, 5 000 personnes formées depuis l'inauguration de février 2024, un réseau de "
    "partenaires établis que sont Telma, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et "
    "ANKY, ainsi qu'une communauté de plus de 26 bénévoles actifs. Ce tissu humain garantit que "
    "le système sera évalué par des utilisateurs réels, dans leur contexte réel, avec des besoins "
    "réels.")

# ── Q8 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 8 — Tâches et évaluation (500 mots max)")
para(doc,
    "Le projet est structuré en cinq ensembles de tâches, chacun associé à des indicateurs "
    "d'évaluation précis et mesurables.\n\n"
    "La première tâche est la constitution des corpus vocaux dialectaux. Pour chaque dialecte "
    "non encore couvert, des sessions d'enregistrement sont organisées dans les régions d'origine "
    "des locuteurs natifs. L'évaluation porte sur le volume de données validées, la diversité des "
    "locuteurs avec une parité de genre imposée à 50 % minimum, ainsi que la qualité technique "
    "des fichiers audio.\n\n"
    "La deuxième tâche est l'affinement des modèles de traduction NLLB LoRA et de synthèse vocale "
    "MMS-TTS VITS pour chaque dialecte. L'évaluation repose sur chrF++ pour la qualité de "
    "traduction avec un objectif de score supérieur ou égal à 45 et d'amélioration de 3 points "
    "minimum sur le baseline malgache officiel, et UTMOS pour la naturalité de la synthèse vocale "
    "avec un objectif de score supérieur ou égal à 3,5 sur 5. Des évaluations humaines "
    "complémentaires sont réalisées par des panels de locuteurs natifs de chaque dialecte.\n\n"
    "La troisième tâche est le déploiement et l'intégration dans les services de la Maison du "
    "Numérique. L'évaluation porte sur le taux de disponibilité du système avec un objectif de "
    "99 % sur les heures d'ouverture, la latence de bout en bout inférieure à cinq secondes, et "
    "la satisfaction des utilisateurs mesurée par questionnaire mensuel.\n\n"
    "La quatrième tâche est la conduite de sessions d'évaluation communautaire trimestrielles. "
    "Ces sessions collectent des retours qualitatifs et alimentent les cycles de réentraînement. "
    "Aucun dialecte n'est déployé en production avant d'avoir atteint les seuils de qualité.\n\n"
    "La cinquième tâche est la publication ouverte de toutes les ressources produites. L'évaluation "
    "se mesure par le nombre de ressources publiées sur HuggingFace et GitHub, le nombre de "
    "téléchargements dans les six premiers mois et la réutilisation documentée par d'autres "
    "équipes de la communauté NLP africaine. Un tableau de bord de suivi mensuel est maintenu et "
    "partagé avec les partenaires de LINGUA Africa.")

# ── Q9 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 9 — Méthodologie (1000 mots max)")
para(doc,
    "La méthodologie de ce projet s'articule autour de quatre piliers interdépendants : une "
    "approche technique rigoureuse fondée sur l'état de l'art en speech AI, une démarche de "
    "collecte de données communautaire et éthiquement encadrée, un cycle d'évaluation continu "
    "ancré dans les retours des locuteurs natifs, et une couche d'application orientée utilisateur "
    "qui rend le service accessible en dehors de tout contexte technique.")

subh(doc, "Premier pilier : l'architecture technique")
para(doc,
    "Le pipeline de traduction parole-vers-parole repose sur quatre modules en cascade, chacun "
    "optimisé pour les contraintes du contexte africain, à savoir la latence minimale, le coût "
    "de calcul maîtrisé et l'adaptabilité à des données en faible volume.\n\n"
    "La détection d'activité vocale est assurée par Silero VAD v5, un modèle de 2 Mo fonctionnant "
    "en CPU sur des fenêtres de 32 ms, qui filtre les segments de silence et réduit les coûts de "
    "calcul de 30 à 50 %.\n\n"
    "La reconnaissance automatique de la parole est assurée par Whisper large-v3-turbo quantifié "
    "en INT8 via CTranslate2, qui offre le meilleur rapport précision/vitesse/empreinte pour les "
    "six langues source visées, avec 1,7 Go de VRAM et une vitesse deux fois supérieure à la "
    "version FP16.\n\n"
    "La traduction neuronale est assurée par NLLB-200-distilled-600M, affiné via PEFT/LoRA "
    "(rang 16) pour chaque paire source vers plt_Latn. L'affinement est conduit sur Vertex AI "
    "Custom Training avec des GPU NVIDIA L4 Spot à environ 0,28 USD de l'heure, avec des runs "
    "de 6 à 12 heures par langue source. L'amélioration de chrF++ mesurée est de 2 à 8 points.\n\n"
    "La synthèse vocale dialectale est assurée par MMS-TTS-MLG VITS de Meta, affiné par dialecte "
    "via le framework ylacombe/finetune-hf-vits. Le fine-tuning nécessite 80 à 150 échantillons "
    "et une à deux heures de calcul sur GPU L4 Spot. L'ensemble du cycle de vie des modèles est "
    "orchestré via Vertex AI Pipelines selon une architecture Kubeflow DAG. L'empreinte VRAM "
    "totale du pipeline en production est de 6,2 Go sur un GPU L4 de 24 Go, pour un coût "
    "opérationnel mensuel estimé à environ 42 USD.")

subh(doc, "Deuxième pilier : la collecte de données communautaire")
para(doc,
    "La collecte de données vocales pour les quatorze dialectes non encore couverts suit un "
    "protocole structuré en quatre étapes : identification et recrutement des coordinateurs "
    "locaux au sein des communautés elles-mêmes, de préférence des femmes, rémunérés "
    "équitablement ; préparation des textes de collecte adaptés aux domaines prioritaires et "
    "validés par des locuteurs natifs ; sessions d'enregistrement dans des espaces calmes avec "
    "signature d'un formulaire de consentement éclairé disponible en malgache officiel et dans "
    "la variété dialectale locale ; traitement automatique et validation manuelle par un second "
    "locuteur natif qui confirme la transcription et l'authenticité dialectale.")

subh(doc, "Troisième pilier : l'évaluation continue et l'amélioration itérative")
para(doc,
    "L'évaluation automatique utilise chrF++ pour la traduction, UTMOS pour la synthèse vocale "
    "et WER pour la reconnaissance vocale, sur des jeux de test réservés dès la collecte et "
    "jamais utilisés pour l'entraînement. L'évaluation humaine est conduite trimestriellement "
    "avec des panels de locuteurs natifs. Le déploiement en production utilise une stratégie "
    "blue/green sur Cloud Run GPU, avec rollback automatique en cas de régression. Aucun dialecte "
    "n'est déployé avant d'avoir atteint les seuils de qualité définis.")

subh(doc, "Quatrième pilier : la couche applicative orientée utilisateur")
para(doc,
    "Le pipeline de modèles, aussi performant soit-il, ne produit d'impact que s'il est accessible "
    "à des utilisateurs non techniques. La couche applicative constitue le point de contact direct "
    "avec les bénéficiaires.\n\n"
    "L'API FastAPI déployée sur Cloud Run GPU expose les modèles via des endpoints REST documentés, "
    "permettant à tout partenaire institutionnel d'intégrer le service de traduction dialectale "
    "dans ses propres outils. L'API gère l'authentification, la sélection du dialecte cible, la "
    "validation des entrées audio et la remontée d'erreurs structurées. Le code source complet est "
    "publié sur github.com/mgvaovao/backend_ia sous licence Apache 2.0.\n\n"
    "Par-dessus cette API, une interface temps réel — WebRTC pour les accès navigateur ou "
    "WebSocket pour les intégrations partenaires — permet des sessions de traduction interactive "
    "à moins de cinq secondes de latence. La détection de fin de phrase s'appuie sur Silero VAD, "
    "déjà intégré au pipeline, qui segmente le flux audio entrant en fenêtres de 32 ms et "
    "déclenche chaque cycle de traduction dès la fin d'une phrase, sans intervention de "
    "l'utilisateur. L'utilisateur choisit son dialecte cible et s'exprime dans l'une des six "
    "langues source. Le système transcrit, traduit et synthétise vocalement la réponse en une "
    "seule requête unifiée.\n\n"
    "Le développement applicatif comprend également un tableau de bord de monitoring de qualité "
    "en production, un mécanisme de feedback utilisateur intégré qui alimente directement les "
    "cycles de réentraînement, et des outils de suivi des dialectes les plus sollicités. Cette "
    "boucle entre l'usage réel et l'amélioration des modèles garantit que le système progressera "
    "en conditions opérationnelles.")

# ── Q10 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 10 — Livrables et apprentissages attendus (500 mots max)")
para(doc,
    "Les livrables du projet s'articulent en trois catégories : les ressources linguistiques "
    "ouvertes, les modèles et outils open-source, et l'impact communautaire documenté.\n\n"
    "En matière de ressources linguistiques, le projet produira et publiera dix-huit corpus audio "
    "dialectaux couvrant l'ensemble des variétés régionales du malgache, soit un total estimé de "
    "2 500 à 3 000 heures d'enregistrement vocal transcrit et validé. Ces corpus seront publiés "
    "sur HuggingFace et déposés dans Common Voice sous licence Creative Commons BY 4.0.\n\n"
    "En matière de modèles et d'outils, le projet publiera sur github.com/mgvaovao/ml et "
    "HuggingFace les adaptateurs LoRA affinés de NLLB-200 pour dix-huit dialectes malgaches sous "
    "licence Apache 2.0, les checkpoints MMS-TTS-MLG VITS pour dix-huit dialectes également sous "
    "Apache 2.0, les scripts d'affinement reproductibles avec documentation complète, un benchmark "
    "d'évaluation dialectal malgache avec jeux de test hold-out et métriques de référence, ainsi "
    "qu'une API publique documentée sur github.com/mgvaovao/backend_ia.\n\n"
    "Sur le plan de l'impact communautaire, le projet documentera le nombre de sessions "
    "d'utilisation du système à la Maison du Numérique avec un objectif de 2 000 sessions sur "
    "douze mois, le nombre de locuteurs natifs ayant participé à la collecte avec un objectif de "
    "500 personnes réparties sur quatorze régions, ainsi que les résultats des évaluations de "
    "satisfaction et d'intelligibilité menées auprès des utilisateurs.\n\n"
    "Les apprentissages clés porteront sur les conditions minimales de données nécessaires pour "
    "un affinement de modèles TTS et MT de qualité déployable sur des dialectes à très faibles "
    "ressources, les meilleures pratiques pour la collecte de données vocales communautaires dans "
    "des contextes ruraux africains, et une analyse comparative des performances des modèles sur "
    "dix-huit variétés dialectales. Toutes ces connaissances seront publiées dans un rapport "
    "technique final partagé avec la communauté Masakhane, en français et en anglais.")

# ── Q11 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 11 — Calendrier et jalons (400 mots max)")
para(doc,
    "Le projet est planifié sur une durée de dix-huit mois, structurée en trois phases "
    "successives.\n\n"
    "Phase 1 — Mise en place et lancement (Mois 1 à 4) : recrutement et formation des quatorze "
    "coordinateurs locaux, finalisation des protocoles de consentement et des textes de collecte "
    "dans chaque dialecte, établissement des partenariats avec les antennes régionales, lancement "
    "des sessions d'enregistrement pour les cinq premiers dialectes prioritaires, à savoir "
    "l'antandroy, le tsimihety, le vezo, le bara et le sihanaka. Livrable de fin de phase : "
    "infrastructure de collecte opérationnelle et premiers affinements en cours sur Vertex AI.\n\n"
    "Phase 2 — Production principale (Mois 5 à 12) : collecte des données pour les neuf dialectes "
    "restants, affinement des modèles NLLB et MMS-TTS pour l'ensemble des dix-huit dialectes, "
    "évaluation automatique et humaine de chaque modèle dialectal, déploiement progressif des "
    "dialectes validés. Jalon M8 : dix premiers dialectes affinés, évalués et déployés. "
    "Jalon M12 : dix-huit dialectes affinés et en cours d'évaluation communautaire, "
    "1 000 sessions d'utilisation documentées.\n\n"
    "Phase 3 — Consolidation, publication et transfert (Mois 13 à 18) : sessions d'évaluation "
    "communautaire finales, réentraînements ciblés, publication intégrale des ressources sur "
    "HuggingFace et GitHub, organisation d'un atelier de restitution ouvert à la communauté NLP "
    "africaine, rédaction du rapport technique final. Livrable final M18 : dix-huit dialectes "
    "opérationnels, tous les corpus et modèles publiés, 2 000 sessions d'utilisation documentées "
    "et rapport technique final soumis à la communauté Masakhane.")

# ── Q12 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 12 — Éthique, inclusion et gouvernance des données (500 mots max)")
para(doc,
    "La dimension éthique est au cœur de la conception de MGVaovao et non une considération "
    "secondaire.\n\n"
    "Sur le consentement et la protection des locuteurs, chaque participant signe un formulaire "
    "de consentement éclairé disponible en malgache officiel et dans la variété dialectale de la "
    "région de collecte. Ce formulaire explique la nature des données collectées, leur usage prévu, "
    "la licence CC BY 4.0 sous laquelle elles seront publiées, ainsi que le droit de retrait à "
    "tout moment avant la publication. Les mineurs ne participent qu'avec le consentement écrit "
    "d'un parent ou tuteur.\n\n"
    "Sur l'inclusion et la représentation, le protocole de collecte impose une parité de genre : "
    "au minimum 50 % des locuteurs enregistrés dans chaque dialecte sont des femmes. La diversité "
    "d'âge est prise en compte avec trois tranches couvrant les 18 à 35 ans, les 36 à 55 ans et "
    "les 55 ans et plus. Les coordinateurs locaux sont eux-mêmes membres des communautés ciblées. "
    "L'engagement de la Maison du Numérique pour l'inclusion va au-delà du genre et de l'âge : "
    "l'organisation conduit déjà un programme spécifique d'inclusion numérique pour les enfants "
    "atteints de trisomie 21, ce qui témoigne de façon tangible que l'équité et l'inclusion sont "
    "des pratiques quotidiennes documentées et non de simples déclarations d'intention.\n\n"
    "Sur les licences et l'ouverture, tous les livrables produits sont publiés sous des licences "
    "pleinement ouvertes : Apache 2.0 pour les modèles et le code, Creative Commons BY 4.0 pour "
    "les données.\n\n"
    "Sur l'impact environnemental, le projet optimise délibérément son empreinte de calcul via "
    "l'utilisation de modèles distillés, la quantification INT8, le fine-tuning LoRA et une "
    "infrastructure de production à scale-to-zero éliminant la consommation d'énergie en dehors "
    "des périodes d'utilisation active.\n\n"
    "Sur la gouvernance des données, les données collectées sont stockées sur GCS avec chiffrement "
    "au repos et accès restreint à l'équipe du projet. Fenitra Ravelomanantsoa, en tant que "
    "juriste spécialisé en droit numérique et Directeur des affaires juridiques et réglementaires "
    "Cloud chez Google, garantit personnellement la conformité du projet avec les standards "
    "internationaux de protection des données. Cette expertise de directeur au sein d'une des "
    "principales entreprises technologiques mondiales est rare dans les projets de données "
    "africaines et constitue un atout distinctif de cette candidature.")

# ── Q13 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 13(a) — Candidature en consortium ?")
para(doc,
    "Non. MGVaovao - Maison du Numérique (Madagasikara Vaovao) soumet cette proposition en tant "
    "qu'organisation principale. Le projet s'appuie sur un réseau de partenaires opérationnels "
    "établis, à savoir Telma Madagascar, Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et "
    "ANKY, mais ceux-ci interviennent comme partenaires et non comme co-candidats formels. Des "
    "lettres de soutien peuvent être fournies sur demande.")

# ── Q14 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 14 — Lettres de soutien et documentation complémentaire")
para(doc,
    "Des lettres de soutien peuvent être sollicitées auprès des partenaires opérationnels de la "
    "Maison du Numérique, notamment Telma Madagascar pour les programmes E-JERY et HOLI DEV, "
    "Sayna, CoderDojo Antananarivo, STEM4Good Madagascar et ANKY. Ces partenariats sont actifs "
    "et documentés depuis l'inauguration de la Maison du Numérique en février 2024.\n\n"
    "La documentation complémentaire du projet est accessible directement dans les dépôts publics "
    "GitHub. Le dépôt github.com/mgvaovao/ml contient le fichier README détaillé décrivant "
    "l'architecture complète du pipeline, les instructions de reproduction de l'affinement, les "
    "métriques d'évaluation obtenues et la structure des données, ainsi qu'un fichier "
    "MGVaovao_Architecture_Complete.md qui documente l'ensemble des choix architecturaux, des "
    "dépendances et du flux de données. Le dépôt github.com/mgvaovao/backend_ia contient de même "
    "un README complet et la documentation de l'API. L'ensemble de ces ressources est publié "
    "sous licence Apache 2.0.")

# ── Q15 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 15 — Membres de l'équipe et rôles (400 mots max)")

subh(doc, "Fenitra Ravelomanantsoa — Fondateur et Directeur général de MGVaovao - Maison du Numérique")
para(doc,
    "Juriste de formation et Directeur des affaires juridiques et réglementaires Cloud (Head of "
    "Cloud Regulatory) chez Google à Zurich, Fenitra occupe un poste de direction dans l'une des "
    "principales entreprises technologiques mondiales, où il supervise la conformité réglementaire "
    "des infrastructures cloud à l'échelle internationale. Après plus de 20 ans de carrière "
    "internationale à Paris, Barcelone, Londres et Zurich, il a fondé l'association Madagasikara "
    "Vaovao et MGVaovao - Maison du Numérique en novembre 2023, convaincu que son expertise en "
    "gouvernance des technologies, protection des données et compliance cloud pouvait bénéficier "
    "directement à son pays. Il supervise la stratégie globale, les partenariats institutionnels "
    "et la gouvernance éthique du projet.")

subh(doc, "Norolala Randrianarison — Directrice locale et Responsable des opérations")
para(doc,
    "Professionnelle du secteur des télécommunications et du numérique à Madagascar, Mme Noro "
    "assure la direction opérationnelle de la Maison du Numérique au quotidien. Elle supervise "
    "l'accueil des communautés, le déploiement des programmes, la coordination des bénévoles et "
    "la relation avec les partenaires institutionnels locaux.")

subh(doc, "Guillaume Rakotonjanahary Tsantaniaina — Chef de projet technique — ML et Développement")
para(doc,
    "Ingénieur AI/ML avec plus de cinq ans d'expérience dans des systèmes de production en "
    "Speech AI, NLP et infrastructure cloud GCP, Guillaume est titulaire d'un Master en Big Data "
    "et IA de l'ESTIA (France), obtenu avec mention Très Bien (17,2/20). En tant que chef de "
    "projet technique, il prend en charge le volet ML et développement du pipeline : architecture "
    "des modèles, affinement NLLB et MMS-TTS, déploiement sur Cloud Run GPU et orchestration "
    "MLOps sur Vertex AI. Au cours de ses cinq années d'expérience, il a développé une gamme "
    "étendue de systèmes IA : pipelines Speech AI complets (ASR, traduction neuronale, synthèse "
    "vocale), systèmes multi-agents LLM avec LangGraph et Google ADK, architectures RAG hybrides "
    "(vectoriel, graphe, multimodal), modèles de vision par ordinateur (YOLO V8, CLIP, SAM), "
    "plateformes de santé numérique et infrastructures MLOps sur Vertex AI. Locuteur natif du "
    "malgache et du français, il apporte une compréhension intime des nuances dialectales. "
    "Lauréat d'IndabaX Madagascar 2023 (3e place, classification NLP médicale à 94 % de "
    "précision) et participant au DataTour 2025 (compétition pan-africaine, modèles de "
    "recommandation et de scoring crédit), il est actif dans l'écosystème IA africain.")

subh(doc, "Karine Maholisoa Rajaofera — Chef de projet Data, Opérations et Fonctionnel")
para(doc,
    "Titulaire d'un Bachelor en Business Management, Karine apporte dix ans d'expérience dans "
    "les opérations de données, la collecte à grande échelle et la coordination terrain. "
    "Spécialiste des données et experte en lidar chez SmartOne.ai, elle a conduit des projets "
    "de collecte, d'annotation et de validation de données en conditions réelles sur une décennie. "
    "Elle rejoint MGVaovao - Maison du Numérique en septembre 2025 et pilote depuis lors le "
    "programme d'IA sur les dialectes malgaches en tant que chef de projet principal. Elle "
    "supervise le cycle complet de collecte vocale dans les quatorze régions dialectales, définit "
    "les protocoles d'annotation, assure le contrôle qualité des transcriptions, coordonne les "
    "équipes terrain et traduit les besoins métier en spécifications fonctionnelles pour le "
    "pipeline technique. Maîtrisant les outils bureautiques et collaboratifs tels que Word, "
    "Excel, Google Sheets et l'ensemble des plateformes Google, elle assure l'interface entre "
    "les réalités opérationnelles du terrain et le volet technique. Elle pilote également le "
    "programme d'inclusion numérique des enfants atteints de trisomie 21 à la Maison du Numérique.")

subh(doc, "Chef de projet partenariats et impact (à recruter) · Coordinateurs locaux (14, à recruter)")
para(doc,
    "Un troisième chef de projet dédié aux partenariats institutionnels et à la mesure d'impact "
    "sera recruté en début de projet sur fonds LINGUA Africa. Un coordinateur de terrain sera "
    "recruté pour chacun des quatorze dialectes à couvrir, au sein des communautés locutrices, "
    "de préférence des femmes.")

# ── Q16 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 16 — Travaux antérieurs et références (300 mots max)")
para(doc,
    "Ce projet s'inscrit dans une trajectoire de recherche et de développement cohérente dont "
    "les jalons antérieurs établissent à la fois sa faisabilité et son originalité.\n\n"
    "MGVaovao - Maison du Numérique, fondée en novembre 2023, opère depuis son inauguration en "
    "février 2024. C'est sur cette base institutionnelle solide que le projet de traduction "
    "speech-to-speech en dialectes malgaches a été lancé fin 2025, après une phase préliminaire "
    "d'évaluation des architectures ASR et TTS existantes pour les langues à faibles ressources, "
    "notamment Whisper, Chirp de Vertex AI Studio et les architectures VITS, qui a permis "
    "d'établir la méthodologie d'adaptation par transfert aujourd'hui au cœur du pipeline.\n\n"
    "Ce prototype de traduction parole-vers-parole est opérationnel depuis avril 2026 pour quatre "
    "dialectes, à savoir le malgache officiel, le betsileo, le betsimisaraka et le sakalava, avec "
    "une latence de bout en bout inférieure à cinq secondes. Il constitue un premier résultat "
    "concret à améliorer et à étendre, non un système finalisé. Environ 1 000 paires de données "
    "ont déjà été constituées, ce qui démontre la capacité opérationnelle de l'équipe à collecter "
    "et traiter des données dialectales réelles.\n\n"
    "Sur le plan académique, le projet s'appuie sur les travaux fondateurs de la communauté "
    "Masakhane, sur les publications de l'équipe NLLB de Costa-jussà et al. (2022) pour la "
    "traduction multilingue, sur les travaux de Pratap et al. (2023) sur MMS pour la synthèse "
    "vocale multilingue, et sur les avancées en reconnaissance automatique de la parole pour "
    "les langues sous-dotées.\n\n"
    "La Maison du Numérique apporte une base communautaire documentée et vérifiable : 5 000 "
    "personnes formées depuis l'inauguration de février 2024, 550 utilisateurs mensuels actifs, "
    "et des partenariats opérationnels établis avec Telma Madagascar, Sayna, CoderDojo "
    "Antananarivo, STEM4Good Madagascar et ANKY.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Budget — Question 17")

qlabel(doc, "Question 17(b) — Tableau récapitulatif du budget")
btable(doc, [
    ("1. Personnel — direction permanente (5 postes)",              "144 900"),
    ("2. Équipement et logiciels",                                    "8 000"),
    ("3. Collecte terrain — 54 collecteurs × 133 USD × 4 mois",     "28 728"),
    ("4. Annotation ground truth — 36 annotateurs × 200 USD × 4 mois", "28 800"),
    ("5. Déplacements et terrain",                                   "16 000"),
    ("6. Ateliers, réunions et formation",                            "4 500"),
    ("7. Communication et sensibilisation",                           "1 500"),
    ("8. Autres coûts directs",                                       "1 000"),
    ("Total des coûts directs",                                    "233 428"),
    ("9. Frais généraux / Coûts indirects (5 %)",                   "11 671"),
    ("Grand Total",                                                "245 099"),
])
para(doc,
    "Co-financement organisation (hors budget LINGUA Africa) : 8 développeurs "
    "(backend, frontend, IA, data science, DevOps) × 333 USD (1 500 000 MGA) × 18 mois "
    "= 47 952 USD.")

doc.add_paragraph()
qlabel(doc, "Question 17(c) — Justification du budget (300 mots max)")
para(doc,
    "Le budget proposé de 245 099 USD reflète fidèlement les activités planifiées et les coûts "
    "réels du contexte malgache, en restant en dessous du plafond de 250 000 USD prévu "
    "pour la Catégorie 3.\n\n"
    "Le poste personnel (144 900 USD) couvre l'équipe de direction permanente sur dix-huit mois : "
    "le fondateur en conseil stratégique à mi-temps (22 500 USD), la directrice locale à temps "
    "plein (36 000 USD), le Chef de projet technique ML (32 400 USD), la Chef de projet Data et "
    "Opérations (32 400 USD) et un chef de projet partenariats démarrant au mois 7 (21 600 USD). "
    "L'équipe technique de huit développeurs — backend, frontend, IA, data scientists et DevOps — "
    "constitue un apport de l'organisation de 47 952 USD (1 500 000 MGA × 18 mois × 8 personnes), "
    "non inclus dans la demande LINGUA Africa.\n\n"
    "Le poste collecte terrain (28 728 USD) rémunère 54 collecteurs — trois par dialecte — "
    "à 133 USD/mois (600 000 MGA) sur quatre mois actifs de collecte intensive.\n\n"
    "Le poste annotation et vérification (28 800 USD) rémunère 36 annotateurs-transcripteurs "
    "— deux par dialecte — à 200 USD/mois (900 000 MGA) sur quatre mois de ground truth.\n\n"
    "Le poste équipement et logiciels (8 000 USD) couvre six ordinateurs portables et le matériel "
    "d'enregistrement terrain. Les déplacements (16 000 USD) couvrent les dix-huit régions "
    "dialectales. Les ateliers (4 500 USD) financent la formation des équipes terrain, un atelier "
    "de restitution et une conférence. Les frais généraux sont limités à 5 % (11 671 USD).")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# RESSOURCES DE CALCUL
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Ressources de calcul — Question 18")

qlabel(doc, "Question 18(a) — Besoin en ressources de calcul ?")
para(doc, "Oui.")

qlabel(doc, "Question 18(b) — Montant demandé en ressources de calcul")
para(doc, "150 000 USD en crédits de calcul GCP (sur un maximum de 400 000 USD pour la Catégorie 3).")

qlabel(doc, "Question 18(c) — Usage des ressources de calcul (300 mots max)")
para(doc,
    "Les crédits de calcul GCP demandés (150 000 USD) seront répartis sur trois composantes de "
    "l'architecture technique du projet.\n\n"
    "La part principale, soit environ 80 000 USD, sera allouée aux travaux d'affinement des "
    "modèles sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot à environ 0,28 USD de "
    "l'heure. Ces crédits couvrent les runs de fine-tuning NLLB LoRA pour les six langues source "
    "et les dix-huit dialectes, en incluant les cycles d'expérimentation, d'optimisation des "
    "hyperparamètres et de réentraînement sur nouvelles données, ainsi que l'affinement MMS-TTS "
    "pour chaque dialecte.\n\n"
    "Une part significative, soit environ 45 000 USD, sera allouée à l'infrastructure de "
    "production. Elle couvre Cloud Run GPU avec un NVIDIA L4 pour l'hébergement de l'API MGVaovao "
    "sur dix-huit mois, avec une capacité de trois à cinq sessions WebRTC concurrentes et "
    "scale-to-zero en dehors des heures d'utilisation.\n\n"
    "La partie restante, environ 25 000 USD, couvrira les pipelines d'orchestration et "
    "d'évaluation automatique via Vertex AI Pipelines, le stockage GCS des corpus audio et "
    "checkpoints pour un volume d'environ 3 To, les services d'intégration continue et de "
    "monitoring ainsi que le traitement des données dans les pipelines d'ingestion.\n\n"
    "L'ensemble de l'architecture est conçu avec une philosophie de frugalité : les instances "
    "Spot réduisent le coût du fine-tuning jusqu'à 70 % par rapport aux instances à la demande, "
    "les modèles sont distillés et quantifiés pour la production, et le scale-to-zero élimine "
    "la consommation en dehors des heures d'utilisation active.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# SUPPORT TECHNIQUE
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Support technique — Question 19")

qlabel(doc, "Question 19(a) — Besoin en support technique ?")
para(doc, "Oui.")

qlabel(doc, "Question 19(b) — Nature du support technique souhaité (300 mots max)")
para(doc,
    "Le soutien technique sollicité porte sur trois domaines complémentaires à l'expertise "
    "interne de l'équipe.\n\n"
    "Le premier domaine est la linguistique computationnelle appliquée aux dialectes malgaches. "
    "La diversité dialectale du malgache soulève des questions spécialisées, notamment la "
    "définition des orthographes de référence pour les dialectes non standardisés, la gestion "
    "des variations phonologiques intradialectales et les protocoles d'annotation adaptés aux "
    "langues à tradition principalement orale. Un accès à des experts en linguistique descriptive "
    "des langues malagasyphones, via le réseau d'academic fellows de LINGUA Africa, serait "
    "directement utile.\n\n"
    "Le deuxième domaine est l'évaluation humaine à grande échelle. Mettre en place des panels "
    "de locuteurs natifs de dix-huit dialectes distincts avec des protocoles d'évaluation "
    "standardisés est une démarche que l'équipe mène pour la première fois à cette échelle. Un "
    "accompagnement méthodologique de chercheurs ayant une expérience dans l'évaluation de "
    "systèmes de parole pour langues africaines serait très précieux.\n\n"
    "Le troisième domaine est la mise en réseau avec d'autres projets de l'écosystème LINGUA "
    "Africa travaillant sur des problématiques similaires, telles que les langues insulaires "
    "africaines, les dialectes régionaux et les langues à tradition orale. Un accès structuré "
    "aux communautés de pratique Masakhane permettrait à l'équipe de bénéficier des "
    "apprentissages d'autres projets et de contribuer en retour avec ses propres résultats sur "
    "le malgache.")

# ═══════════════════════════════════════════════════════════════════════════════
# NOTES DE RÉDACTION
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
h1(doc, "Notes avant soumission")

note(doc,
    "NOTE 1 — GitHub public : avant soumission, rendez le dépôt github.com/mgvaovao/ml public "
    "et ajoutez un fichier LICENSE (Apache 2.0). Vérifiez que MGVaovao_Architecture_Complete.md "
    "est bien présent dans le dépôt.")
note(doc,
    "NOTE 2 — Budget détaillé (Q17a) : le formulaire requiert un fichier Excel séparé "
    "(LINGUA_Africa_Budget_Detaille.xlsx). Téléversez-le sur Submittable lors de la soumission.")
note(doc,
    "NOTE 3 — Lettres de soutien (Q14) : préparez des lettres de soutien de Telma et/ou Sayna. "
    "Ces lettres renforceront significativement le dossier.")
note(doc,
    "NOTE 4 — Compte de mots : chaque réponse a été rédigée sous le plafond indiqué. "
    "Vérifiez le compte dans Word (Révision > Statistiques) avant soumission.")
note(doc,
    "NOTE 5 — Q9 longueur : la section méthodologie dépasse légèrement 1 000 mots avec le "
    "quatrième pilier. Résumez si le formulaire impose un comptage strict.")

output_path = r"C:\mgvaovao\LINGUA_Africa_Candidature_MGVaovao.docx"
doc.save(output_path)
print(f"Fichier sauvegardé : {output_path}")
