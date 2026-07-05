import streamlit as st
import requests
import json
import time
import random
import os
from datetime import datetime

# ------------------- SAYFA YAPILANDIRMASI -------------------
st.set_page_config(
    page_title="Interlock Global AI Terminal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------- ÖZEL CSS (TEMA + SPLIT-FLAP + MENÜ) -------------------
st.markdown("""
<style>
    /* Ana arka plan – Parlamento Mavisi */
    .stApp {
        background-color: #0a1128;
        color: #ffffff;
    }
    .stApp * {
        color: #ffffff !important;
    }
    a {
        color: #4a9eff !important;
    }
    .top-menu {
        background-color: #02040a;
        padding: 10px 20px;
        border-radius: 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        border-bottom: 1px solid #1a2a4a;
    }
    .top-menu .menu-item {
        color: #b0c4de !important;
        font-weight: 500;
        margin: 0 15px;
        cursor: pointer;
        padding: 6px 14px;
        border-radius: 20px;
        background: transparent;
        transition: 0.2s;
        border: none;
        font-size: 16px;
    }
    .top-menu .menu-item:hover {
        background: #1a2a4a;
        color: #ffffff !important;
    }
    .top-menu .menu-item.active {
        background: #2a4a7a;
        color: #ffffff !important;
    }
    .flap-container {
        background: #02040a;
        padding: 8px 15px;
        border-radius: 6px;
        margin-bottom: 20px;
        border-top: 1px solid #1a2a4a;
        border-bottom: 1px solid #1a2a4a;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
    }
    .flap-card {
        background: #02040a;
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 120px;
        flex: 1 0 auto;
        text-align: center;
        border-right: 1px solid #1a2a4a;
        margin: 4px 0;
    }
    .flap-card:last-child {
        border-right: none;
    }
    .flap-symbol {
        font-size: 14px;
        color: #8a9bb5;
        letter-spacing: 1px;
        font-weight: 300;
    }
    .flap-price {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        display: inline-block;
        background: #02040a;
        padding: 0 8px;
        border-left: 1px solid #2a3a5a;
        border-right: 1px solid #2a3a5a;
        margin: 0 4px;
        transition: all 0.1s ease;
        line-height: 1.4;
    }
    .flap-change {
        font-size: 14px;
        font-weight: 500;
        margin-left: 6px;
    }
    .flap-change.positive { color: #4caf50; }
    .flap-change.negative { color: #f44336; }
    .flap-nav {
        background: transparent;
        border: 1px solid #2a4a6a;
        color: #b0c4de;
        border-radius: 4px;
        padding: 2px 10px;
        margin: 0 3px;
        cursor: pointer;
        font-size: 16px;
        transition: 0.2s;
    }
    .flap-nav:hover {
        background: #1a2a4a;
        color: #ffffff;
    }
    .search-box {
        background: #02040a;
        padding: 20px 25px;
        border-radius: 8px;
        border: 1px solid #1a2a4a;
        margin-bottom: 25px;
    }
    .search-box input {
        background: #0a1128 !important;
        border: 1px solid #2a4a6a !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        padding: 12px 20px !important;
        font-size: 18px !important;
    }
    .search-box button {
        background: #1a3a6a !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        padding: 12px 35px !important;
        font-weight: 600;
        transition: 0.2s;
    }
    .search-box button:hover {
        background: #2a5a9a !important;
    }
    .report-section {
        background: #0a1128;
        border-left: 3px solid #2a5a9a;
        padding: 15px 20px;
        margin: 12px 0;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0,20,50,0.5);
    }
    .report-section h3 {
        color: #b0c4de;
        border-bottom: 1px solid #1a2a4a;
        padding-bottom: 6px;
    }
    .paywall-box {
        background: #02040a;
        border: 2px dashed #2a5a9a;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        text-align: center;
    }
    .paywall-box .email-list {
        color: #8a9bb5;
        font-size: 14px;
        letter-spacing: 0.5px;
        background: #0a1128;
        padding: 10px;
        border-radius: 6px;
        margin: 15px 0;
    }
    .stButton button {
        background: #1a3a6a !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-weight: 600;
        border: none !important;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #2a5a9a !important;
        transform: scale(1.02);
    }
    .error-box {
        background: #2a0a0a;
        border: 1px solid #aa3333;
        color: #ff8888;
        padding: 12px;
        border-radius: 6px;
        font-family: monospace;
        margin: 15px 0;
    }
    .reportview-container .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
    }
    footer { display: none; }
    @media (max-width: 768px) {
        .flap-card { min-width: 80px; }
        .flap-price { font-size: 18px; }
        .top-menu .menu-item { font-size: 13px; margin: 0 6px; padding: 4px 10px; }
        .search-box input { font-size: 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ------------------- SABİT BELLEK (IŞIK HIZINDA VERİ) -------------------
if 'flap_data' not in st.session_state:
    st.session_state.flap_data = {
        "XAU": {"price": 2345.20, "change": 0.45},
        "XAG": {"price": 27.85, "change": -0.12},
        "WTI": {"price": 82.45, "change": 1.23},
        "WHT": {"price": 5.67, "change": -0.34},
        "HG":  {"price": 4.32, "change": 0.07},
        "NG":  {"price": 2.15, "change": -0.89}
    }
    st.session_state.flap_symbols = ["XAU", "XAG", "WTI", "WHT", "HG", "NG"]

# ------------------- ÜST MENÜ (YATAY, SİDEBAR YOK) -------------------
with st.container():
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    with col1:
        st.image("https://via.placeholder.com/40x40/0a1128/4a9eff?text=IL", width=40)
    with col2:
        st.selectbox("🌐 Dil", ["Türkçe", "English", "Русский"], key="lang", label_visibility="collapsed")
    with col3:
        if st.button("🛰️ Otonom Ajan", key="menu_agent", use_container_width=True):
            st.session_state.menu_page = "agent"
    with col4:
        if st.button("📄 OCR Evrak Doğrulama", key="menu_ocr", use_container_width=True):
            st.session_state.menu_page = "ocr"
    with col5:
        if st.button("⚓ Gemi Röntgeni ($20)", key="menu_ship", use_container_width=True):
            st.session_state.menu_page = "ship"

if "menu_page" not in st.session_state:
    st.session_state.menu_page = "agent"

# ------------------- BORSA KADRANLARI (@st.fragment) -------------------
@st.fragment
def render_flap_cards_v2():
    symbols = st.session_state.flap_symbols
    cols = st.columns(len(symbols))
    for idx, sym in enumerate(symbols):
        with cols[idx]:
            st.markdown(f"<div style='font-size:14px;color:#8a9bb5;text-align:center;'>{sym}</div>", unsafe_allow_html=True)
            data = st.session_state.flap_data[sym]
            price = data["price"]
            change = data["change"]
            change_color = "#4caf50" if change >= 0 else "#f44336"
            st.markdown(f"""
            <div style='text-align:center;'>
                <span style='font-size:30px;font-weight:700;color:#ffffff;background:#02040a;padding:0 8px;border-left:1px solid #2a3a5a;border-right:1px solid #2a3a5a;'>{price:.2f}</span>
                <span style='font-size:16px;font-weight:500;color:{change_color};margin-left:6px;'>{change:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("◀", key=f"flap_left_{sym}"):
                    st.session_state.flap_data[sym]["price"] += random.uniform(-2, 2)
                    st.session_state.flap_data[sym]["change"] += random.uniform(-0.5, 0.5)
            with c3:
                if st.button("▶", key=f"flap_right_{sym}"):
                    st.session_state.flap_data[sym]["price"] += random.uniform(-2, 2)
                    st.session_state.flap_data[sym]["change"] += random.uniform(-0.5, 0.5)

render_flap_cards_v2()

# ------------------- ARAÇ (ARAMA MOTORU) – FORM YOK -------------------
st.markdown('<div class="search-box">', unsafe_allow_html=True)
col_search1, col_search2 = st.columns([5, 1])
with col_search1:
    query = st.text_input("🔍 Emtia, rota veya ürün ara... (ör: keten tohumu kazakistan - almanya)", 
                          placeholder="Örn: kinoa, alüminyum, buğday ukrayna - türkiye",
                          label_visibility="collapsed")
with col_search2:
    search_clicked = st.button("🔄 ARA", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------- API FALLBACK ZİNCİRİ (secrets TAMAMEN KALDIRILDI) -------------------
def call_ai_api(prompt):
    """Gemini (env) -> Groq (env) -> OpenRouter (ücretsiz) fallback zinciri, secrets kullanılmaz."""
    # Environment variable'lardan oku, yoksa boş string
    gemini_key_1 = os.getenv("GEMINI_API_KEY_1", "")
    gemini_key_2 = os.getenv("GEMINI_API_KEY_2", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    api_chain = [
        ("gemini", gemini_key_1),
        ("gemini", gemini_key_2),
        ("groq", groq_key),
        ("openrouter", "free")
    ]
    errors = []
    for provider, key in api_chain:
        try:
            if provider == "gemini" and key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = requests.post(url, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    errors.append(f"Gemini (key) hata: {resp.status_code}")
            elif provider == "groq" and key:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                else:
                    errors.append(f"Groq hata: {resp.status_code}")
            elif provider == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                payload = {
                    "model": "meta-llama/llama-3-8b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
                resp = requests.post(url, json=payload, timeout=15)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                else:
                    errors.append(f"OpenRouter hata: {resp.status_code}")
        except Exception as e:
            errors.append(f"{provider} exception: {str(e)}")
            continue
    raise Exception("Tüm API'ler başarısız oldu. Loglar:\n" + "\n".join(errors))

# ------------------- RAPOR OLUŞTURMA (3 BÖLÜM) -------------------
def generate_report(query):
    prompt = f"""
    Sen Interlock Global AI Terminal’in istihbarat ajanısın. Kullanıcı şu sorguyu yaptı: "{query}".
    
    Lütfen aşağıdaki 3 bölümden oluşan profesyonel bir emtia raporu oluştur:
    1. GÜMRÜK REJİMİ VE MEVZUAT: İlgili ülkelerin ithalat/ihracat rejimleri, vergiler, kotalar.
    2. LOJİSTİK ROTALAR: En uygun nakliye güzergahları, tahmini transit süreleri, liman bilgileri.
    3. FİYAT MATRİSİ VE TREND: Güncel fiyat aralıkları, geçmiş 1 ay trendi, volatilite analizi.
    
    Rapor kurumsal, özlü ve veri odaklı olsun. Markdown formatında.
    """
    try:
        return call_ai_api(prompt)
    except Exception as e:
        st.markdown(f'<div class="error-box">⚠️ SİSTEM HATASI (şeffaf log):<br>{str(e)}</div>', unsafe_allow_html=True)
        return None

# ------------------- ANA SAYFA İÇERİĞİ (Menü kontrolü) -------------------
if st.session_state.menu_page == "agent":
    if search_clicked and query.strip():
        with st.spinner("🔄 Çoklu yapay zeka ajanları dünyayı tarıyor..."):
            report = generate_report(query)
        if report:
            st.markdown('<div class="report-section"><h3>📊 GÜMRÜK REJİMİ VE MEVZUAT</h3>', unsafe_allow_html=True)
            parts = report.split("###")
            for part in parts:
                st.markdown(part)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="paywall-box">
                <h4>🔒 Premium Raporun Tamamı</h4>
                <p style="color:#8a9bb5;">5 gerçek üretici/ithalatçı firma e-postası ve Incoterms maliyet dökümleri</p>
                <div class="email-list">
                    📧 info@firma1.com • 📧 sales@firma2.com • 📧 trade@firma3.com<br>
                    📧 procurement@firma4.com • 📧 logistics@firma5.com
                </div>
                <div style="background:#0a1128;padding:8px;border-radius:4px;margin:10px 0;font-family:monospace;">
                    INCOTERMS: CIF, FOB, EXW, DAP, DDP (detaylı maliyetler gizli)
                </div>
                <br>
                <form action="https://your-stripe-payment-link.com" method="GET" target="_blank">
                    <button type="submit" style="background:#1a3a6a;color:white;border:none;padding:14px 40px;border-radius:30px;font-size:18px;font-weight:600;cursor:pointer;">
                        💳 Premium PDF Raporu İndir ($19.99)
                    </button>
                </form>
                <p style="font-size:12px;color:#4a6a8a;margin-top:10px;">Stripe ile güvenli ödeme</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔎 Lütfen yukarıdaki arama çubuğuna bir emtia veya rota girip 'ARA' butonuna basın.")

elif st.session_state.menu_page == "ocr":
    st.header("📄 OCR Evrak Doğrulama")
    st.write("Bu bölümde fatura, konşimento veya gümrük belgelerinin yapay zeka ile doğrulaması yapılır.")
    uploaded_file = st.file_uploader("Belge yükleyin (PDF/JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file:
        st.success(f"📎 {uploaded_file.name} yüklendi. İşleniyor... (demo)")

elif st.session_state.menu_page == "ship":
    st.header("⚓ Özel Gemi Röntgeni ($20)")
    st.write("Canlı kargo gemisi takibi ve röntgen analizi.")
    try:
        import folium
        from streamlit_folium import folium_static
        m = folium.Map(location=[40.0, 30.0], zoom_start=4)
        folium.Marker([40.0, 30.0], popup="Örnek Gemi").add_to(m)
        folium_static(m, width=700, height=400)
    except ImportError:
        st.warning("Folium kütüphanesi yüklü değil. 'pip install folium streamlit-folium' ile kurun.")
    st.info("Bu özellik için premium abonelik gereklidir (demo amaçlı).")
