# -*- coding: utf-8 -*-
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

def rf(run, bold=False, size=11, color=None, italic=False):
    run.bold = bold; run.italic = italic
    run.font.size = Pt(size); run.font.name = "Calibri"
    if color: run.font.color.rgb = RGBColor(*color)

def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text.upper())
    rf(run, bold=True, size=14, color=(31, 78, 121))
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), '8')
    bot.set(qn('w:space'), '1');   bot.set(qn('w:color'), '1F4E79')
    pBdr.append(bot); pPr.append(pBdr)

def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    rf(p.add_run(text), bold=True, size=12, color=(0, 70, 127))

def body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.left_indent  = Cm(0.3)
    rf(p.add_run(text), size=11)

def bullet(doc, label, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Cm(0.8)
    r1 = p.add_run(label + " ")
    rf(r1, bold=True, size=11)
    r2 = p.add_run(text)
    rf(r2, size=11)

def divider(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(6)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), '4')
    bot.set(qn('w:space'), '1');   bot.set(qn('w:color'), 'AAAAAA')
    pBdr.append(bot); pPr.append(pBdr)

def lang_banner(doc, text, color):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(10)
    rf(p.add_run(text), bold=True, size=13, color=color)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE DE TITRE
# ─────────────────────────────────────────────────────────────────────────────
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(30)
rf(p.add_run("MGVaovao — Maison du Numérique"), bold=True, size=22, color=(31, 78, 121))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Madagasikara Vaovao · Antananarivo, Madagascar"), size=13, color=(80, 80, 80))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
rf(p.add_run("Description du projet / Project Description"), bold=True, size=14, color=(0, 70, 127), italic=True)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Traduction parole-vers-parole en temps réel — 18 dialectes malgaches"), size=12, italic=True, color=(100, 100, 100))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf(p.add_run("Real-Time Speech-to-Speech Translation — 18 Malagasy Dialects"), size=12, italic=True, color=(100, 100, 100))

doc.add_page_break()

# ═════════════════════════════════════════════════════════════════════════════
# VERSION FRANÇAISE
# ═════════════════════════════════════════════════════════════════════════════
lang_banner(doc, "— VERSION FRANÇAISE —", (31, 78, 121))

h1(doc, "MGVaovao — Traduction parole-vers-parole en temps réel en dialectes malgaches")

h2(doc, "Vue d'ensemble")
body(doc,
    "MGVaovao - Maison du Numérique (programme de l'association Madagasikara Vaovao) développe, "
    "depuis Antananarivo, une infrastructure d'intelligence artificielle ouverte permettant la "
    "traduction automatique parole-vers-parole en temps réel à destination de dix-huit dialectes "
    "malgaches. Ce projet constitue la première initiative au monde à créer des ressources "
    "linguistiques vocales ouvertes pour l'ensemble du continuum dialectal du malgache, une "
    "langue parlée par plus de 28 millions de personnes.")

divider(doc)
h2(doc, "Contexte et problème adressé")
body(doc,
    "Madagascar est une île-continent d'une richesse linguistique exceptionnelle. Si le malgache "
    "compte parmi les quarante langues africaines les plus parlées, cette réalité dissimule une "
    "fragmentation dialectale profonde : dix-huit dialectes régionaux vivants, notamment le betsileo, "
    "le betsimisaraka, le sakalava, l'antandroy, le tsimihety, le vezo, le bara, le sihanaka, l'antakarana, le makoa, "
    "l'antaisaka et sept autres, coexistent sur l'ensemble du territoire national. Ces variétés "
    "diffèrent phonologiquement et lexicalement au point de constituer de véritables barrières "
    "de communication entre communautés.")
body(doc,
    "Le malgache officiel (variété Merina) est la seule forme disposant d'une présence minimale "
    "dans les systèmes d'intelligence artificielle existants. Aucun des dix-sept dialectes "
    "régionaux n'est représenté dans les grandes bases de données multilingues telles que Common "
    "Voice, FLORES-200 ou OPUS. Cette absence prive des millions de locuteurs d'un accès équitable "
    "aux services éducatifs, sanitaires et civiques disponibles sous forme numérique. Lorsqu'un "
    "agriculteur betsileo cherche des informations sur des semences résistantes à la sécheresse, "
    "ou qu'une mère betsimisaraka souhaite comprendre des consignes de santé maternelle, les outils "
    "numériques disponibles ne parlent pas leur langue.")
