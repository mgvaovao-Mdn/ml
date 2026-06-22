"""Generate internal memo to Fenitra about LinkedIn content strategy."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(3)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.5)
    section.right_margin  = Cm(2.5)

def h1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0x1a, 0x56, 0x9e)
    return p

def h2(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x1a, 0x56, 0x9e)
    return p

def body(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p

def bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        run1 = p.add_run(bold_prefix)
        run1.bold = True
        run1.font.size = Pt(11)
        run2 = p.add_run(text)
        run2.font.size = Pt(11)
    else:
        run = p.add_run(text)
        run.font.size = Pt(11)
    return p

def box(doc, text):
    """Highlighted note box (simulated with a grey paragraph)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(f"  {text}  ")
    run.font.size = Pt(11)
    run.italic = True
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    # Shade paragraph
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'EBF3FB')
    pPr.append(shd)
    return p

# ── ENTÊTE ────────────────────────────────────────────────────────────────────
h1(doc, "NOTE INTERNE")
h1(doc, "MGVaovao – Maison du Numérique")
doc.add_paragraph()

meta = [
    ("À",        "Fenitra"),
    ("De",       "Équipe MGVaovao"),
    ("Date",     "Mai 2026"),
    ("Objet",    "Pourquoi il est urgent de publier sur LinkedIn — et ce que ça change pour notre candidature"),
]
for label, val in meta:
    p = doc.add_paragraph()
    run1 = p.add_run(f"{label} : ")
    run1.bold = True
    run1.font.size = Pt(11)
    run2 = p.add_run(val)
    run2.font.size = Pt(11)

doc.add_paragraph()

# ── INTRO ─────────────────────────────────────────────────────────────────────
body(doc,
    "Fenitra,")
doc.add_paragraph()

body(doc,
    "Cette note a pour but de t'expliquer clairement pourquoi il est important — et même urgent — "
    "que nous créions du contenu régulier sur la page LinkedIn de Maison du Numérique Madagascar. "
    "Ce n'est pas uniquement une question de visibilité. Il y a une raison concrète et stratégique "
    "derrière cette demande.")
doc.add_paragraph()

# ── SECTION 1 ─────────────────────────────────────────────────────────────────
h2(doc, "1. Ce que demandent les organisateurs du concours")
doc.add_paragraph()

body(doc,
    "Dans le formulaire de candidature, les organisateurs demandent explicitement de fournir "
    "des liens vers notre présence en ligne. L'objectif est simple : prouver que notre organisation "
    "existe, qu'elle est active, et qu'elle a déjà une empreinte numérique réelle.")

doc.add_paragraph()
body(doc, "Les liens demandés incluent notamment :")
bullet(doc, "Notre site web officiel")
bullet(doc, "Notre page Facebook")
bullet(doc, "Notre page LinkedIn")
bullet(doc, "Une démonstration de notre application (demo en ligne)")
bullet(doc, "Tout autre lien prouvant notre activité en ligne")
doc.add_paragraph()

box(doc,
    "💡 En résumé : une page LinkedIn vide ou inactive, c'est une preuve manquante. "
    "Une page avec des publications régulières, c'est une preuve forte que l'organisation "
    "est sérieuse, engagée et visible.")
doc.add_paragraph()

# ── SECTION 2 ─────────────────────────────────────────────────────────────────
h2(doc, "2. LinkedIn n'est pas qu'un réseau social — c'est une preuve d'existence professionnelle")
doc.add_paragraph()

body(doc,
    "Pour un jury de sélection, LinkedIn est l'équivalent d'un portfolio professionnel en ligne. "
    "Quand ils cliquent sur notre lien et trouvent :")

bullet(doc, "des publications récentes sur notre projet,", bold_prefix="✅  ")
bullet(doc, "des annonces sur notre outil d'IA de traduction,", bold_prefix="✅  ")
bullet(doc, "des témoignages de partenaires,", bold_prefix="✅  ")
bullet(doc, "une communauté qui réagit et commente,", bold_prefix="✅  ")

doc.add_paragraph()
body(doc,
    "… ils voient une organisation vivante, crédible, et en mouvement. C'est exactement le "
    "signal qu'un jury veut recevoir avant de sélectionner un projet.")

doc.add_paragraph()
body(doc,
    "À l'inverse, si notre page n'a pas de publications ou si la dernière date de plusieurs mois, "
    "cela crée un doute : est-ce que ce projet est vraiment actif ? Est-ce que cette organisation "
    "a vraiment la capacité de porter quelque chose à l'échelle africaine ?")
