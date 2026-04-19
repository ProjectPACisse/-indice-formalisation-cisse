import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import json
import pandas as pd
from datetime import datetime
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import os
import tempfile
import zipfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- CHARGEMENT DES ANIMATIONS LOTTIE ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

lottie_hero = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_ghp9v4re.json")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Indice de Formalisation | Cabinet Cissé",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INITIALISATION DES SESSION STATES ---
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# Fonction pour convertir hex en couleur ReportLab
def hex_to_reportlab_color(hex_color):
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return colors.Color(r, g, b)
    except:
        return colors.HexColor('#2563eb')

# ═══════════════════════════════════════════════════════════════
# FONCTION DE GÉNÉRATION DU GRAPHIQUE RADAR
# ═══════════════════════════════════════════════════════════════
def generate_radar_chart(scores, color_hex):
    labels = ['Admin', 'Compta', 'Fiscal', 'Travail', 'Finance', 'Digital']
    values = [
        scores.get('Admin.', 0),
        scores.get('Compta.', 0),
        scores.get('Fiscal.', 0),
        scores.get('Social.', 0),
        scores.get('Finance.', 0),
        scores.get('Digital.', 0)
    ]
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values_radar = values + values[:1]
    angles_radar = np.concatenate((angles, [angles[0]]))
    
    fig = plt.figure(figsize=(8, 8), facecolor='white', dpi=150)
    ax = fig.add_subplot(111, polar=True)
    
    color_hex = color_hex.lstrip('#')
    rgb = tuple(int(color_hex[i:i+2], 16)/255 for i in (0, 2, 4))
    
    ax.plot(angles_radar, values_radar, 'o-', linewidth=2.5, color=rgb, markersize=6)
    ax.fill(angles_radar, values_radar, alpha=0.25, color=rgb)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.spines['polar'].set_visible(False)
    
    radar_path = os.path.join(tempfile.gettempdir(), 'radar_chart.png')
    plt.savefig(radar_path, bbox_inches='tight', dpi=150, facecolor='white')
    plt.close()
    
    return radar_path