body(doc,
    "À ce jour, moins de dix travaux académiques publiés traitent du traitement automatique du "
    "malgache dans sa diversité dialectale.")

divider(doc)
h2(doc, "Solution développée")
body(doc,
    "Le système développé par MGVaovao est un pipeline de traduction parole-vers-parole en cascade, "
    "composé de quatre modules complémentaires et optimisés pour les contraintes du contexte "
    "africain, notamment la latence minimale, le coût de calcul maîtrisé et l'adaptabilité aux données en faible volume.")
bullet(doc, "Module 1 — Détection d'activité vocale :",
    "Basé sur Silero VAD v5, ce modèle léger de 2 Mo fonctionne en CPU sur des fenêtres de "
    "32 millisecondes. Il filtre les segments de silence avant traitement et réduit les coûts "
    "de calcul de 30 à 50 % sur des enregistrements réels.")
bullet(doc, "Module 2 — Reconnaissance automatique de la parole (ASR) :",
    "Fondé sur Whisper large-v3-turbo quantifié en INT8 via CTranslate2, ce module prend en "
    "charge 99 langues d'entrée, dont le français, l'anglais, l'allemand, l'espagnol, l'italien "
    "et le portugais. La quantification INT8 offre une vitesse deux fois supérieure au modèle "
    "FP16 original pour une empreinte VRAM d'environ 1,7 Go.")
bullet(doc, "Module 3 — Traduction neuronale :",
    "Basé sur NLLB-200-distilled-600M, affiné par apprentissage par transfert via LoRA (rang 16, "
    "PEFT) pour chaque paire de langues source vers le malgache officiel (plt_Latn). L'affinement "
    "est conduit sur Vertex AI Custom Training avec des GPU NVIDIA L4 Spot, produisant une "
    "amélioration mesurée de 2 à 8 points de chrF++ par rapport au modèle de base.")
bullet(doc, "Module 4 — Synthèse vocale dialectale (TTS) :",
    "Basé sur MMS-TTS-MLG VITS de Meta, affiné par dialecte à partir de 80 à 150 échantillons "
    "audio de haute qualité, en une à deux heures sur GPU, via le framework ylacombe/finetune-hf-vits. "
    "Chaque checkpoint dialectal est versionné avec ses métadonnées d'évaluation.")
body(doc,
    "L'ensemble du pipeline est exposé via une API FastAPI déployée sur Google Cloud Run GPU "
    "(NVIDIA L4, 24 Go), avec une latence de bout en bout inférieure à cinq secondes et une "
    "empreinte VRAM totale de 6,2 Go permettant trois à cinq sessions concurrentes par instance.")
body(doc,
    "État d'avancement actuel : Un premier proof of concept couvrant quatre dialectes (malgache "
    "officiel, betsileo, betsimisaraka, sakalava) est opérationnel depuis avril 2026. Environ "
    "1 000 paires de données ont déjà été constituées depuis le lancement fin 2025.")

divider(doc)
h2(doc, "Données et ressources linguistiques")
body(doc,
    "La composante de création de données est au cœur du projet. Pour chaque dialecte cible, le "
    "protocole vise la constitution d'un corpus initial de 150 à 200 heures de parole naturelle "
    "et 10 000 paires audio-transcription de haute qualité. Les données sont collectées par des "
    "coordinateurs locaux recrutés au sein des communautés elles-mêmes, de préférence des femmes, "
    "formés au protocole de collecte et rémunérés équitablement.")
body(doc,
    "Toutes les ressources produites sont publiées intégralement sous licences ouvertes : Apache 2.0 "
    "pour les modèles et le code, Creative Commons BY 4.0 pour les données audio et les "
    "transcriptions. Elles sont déposées sur HuggingFace et dans Mozilla Common Voice, garantissant "
    "leur réutilisation par l'ensemble de la communauté de recherche en NLP africain.")

divider(doc)
h2(doc, "Impact communautaire et ancrage local")
body(doc,
    "MGVaovao - Maison du Numérique est un centre numérique communautaire physique, inauguré en "
    "février 2024 à Ambatonakanga, Antananarivo, sur un modèle philanthropique unique : financé "
    "exclusivement sur les fonds propres du fondateur, l'accès à l'ensemble des programmes est "
    "entièrement gratuit (0 ariary) pour tous les bénéficiaires.")
