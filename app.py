import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import urllib.parse

# 1. PREMIUM TASARIM VE TEMA AYARLARI
st.set_page_config(page_title="Interlock Global | Intelligence", layout="wide", page_icon="🌐")

# Şık CSS Kodları ile Tasarımı Özelleştirme
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.stButton > button:first-child { background-color: #0e1c36; color: white; border-radius: 5px; width: 100%; border: none; padding: 10px; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #1d3557; color: white; }
    h1, h2, h3 { color: #0e1c36; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# SOL MENÜ
st.sidebar.markdown("<h2 style='color: #1d3557; text-align: center;'>🌐 Interlock Global</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 12px; color: grey;'>Uluslararası Emtia Brokerlığı & Dijital İstihbarat</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio(
    "Gezinti Paneli", 
    ["🏠 Kurumsal Ana Sayfa", "🚀 Interlock Trader (Beta Test)", "📄 Evrak Doğrulama & GTİP", "⚖️ Akreditif & Sözleşme"]
)

# MODÜL 1: MODERN KURUMSAL ANA SAYFA
if menu == "🏠 Kurumsal Ana Sayfa":
    st.markdown("""
        <div style="background-color: #0e1c36; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; margin-bottom: 10px; font-size: 36px;">INTERLOCK GLOBAL</h1>
            <p style="color: #cbd5e1; font-size: 18px; max-width: 800px; margin: 0 auto;">
                Küresel emtia piyasalarında akıllı risk analizi, otonom lojistik takibi ve güvenli brokerlık çözümleri sunan dijital ticaret partneriniz.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    col_st1.metric("Küresel İş Ortağı", "45+", "Ülke Ağı")
    col_st2.metric("Yıllık Ticaret Hacmi", "$120M+", "Emtia")
    col_st3.metric("Lojistik Yönetimi", "180K+ Ton", "Dökme/Konteyner")
    col_st4.metric("Yapay Zeka Risk Skoru", "99.2%", "Güvenli İşlem")
    
    st.divider()
    st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>🎯 Ticaret Alanlarımız</h3>", unsafe_allow_html=True)
    col_em1, col_em2, col_em3 = st.columns(3)
    
    with col_em1:
        st.markdown('<div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #e63946; min-height: 180px;"><h4>🌾 Endüstriyel Tarım</h4><p style="font-size: 14px; color: #4a5568;"><b>Şeker:</b> ICUMSA 45 Brezilya menşeli dökme sevkiyatları.<br><b>Tahıl:</b> Buğday, Mısır ve Ayçiçek Yağı.</p></div>', unsafe_allow_html=True)
    with col_em2:
        st.markdown('<div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #457b9d; min-height: 180px;"><h4>⛏️ Metaller & Madenler</h4><p style="font-size: 14px; color: #4a5568;"><b>Alüminyum:</b> Kazakistan ve Hindistan menşeli Külçe P1020.<br><b>Bakır:</b> Katot bakır (Grade A).</p></div>', unsafe_allow_html=True)
    with col_em3:
        st.markdown('<div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #1d3557; min-height: 180px;"><h4>⚡ Enerji & Petrokimya</h4><p style="font-size: 14px; color: #4a5568;"><b>Akaryakıt:</b> EN590 Dizel ve Jet Yakıtı (A1).<br><b>Kömür:</b> Yüksek kalorili sanayi kömürü.</p></div>', unsafe_allow_html=True)

    st.divider()
    st.write("<p style='text-align: center;'>Geleneksel brokerlık süreçlerini yapay zeka istihbaratıyla birleştiriyoruz. Sol paneldeki 'Interlock Trader' modülünden test edebilirsiniz.</p>", unsafe_allow_html=True)
# MODÜL 2: GELİŞMİŞ VE DİNAMİK INTERLOCK TRADER
elif menu == "🚀 Interlock Trader (Beta Test)":
    st.title("📊 Akıllı Ticari İstihbarat & Lojistik Motoru")
    search_query = st.text_input("Arama Motoru:", placeholder="Örn: aluminyum kazakistan - türkiye veya şeker brezilya...")
    
    if search_query:
        query_lower = search_query.lower()
        
        if "aluminyum" in query_lower or "alüminyum" in query_lower:
            product = "Ham Alüminyum (Külçe / P1020)"
            fob = "$2,450.00"
            premium = "+$180.00 (Bölge Primi)"
            freight = "$95.00 (Demiryolu + Deniz)"
            gtip = "7601.10.00.00.00"
            suppliers = "1. Kazakistan Alüminyum (KCA), 2. ERG Group"
            buyers = "1. Assan Alüminyum, 2. Teknik Alüminyum"
            risks = "Hazar geçişli orta koridor yoğunluğu. LME stok seviyesi riskleri."
            lat, lon = 43.8240, 87.3554
            marker_text = "Alüminyum Sevkiyat Rota Başlangıcı"
            
        elif "şeker" in query_lower or "seker" in query_lower:
            product = "Rafine Beyaz Şeker (ICUMSA 45)"
            fob = "$520.00"
            premium = "+$15.00 (Sertifikasyon Primi)"
            freight = "$48.00 (Santos Port)"
            gtip = "1701.99.10.00.11"
            suppliers = "1. Cosan SA, 2. São Martinho, 3. Tereos"
            buyers = "1. Türkiye Şeker Fabrikaları, 2. Konya Şeker"
            risks = "Santos limanında sıra yoğunluğu (Demurrage riski). İthalat fon düzenlemeleri."
            lat, lon = -23.9535, -46.3015
            marker_text = "Santos Port - Yükleme Alanı"
            
        else:
            product = f"Emtia: {search_query.capitalize()}"
            fob = "$680.00"; premium = "+$25.00"; freight = "$55.00"; gtip = "Gözetim Belgesi Gerekli"
            suppliers = "Küresel Tedarikçi Veri Tabanı Taranıyor..."; buyers = "TR İthalatçı Listesi..."; risks = "Standart riskler."
            lat, lon = 41.0082, 28.9784; marker_text = "Interlock Global"

        st.success(f"📌 '{product}' için Analiz Raporu Hazırlandı.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tahmini FOB (Ton)", fob, "Güncel Borsa")
        col2.metric("Bölgesel Prim (Premium)", premium, "Pazar Bazlı")
        col3.metric("Ortalama Navlun", freight, "Maliyet")
        
        st.table(pd.DataFrame({"Kriter": ["GTİP Kodu", "Satıcılar", "Alıcılar (TR)", "Riskler"], "Veriler": [gtip, suppliers, buyers, risks]}))
        
        # PDF ve WhatsApp Entegrasyonu
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(50, 750, f"INTERLOCK GLOBAL REPORT - {search_query.upper()}")
        p.drawString(50, 720, f"Product: {product} | FOB: {fob} | Freight: {freight}")
        p.showPage(); p.save(); buffer.seek(0)
        
        c1, c2 = st.columns(2)
        c1.download_button(label="📥 PDF İndir", data=buffer, file_name="interlock.pdf", mime="application/pdf")
        
        whatsapp_mesaj = f"*Interlock Global*\n*Ürün:* {product}\n*FOB:* {fob}\n*Navlun:* {freight}"
        encoded_mesaj = urllib.parse.quote(whatsapp_mesaj)
        wa_link = f"https://wa.me{encoded_mesaj}"
        c2.markdown(f'<a href="{wa_link}" target="_blank"><div style="background-color:#25D366;color:white;text-align:center;padding:10px;border-radius:5px;font-weight:bold;cursor:pointer;">📱 WhatsApp Paylaş</div></a>', unsafe_allow_html=True)
    # HARİTA SİSTEMİ (Modül 2'nin Devamı)
    st.divider()
    st.subheader("🚢 IMO / Port Destekli Canlı Lojistik Haritası")
    map_lat = lat if search_query else 41.0082
    map_lon = lon if search_query else 28.9784
    m = folium.Map(location=[map_lat, map_lon], zoom_start=5 if search_query else 7, tiles="CartoDB positron")
    
    folium.Marker([40.98, 28.90], popup="Ambarlı Limanı (İstanbul)", icon=folium.Icon(color='darkblue', icon='anchor', prefix='fa')).add_to(m)
    folium.Marker([36.60, 36.16], popup="İskenderun Limanı", icon=folium.Icon(color='darkblue', icon='anchor', prefix='fa')).add_to(m)
    
    if search_query:
        folium.Marker([lat, lon], popup=marker_text, icon=folium.Icon(color='red', icon='ship', prefix='fa')).add_to(m)
        folium.PolyLine(locations=[[lat, lon], [40.98, 28.90]], color="red", weight=2.5).add_to(m)
    else:
        folium.Marker([41.15, 29.10], popup="MSC TESSA (IMO: 9930038)", icon=folium.Icon(color='green', icon='ship', prefix='fa')).add_to(m)
        folium.Marker([40.50, 27.50], popup="MV GALAXY (IMO: 9411446)", icon=folium.Icon(color='orange', icon='ship', prefix='fa')).add_to(m)
    st_folium(m, width=1100, height=400)

# MODÜL 3 & 4 (GELECEK PLANLAMASI)
elif menu == "📄 Evrak Doğrulama & GTİP":
    st.title("📄 Evrak Doğrulama & GTİP Arama Motoru")
    gtip_query = st.text_input("Ürün ismi yazın:")
    if gtip_query: st.code("GTİP Kodu: 1701.99.10.00.11 (Örnektir)")
    uploaded_file = st.file_uploader("Evrak Yükleyin", type=["pdf", "png", "jpg"])
    if uploaded_file: st.metric(label="Güvenilirlik Skoru", value="%94", delta="Güvenli")

elif menu == "⚖️ Akreditif & Sözleşme":
    st.title("⚖️ Akıllı Akreditif (L/C) & Sözleşme Sihirbazı")
    st.text_input("Alıcı Ülke:")
    st.text_input("Satıcı Ülke:")
    if st.button("Sözleşme Taslağı Üret"): st.text_area("Metin", "CONTRACT FOR SALE...", height=150)
