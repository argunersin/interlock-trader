# -*- coding: utf-8 -*-
"""
INTERLOCK GLOBAL AI TERMINAL
VIP Emtia İstihbarat Platformu — app.py
Mimari kurallar: Parlement Mavisi tema, Split-Flap borsa kadranları,
sidebar YOK, form YASAK, 4 katmanlı API sigorta zinciri, şeffaf hata raporlayıcısı.
"""

import streamlit as st
import random
import time
import json
import traceback
import requests

# ============================================================
# 0) SAYFA AYARLARI — Sidebar tamamen iptal, wide layout
# ============================================================
st.set_page_config(
    page_title="Interlock Global AI Terminal",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 1) KÜRESEL CSS — Parlement Mavisi tema + sidebar/whitespace kazıma
# ============================================================
st.markdown("""
<style>
    /* Sidebar'ı ve o kilit ok ikonunu kökten sök */
    section[data-testid="stSidebar"], div[data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Ana arkaplan — Parlement Mavisi */
    .stApp {
        background-color: #0a1128;
        color: #e8ecf5;
    }

    /* Streamlit varsayılan üst boşluk/footer/header temizliği */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    /* Alt beyaz boşluk bloklarını kazı */
    div[data-testid="stVerticalBlock"] > div:empty,
    iframe[title="streamlit_folium.st_folium"] {
        display: none !important;
    }

    /* Split-Flap Kadran Kartı */
    .flap-card {
        background-color: #02040a;
        border: 1px solid #1c2440;
        border-radius: 6px;
        text-align: center;
        padding: 14px 6px;
        position: relative;
        box-shadow: 0 0 12px rgba(0,0,0,0.6);
    }
    .flap-card::after {
        content: "";
        position: absolute;
        left: 0; right: 0; top: 50%;
        height: 1px;
        background: rgba(232,236,245,0.15);
    }
    .flap-symbol {
        font-size: 13px;
        color: #7a86b8;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .flap-value {
        font-size: 22px;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        color: #f5f7fb;
    }
    .flap-delta-up { color: #2ecc71; font-size: 13px; }
    .flap-delta-down { color: #e74c3c; font-size: 13px; }

    /* Üst yatay departman / dil şeridi */
    .top-strip {
        display: flex;
        gap: 8px;
        background-color: #050a1c;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid #1c2440;
        margin-bottom: 14px;
    }

    .stButton>button {
        background-color: #11183a;
        color: #e8ecf5;
        border: 1px solid #2a3563;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton>button:hover {
        border-color: #4a5fd9;
        color: #ffffff;
    }

    .stTextInput>div>div>input {
        background-color: #050a1c;
        color: #e8ecf5;
        border: 1px solid #2a3563;
    }

    .report-section {
        background-color: #0d1533;
        border: 1px solid #1c2440;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }

    .paywall-blur {
        filter: blur(6px);
        pointer-events: none;
        user-select: none;
    }

    .disclaimer {
        font-size: 12px;
        color: #7a86b8;
        border-top: 1px dashed #2a3563;
        margin-top: 10px;
        padding-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2) SESSION STATE — Sabit bellek (Instant Flash Memory)
#    Borsa verileri interneti asla beklemez; ilk açılışta bir kez
#    üretilir, sonrasında sadece session_state'ten okunur.
# ============================================================
if "ticker_data" not in st.session_state:
    seed_symbols = ["KETEN TOHUMU", "KİNOA", "ALÜMİNYUM", "PAMUK", "BUĞDAY", "BAKIR"]
    st.session_state.ticker_data = [
        {
            "symbol": s,
            "value": round(random.uniform(120, 980), 2),
            "delta": round(random.uniform(-3.5, 3.5), 2),
        }
        for s in seed_symbols
    ]

if "active_department" not in st.session_state:
    st.session_state.active_department = "Otonom Ajan"

if "language" not in st.session_state:
    st.session_state.language = "TR"

if "last_report" not in st.session_state:
    st.session_state.last_report = None

if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False

if "last_error_log" not in st.session_state:
    st.session_state.last_error_log = None


# ============================================================
# 3) SPLIT-FLAP KADRAN BLOĞU — @st.fragment ile Bölgesel Hafıza Zırhı
#    Bu blok yeniden çalışsa bile SADECE kendi alanını günceller,
#    sayfa hiçbir zaman kararmaz / flaş patlaması yaşanmaz.
# ============================================================
@st.fragment(run_every=4)
def render_ticker_wall():
    cols = st.columns(6)
    for i, col in enumerate(cols):
        item = st.session_state.ticker_data[i]
        # Sadece küçük bir "nabız" oynatması — internete gitmeden, sabit bellekten
        drift = round(random.uniform(-0.6, 0.6), 2)
        item["value"] = max(1, round(item["value"] + drift, 2))
        item["delta"] = round(item["delta"] * 0.9 + drift, 2)
        delta_class = "flap-delta-up" if item["delta"] >= 0 else "flap-delta-down"
        arrow = "▲" if item["delta"] >= 0 else "▼"
        with col:
            st.markdown(f"""
            <div class="flap-card">
                <div class="flap-symbol">{item['symbol']}</div>
                <div class="flap-value">{item['value']}</div>
                <div class="{delta_class}">{arrow} {abs(item['delta'])}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# 4) ÜST YATAY MENÜ — Sidebar yerine geçen departman + dil şeridi
# ============================================================
def render_top_strip():
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    departments = {
        "🤖 Otonom Ajan": "Otonom Ajan",
        "📄 OCR Evrak Doğrulama": "OCR Evrak Doğrulama",
        "⚓ Gemi Röntgeni ($20)": "Gemi Röntgeni",
    }
    cols = [c1, c2, c3]
    for col, (label, key) in zip(cols, departments.items()):
        with col:
            if st.button(label, use_container_width=True, key=f"dept_{key}"):
                st.session_state.active_department = key
    with c4:
        lang = st.selectbox(
            "🌐", ["TR", "EN", "DE", "AR"],
            index=["TR", "EN", "DE", "AR"].index(st.session_state.language),
            label_visibility="collapsed",
        )
        st.session_state.language = lang


# ============================================================
# 5) API SİGORTA ZİNCİRİ (Fallback Chain) — Şeffaf Hata Raporlayıcısı
#    Sıra: Gemini Key #1 -> Gemini Key #2 -> Groq -> OpenRouter (free)
#    st.secrets içine şu anahtarları eklemen gerekir:
#    GEMINI_API_KEY_1, GEMINI_API_KEY_2, GROQ_API_KEY, OPENROUTER_API_KEY (opsiyonel)
# ============================================================
def call_gemini(prompt: str, key_name: str) -> str:
    api_key = st.secrets.get(key_name, "")
    if not api_key:
        raise RuntimeError(f"{key_name} tanımlı değil (st.secrets).")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_groq(prompt: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY tanımlı değil.")
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_openrouter_free(prompt: str) -> str:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=25,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def generate_intelligence_report(query: str) -> dict:
    """
    4 katmanlı sigorta zinciri. Her katman sırayla denenir;
    tamamı düşerse şeffaf hata raporu döner (kullanıcıya asla
    'pembe hata' gösterilmez — gerçek log şeffaf şekilde sunulur).
    """
    prompt = (
        "Sen bir uluslararası emtia lojistik istihbarat ajanısın. "
        f"Şu sorgu için: '{query}' — 3 kısa kurumsal bölüm üret: "
        "1) Gümrük Rejimi Özeti 2) Lojistik Rota Analizi 3) Fiyat Matrisi. "
        "Ayrıca (varsa) örnek 5 üretici/ithalatçı firma adı ve iletişim biçimi öner. "
        "Yanıtın sonuna şunu ekle: '[AI_GENERATED_ESTIMATE]'."
    )

    chain = [
        ("Gemini #1", lambda: call_gemini(prompt, "GEMINI_API_KEY_1")),
        ("Gemini #2", lambda: call_gemini(prompt, "GEMINI_API_KEY_2")),
        ("Groq", lambda: call_groq(prompt)),
        ("OpenRouter (free)", lambda: call_openrouter_free(prompt)),
    ]

    errors = []
    for label, fn in chain:
        try:
            text = fn()
            return {"source": label, "text": text, "errors": errors}
        except Exception as e:
            errors.append(f"{label}: {repr(e)}")
            continue

    # Hepsi düştü — Şeffaf Hata Raporlayıcısı
    full_log = "\n".join(errors) + "\n\n" + traceback.format_exc()
    st.session_state.last_error_log = full_log
    return {"source": None, "text": None, "errors": errors}


# ============================================================
# 6) ARAMA MOTORU — FORM YOK. Saf text_input + button + Enter.
# ============================================================
def run_search():
    query = st.session_state.get("search_query", "").strip()
    if not query:
        st.warning("Lütfen bir emtia / rota girin. Örn: 'keten tohumu kazakistan - almanya'")
        return
    with st.spinner("Çoklu Yapay Zeka Ajanları küresel veriyi tarıyor..."):
        result = generate_intelligence_report(query)
    st.session_state.last_report = result
    st.session_state.premium_unlocked = False


def render_search_bar():
    st.text_input(
        "🔎 Emtia / Rota Ara",
        placeholder="Örn: kinoa | alüminyum | keten tohumu kazakistan - almanya",
        key="search_query",
        on_change=run_search,   # Saf Enter ile tetikleme
        label_visibility="collapsed",
    )
    st.button("İSTİHBARAT RAPORU OLUŞTUR", on_click=run_search, use_container_width=False)


# ============================================================
# 7) RAPOR GÖRÜNÜMÜ — 3 bölüm + paywall
# ============================================================
def render_report():
    result = st.session_state.last_report
    if not result:
        return

    if result["text"] is None:
        st.error("⚠️ Şeffaf Hata Raporlayıcısı: Tüm API katmanları yanıt veremedi.")
        with st.expander("Ham hata logunu görüntüle"):
            st.code(st.session_state.last_error_log or "Log bulunamadı.")
        return

    st.caption(f"Kaynak motor: {result['source']}")

    raw_text = result["text"]
    # Basit gösterim: tam metni 3 sahte-bölüm kartına böl (gerçek üretimde
    # modelin yapılandırılmış JSON döndürmesi istenmeli).
    st.markdown(f"""
    <div class="report-section">
        <h4>📦 Gümrük Rejimi & Lojistik & Fiyat Matrisi</h4>
        <p style="white-space: pre-wrap;">{raw_text[:600]}</p>
        <div class="disclaimer">
            Bu içerik yapay zeka ajanları tarafından tahmini olarak derlenmiştir;
            firma isimleri/e-postaları doğrulanmadan iş kararı almayınız. [AI_GENERATED_ESTIMATE]
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.premium_unlocked:
        st.markdown(f"""
        <div class="report-section paywall-blur">
            <h4>🔒 Premium: 5 Üretici/İthalatçı İletişim Bloğu + Incoterms Dökümü</h4>
            <p>{raw_text[600:1400] if len(raw_text) > 600 else 'Premium detaylar burada gizli.'}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💳 Premium PDF Raporu — $19.99 (Stripe)"):
            # NOT: Gerçek entegrasyonda burada Stripe Checkout Session
            # oluşturulup kullanıcı ödeme sayfasına yönlendirilmeli.
            st.session_state.premium_unlocked = True
            st.rerun()
    else:
        st.success("✅ Premium içerik açıldı (ödeme entegrasyonu backend'de tamamlanmalı).")
        st.markdown(f"""
        <div class="report-section">
            <h4>🔓 Premium Detaylar</h4>
            <p style="white-space: pre-wrap;">{raw_text[600:]}</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 8) DEPARTMAN İÇERİKLERİ
# ============================================================
def render_active_department():
    dept = st.session_state.active_department
    if dept == "Otonom Ajan":
        render_search_bar()
        render_report()
    elif dept == "OCR Evrak Doğrulama":
        st.info("📄 OCR Evrak Doğrulama modülü — evrak yükleme alanı burada yapılandırılır.")
        st.file_uploader("Gümrük evrakını yükleyin", type=["pdf", "png", "jpg"])
    elif dept == "Gemi Röntgeni":
        st.info("⚓ Özel Gemi Röntgeni ($20) — canlı kargo haritası SADECE bu sekmede yüklenir.")
        st.warning("Folium haritası entegrasyonu bu sekmeye özel olarak eklenmelidir (ana sayfada değil).")


# ============================================================
# 9) SAYFA ÇIKTISI
# ============================================================
st.markdown("### 🛰️ INTERLOCK GLOBAL AI TERMINAL")
render_ticker_wall()
render_top_strip()
render_active_department()
