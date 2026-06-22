# MGVaovao — Real-Time Speech-to-Speech Translation into Malagasy Dialects
## Project Description

### Overview

MGVaovao - Maison du Numérique (a programme of the Madagasikara Vaovao association) is developing, from Antananarivo, an open artificial intelligence infrastructure enabling automated real-time speech-to-speech translation into eighteen Malagasy dialects. This project constitutes the first initiative worldwide to create open vocal linguistic resources for the full dialectal continuum of Malagasy, a language spoken by over 28 million people.

---

### Context and Problem Statement

Madagascar is an island-continent of exceptional linguistic richness. While Malagasy ranks among the forty most widely spoken African languages in Africa, this recognition conceals a profound dialectal fragmentation: eighteen living regional dialects — Betsileo, Betsimisaraka, Sakalava, Antandroy, Tsimihety, Vezo, Bara, Sihanaka, Antakarana, Makoa, Antaisaka, and seven others — coexist across the national territory. These varieties differ phonologically and lexically to the point of creating genuine communication barriers between communities.

Official Malagasy (the Merina variety) is the only form with even a minimal presence in existing AI systems. None of the seventeen regional dialects are represented in major multilingual datasets such as Common Voice, FLORES-200, or OPUS. This absence denies millions of speakers equitable access to educational, health, and civic services available in digital form. When a Betsileo farmer searches for information on drought-resistant seeds, or a Betsimisaraka mother tries to understand maternal health guidelines, the available digital tools do not speak their language.

To date, fewer than ten published academic works address the computational processing of Malagasy in its dialectal diversity.

---

### Solution Developed

The system developed by MGVaovao is a speech-to-speech cascade pipeline composed of four complementary modules, each optimised for the constraints of the African context — minimal latency, controlled compute cost, and adaptability to low-volume data.

**Module 1 — Voice Activity Detection**
Based on Silero VAD v5, this lightweight 2 MB model runs on CPU in 32-millisecond windows. It filters silence segments before processing and reduces compute costs by 30 to 50 percent on real-world recordings.

**Module 2 — Automatic Speech Recognition (ASR)**
Based on Whisper large-v3-turbo quantised to INT8 via CTranslate2, this module supports 99 input languages, including French, English, German, Spanish, Italian, and Portuguese. INT8 quantisation delivers twice the inference speed of the original FP16 model at approximately 1.7 GB VRAM.

**Module 3 — Neural Machine Translation**
Based on NLLB-200-distilled-600M, fine-tuned via transfer learning using LoRA (rank 16, PEFT) for each source language-to-plt_Latn language pair. Fine-tuning is conducted on Vertex AI Custom Training with NVIDIA L4 Spot GPUs, producing a measured improvement of 2 to 8 chrF++ points over the baseline.

**Module 4 — Dialectal Text-to-Speech Synthesis (TTS)**
Based on Meta's MMS-TTS-MLG VITS model, fine-tuned per dialect from 80 to 150 high-quality audio samples in 1 to 2 hours of GPU compute, via the ylacombe/finetune-hf-vits framework. Each dialect checkpoint is versioned with its evaluation metadata.

The full pipeline is exposed through a FastAPI application deployed on Google Cloud Run GPU (NVIDIA L4, 24 GB), with end-to-end latency under five seconds and a total VRAM footprint of 6.2 GB supporting three to five concurrent sessions per instance.

**Current status:** A first working proof of concept covering four dialects (Official Malagasy, Betsileo, Betsimisaraka, Sakalava) has been operational since April 2026. Approximately 1,000 data pairs have already been compiled since the project launch at end of 2025.

---

### Data and Linguistic Resources

The data creation component is central to the project. For each target dialect, the protocol aims to build an initial corpus of 150 to 200 hours of natural speech and 10,000 high-quality audio-transcription pairs. Data is collected by local coordinators recruited from within the communities themselves, with priority given to women, trained in the collection protocol, and fairly compensated.

All produced resources are published in their entirety under open licences: Apache 2.0 for models and code, Creative Commons BY 4.0 for audio data and transcriptions. They are deposited on HuggingFace and Mozilla Common Voice, ensuring their reuse by the entire African NLP research community.

---

### Community Impact and Local Grounding

MGVaovao - Maison du Numérique is a physical community digital centre, inaugurated in February 2024 in Ambatonakanga, Antananarivo, on a unique philanthropic model: funded exclusively from the founder's personal resources, access to all programmes is entirely free of charge (0 ariary) for all beneficiaries.

Since its inauguration, the centre has welcomed over **5,500 unique beneficiaries** (48% women, aged 7 to 65) and has accompanied **2,366 people trained** through its partner programmes:
- **e-jery** — digital inclusion programme for vulnerable children (1,483 people trained)
- **ANKY** — personal development and entrepreneurship training (472 people trained)
- **Madagascar DataCamp** — basic Excel training for students (411 people trained)
- **YAS Madagascar** — Ampela Online programme for women's online entrepreneurship
- **Down Syndrome Madagascar** — digital inclusion programme for 28 children with Down syndrome (trisomy 21)

The centre relies on a community of over 26 documented active volunteers and has established partnerships across the national territory.

MGVaovao - Maison du Numérique was **shortlisted for the RSE de l'Année 2026 Award** at the April 2026 2nd edition of the CEO Summit Indian Ocean, an external recognition of the organisation's social impact.

---

### Concrete Use Cases

**Education** — The system allows trainers to address learners in their native linguistic variety, improving comprehension and engagement in digital literacy and special needs education programmes. An interactive kiosk deployed at Maison du Numérique's premises allows anyone to speak in French, English, or another supported language and immediately receive an audio response in their Malagasy dialect.

**Civic Inclusion** — Citizens who do not speak Official Malagasy can access information on public services, civic rights, and administrative procedures in their dialect. This need is particularly acute in rural areas where language barriers are the primary obstacle to information access.

**Public API** — A documented, publicly accessible API enables institutional partners — community health services, literacy associations, NGOs, social support organisations — to integrate dialectal communication capability into their own tools.

---

### Openness and Reproducibility

The complete source code, fine-tuning scripts, and technical documentation are published under Apache 2.0 on:
- **github.com/mgvaovao-Mdn/ml** — ML pipeline, models, fine-tuning scripts
- **github.com/mgvaovao-Mdn/backend_ia** — API, technical documentation

Dialectal audio corpora will be deposited on HuggingFace and Mozilla Common Voice under Creative Commons BY 4.0, constituting the first open vocal linguistic resources for dialectal Malagasy.

---

### Organisation

**Legal Name:** Madagasikara Vaovao  
**Trading Name:** Maison du Numérique / MGVaovao  
**Type:** Non-profit association  
**Headquarters:** Antananarivo, Madagascar  
**Website:** https://mgvaovao.com  
**Email:** contact@mgvaovao.com
