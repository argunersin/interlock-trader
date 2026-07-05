import streamlit as st
import random
import time
import io
import base64
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ------------------- SAYFA YAPILANDIRMASI -------------------
st.set_page_config(
    page_title="Interlock Global AI Terminal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------- TÜRKÇE EMTİA GRUPLARI (DEMO FİYATLAR) -------------------
INITIAL_PRICES = {
    "Altın": 2350.50, "Gümüş": 28.75, "Ham Petrol (WTI)": 82.45, "Ham Petrol (Brent)": 86.20,
    "Doğalgaz": 2.15, "Buğday": 620.00, "Mısır": 440.00, "Soya Fasulyesi": 1180.00,
    "Keten Tohumu": 770.73, "Şeker": 19.50, "Kahve": 245.00, "Kakao": 7200.00,
    "Pamuk": 72.00, "Bakır": 4.32, "Alüminyum": 2600.00, "Çinko": 2800.00,
    "Nikel": 17000.00, "Üre (Gübre)": 450.00, "PVC": 850.00
}
COMMODITY_GROUPS = {
    "🥇 Değerli Metaller": ["Altın", "Gümüş"],
    "🛢️ Enerji": ["Ham Petrol (WTI)", "Ham Petrol (Brent)", "Doğalgaz"],
    "🌾 Tahıllar & Yağlı Tohumlar": ["Buğday", "Mısır", "Soya Fasulyesi", "Keten Tohumu"],
    "🍫 Yumuşak Emtialar": ["Şeker", "Kahve", "Kakao", "Pamuk"],
    "🔩 Endüstriyel Metaller": ["Bakır", "Alüminyum", "Çinko", "Nikel"],
    "🧪 Kimya & Gübre": ["Üre (Gübre)", "PVC"]
}

if "prices" not in st.session_state:
    st.session_state.prices = INITIAL_PRICES.copy()
    st.session_state.change = {name: 0.0 for name in INITIAL_PRICES}

def update_prices(volatility=0.015):
    for name in st.session_state.prices:
        old = st.session_state.prices[name]
        delta = random.uniform(-volatility, volatility) * old
        new = old + delta
        st.session_state.prices[name] = round(new, 2)
        st.session_state.change[name] = round((delta / old) * 100, 2)

# ------------------- CSS (HAVAALANI TERMİNALİ) -------------------
st.markdown("""
<style>
    .stApp { background-color: #0a1128; color: #ffffff; }
    .stApp * { color: #ffffff !important; }
    .top-menu {
        background-color: #02040a;
        padding: 8px 15px;
        border-radius: 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        border-bottom: 1px solid #1a2a4a;
        flex-wrap: wrap;
    }
    .top-menu .menu-item {
        color: #b0c4de !important;
        font-weight: 500;
        margin: 0 8px;
        cursor: pointer;
        padding: 5px 12px;
        border-radius: 20px;
        background: transparent;
        border: none;
        font-size: 14px;
    }
    .top-menu .menu-item:hover { background: #1a2a4a; color: #fff !important; }
    .group-title {
        color: #6a8aaa;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
        text-align: left;
        margin: 15px 0 8px 0;
        border-bottom: 1px solid #1a2a4a;
        padding-bottom: 4px;
    }
    [data-testid="stMetric"] {
        background-color: #02040a !important;
        padding: 10px 8px !important;
        border-radius: 6px !important;
        border: 1px solid #1a2a4a !important;
        text-align: center !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.9) !important;
        margin: 2px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8a9bb5 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        justify-content: center !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        font-family: 'Courier New', monospace !important;
        justify-content: center !important;
        background: #010308 !important;
        padding: 0 10px !important;
        border-left: 1px solid #2a3a5a !important;
        border-right: 1px solid #2a3a5a !important;
        display: inline-block !important;
        line-height: 1.6 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        justify-content: center !important;
        margin-left: 6px !important;
    }
    .search-box {
        background: #02040a;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #1a2a4a;
        margin: 15px 0;
    }
    .search-box input {
        background: #0a1128 !important;
        border: 1px solid #2a4a6a !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        padding: 10px 18px !important;
        font-size: 16px !important;
    }
    .search-box button {
        background: #1a3a6a !important;
        border: none !important;
        color: #fff !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-weight: 600;
    }
    .search-box button:hover { background: #2a5a9a !important; }
    .report-section {
        background: #0a1128;
        border-left: 4px solid #2a5a9a;
        padding: 12px 18px;
        margin: 10px 0;
        border-radius: 4px;
        box-shadow: 0 0 20px rgba(0,20,50,0.5);
    }
    .paywall-box {
        background: #02040a;
        border: 2px solid #2a5a9a;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        text-align: center;
    }
    .paywall-box .email-list {
        color: #8a9bb5;
        font-size: 13px;
        background: #0a1128;
        padding: 8px;
        border-radius: 4px;
        margin: 10px 0;
    }
    footer { display: none; }
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0rem !important; }
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] { font-size: 18px !important; padding: 0 4px !important; }
        .top-menu .menu-item { font-size: 11px; margin: 0 4px; padding: 4px 8px; }
        .search-box input { font-size: 14px; }
    }
</style>
""", unsafe_allow_html=True)

# ------------------- ÜST MENÜ -------------------
with st.container():
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    with col1:
        st.image("https://via.placeholder.com/40x40/0a1128/4a9eff?text=IL", width=40)
    with col2:
        st.selectbox("🌐 Dil", ["Türkçe", "English"], key="lang", label_visibility="collapsed")
    with col3:
        if st.button("🛰️ Otonom Ajan", key="menu_agent", use_container_width=True):
            st.session_state.menu_page = "agent"
    with col4:
        if st.button("📄 OCR Evrak", key="menu_ocr", use_container_width=True):
            st.session_state.menu_page = "ocr"
    with col5:
        if st.button("⚓ Gemi Röntgeni ($20)", key="menu_ship", use_container_width=True):
            st.session_state.menu_page = "ship"

if "menu_page" not in st.session_state:
    st.session_state.menu_page = "agent"

# ------------------- PANO (GRID 3) -------------------
st.markdown("### ✈️ CANLI EMTİA FİYATLARI (Terminal Panosu)")
col_update, col_info = st.columns([1, 5])
with col_update:
    if st.button("🔄 Fiyatları Güncelle (Roll!)", use_container_width=True):
        update_prices(0.02)
        st.rerun()
with col_info:
    st.caption("Her tıklamada fiyatlar değişir, kartlar döner.")

for group_name, products in COMMODITY_GROUPS.items():
    st.markdown(f"<div class='group-title'>{group_name}</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            price = st.session_state.prices.get(product, 0.0)
            change = st.session_state.change.get(product, 0.0)
            st.metric(label=product, value=f"{price:.2f}", delta=f"{change:+.2f}%", delta_color="normal")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"◀ Önceki ({group_name[:2]})", key=f"prev_{group_name}"):
            update_prices(0.01); st.rerun()
    with c2:
        if st.button(f"Sonraki ▶ ({group_name[:2]})", key=f"next_{group_name}"):
            update_prices(0.01); st.rerun()
    st.markdown("---")

# ------------------- ARAMA MOTORU -------------------
st.markdown('<div class="search-box">', unsafe_allow_html=True)
st.markdown("**🔍 Emtia veya Rota Ara** (*Örn:* `şeker` veya `keten tohumu kazakistan türkiye`)")
col_search1, col_search2 = st.columns([5, 1])
with col_search1:
    query = st.text_input("", placeholder="Ürün adı veya 'Ürün SatıcıÜlke AlıcıÜlke'", label_visibility="collapsed")
with col_search2:
    search_clicked = st.button("🔄 ARA", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- AI RAPOR (FALLBACK) -------------------
def call_ai_api(prompt):
    try:
        import requests
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5, "max_tokens": 1024
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except: pass
    return None

def generate_report(query):
    words = query.split(); is_bilateral = len(words) >= 3
    prefix = "spesifik rota" if is_bilateral else "küresel piyasa"
    prompt = f"Kullanıcı '{query}' için {prefix} raporu istiyor. 3 bölüm: Gümrük/Mevzuat, Lojistik/Navlun, Fiyat/Trend. Markdown."
    ai = call_ai_api(prompt)
    if ai:
        return ai
    else:
        # Zengin örnek rapor (PDF için de kullanılacak)
        return f"""
### 📊 KAPSAMLI ÖN İZLEME RAPORU: {query.upper()}

**1. GÜMRÜK VE MEVZUAT ANALİZİ**  
- Güncel ithalat vergisi oranı: %8,5 (standart)  
- Anti-damping riski: Düşük (henüz soruşturma yok)  
- Önerilen HS Kodu: 7601.10 (Alüminyum külçe)  

**2. LOJİSTİK VE NAVLUN DURUMU**  
- En uygun rota: **Kazakistan (Aktau Limanı) → Karadeniz → Türkiye (İzmir)**  
- Tahmini transit süresi: 22 gün  
- Konteyner navlunu (40ft): $4.200 - $5.800 arası  

**3. FİYAT TRENDİ VE TAHMİN**  
- Güncel LME Alüminyum: $2.620/Ton  
- 1 aylık değişim: +%3.2 (yukarı yönlü)  
- 3 aylık tahmin: $2.750/Ton (arz sıkışıklığı nedeniyle)
"""

# ------------------- 📄 PDF OLUŞTURUCU (AFİLLİ VE KAPSAMLI) -------------------
def create_pdf_report(query, report_md):
    """reportlab ile grafikli, tablolu profesyonel PDF oluştur."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Başlık Stili
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.darkblue, alignment=TA_CENTER, spaceAfter=12)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.grey, alignment=TA_CENTER)
    body_style = styles['BodyText']
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceAfter=6)

    # 1. Başlık
    story.append(Paragraph("INTERLOCK GLOBAL AI TERMINAL", title_style))
    story.append(Paragraph(f"Kapsamlı Emtia İstihbarat Raporu", sub_style))
    story.append(Paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d-%m-%Y %H:%M')}", sub_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>Konu:</b> {query.upper()}", body_style))
    story.append(Spacer(1, 0.3*cm))

    # 2. Grafik Ekle (Matplotlib ile çizilmiş simüle fiyat)
    fig, ax = plt.subplots(figsize=(6, 3))
    days = list(range(1, 31))
    base_price = random.randint(500, 3000)
    prices = [base_price + sum(random.uniform(-5, 5) for _ in range(i)) for i in range(30)]
    ax.plot(days, prices, marker='o', linestyle='-', color='#1a3a6a', linewidth=2)
    ax.set_title(f"{query.upper()} - Son 30 Gün Fiyat Trendi", fontsize=10)
    ax.set_xlabel("Gün")
    ax.set_ylabel("Fiyat ($/Ton)")
    ax.grid(True, linestyle='--', alpha=0.5)
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)
    img = Image(img_buffer, width=15*cm, height=8*cm)
    story.append(img)
    story.append(Spacer(1, 0.5*cm))

    # 3. Rapor Metnini Parse et (Markdown'dan temizle)
    lines = report_md.split('\n')
    for line in lines:
        if line.strip().startswith('#'):
            story.append(Paragraph(line.replace('#', '').strip(), h2_style))
        elif line.strip():
            story.append(Paragraph(line.strip(), body_style))
        story.append(Spacer(1, 0.1*cm))

    # 4. Tablo: Potansiyel Alıcı/Satıcı Firmalar
    story.append(Paragraph("Potansiyel Ticaret Firmaları", h2_style))
    data = [
        ['Firma Adı', 'Rol', 'Ülke'],
        ['Global Metal Trading', 'Alıcı', 'Türkiye'],
        ['Eurasian Resources', 'Satıcı', 'Kazakistan'],
        ['İzmir Alüminyum A.Ş.', 'Alıcı', 'Türkiye'],
        ['Almaty Export Hub', 'Satıcı', 'Kazakistan'],
        ['MSC Logistics', 'Navlun', 'İsviçre']
    ]
    table = Table(data, colWidths=[5*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    # 5. Footer (Ücret Uyarısı)
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.red, alignment=TA_CENTER)
    story.append(Paragraph("<b>⚠️ ÖNEMLİ UYARI:</b> Bu rapor önizleme amaçlıdır. Tam sürüm ve gerçek zamanlı veri akışı için ileride $19.99/rapor ücretlendirmesi uygulanacaktır.", footer_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("© 2025 Interlock Global - Tüm hakları saklıdır.", ParagraphStyle('Copy', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------- ANA SAYFA RAPOR + PDF BUTONU -------------------
if st.session_state.menu_page == "agent":
    if search_clicked and query.strip():
        with st.spinner("🔄 Yapay zeka ajanları taranıyor..."):
            report_text = generate_report(query)
        
        if report_text:
            # Ekran Gösterimi
            st.markdown(f'<div class="report-section"><h3>📌 RAPOR: {query.upper()}</h3>', unsafe_allow_html=True)
            st.markdown(report_text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 1. PAYWALL GÖRÜNÜMÜ (Firmalar)
            st.markdown("""
            <div class="paywall-box">
                <h4>🔒 Premium Raporun Tamamı (5 Gerçek Firma + Incoterms)</h4>
                <div class="email-list">
                    📧 info@globaltraders.com • 📧 sales@agriexport.com • 📧 trade@metalhub.com<br>
                    📧 procurement@logisticsworld.com • 📧 cargo@shippingline.com
                </div>
                <div style="background:#0a1128;padding:6px;border-radius:4px;margin:8px 0;font-family:monospace;font-size:14px;">
                    INCOTERMS: CIF, FOB, EXW, DAP, DDP (detaylı maliyetler gizli)
                </div>
            """, unsafe_allow_html=True)
            
            # 2. PDF İNDİR BUTONU (Şimdilik Ücretsiz, Uyarılı)
            pdf_bytes = create_pdf_report(query, report_text)
            st.download_button(
                label="📄 Bu Raporu PDF Olarak İndir (Ücretsiz Deneme)",
                data=pdf_bytes,
                file_name=f"Interlock_Rapor_{query[:20]}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.warning("🚨 **Bu sürüm deneme amaçlıdır.** Ticari kullanım ve gerçek zamanlı tam veri akışı için ileride **$19.99** abonelik gerekecektir.", icon="⚠️")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔎 Lütfen yukarıdaki arama çubuğuna bir emtia veya rota girip 'ARA' butonuna basın.")

elif st.session_state.menu_page == "ocr":
    st.header("📄 OCR Evrak Doğrulama (Demo)")
    uploaded_file = st.file_uploader("Belge yükleyin (PDF/JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file:
        st.success(f"📎 {uploaded_file.name} yüklendi. (Demo)")

elif st.session_state.menu_page == "ship":
    st.header("⚓ Özel Gemi Röntgeni ($20 - Demo)")
    try:
        import folium
        from streamlit_folium import folium_static
        m = folium.Map(location=[40.0, 30.0], zoom_start=4)
        folium.Marker([40.0, 30.0], popup="Örnek Gemi").add_to(m)
        folium_static(m, width=700, height=400)
    except:
        st.warning("Harita kütüphanesi yüklenemedi.")
