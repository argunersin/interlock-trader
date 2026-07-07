# ==========================================
# main.py veya app.py - ORKESTRA ŞEFİ (ANA DOSYA)
# ==========================================
import streamlit as st
import pandas as pd
import yfinance as yf
import os

# Bağımsız olarak oluşturduğumuz modül odalarını içeri çağırıyoruz
from borsa_ekrani import render_borsa_ekrani
from istihbarat_odasi import render_istihbarat_odasi
from evrak_analiz import render_evrak_analiz
from gemi_xray import render_gemi_xray

# Ekranı geniş modda açıyoruz ve telefonlarda kilitlenen sidebar'ı (yan menüyü)
# Claude'un 6. uyarısı uyarınca tamamen engellemek için 'collapsed' yapıyoruz.
st.set_page_config(
    page_title="Küresel Emtia & Ticaret İstihbarat Paneli",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Telefon ekranlarında yan menünün yanlışlıkla bile açılmasını engellemek için CSS şırınga ediyoruz
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 5. UYARI ÇÖZÜMÜ: Asla Çökmeyen Akıllı Şifre ve API Anahtarı Sigorta Zinciri
def get_api_key(key_name):
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2:
                            k, v = parts
                            if k.strip() == key_name:
                                return v.strip().strip('"').strip("'")
        except Exception:
            pass
            
    return os.environ.get(key_name, None)

# API anahtarlarını güvenli zincirden çekiyoruz
GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")
OPENROUTER_API_KEY = get_api_key("OPENROUTER_API_KEY")

# 60 Kalemlik Canlı Emtia Listesi Tanımı
COMMODITY_GROUPS = {
    "Enerji": {
        "Ham Petrol (WTI)": "CL=F", "Brent Petrol": "BZ=F", "Doğalgaz": "NG=F",
        "Isıtma Yağı": "HO=F", "RBOB Benzin": "RB=F", "Kömür (Rotterdam)": "MTF=F",
        "Etanol": "CU=F", "Uranyum": "UX=F", "Karbon İzinleri": "CFI=F"
    },
    "Değerli Metaller": {
        "Altın": "GC=F", "Gümüş": "SI=F", "Platin": "PL=F",
        "Paladyum": "PA=F", "Rodyum (İndeks)": "RHO", "İridyum (İndeks)": "IRD"
    },
    "LME Endüstriyel Metaller": {
        "Bakır": "HG=F", "Alüminyum": "ALI=F", "Çinko": "ZNC=F",
        "Kurşun": "PB=F", "Nikel": "NIL=F", "Kalay": "TIN=F",
        "Demir Cevheri": "TIO=F", "Çelik Hurda": "HRF=F", "Lityum Karbonat": "LTH=F"
    },
    "Tarım & Gıda": {
        "Buğday": "W=F", "Mısır": "C=F", "Soya Fasulyesi": "S=F",
        "Kahve (Arabica)": "KC=F", "Kakao": "CC=F", "Pamuk": "CT=F",
        "Şeker": "SB=F", "Canlı Sığır": "LC=F", "Kinoa (İndeks)": "QN=F",
        "Pirinç": "ZR=F", "Yulaf": "O=F", "Kereste": "LBS=F"
    },
    "Kimyasallar & Plastik": {
        "Polipropilen": "PP=F", "Polietilen": "PE=F", "PVC": "PVC=F",
        "Metanol": "MET=F", "Üre (Gübre)": "UREA=F", "Amonyak": "AM=F",
        "Kaustik Soda": "CS=F", "Kostik": "KST=F"
    },
    "Navlun & Lojistik (Konteyner/Kuru Yük)": {
        "Baltık Kuru Yük (BDI)": "^BDI", "Konteyner Endeksi (WCI)": "WCI=F",
        "Rotterdam-Şanghay": "RSH=F", "Şanghay-Los Angeles": "SLA=F",
        "Süveyş Geçiş Maliyeti": "SUZ=F", "Panama Geçiş Maliyeti": "PAN=F",
        "Tanker Navlun Endeksi": "BDTI", "Hava Kargo Endeksi (BAI)": "BAI=F"
    },
    "Çoklu Kur Ticaret Paneli": {
        "Dolar / TL": "USDTRY=X", "Euro / TL": "EURTRY=X", "Euro / Dolar": "EURUSD=X",
        "Sterlin / Dolar": "GBPUSD=X", "Dolar / Ruble": "RUB=X", "Dolar / Yuan": "CNY=X",
        "Dolar / Yen": "JPY=X", "Dolar / İsviçre Frangı": "CHF=X"
    }
}

@st.cache_data(ttl=300)
def fetch_live_commodity_data():
    rows = []
    tickers_to_fetch = []
    ticker_to_name = {}
    ticker_to_group = {}

    for group, commodities in COMMODITY_GROUPS.items():
        for name, ticker in commodities.items():
            tickers_to_fetch.append(ticker)
            ticker_to_name[ticker] = name
            ticker_to_group[ticker] = group

    try:
        data = yf.download(tickers_to_fetch, period="1d", interval="1m", group_by="ticker", progress=False)
        for ticker in tickers_to_fetch:
            name = ticker_to_name[ticker]
            group = ticker_to_group[ticker]
            price, change, status = 0.0, 0.0, "Canlı"
            try:
                if ticker in data.columns.levels:
                    ticker_data = data[ticker]
                    if not ticker_data.empty:
                        valid_prices = ticker_data['Close'].dropna()
                        if not valid_prices.empty:
                            price = float(valid_prices.iloc[-1])
                            valid_opens = ticker_data['Open'].dropna()
                            if not valid_opens.empty and valid_opens.iloc != 0:
                                change = ((price - valid_opens.iloc) / valid_opens.iloc) * 100
                        else:
                            backup = yf.Ticker(ticker).history(period="2d")
                            if len(backup) >= 1:
                                price = float(backup['Close'].iloc[-1])
                                if len(backup) >= 2:
                                    change = ((price - backup['Close'].iloc[-2]) / backup['Close'].iloc[-2]) * 100
            except Exception:
                status = "Bağlantı Hatası"

            rows.append({"Grup": group, "Emtia/Kur Adı": name, "Sembol": ticker, "Son Fiyat": price, "Günlük Değişim (%)": change, "Durum": status})
    except Exception:
        pass
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Grup", "Emtia/Kur Adı", "Sembol", "Son Fiyat", "Günlük Değişim (%)", "Durum"])

# Verileri çekiyoruz
with st.spinner("Küresel veri hatları bağlanıyor ve canlı fiyatlar yükleniyor..."):
    df_market = fetch_live_commodity_data()

# Üst Bloomberg Kayan Fiyat Bandı (Ticker)
if not df_market.empty:
    ticker_items = []
    ticker_df = df_market[df_market["Son Fiyat"] > 0].head(25)
    for _, row in ticker_df.iterrows():
        color = "#00ffcc" if row["Günlük Değişim (%)"] >= 0 else "#ff3366"
        sign = "+" if row["Günlük Değişim (%)"] >= 0 else ""
        ticker_items.append(
            f'<span style="color:#ffffff; font-weight:bold; margin-right:5px;">{row["Emtia/Kur Adı"]}:</span> '
            f'<span style="color:{color}; font-weight:bold;">{row["Son Fiyat"]:.2f} ({sign}{row["Günlük Değişim (%)"]:.2f}%)</span>'
        )
    ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; ".join(ticker_items)
    st.markdown(f"""
        <div style="background-color: #0e1117; border-bottom: 2px solid #1f2937; padding: 10px 0; overflow: hidden; white-space: nowrap; width: 100%;">
            <marquee behavior="scroll" direction="left" scrollamount="5" style="font-family: monospace; font-size: 14px;">
                {ticker_text}
            </marquee>
        </div>
        <br>
    """, unsafe_allow_html=True)

# ANA BAŞLIKLAR
st.title("🌐 Küresel Emtia & Ticaret İstihbarat Deposu")
st.caption("Modüler Mimari, Gerçek Zamanlı Veriler ve Gelişmiş Yapay Zeka Odaları")

# İstediğin Yepyeni Giriş Düzeni: 4 Bağımsız Sekme Halinde Odalar Açılıyor
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Canlı Piyasa & Hesap Makinesi", 
    "🧠 AI Ticaret İstihbarat Odası", 
    "📝 Ticari Evrak OCR & Doğrulama", 
    "🚢 Gemi X-Ray & Lojistik Takip"
])

# Her bir sekmeye, ilgili bağımsız dosyadaki fonksiyonu bağlıyoruz
with tab1:
    render_borsa_ekrani(df_market)

with tab2:
    render_istihbarat_odasi(GEMINI_API_KEY, OPENROUTER_API_KEY)

with tab3:
    render_evrak_analiz(GEMINI_API_KEY)

with tab4:
    render_gemi_xray()