# ═══════════════════════════════════════════════════════════════
# FONCTION DE GÉNÉRATION PDF PROFESSIONNELLE
# ═══════════════════════════════════════════════════════════════
def generate_professional_pdf(entreprise_info, score_global, niveau, label, color, scores, packages, uploaded_files_info):
    
    radar_path = generate_radar_chart(scores, color)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=1.8*cm, leftMargin=1.8*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    reportlab_color = hex_to_reportlab_color(color)
    
    custom_title = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24,
                                  fontName='Helvetica-Bold', textColor=colors.HexColor('#1e3a8a'),
                                  alignment=TA_CENTER, spaceAfter=15)
    
    custom_subtitle = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=10,
                                     fontName='Helvetica', textColor=colors.HexColor('#64748b'),
                                     alignment=TA_CENTER, spaceAfter=25)
    
    custom_section = ParagraphStyle('CustomSection', parent=styles['Heading2'], fontSize=14,
                                    fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'),
                                    spaceBefore=15, spaceAfter=12)
    
    custom_normal = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10,
                                   fontName='Helvetica', textColor=colors.HexColor('#334155'),
                                   spaceAfter=6, alignment=TA_LEFT)
    
    custom_bold = ParagraphStyle('CustomBold', parent=styles['Normal'], fontSize=10,
                                 fontName='Helvetica-Bold', textColor=colors.HexColor('#1e293b'),
                                 spaceAfter=4)
    
    score_style = ParagraphStyle('ScoreStyle', parent=styles['Normal'], fontSize=52,
                                 fontName='Helvetica-Bold', textColor=reportlab_color,
                                 alignment=TA_CENTER, spaceAfter=8)
    
    story = []
    
    # ==================== PAGE 1 ====================
    header_frame = Table([["CABINET CONSEIL CISSÉ"]], colWidths=[16*cm])
    header_frame.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 11),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
    ]))
    story.append(header_frame)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("RAPPORT D'INDICE DE FORMALISATION", custom_title))
    story.append(Paragraph(f"Document établi le {datetime.now().strftime('%d %B %Y')}", custom_subtitle))
    story.append(Spacer(1, 20))
    story.append(Paragraph("✦ ✦ ✦", custom_subtitle))
    story.append(Spacer(1, 25))
    
    # Identification
    story.append(Paragraph("IDENTIFICATION DE L'ENTREPRISE", custom_section))
    story.append(Spacer(1, 8))
    
    info_data = [
        ["Nom de l'entreprise", entreprise_info.get('nom', 'Non renseigné')],
        ["Secteur d'activité", entreprise_info.get('secteur', 'Non renseigné')],
        ["Date de création", entreprise_info.get('date_creation', 'Non renseignée')],
        ["Effectif", str(entreprise_info.get('employes', 'Non renseigné')) + " employés"],
    ]
    
    info_table = Table(info_data, colWidths=[5.5*cm, 9.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#475569')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    
    # Score Global
    story.append(Paragraph("SCORE GLOBAL DE FORMALISATION", custom_section))
    story.append(Spacer(1, 15))
    
    score_frame = Table([[f"{score_global:.1f}%"]], colWidths=[16*cm])
    score_frame.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(color + '15')),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, 0), 25),
        ('BOTTOMPADDING', (0, 0), (0, 0), 15),
    ]))
    story.append(score_frame)
    
    gauge_width = 12 * cm
    fill_width = (score_global / 100) * gauge_width
    gauge_data = [["", ""]]
    gauge_table = Table(gauge_data, colWidths=[fill_width, gauge_width - fill_width])
    gauge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), reportlab_color),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(gauge_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"NIVEAU {niveau} : {label}", custom_bold))
    story.append(Spacer(1, 20))
    
    story.append(PageBreak())
    
    # ==================== PAGE 2 ====================
    if os.path.exists(radar_path):
        story.append(Paragraph("ANALYSE VISUELLE", custom_section))
        story.append(Spacer(1, 8))
        img = Image(radar_path, width=10*cm, height=10*cm, hAlign='CENTER')
        story.append(img)
        story.append(Spacer(1, 10))
        story.append(Paragraph("Graphique radar des 6 dimensions de formalisation", custom_subtitle))
    
    story.append(PageBreak())
    
    # ==================== PAGE 3 ====================
    story.append(Paragraph("DÉTAIL PAR DIMENSION", custom_section))
    story.append(Spacer(1, 12))
    
    dims = [
        ('Admin.', 'Formalisation Administrative', '#3b82f6'),
        ('Compta.', 'Gestion Comptable', '#10b981'),
        ('Fiscal.', 'Conformité Fiscale', '#f59e0b'),
        ('Social.', 'Travail Décent', '#8b5cf6'),
        ('Finance.', 'Gestion Financière', '#ef4444'),
        ('Digital.', 'Capacités Numériques', '#06b6d4'),
    ]
    
    for key, name, c in dims:
        val = scores[key]
        story.append(Paragraph(f"{name}", custom_bold))
        data = [[f"{val:.0f}%", ""]]
        t = Table(data, colWidths=[val/100*10*cm, (100-val)/100*10*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(c)),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 8),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (0, 0), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))
    
    story.append(Spacer(1, 15))
    
    # Tableau récapitulatif
    story.append(Paragraph("RÉCAPITULATIF DES SCORES", custom_section))
    story.append(Spacer(1, 8))
    
    recap_data = [["Dimension", "Score", "Appréciation"]]
    for key, name, c in dims:
        val = scores[key]
        appreciation = "Excellent" if val >= 80 else "Bon" if val >= 60 else "À améliorer" if val >= 40 else "Critique"
        recap_data.append([name, f"{val:.0f}%", appreciation])
    
    recap_table = Table(recap_data, colWidths=[6.5*cm, 3*cm, 6.5*cm])
    recap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(recap_table)
    
    # Section Justificatifs
    if uploaded_files_info:
        story.append(Spacer(1, 20))
        story.append(Paragraph("JUSTIFICATIFS FOURNIS", custom_section))
        story.append(Spacer(1, 8))
        
        current_dim = ""
        for file_info in uploaded_files_info:
            if file_info['dimension'] != current_dim:
                current_dim = file_info['dimension']
                story.append(Paragraph(f"<b>{current_dim}</b>", custom_bold))
            story.append(Paragraph(f"   • {file_info['sub_item']} : {file_info['filename']}", custom_normal))
            story.append(Spacer(1, 2))
    
    story.append(PageBreak())
    
    # ==================== PAGE 4 ====================
    story.append(Paragraph("PROGRAMME D'ACCOMPAGNEMENT", custom_section))
    story.append(Spacer(1, 12))
    
    level_box = Table([[f"NIVEAU {niveau} : {label}"]], colWidths=[16*cm])
    level_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), reportlab_color),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 12),
        ('TOPPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
    ]))
    story.append(level_box)
    story.append(Spacer(1, 15))
    
    for i, package in enumerate(packages[:5], 1):
        story.append(Paragraph(f"{i}. {package}", custom_normal))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 25))
    
    # Conclusion
    story.append(Paragraph("CONCLUSION", custom_section))
    story.append(Spacer(1, 10))
    
    if score_global < 40:
        conclusion = f"L'entreprise {entreprise_info.get('nom', '')} se trouve à un stade critique de formalisation. Une action immédiate est nécessaire."
    elif score_global < 60:
        conclusion = f"L'entreprise {entreprise_info.get('nom', '')} a entamé les premières démarches de formalisation mais reste fragile."
    elif score_global < 80:
        conclusion = f"L'entreprise {entreprise_info.get('nom', '')} a atteint un bon niveau de formalisation."
    else:
        conclusion = f"Félicitations à {entreprise_info.get('nom', '')} ! L'entreprise a atteint le niveau d'excellence."
    
    story.append(Paragraph(conclusion, custom_normal))
    
    # Pied de page
    story.append(Spacer(1, 40))
    story.append(Paragraph("─" * 50, custom_subtitle))
    story.append(Paragraph("Cabinet Conseil Cissé - Sénégal", custom_normal))
    story.append(Paragraph("3cabinetconseilcisse@gmail.com | +221 77 495 07 58", custom_normal))
    
    doc.build(story)
    
    if os.path.exists(radar_path):
        os.remove(radar_path)
    
    buffer.seek(0)
    return buffer

