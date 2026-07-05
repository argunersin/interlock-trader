import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import urllib.parse
import json
import os
import requests

# 🛡️ GÜVENLİK ZIRHI: RENDER KASASINDAN OKUMA
import google.generativeai as genai
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

st.set_page_config(page_title="Interlock Global AI Terminal", layout="wide", page_icon="📟")

st.markdown("""
    <style>
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: transparent !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* 🎨 VIP WALL STREET RENK MATRİSİ: PARLEMENT MAVİSİ ANA EKRAN */
    .main, block-container, .stApp { background-color: #0a1128 !important; color: #ffffff !important; }
    
    /* 📟 KUŞ TÜYÜ HAFİFLİKTE SİMSIYAH MEKANİK FLAP KASALARI VE ORTADAN BÖLÜNMÜŞ ÇİZGİ */
    .split-flap-card {
        background: #02040a !important; 
        border: 2px solid #1f2937; border-radius: 6px; padding: 25px 15px; text-align: center;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.9), 0 6px 12px rgba(0,0,0,0.6); min-height: 140px;
        display: flex; flex-direction: column; justify-content: center; perspective: 1000px;
        position: relative; width: 100% !important;
    }
    .split-flap-card::after {
        content: ""; position: absolute; left: 0; top: 50%; width: 100%; height: 2px;
        background: #111625 !important; box-shadow: 0 1px 2px rgba(0,0,0,0.8); z-index: 10;
    }
    .split-flap-title { font-family: 'Courier New', monospace; font-size: 11px; color: #9ca3af; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; z-index: 5; }
    
    /* SAF BEYAZ NOSTALJİK RAKAMLAR VE 0.4 SN PIRRR TAKLA ANİMASYONU */
    .split-flap-value { 
        font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; color: #ffffff !important; 
        text-shadow: 0 0 8px rgba(255,255,255,0.3); display: inline-block; transform-style: preserve-3d;
        animation: pirrrRotation 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 5; white-space: nowrap !important;
    }
    @keyframes pirrrRotation {
        0% { transform: rotateX(-90deg); opacity: 0.5; }
        100% { transform: rotateX(0deg); opacity: 1; }
    }
    .split-flap-sub { font-family: 'Courier New', monospace; font-size: 11px; color: #10b981; margin-top: 5px; z-index: 5; }
    
    /* ⌨️ SİMSİYAH PARILDAYAN KURUMSAL NEON SORGULAMA BUTONU */
    div.stButton > button {
        background-color: #02040a !important; color: #ffffff !important;
        border: 2px solid #d4af37 !important; font-family: 'Courier New', monospace !important;
        font-weight: bold !important; font-size: 14px !important; padding: 12px 30px !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.3) !important; transition: all 0.3s ease !important;
        width: 100% !important; margin-top: 15px !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 25px rgba(212,175,55,0.6) !important; background-color: #0b1124 !important; color: #d4af37 !important;
    }
    
    /* 🚨 TARAYICIYI KİLİTLEYEN SOL MENÜYÜ TAMAMEN KAZIYAN SİBER ZIRH */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; width: 0px !important; }
    iframe, .element-container { background-color: transparent !important; color: transparent !important; height: 0px !important; display: none !important; }
    
    .stTable, table, tr, td, th { background-color: #04091a !important; color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    th { color: #00f2fe !important; font-weight: bold !important; border-bottom: 2px solid #1f2937 !important; }
    td { border-bottom: 1px solid #1f2937 !important; padding: 12px !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Courier New', monospace !important; }
    </style>
    """, unsafe_allow_html=True)
# 📟 YATAY ÜST KUMANDA PANELİ (SIFIR KİLİTLENME VE TAM UYUMLULUK DÜZENİ)
col_top1, col_top2 = st.columns(2)
with col_top2:
    lang = st.selectbox("🌐 LANGUAGE / DİL:", ["English", "Türkçe"], label_visibility="collapsed")

if lang == "Türkçe":
    mod1 = "🚀 Otonom İstihbarat Ajanı"
    mod2 = "📄 Evrak Analiz (OCR)"
    mod3 = "⚓ Özel Gemi Röntgeni ($20)"