body(doc,
    "Depuis son inauguration, le centre a accueilli plus de 5 500 bénéficiaires uniques "
    "(48 % de femmes, de 7 à 65 ans) et a accompagné 2 366 personnes formées à travers ses "
    "programmes partenaires :")
bullet(doc, "e-jery :", "programme d'inclusion numérique pour les enfants vulnérables (1 483 personnes formées)")
bullet(doc, "ANKY :", "formation en développement personnel et entrepreneuriat (472 personnes formées)")
bullet(doc, "Madagascar DataCamp :", "formation Excel de base pour les étudiants (411 personnes formées)")
bullet(doc, "YAS Madagascar :", "programme Ampela Online pour l'entrepreneuriat féminin en ligne")
bullet(doc, "Down Syndrome Madagascar :", "programme d'inclusion numérique pour 28 enfants porteurs de trisomie 21")
body(doc,
    "Le centre s'appuie sur une communauté de plus de 26 bénévoles actifs et dispose de "
    "partenariats établis sur l'ensemble du territoire national.")
body(doc,
    "MGVaovao - Maison du Numérique a été nominée au prix RSE de l'Année 2026 lors de la "
    "2e édition du CEO Summit Indian Ocean (avril 2026), une reconnaissance externe de "
    "l'impact social de l'organisation.")

divider(doc)
h2(doc, "Cas d'usage concrets")
bullet(doc, "Éducation :",
    "Le système permet aux formateurs de s'adresser aux apprenants dans leur variété linguistique "
    "maternelle, améliorant la compréhension et l'engagement dans les programmes d'alphabétisation "
    "numérique et d'éducation spécialisée. Une borne interactive déployée dans les locaux de la "
    "Maison du Numérique permet à toute personne de s'exprimer en français, anglais ou autre "
    "langue prise en charge, et de recevoir immédiatement une réponse audio dans son dialecte.")
bullet(doc, "Inclusion civique :",
    "Des citoyens non locuteurs du malgache officiel peuvent accéder à des informations sur les "
    "services publics, les droits civiques et les procédures administratives dans leur dialecte. "
    "Ce besoin est particulièrement aigu dans les zones rurales où les barrières linguistiques "
    "constituent le premier obstacle à l'accès à l'information.")
bullet(doc, "API publique :",
    "Une API documentée et accessible permet à des partenaires institutionnels tels que les services de "
    "santé communautaire, les associations d'alphabétisation, les ONG et les organisations d'appui social "
    "d'intégrer la capacité de communication dialectale dans leurs propres outils.")

divider(doc)
h2(doc, "Ouverture et reproductibilité")
body(doc,
    "L'intégralité du code source, des scripts d'affinement et de la documentation technique est "
    "publiée sous licence Apache 2.0 sur :")
bullet(doc, "github.com/mgvaovao-Mdn/ml :", "pipeline ML, modèles, scripts d'affinement")
bullet(doc, "github.com/mgvaovao-Mdn/backend_ia :", "API, documentation technique")
body(doc,
    "Les corpus audio dialectaux seront déposés sur HuggingFace et dans Mozilla Common Voice "
    "sous Creative Commons BY 4.0, constituant les premières ressources linguistiques vocales "
    "ouvertes pour le malgache dialectal.")

divider(doc)
h2(doc, "Informations sur l'organisation")
bullet(doc, "Nom légal :", "Madagasikara Vaovao")
bullet(doc, "Nom commercial :", "Maison du Numérique / MGVaovao")
bullet(doc, "Type :", "Association à but non lucratif")
bullet(doc, "Siège :", "Antananarivo, Madagascar")
bullet(doc, "Site web :", "https://mgvaovao.com")
bullet(doc, "Email :", "contact@mgvaovao.com")

# ═════════════════════════════════════════════════════════════════════════════
# SÉPARATEUR DE LANGUE
# ═════════════════════════════════════════════════════════════════════════════
doc.add_page_break()

# ═════════════════════════════════════════════════════════════════════════════
# ENGLISH VERSION
# ═════════════════════════════════════════════════════════════════════════════
lang_banner(doc, "— ENGLISH VERSION —", (0, 70, 127))

