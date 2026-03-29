# -*- coding: utf-8 -*-
"""
KVKK/GDPR Uyumlu Veri Saklama-Silme Takip Sistemi - Proje Raporu
244410059 Arda Enes Bas
"""

import os, io, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, PageBreak, HRFlowable, KeepTogether)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

# ─── Font Registration ────────────────────────────────────────────────────────
for name, path in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),
                    ('Arial-Italic','ariali.ttf'),('Arial-BI','arialbi.ttf')]:
    try:
        pdfmetrics.registerFont(TTFont(name, f'C:/Windows/Fonts/{path}'))
    except Exception:
        pass
try:
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                                   italic='Arial-Italic', boldItalic='Arial-BI')
except Exception:
    pass

# Matplotlib Turkish font
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ─── Directories ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, '_report_imgs')
os.makedirs(IMG, exist_ok=True)

W, H = A4   # 595.27 x 841.89 pts

# ─── Colour Palette ──────────────────────────────────────────────────────────
BLUE  = colors.HexColor('#1F4E79')
LBLUE = colors.HexColor('#2E75B6')
LLBLUE= colors.HexColor('#BDD7EE')
ORANGE= colors.HexColor('#C55A11')
HEADER_BG = colors.HexColor('#2E75B6')
ALT_ROW   = colors.HexColor('#DEEAF1')
WHITE = colors.white
BLACK = colors.black

# ─── Styles ──────────────────────────────────────────────────────────────────
def make_styles():
    s = {}
    base = dict(fontName='Arial', leading=14)
    s['title']   = ParagraphStyle('title',   fontName='Arial-Bold', fontSize=22,
                                   alignment=TA_CENTER, spaceAfter=8, textColor=BLUE)
    s['h1']      = ParagraphStyle('h1',      fontName='Arial-Bold', fontSize=14,
                                   spaceAfter=6, spaceBefore=12, textColor=BLUE)
    s['h2']      = ParagraphStyle('h2',      fontName='Arial-Bold', fontSize=12,
                                   spaceAfter=4, spaceBefore=8, textColor=LBLUE)
    s['body']    = ParagraphStyle('body',    fontName='Arial', fontSize=10,
                                   alignment=TA_JUSTIFY, leading=15, spaceAfter=6)
    s['bullet']  = ParagraphStyle('bullet',  fontName='Arial', fontSize=10,
                                   leading=14, leftIndent=16, spaceAfter=3,
                                   bulletIndent=6)
    s['center']  = ParagraphStyle('center',  fontName='Arial', fontSize=10,
                                   alignment=TA_CENTER, leading=13)
    s['bold']    = ParagraphStyle('bold',    fontName='Arial-Bold', fontSize=10,
                                   leading=13, spaceAfter=3)
    s['small']   = ParagraphStyle('small',   fontName='Arial', fontSize=8,
                                   alignment=TA_CENTER, leading=11)
    s['cover_uni']= ParagraphStyle('cover_uni', fontName='Arial-Bold', fontSize=14,
                                    alignment=TA_CENTER, textColor=BLUE, leading=20)
    s['cover_proj']=ParagraphStyle('cover_proj',fontName='Arial-Bold', fontSize=16,
                                    alignment=TA_CENTER, textColor=BLUE, leading=22,
                                    spaceBefore=20, spaceAfter=20)
    s['cover_sub'] =ParagraphStyle('cover_sub', fontName='Arial', fontSize=11,
                                    alignment=TA_CENTER, textColor=ORANGE, leading=16)
    s['scenario_label'] = ParagraphStyle('sc_label', fontName='Arial-Bold', fontSize=10,
                                          textColor=BLUE, spaceAfter=2)
    s['scenario_val']   = ParagraphStyle('sc_val',   fontName='Arial', fontSize=10,
                                          leading=14, leftIndent=12, spaceAfter=4)
    return s

ST = make_styles()

# ─── Table helpers ───────────────────────────────────────────────────────────
def header_style(col_widths, header_texts, data_rows, col_spans=None):
    """Return (table, style_list) ready to use."""
    header = [Paragraph(f'<b>{t}</b>', ST['small']) for t in header_texts]
    rows = [[Paragraph(str(c), ST['small']) for c in r] for r in data_rows]
    t = Table([header] + rows, colWidths=col_widths, repeatRows=1)
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HEADER_BG),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, ALT_ROW]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0),(-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ])
    return t, ts

def section_heading(text):
    return [Paragraph(text, ST['h1']), HRFlowable(width='100%', thickness=1.5,
            color=LBLUE, spaceAfter=6)]

def sub_heading(text):
    return [Paragraph(text, ST['h2'])]

def body(text):
    return Paragraph(text, ST['body'])

def bullet(text):
    return Paragraph(f'• {text}', ST['bullet'])

def sp(n=6):
    return Spacer(1, n)

# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

# ─── 1. Gantt Chart ──────────────────────────────────────────────────────────
def gen_gantt():
    tasks = [
        ("Proje Alan Tanımı",           0,  2),   # 15-16 Sub
        ("Kabul ve Kısıtlar",           2,  1),   # 17 Sub
        ("İş-Zaman Çizelgesi",          3,  1),   # 18 Sub
        ("Ekip Org. Semasi",            4,  1),   # 19 Sub
        ("Risk Tablosu",                5,  2),   # 20-21 Sub
        ("Proje Raporu Oluşturma",      7,  2),   # 22-23 Sub
        ("Kullanıcı Senaryoları",       9,  4),   # 24-27 Sub
        ("Etkileşim Diyagramları",      13,  2),   # 28 Sub - 1 Mar
        ("Sözleşmeler",                15,  1),   # 2 Mar
        ("Veritabanı Modelleme",       16,  2),   # 3-4 Mar
        ("Rapor Güncelleme",           18,  1),   # 5 Mar
        ("Kullanıcı Ekranları",        19,  2),   # 6-7 Mar
        ("Sınıf Diyagramı",             21,  1),   # 8 Mar
        ("Sıralama Diyagramı",          22,  1),   # 9 Mar
        ("Veritabanı Oluşturma",       23,  3),   # 10-12 Mar
        ("Ekran Tasarimi",             26,  1),   # 13 Mar
        ("Rapor Güncelleme 2",         27,  1),   # 14 Mar
        ("Kodlama",                    28,  6),   # 15-20 Mar
        ("Test",                       34,  2),   # 21-22 Mar
        ("Canlı'ya Alma",              36,  2),   # 23-24 Mar
    ]
    fig, ax = plt.subplots(figsize=(14, 7))
    colors_list = ['#2E75B6','#1F4E79','#C55A11','#70AD47','#ED7D31']
    for i, (name, start, dur) in enumerate(tasks):
        c = colors_list[i % len(colors_list)]
        ax.barh(i, dur, left=start, height=0.6, color=c, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in tasks], fontsize=8)
    ax.set_xlabel("Tarih (15 Şub 2026 - 24 Mar 2026)", fontsize=9)
    ax.set_title("Gantt Diyagramı - KVKK Retention Platform", fontsize=11, fontweight='bold', color='#1F4E79')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, 38)
    ticks  = [0, 7, 14, 21, 28, 35, 38]
    labels = ["15 Şub", "22 Şub", "01 Mar", "08 Mar", "15 Mar", "22 Mar", "24 Mar"]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=7)
    plt.tight_layout()
    path = os.path.join(IMG, 'gantt.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

# ─── 2. Class Diagram ────────────────────────────────────────────────────────
def draw_class_box(ax, x, y, w, h, title, attrs, methods=None, fc='#DEEAF1', tc='#1F4E79'):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                          facecolor=fc, edgecolor=tc, linewidth=1.2)
    ax.add_patch(box)
    line_h = h / (1 + len(attrs) + (len(methods) if methods else 0) + 2)
    ax.text(x + w/2, y + h - line_h*0.8, title, ha='center', va='center',
            fontsize=7, fontweight='bold', color=tc)
    ax.plot([x, x+w], [y + h - line_h*1.5]*2, color=tc, lw=0.8)
    for i, a in enumerate(attrs):
        ax.text(x+0.05, y + h - line_h*(2.2+i), f'+{a}', va='center', fontsize=5.5, color='#333333')
    if methods:
        yy = y + h - line_h*(2.2+len(attrs)+0.5)
        ax.plot([x, x+w], [yy]*2, color=tc, lw=0.5, linestyle='--')
        for j, m in enumerate(methods):
            ax.text(x+0.05, yy - line_h*(0.8+j), f'+{m}', va='center', fontsize=5, color='#555555')

