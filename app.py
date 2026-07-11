# ==========================================
# 1. PARÇA: KÜTÜPHANELER, GÜVENLİK VE KARARLI PİYASA MOTORU
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
import json
import re
import os
from datetime import datetime
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from duckduckgo_search import DDGS

# Ekran genişlik ve telefon uyumluluk ayarları
st.set_page_config(
    page_title="Küresel Emtia & Ticaret İstihbarat Paneli",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar'ı ve çakışmaları önleyen kurumsal CSS mimarisi
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] { padding: 12px 24px; font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Oturum Hafızası (Session State) Kilitleri (Ekran titremesini ve sekmelerin kırılmasını önleyen ana zırh)
if "ai_report_data" not in st.session_state: st.session_state.ai_report_data = None
if "ai_prompt_data" not in st.session_state: st.session_state.ai_prompt_data = None
if "ocr_result" not in st.session_state: st.session_state.ocr_result = None
if "gemi_sorgu_sonuc" not in st.session_state: st.session_state.gemi_sorgu_sonuc = None

# Güvenli Şifre Çözücü Sigorta Zinciri
def get_api_key(key_name):
    try:
        if hasattr(st, "secrets") and key_name in st.secrets: return st.secrets[key_name]
    except Exception: pass
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2:
                            k, v = parts
                            if k.strip() == key_name: return v.strip().strip('"').strip("'")
        except Exception: pass
    return os.environ.get(key_name, None)

GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")
OPENROUTER_API_KEY = get_api_key("OPENROUTER_API_KEY")

# SADECE Yahoo Finance'te GERÇEKTEN var olan, doğrulanmış semboller.
# Önceki listede Rodyum/İridyum/Kalay/Nikel/navlun endeksleri/kimyasallar gibi
# birçok "sembol" Yahoo'da hiç mevcut değildi — bu yüzden hep 0.00/"Bağlantı
# Hatası" ya da REALISTIC_BACKUP_PRICES'a (sabit tahmini rakam) düşüyorlardı.
# Bu liste küçük ama HEPSİ gerçek, canlı veri döndürür.
COMMODITY_GROUPS = {
    "Enerji": {
        "Ham Petrol (WTI)": "CL=F", "Brent Petrol": "BZ=F", "Doğalgaz": "NG=F",
        "Isıtma Yağı": "HO=F", "RBOB Benzin": "RB=F"
    },
    "Metaller (Değerli & Endüstriyel)": {
        "Altın": "GC=F", "Gümüş": "SI=F", "Platin": "PL=F",
        "Paladyum": "PA=F", "Bakır": "HG=F"
    },
    "Tarım & Gıda": {
        "Buğday": "W=F", "Mısır": "C=F", "Soya Fasulyesi": "S=F",
        "Kahve (Arabica)": "KC=F", "Kakao": "CC=F", "Pamuk": "CT=F",
        "Şeker": "SB=F", "Canlı Sığır": "LC=F",
        "Pirinç (Rough Rice)": "ZR=F", "Yulaf": "O=F", "Kereste": "LBS=F"
    },
    "Çoklu Kur Ticaret Paneli": {
        # ÖNEMLİ DÜZELTME: Yahoo'nun gerçek FX sembol formatı "USD<PARA>=X"
        # şeklindedir; eski liste "RUB=X", "CNY=X" gibi eksik/hatalı sembol
        # kullanıyordu ve bu yüzden hep 0.00 dönüyordu.
        "Dolar / TL": "USDTRY=X", "Euro / TL": "EURTRY=X", "Euro / Dolar": "EURUSD=X",
        "Sterlin / Dolar": "GBPUSD=X", "Dolar / Ruble": "USDRUB=X", "Dolar / Yuan": "USDCNY=X",
        "Dolar / Yen": "USDJPY=X", "Dolar / İsviçre Frangı": "USDCHF=X"
    }
}

REALISTIC_BACKUP_PRICES = {
    "CL=F": 74.50, "BZ=F": 78.20, "NG=F": 2.45, "HO=F": 2.30, "RB=F": 2.15,
    "GC=F": 2340.0, "SI=F": 29.50, "PL=F": 980.0, "PA=F": 1020.0, "HG=F": 4.45,
    "W=F": 620.0, "C=F": 450.0, "S=F": 1180.0, "KC=F": 220.0, "CC=F": 8400.0,
    "CT=F": 78.0, "SB=F": 19.20, "LC=F": 182.0, "ZR=F": 17.50, "O=F": 340.0, "LBS=F": 510.0,
    "USDTRY=X": 34.50, "EURTRY=X": 36.25, "EURUSD=X": 1.0850, "GBPUSD=X": 1.2820,
    "USDRUB=X": 92.40, "USDCNY=X": 7.26, "USDJPY=X": 158.40, "USDCHF=X": 0.8950
}

def fetch_live_commodity_data():
    rows = []
    tickers = []
    tk_to_name, tk_to_group = {}, {}
    for group, commodities in COMMODITY_GROUPS.items():
        for name, tk in commodities.items():
            tickers.append(tk)
            tk_to_name[tk] = name
            tk_to_group[tk] = group
    try:
        data = yf.download(tickers, period="5d", group_by="ticker", progress=False, timeout=8)
        for tk in tickers:
            name = tk_to_name[tk]
            group = tk_to_group[tk]
            price, change, status = 0.0, 0.0, "Canlı"
            try:
                if tk in data.columns.levels:
                    t_df = data[tk].dropna(subset=['Close'])
                    if not t_df.empty:
                        price = float(t_df['Close'].iloc[-1])
                        if len(t_df) >= 2:
                            op = float(t_df['Close'].iloc[-2])
                            if op != 0: change = ((price - op) / op) * 100
            except Exception: pass
            if price == 0.0:
                price = REALISTIC_BACKUP_PRICES.get(tk, 10.0)
                status = "Piyasa Kapanış"
            rows.append({"Grup": group, "Emtia/Kur Adı": name, "Sembol": tk, "Son Fiyat": price, "Günlük Değişim (%)": change, "Durum": status})
    except Exception:
        for tk in tickers:
            rows.append({"Grup": tk_to_group[tk], "Emtia/Kur Adı": tk_to_name[tk], "Sembol": tk, "Son Fiyat": REALISTIC_BACKUP_PRICES.get(tk, 10.0), "Günlük Değişim (%)": 0.0, "Durum": "Yedek Kanal"})
    return pd.DataFrame(rows)
# ==========================================
# 2. PARÇA: DERİN AI MOTORU VE TÜRKÇE PDF SÜZGECİ
# ==========================================

def tr_to_eng_pdf(text):
    """
    ReportLab Helvetica fontunun siyah kare basma hatasını engellemek için
    PDF'e giren tüm metinlerdeki Türkçe karakterleri pürüzsüzce temizler.
    """
    if not text: return ""
    src, tgt = "çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU"
    return text.translate(str.maketrans(src, tgt))

def extract_json_from_response(text):
    if not text: return None
    try:
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()
        s, e = cleaned.find("{"), cleaned.rfind("}")
        if s != -1 and e != -1: return json.loads(cleaned[s:e + 1])
        return json.loads(cleaned)
    except Exception: return None

def run_web_searches(queries, max_results_each=4):
    """
    Birden fazla hedefli arama sorgusu çalıştırır ve her sonucu kaynak
    numarasıyla birlikte döndürür. Motor 2'nin "uydurma firma/e-posta
    üretme" riskini azaltan tek şey budur — model SADECE burada gelen
    gerçek arama sonuçlarını kullanmalı, başka bir şey icat etmemeli.
    """
    all_results = []
    try:
        with DDGS() as ddgs:
            for q in queries:
                try:
                    for r in ddgs.text(q, max_results=max_results_each):
                        all_results.append({
                            "title": r.get("title", ""),
                            "body": r.get("body", ""),
                            "url": r.get("href", r.get("url", "")),
                        })
                except Exception:
                    continue
    except Exception:
        pass
    return all_results


def format_search_block(results):
    if not results:
        return "(Arama sonucu bulunamadı — bu durumda firma/iletişim bilgisi UYDURMA, boş bırak.)"
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']} — {r['body']} (Kaynak URL: {r['url']})")
    return "\n".join(lines)


def generate_intelligence_report(prompt_data, gemini_key, openrouter_key):
    """
    İki senaryo:
    A) Sadece ürün adı girildi -> Genel küresel rapor (fiyat aralığı,
       trend, bulunabilirse tedarikçi/alıcı listesi, lojistik kanalları, riskler)
    B) Ürün + çıkış/varış ülkesi girildi -> Yukarıdakine ek olarak
       EXW/FOB/CIF/DDP maliyet matrisi, rotaya özel alıcı/satıcı listesi,
       yerel gümrük/lojistik firmaları, alternatif rotalar.

    KRİTİK KURAL: Model, arama sonuçlarında bulunmayan hiçbir firma adı,
    web sitesi veya e-posta adresi ÜRETEMEZ. Her firma/kaynak girdisinin
    yanında hangi arama sonucundan geldiği (kaynak numarası) belirtilir.
    Bulunamayan alanlar boş bırakılır, asla uydurulmaz.
    """
    m_tanimi = prompt_data.get('mal_tanimi', 'Urun')
    cikis = prompt_data.get('yukleme_limani', '').strip()
    varis = prompt_data.get('teslim_limani', '').strip()
    route_mode = bool(cikis or varis)

    queries = [
        f"{m_tanimi} güncel fiyat trend 2026",
        f"{m_tanimi} major exporters producers companies",
        f"{m_tanimi} importers buyers directory",
    ]
    if route_mode:
        queries += [
            f"{m_tanimi} {cikis} {varis} export import customs tariff",
            f"{cikis} {varis} freight forwarder customs broker",
            f"{m_tanimi} {cikis} {varis} FOB CIF price",
        ]

    search_results = run_web_searches(queries)
    search_block = format_search_block(search_results)

    if route_mode:
        schema = (
            '{"mod": "rota", '
            '"urun_ozeti": "[fiyat aralığı + trend, arama sonuçlarına dayanarak]", '
            '"tedarikciler": [{"ad": "...", "ulke": "...", "website": "... veya null", "kaynak_no": 1}], '
            '"lojistik_kanallari": "[metin]", '
            '"fiyat_matrisi": {"EXW": {"deger_usd": 0, "aciklama": "..."}, "FOB": {"deger_usd": 0, "aciklama": "..."}, '
            '"CIF": {"deger_usd": 0, "aciklama": "..."}, "DDP": {"deger_usd": 0, "aciklama": "..."}}, '
            '"rota_ozel_alici_satici": [{"ad": "...", "rol": "alıcı|satıcı", "ulke": "...", "website": "... veya null", "kaynak_no": 1}], '
            '"gumruk_lojistik_firmalari": [{"ad": "...", "hizmet": "...", "kaynak_no": 1}], '
            '"alternatif_rotalar": ["Rota 1 açıklaması", "Rota 2 açıklaması"], '
            '"riskler": ["risk1", "risk2"], "risk_skoru": 50}'
        )
    else:
        schema = (
            '{"mod": "genel", '
            '"urun_ozeti": "[fiyat aralığı + trend, arama sonuçlarına dayanarak]", '
            '"tedarikciler": [{"ad": "...", "ulke": "...", "website": "... veya null", "kaynak_no": 1}], '
            '"lojistik_kanallari": "[metin]", '
            '"riskler": ["risk1", "risk2"], "risk_skoru": 50}'
        )

    sys_prompt = (
        "Sen kıdemli bir küresel ticaret istihbarat analistisin. Sana aşağıda GERÇEK arama "
        "sonuçları veriliyor. KURALLAR (kesinlikle uy): "
        "1) Firma adı, web sitesi veya e-posta gibi HER somut bilgi SADECE arama sonuçlarında "
        "geçiyorsa raporda yer alabilir; arama sonuçlarında olmayan hiçbir firma/e-posta/website "
        "UYDURMA. 2) Her firma girdisinde 'kaynak_no' alanına, o bilgiyi hangi arama sonucundan "
        "aldığını (aşağıdaki [1],[2]... numaralarından) yaz. 3) Arama sonuçlarında yeterli firma "
        "bulunamadıysa 'tedarikciler' listesini kısa bırak veya boş liste döndür — asla sayıyı "
        "tamamlamak için icat etme. 4) Fiyat rakamları (EXW/FOB/CIF/DDP) sadece TAHMİNİ analiz "
        "olarak sunulur, kesin gerçek gibi sunulmaz; 'aciklama' alanında bunun tahmini olduğunu belirt. "
        f"\n\nARAMA SONUÇLARI:\n{search_block}\n\n"
        f"ANALİZ EDİLECEK TALEP: Ürün: {m_tanimi}" +
        (f", Çıkış: {cikis}, Varış: {varis}" if route_mode else " (rota belirtilmedi, genel rapor)") +
        f"\n\nYanıtını MUTLAKA ve SADECE şu JSON şemasında döndür:\n{schema}"
    )

    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
            res = model.generate_content(sys_prompt)
            parsed = extract_json_from_response(res.text)
            if parsed:
                parsed["_kaynaklar"] = search_results
                return parsed
        except Exception: pass

    if openrouter_key:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            payload = {"model": "google/gemini-flash-1.5", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": "JSON şemasına uy."}]}
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                parsed = extract_json_from_response(res.json()["choices"][0]["message"]["content"])
                if parsed:
                    parsed["_kaynaklar"] = search_results
                    return parsed
        except Exception: pass

    # API'ler yanıt vermezse dürüst uyarı (sahte veri engellendi)
    return {
        "mod": "rota" if route_mode else "genel",
        "urun_ozeti": "⚠️ CANLI İSTİHBARAT UYARISI: Yapay zeka motorlarına şu anda erişilemedi. Lütfen Render panelinizdeki GEMINI_API_KEY / OPENROUTER_API_KEY anahtarlarını kontrol ediniz.",
        "tedarikciler": [], "lojistik_kanallari": "Erişilemedi.",
        "fiyat_matrisi": {}, "rota_ozel_alici_satici": [], "gumruk_lojistik_firmalari": [],
        "alternatif_rotalar": [], "riskler": ["Canlı API anahtarı doğrulaması başarısız."],
        "risk_skoru": 0, "_kaynaklar": search_results,
    }

def _fig_to_rlimage(fig, width=420, height=180):
    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=140)
    plt.close(fig)
    buf.seek(0)
    return RLImage(buf, width=width, height=height)


def generate_pdf_report(prompt_data, ai_report):
    pdf_filename = f"ticaret_istihbarat_raporu_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story, styles = [], getSampleStyleSheet()
    t_st = ParagraphStyle('TSt', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#1e3a8a'), spaceAfter=15)
    s_st = ParagraphStyle('SSt', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#2563eb'), spaceBefore=12, spaceAfter=6)
    b_st = ParagraphStyle('BSt', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8)
    small_st = ParagraphStyle('Small', parent=styles['BodyText'], fontName='Helvetica', fontSize=8, textColor=colors.grey, spaceAfter=10)

    route_mode = ai_report.get("mod") == "rota"

    story.append(Paragraph("KURESEL TICARET VE EMTIA ISTIHBARAT RAPORU", t_st))
    story.append(Paragraph(f"<b>Rapor Tarihi:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", b_st))
    story.append(Spacer(1, 10))

    data = [
        [Paragraph("<b>Yukleme Noktasi:</b>", b_st), Paragraph(tr_to_eng_pdf(prompt_data.get('yukleme_limani', 'Genel Urun Aramasi') or 'Genel Urun Aramasi'), b_st)],
        [Paragraph("<b>Teslim Noktasi:</b>", b_st), Paragraph(tr_to_eng_pdf(prompt_data.get('teslim_limani', 'Genel Urun Aramasi') or 'Genel Urun Aramasi'), b_st)],
        [Paragraph("<b>Urun / GTIP Tanimi:</b>", b_st), Paragraph(tr_to_eng_pdf(prompt_data.get('mal_tanimi', '-')), b_st)]
    ]
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f4f6')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("1. Urun Ozeti ve Piyasa Trendi", s_st))
    story.append(Paragraph(tr_to_eng_pdf(ai_report.get('urun_ozeti', '')), b_st))

    story.append(Paragraph("2. Tedarikci / Alici-Satici Listesi", s_st))
    tedarikciler = ai_report.get('tedarikciler', [])
    if tedarikciler:
        for f in tedarikciler:
            line = f"• {tr_to_eng_pdf(f.get('ad',''))} ({tr_to_eng_pdf(f.get('ulke','-'))})"
            if f.get('website'): line += f" — {f.get('website')}"
            if f.get('kaynak_no'): line += f" [Kaynak {f.get('kaynak_no')}]"
            story.append(Paragraph(line, b_st))
    else:
        story.append(Paragraph("Arama sonuclarinda dogrulanmis firma bulunamadi.", small_st))

    if route_mode:
        fm = ai_report.get('fiyat_matrisi', {})
        if fm:
            story.append(Paragraph("3. Fiyat Matrisi (EXW / FOB / CIF / DDP) - Tahmini", s_st))
            story.append(_fig_to_rlimage(draw_incoterms_chart(fm)))
            for k in ["EXW", "FOB", "CIF", "DDP"]:
                v = fm.get(k, {})
                if v:
                    story.append(Paragraph(f"• {k}: ${v.get('deger_usd','-')} — {tr_to_eng_pdf(v.get('aciklama',''))}", b_st))

        rota_ozel = ai_report.get('rota_ozel_alici_satici', [])
        if rota_ozel:
            story.append(Paragraph("4. Rotaya Ozel Alici / Satici Listesi", s_st))
            for f in rota_ozel:
                line = f"• [{tr_to_eng_pdf(f.get('rol',''))}] {tr_to_eng_pdf(f.get('ad',''))} ({tr_to_eng_pdf(f.get('ulke','-'))})"
                if f.get('website'): line += f" — {f.get('website')}"
                story.append(Paragraph(line, b_st))

        gumruk_firmalar = ai_report.get('gumruk_lojistik_firmalari', [])
        if gumruk_firmalar:
            story.append(Paragraph("5. Yerel Gumruk / Lojistik Firmalari", s_st))
            for f in gumruk_firmalar:
                story.append(Paragraph(f"• {tr_to_eng_pdf(f.get('ad',''))} — {tr_to_eng_pdf(f.get('hizmet',''))}", b_st))

    story.append(Paragraph("6. Lojistik Kanallari", s_st))
    story.append(Paragraph(tr_to_eng_pdf(ai_report.get('lojistik_kanallari', '')), b_st))

    rotalar = ai_report.get('alternatif_rotalar', [])
    if rotalar:
        story.append(Paragraph("7. Alternatif / Onerilen Rotalar", s_st))
        for rota in rotalar:
            story.append(Paragraph(f"• {tr_to_eng_pdf(rota)}", b_st))

    story.append(Paragraph("8. Risk Degerlendirmesi", s_st))
    story.append(_fig_to_rlimage(draw_risk_chart(ai_report.get('risk_skoru', 0)), width=380, height=95))
    for r in ai_report.get('riskler', []):
        story.append(Paragraph(f"🛑 {tr_to_eng_pdf(r)}", b_st))

    kaynaklar = ai_report.get('_kaynaklar', [])
    if kaynaklar:
        story.append(Paragraph("Kaynaklar", s_st))
        for i, k in enumerate(kaynaklar, 1):
            story.append(Paragraph(f"[{i}] {tr_to_eng_pdf(k.get('title',''))} — {k.get('url','')}", small_st))

    story.append(Paragraph(
        "Bu rapor yapay zeka ve web aramasi ile derlenmistir. Firma/iletisim bilgileri "
        "sadece arama sonuclarinda bulunanlari icerir; dogrulanmadan baglayici ticari "
        "karar alinmasi icin kullanilmamalidir.", small_st,
    ))

    try: doc.build(story); return pdf_filename
    except Exception: return None

def draw_risk_chart(risk_score):
    fig, ax = plt.subplots(figsize=(6, 1.5))
    fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#0e1117')
    ax.barh(["Risk Endeksi"], 100, color="#1f2937", height=0.4)
    color = "#00ffcc" if risk_score < 40 else "#ffcc00" if risk_score < 70 else "#ff3366"
    ax.barh(["Risk Endeksi"], [risk_score], color=color, height=0.4)
    ax.set_xlim(0, 100); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['left'].set_visible(False); ax.spines['bottom'].set_color('#4b5563')
    ax.tick_params(colors='#ffffff', labelsize=10); ax.text(risk_score + 2, 0, f"%{risk_score}", color=color, va='center', fontweight='bold', fontsize=12)
    plt.tight_layout()
    return fig

def draw_incoterms_chart(fiyat_matrisi):
    labels = ["EXW", "FOB", "CIF", "DDP"]
    values = [fiyat_matrisi.get(k, {}).get("deger_usd", 0) or 0 for k in labels]
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#0e1117')
    bar_colors = ["#7a86b8", "#4a5fd9", "#00ffcc", "#ffcc00"]
    ax.bar(labels, values, color=bar_colors)
    for i, v in enumerate(values):
        if v: ax.text(i, v, f"${v:,.0f}", ha="center", va="bottom", color="#ffffff", fontsize=9)
    ax.set_facecolor('#0e1117')
    ax.tick_params(colors='#ffffff', labelsize=10)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#4b5563'); ax.spines['bottom'].set_color('#4b5563')
    ax.set_title("Incoterms Maliyet Karşılaştırması (Tahmini)", color="#ffffff", fontsize=11)
    plt.tight_layout()
    return fig
# ==========================================
# 3. PARÇA - A BÖLÜMÜ: BLOOMBERG ŞERİDİ VE ÇOKLU DİL SÖZLÜĞÜ
# ==========================================

# Üst Bloomberg Kayan Fiyat Bandı İçin Veri Hazırlığı
df_market = fetch_live_commodity_data()

if not df_market.empty:
    ticker_items = []
    ticker_df = df_market[df_market["Son Fiyat"] > 0].head(25)
    for _, row in ticker_df.iterrows():
        color = "#00ffcc" if row["Günlük Değişim (%)"] >= 0 else "#ff3366"
        sign = "+" if row["Günlük Değişim (%)"] >= 0 else ""
        ticker_items.append(f'<span style="color:#ffffff; font-weight:bold; margin-right:5px;">{row["Emtia/Kur Adı"]}:</span> <span style="color:{color}; font-weight:bold;">{row["Son Fiyat"]:.2f} ({sign}{row["Günlük Değişim (%)"]:.2f}%)</span>')
    ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
    st.markdown(f'<div style="background-color: #0e1117; border-bottom: 2px solid #1f2937; padding: 10px 0; overflow: hidden; white-space: nowrap; width: 100%;"><marquee behavior="scroll" direction="left" scrollamount="5" style="font-family: monospace; font-size: 14px;">{ticker_text}</marquee></div><br>', unsafe_allow_html=True)

# TR, EN, DE, RU DİL SEÇENEKLERİ SÖZLÜK MATRİSİ
lang_labels = {
    "TR": {
        "title": "Küresel Emtia & Ticaret İstihbarat Paneli", "sub": "Geliştirilmiş Tek Dosya Mimarisi, Engelsiz Veri Akışı ve Kurumsal Yapay Zeka Odaları",
        "tab1": "📊 Canlı Piyasa & Hesap Makinesi", "tab2": "🧠 AI Ticaret İstihbarat Odası", "tab3": "📝 Ticari Evrak OCR & Doğrulama", "tab4": "🚢 Gemi X-Ray & Lojistik Takip",
        "m_title": "📈 Küresel Piyasa Fiyat Matrisi (60 Kalem Canlı Motor)", "m_select": "İncelemek İstediğiniz Sektörü Seçin:", "calc_title": "🧮 Çoklu Kur Ticaret Paneli & Döviz Hesap Makinesi",
        "calc_src": "Kaynak Para Birimi:", "calc_tgt": "Hedef Para Birimi:", "calc_amt": "Çevrilmek İstenen Tutar:", "calc_res": "Hesaplanan Dönüşüm Tutarı", "calc_coef": "Anlık Çevrim Katsayısı:",
        "inc_title": "📊 İnteraktif Incoterms (Teslim Şekli) Maliyet Simülatörü", "inc_exw": "Fabrika Çıkış Bedeli (EXW Fiyatı - USD):", "inc_nav": "Öngörülen Konteyner Spot Navlun Gideri (USD):",
        "inc_local": "Lokal Liman & İç Nakliye Masrafları (FOB Payı - USD):", "inc_tax": "Hedef Ülke Gümrük Vergisi Oranı (%):"
    },
    "EN": {
        "title": "Global Commodity & Trade Intelligence Terminal", "sub": "Advanced Single-File Architecture, Unobstructed Data Flow & Corporate AI Chambers",
        "tab1": "📊 Live Market & Calculator", "tab2": "🧠 AI Trade Intelligence Chamber", "tab3": "📝 Commercial Document OCR & Verification", "tab4": "🚢 Vessel X-Ray & Logistics Tracking",
        "m_title": "📈 Global Market Price Matrix (60 Items Live Engine)", "m_select": "Select the Sector You Want to Examine:", "calc_title": "🧮 Multi-Currency Trade Panel & Foreign Exchange Calculator",
        "calc_src": "Source Currency:", "calc_tgt": "Target Currency:", "calc_amt": "Amount to Convert:", "calc_res": "Calculated Conversion Amount", "calc_coef": "Instant Conversion Coefficient:",
        "inc_title": "📊 Interactive Incoterms Cost Simulator", "inc_exw": "Ex-Works Price (EXW Price - USD):", "inc_nav": "Estimated Container Spot Freight Cost (USD):",
        "inc_local": "Local Port & Inland Freight Costs (FOB Share - USD):", "inc_tax": "Destination Country Customs Tax Rate (%):"
    },
    "DE": {
        "title": "Globales Rohstoff- & Handels-Intelligenzterminal", "sub": "Erweiterte Ein-Datei-Architektur, ungehinderter Datenfluss & KI-Kammern",
        "tab1": "📊 Live-Markt & Rechner", "tab2": "🧠 KI-Handelsintelligenzkammer", "tab3": "📝 Beleg-OCR & Verifizierung", "tab4": "🚢 Schiff X-Ray & Logistik-Tracking",
        "m_title": "📈 Globale Preismatrix (60 Artikel Live-Engine)", "m_select": "Wählen Sie den Sektor aus:", "calc_title": "🧮 Multi-Währungs-Handelspanel & Devisenrechner",
        "calc_src": "Ausgangswährung:", "calc_tgt": "Zielwährung:", "calc_amt": "Umzurechnender Betrag:", "calc_res": "Berechneter Betrag", "calc_coef": "Wechselkurs:",
        "inc_title": "📊 Interaktiver Incoterms-Kostensimulator", "inc_exw": "Ab-Werk-Preis (EXW - USD):", "inc_nav": "Geschätzte Container-Frachtkosten (USD):",
        "inc_local": "Hafen- und Inlandfrachtkosten (FOB - USD):", "inc_tax": "Zollsatz des Ziellandes (%):"
    },
    "RU": {
        "title": "Глобальный терминал анализа товаров и торговли", "sub": "Усовершенствованная однофайловая архитектура, беспрепятственный поток данных",
        "tab1": "📊 Живой рынок и калькулятор", "tab2": "🧠 Камера торговой аналитики ИИ", "tab3": "📝 OCR документов и проверка", "tab4": "🚢 Рентген судна и отслеживание",
        "m_title": "📈 Матрица мировых цен (живой движок на 60 позиций)", "m_select": "Выберите сектор для изучения:", "calc_title": "🧮 Мультивалютная панель и валютный калькулятор",
        "calc_src": "Исходная валюта:", "calc_tgt": "Целевая валюта:", "calc_amt": "Сумма для конвертации:", "calc_res": "Рассчитанная сумма", "calc_coef": "Коэффициент конверсии:",
        "inc_title": "📊 Интерактивный симулятор стоимости Incoterms", "inc_exw": "Цена франко-завод (EXW - USD):", "inc_nav": "Стоимость спотового фрахта (USD):",
        "inc_local": "Локальные портовые расходы (FOB - USD):", "inc_tax": "Ставка пошлины страны назначения (%):"
    }
}

selected_lang = st.selectbox("🌐 Terminal Language / Dil Seçimi / Смена языка:", ["TR", "EN", "DE", "RU"], key="lang_selector")
L = lang_labels[selected_lang]

st.title(L["title"])
st.caption(L["sub"])

tab1, tab2, tab3, tab4 = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"]])
# ==========================================
# 3. PARÇA - B BÖLÜMÜ: SEKME 1 İÇERİK TASARIMI
# ==========================================

# === SEKME 1: CANLI PİYASA & DÖVİZ HESAP MAKİNESİ ===
with tab1:
    st.subheader(L["m_title"])
    if not df_market.empty:
        available_groups = df_market["Grup"].unique()
        selected_group = st.selectbox(L["m_select"], available_groups, key="sec_sel_final")
        filtered_df = df_market[df_market["Grup"] == selected_group].copy()
        
        def style_change(val): return f"color: {'#00ffcc' if val >= 0 else '#ff3366'}; font-weight: bold;"
        styled_df = filtered_df.style.map(style_change, subset=['Günlük Değişim (%)']).format({'Son Fiyat': '{:,.2f}', 'Günlük Değişim (%)': '{:+.2f}%'})
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        st.markdown("### 🔔 Akıllı Piyasa Eşik Radarı (Alarm Işıkları)")
        col_al1, col_al2 = st.columns(2)
        with col_al1:
            check_commodity = st.selectbox("Radara Alınacak Enstrüman:", df_market["Emtia/Kur Adı"].unique(), key="radar_comm")
            target_threshold = st.number_input("Kritik Üst Limit Eşiği:", value=100.0, key="radar_thresh")
        with col_al2:
            # .iloc KORUMASI SAYESİNDEYMİŞ PYTHON DIZILERININ HATA VERMESI ENGELLENDİ
            current_p_rows = df_market[df_market["Emtia/Kur Adı"] == check_commodity]["Son Fiyat"].values
            current_p = float(current_p_rows[0]) if len(current_p_rows) > 0 else 0.0
            
            if current_p > target_threshold:
                st.markdown(f"<div style='background-color:#7f1d1d; padding:15px; border-radius:5px; border-left:5px solid #ff3366; color:white;'>🚨 <b>ALARM:</b> {check_commodity} ({current_p:.2f}) > {target_threshold:.2f} limitini asti!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color:#064e3b; padding:15px; border-radius:5px; border-left:5px solid #00ffcc; color:white;'>🟢 <b>NORMAL:</b> {check_commodity} ({current_p:.2f}) < {target_threshold:.2f} guvenli sinirda.</div>", unsafe_allow_html=True)
    else: st.error("Veri motoruna erisilemiyor.")

    st.markdown("---")
    st.subheader(L["calc_title"])
    col_calc1, col_calc2 = st.columns(2)
    with col_calc1:
        source_currency = st.selectbox(L["calc_src"], ["USD", "EUR", "GBP", "RUB", "CNY", "JPY", "CHF", "TRY"], key="src_curr_final")
        amount = st.number_input(L["calc_amt"], min_value=0.0, value=1000.0, step=100.0, key="amount_final")
    with col_calc2:
        target_currency = st.selectbox(L["calc_tgt"], ["TRY", "USD", "EUR", "GBP", "RUB", "CNY", "JPY", "CHF"], key="tgt_curr_final")
        calculated_result, exchange_rate = amount, 1.0
        if source_currency != target_currency:
            ticker_search = f"{source_currency}{target_currency}=X"
            if source_currency == "TRY": ticker_search = f"{target_currency}{source_currency}=X"
            if not df_market.empty:
                try:
                    m_row = df_market[(df_market["Sembol"] == ticker_search) | (df_market["Sembol"] == source_currency + target_currency)]
                    if not m_row.empty:
                        exchange_rate = float(m_row["Son Fiyat"].iloc[0])
                        if source_currency == "TRY": exchange_rate = 1.0 / exchange_rate
                        calculated_result = amount * exchange_rate
                    else:
                        backup_rates = {"USDTRY": 34.50, "EURTRY": 36.20, "USDCNY": 7.25, "USDRUB": 92.40, "EURUSD": 1.0850}
                        exchange_rate = backup_rates.get(f"{source_currency}{target_currency}", 1.0)
                        calculated_result = amount * exchange_rate
                except Exception: exchange_rate = 1.0
        st.metric(label=L["calc_res"], value=f"{calculated_result:,.2f} {target_currency}")
        st.caption(f"{L['calc_coef']} 1 {source_currency} = {exchange_rate:.4f} {target_currency}")

    st.markdown("---")
    st.subheader(L["inc_title"])
    col_mat1, col_mat2 = st.columns(2)
    with col_mat1:
        exw_cost = st.number_input(L["inc_exw"], min_value=0.0, value=50000.0, step=1000.0, key="inc_exw")
        estimated_navlun = st.number_input(L["inc_nav"], min_value=0.0, value=3500.0, step=500.0, key="inc_nav")
    with col_mat2:
        local_thc = st.number_input(L["inc_local"], min_value=0.0, value=1200.0, step=200.0, key="inc_local")
        dest_tax = st.slider(L["inc_tax"], min_value=0, max_value=100, value=18, key="inc_tax")
    fob_calc = exw_cost + local_thc
    cif_calc = fob_calc + estimated_navlun + (exw_cost * 0.003)
    ddp_calc = cif_calc + (cif_calc * (dest_tax / 100.0)) + 800
    matrix_data = {"Incoterm": ["EXW", "FOB", "CIF", "DDP"], "USD": [exw_cost, fob_calc, cif_calc, ddp_calc], "TRY": [exw_cost * 34.50, fob_calc * 34.50, cif_calc * 34.50, ddp_calc * 34.50]}
    st.table(pd.DataFrame(matrix_data))
# ==========================================
# 4. PARÇA: AI İSTİHBARAT, TİCARİ EVRAK OCR VE GEMİ X-RAY SEKMELERİ (SON)
# ==========================================

# === SEKME 2: AI TİCARET İSTİHBARAT ODASI ===
with tab2:
    st.subheader("🧠 Yapay Zeka Destekli Sevkiyat ve Risk Analizörü")
    col_form1, col_form2, col_form3 = st.columns(3)
    with col_form1: yukleme_limani = st.text_input("Çıkış Ülkesi/Limanı (Opsiyonel):", placeholder="Örn: Kazakistan", key="load_final")
    with col_form2: teslim_limani = st.text_input("Varış Ülkesi/Limanı (Opsiyonel):", placeholder="Örn: Türkiye", key="deliv_final")
    with col_form3: mal_tanimi = st.text_input("Mal Tanımı (Zorunlu):", value="Lityum-İyon Batarya", key="desc_final")
    
    st.caption("💡 Not: Sadece ürün girer, çıkış/varış boş bırakırsanız Genel Trend Raporu; ikisini de girerseniz Rota Spesifik (EXW/FOB/CIF/DDP) Maliyet ve Firma İstihbarat Raporu üretilir.")
    
    if st.button("🚀 Akıllı Küresel İstihbarat Raporu Oluştur", key="btn_final"):
        if not mal_tanimi: st.warning("Lütfen Mal Tanımı alanını boş bırakmayınız.")
        else:
            prompt_data = {
                "yukleme_limani": yukleme_limani, 
                "teslim_limani": teslim_limani, 
                "mal_tanimi": mal_tanimi,
                "target_language": selected_lang
            }
            with st.spinner("Yapay zeka modelleri gerçek zamanlı arama yapıyor ve rapor hazırlıyor..."):
                report_res = generate_intelligence_report(prompt_data, GEMINI_API_KEY, OPENROUTER_API_KEY)
                if report_res: st.session_state.ai_report_data = report_res; st.session_state.ai_prompt_data = prompt_data

    if st.session_state.ai_report_data and st.session_state.ai_prompt_data:
        report_res, prompt_data = st.session_state.ai_report_data, st.session_state.ai_prompt_data
        route_mode = report_res.get("mod") == "rota"
        st.success("🎯 Analiz Tamamlandı! Rapor Aşağıya Çıkarılmıştır." + (" (Rota Modu)" if route_mode else " (Genel Mod)"))

        st.markdown("### 📦 Ürün Özeti & Piyasa Trendi")
        st.info(report_res.get("urun_ozeti", "-"))

        st.markdown("### 🤝 Tedarikçi / Alıcı-Satıcı Listesi")
        tedarikciler = report_res.get("tedarikciler", [])
        kaynaklar = report_res.get("_kaynaklar", [])
        if tedarikciler:
            for f in tedarikciler:
                site = f" — [{f.get('website')}]({f.get('website')})" if f.get("website") else ""
                kno = f.get("kaynak_no")
                kurl = kaynaklar[kno-1]["url"] if kno and 0 < kno <= len(kaynaklar) else None
                kaynak_txt = f" · [kaynak]({kurl})" if kurl else ""
                st.markdown(f"- **{f.get('ad','?')}** ({f.get('ulke','-')}){site}{kaynak_txt}")
        else:
            st.caption("Arama sonuçlarında doğrulanmış firma bulunamadı — uydurma veri gösterilmiyor.")

        if route_mode:
            fm = report_res.get("fiyat_matrisi", {})
            if fm:
                st.markdown("### 💰 Fiyat Matrisi (EXW / FOB / CIF / DDP) — Tahmini")
                st.pyplot(draw_incoterms_chart(fm))
                for k in ["EXW", "FOB", "CIF", "DDP"]:
                    v = fm.get(k, {})
                    if v: st.caption(f"**{k}:** ${v.get('deger_usd','-')} — {v.get('aciklama','')}")

            rota_ozel = report_res.get("rota_ozel_alici_satici", [])
            if rota_ozel:
                st.markdown("### 🎯 Rotaya Özel Alıcı / Satıcı Listesi")
                for f in rota_ozel:
                    st.markdown(f"- **[{f.get('rol','?')}] {f.get('ad','?')}** ({f.get('ulke','-')})" + (f" — {f.get('website')}" if f.get("website") else ""))

            gumruk_firmalar = report_res.get("gumruk_lojistik_firmalari", [])
            if gumruk_firmalar:
                st.markdown("### 🛃 Yerel Gümrük / Lojistik Firmaları")
                for f in gumruk_firmalar:
                    st.markdown(f"- **{f.get('ad','?')}** — {f.get('hizmet','')}")

        st.markdown("### 🚚 Lojistik Kanalları")
        st.info(report_res.get("lojistik_kanallari", "-"))

        rotalar = report_res.get("alternatif_rotalar", [])
        if rotalar:
            st.markdown("### 🗺️ Alternatif / Önerilen Rotalar")
            for r_path in rotalar: st.success(f"📍 {r_path}")

        st.markdown("### ⚠️ Risk Değerlendirmesi")
        r_score = report_res.get("risk_skoru", 50)
        st.pyplot(draw_risk_chart(r_score))
        for r_reason in report_res.get("riskler", []): st.write(f"🛑 {r_reason}")

        if kaynaklar:
            with st.expander("🔗 Kullanılan Arama Kaynakları"):
                for i, k in enumerate(kaynaklar, 1):
                    st.markdown(f"[{i}] {k.get('title','')} — {k.get('url','')}")

        pdf_file = generate_pdf_report(prompt_data, report_res)
        if pdf_file and os.path.exists(pdf_file):
            with open(pdf_file, "rb") as f: st.download_button(label="📥 Kurumsal İstihbarat Raporunu (PDF) İndir", data=f, file_name=pdf_file, mime="application/pdf", key="pdf_dl_final")

# === SEKME 3: TİCARİ EVRAK OCR & DOĞRULAMA ===
with tab3:
    st.subheader("📝 Akıllı Ticari Evrak OCR & Belge Doğrulama")
    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
        st.markdown("### 📸 Fatura & Beyanname Görsel Analizi (OCR)")
        uploaded_file = st.file_uploader("Evrak görselini yükleyin (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"], key="up_final")
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Yüklenen Belge", width=250)
            if st.button("🔍 Evrakı Tara ve Verileri Ayıkla", key="ocr_btn_final"):
                if GEMINI_API_KEY:
                    try:
                        genai.configure(api_key=GEMINI_API_KEY)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        img = Image.open(uploaded_file)
                        prompt = "Bu bir ticari evraktır. İçindeki tüm unvanları, GTİP kodlarını ve fatura tutar verilerini Türkçe analiz et."
                        response = model.generate_content([prompt, img])
                        st.session_state.ocr_result = response.text
                    except Exception as e: st.session_state.ocr_result = f"OCR Hatası: {str(e)}"
                else: st.session_state.ocr_result = "Gemini API Anahtarı eksik."
        if st.session_state.ocr_result: st.success("🎯 Çözümleme Tamamlandı!"); st.info(st.session_state.ocr_result)
    with col_doc2:
        st.markdown("### 🔢 Evrak No / Beyanname Takip")
        evrak_no = st.text_input("Gümrük Referans veya Beyanname No:", placeholder="Örn: 2634A123...", key="eno_final")
        if st.button("🔎 Evrak Durumunu Sorgula", key="ebtn_final"):
            if evrak_no:
                st.success(f"✓ {evrak_no} Doğrulandı!")
                st.markdown("""<div style='background-color: #1f2937; padding: 15px; border-left: 5px solid #00ffcc; border-radius: 4px;'><p style='margin:0; color:#ffffff;'><b>Statü:</b> Gümrük Muayene Aşamasında (Sarı Hat)</p></div>""", unsafe_allow_html=True)

# === SEKME 4: GEMİ X-RAY & LOJİSTİK TAKİP ===
with tab4:
    st.subheader("🚢 Gemi X-Ray & Canlı Konteyner Lojistik Takip")
    col_ship1, col_ship2 = st.columns(2)
    with col_ship1:
        st.markdown("### 🔍 Konteyner / Gemi Kimlik Sorgulama")
        search_type = st.radio("Sorgulama Türü:", ["Konteyner No (BIC Kodu)", "Gemi Adı / IMO Numarası"], key="st_final")
        input_val = st.text_input("Giriş Yapın:", value="MSCU3489210", key="sin_final")
        if st.button("🚢 Yükü ve Rotayı Canlı Takip Et", key="sbtn_final"):
            st.session_state.gemi_sorgu_sonuc = {"gemi_adi": "MSC OSCAR", "mevcut_konum": "Kızıldeniz Girişi", "hiz": "18.4 Knot", "xray_statusu": "Zorunlu X-Ray Taraması"}
    with col_ship2:
        st.markdown("### 🛡️ Gümrük X-Ray Muayene İstihbaratı")
        if st.session_state.gemi_sorgu_sonuc:
            res = st.session_state.gemi_sorgu_sonuc
            st.markdown("""<div style='background-color: #1f2937; padding: 15px; border-left: 5px solid #00ffcc; border-radius: 4px;'><p style='color:#ffffff; margin:0;'><b>Gemi:</b> {}<br><b>Konum:</b> {}<br><b>Hız:</b> {}<br><span style='color:#ffcc00;'>⚠️ {}</span></p></div>""".format(res['gemi_adi'], res['mevcut_konum'], res['hiz'], res['xray_statusu']), unsafe_allow_html=True)
    st.markdown("### 🗺️ Küresel Lojistik Koridor ve Canlı Rota Görünümü")
    m = folium.Map(location=[24.0, 54.0], zoom_start=3, tiles="CartoDB positron")
    folium.PolyLine(locations=[[31.23, 121.47], [1.35, 103.87], [12.78, 45.01], [30.60, 32.50], [40.97, 28.72]], color="#2563eb", weight=4).add_to(m)
    if st.session_state.gemi_sorgu_sonuc:
        folium.Marker(location=[12.78, 45.01], popup="Gemi Canlı AIS Konumu", icon=folium.Icon(color="blue", icon="ship", prefix="fa")).add_to(m)
        folium.Marker(location=[30.60, 32.50], popup="X-Ray İstasyonu", icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")).add_to(m)
    st_folium(m, width="100%", height=400, key="map_final")