doc.add_paragraph()

# ── SECTION 3 ─────────────────────────────────────────────────────────────────
h2(doc, "3. Les lettres de soutien de nos partenaires : une autre preuve déjà en cours")
doc.add_paragraph()

body(doc,
    "Pour renforcer notre dossier, nous avons déjà préparé des modèles de lettres de soutien "
    "que nous allons envoyer à nos partenaires : YANKY, YAS / Ampela Online, EJERY, "
    "et Down Syndrome Madagascar.")

doc.add_paragraph()
body(doc,
    "Ces lettres constituent une preuve complémentaire très importante : elles montrent que "
    "notre projet n'est pas isolé, qu'il est reconnu et soutenu par d'autres acteurs "
    "institutionnels et associatifs de l'écosystème malgache.")

doc.add_paragraph()
box(doc,
    "📎 Ces lettres de soutien + notre présence active sur LinkedIn + notre demo en ligne "
    "= un dossier complet qui montre que MGVaovao est un projet réel, ancré, et soutenu.")
doc.add_paragraph()

# ── SECTION 4 ─────────────────────────────────────────────────────────────────
h2(doc, "4. Ce qu'on te demande concrètement")
doc.add_paragraph()

body(doc,
    "Nous avons préparé 6 publications LinkedIn prêtes à l'emploi, avec des textes rédigés, "
    "des hashtags adaptés et des conseils de publication. Chaque post couvre un angle différent "
    "de notre projet :")

bullet(doc, "Pourquoi le malgache est absent du numérique (storytelling engagé)")
bullet(doc, "Présentation de notre outil d'IA de traduction (annonce produit)")
bullet(doc, "L'impact humain sur des communautés rurales (inclusion)")
bullet(doc, "L'équipe derrière le projet (crédibilité)")
bullet(doc, "Notre vision à 5 ans (ambition)")
bullet(doc, "Le lancement de notre démo en ligne (milestone)")

doc.add_paragraph()
body(doc,
    "Ta mission est de :")

bullet(doc, "Adapter légèrement chaque texte si besoin (ajouter un détail personnel ou un exemple concret)",
       bold_prefix="1.  ")
bullet(doc, "Programmer ou publier un post par semaine sur la page LinkedIn de Maison du Numérique Madagascar",
       bold_prefix="2.  ")
bullet(doc, "Ajouter une image ou une courte vidéo si tu en as (captures de la démo, photo d'équipe, etc.)",
       bold_prefix="3.  ")
bullet(doc, "Répondre aux commentaires rapidement après publication pour booster la portée",
       bold_prefix="4.  ")
doc.add_paragraph()

# ── SECTION 5 ─────────────────────────────────────────────────────────────────
h2(doc, "5. Le timing est important")
doc.add_paragraph()

body(doc,
    "La candidature doit être finalisée. Chaque semaine sans publication est une semaine perdue. "
    "Idéalement, nous voulons avoir au moins 3 à 4 publications visibles sur la page avant de "
    "soumettre le lien LinkedIn dans le formulaire.")

doc.add_paragraph()
box(doc,
    "🎯 Objectif : commencer dès cette semaine avec le Post 1, "
    "et publier un post tous les 5-7 jours jusqu'à la soumission du dossier.")
doc.add_paragraph()

# ── CONCLUSION ────────────────────────────────────────────────────────────────
h2(doc, "En conclusion")
doc.add_paragraph()

body(doc,
    "Ce n'est pas du travail supplémentaire pour le plaisir de poster. C'est une exigence "
    "directe du dossier de candidature, et c'est l'une des preuves les plus visibles et les "
    "plus faciles à vérifier pour un jury.")

body(doc,
    "Notre projet est solide. Notre technologie existe et fonctionne. Nos partenaires nous "
    "soutiennent. Il nous reste à montrer tout cela au monde — et LinkedIn est l'une des "
    "fenêtres les plus efficaces pour le faire.")

doc.add_paragraph()
body(doc,
    "Merci Fenitra pour ton engagement dans cette démarche. On compte sur toi.")
doc.add_paragraph()
doc.add_paragraph()

body(doc, "Avec toute notre confiance,")
body(doc, "L'équipe MGVaovao – Maison du Numérique")

# ── SAVE ─────────────────────────────────────────────────────────────────────
output = "C:/Github Repositories/mgvaovao/LINGUA_Note_Fenitra_LinkedIn.docx"
doc.save(output)
print(f"Saved: {output}")
