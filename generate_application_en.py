# -*- coding: utf-8 -*-
"""
Generates the English Word application document for LINGUA Africa — MGVaovao / Maison du Numérique
Source: LINGUA_Africa_Application_QA.md (approved version)
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

def btable(doc, rows, col0="Cost Category", col1="Amount (USD)"):
    t = doc.add_table(rows=len(rows)+1, cols=2)
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    hdr[0].text = col0; hdr[1].text = col1
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
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(20)
rf(p.add_run("LINGUA AFRICA 2026 — FULL PROPOSAL"), bold=True, size=20, color=(31, 78, 121))

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
rf(p.add_run("Application Language: English  |  Deadline: June 15, 2026"), size=11, italic=True)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ORGANISATION DETAILS
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Organisation Details")

field(doc, "Application Language:",          "English")
field(doc, "Organization Legal Name:",       "Madagasikara Vaovao")
field(doc, "Organization Trading Name:",     "Maison du Numérique / MGVaovao")
field(doc, "Organization Type:",             "Non-profit association")
field(doc, "Country of Headquarters:",       "Madagascar")
field(doc, "Countries of Presence:",         "Madagascar")
field(doc, "Organization Email:",            "contact@mgvaovao.com")
field(doc, "Web Presence:",
    "https://mgvaovao.com  |  https://github.com/mgvaovao-Mdn/ml  |  "
    "https://github.com/mgvaovao-Mdn/backend_ia  |  "
    "https://www.linkedin.com/company/maison-du-num%C3%A9rique-madagascar  |  "
    "https://www.facebook.com/profile.php?id=61552728359577")
field(doc, "Previous Masakhane Application:",              "No")
field(doc, "Currently Involved in Masakhane Project:",     "No")

doc.add_paragraph()
h1(doc, "Organization Contact Person")
field(doc, "First Name:", "Fenitra")
field(doc, "Last Name:",  "Ravelomanantsoa")
field(doc, "Email:",      "fenitra@google.com")
field(doc, "Phone:",      "+261 38 37 773 93")
field(doc, "Role:",       "Founder and Executive Director")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# FULL PROPOSAL DETAILS
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Full Proposal Details")

# ── Q1a ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 1(a) — Category / Categories")
para(doc,
    "Categories selected: Category 1 — Data Creation, Category 2 — Model and Tool Development, "
    "and Category 3 — Sectoral Applications.\n\n"
    "This project, carried by MGVaovao - Maison du Numérique, does not fall under a single "
    "primary category because it constitutes a complete and inseparable pipeline in which all "
    "three dimensions carry equal weight. Category 1 covers the systematic constitution of the "
    "first open speech corpora for 18 Malagasy dialects, without which no fine-tuning is "
    "possible. Category 2 covers the fine-tuning of the foundational models NLLB-200 and "
    "MMS-TTS-MLG for each of these dialects, which is the technical core of the project. "
    "Category 3 covers the deployment of the whole system in a real-world application serving "
    "communities. These three dimensions are mutually conditioning: creating data without "
    "training models produces no impact, training models without integrating them into an "
    "application does not reach beneficiaries, and deploying an application without quality "
    "data and models is not credible. The strength of this application is precisely that it "
    "covers the entire pipeline, from community-based collection to production use.")

# ── Q1b ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 1(b) — Project Title and Summary (300-word limit)")
para(doc,
    "Project Title:\n"
    "Real-Time Multilingual Speech-to-Speech Translation into 18 Malagasy Dialects — "
    "an Open AI Infrastructure for Linguistic Inclusion")
para(doc,
    "Summary:\n\n"
    "Madagascar is an island-continent where 28 million people speak a profoundly plural "
    "Malagasy language: 18 living regional dialects, each carrying distinct identities and "
    "cultures, none of which have ever been represented in modern AI systems. This gap denies "
    "millions of speakers equitable access to digital education, healthcare services, and "
    "civic resources.\n\n"
    "MGVaovao - Maison du Numérique is the organisation carrying this project. It is developing, "
    "from Antananarivo, a real-time speech-to-speech translation system designed to automatically "
    "convert spoken input in six international languages — French, English, German, Spanish, "
    "Italian, and Portuguese — into natural Malagasy speech in the dialect chosen by the user.\n\n"
    "A first working proof of concept covering four dialects has been operational since April 2026, "
    "with end-to-end latency under five seconds, on Cloud Run GPU. This prototype demonstrates "
    "the technical feasibility of the approach and constitutes a concrete foundation to be improved "
    "and extended — not a finalised system or a fully deployed production solution. Since the "
    "project launch at end of 2025, the team has already compiled approximately 1,000 data pairs, "
    "confirming the operational feasibility of the collection process.\n\n"
    "LINGUA Africa support will allow us to extend coverage to the remaining 14 dialects, "
    "build the first open vocal resources for the full Malagasy dialect continuum, and deploy "
    "this service within the education, health, and civic inclusion programmes of MGVaovao - "
    "Maison du Numérique — shortlisted for the RSE de l'Année 2026 Award (CEO Summit Indian "
    "Ocean) —, a community centre that has reached over 5,500 unique beneficiaries (48% women, "
    "aged 7 to 65, entirely free of charge) and accompanied 2,366 certified people since its "
    "inauguration in February 2024.")

# ── Q2 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 2 — Rationale and Objectives (750-word limit)")
para(doc,
    "Malagasy ranks among the forty most widely spoken African languages. But behind that "
    "recognition lies a far more complex reality. Madagascar is an island-continent where "
    "eighteen regional dialects coexist, some differing phonologically and lexically to the "
    "point of creating genuine communication barriers between communities. Official Malagasy "
    "(the Merina variety, plt_Latn) is the administrative and media language, yet millions of "
    "Malagasy speakers in the Betsileo, Betsimisaraka, Sakalava, Antandroy, and many other "
    "regions can only access digital, educational, and health services through a language that "
    "is not their own — or cannot access them at all.\n\n"
    "This imbalance is compounded by a persistent digital divide. When a Betsileo farmer "
    "searches for information on drought-resistant seeds, when a Betsimisaraka mother tries "
    "to understand maternal health guidelines, or when a Sakalava citizen wants to access an "
    "online government service, the available digital tools function either in Official Malagasy "
    "or in a colonial language. No existing AI system speaks their dialect. That is precisely "
    "the documented, measurable gap that MGVaovao - Maison du Numérique has set out to close.\n\n"
    "The project pursues three interconnected objectives. The first is to create the first open "
    "linguistic resources for eighteen Malagasy dialects: annotated audio corpora, fine-tuned "
    "model weights, and reproducible evaluation benchmarks, published entirely under Apache 2.0 "
    "and Creative Commons BY 4.0 licences. The second is to deploy a concrete, immediately "
    "usable tool accessible from Maison du Numérique and through a public API, enabling "
    "education, health, and civic services to communicate with their beneficiaries in the "
    "appropriate Malagasy dialect. The third is to embed the project within a verifiable, "
    "sustained community dynamic where native speakers participate in data collection, "
    "validation, and evaluation.\n\n"
    "To date, fewer than ten published academic works address the computational processing of "
    "Malagasy in its dialectal diversity. Major multilingual datasets — Common Voice, FLORES-200, "
    "OPUS — contain data for Official Malagasy, but nothing for its regional varieties. "
    "MGVaovao - Maison du Numérique is creating these resources for the first time, with "
    "rigour, within a community framework, and under fully open licences.\n\n"
    "The direct beneficiaries are the speakers of under-represented Malagasy dialects, a "
    "population estimated at over fifteen million people. Among Maison du Numérique's active "
    "programmes are a digital inclusion initiative for children with Down syndrome (trisomy 21) "
    "— 28 children accompanied across three cohorts in partnership with Down Syndrome Madagascar "
    "— and the Ampela Online programme for women's entrepreneurship, concrete demonstrations "
    "that the organisation's mission extends to every form of exclusion.\n\n"
    "The team carrying this project is deeply locally rooted and technically capable at an "
    "international level. Fenitra Ravelomanantsoa, founder of Madagasikara Vaovao, is Head of "
    "Cloud Regulatory Affairs at Google in Zurich — the first Malagasy to reach a senior "
    "leadership position in this company. He regularly speaks at major international forums on "
    "AI governance — including the CEO Summit Indian Ocean (April 2026), where he is also a "
    "candidate for the CEO of the Year award — and the modernisation of public infrastructure "
    "through Cloud. "
    "Norolala Randrianarison handles day-to-day operational management. Guillaume Rakotonjanahary "
    "Tsantaniaina and Karine Maholisoa Rajaofera each lead a complementary strand of the project. "
    "Guillaume is Technical Project Lead for ML development, pipeline architecture, and cloud "
    "deployment. Holder of a Master's in Big Data and AI from ESTIA France with distinction "
    "(17.2/20), he has built across five years a broad range of production AI systems: complete "
    "Speech AI pipelines, multi-agent LLM systems with LangGraph and Google ADK, hybrid RAG "
    "architectures, computer vision models (YOLO V8, CLIP, SAM), digital health platforms, and "
    "MLOps infrastructure on Vertex AI. His participation in IndabaX Madagascar 2023 (3rd place, "
    "NLP medical classification at 94% accuracy) and DataTour 2025 (pan-African competition) "
    "demonstrates his engagement in the African AI ecosystem. Karine Maholisoa Rajaofera, Data "
    "Operations and Functional Project Lead, brings ten years of experience in data operations, "
    "annotation, and large-scale collection coordination. This complementarity between "
    "world-class ML expertise and hands-on data operations mastery makes this project both "
    "technically solid and genuinely grounded in operational community reality.")

# ── Q3 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 3 — Languages Covered and Justification (350-word limit)")
para(doc,
    "The project targets Malagasy across the full continuum of its eighteen regional dialects. "
    "Malagasy is spoken by over 28 million people, placing it among the forty most widely "
    "spoken African languages. Yet behind this apparent unity lies a dialectal reality of "
    "remarkable richness and complexity that is almost entirely absent from existing AI systems.\n\n"
    "Official Malagasy (plt_Latn, the Merina variety) is the only form that today enjoys even "
    "a minimal presence in multilingual corpora such as FLORES-200 and Common Voice. The "
    "seventeen regional dialects — including Betsileo, Betsimisaraka, Sakalava, Antandroy, "
    "Tsimihety, Vezo, Bara, Sihanaka, Antakarana, Makoa, and Antaisaka — have no representation "
    "whatsoever in the global NLP ecosystem.\n\n"
    "Three converging reasons justify this choice. First, this is a documented and measurable "
    "gap: no validated dialectal speech corpus, no production NLP model, and no open dialectal "
    "voice synthesis tool exists for any of these varieties. The value created for the global "
    "NLP community is therefore maximal and immediate. Second, this choice is grounded in "
    "irrefutable community legitimacy: the team is Malagasy, based in Antananarivo, native "
    "speakers of the target languages, and Maison du Numérique has been operating physically "
    "within these communities since February 2024, with established partnerships across the "
    "national territory. Third, the potential impact is both immediate and durable: a system "
    "that speaks Betsileo to a family in the Haute-Matsiatra region or Sakalava to a fisherman "
    "in Mahajanga is not a distant ambition. It is a reality our technical infrastructure makes "
    "possible today for four dialects, and that LINGUA Africa funding will extend to the "
    "remaining fourteen varieties over eighteen structured months.")

# ── Q4 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 4 — Domains and Subdomains (300-word limit)")
para(doc,
    "This dialectal translation project operates at the intersection of three priority domains "
    "defined by LINGUA Africa.\n\n"
    "The first domain is education. Maison du Numérique has reached over 5,500 unique "
    "beneficiaries through its digital literacy programmes, with 2,366 people trained and "
    "certified via e-jery, ANKY, and Madagascar DataCamp. Most significantly, Maison du "
    "Numérique runs a digital inclusion programme for children with Down syndrome (trisomy 21) "
    "— 28 children accompanied in partnership with Down Syndrome Madagascar — and the Ampela "
    "Online programme for women's entrepreneurship, initiatives that demonstrate a radically "
    "inclusive vision of digital access. Integrating a dialectal translation system "
    "allows trainers to address learners in their native linguistic variety, improving "
    "comprehension and engagement. Targeted sub-domains include digital literacy, foundational "
    "education, and special needs education.\n\n"
    "The second domain is public health. In partnership with community health actors, the system "
    "will enable the dissemination of prevention messages covering maternal and child health, "
    "vaccination, and epidemic management, in the dialects of the regions concerned.\n\n"
    "The third domain is civic and digital inclusion. The system will enable citizens who do "
    "not speak Official Malagasy to access information on public services, civic rights, and "
    "government resources in their dialect. This need is particularly acute in rural areas, "
    "where language barriers are the primary obstacle to information access.")

# ── Q5 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 5 — Data Collection (500-word limit — Category 1)")
para(doc,
    "This project covers Category 1 through its substantial data creation component, without "
    "which the extension to the fourteen remaining dialects would be impossible.\n\n"
    "Type of data: audio recordings of natural and read speech, in WAV 16 kHz mono format, "
    "produced by native speakers of each target dialect, paired with orthographic transcriptions "
    "validated by a second native speaker. The texts used for guided readings are adapted to the "
    "project's priority domains — education, community health, civic services — ensuring the "
    "data is both linguistically representative and immediately useful for the intended use cases. "
    "Since the project launch at end of 2025, approximately 1,000 data pairs have already been "
    "compiled for the initial dialects, providing concrete proof that the collection protocol "
    "works.\n\n"
    "Volume targets: for each dialect, the project aims to compile an initial corpus of 150 to "
    "200 hours of speech and 10,000 high-quality audio-transcription pairs. The fourteen "
    "remaining dialects represent a target corpus of approximately 2,100 to 2,800 hours of "
    "recordings and 140,000 audio-transcription pairs.\n\n"
    "Collection approach: data collection will be organised in partnership with local "
    "coordinators in each linguistic region — Fianarantsoa for Betsileo, Toamasina for "
    "Betsimisaraka, Mahajanga for Sakalava, Ambovombe for Antandroy, Mandritsara for "
    "Tsimihety. Coordinators are recruited from within the communities themselves, with "
    "priority given to women, trained in the collection protocol, and fairly compensated.\n\n"
    "Openness: all produced data will be published under Creative Commons BY 4.0 on HuggingFace "
    "and contributed to Mozilla Common Voice, enabling reuse by the entire African NLP research "
    "community. Transcriptions will also be available in TSV format compatible with standard "
    "Masakhane community tools.\n\n"
    "The protocol follows international ethical standards: written informed consent in Official "
    "Malagasy and the local dialect, right of withdrawal at any point before publication, and "
    "prohibition of recording minors without written parental consent.")

# ── Q6 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 6 — Models and Tools (500-word limit — Category 2)")
para(doc,
    "The speech-to-speech pipeline developed in this project is composed of four cascade stages. "
    "A working proof of concept is functional for four dialects today and the architecture is "
    "designed to scale across all eighteen Malagasy dialectal varieties.\n\n"
    "The first component is a Voice Activity Detection module based on Silero VAD v5. This "
    "lightweight model (2 MB), running on CPU in 32-millisecond windows, filters silence "
    "segments before passing them to the ASR module, reducing compute costs by 30 to 50 percent "
    "on real-world recordings.\n\n"
    "The second component is the Automatic Speech Recognition module, based on Whisper "
    "large-v3-turbo quantised to INT8 via CTranslate2. This model supports 99 input languages, "
    "covering all six source languages targeted by the project. INT8 quantisation delivers "
    "twice the inference speed of the FP16 original while maintaining comparable accuracy, at "
    "approximately 1.7 GB VRAM.\n\n"
    "The third component is the Neural Machine Translation module, based on "
    "NLLB-200-distilled-600M, fine-tuned via LoRA (rank 16, PEFT) for each source-to-plt_Latn "
    "language pair. Fine-tuning is conducted on Vertex AI Custom Training (NVIDIA L4 Spot, "
    "~USD 0.28/hour), in 6 to 12-hour runs per language pair. The measured chrF++ improvement "
    "is 2 to 8 points over the baseline, depending on the language pair. All fine-tuned LoRA "
    "weights are published under Apache 2.0.\n\n"
    "The fourth component is the dialectal Text-to-Speech synthesis module, based on Meta's "
    "MMS-TTS-MLG VITS model, fine-tuned per dialect from 80 to 150 high-quality audio samples "
    "in 1 to 2 hours on an L4 Spot GPU via the ylacombe/finetune-hf-vits framework. Each "
    "dialect checkpoint is versioned in Vertex AI Model Registry with associated evaluation "
    "metadata. All checkpoints are published under Apache 2.0.\n\n"
    "The full pipeline is exposed through a FastAPI application deployed on Google Cloud Run "
    "GPU (NVIDIA L4 24 GB), with end-to-end latency under five seconds and a total VRAM "
    "footprint of 6.2 GB supporting three to five concurrent sessions per instance. The "
    "complete source code, fine-tuning scripts, and technical documentation are published on "
    "GitHub at github.com/mgvaovao-Mdn/ml and github.com/mgvaovao-Mdn/backend_ia, under Apache 2.0.\n\n"
    "These components reflect the most performant models available at the time of prototype "
    "development. The architecture is modular: should more powerful or better-suited models "
    "for very low-resource languages emerge during the project, their integration into the "
    "pipeline would be considered and evaluated against the same quality criteria.")

# ── Q7 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 7 — Use Case (500-word limit — Category 3)")
para(doc,
    "The primary use case is a multilingual-to-Malagasy dialectal translation and information "
    "service accessible from MGVaovao - Maison du Numérique and through a public API, designed "
    "for populations who do not speak Official Malagasy or international languages but who need "
    "to access educational, health, and civic services.\n\n"
    "Concretely, the system operates through two complementary interfaces. The first is an "
    "interactive kiosk deployed at the Maison du Numérique premises in Ambatonakanga, "
    "Antananarivo: a person speaks in French, English, or any other supported language and "
    "immediately receives an audio response in their Malagasy dialect. This kiosk is used "
    "during onboarding sessions for new learners, in training workshops, and in community "
    "information drop-in sessions. The second interface is a public, documented API accessible "
    "to institutional partners — community health services, literacy associations, NGOs, and "
    "social support organisations — wishing to integrate dialectal communication capability "
    "into their own tools.\n\n"
    "The expected impact is structured around four axes. In education, the system allows "
    "trainers to address learners in their native variety, improving comprehension and reducing "
    "dropout from digital literacy programmes. In health, community health partners can "
    "disseminate prevention messages in the dialects of the regions concerned, without "
    "requiring a human interpreter. In civic inclusion, information on citizens' rights and "
    "administrative procedures can be made accessible in dialect. In terms of digital "
    "sovereignty, Madagascar will for the first time have an open linguistic infrastructure "
    "built by Malagasy people for Malagasy people.\n\n"
    "Maison du Numérique constitutes the ideal pilot environment: over 5,500 unique "
    "beneficiaries, 2,366 people trained and certified via e-jery, ANKY, and Madagascar "
    "DataCamp, and a community of over 26 documented active volunteers. This human fabric guarantees that the system will be "
    "evaluated by real users, in their real context, with genuine needs.")

# ── Q8 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 8 — Tasks and Evaluation (500-word limit)")
para(doc,
    "The project is structured around five main task sets, each associated with precise and "
    "measurable evaluation indicators.\n\n"
    "The first task is the constitution of dialectal speech corpora. For each dialect not yet "
    "covered, recording sessions are organised in native speakers' home regions. Evaluation "
    "covers validated data volume (in hours and audio-transcription pairs), speaker diversity "
    "(gender parity enforced at a minimum of 50%, age diversity across three brackets), and "
    "technical audio quality.\n\n"
    "The second task is the fine-tuning of translation (NLLB LoRA) and voice synthesis "
    "(MMS-TTS VITS) models for each dialect. Evaluation relies on chrF++ for translation "
    "quality (target: score ≥ 45 and improvement of at least 3 points over the Official "
    "Malagasy baseline) and UTMOS for synthesis naturalness (target: score ≥ 3.5 out of 5). "
    "Complementary human evaluations are conducted by panels of native speakers from each "
    "dialect to validate intelligibility and naturalness.\n\n"
    "The third task is deployment and integration within Maison du Numérique services. "
    "Evaluation covers system availability (target: 99% during opening hours), end-to-end "
    "latency (target: under five seconds), and user satisfaction measured through a structured "
    "monthly questionnaire.\n\n"
    "The fourth task is the conduct of quarterly community evaluation sessions with native "
    "speakers of each dialect. These sessions collect qualitative feedback on translation and "
    "synthesis quality and feed directly into model retraining cycles. No dialect is deployed "
    "to production before reaching the defined quality thresholds.\n\n"
    "The fifth task is the open publication of all produced resources. Evaluation covers the "
    "number of resources published on HuggingFace and GitHub, the number of downloads within "
    "the first six months, and documented reuse by other teams in the African NLP community. "
    "A monthly tracking dashboard is maintained and shared with LINGUA Africa partners.")

# ── Q9 ────────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 9 — Methodology (1,000-word limit)")
para(doc,
    "The methodology of this project rests on four interdependent pillars: a rigorous technical "
    "approach grounded in state-of-the-art speech AI, a community-based and ethically governed "
    "data collection process, a continuous evaluation cycle anchored in native speaker feedback, "
    "and a user-facing application layer that makes the service accessible outside any technical "
    "context.")

subh(doc, "Pillar 1 — Technical Architecture")
para(doc,
    "The speech-to-speech pipeline is composed of four cascade modules, each optimised for the "
    "constraints of the African context: minimal latency, controlled compute cost, and "
    "adaptability to low-volume data.\n\n"
    "Voice Activity Detection uses Silero VAD v5, a 2 MB model running on CPU in 32 ms windows. "
    "It filters silence segments before ASR processing, reducing compute costs by 30 to 50 "
    "percent on real-world recordings.\n\n"
    "Automatic Speech Recognition uses Whisper large-v3-turbo quantised to INT8 via CTranslate2, "
    "which delivers the best accuracy-to-speed-to-footprint ratio for the six source languages "
    "targeted (1.7 GB VRAM, 2× faster than the FP16 version).\n\n"
    "Neural Machine Translation uses NLLB-200-distilled-600M fine-tuned via PEFT/LoRA (rank 16) "
    "for each source-to-plt_Latn pair. Fine-tuning runs on Vertex AI Custom Training (NVIDIA L4 "
    "Spot, ~USD 0.28/hour) in 6 to 12-hour runs per language pair. The measured chrF++ "
    "improvement is 2 to 8 points. The full MLOps lifecycle is orchestrated via Vertex AI "
    "Pipelines (Kubeflow DAG) with automatic triggering on new data via Pub/Sub on GCS.\n\n"
    "Text-to-Speech Synthesis uses Meta's MMS-TTS-MLG VITS fine-tuned per dialect via the "
    "ylacombe/finetune-hf-vits framework. Each dialect requires 80 to 150 audio samples and "
    "1 to 2 hours of GPU compute. The total VRAM footprint in production is 6.2 GB on an L4 "
    "GPU, with a steady-state operational cost of approximately USD 42 per month.")

subh(doc, "Pillar 2 — Community-Based Data Collection")
para(doc,
    "The collection of speech data for the fourteen uncovered dialects follows a structured "
    "four-step protocol: identification and recruitment of local coordinators from within the "
    "communities themselves, with priority given to women, and fair compensation per coordinated "
    "session hour; preparation of collection texts adapted to priority domains and validated by "
    "native speakers for dialectal representativeness; recording sessions in quiet community "
    "spaces with signed informed consent forms available in both Official Malagasy and the "
    "local dialect; and automated processing followed by manual validation by a second native "
    "speaker who confirms the transcription and dialectal authenticity.")

subh(doc, "Pillar 3 — Continuous Evaluation and Iterative Improvement")
para(doc,
    "Automatic evaluation uses chrF++ (translation), UTMOS (TTS), and WER (ASR) on hold-out "
    "test sets reserved from the collection phase and never used in training. Human evaluation "
    "is conducted quarterly with panels of native speakers from each dialect. Production "
    "deployment uses a blue/green strategy on Cloud Run GPU with automatic rollback on "
    "performance regression. No dialect is promoted to production before reaching the defined "
    "quality thresholds (chrF++ ≥ 45, UTMOS ≥ 3.5).")

subh(doc, "Pillar 4 — User-Facing Application Layer")
para(doc,
    "The model pipeline, however performant, produces impact only if it is accessible to "
    "non-technical users. The application layer is the direct point of contact with "
    "beneficiaries.\n\n"
    "The FastAPI application deployed on Cloud Run GPU exposes the models through documented "
    "REST endpoints, enabling any institutional partner to integrate the dialectal translation "
    "service into their own tools. The API handles authentication, target dialect selection, "
    "audio input validation, and structured error responses. The full source code is published "
    "at github.com/mgvaovao-Mdn/backend_ia under Apache 2.0.\n\n"
    "On top of this API, a real-time interface — WebRTC for browser-based access or WebSocket "
    "for partner integrations — enables interactive translation sessions with under five seconds "
    "of end-to-end latency. Automatic end-of-speech detection relies on Silero VAD, already "
    "integrated at the core of the pipeline, which segments the incoming audio stream in 32 ms "
    "windows and triggers each translation cycle as soon as a sentence ends, without requiring "
    "any user action. The user selects their target dialect and speaks in one of the six supported "
    "source languages. The system transcribes, translates, and synthesises the response in a "
    "single unified request.\n\n"
    "The application layer also includes a production quality monitoring dashboard, an "
    "integrated user feedback mechanism feeding directly into retraining cycles, and usage "
    "tracking tools showing which dialects are most frequently requested. This feedback loop "
    "between real usage and model improvement ensures the system will continue to progress "
    "under operational conditions.")

# ── Q10 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 10 — Expected Outputs and Key Learnings (500-word limit)")
para(doc,
    "The deliverables of the project fall into three categories: open linguistic resources, "
    "open-source models and tools, and documented community impact.\n\n"
    "In terms of linguistic resources, the project will produce and publish eighteen dialectal "
    "audio corpora covering the full range of Malagasy regional varieties — an estimated total "
    "of 2,500 to 3,000 hours of transcribed and validated speech. These corpora will be "
    "published on HuggingFace and contributed to Mozilla Common Voice under Creative Commons "
    "BY 4.0. They will constitute the first open speech resources for Malagasy dialects, "
    "immediately reusable by the African and global NLP research community.\n\n"
    "In terms of models and tools, the project will publish on github.com/mgvaovao-Mdn/ml and "
    "HuggingFace: LoRA fine-tuned NLLB-200 weights for eighteen Malagasy dialects (Apache 2.0); "
    "MMS-TTS-MLG VITS checkpoints for eighteen dialects (Apache 2.0); fully documented, "
    "reproducible fine-tuning scripts; a Malagasy dialectal evaluation benchmark with hold-out "
    "test sets and reference metrics; and a public, documented API at "
    "github.com/mgvaovao-Mdn/backend_ia enabling third-party integration of the pipeline.\n\n"
    "In terms of community impact, the project will document: the number of system usage "
    "sessions at Maison du Numérique (target: 2,000 sessions over twelve months); the number "
    "of native speakers who participated in data collection (target: 500 people across "
    "fourteen regions); and the results of satisfaction and intelligibility evaluations "
    "conducted with end users.\n\n"
    "Key learnings will cover the minimum data conditions required for deployable-quality TTS "
    "and MT fine-tuning on very low-resource dialects; best practices for community speech "
    "data collection in rural African contexts; and a comparative performance analysis across "
    "eighteen dialectal varieties identifying the linguistic factors that influence ASR, MT, "
    "and TTS system quality. All insights and resources will be published in a final technical "
    "report shared with the Masakhane community, in both English and French.")

# ── Q11 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 11 — Proposed Timeline and Key Milestones (400-word limit)")
para(doc,
    "The project is planned over eighteen months, structured in three successive phases.\n\n"
    "Phase 1 — Setup and Launch (Months 1 to 4): recruitment and training of fourteen local "
    "coordinators; finalisation of informed consent protocols and collection texts in each "
    "dialect; establishment of partnerships with regional branches and community associations; "
    "launch of recording sessions for the five first priority dialects (Antandroy, Tsimihety, "
    "Vezo, Bara, Sihanaka). End-of-phase deliverable: collection infrastructure operational "
    "and first fine-tuning runs underway on Vertex AI.\n\n"
    "Phase 2 — Main Production (Months 5 to 12): data collection for the remaining nine "
    "dialects; fine-tuning of NLLB and MMS-TTS models for all eighteen dialects as data "
    "becomes available; automatic and human evaluation of each dialectal model; progressive "
    "deployment of validated dialects within Maison du Numérique's service system. "
    "Milestone M8: ten dialects fine-tuned, evaluated, and deployed (chrF++ ≥ 45, UTMOS ≥ 3.5). "
    "Milestone M12: all eighteen dialects fine-tuned and in community evaluation, 1,000 usage "
    "sessions documented.\n\n"
    "Phase 3 — Consolidation, Publication, and Transfer (Months 13 to 18): final community "
    "evaluation sessions for all dialects; targeted retraining based on feedback; full "
    "publication of all resources on HuggingFace and GitHub; organisation of an open "
    "dissemination workshop for the African NLP community; drafting and publication of the "
    "final technical report. Final deliverable M18: eighteen dialects operational, corpora "
    "and models published, full documentation, 2,000 usage sessions documented, and final "
    "technical report submitted to the Masakhane community.")

# ── Q12 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 12 — Ethical, Inclusion, and Data Governance Considerations (500-word limit)")
para(doc,
    "Ethics is at the core of MGVaovao's design — not an afterthought.\n\n"
    "On consent and speaker protection, every participant signs an informed consent form "
    "available in Official Malagasy and in their local dialect. This form explains the nature "
    "of the data collected, its intended use, the CC BY 4.0 licence under which it will be "
    "published, and the unconditional right of withdrawal at any point before publication. "
    "Minors participate only with written parental or guardian consent.\n\n"
    "On inclusion and representation, the collection protocol explicitly mandates gender "
    "parity: at minimum 50 percent of recorded speakers in each dialect must be women. Age "
    "diversity is addressed with three age brackets (18–35, 36–55, 55+) to capture "
    "intergenerational phonological variation. Local coordinators are themselves members of "
    "the targeted communities. Maison du Numérique's commitment to inclusion goes beyond "
    "gender and age: the organisation already runs a dedicated digital inclusion programme "
    "for children with Down syndrome — 28 children accompanied in partnership with Down "
    "Syndrome Madagascar — and the Ampela Online programme for women's entrepreneurship, "
    "documented daily practices that place it among the most genuinely inclusive organisations "
    "in Madagascar's digital ecosystem.\n\n"
    "On licensing and openness, all project deliverables — audio corpora, transcriptions, "
    "fine-tuned model weights, scripts, documentation — are published under fully open "
    "licences: Apache 2.0 for models and code, Creative Commons BY 4.0 for data.\n\n"
    "On environmental impact, the project deliberately minimises its compute footprint through "
    "the use of distilled models (NLLB-200-distilled-600M), INT8 quantisation, LoRA "
    "fine-tuning, and a scale-to-zero production infrastructure that eliminates energy "
    "consumption outside active usage periods.\n\n"
    "On data governance, all collected data is stored on GCS with encryption at rest and "
    "access restricted to the project team. Fenitra Ravelomanantsoa, as Head of Cloud "
    "Regulatory Affairs at Google, personally ensures the project's compliance with "
    "international data protection standards. This level of expertise in data governance "
    "is rare among African language AI projects and represents a distinctive asset of this "
    "application.")

# ── Q13 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 13(a) — Applying as a Consortium?")
para(doc,
    "No. MGVaovao - Maison du Numérique (Madagasikara Vaovao) submits this proposal as the "
    "lead organisation. The project operates with an established network of operational "
    "partners — e-jery, ANKY, Madagascar DataCamp, and Down Syndrome Madagascar — who "
    "contribute to community outreach and programme delivery but are not formal co-applicants. "
    "Letters of support can be provided on request.")

# ── Q14 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 14 — Letters of Support and Supplementary Documentation")
para(doc,
    "Letters of support can be requested from Maison du Numérique's operational partners, "
    "notably e-jery (digital training, 1,483 people certified), ANKY (472), Madagascar "
    "DataCamp (411), and Down Syndrome Madagascar (trisomy 21 programme). These partnerships "
    "are active and documented since the inauguration of Maison du Numérique in February 2024.\n\n"
    "Supplementary documentation is directly accessible in the public GitHub repositories. "
    "The repository github.com/mgvaovao-Mdn/ml contains a detailed README describing the "
    "complete pipeline architecture, fine-tuning reproduction instructions, evaluation "
    "metrics obtained, and data structure, as well as a file MGVaovao_Architecture_Complete.md "
    "documenting all architectural choices, dependencies, and data flow. The repository "
    "github.com/mgvaovao-Mdn/backend_ia likewise contains a complete README and API documentation. "
    "All of these resources are published under Apache 2.0 licence.")

# ── Q15 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 15 — Project Team Members and Roles (400-word limit)")

subh(doc, "Fenitra Ravelomanantsoa — Founder and Executive Director, MGVaovao - Maison du Numérique")
para(doc,
    "Head of Cloud Regulatory Affairs at Google in Zurich — the first Malagasy to reach a "
    "senior leadership position in this company —, Fenitra oversees cloud regulatory compliance "
    "at international scale. A speaker at the CEO Summit Indian Ocean (April 2026) and candidate "
    "for the CEO of the Year award, he founded the Madagasikara Vaovao association and MGVaovao "
    "- Maison du Numérique in November 2023 on a unique philanthropic model: funded exclusively "
    "from the founder's personal resources, Maison du Numérique provides fully free access "
    "(0 ariary) to digital training for Malagasy communities. He oversees the project's global "
    "strategy, institutional partnerships, and ethical governance.")

subh(doc, "Norolala Randrianarison — Local Director and Operations Manager")
para(doc,
    "A professional from the Malagasy telecommunications and digital sector, Mme Noro handles "
    "the day-to-day operational management of Maison du Numérique. She oversees community "
    "reception, programme deployment, volunteer coordination, and relationships with local "
    "institutional partners.")

subh(doc, "Guillaume Rakotonjanahary Tsantaniaina — Technical Project Lead — ML and Development")
para(doc,
    "An AI/ML Engineer with over five years of experience in production-grade Speech AI, NLP, "
    "and GCP cloud infrastructure, Guillaume holds a Master's in Big Data and Artificial "
    "Intelligence from ESTIA (France) with distinction (17.2/20). As Technical Project Lead, "
    "he is responsible for the ML and development strand: model architecture, NLLB and "
    "MMS-TTS fine-tuning, Cloud Run GPU deployment, and MLOps orchestration on Vertex AI. "
    "Across five years he has built a broad range of production AI systems: complete Speech AI "
    "pipelines (ASR, neural translation, voice synthesis), multi-agent LLM systems with "
    "LangGraph and Google ADK, hybrid RAG architectures (vector, graph, multimodal), computer "
    "vision models (YOLO V8, CLIP, SAM), digital health platforms, and MLOps infrastructure "
    "on Vertex AI. A native Malagasy and French speaker, he brings intimate knowledge of "
    "dialectal nuances essential to model quality. Placed 3rd at IndabaX Madagascar 2023 "
    "(NLP medical classification at 94% accuracy) and a participant in DataTour 2025 (pan-"
    "African competition, recommendation and credit scoring models), he is an active member "
    "of the African AI ecosystem.")

subh(doc, "Karine Maholisoa Rajaofera — Data, Operations, and Functional Project Lead")
para(doc,
    "Holder of a Bachelor's degree in Business Management, Karine brings ten years of "
    "experience in data operations, large-scale collection, and field team coordination. "
    "A Data Specialist and Lidar Expert at SmartOne.ai, she has led data collection, "
    "annotation, and validation projects in real-world conditions over a decade. She joined "
    "MGVaovao - Maison du Numérique in September 2025 and has since led the AI programme on "
    "Malagasy dialects as principal project lead. She oversees the full voice collection cycle "
    "across fourteen dialectal regions, defines annotation protocols, ensures transcription "
    "quality control, coordinates field teams, and translates business requirements into "
    "functional specifications for the technical pipeline. Proficient in Word, Excel, Google "
    "Sheets, and the full suite of Google platforms, she serves as the interface between "
    "field operational realities and the technical strand. She also leads the digital "
    "inclusion programme for children with Down syndrome at Maison du Numérique (28 children "
    "accompanied in partnership with Down Syndrome Madagascar).")

subh(doc, "Partnerships & Impact Lead (to be recruited) · 14 Local Coordinators (to be recruited)")
para(doc,
    "A third project lead dedicated to institutional partnerships and impact measurement will "
    "be recruited at the start of the project on LINGUA Africa funds. One field coordinator "
    "will be recruited per dialect region — fourteen in total — from within the speaker "
    "communities, with priority given to women.")

# ── Q16 ───────────────────────────────────────────────────────────────────────
qlabel(doc, "Question 16 — Relevant Prior Work and References (300-word limit)")
para(doc,
    "This project builds on a coherent research and development trajectory whose prior "
    "milestones establish both its feasibility and its originality.\n\n"
    "MGVaovao - Maison du Numérique, founded in November 2023, has been operating since its "
    "inauguration in February 2024. It is on this solid institutional base that the "
    "speech-to-speech translation project in Malagasy dialects was launched at end of 2025, "
    "following a preliminary phase of evaluation of existing ASR and TTS architectures for "
    "low-resource languages — including Whisper, Chirp (Vertex AI Studio), and VITS "
    "architectures — which established the transfer adaptation methodology now at the core "
    "of the pipeline.\n\n"
    "This prototype has been operational since April 2026 for four dialects (Official Malagasy, "
    "Betsileo, Betsimisaraka, Sakalava), with end-to-end latency under five seconds; it is a "
    "first result to be extended, not a finalised system. Approximately 1,000 data pairs have "
    "already been compiled, including text-text pairs for neural translation and text-audio "
    "pairs for speech synthesis.\n\n"
    "Academically, the project builds on the foundational work of the Masakhane community "
    "on African low-resource languages; on the NLLB team publications (Costa-jussà et al., "
    "2022) on massively multilingual translation; on Pratap et al. (2023) on MMS for "
    "multilingual voice synthesis; and on advances in automatic speech recognition for "
    "under-resourced languages.\n\n"
    "Maison du Numérique brings a documented and verifiable community base: over 5,500 unique "
    "beneficiaries since its February 2024 inauguration, 2,366 people trained and certified "
    "via e-jery (1,483), ANKY (472), and Madagascar DataCamp (411), and 28 children with Down "
    "syndrome accompanied in partnership with Down Syndrome Madagascar. Shortlisted for the "
    "RSE de l'Année 2026 Award (CEO Summit Indian Ocean), MGVaovao benefits from external "
    "recognition of its social impact.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Budget — Question 17")

qlabel(doc, "Question 17(b) — Summary Budget Table")
btable(doc, [
    ("1. Personnel — leadership + technical team (13 positions)",    "192,852"),
    ("2. Equipment and software",                                      "8,000"),
    ("3. Field collection — 20 collectors × USD 133 × 4 months",     "10,640"),
    ("4. Annotation & ground truth — 9 annotators × USD 133 × 3 months", "3,591"),
    ("5. Travel and field activities",                                "16,000"),
    ("6. Workshops, meetings and training",                            "4,500"),
    ("7. Communications and outreach",                                 "1,500"),
    ("8. Other direct costs",                                          "1,000"),
    ("Total Direct Costs",                                          "238,083"),
    ("9. Overhead / Indirect Costs (5%)",                            "11,904"),
    ("Grand Total",                                                 "249,987"),
])

doc.add_paragraph()
qlabel(doc, "Question 17(c) — Budget Justification (300-word limit)")
para(doc,
    "The proposed budget of USD 249,987 faithfully reflects the planned activities and the "
    "real cost structure of the Malagasy context, remaining below the USD 250,000 ceiling "
    "for Category 3.\n\n"
    "Personnel (USD 192,852) covers 13 positions over eighteen months: the five permanent "
    "leadership team members (founder at 50%, local director, Technical ML Project Lead, "
    "Data Operations Project Lead, and partnerships project lead starting month 7), plus "
    "eight developers — backend, frontend, AI, data science, DevOps — paid at 1,500,000 MGA "
    "per month (USD 333 each), fully included in the LINGUA Africa budget.\n\n"
    "Field collection (USD 10,640) pays 20 field collectors at USD 133/month (600,000 MGA) "
    "over four active collection months (20 × 133 × 4 = USD 10,640).\n\n"
    "Annotation and ground truth (USD 3,591) pays 9 transcription annotators at USD 133/month "
    "(600,000 MGA) over three active processing months (9 × 133 × 3 = USD 3,591).\n\n"
    "Equipment and software (USD 8,000) covers six laptops and field recording hardware. "
    "Travel (USD 16,000) covers eighteen dialect regions. Workshops (USD 4,500) fund field "
    "team training, a final dissemination event, and a regional conference. Overhead is "
    "capped at 5% (USD 11,904).")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# COMPUTE RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Compute Resources — Question 18")

qlabel(doc, "Question 18(a) — Do you need compute resources?")
para(doc, "Yes.")

qlabel(doc, "Question 18(b) — Amount Requested")
para(doc, "USD 150,000 in GCP compute credits (within the USD 400,000 ceiling for Category 3).")

qlabel(doc, "Question 18(c) — Use of Compute Resources (300-word limit)")
para(doc,
    "The requested GCP compute credits (USD 150,000) will be allocated across three components "
    "of the project's technical architecture.\n\n"
    "The largest share, approximately USD 80,000, will be allocated to model fine-tuning on "
    "Vertex AI Custom Training with NVIDIA L4 Spot GPUs at approximately USD 0.28/hour. These "
    "credits cover NLLB LoRA fine-tuning runs for six source languages and eighteen dialects, "
    "including experimentation cycles, hyperparameter optimisation, and retraining on new data, "
    "as well as MMS-TTS fine-tuning for each dialect. The experimentation budget is intentionally "
    "generous to allow multiple quality iterations on poorly documented dialects, where data "
    "and parameter optimisation is critical to reaching the required quality thresholds.\n\n"
    "A significant share, approximately USD 45,000, will be allocated to production "
    "infrastructure: Cloud Run GPU with an NVIDIA L4 for hosting the MGVaovao API over "
    "eighteen months, supporting three to five concurrent WebRTC sessions during Maison du "
    "Numérique opening hours, with scale-to-zero outside active usage periods.\n\n"
    "The remaining portion, approximately USD 25,000, will cover orchestration and automated "
    "evaluation pipelines via Vertex AI Pipelines, GCS storage for audio corpora and "
    "checkpoints (approximately 3 TB total), continuous integration and monitoring services "
    "(Cloud Build, Artifact Registry, Cloud Monitoring), and audio data ingestion pipeline "
    "processing.\n\n"
    "The entire architecture is built on a frugality-first philosophy: Spot instances reduce "
    "fine-tuning cost by up to 70% versus on-demand, models are distilled and quantised for "
    "production, and scale-to-zero eliminates idle consumption.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# TECHNICAL SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════
h1(doc, "Technical Support — Question 19")

qlabel(doc, "Question 19(a) — Do you need technical support?")
para(doc, "Yes.")

qlabel(doc, "Question 19(b) — What Kind of Technical Support? (300-word limit)")
para(doc,
    "The technical support MGVaovao seeks from LINGUA Africa complements the team's internal "
    "expertise in three specific areas.\n\n"
    "The first area is computational linguistics applied to Malagasy dialects. While the team "
    "has full command of the technical tools, the dialectal diversity of Malagasy raises "
    "specialised linguistic questions the team cannot resolve alone: defining reference "
    "orthographies for non-standardised dialects, managing intra-dialectal phonological "
    "variation, and designing annotation protocols adapted to languages with predominantly oral "
    "traditions. Access to experts in the descriptive linguistics of Malagasy varieties — "
    "through LINGUA Africa's network of academic fellows — would be directly valuable.\n\n"
    "The second area is large-scale human evaluation. Setting up rigorous native-speaker "
    "evaluation panels across eighteen distinct dialects, with standardised protocols and "
    "systematic result analysis, is a methodology the team is implementing at this scale for "
    "the first time. Methodological guidance from researchers experienced in evaluating speech "
    "systems for African languages would strengthen the scientific rigour of the project's "
    "outputs.\n\n"
    "The third area is networking with other LINGUA Africa ecosystem projects working on "
    "similar challenges — insular African languages, regional dialects, languages with oral "
    "traditions. Structured access to Masakhane communities of practice would allow the team "
    "to learn from other projects and contribute in return with its own findings on Malagasy, "
    "enriching the collective ecosystem that LINGUA Africa is building.")

# ═══════════════════════════════════════════════════════════════════════════════
# EDITORIAL NOTES
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
h1(doc, "Notes Before Submission")

note(doc,
    "NOTE 1 — GitHub public repositories: before submission, make github.com/mgvaovao-Mdn/ml "
    "public and add a LICENSE file (Apache 2.0). Verify that MGVaovao_Architecture_Complete.md "
    "is present in the repository.")
note(doc,
    "NOTE 2 — Detailed Budget (Q17a): the form requires a separate Excel file "
    "(LINGUA_Africa_Budget_Detaille.xlsx). Upload it to Submittable during submission.")
note(doc,
    "NOTE 3 — Letters of Support (Q14): prepare support letters from e-jery and/or ANKY "
    "and Down Syndrome Madagascar. These letters will significantly strengthen the application.")
note(doc,
    "NOTE 4 — Word count: each answer was drafted under the stated word limit. "
    "Verify in Word (Review > Word Count) before final submission.")
note(doc,
    "NOTE 5 — Q9 length: the methodology section exceeds 1,000 words slightly with the fourth "
    "pillar added. Trim if the form enforces a strict word count.")

output_path = r"C:\mgvaovao\LINGUA_Africa_Application_MGVaovao_EN.docx"
doc.save(output_path)
print(f"File saved: {output_path}")
