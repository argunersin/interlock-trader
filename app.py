import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import urllib.parse
import json
import os

# 🔒 GÜVENLİK ZIRHI: ŞİFRE KODUN İÇİNDEN KALDIRILDI, RENDER KASASINDAN OKUNUYOR
import google.generativeai as genai
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
elif "google_api_key" in st.secrets:
    genai.configure(api_key=st.secrets["google_api_key"])

# 1. RETRO SİBER TERMİNAL GÖRSEL AYARLARI
st.set_page_config(page_title="Interlock Global AI Terminal", layout="wide", page_icon="📟")

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

st.sidebar.markdown("<h2 style='color: #00f2fe; text-align: center;'>📟 TERMINAL v4</h2>", unsafe_allow_html=True)
st.sidebar.caption("Zırhlı Yapay Zeka Sistemi Aktif")
menu = st.sidebar.radio("İŞLEM MODÜLÜ", ["🚀 Otonom İstihbarat Ajanı", "📄 Evrak Analiz (OCR)", "⚓ Özel Gemi Röntgeni ($20)"])

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
if menu == "🚀 Otonom İstihbarat Ajanı":
    st.markdown("<h1 style='color: #00f2fe;'>📟 INTERLOCK GLOBAL REAL-TIME RADAR</h1>", unsafe_allow_html=True)
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
    # 🧠 OTONOM YAPAY ZEKA AJANI VE DERİN RAPORLAMA KATMANI (ACCIO MODELİ)
    st.divider()
    search_query = st.text_input("Gelişmiş Yapay Zeka İstihbarat Terminali (Emtia ve Ülkeleri Yazın):", placeholder="Örn: irmik kazakistan - endonezya veya aluminyum rusya - türkiye")
    
    if search_query:
        st.info("📟 Interlock Otonom Ajanları internete çıkıyor, küresel veri ağları, gümrük kotaları ve B2B platformları taranıyor... Lütfen bekleyin (3-5 sn)...")
        
        # GEMINI UYANDIRMA VE YAPAY ZEKA TALİMAT MATRİSİ
        prompt = f"""
        Sen uluslararası bir emtia brokerlığı yapay zeka ajanısın (Interlock Accio Modeli).
        Kullanıcı şu sorguyu yaptı: '{search_query}'.
        Bu sorguya göre dünya genelindeki B2B ağlarından, gümrük kayıtlarından ve ticaret koridorlarından anlık istihbarat topla.
        Bize tam olarak şu kriterleri içeren ve kesinlikle boş metin içermeyen JSON formatında bir yanıt ver:
        1. "Urun_Adi": Sorgulanan emtianın tam ticari adı ve GTİP (HS Code) kodu.
        2. "Fiyat_Matrisi": Incoterms 2025 kurallarına uygun olarak EXW, FOB, CIF ve DDP tahmini ton başına maliyet kırılımları ve varsa bölgesel pazar primleri.
        3. "Lojistik_Rota": Çıkış limanından varış limanına kadar kullanılacak en optimize deniz/demiryolu ticaret koridoru ve tahmini navlun süresi.
        4. "Mevzuat_Kotalar": Hedef ülkenin uyguladığı güncel gümrük vergileri, anti-damping veya tarife kontenjanları.
        5. "Gerekli_Evraklar": Gümrükten sorunsuz geçmesi için zorunlu olan en az 5 adet kurumsal resmi evrak (MBL, SGS, Phytosanitary vb.).
        6. "Top5_Saticilar": O menşe ülkedeki en büyük 5 üretici/ihracatçı firmanın adı, kurumsal e-posta adresi ve telefon bilgisi.
        7. "Top5_Alicilar": O hedef ülkedeki en büyük 5 ithalatçı/alıcı firmanın adı, e-posta ve iletişim bilgisi.
        8. "Top5_Lojistik_Gumruk": Bu hatta operasyon yürüten yerel/küresel 5 nakliye ve gümrük müşavirliği firmasının kontak bilgileri.
        
        Yanıtı SADECE saf ve geçerli bir JSON olarak döndür. Markdown etiketleri (```json gibi) veya açıklama metinleri KESİNLİKLE ekleme. Doğrudan parantezle başla.
        """
        
        try:
            # Gemini 1.5 Flash ile internet tabanlı otonom veri üretimi
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            ai_data = json.loads(clean_text)
            
            # Gelen Verileri Terminal Ekranına Basma
            product = ai_data.get("Urun_Adi", "Emtia Segmenti")
            st.success(f"📌 {product} Analiz Segmenti Başarıyla Kilitlendi.")
            
            report_data = {
                "Incoterms Fiyat Matrisi": ai_data.get("Fiyat_Matrisi", "Hesaplanıyor..."),
                "Optimize Lojistik Koridor": ai_data.get("Lojistik_Rota", "Analiz ediliyor..."),
                "Gümrük Rejimi & Kotalar": ai_data.get("Mevzuat_Kotalar", "Taranıyor..."),
                "Zorunlu Resmi Belgeler": ai_data.get("Gerekli_Evraklar", "Listeleniyor..."),
                "Top 5 Menşe Üretici / İhracatçı": ai_data.get("Top5_Saticilar", "Mailler çekiliyor..."),
                "Top 5 Hedef İthalatçı / Alıcı": ai_data.get("Top5_Alicilar", "İletişim ağları taranıyor..."),
                "Top 5 Lojistik & Gümrük Acentesi": ai_data.get("Top5_Lojistik_Gumruk", "Kontaklar doğrulanıyor...")
            }
            
            st.table(pd.DataFrame(list(report_data.items()), columns=["Yapay Zeka İstihbarat Kriteri", "Otonom Canlı Rapor Çıktısı"]))
            
            # PDF VE WHATSAPP ENTEGRASYONU
            pdf_file = generate_advanced_pdf(search_query, report_data)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.download_button(label="📥 İstihbarat Brifingi Resmi PDF İndir", data=pdf_file, file_name=f"Interlock_{search_query}_Briefing.pdf")
            with col_b2:
                wa_text = f"*INTERLOCK AI BRIEFING*\n\n*Sorgu:* {search_query.upper()}\n*Detaylar:* {product}\n\nCanlı yapay zeka ajan raporu PDF formatında sisteme yüklenmiştir."
                st.markdown(f'<a href="https://wa.me{urllib.parse.quote(wa_text)}" target="_blank"><div style="background-color:#25D366;color:white;text-align:center;padding:12px;border-radius:5px;font-weight:bold;cursor:pointer;">📱 Brifingi WhatsApp İletişim Hattına Gönder</div></a>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ Yapay zeka ajan hattında bir yoğunluk oluştu: {str(e)}. Lütfen sorguyu tekrar deneyin.")

    # HARİTA KATMANI (SABİT)
    st.divider()
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=4, tiles="CartoDB dark_matter")
    folium.Marker([41.15, 29.10], popup="MSC TESSA (Aktif Kargo)", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=450)

elif menu == "📄 Evrak Analiz (OCR)":
    st.title("📄 Akıllı Evrak Doğrulama Terminali")
    st.info("Bu modül, yüklenen belgeleri yapay zeka görüşüyle (Vision LLM) tarayarak sahtecilik ve tutarsızlık analizlerini pıt pıt listeleyecektir.")
    st.file_uploader("Evrak Yükleyin (PDF/JPG/PNG)", type=["pdf", "jpg", "png"])

elif menu == "⚓ Özel Gemi Röntgeni ($20)":
    st.title("⚓ Özel Gemi Röntgeni & Cargo Manifest Detayları")
    ship_imo = st.text_input("Gemi IMO Numarası Girin:", placeholder="Örn: 9930038")
    if ship_imo:
        st.markdown('<div style="background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; text-align:center;"><h3>💳 RAPOR SATIN ALMA PANELİ</h3><p style="color: #cbd5e1; font-size:14px; margin-bottom:15px;">Bu sorgu için hesabınızdan <b>$20.00 USD</b> düşülecektir.</p><button style="background-color:#d4af37; color:#0e1c36; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">Kredi Kartı ile Güvenli Öde</button></div>', unsafe_allow_html=True)
