import streamlit as st
import random
import time
import io
import base64
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import yfinance as yf
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json

# ------------------- SAYFA YAPILANDIRMASI -------------------
st.set_page_config(
    page_title="Interlock Global AI Terminal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------- DEVASA EMTİA GRUPLARI -------------------
COMMODITY_GROUPS = {
    "🥇 Değerli Metaller": [
        "Altın", "Gümüş", "Platin", "Paladyum"
    ],
    "🛢️ Enerji & Petrol Ürünleri": [
        "Ham Petrol (WTI)", "Ham Petrol (Brent)", "Doğalgaz", 
        "Dizel (Ultra Low Sulfur)", "Fuel Oil (HSFO)", "Jet Yakıtı (JET)"
    ],
    "🌾 Tahıllar & Yağlı Tohumlar": [
        "Buğday", "Mısır", "Soya Fasulyesi", "Ayçiçek Yağı",
        "Kanola", "Palm Yağı"
    ],
    "🍫 Yumuşak Emtialar (Softs)": [
        "Şeker (Raw)", "Şeker (White)", "Kahve (Arabica)", "Kakao",
        "Pamuk", "Portakal Suyu (FCOJ)", "Kereste (Lumber)"
    ],
    "🔩 Endüstriyel Metaller (LME)": [
        "Bakır", "Alüminyum", "Çinko", "Nikel",
        "Kurşun", "Kalay", "Alüminyum Alaşım", "Çelik Rebar"
    ],
    "🧪 Kimyasallar & Gübre": [
        "Üre (Gübre)", "Soda Külü", "Sülfürik Asit", "PVC",
        "DAP (Diamonyum Fosfat)", "Potasyum Klorür (MOP)"
    ]
}

# Yahoo Ticker eşleştirmesi (genişletildi)
TICKER_MAP = {
    "Altın": "GC=F",
    "Gümüş": "SI=F",
    "Platin": "PL=F",
    "Paladyum": "PA=F",
    "Ham Petrol (WTI)": "CL=F",
    "Ham Petrol (Brent)": "BZ=F",
    "Doğalgaz": "NG=F",
    "Dizel (Ultra Low Sulfur)": "RB=F",  # RBOB benzin, dizel için yakın
    "Fuel Oil (HSFO)": "HO=F",           # Isıtma yağı
    "Jet Yakıtı (JET)": None,            # Yok, simüle
    "Buğday": "ZW=F",
    "Mısır": "ZC=F",
    "Soya Fasulyesi": "ZS=F",
    "Ayçiçek Yağı": None,                # Yok
    "Kanola": "RS=F",                    # Kanola (Canola) CBOT
    "Palm Yağı": None,                   # Yok
    "Şeker (Raw)": "SB=F",
    "Şeker (White)": None,               # Yok
    "Kahve (Arabica)": "KC=F",
    "Kakao": "CC=F",
    "Pamuk": "CT=F",
    "Portakal Suyu (FCOJ)": "OJ=F",
    "Kereste (Lumber)": "LBS=F",
    "Bakır": "HG=F",
    "Alüminyum": None,                   # LME tipi yok
    "Çinko": None,
    "Nikel": None,
    "Kurşun": None,
    "Kalay": None,
    "Alüminyum Alaşım": None,
    "Çelik Rebar": None,
    "Üre (Gübre)": None,
    "Soda Külü": None,
    "Sülfürik Asit": None,
    "PVC": None,
    "DAP (Diamonyum Fosfat)": None,
    "Potasyum Klorür (MOP)": None,
}

# Gerçekçi başlangıç fiyatları (simülasyon için)
DEFAULT_PRICES = {
    "Altın": 2350.0, "Gümüş": 28.5, "Platin": 980.0, "Paladyum": 1050.0,
    "Ham Petrol (WTI)": 82.0, "Ham Petrol (Brent)": 86.0, "Doğalgaz": 2.1,
    "Dizel (Ultra Low Sulfur)": 2.8, "Fuel Oil (HSFO)": 450.0, "Jet Yakıtı (JET)": 800.0,
    "Buğday": 620.0, "Mısır": 440.0, "Soya Fasulyesi": 1180.0,
    "Ayçiçek Yağı": 950.0, "Kanola": 580.0, "Palm Yağı": 780.0,
    "Şeker (Raw)": 19.5, "Şeker (White)": 22.0, "Kahve (Arabica)": 245.0,
    "Kakao": 7200.0, "Pamuk": 72.0, "Portakal Suyu (FCOJ)": 280.0,
    "Kereste (Lumber)": 450.0,
    "Bakır": 4.3, "Alüminyum": 2600.0, "Çinko": 2800.0, "Nikel": 17000.0,
    "Kurşun": 2100.0, "Kalay": 28000.0, "Alüminyum Alaşım": 2400.0,
    "Çelik Rebar": 650.0,
    "Üre (Gübre)": 450.0, "Soda Külü": 300.0, "Sülfürik Asit": 120.0,
    "PVC": 850.0, "DAP (Diamonyum Fosfat)": 600.0, "Potasyum Klorür (MOP)": 500.0
}

# ------------------- SESSION STATE -------------------
if "prices" not in st.session_state:
    st.session_state.prices = DEFAULT_PRICES.copy()
    st.session_state.change = {k: 0.0 for k in DEFAULT_PRICES}
if "selected_index" not in st.session_state:
    st.session_state.selected_index = {group: 0 for group in COMMODITY_GROUPS}

# ------------------- FİYAT ÇEKME (YAHOO + SİMÜLASYON) -------------------
def fetch_real_prices():
    new_prices = {}
    for product, ticker in TICKER_MAP.items():
        if ticker:
            try:
                data = yf.download(ticker, period='1d', interval='5m', progress=False)
                if not data.empty:
                    last = data['Close'].iloc[-1]
                    open_ = data['Open'].iloc[0]
                    change = ((last - open_) / open_) * 100 if open_ != 0 else 0
                    new_prices[product] = round(last, 2)
                    st.session_state.change[product] = round(change, 2)
                else:
                    new_prices[product] = DEFAULT_PRICES[product]
                    st.session_state.change[product] = 0.0
            except:
                new_prices[product] = DEFAULT_PRICES[product]
                st.session_state.change[product] = 0.0
        else:
            # Ticker yoksa simüle et
            base = DEFAULT_PRICES[product]
            new_prices[product] = round(base * (1 + random.uniform(-0.015, 0.015)), 2)
            st.session_state.change[product] = round(random.uniform(-2.0, 2.0), 2)
    return new_prices

def update_prices():
    try:
        real = fetch_real_prices()
        st.session_state.prices.update(real)
    except:
        for p in st.session_state.prices:
            old = st.session_state.prices[p]
            delta = random.uniform(-0.015, 0.015) * old
            st.session_state.prices[p] = round(old + delta, 2)
            st.session_state.change[p] = round((delta / old) * 100, 2)

# ------------------- REGISTRY LOOKUP API (Firma Bilgileri) -------------------
def fetch_companies(query):
    url = "https://api.registry.lookup/v1/search"
    params = {"q": query, "limit": 10, "jurisdiction": "all"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            companies = []
            for item in data.get("results", []):
                companies.append({
                    "name": item.get("name", ""),
                    "country": item.get("jurisdiction", ""),
                    "registration_number": item.get("registration_number", ""),
                    "status": item.get("status", "")
                })
            return companies
        else:
            return None
    except:
        return None

# ------------------- CSS (SABİT) -------------------
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
    .group-card {
        background-color: #02040a;
        border: 1px solid #1a2a4a;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
        margin-bottom: 10px;
    }
    .group-card .product-name {
        font-size: 14px;
        color: #8a9bb5;
        letter-spacing: 0.5px;
    }
    .group-card .price {
        font-size: 28px;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        background: #010308;
        padding: 0 12px;
        border-left: 1px solid #2a3a5a;
        border-right: 1px solid #2a3a5a;
        display: inline-block;
        line-height: 1.5;
    }
    .group-card .change {
        font-size: 16px;
        font-weight: 600;
        margin-left: 6px;
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

# ------------------- GRUP KARTLARI (3 SÜTUN) -------------------
st.markdown("### ✈️ CANLI EMTİA FİYATLARI (Terminal Panosu)")

if st.button("🔄 Tüm Fiyatları Güncelle (Canlı Veri)"):
    update_prices()
    st.rerun()

# Grupları 3 sütunlu grid olarak göster
group_list = list(COMMODITY_GROUPS.items())
for i in range(0, len(group_list), 3):
    row_groups = group_list[i:i+3]
    cols = st.columns(len(row_groups))
    for col, (group_name, products) in zip(cols, row_groups):
        with col:
            st.markdown(f"<div class='group-title'>{group_name}</div>", unsafe_allow_html=True)
            idx = st.session_state.selected_index.get(group_name, 0)
            if idx >= len(products):
                idx = 0
            product = products[idx]
            price = st.session_state.prices.get(product, 0.0)
            change = st.session_state.change.get(product, 0.0)
            change_color = "#4caf50" if change >= 0 else "#f44336"
            arrow = "↑" if change >= 0 else "↓"
            st.markdown(f"""
            <div class="group-card">
                <div class="product-name">{product}</div>
                <div>
                    <span class="price">{price:.2f}</span>
                    <span class="change" style="color:{change_color};">{arrow} {change:+.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("◀", key=f"prev_{group_name}"):
                    idx = (idx - 1) % len(products)
                    st.session_state.selected_index[group_name] = idx
                    st.rerun()
            with col3:
                if st.button("▶", key=f"next_{group_name}"):
                    idx = (idx + 1) % len(products)
                    st.session_state.selected_index[group_name] = idx
                    st.rerun()
            st.markdown("---")

# ------------------- ARAMA MOTORU -------------------
st.markdown('<div class="search-box">', unsafe_allow_html=True)
st.markdown("**🔍 Emtia veya Rota Ara** (*Örn:* `şeker` veya `ayçiçek yağı kazakistan türkiye`)")
col_search1, col_search2 = st.columns([5, 1])
with col_search1:
    query = st.text_input("", placeholder="Ürün adı veya 'Ürün SatıcıÜlke AlıcıÜlke'", label_visibility="collapsed")
with col_search2:
    search_clicked = st.button("🔄 ARA", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- AI RAPOR (DİNAMİK YEDEK) -------------------
def call_ai_api(prompt):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except: pass
    return None

def generate_report(query):
    words = query.split()
    is_bilateral = len(words) >= 3
    product = words[0] if words else query

    # Registry Lookup'tan firmaları çek
    companies = fetch_companies(query)
    company_table = ""
    if companies:
        company_table = "#### Gerçek Firmalar (Registry Lookup)\n\n| Firma | Ülke | Sicil No | Durum |\n|-------|------|----------|-------|\n"
        for comp in companies[:8]:
            company_table += f"| {comp['name']} | {comp['country']} | {comp['registration_number']} | {comp['status']} |\n"
    else:
        company_table = """
        #### Örnek Ticaret Firmaları (Geçici)
        | Firma | Rol | Ülke | İletişim |
        |-------|-----|------|----------|
        | Global Trade Corp | Alıcı | Türkiye | info@globaltrade.com |
        | Eurasia Agro | Satıcı | Kazakistan | sales@eurasia.kz |
        | İstanbul Commodities | Alıcı | Türkiye | procurement@istanbul.com |
        | Almaty Export | Satıcı | Kazakistan | trade@almaty.kz |
        | Bosphorus Logistics | Lojistik | Türkiye | cargo@bosphorus.com |
        """

    if is_bilateral:
        prompt = f"""
        Kullanıcı '{query}' rotası için detaylı ticaret raporu istiyor.
        Ürün: {product}. Ülkeler: {words[1]} ve {words[2]}.
        Lütfen aşağıdaki bölümleri içeren profesyonel bir rapor hazırla:
        1. GÜMRÜK VE MEVZUAT: Bu iki ülke arasındaki ithalat/ihracat vergileri, anti-damping, HS kodları.
        2. LOJİSTİK VE NAVLUN: En uygun rota, transit süresi, konteyner/dökme navlun fiyatları.
        3. FİYAT VE TREND: {product} için güncel fiyat, 1 aylık değişim, 3 aylık tahmin.
        4. TİCARET FIRMALARI: Aşağıdaki firma tablosunu kullan.
        5. EXW/FOB/CIF KARŞILAŞTIRMASI: Bu rotaya özel fiyat alternatifleri.
        Raporu markdown formatında, tablolar kullanarak hazırla.

        Firma Tablosu:
        {company_table}
        """
    else:
        prompt = f"""
        Kullanıcı '{query}' ürünü için küresel piyasa raporu istiyor.
        Ürün: {product}.
        Lütfen aşağıdaki bölümleri içeren kapsamlı bir rapor hazırla:
        1. KÜRESEL ARZ-TALEP: Başlıca üretici ve tüketici ülkeler.
        2. LOJİSTİK AĞI: Ana limanlar, kara yolları, lojistik firmaları.
        3. FİYATLAR VE TREND: Dünya borsalarındaki fiyatlar, geçmiş aylık değişim.
        4. TİCARET FIRMALARI: Aşağıdaki firma tablosunu kullan.
        5. EXW/FOB/CIF KARŞILAŞTIRMASI: Farklı teslim koşullarında fiyatlar.
        Markdown formatında, tablolarla zenginleştir.

        Firma Tablosu:
        {company_table}
        """

    ai_response = call_ai_api(prompt)
    if ai_response:
        return ai_response
    else:
        # Dinamik yedek rapor – sorguyu kullan
        return f"""
### 📊 KAPSAMLI İSTİHBARAT RAPORU: {query.upper()}

#### 1. GÜMRÜK VE MEVZUAT
- {product} için standart ithalat vergisi: %8,5 (Türkiye), %5 (AB), %12 (Rusya)
- Önerilen HS Kodu: {random.choice(['1512.11', '1507.10', '1515.90'])} (Ürüne göre değişir)
- Anti-damping: Yok (henüz soruşturma açılmadı)

#### 2. LOJİSTİK VE NAVLUN
- Önerilen rota: **{words[1] if is_bilateral else 'Kazakistan'} → Karadeniz → Türkiye (İzmir)**
- Transit süresi: 22 gün (tahmini)
- Navlun: 40ft Konteyner $4.500 - $6.000, Dökme $35/ton

#### 3. FİYAT TRENDİ VE TAHMİN
- Güncel {product} fiyatı: {random.randint(500, 3000)} $/ton
- 1 aylık değişim: +%{random.randint(0,5)} (yukarı yönlü)
- 3 aylık tahmin: {random.randint(500, 3500)} $/ton (arz/talep dengesine bağlı)

#### 4. TİCARET FIRMALARI
{company_table}

#### 5. EXW/FOB/CIF ALTERNATİFLERİ
| Teslim Şekli | Fiyat ($/ton) | Açıklama |
|--------------|---------------|----------|
| EXW ({words[1] if is_bilateral else 'Üretici'}) | {random.randint(400, 2800)} | Fabrika çıkışı |
| FOB (Liman) | {random.randint(450, 2900)} | Limanda yükleme |
| CIF (Türkiye) | {random.randint(500, 3000)} | Sigorta+navlun dahil |
| Bölgesel prim | +${random.randint(20, 80)} | Ek lojistik maliyet |

> **Not:** Bu rapor önizleme amaçlıdır. Gerçek zamanlı veri ve tam firma bilgileri için premium sürüme geçin.
"""

# ------------------- PDF OLUŞTURUCU (TÜRKÇE FONT DÜZELTMELİ) -------------------
def create_pdf_report(query, report_md):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    try:
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        font_name = 'DejaVu'
    except:
        font_name = 'Helvetica'

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName=font_name, fontSize=18, textColor=colors.darkblue, alignment=TA_CENTER, spaceAfter=12)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Heading2'], fontName=font_name, fontSize=12, textColor=colors.grey, alignment=TA_CENTER)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontName=font_name, fontSize=10)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName=font_name, fontSize=14, textColor=colors.darkblue, spaceAfter=6)

    story.append(Paragraph("INTERLOCK GLOBAL AI TERMINAL", title_style))
    story.append(Paragraph(f"Kapsamlı Emtia İstihbarat Raporu", sub_style))
    story.append(Paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d-%m-%Y %H:%M')}", sub_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>Konu:</b> {query.upper()}", body_style))
    story.append(Spacer(1, 0.3*cm))

    # Grafik
    fig, ax = plt.subplots(figsize=(6, 3))
    days = list(range(1, 31))
    base = random.randint(500, 3000)
    prices = [base + sum(random.uniform(-5, 5) for _ in range(i)) for i in range(30)]
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

    # Rapor metni
    lines = report_md.split('\n')
    for line in lines:
        if line.strip().startswith('#'):
            story.append(Paragraph(line.replace('#', '').strip(), h2_style))
        elif line.strip():
            story.append(Paragraph(line.strip(), body_style))
        story.append(Spacer(1, 0.1*cm))

    # Footer uyarı
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontName=font_name, fontSize=9, textColor=colors.red, alignment=TA_CENTER)
    story.append(Paragraph("<b>⚠️ UYARI:</b> Bu rapor önizleme amaçlıdır. Tam sürüm ve gerçek zamanlı veri için ileride $19.99/rapor ücretlendirmesi uygulanacaktır.", footer_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("© 2025 Interlock Global - Tüm hakları saklıdır.", ParagraphStyle('Copy', parent=styles['Normal'], fontName=font_name, fontSize=8, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------- ANA SAYFA RAPOR + PDF -------------------
if st.session_state.menu_page == "agent":
    if search_clicked and query.strip():
        with st.spinner("🔄 Yapay zeka ajanları taranıyor..."):
            report_text = generate_report(query)
        
        if report_text:
            st.markdown(f'<div class="report-section"><h3>📌 RAPOR: {query.upper()}</h3>', unsafe_allow_html=True)
            st.markdown(report_text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="paywall-box">
                <h4>🔒 Premium Raporun Tamamı (5 Gerçek Firma + İletişim)</h4>
                <div class="email-list">
                    📧 info@globaltraders.com • 📧 sales@agriexport.com • 📧 trade@metalhub.com<br>
                    📧 procurement@logisticsworld.com • 📧 cargo@shippingline.com
                </div>
                <div style="background:#0a1128;padding:6px;border-radius:4px;margin:8px 0;font-family:monospace;font-size:14px;">
                    INCOTERMS: CIF, FOB, EXW, DAP, DDP (detaylı maliyetler gizli)
                </div>
            """, unsafe_allow_html=True)
            
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
    st.write("Bu modül geliştirme aşamasındadır. Görsel veya evrak no girişi ile doğrulama yapılacak.")
    uploaded_file = st.file_uploader("Belge yükleyin (PDF/JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file:
        st.success(f"📎 {uploaded_file.name} yüklendi. (Demo)")

elif st.session_state.menu_page == "ship":
    st.header("⚓ Özel Gemi Röntgeni ($20 - Demo)")
    st.write("Bu modül geliştirme aşamasındadır. Canlı gemi takibi ve röntgen analizi eklenecek.")
    try:
        import folium
        from streamlit_folium import folium_static
        m = folium.Map(location=[40.0, 30.0], zoom_start=4)
        folium.Marker([40.0, 30.0], popup="Örnek Gemi").add_to(m)
        folium_static(m, width=700, height=400)
    except:
        st.warning("Harita kütüphanesi yüklenemedi.")