def gen_class_diagram():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_facecolor('#F8FBFF')
    fig.patch.set_facecolor('#F8FBFF')
    ax.set_title("Sınıf Diyagramı - KVKK Retention Platform", fontsize=12, fontweight='bold', color='#1F4E79', pad=10)

    classes = [
        # (x, y, w, h, title, attrs, methods)
        (0.3, 6.5, 2.5, 3.2, "DataSubject",
         ["Id: int","FirstName: string","LastName: string","Email: string",
          "Password: string","CreatedAt: DateTime","KvkkConsentDate: DateTime",
          "IsAnonymized: bool"],
         ["Register()","AnonymizeAccount()"]),
        (3.2, 7.2, 2.4, 2.5, "User",
         ["Id: int","TcKimlikNo: string","PhoneNumber: string",
          "Email: string","IsKvkkAccepted: bool"], []),
        (6.2, 7.0, 2.5, 2.7, "PersonalDataEntry",
         ["Id: int","SubjectId: int","CategoryId: int","DataValue: string",
          "CollectedAt: DateTime","ExpirationDate: DateTime","Status: string"],
         ["Anonymize()"]),
        (9.2, 7.5, 2.4, 2.2, "DataCategory",
         ["Id: int","CategoryName: string","Description: string"], []),
        (12.2, 7.5, 2.5, 2.2, "RetentionPolicy",
         ["Id: int","CategoryId: int","RetentionMonths: int",
          "ActionType: string","IsActive: bool"], []),
        (0.3, 3.0, 2.5, 3.1, "ConsentLog",
         ["Id: int","SubjectId: int","CategoryId: int",
          "ConsentDate: DateTime","IsRevoked: bool","RevokedAt: DateTime"], []),
        (3.2, 3.2, 2.4, 2.8, "AuditLog",
         ["Id: int","TableName: string","RecordId: int","Action: string",
          "ActionDate: DateTime","PerformedBy: string","Details: string"], []),
        (6.2, 3.2, 2.5, 2.8, "JobPosting",
         ["Id: int","Title: string","Description: string",
          "Department: string","Status: string","CreatedAt: DateTime"], []),
        (9.2, 3.2, 2.4, 2.8, "JobApplication",
         ["Id: int","SubjectId: int","JobPostingId: int",
          "ApplicationDate: DateTime","Status: string"], []),
    ]

    for c in classes:
        draw_class_box(ax, *c)

    # Relationships (lines)
    rels = [
        ((1.55, 6.5),(1.55, 6.1),(0.3+1.25, 6.1)),   # DataSubject->ConsentLog
        ((1.55, 6.5),(3.7, 5.8),(3.7, 6.0)),           # DataSubject->AuditLog (approx)
        ((1.55, 6.5),(7.45, 5.8),(7.45, 6.0)),         # DataSubject->JobApp
        ((7.45, 6.5),(10.4, 6.5),(10.4, 7.5)),         # PersonalDataEntry->DataCategory
        ((10.4, 7.5),(13.4, 7.5)),                     # DataCategory->RetentionPolicy
    ]
    simple_arrows = [
        ((1.55, 6.5),(1.55+1.25, 6.0)),   # DS -> ConsentLog
        ((1.55, 6.5),(4.4,  6.0)),         # DS -> AuditLog
        ((1.55, 6.5),(9.7,  6.2),(9.7, 6.0)), # DS -> JobApp
        ((7.45, 7.0),(10.4, 7.5)),         # PDE -> DataCat
        ((10.4, 7.5),(13.45, 7.6)),        # DataCat -> RetPolicy
        ((7.45, 7.0),(4.4, 6.0)),          # PDE -> AuditLog (trigger)
        ((9.7,  3.2),(7.45, 3.2)),         # JobApp -> JobPosting
    ]
    for pts in simple_arrows:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[0], ys[0]),
                    arrowprops=dict(arrowstyle='->', color='#2E75B6', lw=1.0))

    # Legend
    ax.text(0.3, 0.5, "* Kesik cizgi: trigger iliskisi   -> : bagimlilk iliskisi",
            fontsize=7, color='gray', style='italic')
    plt.tight_layout()
    path = os.path.join(IMG, 'class_diag.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

# ─── 3. Use Case Diagram ─────────────────────────────────────────────────────
def draw_actor(ax, x, y, name):
    circle = plt.Circle((x, y+0.4), 0.18, color='#1F4E79', zorder=3)
    ax.add_patch(circle)
    ax.plot([x, x], [y+0.22, y-0.15], color='#1F4E79', lw=1.5)
    ax.plot([x-0.22, x+0.22], [y+0.05, y+0.05], color='#1F4E79', lw=1.5)
    ax.plot([x, x-0.2], [y-0.15, y-0.45], color='#1F4E79', lw=1.5)
    ax.plot([x, x+0.2], [y-0.15, y-0.45], color='#1F4E79', lw=1.5)
    ax.text(x, y-0.65, name, ha='center', va='top', fontsize=7.5, fontweight='bold', color='#1F4E79')

def draw_usecase(ax, x, y, rx, ry, text, fc='#DEEAF1', ec='#2E75B6'):
    ell = mpatches.Ellipse((x, y), rx*2, ry*2, facecolor=fc, edgecolor=ec, linewidth=1.2, zorder=2)
    ax.add_patch(ell)
    lines = textwrap.wrap(text, 18)
    for i, line in enumerate(lines):
        ax.text(x, y + (len(lines)-1)*0.1 - i*0.2, line, ha='center', va='center',
                fontsize=6.5, color='#1F4E79', zorder=3)

def gen_usecase_diagram():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_facecolor('#F8FBFF'); fig.patch.set_facecolor('#F8FBFF')
    ax.set_title("Use Case Diyagramı - KVKK Retention Platform", fontsize=12,
                  fontweight='bold', color='#1F4E79', pad=10)

    # System boundary
    sys_box = mpatches.FancyBboxPatch((1.8, 0.3), 10, 9.2, boxstyle="round,pad=0.1",
                                       facecolor='#EEF4FB', edgecolor='#2E75B6', linewidth=2, zorder=0)
    ax.add_patch(sys_box)
    ax.text(6.8, 9.35, "KVKK Retention & İş İlanı Platformu", ha='center', fontsize=9,
            fontweight='bold', color='#2E75B6')

    # Actors
    draw_actor(ax, 0.8, 7.0, "Admin")
    draw_actor(ax, 0.8, 2.5, "Aday")
    draw_actor(ax, 13.2, 5.0, "Veritabanı")

    # Use cases
    admin_ucs = [
        (5.5, 8.5, 2.0, 0.38, "Veri Saklama Politikası Yönetimi"),
        (5.5, 7.5, 2.0, 0.38, "Süresi Dolan Verileri İşle"),
        (5.5, 6.5, 2.0, 0.38, "Denetim Kaydi Görüntüle"),
        (5.5, 5.5, 2.0, 0.38, "Veri Sahibi Yönetimi"),
        (9.5, 8.5, 2.0, 0.38, "Admin Giris"),
    ]
    cand_ucs = [
        (5.5, 4.2, 2.0, 0.38, "Kayit ve KVKK Onay"),
        (5.5, 3.2, 2.0, 0.38, "İş İlanı Görüntüle ve Başvur"),
        (5.5, 2.2, 2.0, 0.38, "Profil Güncelle"),
        (5.5, 1.2, 2.0, 0.38, "Unutulma Hakkı Kullan"),
        (9.5, 3.5, 2.0, 0.38, "Aday Giris"),
    ]
    for uc in admin_ucs + cand_ucs:
        fc = '#FFE8D6' if 'Giris' in uc[4] else '#DEEAF1'
        draw_usecase(ax, uc[0], uc[1], uc[2], uc[3], uc[4], fc=fc)

    # Connections admin
    for uc in admin_ucs:
        ax.annotate('', xy=(uc[0]-uc[2], uc[1]), xytext=(1.2, 7.1),
                    arrowprops=dict(arrowstyle='-', color='#555555', lw=0.8))
    for uc in cand_ucs:
        ax.annotate('', xy=(uc[0]-uc[2], uc[1]), xytext=(1.2, 2.6),
                    arrowprops=dict(arrowstyle='-', color='#555555', lw=0.8))

    # DB connections
    for uc in [(5.5, 7.5),(5.5, 5.5),(5.5, 4.2),(5.5, 1.2)]:
        ax.annotate('', xy=(12.7, 5.1), xytext=(uc[0]+2.0, uc[1]),
                    arrowprops=dict(arrowstyle='->', color='#C55A11', lw=0.7,
                                   connectionstyle='arc3,rad=0.1'))

    # Include: Başvur -> Aday Giris
    ax.annotate('', xy=(9.5-2.0, 3.5), xytext=(5.5+2.0, 3.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=0.7, linestyle='dashed'))
    ax.text(7.6, 3.4, '<<include>>', fontsize=5.5, color='gray', style='italic')

    plt.tight_layout()
    path = os.path.join(IMG, 'usecase.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

# ─── 4. Sequence Diagram (Senaryo 1: Kayit) ─────────────────────────────────
def gen_sequence_diagram():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_facecolor('#F8FBFF'); fig.patch.set_facecolor('#F8FBFF')
    ax.set_title("Sıralama Diyagramı - Senaryo 1: Aday Kaydı ve KVKK Rızası",
                  fontsize=11, fontweight='bold', color='#1F4E79')

    lifelines = [
        (1.2,  "GUI\n(Tarayici)"),
        (3.5,  "AuthController"),
        (6.0,  "DataSubject"),
        (8.5,  "PersonalDataEntry"),
        (11.0, "AuditLog / ConsentLog"),
    ]
    top = 7.2; bot = 0.4
    for x, name in lifelines:
        ax.add_patch(FancyBboxPatch((x-0.55, top-0.1), 1.1, 0.4,
                                    boxstyle="round,pad=0.04", facecolor='#2E75B6',
                                    edgecolor='#1F4E79', linewidth=1))
        ax.text(x, top+0.1, name, ha='center', va='bottom', fontsize=7,
                color='white', fontweight='bold')
        ax.plot([x, x], [top-0.1, bot], color='#2E75B6', lw=0.8, linestyle='--')

    msgs = [
        (1.2, 3.5, 6.7,  "1. Register(model) POST"),
        (3.5, 6.0, 6.2,  "2. DataSubject.Add(subject)"),
        (6.0, 8.5, 5.7,  "3. PersonalDataEntry.Add(tcknEntry)"),
        (8.5, 6.0, 5.2,  "   tcknEntry saved"),
        (6.0, 8.5, 4.7,  "4. PersonalDataEntry.Add(phoneEntry)"),
        (8.5, 6.0, 4.2,  "   phoneEntry saved"),
        (6.0, 11.0,3.7,  "5. ConsentLog.Add(consentLog)"),
        (6.0, 11.0,3.2,  "6. AuditLog.Add('INSERT')"),
        (11.0,6.0, 2.7,  "   logs saved"),
        (3.5, 1.2, 2.2,  "7. RedirectToAction(Login)"),
        (1.2, 3.5, 1.7,  "8. HTTP 302 -> /Auth/Login"),
    ]
    for x1, x2, y, label in msgs:
        dx = x2 - x1
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle='->' if dx > 0 else '<-',
                                   color='#1F4E79', lw=1.0))
        mid = (x1+x2)/2
        ax.text(mid, y+0.08, label, ha='center', va='bottom', fontsize=6.5, color='#333')

    plt.tight_layout()
    path = os.path.join(IMG, 'sequence.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

# ─── 5. ER Diagram ───────────────────────────────────────────────────────────
def draw_er_table(ax, x, y, title, cols, w=2.2, row_h=0.28):
    h = row_h * (len(cols) + 1)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                 facecolor='#DEEAF1', edgecolor='#1F4E79', linewidth=1.2))
    ax.add_patch(plt.Rectangle((x, y+h-row_h), w, row_h,
                                 facecolor='#2E75B6', edgecolor='#1F4E79', linewidth=1.2))
    ax.text(x+w/2, y+h-row_h/2, title, ha='center', va='center',
            fontsize=7, fontweight='bold', color='white')
    for i, (pk, col) in enumerate(cols):
        yy = y + h - row_h*(i+2)
        prefix = 'PK ' if pk == 'PK' else ('FK ' if pk == 'FK' else '   ')
        ax.text(x+0.08, yy+row_h/2, f'{prefix}{col}', va='center',
                fontsize=5.8, color='#1F4E79' if pk == 'PK' else ('#C55A11' if pk == 'FK' else '#333'),
                fontweight='bold' if pk in ('PK','FK') else 'normal')