h1(doc, "MGVaovao — Real-Time Speech-to-Speech Translation into Malagasy Dialects")

h2(doc, "Overview")
body(doc,
    "MGVaovao - Maison du Numérique (a programme of the Madagasikara Vaovao association) is "
    "developing, from Antananarivo, an open artificial intelligence infrastructure enabling "
    "automated real-time speech-to-speech translation into eighteen Malagasy dialects. This "
    "project constitutes the first initiative worldwide to create open vocal linguistic resources "
    "for the full dialectal continuum of Malagasy, a language spoken by over 28 million people.")

divider(doc)
h2(doc, "Context and Problem Statement")
body(doc,
    "Madagascar is an island-continent of exceptional linguistic richness. While Malagasy ranks "
    "among the forty most widely spoken African languages, this recognition conceals a profound "
    "dialectal fragmentation: eighteen living regional dialects, including Betsileo, Betsimisaraka, "
    "Sakalava, Antandroy, Tsimihety, Vezo, Bara, Sihanaka, Antakarana, Makoa, Antaisaka, and "
    "seven others, coexist across the national territory. These varieties differ phonologically "
    "and lexically to the point of creating genuine communication barriers between communities.")
body(doc,
    "Official Malagasy (the Merina variety) is the only form with even a minimal presence in "
    "existing AI systems. None of the seventeen regional dialects are represented in major "
    "multilingual datasets such as Common Voice, FLORES-200, or OPUS. This absence denies "
    "millions of speakers equitable access to educational, health, and civic services available "
    "in digital form. When a Betsileo farmer searches for information on drought-resistant seeds, "
    "or a Betsimisaraka mother tries to understand maternal health guidelines, the available "
    "digital tools do not speak their language.")
body(doc,
    "To date, fewer than ten published academic works address the computational processing of "
    "Malagasy in its dialectal diversity.")

divider(doc)
h2(doc, "Solution Developed")
body(doc,
    "The system developed by MGVaovao is a speech-to-speech cascade pipeline composed of four "
    "complementary modules, each optimised for the constraints of the African context, "
    "namely minimal latency, controlled compute cost, and adaptability to low-volume data.")
bullet(doc, "Module 1 — Voice Activity Detection:",
    "Based on Silero VAD v5, this lightweight 2 MB model runs on CPU in 32-millisecond windows. "
    "It filters silence segments before processing and reduces compute costs by 30 to 50 percent "
    "on real-world recordings.")
bullet(doc, "Module 2 — Automatic Speech Recognition (ASR):",
    "Based on Whisper large-v3-turbo quantised to INT8 via CTranslate2, this module supports "
    "99 input languages, including French, English, German, Spanish, Italian, and Portuguese. "
    "INT8 quantisation delivers twice the inference speed of the original FP16 model at "
    "approximately 1.7 GB VRAM.")
bullet(doc, "Module 3 — Neural Machine Translation:",
    "Based on NLLB-200-distilled-600M, fine-tuned via transfer learning using LoRA (rank 16, "
    "PEFT) for each source language-to-plt_Latn language pair. Fine-tuning is conducted on "
    "Vertex AI Custom Training with NVIDIA L4 Spot GPUs, producing a measured improvement of "
    "2 to 8 chrF++ points over the baseline.")
bullet(doc, "Module 4 — Dialectal Text-to-Speech Synthesis (TTS):",
    "Based on Meta's MMS-TTS-MLG VITS model, fine-tuned per dialect from 80 to 150 high-quality "
    "audio samples in 1 to 2 hours of GPU compute, via the ylacombe/finetune-hf-vits framework. "
    "Each dialect checkpoint is versioned with its evaluation metadata.")
body(doc,
    "The full pipeline is exposed through a FastAPI application deployed on Google Cloud Run GPU "
    "(NVIDIA L4, 24 GB), with end-to-end latency under five seconds and a total VRAM footprint "
    "of 6.2 GB supporting three to five concurrent sessions per instance.")
body(doc,
    "Current status: A first working proof of concept covering four dialects (Official Malagasy, "
    "Betsileo, Betsimisaraka, Sakalava) has been operational since April 2026. Approximately "
    "1,000 data pairs have already been compiled since the project launch at end of 2025.")