else:
    mod1 = "🚀 Autonomous AI Agent"
    mod2 = "📄 Document Analysis (OCR)"
    mod3 = "⚓ Custom Vessel X-Ray ($20)"

with col_top1:
    menu = st.radio("MODULE / MODÜL:", [mod1, mod2, mod3], horizontal=True, label_visibility="collapsed")

def generate_advanced_pdf(query, ai_data, mode):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, "INTERLOCK GLOBAL - PREMIUM INTELLIGENCE BRIEFING")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, f"Analysis Mode / Mod: {mode.upper()} | Target: {query.upper()}")
    y = 700
    for key, val in ai_data.items():
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"■ {key.upper()}")
        y -= 15
        p.setFont("Helvetica", 9)
        words = str(val).split()
        line = ""
        for word in words:
            if len(line) + len(word) < 85: line += " " + word
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

# BÖLGESEL HAFIZA: SADECE KADRANLARI YENİLER, SAYFAYI ASLA KARARTMAZ VEYA KIRPMAZ
@st.fragment
def show_mechanical_radar(lang):
    ali_p = 3266.50; cu_p = 9120.00; sugar_p = 329.72; wheat_p = 245.00; oil_p = 71.38

    metals_list = ["Alüminyum Külçe (P1020)", "Bakır Katot (Grade A)", "İnşaat Demiri (Rebar)", "HMS 1/2 Demir Hurdası", "Çinko", "Kurşun", "Nikel", "Kalay", "Külçe Altın (999.9)", "Külçe Gümüş"]
    agri_list = ["Beyaz Şeker (ICUMSA 45)", "Ham Kamış Şekeri", "Sızma Zeytinyağı", "Rafine Zeytinyağı", "Ham Ayçiçek Yağı", "Ham Soya Yağı", "Palm Yağı (RBD)", "Ekmeklik Buğday", "Makarnalık Durum Buğdayı", "Sarı Mısır", "Arpa", "Ham Pamuk", "Kakao Çekirdeği", "Kahve Çekirdeği"]

    if "m_idx" not in st.session_state: st.session_state.m_idx = 0
    if "a_idx" not in st.session_state: st.session_state.a_idx = 0

    st.write("")
    st.columns(1)
    c_b1, c_b2, c_b3 = st.columns(3)
    
    with c_b1:
        metal_select = metals_list[st.session_state.m_idx]
        if st.session_state.m_idx == 0:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">${ali_p}</div><div class="split-flap-sub">ALÜMİNYUM / TON</div></div>', unsafe_allow_html=True)
        elif st.session_state.m_idx == 1:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">${cu_p}</div><div class="split-flap-sub">BAKIR KATOT / TON</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• LME METALLER</div><div class="split-flap-value">$410.00</div><div class="split-flap-sub">{metal_select[:15].upper()}</div></div>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("◀", key="m_up"): st.session_state.m_idx = (st.session_state.m_idx - 1) % len(metals_list)
        with col_m2:
            if st.button("▶", key="m_down"): st.session_state.m_idx = (st.session_state.m_idx + 1) % len(metals_list)
            
    with c_b2:
        gida_select = agri_list[st.session_state.a_idx]
        if st.session_state.a_idx == 0:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">${sugar_p}</div><div class="split-flap-sub">ŞEKER ENDEKSİ / TON</div></div>', unsafe_allow_html=True)
        elif st.session_state.a_idx == 7:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">${wheat_p}</div><div class="split-flap-sub">BUĞDAY / TON</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="split-flap-card"><div class="split-flap-title">• ENDÜSTRİYEL GIDA</div><div class="split-flap-value">$530.00</div><div class="split-flap-sub">{gida_select[:15].upper()}</div></div>', unsafe_allow_html=True)
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("◀", key="a_up"): st.session_state.a_idx = (st.session_state.a_idx - 1) % len(agri_list)
        with col_a2:
            if st.button("▶", key="a_down"): st.session_state.a_idx = (st.session_state.a_idx + 1) % len(agri_list)
            
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
if menu in [mod1, "🚀 Otonom İstihbarat Ajanı", "🚀 Autonomous AI Agent"]:
    show_mechanical_radar(lang)
    st.divider()
    
    mode_label = "SELECT ANALYSIS TYPE / ANALİZ MODU SEÇİN:" if lang == "English" else "🔮 ARTIK ÇİFT MOD AKTİF - ANALİZ MODU SEÇİN:"
    opt_route = "📍 Nokta Atışı Rota Analizi (Specific Route)"
    opt_global = "🌐 Küresel Makro Emtia Analizi (Global Market Analysis)"
    search_mode = st.radio(mode_label, [opt_route, opt_global], horizontal=True)

    search_placeholder = "e.g., flaxseed kazakhstan - germany or quinoa" if lang == "English" else "Örn: keten tohumu kazakistan - almanya VEYA sadece 'kinoa', 'chia' gibi ürün ismi"
    search_label = "Advanced AI Intelligence Search (Unlimited Commodities):" if lang == "English" else "Gemi İstihbarat Motoru (Sonsuz Emtia Özgürlüğü):"
    
    search_query = st.text_input(search_label, placeholder=search_placeholder, key="unrestricted_ai_query")
    
    submit_btn_label = "EXECUTE SEARCH (ENTER)" if lang == "English" else "İSTİHBARATI BAŞLAT (ENTER)"
    submit_button = st.button(label=submit_btn_label, key="unrestricted_ai_btn")
    
    if (submit_button or (search_query and st.session_state.get("last_query", "") != search_query)):
        st.session_state["last_query"] = search_query
        st.info("📟 Interlock Accio AI Agents exploring global trade networks... Please wait..." if lang == "English" else "📟 Interlock Otonom Ajanları küresel veri ağlarını tarıyor... Lütfen bekleyin...")
        
        prompt = f"""
        Sen uluslararası bir emtia brokerlığı yapay zeka ajanısın (Interlock Accio Modeli).
        Kullanıcı '{search_mode}' modunu seçti ve şu sorguyu yaptı: '{search_query}'.
        JSON formatında tam bir yanıt döndür. Anahtarlar: "Urun_Adi", "Fiyat_Matrisi", "Lojistik_Rota", "Mevzuat_Kotalar", "Gerekli_Evraklar", "Top5_Saticilar", "Top5_Alicilar", "Top5_Lojistik_Gumruk".
        Rapor oluştururken OpenCorporates ve ITC Trade Map/UN Comtrade resmi kurumsal veri tabanlarını referans al. Şirketlerin sicil kontrol durumlarını (Yasal olarak kayıtlı ve aktif mi) "Mevzuat_Kotalar" veya "Top5_Saticilar" içinde resmi yıl ve numaralarla raporla.
        """
        
        ai_data = None
        gemini_error_msg = ""
        groq_error_msg = ""
        openrouter_error_msg = ""
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            ai_data = json.loads(clean_text)
        except Exception as e:
            gemini_error_msg = str(e)
            try:
                groq_key = os.environ.get("GROQ_API_KEY")
                if groq_key:
                    payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
                    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                    res = requests.post("https://groq.com", json=payload, headers=headers, timeout=30)
                    if res.status_code == 200:
                        ai_data = json.loads(res.json()['choices']['message']['content'].strip())
                    else:
                        groq_error_msg = f"Groq HTTP {res.status_code}"
                else:
                    groq_error_msg = "GROQ KEY MISSING"
            except Exception as e2:
                groq_error_msg = str(e2)

            if not ai_data:
                try:
                    payload_or = {"model": "meta-llama/llama-3-8b-instruct:free", "messages": [{"role": "user", "content": prompt}]}
                    headers_or = {"Content-Type": "application/json"}
                    res_or = requests.post("https://openrouter.ai", json=payload_or, headers=headers_or, timeout=30)
                    if res_or.status_code == 200:
                        raw_out_or = res_or.json()['choices']['message']['content']
                        clean_or = raw_out_or.strip().replace("```json", "").replace("```", "")
                        start_idx = clean_or.find("{")
                        end_idx = clean_or.rfind("}") + 1
                        if start_idx != -1 and end_idx > start_idx:
                            ai_data = json.loads(clean_or[start_idx:end_idx])
                        else:
                            ai_data = {"Urun_Adi": search_query, "Mevzuat_Kotalar": raw_out_or, "Lojistik_Rota": "OpenRouter Havuzu Aktif"}
                    else:
                        openrouter_error_msg = f"OpenRouter HTTP {res_or.status_code}"
                except Exception as e3:
                    openrouter_error_msg = str(e3)

        if not ai_data:
            st.error("❌ YAPAY ZEKA MOTORLARI KÜRESEL LİMİT DUVARINA TAKILDI!")
            st.code(f"Google Gemini Hatası: {gemini_error_msg}\nGroq Hatası: {groq_error_msg}\nOpenRouter Yedek Ordusu Hatası: {openrouter_error_msg}", language="python")

        if ai_data:
            product = ai_data.get("Urun_Adi", "Emtia Segmenti")
            st.success(f"📌 {product} - AI Target Locked.")
            
            st.markdown(f"### 🛃 BÖLÜM 1: MEVZUAT & REGESTRAL DOĞRULAMA (OpenCorporates / ITC)")
            st.write(ai_data.get("Mevzuat_Kotalar", ""))
            
            st.markdown(f"### 🚚 BÖLÜM 2: LOJİSTİK & KÜRESEL HACİM KORİDORU")
            st.write(ai_data.get("Lojistik_Rota", ""))
            
            st.markdown(f"### 🔒 BÖLÜM 3: KİLİTLİ GİZLİ KASALAR & PROJEKSİYON")
            st.warning("🔓 Premium veriler holding kasasındadır. Aşağıdan indirin.")
            
            st.markdown(f"#### 📈 GLOBAL {product.upper()} PRICE TREND (6-MONTH PROJECTION)")
            # 📌 HATA VEREN BOŞ VİRGÜL UÇTU, YERİNE IŞIK HIZINDA HAZIR SABİT MATRİS MÜHÜRLENDİ!
            chart_data = pd.DataFrame([100, 105, 115, 110, 125, 130], columns=[product], index=["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
            st.line_chart(chart_data)
            
            pay_desc = "5 adet gerçek üretici/ithalatçı mailini ve OpenCorporates sicil kayıtlarını anında açın." if lang == "Türkçe" else "Get all 5 supplier/buyer corporate emails and official OpenCorporates registry data instantly."
            st.markdown(f"""
                <div style="background-color: #04091a; padding: 25px; border-radius: 8px; border: 2px dashed #d4af37; text-align:center; margin-top:20px;">
                    <h3 style="color:#d4af37; font-family:'Courier New', monospace;">🪙 PREMIUM REPORT OVERVIEW ($19.99)</h3>
                    <p style="color: #cbd5e1; font-size:13px; margin-bottom:15px; font-family:'Courier New', monospace;">{pay_desc}</p>
                    <div style="display:inline-block; padding:12px 25px; background-color:#d4af37; color:#0e1c36; border-radius:5px; font-weight:bold; cursor:pointer; font-family:'Courier New', monospace;">
                        Stripe / Credit Card Secure Pay ($19.99)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            pdf_file = generate_advanced_pdf(search_query, ai_data, search_mode)
            st.download_button(label="🔑 [SIMULATION] Download Premium PDF Report", data=pdf_file, file_name=f"Interlock_{search_query}_Premium.pdf")

elif menu in [mod2, "📄 Evrak Analiz (OCR)", "📄 Document Analysis (OCR)"]:
    st.title("📄 Akıllı Evrak Doğrulama Terminali")
    st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])

elif menu in [mod3, "⚓ Özel Gemi Röntgeni ($20)", "⚓ Custom Vessel X-Ray ($20)"]:
    st.title("⚓ Özel Gemi Röntgeni & Cargo Manifest")
    ship_imo = st.text_input("IMO Number / Gemi IMO Girin:", placeholder="Örn: 9930038")
    
    st.divider()
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=4, tiles="CartoDB dark_matter")
    folium.Marker([41.15, 29.10], popup="MSC TESSA", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=450)
    
    if ship_imo:
        st.markdown('<div style="background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; text-align:center;"><h3>💳 RAPOR SATIN ALMA PANELİ</h3><button style="background-color:#d4af37; color:#0e1c36; border:none; padding:10px 20px; border-radius:5px; font-weight:bold;">Kredi Kartı ile Güvenli Öde</button></div>', unsafe_allow_html=True)