# ═══════════════════════════════════════════════════════════════
# FONCTION DE CRÉATION DU ZIP AVEC RAPPORT + JUSTIFICATIFS
# ═══════════════════════════════════════════════════════════════
def create_zip_with_attachments(entreprise_info, pdf_buffer, uploaded_files_dict):
    """Crée un fichier ZIP contenant le PDF et tous les justificatifs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Ajouter le PDF
        pdf_filename = f"Rapport_Formalisation_{entreprise_info['nom'].replace(' ', '_')}.pdf"
        zip_file.writestr(pdf_filename, pdf_buffer.getvalue())
        
        # Ajouter les justificatifs
        for key, file_data in uploaded_files_dict.items():
            if file_data and file_data.get('file_data') is not None:
                # Nettoyer le nom du fichier
                safe_filename = file_data['filename'].replace(' ', '_')
                # Créer un dossier par dimension
                folder_name = file_data['dimension'].replace(' ', '_')
                zip_path = f"Justificatifs/{folder_name}/{safe_filename}"
                zip_file.writestr(zip_path, file_data['file_data'])
    
    zip_buffer.seek(0)
    return zip_buffer

# ═══════════════════════════════════════════════════════════════
# STYLE CSS (Interface Streamlit)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%);
        color: #1e293b;
    }

    .main { background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%); }
    .block-container { padding: 2rem 3rem; max-width: 1400px; }

    .hero-wrapper {
        text-align: center;
        padding: 40px 20px;
        border-radius: 24px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 20px 40px -15px rgba(0,0,0,0.1);
        margin-bottom: 40px;
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a8a10 0%, #3b82f610 100%);
        border: 1px solid #3b82f630;
        color: #1e40af;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 6px 18px;
        border-radius: 50px;
        margin-bottom: 20px;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        line-height: 1.1;
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }
    .hero-subtitle {
        color: #475569;
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto 30px;
    }
    .hero-stat {
        display: inline-block;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 14px 28px;
        margin: 6px;
        transition: all 0.3s ease;
    }
    .hero-stat:hover { transform: translateY(-5px); border-color: #3b82f6; }
    .hero-stat-num { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #2563eb; }
    .hero-stat-label { font-size: 0.75rem; color: #64748b; font-weight: 500; }

    .company-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .company-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
    }

    .dim-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .dim-card:hover { border-color: #3b82f6; transform: translateY(-3px); box-shadow: 0 12px 24px -8px rgba(0,0,0,0.1); }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
    }
    .section-icon {
        width: 44px; height: 44px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
    }
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
    }
    .section-weight {
        font-size: 0.8rem;
        color: #ffffff;
        background: #2563eb;
        padding: 4px 12px;
        border-radius: 20px;
        margin-left: auto;
        font-weight: 600;
    }

    .sub-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.9rem;
        color: #475569;
        font-weight: 500;
    }
    .sub-item-weight {
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .stFileUploader {
        background: #f8fafc !important;
        border: 1px dashed #3b82f6 !important;
        border-radius: 12px !important;
        margin-top: 8px;
        padding: 5px;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 18px 40px;
        border-radius: 14px;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        width: 100%;
        box-shadow: 0 8px 20px rgba(37,99,235,0.2);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(37,99,235,0.3); }

    .score-ring-container {
        text-align: center;
        padding: 40px 30px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 24px;
    }
    .score-value {
        font-family: 'Syne', sans-serif;
        font-size: 5rem;
        font-weight: 800;
        line-height: 1;
        margin: 20px 0 10px;
    }
    .score-level-badge {
        display: inline-block;
        padding: 10px 28px;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        padding: 40px 20px 20px;
        color: #64748b;
        font-size: 0.85rem;
    }
    .footer strong { color: #2563eb; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    if lottie_hero:
        st_lottie(lottie_hero, height=150, key="hero_animation")

st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">Cabinet Conseil Cissé &nbsp;•&nbsp; Sénégal</div>
    <div class="hero-title">Indice de Formalisation<br>des Entreprises</div>
    <div class="hero-subtitle">
        Évaluez votre maturité administrative et accédez à des programmes<br>d'accompagnement sur mesure.
    </div>
    <div>
        <div class="hero-stat"><div class="hero-stat-num">6</div><div class="hero-stat-label">Dimensions évaluées</div></div>
        <div class="hero-stat"><div class="hero-stat-num">5</div><div class="hero-stat-label">Niveaux de maturité</div></div>
        <div class="hero-stat"><div class="hero-stat-num">100%</div><div class="hero-stat-label">Score pondéré</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FORMULAIRE ENTREPRISE
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="company-card"><div class="company-title"><span>🏢</span> Informations de l\'entreprise</div></div>', unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2)
with col_info1:
    nom_entreprise = st.text_input("🏢 Nom de l'entreprise *", placeholder="Ex: SARL CISSÉ & Frères", key="nom_entreprise")
    secteur = st.selectbox("📊 Secteur d'activité", ["Sélectionnez", "Commerce", "Services", "Industrie", "Agriculture", "BTP", "Technologie", "Autre"], key="secteur")
with col_info2:
    date_creation = st.date_input("📅 Date de création", value=None, key="date_creation")
    nb_employes = st.number_input("👥 Nombre d'employés", min_value=0, step=1, key="nb_employes")

# ═══════════════════════════════════════════════════════════════
# DIMENSIONS
# ═══════════════════════════════════════════════════════════════

# DIMENSION 1
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#dbeafe; color:#1e40af;">📁</div>
        <div class="section-title">Formalisation Administrative</div>
        <div class="section-weight">Poids : 30%</div>
    </div>
    <div class="sub-item"><span>RCCM / Actes administratifs</span><span class="sub-item-weight">40%</span></div>
    <div class="sub-item"><span>NINEA</span><span class="sub-item-weight">40%</span></div>
    <div class="sub-item" style="border:none"><span>Autorisations spécifiques / RSE</span><span class="sub-item-weight">20%</span></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    rccm = st.checkbox("✅ RCCM / Actes administratifs", key="rccm")
    if rccm:
        uploaded = st.file_uploader("Justificatif RCCM", type=['pdf', 'jpg', 'png'], key="f1", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f1'] = {
                'dimension': 'Formalisation Administrative',
                'sub_item': 'RCCM / Actes administratifs',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col2:
    ninea = st.checkbox("✅ NINEA", key="ninea")
    if ninea:
        uploaded = st.file_uploader("Justificatif NINEA", type=['pdf', 'jpg', 'png'], key="f2", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f2'] = {
                'dimension': 'Formalisation Administrative',
                'sub_item': 'NINEA',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col3:
    aut = st.checkbox("✅ Autorisations spécifiques / RSE", key="aut")
    if aut:
        uploaded = st.file_uploader("Justificatif Autorisations", type=['pdf', 'jpg'], key="f3", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f3'] = {
                'dimension': 'Formalisation Administrative',
                'sub_item': 'Autorisations spécifiques / RSE',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }

s1 = (rccm * 0.4 + ninea * 0.4 + aut * 0.2) * 100
scores = {'Admin.': s1}

# DIMENSION 2
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#dcfce7; color:#166534;">📈</div>
        <div class="section-title">Gestion Comptable</div>
        <div class="section-weight">Poids : 20%</div>
    </div>
</div>
""", unsafe_allow_html=True)