divider(doc)
h2(doc, "Data and Linguistic Resources")
body(doc,
    "The data creation component is central to the project. For each target dialect, the protocol "
    "aims to build an initial corpus of 150 to 200 hours of natural speech and 10,000 high-quality "
    "audio-transcription pairs. Data is collected by local coordinators recruited from within the "
    "communities themselves, with priority given to women, trained in the collection protocol, "
    "and fairly compensated.")
body(doc,
    "All produced resources are published in their entirety under open licences: Apache 2.0 for "
    "models and code, Creative Commons BY 4.0 for audio data and transcriptions. They are "
    "deposited on HuggingFace and Mozilla Common Voice, ensuring their reuse by the entire "
    "African NLP research community.")

divider(doc)
h2(doc, "Community Impact and Local Grounding")
body(doc,
    "MGVaovao - Maison du Numérique is a physical community digital centre, inaugurated in "
    "February 2024 in Ambatonakanga, Antananarivo, on a unique philanthropic model: funded "
    "exclusively from the founder's personal resources, access to all programmes is entirely "
    "free of charge (0 ariary) for all beneficiaries.")
body(doc,
    "Since its inauguration, the centre has welcomed over 5,500 unique beneficiaries (48% women, "
    "aged 7 to 65) and has accompanied 2,366 people trained through its partner programmes:")
bullet(doc, "e-jery :", "digital inclusion programme for vulnerable children (1,483 people trained)")
bullet(doc, "ANKY :", "personal development and entrepreneurship training (472 people trained)")
bullet(doc, "Madagascar DataCamp :", "basic Excel training for students (411 people trained)")
bullet(doc, "YAS Madagascar :", "Ampela Online programme for women's online entrepreneurship")
bullet(doc, "Down Syndrome Madagascar :", "digital inclusion programme for 28 children with Down syndrome (trisomy 21)")
body(doc,
    "The centre relies on a community of over 26 documented active volunteers and has established "
    "partnerships across the national territory.")
body(doc,
    "MGVaovao - Maison du Numérique was shortlisted for the RSE de l'Année 2026 Award at the "
    "April 2026 2nd edition of the CEO Summit Indian Ocean, an external recognition of the "
    "organisation's social impact.")

divider(doc)
h2(doc, "Concrete Use Cases")
bullet(doc, "Education :",
    "The system allows trainers to address learners in their native linguistic variety, improving "
    "comprehension and engagement in digital literacy and special needs education programmes. "
    "An interactive kiosk deployed at Maison du Numérique's premises allows anyone to speak in "
    "French, English, or another supported language and immediately receive an audio response "
    "in their Malagasy dialect.")
bullet(doc, "Civic Inclusion :",
    "Citizens who do not speak Official Malagasy can access information on public services, civic "
    "rights, and administrative procedures in their dialect. This need is particularly acute in "
    "rural areas where language barriers are the primary obstacle to information access.")
bullet(doc, "Public API :",
    "A documented, publicly accessible API enables institutional partners such as community health "
    "services, literacy associations, NGOs, and social support organisations to integrate dialectal "
    "communication capability into their own tools.")

divider(doc)
h2(doc, "Openness and Reproducibility")
body(doc,
    "The complete source code, fine-tuning scripts, and technical documentation are published "
    "under Apache 2.0 on:")
bullet(doc, "github.com/mgvaovao-Mdn/ml :", "ML pipeline, models, fine-tuning scripts")
bullet(doc, "github.com/mgvaovao-Mdn/backend_ia :", "API, technical documentation")
body(doc,
    "Dialectal audio corpora will be deposited on HuggingFace and Mozilla Common Voice under "
    "Creative Commons BY 4.0, constituting the first open vocal linguistic resources for "
    "dialectal Malagasy.")

divider(doc)
h2(doc, "Organisation")
bullet(doc, "Legal Name:", "Madagasikara Vaovao")
bullet(doc, "Trading Name:", "Maison du Numérique / MGVaovao")
bullet(doc, "Type:", "Non-profit association")
bullet(doc, "Headquarters:", "Antananarivo, Madagascar")
bullet(doc, "Website:", "https://mgvaovao.com")
bullet(doc, "Email:", "contact@mgvaovao.com")

output_path = r"C:\Github Repositories\mgvaovao\MGVaovao_Project_Description_BILINGUAL.docx"
doc.save(output_path)
print(f"Saved: {output_path}")