def gen_er_diagram():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_facecolor('#F8FBFF'); fig.patch.set_facecolor('#F8FBFF')
    ax.set_title("Veritabanı ER Diyagramı - KvkkRetentionDb", fontsize=12,
                  fontweight='bold', color='#1F4E79')

    tables = {
        'DataSubjects':   (0.3, 5.5, [('PK','Id int'),('','FirstName'),('','LastName'),
                                        ('','Email'),('','Password'),('','CreatedAt'),
                                        ('','IsAnonymized')]),
        'PersonalDataEntries':(3.8, 6.0,[('PK','Id int'),('FK','SubjectId'),('FK','CategoryId'),
                                          ('','DataValue'),('','CollectedAt'),
                                          ('','ExpirationDate'),('','Status')]),
        'DataCategories': (7.3, 7.0, [('PK','Id int'),('','CategoryName'),('','Description')]),
        'RetentionPolicies':(10.5,7.2,[('PK','Id int'),('FK','CategoryId'),
                                        ('','RetentionMonths'),('','ActionType'),('','IsActive')]),
        'ConsentLogs':    (0.3, 1.8, [('PK','Id int'),('FK','SubjectId'),('FK','CategoryId'),
                                        ('','ConsentDate'),('','IsRevoked'),('','RevokedAt')]),
        'AuditLogs':      (3.8, 2.2, [('PK','Id int'),('','TableName'),('','RecordId'),
                                        ('','Action'),('','ActionDate'),('','PerformedBy'),
                                        ('','Details')]),
        'JobPostings':    (7.3, 2.5, [('PK','Id int'),('','Title'),('','Description'),
                                        ('','Department'),('','Status'),('','CreatedAt')]),
        'JobApplications':(10.5,2.8, [('PK','Id int'),('FK','SubjectId'),('FK','JobPostingId'),
                                        ('','ApplicationDate'),('','Status')]),
        'Users':          (13.5,7.0, [('PK','Id int'),('','TcKimlikNo'),('','Email'),
                                        ('','IsKvkkAccepted')]),
    }
    centers = {}
    for name, (x, y, cols) in tables.items():
        draw_er_table(ax, x, y, name, cols)
        rh = 0.28
        h = rh * (len(cols)+1)
        centers[name] = (x+1.1, y+h/2)

    fks = [
        ('PersonalDataEntries','DataSubjects'),
        ('PersonalDataEntries','DataCategories'),
        ('RetentionPolicies',  'DataCategories'),
        ('ConsentLogs',        'DataSubjects'),
        ('ConsentLogs',        'DataCategories'),
        ('JobApplications',    'DataSubjects'),
        ('JobApplications',    'JobPostings'),
    ]
    for a, b in fks:
        ax.annotate('', xy=centers[b], xytext=centers[a],
                    arrowprops=dict(arrowstyle='->', color='#C55A11', lw=0.9,
                                   connectionstyle='arc3,rad=0.05'))
    plt.tight_layout()
    path = os.path.join(IMG, 'er.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

# ─── 6. Activity Diagrams ────────────────────────────────────────────────────
def gen_activity(title, nodes, edges, filename):
    """
    nodes: list of (id, x, y, text, shape)
      shape: 'start'|'end'|'process'|'decision'
    edges: list of (from_id, to_id, label)
    """
    fig, ax = plt.subplots(figsize=(7, 10))
    ax.set_xlim(0, 7); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_facecolor('#F8FBFF'); fig.patch.set_facecolor('#F8FBFF')
    ax.set_title(title, fontsize=9, fontweight='bold', color='#1F4E79', pad=6)

    pos = {}
    for nid, x, y, text, shape in nodes:
        pos[nid] = (x, y)
        if shape == 'start':
            ax.add_patch(plt.Circle((x,y), 0.22, color='#1F4E79', zorder=3))
        elif shape == 'end':
            ax.add_patch(plt.Circle((x,y), 0.25, color='white', ec='#1F4E79', lw=2.5, zorder=3))
            ax.add_patch(plt.Circle((x,y), 0.18, color='#1F4E79', zorder=4))
        elif shape == 'process':
            ax.add_patch(FancyBboxPatch((x-0.95, y-0.22), 1.9, 0.44,
                                         boxstyle="round,pad=0.04", facecolor='#DEEAF1',
                                         edgecolor='#2E75B6', lw=1.0, zorder=2))
            lines = textwrap.wrap(text, 22)
            for li, ln in enumerate(lines):
                ax.text(x, y+(len(lines)-1)*0.1-li*0.2, ln, ha='center', va='center',
                        fontsize=6, color='#1F4E79', zorder=3)
        elif shape == 'decision':
            diamond = plt.Polygon([[x,y+0.32],[x+0.7,y],[x,y-0.32],[x-0.7,y]],
                                    facecolor='#FFE8D6', edgecolor='#C55A11', lw=1.0, zorder=2)
            ax.add_patch(diamond)
            lines = textwrap.wrap(text, 15)
            for li, ln in enumerate(lines):
                ax.text(x, y+(len(lines)-1)*0.09-li*0.18, ln, ha='center', va='center',
                        fontsize=5.5, color='#C55A11', zorder=3)

    for fid, tid, label in edges:
        x1, y1 = pos[fid]
        x2, y2 = pos[tid]
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=0.9,
                                   connectionstyle='arc3,rad=0.0'))
        if label:
            mx, my = (x1+x2)/2+0.05, (y1+y2)/2+0.05
            ax.text(mx, my, label, fontsize=5.5, color='#C55A11', ha='left')

    plt.tight_layout()
    path = os.path.join(IMG, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

def gen_all_activity_diagrams():
    paths = []

    # Activity 1: Aday Kaydi
    nodes1 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Aday kayit formunu acar', 'process'),
        ('n2', 3.5, 7.8, 'Bilgileri doldurur (ad, soyad, email, TCKN, tel, sifre)', 'process'),
        ('d1', 3.5, 6.9, 'KVKK onayi verildi mi?', 'decision'),
        ('n3', 5.8, 6.9, 'Hata mesaji goster', 'process'),
        ('d2', 3.5, 5.9, 'Email kayitli mi?', 'decision'),
        ('n4', 5.8, 5.9, 'Email hatasi goster', 'process'),
        ('n5', 3.5, 5.0, 'DataSubject olustur', 'process'),
        ('n6', 3.5, 4.1, 'PersonalDataEntries kaydet (TCKN, tel)', 'process'),
        ('n7', 3.5, 3.2, 'ConsentLog + AuditLog olustur', 'process'),
        ('n8', 3.5, 2.3, 'Giris sayfasina yon.', 'process'),
        ('e',  3.5, 1.4, '', 'end'),
    ]
    edges1 = [
        ('s','n1',''), ('n1','n2',''), ('n2','d1',''),
        ('d1','n3','H'), ('n3','d1',''),
        ('d1','d2','E'), ('d2','n4','E'), ('n4','d2',''),
        ('d2','n5','H'), ('n5','n6',''), ('n6','n7',''), ('n7','n8',''), ('n8','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 1: Aday Kaydı ve KVKK Rızası", nodes1, edges1, 'act1.png'))

    # Activity 2: İş İlanı Başvurusu
    nodes2 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Aday "Acik Ilanlar" sayfasina gider', 'process'),
        ('n2', 3.5, 7.8, 'İlanı secip "Başvur" tıklari', 'process'),
        ('d1', 3.5, 6.9, 'Aktif başvuru var mi?', 'decision'),
        ('n3', 5.8, 6.9, 'Hata mesaji goster', 'process'),
        ('d2', 3.5, 5.9, 'İptal başvuru var mi?', 'decision'),
        ('n4', 5.8, 5.4, 'Başvuruyu yenile (Bekleniyor)', 'process'),
        ('n5', 3.5, 5.0, 'Yeni JobApplication olustur', 'process'),
        ('n6', 3.5, 4.1, 'Başvurularim sayfasina yon.', 'process'),
        ('e',  3.5, 3.2, '', 'end'),
    ]
    edges2 = [
        ('s','n1',''), ('n1','n2',''), ('n2','d1',''),
        ('d1','n3','E'), ('n3','n6',''),
        ('d1','d2','H'), ('d2','n4','E'), ('n4','n6',''),
        ('d2','n5','H'), ('n5','n6',''), ('n6','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 2: İş İlanı Görüntüle ve Başvur", nodes2, edges2, 'act2.png'))

    # Activity 3: Unutulma Hakkı
    nodes3 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Aday "Hesabimi Sil" secenegi tıklar', 'process'),
        ('d1', 3.5, 7.8, 'Onay dialogu: Onayli mi?', 'decision'),
        ('n2', 5.8, 7.8, 'İşlem iptal, panelde kal', 'process'),
        ('n3', 3.5, 6.8, 'CV dosyasi fiziksel silinir', 'process'),
        ('n4', 3.5, 5.9, 'PersonalDataEntries tamamen silindi', 'process'),
        ('n5', 3.5, 5.0, 'Başvurular İptal Edildi yapılır', 'process'),
        ('n6', 3.5, 4.1, 'Hesap anonimleştirilir', 'process'),
        ('n7', 3.5, 3.2, 'AuditLog: ANONYMIZE', 'process'),
        ('n8', 3.5, 2.3, 'Oturum kapatilir, anasayfaya', 'process'),
        ('e',  3.5, 1.4, '', 'end'),
    ]
    edges3 = [
        ('s','n1',''), ('n1','d1',''), ('d1','n2','H'), ('n2','e',''),
        ('d1','n3','E'), ('n3','n4',''), ('n4','n5',''), ('n5','n6',''),
        ('n6','n7',''), ('n7','n8',''), ('n8','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 3: Unutulma Hakkı / Veri Silme", nodes3, edges3, 'act3.png'))

    # Activity 4: Retention Politikası
    nodes4 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Admin politikalar sayfasina gider', 'process'),
        ('n2', 3.5, 7.8, 'Kategori, sure (ay), aksiyon belirler', 'process'),
        ('d1', 3.5, 6.9, 'Kategori için politika var mi?', 'decision'),
        ('n3', 5.8, 6.9, 'Mevcut politikayı. günceller/pasif yapar', 'process'),
        ('n4', 3.5, 5.9, 'Yeni RetentionPolicy kaydeder', 'process'),
        ('n5', 3.5, 5.0, 'Basari mesaji goster', 'process'),
        ('e',  3.5, 4.1, '', 'end'),
    ]
    edges4 = [
        ('s','n1',''), ('n1','n2',''), ('n2','d1',''),
        ('d1','n3','E'), ('n3','n4',''),
        ('d1','n4','H'), ('n4','n5',''), ('n5','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 4: Veri Saklama Politikası Yönetimi", nodes4, edges4, 'act4.png'))

    # Activity 5: Retention Job
    nodes5 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Admin Dashboard acar', 'process'),
        ('n2', 3.5, 7.8, '"Retention Job Çalıştır" tıklar', 'process'),
        ('n3', 3.5, 6.9, 'sp_ProcessExpiredData çalıştırilir', 'process'),
        ('d1', 3.5, 6.0, 'Süresi dolan veri var mi?', 'decision'),
        ('n4', 5.8, 5.5, 'Etkilenen kayit yok', 'process'),
        ('n5', 3.5, 5.1, 'Veri silinir veya anonimleştirilir', 'process'),
        ('n6', 3.5, 4.2, 'Her işlem için AuditLog', 'process'),
        ('n7', 3.5, 3.3, 'Basari mesaji goster', 'process'),
        ('e',  3.5, 2.4, '', 'end'),
    ]
    edges5 = [
        ('s','n1',''), ('n1','n2',''), ('n2','n3',''), ('n3','d1',''),
        ('d1','n4','H'), ('n4','n7',''),
        ('d1','n5','E'), ('n5','n6',''), ('n6','n7',''), ('n7','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 5: Süresi Dolan Verileri İşle", nodes5, edges5, 'act5.png'))

    # Activity 6: Audit Log
    nodes6 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Admin "Denetim Kayitlari" sayfasini acar', 'process'),
        ('d1', 3.5, 7.8, 'Kayit var mi?', 'decision'),
        ('n2', 5.8, 7.8, '"Kayit yok" mesaji goster', 'process'),
        ('n3', 3.5, 6.8, 'AuditLogs listelenir', 'process'),
        ('n4', 3.5, 5.9, 'Admin kayitlari inceler', 'process'),
        ('e',  3.5, 5.0, '', 'end'),
    ]
    edges6 = [
        ('s','n1',''), ('n1','d1',''), ('d1','n2','H'), ('n2','e',''),
        ('d1','n3','E'), ('n3','n4',''), ('n4','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 6: Denetim Kaydi Görüntüle", nodes6, edges6, 'act6.png'))

    # Activity 7: Profil Güncelleme
    nodes7 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Aday profil güncelleme formu acar', 'process'),
        ('n2', 3.5, 7.8, 'Ad, soyad, tel, eğitim, deneyim girer', 'process'),
        ('d1', 3.5, 6.9, 'CV dosyasi yuklendi mi?', 'decision'),
        ('n3', 5.8, 6.4, 'PDF formati doğru mu?', 'process'),
        ('n4', 3.5, 5.9, 'CV sunucuya kaydedilir', 'process'),
        ('n5', 3.5, 5.0, 'PersonalDataEntries güncellenir/eklenir', 'process'),
        ('n6', 3.5, 4.1, 'Basari mesaji goster', 'process'),
        ('e',  3.5, 3.2, '', 'end'),
    ]
    edges7 = [
        ('s','n1',''), ('n1','n2',''), ('n2','d1',''),
        ('d1','n3','E'), ('n3','n4',''),
        ('n4','n5',''), ('d1','n5','H'), ('n5','n6',''), ('n6','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 7: Aday Profil Güncelleme", nodes7, edges7, 'act7.png'))

    # Activity 8: Veri Sahibi Yönetimi
    nodes8 = [
        ('s',  3.5, 9.5, '', 'start'),
        ('n1', 3.5, 8.7, 'Admin veri sahipleri listesine gider', 'process'),
        ('n2', 3.5, 7.8, 'DataSubjects maskeli listelenir', 'process'),
        ('d1', 3.5, 6.9, 'İşlem secimi?', 'decision'),
        ('n3', 5.8, 6.9, 'Veriyi JSON disa aktar', 'process'),
        ('n4', 3.5, 5.9, 'ForceForgetSubject(email) cagrilir', 'process'),
        ('n5', 3.5, 5.0, 'Tum veriler anonimleştirilir + AuditLog', 'process'),
        ('n6', 3.5, 4.1, 'İşlem tamamlandi', 'process'),
        ('e',  3.5, 3.2, '', 'end'),
    ]
    edges8 = [
        ('s','n1',''), ('n1','n2',''), ('n2','d1',''),
        ('d1','n3','Disa Aktar'), ('n3','n6',''),
        ('d1','n4','Unut Hakki'), ('n4','n5',''), ('n5','n6',''), ('n6','e',''),
    ]
    paths.append(gen_activity("Etkileşim Diyagramı 8: Veri Sahibi Yönetimi", nodes8, edges8, 'act8.png'))

    return paths


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT DATA
# ═══════════════════════════════════════════════════════════════════════════════

TASK_ROWS = [
    ["Proje Alan Tanımı",              "15/02/2026", "2 gun",   "16/02/2026"],
    ["Kabul ve Kısıtlari Belirleme",   "17/02/2026", "1 gun",   "17/02/2026"],
    ["Proje İş-Zaman Çizelgesi",       "18/02/2026", "1 gun",   "18/02/2026"],
    ["Ekip Org. Şemasının Oluşturulm.", "19/02/2026", "1 gun",   "19/02/2026"],
    ["Risk Tablosunun Oluşturulması",  "20/02/2026", "2 gun",   "21/02/2026"],
    ["Proje Raporunun Oluşturulması",  "22/02/2026", "2 gun",   "23/02/2026"],
    ["Kullanıcı Senaryoları",          "24/02/2026", "4 gun",   "27/02/2026"],
    ["Etkileşim Diyagramları",          "28/02/2026", "2 gun",   "01/03/2026"],
    ["Sözleşmelerin Hazırlanması",     "02/03/2026", "1 gun",   "02/03/2026"],
    ["Veritabanının Modellenmesi",     "03/03/2026", "2 gun",   "04/03/2026"],
    ["Proje Raporu Güncellenmesi",     "05/03/2026", "1 gun",   "05/03/2026"],
    ["Kullanıcı Ekranları Modelleme",  "06/03/2026", "2 gun",   "07/03/2026"],
    ["Sınıf Diyagramı Çizimi",          "08/03/2026", "1 gun",   "08/03/2026"],
    ["Sıralama Diyagramı Çizimi",       "09/03/2026", "1 gun",   "09/03/2026"],
    ["Veritabanının Oluşturulması",    "10/03/2026", "3 gun",   "12/03/2026"],
    ["Ekran Tasarimi",                 "13/03/2026", "1 gun",   "13/03/2026"],
    ["Proje Raporu Güncelleme 2",      "14/03/2026", "1 gun",   "14/03/2026"],
    ["Kodlama İşlemi",                 "15/03/2026", "6 gun",   "20/03/2026"],
    ["Test",                           "21/03/2026", "2 gun",   "22/03/2026"],
    ["Canlıya Alma",                   "23/03/2026", "2 gun",   "24/03/2026"],
]

TASK_ASSIGN = [
    ["Proje alan tanımı",                         "244410059 Arda Enes Bas"],
    ["Kabul ve kısıtlar",                          "244410059 Arda Enes Bas"],
    ["Senaryo 1 - Aday Kaydı ve KVKK Rızası",       "244410059 Arda Enes Bas"],
    ["Senaryo 2 - İş İlanı ve Başvuru",            "244410059 Arda Enes Bas"],
    ["Senaryo 3 - Unutulma Hakkı",                 "244410059 Arda Enes Bas"],
    ["Senaryo 4 - Veri Saklama Politikası",        "244410059 Arda Enes Bas"],
    ["Senaryo 5 - Retention Job",                  "244410059 Arda Enes Bas"],
    ["Senaryo 6 - Denetim Kaydi",                  "244410059 Arda Enes Bas"],
    ["Senaryo 7 - Profil Güncelleme",              "244410059 Arda Enes Bas"],
    ["Senaryo 8 - Veri Sahibi Yönetimi",           "244410059 Arda Enes Bas"],
    ["Gantt Diyagramı",                             "244410059 Arda Enes Bas"],
    ["Etkinlik Diyagramları (1-8)",                 "244410059 Arda Enes Bas"],
    ["Use Case Diyagramı",                          "244410059 Arda Enes Bas"],
    ["Sözleşmeler",                                "244410059 Arda Enes Bas"],
    ["Sınıf Diyagramı",                             "244410059 Arda Enes Bas"],
    ["Sıralama Diyagramı",                          "244410059 Arda Enes Bas"],
    ["Risk Tablosu",                               "244410059 Arda Enes Bas"],
    ["Yazilimin Kodlanmasi",                       "244410059 Arda Enes Bas"],
    ["Dokumantasyon",                              "244410059 Arda Enes Bas"],
]

RISK_ROWS = [
    ["1",  "Müşterinin (paydaş) farklı beklentileri",           "Müşteri",      "Az",   "Yuksek", "Kullanıcı senaryoları oluşturulur"],
    ["2",  "KVKK gerekliliklerinin eksik anlasilmasi",          "Müşteri",      "Cok",  "Orta",   "Düzenli danismanlik toplantilariyap."],
    ["3",  "Proje için süreç tanımı olmaması",                  "Süreç",        "Cok",  "Dusuk",  "Proje süreç politikası oluşturulur"],
    ["4",  "Personelin süreçe gore atanmamis olmasi",           "Süreç",        "Orta", "Dusuk",  "Personel sürece göre atanmali"],
    ["5",  "Gelistirici standartlarinin teminedilmemesi",       "Süreç",        "Orta", "Dusuk",  "Kodlama standartlari dökümante edilmeli"],
    ["6",  "Düzensiz testler ve değerlendirmeler",              "Süreç",        "Cok",  "Dusuk",  "Test uzm. ile düzenli görüşme yapılmalı"],
    ["7",  "Kullanıcı ihtiyac degisimlerinin denetlenmemesi",   "Süreç",        "Cok",  "Orta",   "Değişiklik yönetim süreci oluşturulur"],
    ["8",  "ASP.NET Core 8 teknolojisinin yeni olmasi",         "Teknoloji",    "Az",   "Dusuk",  "Dusuk risk; izlenmesine gerek yok"],
    ["9",  "Entity Framework Core performans sorunlari",        "Teknoloji",    "Orta", "Orta",   "Sorgu optimizasyonu yapilmali"],
    ["10", "SQL Server erisim/lisans sorunu",                   "Teknoloji",    "Az",   "Dusuk",  "Dusuk risk; yedek DB plani hazirlan."],
    ["11", "Veri maskeleme algoritmalarinin yetersizligi",      "Teknoloji",    "Orta", "Orta",   "Maskeleme fonk. KVKK uzmaniyla test"],
    ["12", "Performans zorlamalari (cok kullanıcı)",            "Teknoloji",    "Az",   "Orta",   "Veritabanı index optimiz. yapılmalı"],
    ["13", "Gelistirme ortaminin olmaması",                     "Gelistirme",   "Cok",  "Dusuk",  "Gelistirme ortami onceden kurulmali"],
    ["14", "Cozumleme araçlarinin eksikligi",                   "Gelistirme",   "Cok",  "Dusuk",  "UML araclari onceden secilmeli"],
    ["15", "Stored procedure tahmin buyuklugu",                 "Urun Buyukl.", "Az",   "Dusuk",  "Dusuk; izlenmesine gerek yok"],
    ["16", "Veritabanı büyüklüğünün artması",                   "Urun Buyukl.", "Az",   "Dusuk",  "Dusuk; izlenmesine gerek yok"],
    ["17", "Cok sayida veri sahibi kaydi",                      "Urun Buyukl.", "Az",   "Orta",   "Uygun veritabanı tasarimi yapilmali"],
    ["18", "Gereksinim degisimlerinin fazlaligi",               "Urun Buyukl.", "Orta", "Orta",   "Degisiklik talep yönetimi yapilmali"],
    ["19", "Teslim tarihinin gerçekçi olmaması",                "Is Yönetimi",  "Cok",  "Dusuk",  "Gantt ile proje plani gözden geçirilmeli"],
    ["20", "KVKK uyumluluk eksikliginin tespit edilmemesi",     "Is Yönetimi",  "Cok",  "Dusuk",  "Uzman incelemesiyle rapor doğrulanmalı"],
]

SCENARIOS = [
    {
        "title": "KULLANIM OYKUSU-1: Aday Kaydı ve KVKK Rızası",
        "actor": "Aday",
        "stakeholders": "KVKK Retention Sistemi, Aday (Veri Sahibi)",
        "pre": [
            "E-posta adresi sistemde daha once kayitli olmamalidir.",
            "KVKK aydınlatma metni sisteme tanımı li olmalıdır.",
            "TC kimlik no, telefon ve sifre bilgileri hazirda olmalıdır.",
        ],
        "post": [
            "DataSubject kaydi veritabanına eklenmiştir.",
            "TC kimlik (10 yil) ve telefon (5 yil) verileri PersonalDataEntries'e kaydedilmiştir.",
            "ConsentLog kaydi oluşturulmuştur.",
            "AuditLog (INSERT) kaydi düşülmüştür.",
        ],
        "main": [
            "Aday kayit formunu acar.",
            "Ad, soyad, e-posta, TC kimlik no, telefon ve sifre bilgilerini girer.",
            "KVKK onay kutucugunu isaretler.",
            "Formu gonderir.",
            "Sistem DataSubject nesnesini olusturur ve veritabanına kaydeder.",
            "TC kimlik ve telefon için PersonalDataEntry kayitlari oluşturulur.",
            "ConsentLog ve AuditLog kayitlari oluşturulur.",
            "Aday giris sayfasina yönlendirilir.",
        ],
        "alt": [
            "1a. E-posta adresi sistemde kayitliysa:\n   1. 'Bu email zaten kayitli' uyarisi gösterilir.\n   2. Farklı e-posta girilmesi istenir.",
            "3a. KVKK onayi verilmemisse:\n   1. Sistem kaydi reddeder.\n   2. Onay zorunlu uyarisi gösterilir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-2: İş İlanı Görüntüleme ve Başvuru",
        "actor": "Aday",
        "stakeholders": "KVKK Retention Sistemi, Aday, İş İlanı Modulu",
        "pre": [
            "Aday sisteme giris yapmis olmalıdır.",
            "Sistemde en az bir acik (status='Acik') iş ilanı bulunmalidir.",
        ],
        "post": [
            "JobApplication kaydi 'Bekleniyor' statusuyle veritabanına eklenmiştir.",
        ],
        "main": [
            "Aday 'Acik Ilanlar' sayfasina gider.",
            "Sistem acik ilanlari listeler (daha once başvurulmuslari gizler).",
            "Aday bir ilanı secip 'Başvur' butonuna tıklar.",
            "Sistem JobApplication nesnesi olusturur ve veritabanına kaydeder.",
            "Aday 'Başvurularim' sayfasina yönlendirilir.",
        ],
        "alt": [
            "3a. Ilana aktif başvuru mevcutsa:\n   1. 'Aktif başvurunuz bulunuyor' hatasi gösterilir.",
            "3b. İptal edilmis başvuru varsa:\n   1. Mevcut başvuru 'Bekleniyor' statusune güncellenir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-3: Unutulma Hakkı / Veri Silme",
        "actor": "Aday",
        "stakeholders": "KVKK Retention Sistemi, Aday (KVKK Madde 11)",
        "pre": [
            "Aday sisteme giris yapmis olmalıdır.",
        ],
        "post": [
            "Tum PersonalDataEntries kayitlari veritabanından silinmiştir.",
            "CV dosyasi fiziksel olarak sunucudan imha edilmistir.",
            "Tum başvurular 'İptal Edildi' yapılmıştır.",
            "Hesap anonimleştirilmiştir (email, ad, soyad degistirilmistir).",
            "AuditLog (ANONYMIZE) kaydi düşülmüştür.",
            "Oturum kapatilmistir.",
        ],
        "main": [
            "Aday profil sayfasinda 'Hesabimi Sil / Unutulma Hakkı' butonuna tıklar.",
            "Onay dialogu gösterilir.",
            "Aday onaylar.",
            "Sistem fiziksel CV dosyasini sunucudan siler.",
            "PersonalDataEntries kayitlari veritabanından kalıcı olarak silinir.",
            "Tum is başvurulari 'İptal Edildi' yapılır.",
            "Hesap anonimleştirilir (ad='Silinmis', soyad='Kullanıcı', email=deleted_xxx@anonymized.local).",
            "AuditLog (ANONYMIZE) kaydi oluşturulur.",
            "Oturum kapatilir ve anasayfaya yönlendirilir.",
        ],
        "alt": [
            "2a. Aday onay dialogunda iptal ederse:\n   1. İşlem durdurulur, aday panelinde kalir.",
            "4a. CV dosyasi mevcut degilse:\n   1. Dosya silme adimi atlanir, diger adimlar devam eder.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-4: Admin - Veri Saklama Politikası Yönetimi",
        "actor": "Admin (Sistem Yöneticisi)",
        "stakeholders": "KVKK Retention Sistemi, Admin",
        "pre": [
            "Admin sisteme giris yapmis olmalıdır.",
            "Sistemde veri kategorileri (DataCategories) tanimli olmalıdır.",
        ],
        "post": [
            "RetentionPolicy kaydi veritabanına eklenmiş/güncellenmiştir.",
        ],
        "main": [
            "Admin veri saklama politikalari sayfasina gider.",
            "Yapmak istedigi işlemi (ekle/güncelle/pasif et) belirler.",
            "Kategori, saklama süresi (ay) ve aksiyon turunu (DELETE/ANONYMIZE) girer.",
            "Formu kaydeder.",
            "Sistem RetentionPolicy tablosuna yazar.",
        ],
        "alt": [
            "3a. Ayni kategori için politika zaten mevcutsa:\n   1. Admin mevcut politikayı günceller veya pasif hale getirir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-5: Admin - Süresi Dolan Verilerin İşlenmesi",
        "actor": "Admin (Sistem Yöneticisi)",
        "stakeholders": "KVKK Retention Sistemi, Admin, SQL Server",
        "pre": [
            "Admin sisteme giris yapmis olmalıdır.",
            "vw_ExpiredDataForAction view'inde süresi dolmus veri olmalıdır.",
        ],
        "post": [
            "sp_ProcessExpiredData sakli yordami basariyla çalıştırilmistir.",
            "Süresi dolan veriler politikayıa gore silinmis veya anonimleştirilmiştir.",
            "Her işlem için AuditLog kaydi oluşturulmuştur.",
        ],
        "main": [
            "Admin ana panelde (Dashboard) aktif veri ve bekleyen silme istatistiklerini gorur.",
            "'Retention Job Çalıştır' butonuna tıklar.",
            "Sistem EXEC sp_ProcessExpiredData komutunu SQL Server'da çalıştırir.",
            "Sakli yordami politikayıa gore süresi dolmus verileri siler/anonimleştirir.",
            "Dashboard yenilenir ve basari mesaji gösterilir.",
        ],
        "alt": [
            "3a. Islenecek veri yoksa:\n   1. İşlem calisir ama kayit etkilenmez.\n   2. Admin bilgilendirilir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-6: Admin - Denetim Kaydı Görüntüleme",
        "actor": "Admin (Sistem Yöneticisi)",
        "stakeholders": "KVKK Retention Sistemi, Admin",
        "pre": [
            "Admin sisteme giris yapmis olmalıdır.",
            "AuditLogs tablosunda kayitlar bulunmalidir.",
        ],
        "post": [
            "Denetim kayitlari kronolojik siralamayla ekranda listelenmi stir.",
        ],
        "main": [
            "Admin 'Denetim Kayitlari' menusu ne tıklar.",
            "Sistem AuditLogs tablosundaki tum kayitlari listeler.",
            "Admin; işlem turu, tarih, yapan kisi ve detaylar sutunlarini inceler.",
        ],
        "alt": [
            "2a. Hic kayit yoksa:\n   1. 'Henuz kayit bulunmamaktadir' bilgisi gösterilir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-7: Aday - Profil Güncelleme",
        "actor": "Aday",
        "stakeholders": "KVKK Retention Sistemi, Aday",
        "pre": [
            "Aday sisteme giris yapmis olmalıdır.",
        ],
        "post": [
            "Ilgili PersonalDataEntries kayitlari güncellenmiş/eklenmiştir.",
            "CV dosyasi yüklenmiş ise fiziksel dosya sunucuda saklanmistir.",
            "Degisiklikler veritabanına kaydedilmiştir.",
        ],
        "main": [
            "Aday 'Profilim' sayfasindaki güncelleme formunu acar.",
            "Ad, soyad, telefon, eğitim, is deneyimi bilgilerini günceller.",
            "Istege bagli olarak CV dosyasi (PDF) yukler.",
            "Formu gonderir.",
            "Sistem verileri KVKK kategorilerine uygun PersonalDataEntries olarak kaydeder.",
            "Basari mesaji gösterilir.",
        ],
        "alt": [
            "3a. CV dosyasi PDF formati disindaysa:\n   1. Dosya reddedilir, hata mesaji gösterilir.",
        ],
    },
    {
        "title": "KULLANIM OYKUSU-8: Admin - Veri Sahibi Yönetimi",
        "actor": "Admin (Sistem Yöneticisi)",
        "stakeholders": "KVKK Retention Sistemi, Admin",
        "pre": [
            "Admin sisteme giris yapmis olmalıdır.",
            "DataSubjects tablosunda en az bir kayit bulunmalidir.",
        ],
        "post": [
            "Veri sahipleri listesi görüntülenmiş veya",
            "Kişisel veriler JSON formatinda disa aktarilmis veya",
            "Zorla unutulma hakki uygulanmıştır.",
        ],
        "main": [
            "Admin 'Veri Sahipleri' sayfasina gider.",
            "Sistem DataSubject kayitlarini maskeli bilgilerle listeler.",
            "Admin bir veri sahibini secer.",
            "Yapmak istedigi işlemi belirler (liste goru, disa aktar, unutulma hakki).",
            "Disa aktarma: Tum veri JSON formatinda indirilir.",
            "Unutulma Hakkı: ForceForgetSubject() cagrilir, tum veriler anonimleştirilir.",
            "İşlem AuditLog'a kaydedilir.",
        ],
        "alt": [
            "5a. Disa aktarma sirasinda veri bulunamazsa:\n   1. Bos JSON nesnesi donulur.",
            "6a. Veri sahibi bulunamazsa:\n   1. 'Kullanıcı bulunamadi' hatasi gösterilir.",
        ],
    },
]

CONTRACTS = [
    {
        "no": "1", "name": "Aday Kaydı ve KVKK Rızası",
        "op": "Register(RegisterViewModel model) - AuthController",
        "ref": "Kullanim Öyküsü 1",
        "pre": ["E-posta sisteme kayitli olmamalidir.", "KVKK onayi verilmis olmalıdır.", "TCKN ve telefon bilgileri girilmis olmalıdır."],
        "post": ["DataSubject veritabanına eklenmiştir.", "PersonalDataEntries (TCKN, telefon) kaydedilmiştir.", "ConsentLog ve AuditLog oluşturulmuştur."],
    },
    {
        "no": "2", "name": "İş İlanı Başvurususu",
        "op": "ApplyToJob(int jobId) - CandidatePanelController",
        "ref": "Kullanim Öyküsü 2",
        "pre": ["Aday sisteme giris yapmis olmalıdır.", "Başvurulacak ilana aktif başvuru olmamalidir."],
        "post": ["JobApplication 'Bekleniyor' statusuyle kaydedilmiştir."],
    },
    {
        "no": "3", "name": "Unutulma Hakkı / Hesap Silme",
        "op": "DeleteMyAccount() - CandidatePanelController",
        "ref": "Kullanim Öyküsü 3",
        "pre": ["Aday sisteme giris yapmis olmalıdır."],
        "post": ["PersonalDataEntries silinmiştir.", "CV fiziksel olarak imha edilmistir.", "Hesap anonimleştirilmiştir.", "AuditLog (ANONYMIZE) oluşturulmuştur."],
    },
    {
        "no": "4", "name": "Veri Saklama Politikası Yönetimi",
        "op": "RetentionPolicyInsert/Update/Delete(RetentionPolicy p) - RetentionPoliciesController",
        "ref": "Kullanim Öyküsü 4",
        "pre": ["Admin sisteme giris yapmis olmalıdır.", "DataCategories tablosunda kategoriler tanimli olmalıdır."],
        "post": ["RetentionPolicy kaydi veritabanına eklenmiş/güncellenmiştir."],
    },
    {
        "no": "5", "name": "Süresi Dolan Verilerin İşlenmesi",
        "op": "RunRetentionJob() - DashboardController",
        "ref": "Kullanim Öyküsü 5",
        "pre": ["Admin sisteme giris yapmis olmalıdır.", "vw_ExpiredDataForAction view'inde süresi dolmus veri olmalıdır."],
        "post": ["sp_ProcessExpiredData çalıştırilmistir.", "Etkilenen veriler silinmis/anonimleştirilmiştir.", "AuditLog kaydi oluşturulmuştur."],
    },
    {
        "no": "6", "name": "Denetim Kaydı Görüntüleme",
        "op": "Index() - AuditLogsController",
        "ref": "Kullanim Öyküsü 6",
        "pre": ["Admin sisteme giris yapmis olmalıdır."],
        "post": ["AuditLog kayitlari ekranda listelenmiştir."],
    },
    {
        "no": "7", "name": "Profil Güncelleme",
        "op": "UpdateProfile(string firstName, string lastName, ...) - CandidatePanelController",
        "ref": "Kullanim Öyküsü 7",
        "pre": ["Aday sisteme giris yapmis olmalıdır."],
        "post": ["PersonalDataEntries güncellenmis/eklenmiştir.", "CV PDF ise fiziksel olarak sunucuya kaydedilmiştir."],
    },
    {
        "no": "8", "name": "Veri Sahibi Yönetimi",
        "op": "ForceForgetSubject(string email, string reason) - DashboardController\nExportUserData(int subjectId, string email) - DataSubjectsController",
        "ref": "Kullanim Öyküsü 8",
        "pre": ["Admin sisteme giris yapmis olmalıdır.", "DataSubjects tablosunda kayit bulunmalidir."],
        "post": ["Secilen işlem gerceklestirilmistir.", "AuditLog kaydi oluşturulmuştur."],
    },
]

SCREENSHOTS = [
    "Anasayfa - Son is ilanlari ve navigasyon menusu",
    "Giris Sayfasi - E-posta ve sifre formu (Admin / Aday)",
    "Kayit Sayfasi - KVKK onay kutucugunu icerir",
    "Admin Dashboard - Aktif veri sayisi, bekleyen silme, grafikler",
    "Veri Sahipleri - Maskeli TCKN ve telefon bilgileri listesi",
    "Aday Paneli - Profil bilgileri ve veri kategorileri",
    "Acik Ilanlar - Başvurulmamış aktif pozisyonlar listesi",
    "Denetim Kayitlari - INSERT/UPDATE/ANONYMIZE işlem gecmisi",
    "Riza Kayitlari - Aktif onay kayitlari listesi",
]


# ═══════════════════════════════════════════════════════════════════════════════
# PDF BUILD
# ═══════════════════════════════════════════════════════════════════════════════

def img_flow(path, w=None, h=None):
    if w and h:
        return Image(path, width=w, height=h)
    elif w:
        from PIL import Image as PILImage
        try:
            im = PILImage.open(path)
            ratio = im.height / im.width
            return Image(path, width=w, height=w*ratio)
        except Exception:
            return Image(path, width=w)
    return Image(path)

def build_pdf(out_path, diagram_paths):
    gantt_p, class_p, uc_p, seq_p, er_p, act_paths = (
        diagram_paths['gantt'], diagram_paths['class'], diagram_paths['usecase'],
        diagram_paths['sequence'], diagram_paths['er'], diagram_paths['activities']
    )
    W_inner = 17*cm

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2.5*cm, bottomMargin=2*cm,
                             title="KVKK Retention Platform Proje Raporu")
    story = []

    # ── COVER PAGE ────────────────────────────────────────────────────────────
    story += [sp(30)]
    story.append(Paragraph("T.C.", ST['cover_uni']))
    story.append(Paragraph("KASTAMONU UNIVERSITESi", ST['cover_uni']))
    story.append(Paragraph("MUHENDISLiK MiMARLIK FAKULTESi", ST['cover_uni']))
    story.append(Paragraph("BiLGiSAYAR MUHENDISLiGi", ST['cover_uni']))
    story += [sp(40)]
    story.append(Paragraph("BM302 VERi TABANI YONETiMi", ST['h2']))
    story.append(Paragraph("KVKK/GDPR Uyumlu Veri Saklama-Silme<br/>(Retention) Takip Sistemi", ST['cover_proj']))
    story += [sp(30)]
    story.append(Paragraph("<b>PROJE SAHiBi</b>", ParagraphStyle('ph', fontName='Arial-Bold', fontSize=12, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("244410059 Arda Enes Bas", ST['cover_sub']))
    story += [sp(60)]
    story.append(Paragraph("KASTAMONU<br/>2026", ST['center']))
    story.append(PageBreak())

    # ── PROJE ALAN TANIMI ─────────────────────────────────────────────────────
    story += section_heading("Proje Alan Tanımı")
    story.append(body(
        "Günümüzde veri koruma mevzuatları, şirketlerin kişisel verileri nasil sakladığıni, "
        "işlediğini ve sildigi ni duzenleme altina almaktadir. Turkiye'de 6698 sayili Kişisel "
        "Verilerin Korunmasi Kanunu (KVKK) ve Avrupa Birligi'nde Genel Veri Koruma Tuzugu (GDPR) "
        "bu duzenleme lerin en önemlileridir. Kurumlar, sahip olduklar kişisel verileri yasada "
        "belirlenen sureler boyunca saklamak, bu sureler dolduğundan otomatik olarak silmek veya "
        "anonimle stirmek ve butun bu işlemleri kayit altina almak zorundadir."
    ))
    story.append(body(
        "Bu proje kapsaminda gelistirilen KVKK/GDPR Uyumlu Veri Saklama-Silme Takip Sistemi, "
        "bir iş ilanı platformuyla entegre edilmis kapsamli bir uyumluluk yönetim sistemidir. "
        "Sistem sayesinde:"
    ))
    bullets1 = [
        "Adaylar kayit olurken KVKK aydınlatma metni ve riza onayi elektronik ortamda alinir ve kayit altina alinir.",
        "Toplanan kişisel veriler (TC kimlik, telefon, eğitim, CV vb.) kategorilere ayrilarak her kategori için ayri saklama süresi politikası tanimlanabilir.",
        "Saklama süresi dolan veriler admin onayiyla sp_ProcessExpiredData sakli yordami araciligiyla otomatik olarak silinir veya anonimleştirilir.",
        "Adaylar KVKK Madde 11 kapsaminda 'Unutulma Hakkı'ni kullanarak tum kişisel verilerini ve fiziksel dosyalarini sisteme siletebilir.",
        "Sistemdeki her veri işleme işlemi AuditLog tablosuna kaydedilerek denetim izi oluşturulur.",
        "Yöneticiler, aktif riza kayitlarini, süresi dolan verileri ve denetim izlerini merkezi bir panelden takip edebilir.",
    ]
    for b in bullets1:
        story.append(bullet(b))
    story += [sp(10)]

    # ── KABUL VE KISITLAR ─────────────────────────────────────────────────────
    story += section_heading("Kabul ve Kısıtlar")
    story.append(body(
        "Sistemin doğru çalışabilmesi için aşağıdaki kabuller ve kısıtlar geçerlidir:"
    ))
    kısıtlar = [
        "SQL Server veritabanınin kurulu ve erişilebilir olduğu kabul edilmektedir (MSSQLSERVER01 ornegi).",
        "Sistemde en az bir admin kullanıcısinin (admin@admin.com) tanimli olduğu varsayilmaktadir.",
        "Adaylarin KVKK metnini okuyarak onaylayarak kayit olduğu kabul edilmektedir.",
        "TC Kimlik Numarasinin doğru olduğuna dair kimlik doğrulama entegrasyonu kapsam disindadir.",
        "Is ilanlarinin yöneticiler tarafindan sisteme eklendigi varsayilmaktadir.",
        "Retention job yalnizca admin tarafindan manuel olarak tetiklenebilmektedir.",
        "CV dosyalarinin PDF formatinda olduğu kabul edilmekte; baska format kabul edilmemektedir.",
        "Sistemin HTTPS protokolu uzerinden erisildigi varsayilmaktadir.",
        "Cookie bazli kimlik doğrulamanin 30 dakika zaman asimi uygulandigi kabul edilmektedir.",
    ]
    for k in kısıtlar:
        story.append(bullet(k))
    story.append(PageBreak())

    # ── PROJE ZAMAN-IS CIZELGESI ──────────────────────────────────────────────
    story += section_heading("Proje Zaman-Is Çizelgesi")
    story.append(Paragraph("Görevlerin Zamanlama Tablosu", ST['h2']))
    cols = [7*cm, 2.8*cm, 2.5*cm, 2.8*cm]
    hdrs = ["GOREV", "Başlangıç", "Sure", "Bitis"]
    t, ts = header_style(cols, hdrs, TASK_ROWS)
    t.setStyle(ts)
    story.append(t)
    story.append(PageBreak())

    # ── GANTT DIAGRAM ─────────────────────────────────────────────────────────
    story += section_heading("Gantt Diyagramı")
    story.append(img_flow(gantt_p, w=W_inner))
    story.append(PageBreak())

    # ── PROJE GOREVLERI ───────────────────────────────────────────────────────
    story += section_heading("Proje Görevleri")
    cols2 = [10*cm, 7*cm]
    hdrs2 = ["Görev", "Sorumlusu"]
    t2, ts2 = header_style(cols2, hdrs2, TASK_ASSIGN)
    t2.setStyle(ts2)
    story.append(t2)
    story.append(PageBreak())

    # ── RISK TABLOSU ──────────────────────────────────────────────────────────
    story += section_heading("Risk Tablosu")
    cols3 = [0.6*cm, 4.5*cm, 2.4*cm, 1.3*cm, 1.5*cm, 4.8*cm]
    hdrs3 = ["ID", "Ad", "Tur", "Etki", "Olasilik", "Cozum"]
    t3, ts3 = header_style(cols3, hdrs3, RISK_ROWS)
    t3.setStyle(ts3)
    story.append(t3)
    story += [sp(14)]

    # Risk matrix
    story.append(Paragraph("Risk Matrisi (Etki x Olasilik)", ST['h2']))
    matrix = [
        [Paragraph("<b>Etki \\ Olas.</b>", ST['small']),
         Paragraph("<b>Dusuk</b>", ST['small']),
         Paragraph("<b>Orta</b>", ST['small']),
         Paragraph("<b>Yuksek</b>", ST['small'])],
        [Paragraph("<b>Cok</b>", ST['small']),
         Paragraph("3-6-13-14-19-20", ST['small']),
         Paragraph("7", ST['small']),
         Paragraph("", ST['small'])],
        [Paragraph("<b>Orta</b>", ST['small']),
         Paragraph("4-5-18", ST['small']),
         Paragraph("9-11-12", ST['small']),
         Paragraph("", ST['small'])],
        [Paragraph("<b>Az</b>", ST['small']),
         Paragraph("8-10-15-16", ST['small']),
         Paragraph("17", ST['small']),
         Paragraph("1-2", ST['small'])],
    ]
    mt = Table(matrix, colWidths=[2.5*cm, 4*cm, 4*cm, 4*cm])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LLBLUE),
        ('BACKGROUND', (0,0), (-1,0), LLBLUE),
        ('BACKGROUND', (1,1), (1,-1), colors.HexColor('#C6EFCE')),
        ('BACKGROUND', (2,1), (2,-1), colors.HexColor('#FFEB9C')),
        ('BACKGROUND', (3,1), (3,-1), colors.HexColor('#FFC7CE')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(mt)
    story.append(PageBreak())

    # ── KULLANIM SENARYOLARI ─────────────────────────────────────────────────
    story += section_heading("Kullanim Senaryoları")
    for sc in SCENARIOS:
        story += [sp(6)]
        story.append(Paragraph(sc['title'], ST['h2']))
        rows = [
            ["Birincil Aktor", sc['actor']],
            ["Ilgililer ve ilgi alanlari", sc['stakeholders']],
            ["On Koşullar", "\n".join(f"• {p}" for p in sc['pre'])],
            ["Son Koşullar", "\n".join(f"• {p}" for p in sc['post'])],
            ["Ana Senaryo", "\n".join(f"{i+1}. {s}" for i, s in enumerate(sc['main']))],
            ["Alternatif Senaryolar", "\n".join(sc['alt'])],
        ]
        sc_data = [[Paragraph(f'<b>{r[0]}</b>', ST['small']),
                    Paragraph(r[1].replace('\n','<br/>'), ST['small'])] for r in rows]
        sc_t = Table(sc_data, colWidths=[4*cm, 12.5*cm])
        sc_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), LLBLUE),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(sc_t)
        story += [sp(8)]
    story.append(PageBreak())

    # ── SOZLESMELER ───────────────────────────────────────────────────────────
    story += section_heading("Sözleşmeler")
    for c in CONTRACTS:
        rows = [
            ["Sözleşme No", c['no']],
            ["Ad", c['name']],
            ["İşlem", c['op']],
            ["Capraz Başvuru", c['ref']],
            ["On Koşullar", "\n".join(f"• {p}" for p in c['pre'])],
            ["Son Koşullar", "\n".join(f"• {p}" for p in c['post'])],
        ]
        ct_data = [[Paragraph(f'<b>{r[0]}</b>', ST['small']),
                    Paragraph(r[1].replace('\n','<br/>'), ST['small'])] for r in rows]
        ct = Table(ct_data, colWidths=[3.5*cm, 13*cm])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), LLBLUE),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(ct)
        story += [sp(10)]
    story.append(PageBreak())

    # ── SINIF DIAGRAMI ────────────────────────────────────────────────────────
    story += section_heading("Sınıf Diyagramı")
    story.append(img_flow(class_p, w=W_inner))
    story.append(PageBreak())

    # ── SIRALAMA DIAGRAMI ─────────────────────────────────────────────────────
    story += section_heading("Sıralama Diyagramı (Senaryo 1)")
    story.append(img_flow(seq_p, w=W_inner))
    story.append(PageBreak())

    # ── USE CASE DIAGRAMI ─────────────────────────────────────────────────────
    story += section_heading("Use Case Diyagramı")
    story.append(img_flow(uc_p, w=W_inner))
    story.append(PageBreak())

    # ── ETKILESIM DIAGRAMLARI ─────────────────────────────────────────────────
    story += section_heading("Etkileşim Diyagramları")
    act_titles = [
        "Etkileşim Diyagramı 1: Aday Kaydı ve KVKK Rızası",
        "Etkileşim Diyagramı 2: İş İlanı Görüntüle ve Başvur",
        "Etkileşim Diyagramı 3: Unutulma Hakkı / Veri Silme",
        "Etkileşim Diyagramı 4: Veri Saklama Politikası",
        "Etkileşim Diyagramı 5: Süresi Dolan Verileri İşle",
        "Etkileşim Diyagramı 6: Denetim Kaydi Görüntüle",
        "Etkileşim Diyagramı 7: Aday Profil Güncelleme",
        "Etkileşim Diyagramı 8: Veri Sahibi Yönetimi",
    ]
    for i in range(0, 8, 2):
        row_imgs = []
        for j in [i, i+1]:
            if j < len(act_paths):
                row_imgs.append(img_flow(act_paths[j], w=7.5*cm))
            else:
                row_imgs.append(Spacer(7.5*cm, 1))
        row_labels = []
        for j in [i, i+1]:
            if j < len(act_titles):
                row_labels.append(Paragraph(act_titles[j], ST['small']))
            else:
                row_labels.append(Spacer(1,1))
        t_act = Table([row_imgs, row_labels], colWidths=[8*cm, 8*cm])
        t_act.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_act)
        story += [sp(8)]
    story.append(PageBreak())

    # ── VERITABANI ER DIAGRAMI ────────────────────────────────────────────────
    story += section_heading("Veritabanı ER Diyagramı")
    story.append(img_flow(er_p, w=W_inner))
    story.append(PageBreak())

    # ── EKRAN GORUNTULERI ─────────────────────────────────────────────────────
    story += section_heading("Uygulama Ekran Görüntüleri")
    story.append(body(
        "Asagida KVKK/GDPR Uyumlu Veri Saklama-Silme Takip Sistemi'ne ait temel ekranlar "
        "belirtilmiştir. Sistem ASP.NET Core 8 MVC mimarisiyle geliştirilmiş, Bootstrap ile "
        "responsive tasarima sahip bir web uygulamasidir."
    ))
    story += [sp(8)]
    for idx, ss in enumerate(SCREENSHOTS, 1):
        story.append(Paragraph(f"<b>Ekran {idx}:</b> {ss}", ST['body']))
        placeholder = Table(
            [[Paragraph(f"[ {ss} ]", ST['center'])]],
            colWidths=[W_inner], rowHeights=[3.5*cm]
        )
        placeholder.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#2E75B6')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EEF4FB')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(placeholder)
        story += [sp(6)]

    doc.build(story)
    print(f"[OK] Rapor oluşturuldu: {out_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Diagramlar oluşturuluyor...")
    gantt_p    = gen_gantt()
    print(f"  [+] Gantt: {gantt_p}")
    class_p    = gen_class_diagram()
    print(f"  [+] Sinif: {class_p}")
    uc_p       = gen_usecase_diagram()
    print(f"  [+] Use Case: {uc_p}")
    seq_p      = gen_sequence_diagram()
    print(f"  [+] Siralama: {seq_p}")
    er_p       = gen_er_diagram()
    print(f"  [+] ER: {er_p}")
    act_paths  = gen_all_activity_diagrams()
    print(f"  [+] Aktivite (8): tamamlandi")

    out = os.path.join(BASE, 'KVKK_Proje_Raporu.pdf')
    print("PDF oluşturuluyor...")
    build_pdf(out, {
        'gantt': gantt_p, 'class': class_p,
        'usecase': uc_p, 'sequence': seq_p,
        'er': er_p, 'activities': act_paths
    })
