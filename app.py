import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import urllib.parse

# 1. RETRO SİBER TERMİNAL AYARLARI
st.set_page_config(page_title="Interlock Global Terminal", layout="wide", page_icon="📟")

st.markdown("""
    <style>
    .main, block-container, .stApp { background-color: #05070f !important; color: #00f2fe !important; }
    .split-flap-card {
        background: linear-gradient(180deg, #111524 49%, #05070f 50%, #111524 51%);
        border: 2px solid #1f2937; border-radius: 8px; padding: 20px; text-align: center;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8), 0 4px 8px rgba(0,0,0,0.5); min-height: 140px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .split-flap-title { font-family: 'Courier New', monospace; font-size: 11px; color: #9ca3af; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; }
    .split-flap-value { font-family: 'Courier New', monospace; font-size: 30px; font-weight: bold; color: #00f2fe; text-shadow: 0 0 10px rgba(0,242,254,0.5); }
    .split-flap-sub { font-family: 'Courier New', monospace; font-size: 11px; color: #10b981; margin-top: 5px; }
    .stTable, table, tr, td, th { background-color: #0b0f19 !important; color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    th { color: #00f2fe !important; font-weight: bold !important; border-bottom: 2px solid #1f2937 !important; }
    td { border-bottom: 1px solid #1f2937 !important; padding: 12px !important; }
    [data-testid="stSidebar"] { background-color: #070a14 !important; border-right: 1px solid #1f2937 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='color: #00f2fe; text-align: center;'>📟 TERMINAL v3</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("İŞLEM MODÜLÜ", ["🚀 İstihbarat & Split-Flap Borsası", "📄 Evrak Analiz (OCR)", "⚓ Özel Gemi Röntgeni ($20)"])

# HATASIZ SADELEŞTİRİLMİŞ PDF MOTORU
def generate_advanced_pdf(query, data_dict):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, "INTERLOCK GLOBAL - ULUSLARARASI TICARET ISTIHBARATI")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, f"Analiz Edilen Rota: {query.upper()}")
    y = 700
    for key, value in data_dict.items():
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, f"{key}:")
        p.setFont("Helvetica", 10)
        p.drawString(200, y, str(value)[:80])
        y -= 25
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# MODÜL 1: CANLI RETRO BORSA VE İSTİHBARAT
if menu == "🚀 İstihbarat & Split-Flap Borsası":
    st.markdown("<h1 style='color: #00f2fe;'>📟 INTERLOCK GLOBAL REAL-TIME TERMINAL</h1>", unsafe_allow_html=True)
    st.caption("Otonom veri akışlı mekanik split-flap model emtia fiyat göstergeleri")
    
    # 2026 CANLI VERİ ÇEKİM MOTORU
    try:
        ali = yf.Ticker("ALI=F").history(period="2d"); ali_p = round(ali['Close'].iloc[-1], 2) if not ali.empty else 3266.50
        cu = yf.Ticker("HG=F").history(period="2d"); cu_p = round(cu['Close'].iloc[-1] * 2204.62, 2) if not cu.empty else 9120.00
        sugar = yf.Ticker("SB=F").history(period="2d"); sugar_p = round(sugar['Close'].iloc[-1] * 22.04, 2) if not sugar.empty else 329.72
        wheat = yf.Ticker("W=F").history(period="2d"); wheat_p = round(wheat['Close'].iloc[-1] * 0.367, 2) if not wheat.empty else 245.00
        oil = yf.Ticker("BZ=F").history(period="2d"); oil_p = round(oil['Close'].iloc[-1], 2) if not oil.empty else 71.38
    except:
        ali_p=3266.50; cu_p=9120.00; sugar_p=329.72; wheat_p=245.00; oil_p=71.38

    # 📻 MEKANİK ÇENTİK KONTROLÜ
    st.subheader("🛠️ Kategori Kumandası (Mekanik Çentik Ayarı)")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        metal_select = st.selectbox("⚙️ LME METALLER GRUBU:", ["Alüminyum (Külçe P1020)", "Bakır Katot (Grade A)", "İnşaat Demiri (Rebar)", "HMS 1/2 Demir Hurdası"])
    with col_sel2:
        gida_select = st.selectbox("🌾 ENDÜSTRİYEL GIDA GRUBU:", ["Beyaz Şeker (ICUMSA 45)", "Ekmeklik Buğday", "Sarı Mısır", "Ham Ayçiçek Yağı"])
        
    # PIT PIT ATAN 6 BÜYÜK RETRO LEVHA YERLEŞİMİ
    st.write("")
    c_b1, c_b2, c_b3 = st.columns(3)
    with c_b1:
        if "Alüminyum" in metal_select:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">${ali_p}</div><div class="split-flap-sub">ALÜMİNYUM / TON</div></div>', unsafe_allow_html=True)
        elif "Bakır" in metal_select:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">${cu_p}</div><div class="split-flap-sub">BAKIR KATOT / TON</div></div>', unsafe_allow_html=True)
        elif "İnşaat" in metal_select:
            st.markdown('<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">$595.00</div><div class="split-flap-sub">İNŞAAT DEMİRİ / TON</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">$365.00</div><div class="split-flap-sub">HMS 1/2 HURDA / TON</div></div>', unsafe_allow_html=True)
            
    with c_b2:
        if "Şeker" in gida_select:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">${sugar_p}</div><div class="split-flap-sub">ŞEKER ENDEKSİ / TON</div></div>', unsafe_allow_html=True)
        elif "Buğday" in gida_select:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">${wheat_p}</div><div class="split-flap-sub">BUĞDAY / TON</div></div>', unsafe_allow_html=True)
        elif "Mısır" in gida_select:
            st.markdown('<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">$185.00</div><div class="split-flap-sub">SARI MISIR / TON</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">$890.00</div><div class="split-flap-sub">AYÇİÇEK YAĞI / TON</div></div>', unsafe_allow_html=True)
            
    with c_b3:
        st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENERJİ & AKARYAKIT</div><div class="split-flap-value">${oil_p}</div><div class="split-flap-sub">BRENT PETROL / VARİL</div></div>', unsafe_allow_html=True)

    st.write("")
    c_b4, c_b5, c_b6 = st.columns(3)
    with c_b4:
        st.markdown('<div class="split-flap-card"><div class="split-flap-title">• ENERJİ ENTEGRASYONU</div><div class="split-flap-value">$745.00</div><div class="split-flap-sub">EN590 DİZEL / TON</div></div>', unsafe_allow_html=True)
    with c_b5:
        st.markdown('<div class="split-flap-card"><div class="split-flap-title">• PLASTİK HAMMADDELER</div><div class="split-flap-value">$1,150</div><div class="split-flap-sub">PVC GRANÜL / TON</div></div>', unsafe_allow_html=True)
    with c_b6:
        st.markdown('<div class="split-flap-card"><div class="split-flap-title">• KÜRESEL NAVLUN ENDEKSİ</div><div class="split-flap-value">1,480</div><div class="split-flap-sub">BDI BALTIK KURUYÜK</div></div>', unsafe_allow_html=True)

    # ARAMA MOTORU VE DERİN RAPORLAMA KATMANI
    st.divider()
    search_query = st.text_input("Gelişmiş Arama Terminali (Emtia ve Ülkeler):", placeholder="Örn: aluminyum kazakistan - türkiye")
    
    if search_query:
        query_lower = search_query.lower()
        if "aluminyum" in query_lower or "alüminyum" in query_lower:
            product = "Ham Alüminyum Külçe (P1020)"; fob_val = f"${ali_p}"; premium_val = "+$195.00"; freight_val = "$110.00"; gtip_val = "7601.10.00.00.00"
            report_data = {
                "GTİP / HS Code": gtip_val,
                "Incoterms 2025 Fiyat Matrisi": f"EXW: $2,950 / TON | FOB: {fob_val} / TON | CIF: $3,450 / TON",
                "Muhtemel Lojistik Rotalar": "Aktau Port (Kazakistan) -> Hazar Denizi Geçişi -> Bakü -> BTK Demiryolu Hattı Orta Koridor güzergahı.",
                "Gümrük Vergileri & Kotası": "Kazakistan-Türkiye İkili Ticaret Anlaşması kapsamında gümrük muafiyeti mevcuttur. TR İthalat Gözetim Belgesi zorunludur.",
                "Gerekli Resmi Evrak Listesi": "1. Proforma Invoice, 2. Master Bill of Lading (MBL), 3. SGS Sertifikası, 4. Certificate of Origin, 5. Çeki Listesi.",
                "Operasyonel Finansal Riskler": "Hazar geçişindeki gecikme riski. LME fiyat oynaklığına karşı Hedging zorunludur.",
                "Top 5 Küresel Lojistik Kontak Ağı": "1. MSC (info@msc.com) | 2. Maersk Line (sales@maersk.com) | 3. CMA CGM | 4. COSCO Shipping | 5. Hapag-Lloyd",
                "Top 5 Küresel Gözetim Kontak Ağı": "1. SGS SA (sgs.global@sgs.com) | 2. Bureau Veritas | 3. Intertek Group | 4. Cotecna Inspection | 5. Saybolt"
            }
            lat, lon = 44.5000, 50.2000; m_text = "Kazakistan Çıkış Terminali"
        elif "şeker" in query_lower or "seker" in query_lower:
            product = "Rafine Beyaz Kamış Şekeri (ICUMSA 45)"; fob_val = f"${sugar_p}"; premium_val = "+$18.00"; freight_val = "$52.00"; gtip_val = "1701.99.10.00.11"
            report_data = {
                "GTİP / HS Code": gtip_val,
                "Incoterms 2025 Fiyat Matrisi": f"EXW: $480 / TON | FOB: {fob_val} / TON | CIF: $610 / TON",
                "Muhtemel Lojistik Rotalar": "Santos veya Paranagua (Brezilya) yükleme -> Atlantik Okyanusu -> Cebelitarık -> Akdeniz / Marmara Limanları.",
                "Gümrük Vergileri & Kotası": "Şeker ithalatı sıkı tarife kontenjanına ya da yüksek fon denetimlerine tabidir.",
                "Gerekli Resmi Evrak Listesi": "1. Commercial Invoice, 2. Ocean Bill of Lading, 3. Phytosanitary Certificate, 4. SGS Kalite Raporu, 5. Fumigasyon Belgesi.",
                "Operasyonel Finansal Riskler": "Santos limanındaki gemi trafiği nedeniyle yüksek Demurrage riski. SGS onayı şarttır.",
                "Top 5 Küresel Lojistik Kontak Ağı": "1. MSC (info@msc.com) | 2. Maersk Line | 3. CMA CGM | 4. COSCO Shipping | 5. Hapag-Lloyd",
                "Top 5 Küresel Gözetim Kontak Ağı": "1. SGS SA (sgs.global@sgs.com) | 2. Bureau Veritas | 3. Intertek Group | 4. Cotecna Inspection | 5. Saybolt"
            }
            lat, lon = -23.9535, -46.3015; m_text = "Santos Port"
        else:
            product = f"Emtia: {search_query.upper()}"; fob_val = "$750.00"; premium_val = "+$30.00"; freight_val = "$65.00"; gtip_val = "Kontrol Ediliyor"
            report_data = {"Veri Durumu": "Test aşamasında 'Alüminyum' veya 'Şeker' yazarak derin raporu simüle edin."}
            lat, lon = 41.0082, 28.9784; m_text = "Hub"

        st.success(f"📌 {product} İçin Canlı Veri Segmenti Kilitlendi.")
        st.table(pd.DataFrame(list(report_data.items()), columns=["Terminal Kriteri", "Mekanik Rapor Çıktısı"]))
        
        pdf_file = generate_advanced_pdf(search_query, report_data)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.download_button(label="📥 Resmi PDF Raporu İndir", data=pdf_file, file_name="Interlock_Briefing.pdf")
        with col_b2:
            wa_text = f"*INTERLOCK GLOBAL REPORT*\n\n*Ürün:* {product}\n*Canlı FOB:* {fob_val}"
            st.markdown(f'<a href="https://wa.me{urllib.parse.quote(wa_text)}" target="_blank"><div style="background-color:#25D366;color:white;text-align:center;padding:12px;border-radius:5px;font-weight:bold;cursor:pointer;">📱 Raporu WhatsApp Hattına Gönder</div></a>', unsafe_allow_html=True)

    # HARİTA KATMANI
    st.divider()
    m_lat = lat if search_query else 41.0082; m_lon = lon if search_query else 28.9784
    m = folium.Map(location=[m_lat, m_lon], zoom_start=4 if search_query else 6, tiles="CartoDB dark_matter")
    if search_query:
        folium.Marker([lat, lon], popup=m_text, icon=folium.Icon(color='red', icon='ship', prefix='fa')).add_to(m)
        folium.PolyLine(locations=[[lat, lon], [40.98, 28.90]], color="#00f2fe", weight=3).add_to(m)
    else:
        folium.Marker([41.15, 29.10], popup="MSC TESSA (Aktif Kargo)", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=450)

elif menu == "📄 Evrak Analiz (OCR)":
    st.title("📄 Akıllı Evrak Doğrulama Terminali")
    st.file_uploader("Evrak Yükleyin (PDF/JPG/PNG)", type=["pdf", "jpg", "png"])

elif menu == "⚓ Özel Gemi Röntgeni ($20)":
    st.title("⚓ Özel Gemi Röntgeni & Cargo Manifest Detayları")
    ship_imo = st.text_input("Gemi IMO Numarası Girin:", placeholder="Örn: 9930038")
    if ship_imo:
        st.markdown('<div style="background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; text-align:center;"><h3>💳 RAPOR SATIN ALMA PANELİ</h3><p style="color: #cbd5e1; font-size:14px; margin-bottom:15px;">Bu sorgu için hesabınızdan <b>$20.00 USD</b> düşülecektir.</p><button style="background-color:#d4af37; color:#0e1c36; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">Kredi Kartı ile Güvenli Öde</button></div>', unsafe_allow_html=True)
