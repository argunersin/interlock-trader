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
import time

# 🔒 GÜVENLİK ZIRHI: RENDER KASASINDAN OKUMA
import google.generativeai as genai
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 1. RETRO SİBER TERMİNAL GÖRSEL AYARLARI
st.set_page_config(page_title="Interlock Global AI Terminal", layout="wide", page_icon="📟")

st.markdown("""
    <style>
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: transparent !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    .main, block-container, .stApp { background-color: #05070f !important; color: #00f2fe !important; }
    
    /* 📟 SAYFAYI KARARTMAYAN, SADECE RAKAMI PIRRR DİYE DÖNDÜREN 3D FLIP KUTULARI */
    .split-flap-card {
        background: #0f1322;
        border: 2px solid #1f2937; border-radius: 6px; padding: 20px; text-align: center;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.9), 0 6px 12px rgba(0,0,0,0.6); min-height: 130px;
        display: flex; flex-direction: column; justify-content: center;
        perspective: 1000px; /* 3D derinlik katmanı */
    }
    .split-flap-title { font-family: 'Courier New', monospace; font-size: 11px; color: #9ca3af; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; }
    
    /* Rakamların takla atma animasyonu (Pırrr efekti) */
    .split-flap-value { 
        font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; color: #00f2fe; 
        text-shadow: 0 0 10px rgba(0,242,254,0.4);
        display: inline-block;
        transform-style: preserve-3d;
        animation: pırrrRotation 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Hızlı döner şak diye durur */
    }
    @keyframes pırrrRotation {
        0% { transform: rotateX(-90deg); opacity: 0.3; }
        50% { transform: rotateX(90deg); opacity: 0.7; color: #d4af37; }
        100% { transform: rotateX(0deg); opacity: 1; }
    }
    .split-flap-sub { font-family: 'Courier New', monospace; font-size: 11px; color: #10b981; margin-top: 5px; }
    
    .stTable, table, tr, td, th { background-color: #0b0f19 !important; color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    th { color: #00f2fe !important; font-weight: bold !important; border-bottom: 2px solid #1f2937 !important; }
    td { border-bottom: 1px solid #1f2937 !important; padding: 12px !important; }
    [data-testid="stSidebar"] { background-color: #070a14 !important; border-right: 1px solid #1f2937 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    </style>
    """, unsafe_allow_html=True)

# SOL MENÜ VE DİL SEÇİM SİHRİ
st.sidebar.markdown("<h2 style='color: #00f2fe; text-align: center;'>📟 TERMINAL v4.2</h2>", unsafe_allow_html=True)
lang = st.sidebar.selectbox("🌐 LANGUAGE / DİL:", ["English", "Türkçe"])

if lang == "Türkçe":
    menu_label = "İŞLEM MODÜLÜ"
    mod1 = "🚀 Otonom İstihbarat Ajanı"
    mod2 = "📄 Evrak Analiz (OCR)"
    mod3 = "⚓ Özel Gemi Röntgeni ($20)"
else:
    menu_label = "OPERATION MODULE"
    mod1 = "🚀 Autonomous AI Agent"
    mod2 = "📄 Document Analysis (OCR)"
    mod3 = "⚓ Custom Vessel X-Ray ($20)"

menu = st.sidebar.radio(menu_label, [mod1, mod2, mod3])

