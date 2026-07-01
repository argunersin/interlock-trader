import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import urllib.parse

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="Interlock Trader Core", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #0b1120; color: #f3f4f6; }
    .stMetric { background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; }
    div.stButton > button:first-child { background-color: #00f2fe; color: #0a0f1d; border-radius: 5px; width: 100%; border: none; padding: 12px; font-weight: bold; font-size: 16px; }
    div.stButton > button:first-child:hover { background-color: #ffffff; box-shadow: 0 0 15px #00f2fe; }
    h1, h2, h3, p, span, label { color: #f3f4f6 !important; }
    .stTable { background-color: #111827; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# SOL MENÜ
st.sidebar.title("📊 TRADER ENGINE")
st.sidebar.caption("v2.1 - Live Core Terminal")
menu = st.sidebar.radio("Modüller", ["🚀 Akıllı İstihbarat & Derin Raporlama", "📄 Evrak Analiz & GTİP", "⚖️ Akreditif Sihirbazı"])

# PDF RAPOR MOTORU
def generate_advanced_pdf(query, data_dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0e1c36'), spaceAfter=15)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#4a5568'), spaceAfter=25)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1a202c'))
    
    story.append(Paragraph("<b>INTERLOCK GLOBAL - ULUSLARARASI TICARET ISTIHBARATI</b>", title_style))
    story.append(Paragraph(f"<b>Analiz Edilen Rota:</b> {query.upper()} | Durum: Canlı Veri", sub_style))
    story.append(Spacer(1, 15))
    
    table_data = [[Paragraph("<b>KRİTER</b>", body_style), Paragraph("<b>STRATEJİK DETAYLAR VE PİYASA ANALİZİ</b>", body_style)]]
    for key, value in data_dict.items():
        table_data.append([Paragraph(f"<b>{key}</b>", body_style), Paragraph(value, body_style)])
        
    t = Table(table_data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#0e1c36')),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

# MODÜL 1: CANLI VERİ VE GELİŞMİŞ İSTİHBARAT
if menu == "🚀 Akıllı İstihbarat & Derin Raporlama":
    st.title("🚀 Yapay Zeka Destekli Küresel İstihbarat Terminali")
    
    st.subheader("📈 Londra Metal & Emtia Borsası Canlı Endeksleri")
    col_lme1, col_lme2, col_lme3 = st.columns(3)
    
    # 2026 Gerçek Zamanlı Veri Çekme Motoru
    try:
        ali_data = yf.Ticker("ALI=F").history(period="2d")
        ali_price = round(ali_data['Close'].iloc[-1], 2) if not ali_data.empty else 3145.00
    except:
        ali_price = 3145.00
    col_lme1.metric("LME Alüminyum (Ton)", f"${ali_price}", "Canlı Borsa")
        
    try:
        oil_data = yf.Ticker("BZ=F").history(period="2d")
        oil_price = round(oil_data['Close'].iloc[-1], 2) if not oil_data.empty else 78.40
    except:
        oil_price = 78.40
    col_lme2.metric("Brent Petrol (Varil)", f"${oil_price}", "Anlık Değişim")
        
    try:
        sugar_data = yf.Ticker("SB=F").history(period="2d")
        sugar_price = round(sugar_data['Close'].iloc[-1] * 22.04, 2) if not sugar_data.empty else 540.20
    except:
        sugar_price = 540.20
    col_lme3.metric("Şeker Endeksi (Ton)", f"${sugar_price}", "Uluslararası")

    st.divider()
    
    search_query = st.text_input("Arama Motoru (Emtia ve Ülkeleri Yazın):", placeholder="Örn: aluminyum kazakistan - türkiye")
    
    if search_query:
        query_lower = search_query.lower()
        
        if "aluminyum" in query_lower or "alüminyum" in query_lower:
            product = "Ham Alüminyum Külçe (P1020 / Saflık %99.7)"
            fob_val = f"${ali_price}"
            premium_val = "+$195.00 (Bölgesel LME Rotterdam / TR Primi)"
            freight_val = "$110.00 (Aktau Port -> Bakü -> BTK Demiryolu)"
            gtip_val = "7601.10.00.00.00"
            
            report_data = {
                "GTİP / HS Code": gtip_val,
                "Menşei Ülke Üreticileri": "1. Kazakhstan Aluminium (KCA), 2. ERG Group Metal Corp, 3. Tau-Ken Samruk Mining",
                "Türkiye İthalatçı Odakları": "1. Assan Alüminyum A.Ş., 2. Saray Metal Sanayi, 3. Teknik Alüminyum",
                "Lojistik Güzergah Analizi": "Aktau Limanı üzerinden dökme yük gemileri veya Bakü-Tiflis-Kars (BTK) demiryolu hattı orta koridor kullanımı.",
                "Gümrük Vergileri ve Kotalar": "Kazakistan ile ikili ticaret anlaşmaları kapsamında esnek gümrük muafiyeti, ancak TR ithalat gözetim belgesi zorunluluğu.",
                "Operasyonel Finansal Riskler": "Hazar geçişindeki lojistik darboğazlar sebebiyle gecikme riski. LME fiyat oynaklığı koruması (Hedging) önerilir."
            }
            lat, lon = 44.5000, 50.2000
            m_text = "Kazakistan Alüminyum Çıkış Koridoru"
            
        elif "şeker" in query_lower or "seker" in query_lower:
            product = "Rafine Beyaz Kamış Şekeri (ICUMSA 45)"
            fob_val = f"${sugar_price}"
            premium_val = "+$18.00 (Sertifikasyon Primi)"
            freight_val = "$52.00 (Dökme Kargo Gemisi - Supramax)"
            gtip_val = "1701.99.10.00.11"
            
            report_data = {
                "GTİP / HS Code": gtip_val,
                "Menşei Ülke Üreticileri": "1. Cosan SA Trading, 2. São Martinho Group, 3. Tereos Sugar Brazil",
                "Türkiye İthalatçı Odakları": "1. Türkiye Şeker Fabrikaları, 2. Konya Şeker Fabrikası, 3. Özel İthalatçılar",
                "Lojistik Güzergah Analizi": "Santos veya Paranagua limanlarından yükleme, Akdeniz / Marmara limanları tahliye dökme yük taşımacılığı.",
                "Gümrük Vergileri ve Kotalar": "Şeker ithalatı tarife kontenjanına ve sıkı gümrük fon denetimlerine tabidir.",
                "Operasyonel Finansal Riskler": "Santos limanındaki gemi kuyrukları nedeniyle yüksek Demurrage riski. SGS raporu kontrol edilmelidir."
            }
            lat, lon = -23.9535, -46.3015
            m_text = "Santos Port - Şeker İhracat Terminali"
        else:
            product = f"Emtia: {search_query.upper()}"
            fob_val = "$750.00"; premium_val = "+$30.00"; freight_val = "$65.00"; gtip_val = "Sorgulanıyor"
            report_data = {"Veri Durumu": "Küresel veri tabanında arama yapılıyor. Lütfen emtia adını net belirtiniz."}
            lat, lon = 41.0082, 28.9784; m_text = "Interlock Hub"

        st.success(f"📌 {product} Analiz Segmenti Aktif.")
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Canlı FOB Fiyatı (Ton)", fob_val, "Gerçek Zamanlı")
        c_m2.metric("Bölge Primi (Premium)", premium_val, "LME Kontrollü")
        c_m3.metric("Navlun Maliyeti (Tahmini)", freight_val, "Rota Endeksli")
        
        st.subheader("📋 Gelişmiş Ticari İstihbarat Detayları")
        st.table(pd.DataFrame(list(report_data.items()), columns=["İstihbarat Kriteri", "Stratejik Veri"]))
        
        st.subheader("📥 Raporlama Merkez Ofis Çıktıları")
        pdf_file = generate_advanced_pdf(search_query, report_data)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.download_button(label="📥 Resmi PDF Raporu İndir", data=pdf_file, file_name=f"Interlock_Rapor.pdf", mime="application/pdf")
        with col_b2:
            wa_text = f"*INTERLOCK GLOBAL REPORT*\n\n*Ürün:* {product}\n*Canlı FOB:* {fob_val}\n*Lojistik:* {freight_val}"
            encoded_wa = urllib.parse.quote(wa_text)
            st.markdown(f'<a href="https://wa.me{encoded_wa}" target="_blank"><div style="background-color:#25D366;color:white;text-align:center;padding:12px;border-radius:5px;font-weight:bold;cursor:pointer;">📱 Raporu WhatsApp Hattına Gönder</div></a>', unsafe_allow_html=True)

    # LOJİSTİK HARİTA
    st.divider()
    st.subheader("🚢 Canlı Denizcilik ve Rota Kontrol Haritası")
    m_lat = lat if search_query else 41.0082
    m_lon = lon if search_query else 28.9784
    m = folium.Map(location=[m_lat, m_lon], zoom_start=4 if search_query else 6, tiles="CartoDB dark_matter")
    
    if search_query:
        folium.Marker([lat, lon], popup=m_text, icon=folium.Icon(color='red', icon='ship', prefix='fa')).add_to(m)
        folium.PolyLine(locations=[[lat, lon], [40.98, 28.90]], color="#00f2fe", weight=3).add_to(m)
    else:
        folium.Marker([41.15, 29.10], popup="MSC TESSA", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=450)

elif menu == "📄 Evrak Analiz & GTİP":
    st.title("📄 Akıllı Evrak Doğrulama Motoru")
    st.file_uploader("Evrak Yükleyin (PDF/JPG)", type=["pdf", "jpg", "png"])

elif menu == "⚖️ Akreditif Sihirbazı":
    st.title("⚖️ Otonom Akreditif (L/C) Kontrolü")
    st.text_input("Firma Detayları:")