systeme = st.selectbox(
    "Système comptable utilisé",
    ["Aucun (0%)", "Cahier recettes-dépenses (20%)", "SMT sans états financiers (30%)", 
     "SMT avec états financiers (50%)", "Système Normal sans états visés (75%)", 
     "Système Normal avec états financiers visés (100%)"],
    key="systeme"
)

uploaded = st.file_uploader("Justificatif états financiers / Brouillard", type=['pdf', 'xlsx'], key="f4")
if uploaded:
    st.session_state.uploaded_files['f4'] = {
        'dimension': 'Gestion Comptable',
        'sub_item': 'États financiers / Brouillard',
        'filename': uploaded.name,
        'file_data': uploaded.getvalue(),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M')
    }

score_compta_map = {
    "Aucun (0%)": 0, "Cahier recettes-dépenses (20%)": 20, "SMT sans états financiers (30%)": 30,
    "SMT avec états financiers (50%)": 50, "Système Normal sans états visés (75%)": 75,
    "Système Normal avec états financiers visés (100%)": 100
}
s2 = score_compta_map[systeme]
scores['Compta.'] = s2

# DIMENSION 3
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#fed7aa; color:#9a3412;">🏛️</div>
        <div class="section-title">Conformité Fiscale</div>
        <div class="section-weight">Poids : 15%</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    cofi = st.checkbox("✅ Enregistrement fiscal / COFI (20%)", key="cofi")
    if cofi:
        uploaded = st.file_uploader("Justificatif enregistrement fiscal", type=['pdf', 'jpg'], key="f5", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f5'] = {
                'dimension': 'Conformité Fiscale',
                'sub_item': 'Enregistrement fiscal / COFI',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_f2:
    declarations = st.checkbox("✅ Déclarations fiscales régulières (40%)", key="decl")
    if declarations:
        uploaded = st.file_uploader("Justificatif déclarations fiscales", type=['pdf'], key="f6", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f6'] = {
                'dimension': 'Conformité Fiscale',
                'sub_item': 'Déclarations fiscales régulières',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_f3:
    quitus = st.checkbox("✅ Quitus fiscal (40%)", key="quitus")
    if quitus:
        uploaded = st.file_uploader("Justificatif quitus fiscal", type=['pdf', 'jpg'], key="f7", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f7'] = {
                'dimension': 'Conformité Fiscale',
                'sub_item': 'Quitus fiscal',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }

s3 = (cofi * 0.20 + declarations * 0.40 + quitus * 0.40) * 100
scores['Fiscal.'] = s3

# DIMENSION 4
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#e9d5ff; color:#4c1d95;">👥</div>
        <div class="section-title">Travail Décent</div>
        <div class="section-weight">Poids : 15%</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns(2)
with col_t1:
    contrats = st.checkbox("✅ Contrats de travail enregistrés (35%)", key="contrats")
    if contrats:
        uploaded = st.file_uploader("Justificatif contrats de travail", type=['pdf'], key="f8", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f8'] = {
                'dimension': 'Travail Décent',
                'sub_item': 'Contrats de travail enregistrés',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
    affiliations = st.checkbox("✅ Affiliations CSS / IPRES / IPM (40%)", key="affil")
    if affiliations:
        uploaded = st.file_uploader("Justificatif affiliations sociales", type=['pdf', 'jpg'], key="f9", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f9'] = {
                'dimension': 'Travail Décent',
                'sub_item': 'Affiliations CSS / IPRES / IPM',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_t2:
    sst = st.checkbox("✅ Conditions SST / conformité (15%)", key="sst")
    droits = st.checkbox("✅ Respect droits collectifs (10%)", key="droits")

s4 = (contrats * 0.35 + affiliations * 0.40 + sst * 0.15 + droits * 0.10) * 100
scores['Social.'] = s4

# DIMENSION 5
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#fecaca; color:#991b1b;">💳</div>
        <div class="section-title">Gestion Financière</div>
        <div class="section-weight">Poids : 10%</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)
with col_g1:
    compte = st.checkbox("✅ Compte bancaire / IMF / wallet (50%)", key="compte")
    if compte:
        uploaded = st.file_uploader("Justificatif RIB ou extrait de compte", type=['pdf', 'jpg'], key="f10", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f10'] = {
                'dimension': 'Gestion Financière',
                'sub_item': 'Compte bancaire / IMF / wallet',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_g2:
    tracabilite = st.checkbox("✅ Traçabilité des opérations (50%)", key="tracab")
    if tracabilite:
        uploaded = st.file_uploader("Justificatif registre / tableau de trésorerie", type=['pdf', 'xlsx'], key="f11", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f11'] = {
                'dimension': 'Gestion Financière',
                'sub_item': 'Traçabilité des opérations',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }

s5 = (compte * 0.50 + tracabilite * 0.50) * 100
scores['Finance.'] = s5

# DIMENSION 6
st.markdown("""
<div class="dim-card">
    <div class="section-header">
        <div class="section-icon" style="background:#cffafe; color:#164e63;">💻</div>
        <div class="section-title">Capacités Organisationnelles & Numériques</div>
        <div class="section-weight">Poids : 10%</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    manuel = st.checkbox("✅ Manuel de procédures / organigramme (40%)", key="manuel")
    if manuel:
        uploaded = st.file_uploader("Justificatif manuel / organigramme", type=['pdf', 'docx'], key="f12", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f12'] = {
                'dimension': 'Capacités Organisationnelles & Numériques',
                'sub_item': 'Manuel de procédures / organigramme',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_n2:
    bizplan = st.checkbox("✅ Plan stratégique / business plan (20%)", key="bizplan")
    if bizplan:
        uploaded = st.file_uploader("Justificatif business plan", type=['pdf', 'docx'], key="f13", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f13'] = {
                'dimension': 'Capacités Organisationnelles & Numériques',
                'sub_item': 'Plan stratégique / business plan',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
with col_n3:
    digital = st.checkbox("✅ Maturité digitale avérée (40%)", key="digital")
    if digital:
        uploaded = st.file_uploader("Justificatif outils numériques", type=['pdf', 'jpg', 'png'], key="f14", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_files['f14'] = {
                'dimension': 'Capacités Organisationnelles & Numériques',
                'sub_item': 'Maturité digitale avérée',
                'filename': uploaded.name,
                'file_data': uploaded.getvalue(),
                'date': datetime.now().strftime('%d/%m/%Y %H:%M')
            }

s6 = (manuel * 0.40 + bizplan * 0.20 + digital * 0.40) * 100
scores['Digital.'] = s6

# ═══════════════════════════════════════════════════════════════
# CALCUL DU SCORE GLOBAL
# ═══════════════════════════════════════════════════════════════
score_global = (s1 * 0.30 + s2 * 0.20 + s3 * 0.15 + s4 * 0.15 + s5 * 0.10 + s6 * 0.10)

# ═══════════════════════════════════════════════════════════════
# BOUTON GÉNÉRATION
# ═══════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate = st.button("🚀 GÉNÉRER L'INDICE DE FORMALISATION")

# ═══════════════════════════════════════════════════════════════
# RÉSULTATS
# ═══════════════════════════════════════════════════════════════
if generate:
    if not nom_entreprise:
        st.error("⚠️ Veuillez renseigner le nom de l'entreprise avant de générer l'indice.")
        st.stop()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Préparer la liste des justificatifs pour le PDF
    uploaded_files_info = []
    for key, file_info in st.session_state.uploaded_files.items():
        uploaded_files_info.append({
            'dimension': file_info['dimension'],
            'sub_item': file_info['sub_item'],
            'filename': file_info['filename'],
            'date': file_info['date']
        })
    
    entreprise_info = {
        'nom': nom_entreprise,
        'secteur': secteur if secteur != "Sélectionnez" else "Non précisé",
        'date_creation': date_creation.strftime('%d/%m/%Y') if date_creation else "Non renseignée",
        'employes': nb_employes if nb_employes > 0 else "Non renseigné"
    }
    
    # Détermination du niveau
    if score_global < 20:
        niveau, label, color = 0, "Informel pur — Zone Grise", "#ef4444"
        packages = [
            "📋 Campagnes de sensibilisation sur la formalisation",
            "📝 Appui à l'immatriculation (NINEA, RCCM)",
            "🏢 Accompagnement à la domiciliation",
            "💳 Ouverture d'un compte bancaire",
            "📜 Assistance sur les autorisations"
        ]
    elif score_global < 40:
        niveau, label, color = 1, "Pré-formalisation — Premiers pas", "#f59e0b"
        packages = [
            "📚 Formation en comptabilité simplifiée",
            "📊 Assistance pour déclarations fiscales",
            "🏦 Formation à l'utilisation d'un compte pro",
            "⚖️ Information sur le droit du travail",
            "💰 Accès à microfinancements adaptés"
        ]
    elif score_global < 60:
        niveau, label, color = 2, "Formalisation de base — Fondations", "#3b82f6"
        packages = [
            "🎓 Formation avancée en gestion",
            "📈 Coaching fiscal",
            "📝 Rédaction des contrats de travail",
            "🤝 Sensibilisation au travail décent",
            "💼 Préparation au crédit bancaire"
        ]
    elif score_global < 80:
        niveau, label, color = 3, "Formalisation intermédiaire — Consolidation", "#8b5cf6"
        packages = [
            "📊 Passage au Système Normal",
            "🏛️ Formation en gouvernance",
            "🛡️ Généralisation couverture sociale",
            "🏗️ Mise en conformité lieu de travail",
            "💎 Accès crédits bancaires importants"
        ]
    else:
        niveau, label, color = 4, "Formalisation avancée — Excellence", "#10b981"
        packages = [
            "🏅 Appui certification qualité",
            "💻 Digitalisation des processus",
            "🌍 Accès aux marchés publics",
            "🤝 Participation foires internationales",
            "💰 Accès au capital-risque",
            "🎯 Coaching internationalisation"
        ]
    
    # Affichage des résultats
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); border-radius: 16px; padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            <div><span style="font-size: 0.8rem; color: #64748b;">ENTREPRISE</span>
            <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800;">{nom_entreprise}</div></div>
            <div><span style="font-size: 0.8rem; color: #64748b;">SECTEUR</span>
            <div style="font-weight: 600; color: #2563eb;">{secteur if secteur != 'Sélectionnez' else 'Non précisé'}</div></div>
            <div><span style="font-size: 0.8rem; color: #64748b;">DATE</span>
            <div style="font-weight: 600;">{datetime.now().strftime('%d/%m/%Y')}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score
    col_res1, col_res2 = st.columns([1, 1])
    
    with col_res1:
        st.markdown(f"""
        <div class="score-ring-container">
            <div style="font-size:0.8rem; color:#64748b; font-weight:600;">SCORE GLOBAL</div>
            <div class="score-value" style="color:{color};">{score_global:.1f}%</div>
            <div class="score-level-badge" style="background:{color}10; color:{color};">NIVEAU {niveau} | {label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_res2:
        dim_details = [
            ('Admin.', 'Formalisation Administrative', '#3b82f6'),
            ('Compta.', 'Gestion Comptable', '#10b981'),
            ('Fiscal.', 'Conformité Fiscale', '#f59e0b'),
            ('Social.', 'Travail Décent', '#8b5cf6'),
            ('Finance.', 'Gestion Financière', '#ef4444'),
            ('Digital.', 'Capacités Numériques', '#06b6d4'),
        ]
        categories = [d[1] for d in dim_details]
        values = [scores[d[0]] for d in dim_details]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself',
                                      fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2)',
                                      line=dict(color=color, width=3), name='Score'))
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0,100])),
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Détail
    st.markdown("### 📊 Détail par dimension")
    for key, name, c in dim_details:
        val = scores[key]
        st.markdown(f"""
        <div style="margin:10px 0;">
            <div style="display:flex; justify-content:space-between;"><span>{name}</span><span style="color:{c}; font-weight:700;">{val:.0f}%</span></div>
            <div style="background:#f1f5f9; border-radius:50px; height:8px;"><div style="width:{val}%; height:100%; background:{c}; border-radius:50px;"></div></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommandations
    st.markdown(f"### 🎯 Programme d'accompagnement - Niveau {niveau}")
    cols = st.columns(2)
    for i, p in enumerate(packages):
        with cols[i % 2]:
            st.markdown(f"- {p}")
    
    # Génération du PDF
    with st.spinner("Génération du rapport PDF..."):
        pdf_buffer = generate_professional_pdf(entreprise_info, score_global, niveau, label, color, scores, packages, uploaded_files_info)
    
    # Création du ZIP avec les justificatifs
    with st.spinner("Préparation des justificatifs..."):
        zip_buffer = create_zip_with_attachments(entreprise_info, pdf_buffer, st.session_state.uploaded_files)
    
    # Bouton unique de téléchargement
    col_zip1, col_zip2, col_zip3 = st.columns([1, 2, 1])
    with col_zip2:
        st.download_button(
            label="📦 TÉLÉCHARGER LE RAPPORT COMPLET (PDF + JUSTIFICATIFS)",
            data=zip_buffer,
            file_name=f"Rapport_Complet_{nom_entreprise.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    # Affichage du nombre de justificatifs
    nb_justificatifs = len(st.session_state.uploaded_files)
    if nb_justificatifs > 0:
        st.success(f"📎 {nb_justificatifs} justificatif(s) inclus dans le téléchargement")
        
        # Afficher la liste des justificatifs dans un expander
        with st.expander("📋 Voir la liste des justificatifs inclus"):
            for key, file_info in st.session_state.uploaded_files.items():
                st.markdown(f"- **{file_info['dimension']}** : {file_info['sub_item']} → `{file_info['filename']}`")
    else:
        st.info("📎 Aucun justificatif téléchargé - Le rapport PDF sera téléchargé seul")
    
    if score_global >= 80:
        st.balloons()
        st.success("🎉 FÉLICITATIONS ! Niveau d'excellence atteint !")

# Footer
st.markdown("""
<div class="footer">
    <hr>
    Propulsé par <strong>Cabinet Conseil Cissé</strong> | 2026 - Sénégal
</div>
""", unsafe_allow_html=True)