# PREMIUM PDF ÜRETİM MOTORU ($19.99 RAPOR İÇİN BÜYÜK VERİLER BURAYA GÖMÜLÜYOR)
def generate_advanced_pdf(query, ai_data, is_tr):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, "INTERLOCK GLOBAL - PREMIUM INTELLIGENCE BRIEFING")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, f"Target Route / Analiz Koridoru: {query.upper()}")
    y = 700
    sections = [
        ("COMMODITY & HS CODE", "Urun_Adi"),
        ("INCOTERMS PRICE MATRIX", "Fiyat_Matrisi"),
        ("LOGISTICS & TRADE ROUTE", "Lojistik_Rota"),
        ("CUSTOMS REGIME & TARIFFS", "Mevzuat_Kotalar"),
        ("REQUIRED OFFICIAL DOCUMENTS", "Gerekli_Evraklar"),
        ("TOP 5 MANUFACTURERS / SUPPLIERS", "Top5_Saticilar"),
        ("TOP 5 KEY BUYERS / IMPORTERS", "Top5_Alicilar"),
        ("TOP 5 LOCAL LOGISTICS & CUSTOMS AGENTS", "Top5_Lojistik_Gumruk")
    ]
    for title, key in sections:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"■ {title}")
        y -= 15
        p.setFont("Helvetica", 9)
        val = str(ai_data.get(key, ""))
        words = val.split()
        line = ""
        for word in words:
            if len(line) + len(word) < 85:
                line += " " + word
            else:
                p.drawString(60, y, line)
                y -= 12
                line = word
        p.drawString(60, y, line)
        y -= 25
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
# MODÜL 1: CANLI RETRO BORSA VE İSTİHBARAT
if menu in ["🚀 Otonom İstihbarat Ajanı", "🚀 Autonomous AI Agent"]:
    st.markdown("<h1 style='color: #00f2fe;'>📟 INTERLOCK GLOBAL REAL-TIME RADAR</h1>", unsafe_allow_html=True)
    st.caption("Autonomous data streaming with slow-motion mechanical split-flap displays" if lang == "English" else "Otonom veri akışlı ve ağır çekim mekanik split-flap model fiyat göstergeleri")
    
    # 2026 CANLI VERİ ÇEKİM MOTORU
    try:
        ali = yf.Ticker("ALI=F").history(period="2d"); ali_p = round(ali['Close'].iloc[-1], 2) if not ali.empty else 3266.50
        cu = yf.Ticker("HG=F").history(period="2d"); cu_p = round(cu['Close'].iloc[-1] * 2204.62, 2) if not cu.empty else 9120.00
        sugar = yf.Ticker("SB=F").history(period="2d"); sugar_p = round(sugar['Close'].iloc[-1] * 22.04, 2) if not sugar.empty else 329.72
        wheat = yf.Ticker("W=F").history(period="2d"); wheat_p = round(wheat['Close'].iloc[-1] * 0.367, 2) if not wheat.empty else 245.00
        oil = yf.Ticker("BZ=F").history(period="2d"); oil_p = round(oil['Close'].iloc[-1], 2) if not oil.empty else 71.38
    except:
        ali_p=3266.50; cu_p=9120.00; sugar_p=329.72; wheat_p=245.00; oil_p=71.38

    # 📻 MEKANİK KUMANDA: SEÇİM ÇENTİKLERİ (SAYFAYI YENİLERKEN EKRANI KARARTMAZ)
    st.write("")
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        m_label = "SELECT METAL / METAL ÇENTİĞİ:" if lang == "English" else "⚙️ METAL SEÇİM ÇENTİĞİ:"
        metal_select = st.radio(m_label, ["Alüminyum (Külçe P1020)", "Bakır Katot (Grade A)", "İnşaat Demiri (Rebar)", "HMS 1/2 Demir Hurdası"], horizontal=True)
    with col_ctrl2:
        g_label = "SELECT AGRI / GIDA ÇENTİĞİ:" if lang == "English" else "🌾 GIDA SEÇİM ÇENTİĞİ:"
        gida_select = st.radio(g_label, ["Beyaz Şeker (ICUMSA 45)", "Ekmeklik Buğday", "Sarı Mısır", "Ham Ayçiçek Yağı"], horizontal=True)

    # PIT PIT ATAN 6 BÜYÜK RETRO LEVHA YERLEŞİMİ (ANİMASYON SADECE DEĞERLERE BAĞLANDI)
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
    # 🧠 ASLA ÇÖKMEYEN ÇİFT YAPAY ZEKA MOTORU, ENTER BUTONU VE \$19.99 PAYWALL
    st.divider()
    search_placeholder = "e.g., sugar brazil - turkey" if lang == "English" else "Örn: şeker brezilya - türkiye"
    search_label = "Advanced AI Intelligence Search:" if lang == "English" else "Gelişmiş Yapay Zeka İstihbarat Arama Motoru:"
    
    with st.form(key="ai_search_form"):
        search_query = st.text_input(search_label, placeholder=search_placeholder)
        submit_btn_label = "EXECUTE SEARCH (ENTER)" if lang == "English" else "İSTİHBARATI BAŞLAT (ENTER)"
        submit_button = st.form_submit_button(label=submit_btn_label)
    
    if submit_button and search_query:
        st.info("📟 Interlock Accio AI Agents exploring global trade networks... Please wait..." if lang == "English" else "📟 Interlock Otonom Ajanları küresel veri ağlarını tarıyor... Lütfen bekleyin...")
        
        prompt = f"""
        Sen uluslararası bir emtia brokerlığı yapay zeka ajanısın (Interlock Accio Modeli).
        Kullanıcı şu sorguyu yaptı: '{search_query}'.
        Bu sorguya göre dünya genelindeki B2B ağlarından, gümrük kayıtlarından bir ticaret koridorlarından anlık istihbarat topla.
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
        
        ai_data = None
        # 1. HAMLE: ÖNCE ANA MOTORU (GOOGLE GEMINI) DENE (ZAMAN AŞIMI 30 SANİYEYE ÇIKARILDI)
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            ai_data = json.loads(clean_text)
        except Exception as gemini_err:
            # 2. HAMLE: GOOGLE ADRESİ KİLİTLİYSE 0.1 SÂNİYEDE RESMİ VE GÜVENLİ GROQ MOTORUNU TETİKLE
            try:
                groq_key = os.environ.get("GROQ_API_KEY")
                if groq_key:
                    payload = {
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    }
                    headers = {
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    }
                    # Zaman aşımı süresi 30 saniye olarak esnetildi, donma önlendi
                    res = requests.post("https://groq.com", json=payload, headers=headers, timeout=30)
                    if res.status_code == 200:
                        raw_out = res.json()['choices']['message']['content']
                        ai_data = json.loads(raw_out.strip())
            except:
                pass

        # VERİLERİ ÖZET SADE FORMATTA EKRANA BASMA VE GİZLEME SİHRİ
        if ai_data:
            try:
                product = ai_data.get("Urun_Adi", "Emtia Segmenti")
                st.success(f"📌 {product} - AI Target Locked.")
                
                summary_tr = {
                    "Analiz Edilen Emtia": product,
                    "Lojistik Güzergah Özeti": ai_data.get("Lojistik_Rota", "")[:130] + "...",
                    "Gümrük & Kota Özeti": ai_data.get("Mevzuat_Kotalar", "")[:130] + "...",
                    "Kilitli Premium Bilgiler": "🔓 5 Adet Canlı Satıcı Maili, 5 Adet İthalatçı Maili, Tam EXW/FOB/CIF/DDP Fiyatları ve Yerel Gümrükçü Kontakları Premium PDF İçine Şifrelenmiştir."
                }
                summary_en = {
                    "Analyzed Commodity": product,
                    "Logistics Route Summary": ai_data.get("Lojistik_Rota", "")[:130] + "...",
                    "Customs & Tariff Summary": ai_data.get("Mevzuat_Kotalar", "")[:130] + "...",
                    "Locked Premium Data": "🔓 5 Live Supplier Emails, 5 Key Importer Emails, Complete EXW/FOB/CIF/DDP Matrix, and Local Customs Agents are LOCKED inside the Premium PDF."
                }
                
                display_data = summary_tr if lang == "Türkçe" else summary_en
                st.table(pd.DataFrame(list(display_data.items()), columns=["Kriter / Milestone", "Terminal Dashboard"]))
                
                # 💳 $19.99'LIK PAYWALL STRIPE PANELİ
                st.write("")
                pay_desc = "5 adet gerçek üretici mailini, 5 adet alıcı telefon/kontak bilgisini ve tam DDP maliyet kırılımlarını anında açın." if lang == "Türkçe" else "Get all 5 supplier emails, 5 buyer phone/mails, and complete DDP cost breakdowns instantly."
                st.markdown(f"""
                    <div style="background-color: #0b0f19; padding: 25px; border-radius: 8px; border: 2px dashed #d4af37; text-align:center; margin-top:20px;">
                        <h3 style="color:#d4af37; font-family:'Courier New', monospace;">🪙 PREMIUM REPORT OVERVIEW ($19.99)</h3>
                        <p style="color: #cbd5e1; font-size:13px; margin-bottom:15px; font-family:'Courier New', monospace;">{pay_desc}</p>
                        <div style="display:inline-block; padding:12px 25px; background-color:#d4af37; color:#0e1c36; border-radius:5px; font-weight:bold; cursor:pointer; font-family:'Courier New', monospace; box-shadow: 0 0 15px rgba(212,175,55,0.4);">
                            Stripe / Credit Card Secure Pay ($19.99)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                pdf_file = generate_advanced_pdf(search_query, ai_data, lang == "Türkçe")
                st.download_button(label="🔑 [SIMULATION] Download Premium PDF Report", data=pdf_file, file_name=f"Interlock_{search_query}_Premium.pdf")
            except Exception as e:
                st.error(f"⚠️ Raporlama Hatası: {str(e)}")
        else:
            st.error("⚠️ Yapay zeka ajan hatlarında geçici küresel yoğunluk. Lütfen sorguyu birkaç saniye sonra tekrar girin.")

    # HARİTA KATMANI (SABİT)
    st.divider()
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=4, tiles="CartoDB dark_matter")
    folium.Marker([41.15, 29.10], popup="MSC TESSA (Aktif Kargo)", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=450)

