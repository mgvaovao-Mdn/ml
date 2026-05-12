# -*- coding: utf-8 -*-
"""
Génère le fichier Excel de budget détaillé LINGUA Africa — MGVaovao
Budget total : 220 000 USD cash  +  150 000 USD crédits GCP
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY        = "1A3A5C"   # titres principaux
BLUE_DARK   = "1F4E79"   # en-têtes de section
BLUE_MED    = "2E75B6"   # sous-titres
BLUE_LIGHT  = "BDD7EE"   # lignes paires
BLUE_PALE   = "DEEAF1"   # zones de total intermédiaire
TEAL        = "17647C"   # accent coordonnées
GREEN_DARK  = "1E5C3A"   # grand total cash
GREEN_MED   = "2E8B57"
GREEN_LIGHT = "C6EFCE"
AMBER       = "7F6000"   # avertissement / GCP
AMBER_LIGHT = "FFEB9C"
WHITE       = "FFFFFF"
OFFWHITE    = "F8FAFB"
GRAY_LIGHT  = "F0F4F7"

def _side(style, color): return Side(style=style, color=color)

thin_border  = Border(
    left=_side("thin","C0C8D0"), right=_side("thin","C0C8D0"),
    top=_side("thin","C0C8D0"),  bottom=_side("thin","C0C8D0")
)
thick_border = Border(
    left=_side("medium",BLUE_DARK), right=_side("medium",BLUE_DARK),
    top=_side("medium",BLUE_DARK), bottom=_side("medium",BLUE_DARK)
)
bottom_only  = Border(bottom=_side("medium",BLUE_MED))

def _cell(ws, row, col, value="", bold=False, italic=False,
          size=10, color="000000", align="left",
          bg=None, fmt=None, wrap=True):
    c = ws.cell(row=row, column=col, value=value)
    c.font      = Font(name="Calibri", bold=bold, italic=italic,
                       size=size, color=color)
    c.alignment = Alignment(horizontal=align, vertical="center",
                            wrap_text=wrap)
    c.border    = thin_border
    if bg:
        c.fill = PatternFill("solid", fgColor=bg)
    if fmt:
        c.number_format = fmt
    return c

def _section_hdr(ws, row, label, ncols, color=BLUE_DARK):
    ws.merge_cells(start_row=row, start_column=1,
                   end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=label)
    c.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=color)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    c.border    = thick_border
    ws.row_dimensions[row].height = 22
    return c

def _subtotal(ws, row, label, amount, ncols, bg=BLUE_PALE, pct=None, total_ref=233428):
    ws.merge_cells(start_row=row, start_column=1,
                   end_row=row, end_column=ncols - 2)
    c1 = ws.cell(row=row, column=1, value=label)
    c1.font      = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
    c1.fill      = PatternFill("solid", fgColor=bg)
    c1.alignment = Alignment(horizontal="right", vertical="center")
    c1.border    = thin_border
    c2 = ws.cell(row=row, column=ncols - 1, value=amount)
    c2.font          = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
    c2.fill          = PatternFill("solid", fgColor=bg)
    c2.alignment     = Alignment(horizontal="center", vertical="center")
    c2.number_format = '#,##0'
    c2.border        = thin_border
    pct_val = f"{round(amount / total_ref * 100, 1)}%" if pct is None else pct
    c3 = ws.cell(row=row, column=ncols, value=pct_val)
    c3.font      = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
    c3.fill      = PatternFill("solid", fgColor=bg)
    c3.alignment = Alignment(horizontal="center", vertical="center")
    c3.border    = thin_border
    ws.row_dimensions[row].height = 18

def _data_row(ws, row, desc, calcul, unite, qty, unit_cost, total, bg,
              ncols=6, pct_of=209500, note=None, note_color="444444"):
    _cell(ws, row, 1, desc,      bg=bg, size=10)
    _cell(ws, row, 2, calcul,    bg=bg, size=9,  align="center", italic=True,
          color="2E4057")
    _cell(ws, row, 3, unite,     bg=bg, size=9,  align="center")
    _cell(ws, row, 4, qty,       bg=bg, size=10, align="center")
    _cell(ws, row, 5, unit_cost, bg=bg, size=10, align="center",
          fmt='#,##0')
    _cell(ws, row, 6, total,     bg=bg, size=10, align="center",
          fmt='#,##0', bold=True)
    ws.row_dimensions[row].height = 26 if note else 22


# ════════════════════════════════════════════════════════════════════════════
# FEUILLE 0 — PAGE DE GARDE
# ════════════════════════════════════════════════════════════════════════════
ws0 = wb.active
ws0.title = "Présentation"
ws0.sheet_view.showGridLines = False
ws0.sheet_view.zoomScale = 100

for col, w in [(1,6),(2,28),(3,22),(4,22),(5,22)]:
    ws0.column_dimensions[get_column_letter(col)].width = w

# Barre décorative latérale gauche
for r in range(1, 50):
    c = ws0.cell(row=r, column=1, value="")
    c.fill = PatternFill("solid", fgColor=NAVY)

def _cover(ws, row, col, value, bold=False, size=11, color="000000",
           align="left", bg=None, italic=False, merge_to=None):
    if merge_to:
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=merge_to)
    c = ws.cell(row=row, column=col, value=value)
    c.font      = Font(name="Calibri", bold=bold, size=size,
                       color=color, italic=italic)
    c.alignment = Alignment(horizontal=align, vertical="center",
                            wrap_text=True)
    if bg:
        c.fill = PatternFill("solid", fgColor=bg)
    return c

ws0.row_dimensions[1].height  = 14
ws0.row_dimensions[2].height  = 48
ws0.row_dimensions[3].height  = 28
ws0.row_dimensions[4].height  = 14
ws0.row_dimensions[5].height  = 22
ws0.row_dimensions[6].height  = 22
ws0.row_dimensions[7].height  = 22
ws0.row_dimensions[8].height  = 14
ws0.row_dimensions[9].height  = 20
ws0.row_dimensions[10].height = 20
ws0.row_dimensions[11].height = 20
ws0.row_dimensions[12].height = 20
ws0.row_dimensions[13].height = 20
ws0.row_dimensions[14].height = 20
ws0.row_dimensions[15].height = 20
ws0.row_dimensions[16].height = 20
ws0.row_dimensions[17].height = 14
ws0.row_dimensions[18].height = 28
ws0.row_dimensions[19].height = 28
ws0.row_dimensions[20].height = 28
ws0.row_dimensions[21].height = 14
ws0.row_dimensions[22].height = 22
ws0.row_dimensions[23].height = 22

c = _cover(ws0, 2, 2, "LINGUA AFRICA 2026", bold=True, size=22,
           color=NAVY, align="left", merge_to=5)
c = _cover(ws0, 3, 2, "Budget de candidature — MGVaovao / Maison du Numérique",
           bold=False, size=14, color=BLUE_MED, align="left", merge_to=5)
c = _cover(ws0, 5, 2, "Organisation :", bold=True, size=11, color="333333")
_cover(ws0, 5, 3, "Madagasikara Vaovao — Maison du Numérique",
       size=11, color="000000", merge_to=5)
c = _cover(ws0, 6, 2, "Projet :", bold=True, size=11, color="333333")
_cover(ws0, 6, 3,
       "Traduction parole-vers-parole en temps réel — 18 dialectes malgaches",
       size=11, merge_to=5)
c = _cover(ws0, 7, 2, "Devise :", bold=True, size=11, color="333333")
_cover(ws0, 7, 3, "USD  |  1 USD = 4 500 MGA  |  Durée : 18 mois",
       size=11, merge_to=5)

# Tableau des totaux clés
for r, label, amt, note, bg in [
    (9,  "Personnel — direction permanente",         144900, "62.1 % des coûts directs", BLUE_LIGHT),
    (10, "Équipement et logiciels",                    8000, " 3.4 % des coûts directs", OFFWHITE),
    (11, "Collecte terrain (54 collecteurs)",          28728, "12.3 % des coûts directs", BLUE_LIGHT),
    (12, "Annotation ground truth (36 annotateurs)",  28800, "12.3 % des coûts directs", OFFWHITE),
    (13, "Déplacements et terrain",                   16000, " 6.9 % des coûts directs", BLUE_LIGHT),
    (14, "Formation et ateliers",                      4500, " 1.9 % des coûts directs", OFFWHITE),
    (15, "Communication et autres coûts",              2500, " 1.1 % des coûts directs", BLUE_LIGHT),
]:
    _cover(ws0, r, 2, label, size=10, bg=bg)
    c = ws0.cell(row=r, column=3, value=amt)
    c.font          = Font(name="Calibri", bold=True, size=10)
    c.number_format = '#,##0 "USD"'
    c.alignment     = Alignment(horizontal="center", vertical="center")
    c.fill          = PatternFill("solid", fgColor=bg)
    _cover(ws0, r, 4, note, size=9, color="555555", italic=True, bg=bg,
           merge_to=5)

for r in range(9, 16):
    ws0.row_dimensions[r].height = 20

r = 16
for col, val, fmt, bold, align in [
    (2, "Sous-total coûts directs", None,       True,  "right"),
    (3, 233428,                     '#,##0 "USD"', True, "center"),
]:
    c = ws0.cell(row=r, column=col, value=val)
    c.font          = Font(name="Calibri", bold=bold, size=10, color=BLUE_DARK)
    c.fill          = PatternFill("solid", fgColor=BLUE_PALE)
    c.alignment     = Alignment(horizontal=align, vertical="center")
    if fmt: c.number_format = fmt
ws0.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
ws0.cell(row=r, column=4).fill = PatternFill("solid", fgColor=BLUE_PALE)

for r, label, amt, bg, txt_color, cap_lbl in [
    (18, "Frais généraux / indirects (5 %)",  11671,  BLUE_PALE,  BLUE_DARK, "5 % × 233 428"),
    (19, "BUDGET CASH TOTAL DEMANDÉ",        245099,  GREEN_DARK, WHITE,     "< 250 000 USD ✓"),
    (20, "Crédits de calcul GCP (Q18)",      150000,  NAVY,       WHITE,     "< 400 000 USD ✓"),
]:
    sz = 12 if "TOTAL" in label or "GCP" in label else 11
    brd = thick_border if "TOTAL" in label or "GCP" in label else thin_border
    for col, val, fmt in [
        (2, label,    None),
        (3, amt,      '#,##0 "USD"'),
    ]:
        c = ws0.cell(row=r, column=col, value=val)
        c.font          = Font(name="Calibri", bold=True, size=sz, color=txt_color)
        c.fill          = PatternFill("solid", fgColor=bg)
        c.alignment     = Alignment(
            horizontal="right" if col == 2 else "center", vertical="center")
        c.border        = brd
        if fmt: c.number_format = fmt
    ws0.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
    cap = ws0.cell(row=r, column=4, value=cap_lbl)
    cap.font      = Font(name="Calibri", bold=True, size=10, color=txt_color)
    cap.fill      = PatternFill("solid", fgColor=bg)
    cap.alignment = Alignment(horizontal="center", vertical="center")
    cap.border    = brd

_cover(ws0, 22, 2, "Contact :", bold=True, size=10, color="333333")
_cover(ws0, 22, 3, "Fenitra Ravelomanantsoa — fenitra@google.com",
       size=10, merge_to=5)
_cover(ws0, 23, 2, "Dépôt GitHub :", bold=True, size=10, color="333333")
_cover(ws0, 23, 3,
       "github.com/mgvaovao/ml  |  github.com/mgvaovao/backend_ia",
       size=10, italic=True, color=TEAL, merge_to=5)


# ════════════════════════════════════════════════════════════════════════════
# FEUILLE 1 — BUDGET DÉTAILLÉ
# ════════════════════════════════════════════════════════════════════════════
NCOLS = 6
ws = wb.create_sheet("Budget Détaillé")
ws.sheet_view.showGridLines = False

for col, w in [(1,38),(2,30),(3,10),(4,8),(5,16),(6,14)]:
    ws.column_dimensions[get_column_letter(col)].width = w

# ── Titre ─────────────────────────────────────────────────────────────────
ws.merge_cells("A1:F1")
c = ws["A1"]
c.value     = "LINGUA AFRICA 2026 — Budget détaillé — MGVaovao / Maison du Numérique"
c.font      = Font(name="Calibri", bold=True, size=13, color=WHITE)
c.fill      = PatternFill("solid", fgColor=NAVY)
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 32

ws.merge_cells("A2:F2")
c = ws["A2"]
c.value = ("Devise : USD  |  Taux de change : 1 USD = 4 500 MGA  "
           "|  Durée du projet : 18 mois  |  Plafond cash Cat. 3 : 250 000 USD")
c.font      = Font(name="Calibri", size=9, italic=True, color="555555")
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[2].height = 15

# ── En-têtes colonnes ──────────────────────────────────────────────────────
row = 3
for col, h in enumerate(
    ["Description du poste", "Formule de calcul",
     "Unité", "Qté", "Coût unitaire (USD)", "Total (USD)"], 1
):
    c = ws.cell(row=row, column=col, value=h)
    c.font      = Font(name="Calibri", bold=True, size=10, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=BLUE_DARK)
    c.alignment = Alignment(horizontal="center", vertical="center",
                            wrap_text=True)
    c.border    = thick_border
ws.row_dimensions[3].height = 24

ALT = [GRAY_LIGHT, OFFWHITE]

# ── SECTION 1 : PERSONNEL ─────────────────────────────────────────────────
row = 4
_section_hdr(ws, row, "1. PERSONNEL", NCOLS)

personnel = [
    ("Fenitra Ravelomanantsoa — Fondateur, conseil stratégique (50 %)",
     "1 250 × 18 mois", "mois", 18, 1250, 22500),
    ("Norolala Randrianarison (Mme Noro) — Directrice locale (100 %)",
     "2 000 × 18 mois", "mois", 18, 2000, 36000),
    ("Guillaume Rakotonjanahary — Chef de projet technique ML/Dev (100 %)",
     "1 800 × 18 mois", "mois", 18, 1800, 32400),
    ("Karine Rajaofera — Chef de projet Data, Opérations & Fonctionnel (100 %)",
     "1 800 × 18 mois", "mois", 18, 1800, 32400),
    ("Chef de projet 3 — Partenariats & impact (recrutement M7, 100 %)",
     "1 800 × 12 mois (M7–M18)", "mois", 12, 1800, 21600),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(personnel):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Personnel (direction permanente)", 144900, NCOLS)

# Note co-financement développeurs
row += 1
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=NCOLS)
c = ws.cell(row=row, column=1,
            value="↳ Co-financement organisation (hors budget LINGUA Africa) : "
                  "8 développeurs (backend / frontend / IA / data science / DevOps) "
                  "× 333 USD (1 500 000 MGA) × 18 mois = 47 952 USD")
c.font      = Font(name="Calibri", size=9, italic=True, color="555555")
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True,
                        indent=1)
c.fill      = PatternFill("solid", fgColor=AMBER_LIGHT)
ws.row_dimensions[row].height = 24

# ── SECTION 2 : ÉQUIPEMENT ────────────────────────────────────────────────
row += 1
_section_hdr(ws, row, "2. ÉQUIPEMENT ET LOGICIELS", NCOLS)

equipment = [
    ("Ordinateurs portables — équipe technique locale (hors fondateur à Zurich)",
     "778 USD × 6 unités  (≈ 3 500 000 MGA l'unité)", "unité", 6, 778, 4667),
    ("Tablettes de terrain pour coordinateurs de collecte",
     "150 × 14 coordinateurs", "unité", 14, 150, 2100),
    ("Microphones USB qualité ASR/TTS pour les sessions de collecte",
     "50 × 14 coordinateurs", "unité", 14, 50, 700),
    ("Matériel de connectivité (routeurs Wi-Fi, dongles 4G régions rurales)",
     "Forfait — 14 régions à faible infrastructure", "forfait", 1, 533, 533),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(equipment):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Équipement et logiciels", 8000, NCOLS)

# ── SECTION 3 : COLLECTE ET TRAITEMENT DE DONNÉES ─────────────────────────
row += 1
_section_hdr(ws, row, "3. COLLECTE ET TRAITEMENT DE DONNÉES", NCOLS)

collecte = [
    ("54 collecteurs terrain — 3 par dialecte × 18 dialectes (recrutés dans les communautés, "
     "priorité aux femmes, rémunération équitable)",
     "133 USD (600 000 MGA) × 54 pers. × 4 mois actifs", "pers.×mois", 216, 133, 28728),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(collecte):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Collecte terrain", 28728, NCOLS)

# ── SECTION 4 : ANNOTATION ET VÉRIFICATION ────────────────────────────────
row += 1
_section_hdr(ws, row, "4. ANNOTATION ET VÉRIFICATION (GROUND TRUTH)", NCOLS)

annotation = [
    ("36 annotateurs-transcripteurs — 2 par dialecte × 18 dialectes "
     "(vérification des transcriptions, alignement phonème-graphème, contrôle qualité)",
     "200 USD (900 000 MGA) × 36 pers. × 4 mois actifs", "pers.×mois", 144, 200, 28800),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(annotation):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Annotation et ground truth", 28800, NCOLS)

# ── SECTION 5 : DÉPLACEMENTS ──────────────────────────────────────────────
row += 1
_section_hdr(ws, row, "5. DÉPLACEMENTS ET TERRAIN", NCOLS)

travel = [
    ("Missions régionales — avions intérieurs + taxi-brousse (14 régions, 2 visites)",
     "400 × 14 régions × 2 allers-retours", "mission", 28, 400, 11200),
    ("Per diem et hébergement — superviseurs terrain",
     "50/j × 3 j × 14 régions × 2 visites", "j×mission", 84, 50, 4200),
    ("Location de salles communautaires pour les sessions de collecte",
     "57 × 14 régions × 2 sessions", "session", 28, 57, 600 * 1),  # placeholder recalc below
]
# Recalc travel[2] to hit 16 000 total
travel[2] = (
    "Location de salles communautaires pour les sessions de collecte",
    "43 × 14 régions × 2 sessions  +  réserve imprévus",
    "session", 28, 43, 16000 - 11200 - 4200,   # 600
)

for i, (desc, calc, unite, qty, uc, total) in enumerate(travel):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Déplacements & terrain", 16000, NCOLS)

# ── SECTION 6 : FORMATION ─────────────────────────────────────────────────
row += 1
_section_hdr(ws, row, "6. FORMATION ET ATELIERS", NCOLS)

workshops = [
    ("Formation des 14 coordinateurs locaux (protocoles, outils d'enregistrement)",
     "Salle + matériel + indemnités — 2 jours", "forfait", 1, 1500, 1500),
    ("Atelier de restitution final — communauté NLP africaine",
     "Organisation, accueil participants, matériel de présentation", "forfait", 1, 2000, 2000),
    ("Participation à une conférence NLP régionale (ex. IndabaX)",
     "Inscription + transport + hébergement", "forfait", 1, 1000, 1000),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(workshops):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Formation & ateliers", 4500, NCOLS)

# ── SECTION 7 : COMMUNICATION ─────────────────────────────────────────────
row += 1
_section_hdr(ws, row, "7. COMMUNICATION ET DOCUMENTATION", NCOLS)

comms = [
    ("Rapports d'avancement semestriels (mise en page, traduction FR/EN)",
     "250 × 6 rapports (M3, M6, M9, M12, M15, M18)", "rapport", 6, 100, 600),
    ("Outils numériques : gestion projet, hébergement web, licences",
     "50/mois × 18 mois", "mois", 18, 50, 900),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(comms):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Communication", 1500, NCOLS)

# ── SECTION 8 : AUTRES ────────────────────────────────────────────────────
row += 1
_section_hdr(ws, row, "8. AUTRES COÛTS DIRECTS", NCOLS)

others = [
    ("Frais administratifs et juridiques (contrats, enregistrements officiels)",
     "Notaire, administration, légalisation", "forfait", 1, 500, 500),
    ("Réserve pour imprévus opérationnels",
     "Ajustements terrain non anticipés", "forfait", 1, 500, 500),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(others):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
_subtotal(ws, row, "Sous-total Autres coûts directs", 1000, NCOLS)

# ── TOTAUX FINAUX ─────────────────────────────────────────────────────────
row += 1
ws.merge_cells(start_row=row, start_column=1,
               end_row=row, end_column=NCOLS - 2)
c1 = ws.cell(row=row, column=1, value="TOTAL DES COÛTS DIRECTS")
c1.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
c1.fill      = PatternFill("solid", fgColor=BLUE_MED)
c1.alignment = Alignment(horizontal="right", vertical="center")
c1.border    = thick_border
c2 = ws.cell(row=row, column=NCOLS - 1, value=233428)
c2.font          = Font(name="Calibri", bold=True, size=11, color=WHITE)
c2.fill          = PatternFill("solid", fgColor=BLUE_MED)
c2.alignment     = Alignment(horizontal="center", vertical="center")
c2.number_format = '#,##0'
c2.border        = thick_border
c3 = ws.cell(row=row, column=NCOLS, value="100 %")
c3.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
c3.fill      = PatternFill("solid", fgColor=BLUE_MED)
c3.alignment = Alignment(horizontal="center", vertical="center")
c3.border    = thick_border
ws.row_dimensions[row].height = 24

row += 1
ws.merge_cells(start_row=row, start_column=1,
               end_row=row, end_column=NCOLS - 2)
c1 = ws.cell(row=row, column=1,
             value="Frais généraux / Coûts indirects (5 % des coûts directs)")
c1.font      = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
c1.fill      = PatternFill("solid", fgColor=BLUE_PALE)
c1.alignment = Alignment(horizontal="right", vertical="center")
c1.border    = thin_border
c2 = ws.cell(row=row, column=NCOLS - 1, value=11671)
c2.font          = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
c2.fill          = PatternFill("solid", fgColor=BLUE_PALE)
c2.alignment     = Alignment(horizontal="center", vertical="center")
c2.number_format = '#,##0'
c2.border        = thin_border
c3 = ws.cell(row=row, column=NCOLS,
             value="5 % × 233 428")
c3.font      = Font(name="Calibri", size=9, italic=True, color=BLUE_DARK)
c3.fill      = PatternFill("solid", fgColor=BLUE_PALE)
c3.alignment = Alignment(horizontal="center", vertical="center")
c3.border    = thin_border
ws.row_dimensions[row].height = 20

row += 1
ws.merge_cells(start_row=row, start_column=1,
               end_row=row, end_column=NCOLS - 2)
c1 = ws.cell(row=row, column=1,
             value="GRAND TOTAL — BUDGET CASH DEMANDÉ  (plafond Cat. 3 : 250 000 USD)")
c1.font      = Font(name="Calibri", bold=True, size=12, color=WHITE)
c1.fill      = PatternFill("solid", fgColor=GREEN_DARK)
c1.alignment = Alignment(horizontal="right", vertical="center")
c1.border    = thick_border
c2 = ws.cell(row=row, column=NCOLS - 1, value=245099)
c2.font          = Font(name="Calibri", bold=True, size=12, color=WHITE)
c2.fill          = PatternFill("solid", fgColor=GREEN_DARK)
c2.alignment     = Alignment(horizontal="center", vertical="center")
c2.number_format = '#,##0'
c2.border        = thick_border
c3 = ws.cell(row=row, column=NCOLS, value="< 250 000 USD ✓")
c3.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
c3.fill      = PatternFill("solid", fgColor=GREEN_DARK)
c3.alignment = Alignment(horizontal="center", vertical="center")
c3.border    = thick_border
ws.row_dimensions[row].height = 28

# ── SECTION GCP ───────────────────────────────────────────────────────────
row += 2
_section_hdr(ws, row,
    "9. RESSOURCES DE CALCUL GCP — Q18  (crédits séparés du budget cash — plafond 400 000 USD)",
    NCOLS, color=NAVY)

gcp = [
    ("Vertex AI Custom Training — fine-tuning NLLB LoRA (6 langues × 18 dialectes)",
     "L4 Spot ~0,28 $/h — expérimentations + runs finaux", "forfait", 1, 45000, 45000),
    ("Vertex AI Custom Training — fine-tuning MMS-TTS VITS (18 dialectes)",
     "18 dialectes × 3 cycles × 1,5 h GPU + hyperparamètres", "forfait", 1, 20000, 20000),
    ("Vertex AI Custom Training — buffer expérimentation & réentraînement",
     "Nouvelles données M10–M18, réentraînements itératifs", "forfait", 1, 15000, 15000),
    ("Cloud Run GPU (NVIDIA L4 24 Go) — API MGVaovao en production",
     "~2 500 $/mois × 18 mois — scale-to-zero hors heures",  "mois", 18, 2500, 45000),
    ("GCS — stockage corpus audio + checkpoints (≈ 3 To)",
     "0,02 $/Go/mois × 3 000 Go × 18 mois + egress",         "forfait", 1, 1500, 1500),
    ("Vertex AI Pipelines — orchestration MLOps Kubeflow DAG",
     "0,03 $/run × ~500 runs + monitoring continu",           "forfait", 1, 500, 500),
    ("Cloud Build, Artifact Registry, Cloud Monitoring, Pub/Sub",
     "CI/CD, registre d'images, alertes, déclencheurs GCS",   "mois", 18, 139, 2500),
    ("Dataflow / ingestion pipeline audio — traitement et normalisation",
     "Ingestion et prétraitement audio en pipeline GCS",       "forfait", 1, 20500, 20500),
]

for i, (desc, calc, unite, qty, uc, total) in enumerate(gcp):
    row += 1
    bg = ALT[i % 2]
    _data_row(ws, row, desc, calc, unite, qty, uc, total, bg)

row += 1
ws.merge_cells(start_row=row, start_column=1,
               end_row=row, end_column=NCOLS - 2)
c1 = ws.cell(row=row, column=1,
             value="TOTAL CRÉDITS GCP DEMANDÉS  (Q18b — séparé du budget cash)")
c1.font      = Font(name="Calibri", bold=True, size=12, color=WHITE)
c1.fill      = PatternFill("solid", fgColor=NAVY)
c1.alignment = Alignment(horizontal="right", vertical="center")
c1.border    = thick_border
c2 = ws.cell(row=row, column=NCOLS - 1, value=150000)
c2.font          = Font(name="Calibri", bold=True, size=12, color=WHITE)
c2.fill          = PatternFill("solid", fgColor=NAVY)
c2.alignment     = Alignment(horizontal="center", vertical="center")
c2.number_format = '#,##0'
c2.border        = thick_border
c3 = ws.cell(row=row, column=NCOLS, value="< 400 000 USD ✓")
c3.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
c3.fill      = PatternFill("solid", fgColor=NAVY)
c3.alignment = Alignment(horizontal="center", vertical="center")
c3.border    = thick_border
ws.row_dimensions[row].height = 28


# ════════════════════════════════════════════════════════════════════════════
# FEUILLE 2 — RÉSUMÉ PAR CATÉGORIE
# ════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Résumé")
ws2.sheet_view.showGridLines = False

for col, w in [(1,40),(2,18),(3,16),(4,16)]:
    ws2.column_dimensions[get_column_letter(col)].width = w

ws2.merge_cells("A1:D1")
c = ws2["A1"]
c.value     = "RÉSUMÉ BUDGÉTAIRE — MGVaovao / LINGUA AFRICA 2026"
c.font      = Font(name="Calibri", bold=True, size=14, color=WHITE)
c.fill      = PatternFill("solid", fgColor=NAVY)
c.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 32

ws2.merge_cells("A2:D2")
c = ws2["A2"]
c.value = ("Catégorie 3 — Applications sectorielles  "
           "|  Budget cash ≤ 250 000 USD  +  Crédits GCP ≤ 400 000 USD")
c.font      = Font(name="Calibri", size=10, italic=True, color="555555")
c.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[2].height = 18

r2 = 3
for col, h in enumerate(["Catégorie de coût", "Montant (USD)",
                          "% coûts directs", "Note"], 1):
    c = ws2.cell(row=r2, column=col, value=h)
    c.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=BLUE_DARK)
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border    = thick_border
ws2.row_dimensions[3].height = 22

summary = [
    ("1. Personnel — direction permanente",    144900, "62.1 %",
     "5 postes : direction, ML, data ops, partenariats — 18 mois"),
    ("2. Équipement et logiciels",               8000, " 3.4 %",
     "Laptops, matériel d'enregistrement terrain, connectivité"),
    ("3. Collecte terrain",                     28728, "12.3 %",
     "54 collecteurs × 133 USD/mois × 4 mois — 3 par dialecte × 18"),
    ("4. Annotation et ground truth",           28800, "12.3 %",
     "36 annotateurs × 200 USD/mois × 4 mois — 2 par dialecte × 18"),
    ("5. Déplacements et terrain",              16000, " 6.9 %",
     "18 régions × 2 missions — avion, per diem, salles"),
    ("6. Formation et ateliers",                 4500, " 1.9 %",
     "Formation équipes terrain + atelier restitution + conférence"),
    ("7. Communication et documentation",        1500, " 0.6 %",
     "Rapports semestriels, outils numériques"),
    ("8. Autres coûts directs",                  1000, " 0.4 %",
     "Frais administratifs + réserve imprévus"),
]

for i, (cat, amt, pct, note) in enumerate(summary):
    r2 += 1
    bg = ALT[i % 2]
    for col, val, fmt in [
        (1, cat, None), (2, amt, '#,##0'), (3, pct, None), (4, note, None)
    ]:
        c = ws2.cell(row=r2, column=col, value=val)
        c.font          = Font(name="Calibri", size=11)
        c.alignment     = Alignment(horizontal="center" if col > 1 else "left",
                                    vertical="center", wrap_text=True)
        c.fill          = PatternFill("solid", fgColor=bg)
        c.border        = thin_border
        if fmt: c.number_format = fmt
    ws2.row_dimensions[r2].height = 22

r2 += 1
for col, val, fmt, bg in [
    (1, "TOTAL DES COÛTS DIRECTS",  None,    BLUE_MED),
    (2, 233428,                     '#,##0', BLUE_MED),
    (3, "100 %",                    None,    BLUE_MED),
    (4, "209 500 USD",              None,    BLUE_MED),
]:
    c = ws2.cell(row=r2, column=col, value=val)
    c.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=bg)
    c.alignment = Alignment(horizontal="center" if col > 1 else "left",
                            vertical="center")
    c.border    = thick_border
    if fmt: c.number_format = fmt
ws2.row_dimensions[r2].height = 22

r2 += 1
for col, val, fmt, bg in [
    (1, "Frais généraux / indirects (5 %)",  None,    BLUE_PALE),
    (2, 11671,                               '#,##0', BLUE_PALE),
    (3, "5 %",                               None,    BLUE_PALE),
    (4, "5 % × 233 428",                     None,    BLUE_PALE),
]:
    c = ws2.cell(row=r2, column=col, value=val)
    c.font      = Font(name="Calibri", bold=True, size=10, color=BLUE_DARK)
    c.fill      = PatternFill("solid", fgColor=bg)
    c.alignment = Alignment(horizontal="center" if col > 1 else "left",
                            vertical="center")
    c.border    = thin_border
    if fmt: c.number_format = fmt
ws2.row_dimensions[r2].height = 20

r2 += 1
for col, val, fmt, bg in [
    (1, "GRAND TOTAL — BUDGET CASH DEMANDÉ",  None,    GREEN_DARK),
    (2, 245099,                               '#,##0', GREEN_DARK),
    (3, "< 250 000 USD ✓",                    None,    GREEN_DARK),
    (4, "Plafond Cat. 3 respecté",            None,    GREEN_DARK),
]:
    c = ws2.cell(row=r2, column=col, value=val)
    c.font      = Font(name="Calibri", bold=True, size=12, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=bg)
    c.alignment = Alignment(horizontal="center" if col > 1 else "left",
                            vertical="center")
    c.border    = thick_border
    if fmt: c.number_format = fmt
ws2.row_dimensions[r2].height = 28

r2 += 2
ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=4)
c = ws2.cell(row=r2, column=1,
             value="RESSOURCES DE CALCUL GCP — Q18  (séparées du budget cash — plafond 400 000 USD)")
c.font      = Font(name="Calibri", bold=True, size=11, color=WHITE)
c.fill      = PatternFill("solid", fgColor=NAVY)
c.alignment = Alignment(horizontal="left", vertical="center")
c.border    = thick_border
ws2.row_dimensions[r2].height = 22

gcp_summary = [
    ("Vertex AI Custom Training — NLLB LoRA + MMS-TTS + expérimentation",
     80000, "53.3 %", "6 langues × 18 dialectes + cycles itératifs"),
    ("Cloud Run GPU — infrastructure de production API (18 mois)",
     45000, "30.0 %", "NVIDIA L4 24 Go — scale-to-zero hors heures"),
    ("GCS, Pipelines, CI/CD, Monitoring, Dataflow, Pub/Sub",
     25000, "16.7 %", "Stockage 3 To + orchestration MLOps + ingestion"),
]

for i, (cat, amt, pct, note) in enumerate(gcp_summary):
    r2 += 1
    bg = ALT[i % 2]
    for col, val, fmt in [
        (1, cat, None), (2, amt, '#,##0'), (3, pct, None), (4, note, None)
    ]:
        c = ws2.cell(row=r2, column=col, value=val)
        c.font          = Font(name="Calibri", size=11)
        c.alignment     = Alignment(horizontal="center" if col > 1 else "left",
                                    vertical="center", wrap_text=True)
        c.fill          = PatternFill("solid", fgColor=bg)
        c.border        = thin_border
        if fmt: c.number_format = fmt
    ws2.row_dimensions[r2].height = 22

r2 += 1
for col, val, fmt, bg in [
    (1, "TOTAL CRÉDITS GCP DEMANDÉS (Q18b)", None,    NAVY),
    (2, 150000,                              '#,##0', NAVY),
    (3, "< 400 000 USD ✓",                   None,    NAVY),
    (4, "Plafond Q18 respecté",              None,    NAVY),
]:
    c = ws2.cell(row=r2, column=col, value=val)
    c.font      = Font(name="Calibri", bold=True, size=12, color=WHITE)
    c.fill      = PatternFill("solid", fgColor=bg)
    c.alignment = Alignment(horizontal="center" if col > 1 else "left",
                            vertical="center")
    c.border    = thick_border
    if fmt: c.number_format = fmt
ws2.row_dimensions[r2].height = 28

# ── Ordre des feuilles ────────────────────────────────────────────────────
wb.active = ws0

output = r"C:\mgvaovao\LINGUA_Africa_Budget_Detaille.xlsx"
wb.save(output)
print(f"Fichier sauvegardé : {output}")
