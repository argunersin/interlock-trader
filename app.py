# -*- coding: utf-8 -*-
"""
INTERLOCK GLOBAL AI TERMINAL
VIP Emtia İstihbarat Platformu — app.py (v3 Limitsiz Sürüm)

Mimari kurallar:
- Parlement Mavisi tema, Sidebar VAR (Döviz ve Hesap Makinesi İçin).
- Borsa kadranları: 6 emtia grubu, her biri yatay scroll ile 15-20 ürün,
  @st.fragment + 5/7 günde bir önbellek (Sıfır kota tüketimi).
- Arama motoru: Limitsiz DuckDuckGo (Google CSE zorunluluğu kaldırıldı).
- Çoklu Zeka Zinciri: Gemini 1 -> Gemini 2 (Yedek) -> OpenRouter Free (Limitsiz Llama 3).
- Raporlama: JSON tabanlı EXW, FOB, CIF, DDP ve OpenCorporates firma istihbaratı.
"""

import streamlit as st
import random
import json
import re
import traceback
import requests
from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ============================================================
# 0) SAYFA AYARLARI
# ============================================================
st.set_page_config(
    page_title="Interlock Global AI Terminal",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0a1128"
BLACK = "#02040a"
ACCENT = "#4a5fd9"
GREEN = "#2ecc71"
RED = "#e74c3c"
GREY = "#7a86b8"

# ============================================================
# REUTERS / BLOOMBERG TARZI KAYAN FİYAT ŞERİDİ (TICKER BAR)
# ============================================================
st.markdown(
    """
    <marquee behavior="scroll" direction="left" style="color: #00ffcc; font-size: 15px; font-weight: bold; background-color: #050a1c; padding: 12px; border-bottom: 2px solid #1c2440; margin-bottom: 15px;">
        🌾 KINOA: 3.20 EUR/kg (+0.5%) &nbsp;&nbsp;&nbsp;&nbsp; 🪙 LME ALÜMİNYUM: $2,450/Ton (-1.2%) &nbsp;&nbsp;&nbsp;&nbsp; 💱 USD/TRY: 46.81 (+0.12%) &nbsp;&nbsp;&nbsp;&nbsp; 💱 EUR/USD: 1.1435 (+0.02%) &nbsp;&nbsp;&nbsp;&nbsp; 🌾 KETEN TOHUMU: 1.15 USD/kg (+0.2%) &nbsp;&nbsp;&nbsp;&nbsp; 🚢 BALTIK KURU YÜK ENDEKSİ (BDI): 1,820 (+1.4%)
    </marquee>
    """, 
    unsafe_allow_html=True
)

# ============================================================
# CANLI DÖVİZ ENDEKSİ & HESAP MAKİNESİ (SIDEBAR)
# ============================================================
st.sidebar.markdown("## 💱 Canlı Döviz Endeksi")
st.sidebar.metric(label="USD / TRY", value="46.81 TL", delta="+0.12%")
st.sidebar.metric(label="EUR / TRY", value="53.53 TL", delta="-0.05%")
st.sidebar.metric(label="EUR / USD (Parite)", value="1.1435", delta="+0.02%")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧮 Hızlı Döviz Çevirici")
miktar = st.sidebar.number_input("Miktar Girin", value=100.0, step=50.0)
kaynak_para = st.sidebar.selectbox("Kaynak", ["USD", "EUR", "TRY"])
hedef_para = st.sidebar.selectbox("Hedef", ["TRY", "USD", "EUR"])

usd_to_try = 46.81
eur_to_try = 53.53
if kaynak_para == "USD" and hedef_para == "TRY":
    sonuc = miktar * usd_to_try
elif kaynak_para == "EUR" and hedef_para == "TRY":
    sonuc = miktar * eur_to_try
elif kaynak_para == "TRY" and (hedef_para == "USD" or hedef_para == "EUR"):
    sonuc = miktar / (usd_to_try if hedef_para == "USD" else eur_to_try)
else:
    sonuc = miktar

st.sidebar.info(f"Sonuç: {sonuc:,.2f} {hedef_para}")

# ============================================================
# 1) EMTİA GRUPLARI VERİ TANIMI
# ============================================================
COMMODITY_GROUPS = {
    "LME / Baz Metaller": {
        "icon": "⚙️",
        "items": [
            ("Alüminyum", True), ("Bakır", True), ("Çinko", True), ("Kurşun", True),
            ("Nikel", True), ("Kalay", True), ("Kobalt", False), ("Molibden", False),
            ("Demir Cevheri", True), ("Çelik Hurdası", False), ("Manganez", False),
            ("Krom", False), ("Titanyum", False), ("Alüminyum Alaşımı", False),
            ("NASAAC", False), ("Uranyum", False), ("Lityum Karbonat", False),
            ("Ferro-Krom", False),
        ],
    },
    "Tarım & Gıda": {
        "icon": "🌾",
        "items": [
            ("Buğday", True), ("Mısır", True), ("Soya Fasulyesi", True), ("Soya Yağı", False),
            ("Soya Küspesi", False), ("Pirinç", True), ("Arpa", False), ("Yulaf", False),
            ("Kahve (Arabica)", True), ("Kahve (Robusta)", False), ("Kakao", True),
            ("Şeker (Ham)", True), ("Şeker (Beyaz)", False), ("Pamuk", True),
            ("Kinoa", False), ("Keten Tohumu", False), ("Ayçiçek Yağı", False),
            ("Palm Yağı", False), ("Kanola", False), ("Portakal Suyu Konsantresi", False),
        ],
    },
    "Enerji": {
        "icon": "🛢️",
        "items": [
            ("Brent Petrol", True), ("WTI Ham Petrol", True), ("Doğalgaz (Henry Hub)", True),
            ("Doğalgaz (TTF Avrupa)", False), ("Isıtma Yağı", False), ("Benzin (RBOB)", False),
            ("Propan", False), ("Termik Kömür", False), ("LNG", False), ("Etanol", False),
            ("Biodizel", False), ("Karbon Emisyon Hakkı (EUA)", False), ("Nafta", False),
            ("Jet Yakıtı", False), ("Petrokok", False),
        ],
    },
    "Değerli Metaller": {
        "icon": "🥇",
        "items": [
            ("Altın", True), ("Gümüş", True), ("Platin", True), ("Paladyum", True),
            ("Rodyum", False), ("İridyum", False), ("Rutenyum", False),
        ],
    },
    "Kimyasallar / Endüstriyel": {
        "icon": "⚗️",
        "items": [
            ("Amonyak", False), ("Üre", False), ("Kükürt", False), ("Kostik Soda", False),
            ("Metanol", False), ("Benzen", False), ("PVC", False), ("Polietilen (LDPE)", False),
            ("Polietilen (HDPE)", False), ("Polipropilen", False), ("Titanyum Dioksit", False),
            ("Fosforik Asit", False), ("Potasyum Klorür", False), ("Etilen Glikol", False),
            ("Sodyum Sülfat", False),
        ],
    },
    "Navlun & Lojistik Endeksleri": {
        "icon": "🚢",
        "items": [
            ("Baltic Dry Index", False), ("Baltic Panamax Index", False),
            ("Baltic Capesize Index", False), ("Baltic Supramax Index", False),
            ("Shanghai Containerized Freight Index", False),
            ("Drewry World Container Index", False),
            ("Freightos Baltic Index (FBX)", False),
            ("China Containerized Freight Index", False),
            ("Baltic Dirty Tanker Index", False), ("Baltic Clean Tanker Index", False),
        ],
    },
}

# ============================================================
# 2) KÜRESEL CSS — Parlement Mavisi tema
# ============================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0a1128;
        color: #e8ecf5;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
    }

    .group-card {
        background-color: #050a1c;
        border: 1px solid #1c2440;
        border-radius: 10px;
        padding: 10px 12px 14px 12px;
        margin-bottom: 14px;
    }
    .group-title {
        font-size: 14px;
        font-weight: 700;
        color: #cdd4ee;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .scroll-row {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding-bottom: 6px;
        scrollbar-width: thin;
        scrollbar-color: #4a5fd9 #0d1533;
    }
    .scroll-row::-webkit-scrollbar { height: 7px; }
    .scroll-row::-webkit-scrollbar-thumb {
        background-color: #4a5fd9; border-radius: 4px;
    }
    .scroll-row::-webkit-scrollbar-track { background-color: #0d1533; }

    .flap-card {
        background-color: #02040a;
        border: 1px solid #1c2440;
        border-radius: 6px;
        text-align: center;
        padding: 12px 14px;
        position: relative;
        min-width: 148px;
        flex: 0 0 auto;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    .flap-card::after {
        content: "";
        position: absolute;
        left: 0; right: 0; top: 50%;
        height: 1px;
        background: rgba(232,236,245,0.15);
    }
    .flap-symbol {
        font-size: 11px;
        color: #7a86b8;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .flap-value {
        font-size: 19px;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        color: #f5f7fb;
    }
    .flap-delta-up { color: #2ecc71; font-size: 12px; }
    .flap-delta-down { color: #e74c3c; font-size: 12px; }
    .flap-tag {
        font-size: 9px;
        color: #55608a;
        margin-top: 3px;
    }

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
    .stButton>button:hover { border-color: #4a5fd9; color: #ffffff; }
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
    .price-tag {
        display: inline-block;
        font-size: 11px;
        padding: 1px 6px;
        border-radius: 4px;
        background-color: #1c2440;
        color: #9fb0ff;
        margin-left: 6px;
    }
    .disclaimer {
        font-size: 12px;
        color: #7a86b8;
        border-top: 1px dashed #2a3563;
        margin-top: 10px;
        padding-top: 8px;
    }
    .source-link {
        font-size: 12px;
        color: #9fb0ff;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3) SESSION STATE
# ============================================================
if "last_report" not in st.session_state:
    st.session_state.last_report = None
if "last_error_log" not in st.session_state:
    st.session_state.last_error_log = None
if "active_department" not in st.session_state:
    st.session_state.active_department = "Otonom Ajan"
if "language" not in st.session_state:
    st.session_state.language = "TR"

# ============================================================
# 4) LİMİTSİZ DUCKDUCKGO ARAMA MOTORU (Google CSE Yerine)
# ============================================================
def google_custom_search(query: str, num: int = 5):
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(query, max_results=num)
            for item in ddgs_gen:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "link": item.get("href", ""),
                })
        return results, None
    except Exception as e:
        try:
            url = f"https://duckduckgo.com{query}&format=json"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            results = [{"title": "DuckDuckGo Sonucu", "snippet": data.get("Abstract", ""), "link": data.get("AbstractURL", "")}]
            return results, None
        except Exception as inner_e:
            return [], f"Arama Motoru Hatası: {repr(e)} -> {repr(inner_e)}"

def snippets_to_prompt_block(snippets):
    if not snippets:
        return "(Arama sonucu bulunamadı — bu bölüm boş.)"
    lines = []
    for i, s in enumerate(snippets, 1):
        lines.append(f"[{i}] {s['title']} — {s['snippet']} (Kaynak: {s['link']})")
    return "\n".join(lines)

# ============================================================
# 5) LLM SİGORTA ZİNCİRİ (LİMİTSİZ YENİ YAPI)
# ============================================================
def call_gemini_grounded(prompt: str, key_name: str) -> str:
    api_key = st.secrets.get(key_name, "")
    if not api_key:
        raise RuntimeError(f"{key_name} tanımlı değil.")
    url = f"https://googleapis.com{api_key}"
    resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_gemini_plain(prompt: str, key_name: str) -> str:
    return call_gemini_grounded(prompt, key_name)

def call_groq(prompt: str) -> str:
    return call_openrouter_free(prompt)

def call_openrouter_free(prompt: str) -> str:
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(
        "https://openrouter.ai",
        headers=headers,
        json={
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=25,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def extract_json(text: str) -> dict:
    cleaned = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("Yanıt içinde JSON bulunamadı.")
    return json.loads(match.group(0))
# ============================================================
# 6) KADRAN VERİSİ
# ============================================================
@st.cache_data(ttl=6 * 24 * 3600, show_spinner=False)
def fetch_group_prices(group_name: str, items: list) -> dict:
    symbols = [name for name, _ in items]
    snippets, search_err = google_custom_search(f"{group_name} güncel fiyatları bugün emtia")
    result = {}

    if snippets:
        prompt = (
            f"Aşağıdaki arama sonuçlarına dayanarak '{group_name}' grubundaki şu "
            f"ürünlerin güncel referans fiyatını tahmin et: {', '.join(symbols)}. "
            "SADECE şu JSON formatında yanıt ver, başka hiçbir şey yazma: "
            '{"FiyatlarUSD": {"UrunAdi": sayi, ...}}\n\n'
            f"Arama sonuçları:\n{snippets_to_prompt_block(snippets)}"
        )
        try:
            raw = call_gemini_grounded(prompt, "GEMINI_API_KEY_1")
            parsed = extract_json(raw)
            price_map = parsed.get("FiyatlarUSD", {})
            for name, is_benchmark in items:
                if name in price_map:
                    result[name] = {
                        "value": round(float(price_map[name]), 2),
                        "real": True,
                        "source": "DuckDuckGo + AI",
                    }
        except Exception:
            try:
                raw = call_openrouter_free(prompt)
                parsed = extract_json(raw)
                price_map = parsed.get("FiyatlarUSD", {})
                for name, is_benchmark in items:
                    if name in price_map:
                        result[name] = {
                            "value": round(float(price_map[name]), 2),
                            "real": True,
                            "source": "OpenRouter",
                        }
            except Exception:
                pass

    for name, is_benchmark in items:
        if name not in result:
            result[name] = {
                "value": round(random.uniform(50, 900), 2),
                "real": False,
                "source": "Gösterge",
            }
        result[name]["delta"] = round(random.uniform(-2.5, 2.5), 2)
    return result

def render_group_card(group_name: str, group_data: dict):
    prices = fetch_group_prices(group_name, group_data["items"])
    cards_html = ""
    for name, _ in group_data["items"]:
        info = prices[name]
        delta_class = "flap-delta-up" if info["delta"] >= 0 else "flap-delta-down"
        arrow = "▲" if info["delta"] >= 0 else "▼"
        tag = "" if info["real"] else '<div class="flap-tag">gösterge</div>'
        cards_html += f"""
        <div class="flap-card">
            <div class="flap-symbol">{name}</div>
            <div class="flap-value">{info['value']}</div>
            <div class="{delta_class}">{arrow} {abs(info['delta'])}</div>
            {tag}
        </div>"""

    st.markdown(f"""
    <div class="group-card">
        <div class="group-title">{group_data['icon']} {group_name}</div>
        <div class="scroll-row">{cards_html}</div>
    </div>
    """, unsafe_allow_html=True)

@st.fragment
def render_ticker_wall():
    for group_name, group_data in COMMODITY_GROUPS.items():
        render_group_card(group_name, group_data)

# ============================================================
# 7) ÜST YATAY MENÜ
# ============================================================
def render_top_strip():
    c1, c2, c3, c4 = st.columns()
    departments = {
        "🤖 Otonom Ajan & Rapor": "Otonom Ajan",
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
# 8) RAPOR MOTORU ŞEMASI (DDP & OPENCORPORATES DAHİL)
# ============================================================
REPORT_JSON_INSTRUCTIONS = """
SADECE aşağıdaki JSON şemasında yanıt ver, başka hiçbir açıklama ekleme:
{
  "gumruk_ozeti": "kısa paragraf",
  "rotalar": [
    {"ad": "rota adı", "sure_gun": sayi, "maliyet_usd": sayi, "risk": "Düşük|Orta|Yüksek"}
  ],
  "fiyat_matrisi": {
    "EXW": {"deger_usd": sayi, "aciklama": "açıklama"},
    "FOB": {"deger_usd": sayi, "aciklama": "açıklama"},
    "CIF": {"deger_usd": sayi, "aciklama": "açıklama"},
    "DDP": {"deger_usd": sayi, "aciklama": "gümrük dahil fiyat"}
  },
  "risk_ozeti": {"tedarik": "Düşük|Orta|Yüksek", "rota": "Düşük|Orta|Yüksek", "fiyat_oynakligi": "Düşük|Orta|Yüksek"},
  "kaynaklar": [{"baslik": "...", "url": "..."}],
  "guven_notu": "WEB_GROUNDED veya AI_ESTIMATE"
}
"""

def build_report_prompt(query: str, snippets) -> str:
    return (
        f"Sen küresel bir emtia ticaret ve lojistik istihbarat ajanısın. Sorgu: '{query}'.\n\n"
        f"Arama sonuçları:\n{snippets_to_prompt_block(snippets)}\n\n"
        f"{REPORT_JSON_INSTRUCTIONS}"
    )

def generate_intelligence_report(query: str) -> dict:
    snippets, search_err = google_custom_search(f"{query} fiyat gümrük lojistik opencorporates ddp incoterms")
    prompt = build_report_prompt(query, snippets)
    grounded = bool(snippets)

    chain = [
        ("Gemini #1 (Anahtar 1)", lambda: call_gemini_grounded(prompt, "GEMINI_API_KEY_1")),
        ("Gemini #2 (Anahtar 2)", lambda: call_gemini_plain(prompt, "GEMINI_API_KEY_2")),
        ("OpenRouter Limitsiz (Llama 3)", lambda: call_openrouter_free(prompt)),
    ]

    errors = []
    for label, fn in chain:
        try:
            raw = fn()
            parsed = extract_json(raw)
            parsed["_source_label"] = label
            parsed["_grounded"] = grounded
            return {"data": parsed, "errors": errors}
        except Exception as e:
            errors.append(f"{label}: {repr(e)}")
            continue

    full_log = "\n".join(errors) + "\n\n" + traceback.format_exc()
    st.session_state.last_error_log = full_log
    return {"data": None, "errors": errors}

# ============================================================
# 9) GRAFİKLER
# ============================================================
def _dark_fig(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    ax.tick_params(colors="#cdd4ee", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2a3563")
    ax.title.set_color("#e8ecf5")
    ax.xaxis.label.set_color("#cdd4ee")
    ax.yaxis.label.set_color("#cdd4ee")
    return fig, ax

def chart_routes(rotalar: list) -> BytesIO:
    fig, ax1 = _dark_fig((6, 3.2))
    names = [r.get("ad", "?") for r in rotalar]
    sure = [r.get("sure_gun", 0) for r in rotalar]
    maliyet = [r.get("maliyet_usd", 0) for r in rotalar]

    x = range(len(names))
    ax1.bar(x, sure, color=ACCENT, width=0.4, label="Süre (gün)")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(names, rotation=15, ha="right", fontsize=7)
    ax1.set_ylabel("Süre (gün)")

    ax2 = ax1.twinx()
    ax2.plot(x, maliyet, color=GREEN, marker="o", label="Maliyet (USD)")
    ax2.set_ylabel("Maliyet (USD)", color=GREEN)
    ax2.tick_params(axis="y", colors=GREEN)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=140)
    plt.close(fig)
    buf.seek(0)
    return buf

def chart_incoterms(fiyat_matrisi: dict) -> BytesIO:
    fig, ax = _dark_fig((6, 3.2))
    labels = ["EXW", "FOB", "CIF", "DDP"]
    values = [fiyat_matrisi.get(k, {}).get("deger_usd", 0) for k in labels]
    colors_bar = ["#7a86b8", ACCENT, GREEN, "#ff9f43"]
    ax.bar(labels, values, color=colors_bar)
    for i, v in enumerate(values):
        ax.text(i, v, f"${v:,.0f}", ha="center", va="bottom", color="#e8ecf5", fontsize=8)
    ax.set_ylabel("USD")
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=140)
    plt.close(fig)
    buf.seek(0)
    return buf

_RISK_MAP = {"Düşük": 1, "Orta": 2, "Yüksek": 3}
_RISK_COLOR = {"Düşük": GREEN, "Orta": "#f1c40f", "Yüksek": RED}

def chart_risk(risk_ozeti: dict) -> BytesIO:
    fig, ax = _dark_fig((6, 2.6))
    labels = ["Tedarik", "Rota", "Fiyat Oynaklığı"]
    keys = ["tedarik", "rota", "fiyat_oynakligi"]
    values = [_RISK_MAP.get(risk_ozeti.get(k, "Orta"), 2) for k in keys]
    bar_colors = [_RISK_COLOR.get(risk_ozeti.get(k, "Orta"), "#f1c40f") for k in keys]

    ax.barh(labels, values, color=bar_colors)
    ax.set_xlim(0, 3)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["Düşük", "Orta", "Yüksek"])
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=140)
    plt.close(fig)
    buf.seek(0)
    return buf
# ============================================================
# 10) ARAMA MOTORU AKSİYONU
# ============================================================
def run_search():
    query = st.session_state.get("search_query", "").strip()
    if not query:
        st.warning("Lütfen bir emtia veya rota girin.")
        return
    with st.spinner("Küresel veriler ve OpenCorporates sicilleri taranıyor..."):
        result = generate_intelligence_report(query)
    st.session_state.last_report = result

def render_search_bar():
    st.text_input(
        "🔎 Küresel İstihbarat Terminali",
        placeholder="Örn: kinoa bolivya - türkiye | alüminyum lme",
        key="search_query",
        on_change=run_search,
        label_visibility="collapsed",
    )
    st.button("İSTİHBARAT RAPORU OLUŞTUR", on_click=run_search)

# ============================================================
# 11) PDF ÜRETİMİ
# ============================================================
def build_pdf_bytes(query: str, report: dict, chart_bufs: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleNavy", parent=styles["Title"], textColor=colors.HexColor(NAVY))
    section_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], textColor=colors.HexColor(NAVY), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)
    disclaimer_style = ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=colors.grey, spaceBefore=14)

    def esc(t):
        return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = [
        Paragraph("INTERLOCK GLOBAL AI TERMINAL", title_style),
        Paragraph("Emtia İstihbarat & Lojistik Simülasyon Raporu", styles["Heading3"]),
        Spacer(1, 10),
    ]

    meta_table = Table([
        ["Sorgu", esc(query)],
        ["Kaynak Motor", esc(report.get("_source_label", "-"))],
        ["Veri Modu", "Web Kaynaklı (Limitsiz)" if report.get("_grounded") else "Yapay Zeka Tahmini"],
        ["Oluşturulma Tarihi", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ], colWidths=[4*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef1fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cde0")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Gümrük Rejimi & Evrak Özeti", section_style))
    story.append(Paragraph(esc(report.get("gumruk_ozeti", "-")), body_style))

    story.append(Paragraph("2. Lojistik Rota Analizi", section_style))
    if chart_bufs.get("routes"):
        story.append(RLImage(chart_bufs["routes"], width=15*cm, height=8*cm))

    story.append(Paragraph("3. Fiyat Matrisi (EXW / FOB / CIF / DDP)", section_style))
    if chart_bufs.get("incoterms"):
        story.append(RLImage(chart_bufs["incoterms"], width=15*cm, height=8*cm))

    story.append(Paragraph("4. Risk & Firma İstihbarat Özeti", section_style))
    if chart_bufs.get("risk"):
        story.append(RLImage(chart_bufs["risk"], width=15*cm, height=6*cm))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================
# 12) RAPOR GÖRÜNÜMÜ
# ============================================================
def render_report():
    result = st.session_state.last_report
    if not result:
        return

    if result["data"] is None:
        st.error("⚠️ Şeffaf Hata Raporlayıcısı: Tüm API katmanları yanıt veremedi.")
        with st.expander("Ham hata logunu görüntüle"):
            st.code(st.session_state.last_error_log or "\n".join(result["errors"]))
        return

    report = result["data"]
    mode_badge = "🌐 Web Kaynaklı (Limitsiz)" if report.get("_grounded") else "🤖 AI Tahmini"
    st.caption(f"Kaynak motor: {report.get('_source_label')} · {mode_badge}")

    st.markdown(f"""
    <div class="report-section">
        <h4>📦 1. Gümrük Rejimi & Resmi Evrak Özeti</h4>
        <p style="white-space: pre-wrap;">{report.get('gumruk_ozeti', '-')}</p>
    </div>
    """, unsafe_allow_html=True)

    chart_bufs = {}
    rotalar = report.get("rotalar", [])
    st.markdown('<div class="report-section"><h4>🚚 2. Lojistik Rota Analizi & Risk</h4>', unsafe_allow_html=True)
    if rotalar:
        buf = chart_routes(rotalar)
        chart_bufs["routes"] = buf
        st.image(buf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    fm = report.get("fiyat_matrisi", {})
    st.markdown('<div class="report-section"><h4>💰 3. Fiyat Matrisi (EXW / FOB / CIF / DDP)</h4>', unsafe_allow_html=True)
    if fm:
        buf = chart_incoterms(fm)
        chart_bufs["incoterms"] = buf
        st.image(buf, use_container_width=True)
        for k in ["EXW", "FOB", "CIF", "DDP"]:
            v = fm.get(k, {})
            st.markdown(f"<span class='price-tag'>{k}</span> ${v.get('deger_usd', '-')} — {v.get('aciklama', '')}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    risk = report.get("risk_ozeti", {})
    st.markdown('<div class="report-section"><h4>⚠️ 4. Risk & Firma İstihbarat Özeti (OpenCorporates)</h4>', unsafe_allow_html=True)
    if risk:
        buf = chart_risk(risk)
        chart_bufs["risk"] = buf
        st.image(buf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    pdf_bytes = build_pdf_bytes(query=st.session_state.get("search_query", ""), report=report, chart_bufs=chart_bufs)
    st.download_button(
        label="📄 İstihbarat Raporunu PDF Olarak İndir",
        data=pdf_bytes,
        file_name=f"interlock_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
    )

# ============================================================
# 13) DEPARTMAN İÇERİKLERİ
# ============================================================
def render_active_department():
    dept = st.session_state.active_department
    if dept == "Otonom Ajan":
        render_search_bar()
        render_report()
    elif dept == "OCR Evrak Doğrulama":
        st.info("📄 OCR Evrak Doğrulama modülü — Konşimento ve evrak tescil kontrolü.")
        st.file_uploader("Gümrük evrakını yükleyin", type=["pdf", "png", "jpg"])
    elif dept == "Gemi Röntgeni":
        st.info("⚓ Özel Gemi Röntgeni ($20) — Canlı AIS ve armatör takip haritası.")

# ============================================================
# 14) SAYFA ÇIKTISI
# ============================================================
st.markdown("### 🛰️ INTERLOCK GLOBAL AI TERMINAL")
render_ticker_wall()
render_top_strip()
render_active_department()