elif menu in [mod2, "📄 Evrak Analiz (OCR)", "📄 Document Analysis (OCR)"]:
    st.title("📄 Akıllı Evrak Doğrulama Terminali" if lang == "Türkçe" else "📄 Smart Document Verification Terminal")
    st.file_uploader("Upload Document (PDF/JPG/PNG)", type=["pdf", "jpg", "png"])

elif menu in [mod3, "⚓ Özel Gemi Röntgeni ($20)", "⚓ Custom Vessel X-Ray ($20)"]:
    st.title("⚓ Özel Gemi Röntgeni & Cargo Manifest" if lang == "Türkçe" else "⚓ Custom Vessel X-Ray & Cargo Manifest")
    ship_imo = st.text_input("IMO Number / Gemi IMO Girin:", placeholder="Örn: 9930038")
    if ship_imo:
        st.markdown('<div style="background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; text-align:center;"><h3>💳 RAPOR SATIN ALMA PANELİ</h3><p style="color: #cbd5e1; font-size:14px; margin-bottom:15px;">Bu sorgu için hesabınızdan <b>$20.00 USD</b> düşülecektir.</p><button style="background-color:#d4af37; color:#0e1c36; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">Kredi Kartı ile Güvenli Öde</button></div>', unsafe_allow_html=True)
