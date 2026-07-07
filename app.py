# ==========================================
# app.py veya main.py - ORKESTRA ŞEFİ (ANA DOSYA)
# ==========================================
import streamlit as st
import os

# Ekran genişlik ve telefon uyumluluk ayarları
st.set_page_config(
    page_title="Küresel Emtia & Ticaret İstihbarat Paneli",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar'ı telefonda kilitlenmesin diye CSS ile tamamen yok ediyoruz
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] { padding: 12px 24px; font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Güvenli Şifre Çözücü Sigorta Fonksiyonu
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

GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")
OPENROUTER_API_KEY = get_api_key("OPENROUTER_API_KEY")

st.title("🌐 Küresel Emtia & Ticaret İstihbarat Deposu")
st.caption("Tam Modüler Mimari, Gerçek Zamanlı Veriler ve Gelişmiş Yapay Zeka Üssü")

# 4 Bağımsız Sekme (Tabs) burada net olarak ayrılıyor
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Canlı Piyasa & Hesap Makinesi", 
    "🧠 AI Ticaret İstihbarat Odası", 
    "📝 Ticari Evrak OCR & Doğrulama", 
    "🚢 Gemi X-Ray & Lojistik Takip"
])

# Modüllerimizi sadece çağırıyoruz (Hata lüksünü sıfıra indiriyoruz)
with tab1:
    try:
        import borsa_ekrani
        borsa_ekrani.render_borsa_ekrani()
    except Exception as e:
        st.error(f"Piyasa ekranı yüklenirken bir hata oluştu: {str(e)}")

with tab2:
    try:
        import istihbarat_odasi
        istihbarat_odasi.render_istihbarat_odasi(GEMINI_API_KEY, OPENROUTER_API_KEY)
    except Exception as e:
        st.error(f"İstihbarat odası yüklenirken bir hata oluştu: {str(e)}")

with tab3:
    try:
        import evrak_analiz
        evrak_analiz.render_evrak_analiz(GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Evrak analiz odası yüklenirken bir hata oluştu: {str(e)}")

with tab4:
    try:
        import gemi_xray
        gemi_xray.render_gemi_xray()
    except Exception as e:
        st.error(f"Lojistik takip odası yüklenirken bir hata oluştu: {str(e)}")
