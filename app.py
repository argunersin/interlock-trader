import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Sayfa Genişlik Ayarları
st.set_page_config(page_title="Interlock Global AI", layout="wide", page_icon="🌐")

# Sol Menü (Navigasyon)
st.sidebar.image("https://placeholder.com", caption="Interlock Global") # Logonuz gelince değişecek
menu = st.sidebar.radio(
    "Gelişmiş Modüller", 
    ["📊 Akıllı Ticari İstihbarat", "🚢 IMO / Port Gemi Takibi", "📄 Evrak Sahtecilik & GTİP", "⚖️ Akreditif & Sözleşme"]
)

# MODÜL 1: TİCARİ İSTİHBARAT VE PDF RAPORLAMA
if menu == "📊 Akıllı Ticari İstihbarat":
    st.title("📊 Akıllı Ticari İstihbarat Motoru")
    st.caption("Emtia, Alıcı/Satıcı Ülke Analizi ve Anlık Maliyet Hesaplama")
    
    # Kullanıcının istediği komplike arama kutusu
    search_query = st.text_input("Arama Motoru (Örn: şeker brezilya - türkiye veya aluminyum)", placeholder="Emtia ve ülkeleri yazın...")
    
    if search_query:
        st.success(f"'{search_query}' analizi yapay zeka tarafından simüle ediliyor...")
        
        # Örnek Dinamik Veri Ekrana Basma
        col1, col2, col3 = st.columns(3)
        col1.metric("Tahmini FOB (Ton)", "$480.00", "Canlı Veri")
        col2.metric("Bölgesel Prim (Premium)", "+$15.00", "LME Bazlı")
        col3.metric("Ortalama Navlun (Lojistik)", "$45.00", "Konteyner/Dökme")
        
        # Detaylı Tablo
        st.subheader("📋 Potansiyel Alıcı/Satıcı ve Vergi Risk Analizi")
        data = {
            "Kategori": ["Satıcı Firmalar (Top 3)", "Alıcı Firmalar (Top 3)", "Gümrük Vergileri & Riskler"],
            "Detaylar": [
                "1. Cosan SA, 2. São Martinho, 3. Tereos (Brezilya yerel tedarikçileri)",
                "1. Türkiye Şeker Fabrikaları, 2. Konya Şeker, 3. Özel İthalatçılar",
                "İthalat rejimi kotasına tabi. %15-25 arası esnek gümrük vergisi riski mevcut."
            ]
        }
        st.table(pd.DataFrame(data))
        
        # PDF Çıktısı Alma Butonu
        st.subheader("📥 Kurumsal Rapor Oluşturma")
        if st.button("PDF Raporu İndir"):
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, f"INTERLOCK GLOBAL - TICARI ISTIHBARAT RAPORU")
            p.drawString(100, 730, f"Sorgu: {search_query}")
            p.drawString(100, 700, "FOB Fiyati: $480.00 | Navlun: $45.00")
            p.drawString(100, 680, "Risk Raporu: Gumruk kotalarina dikkat edilmelidir.")
            p.showPage()
            p.save()
            buffer.seek(0)
            st.download_button(label="📥 PDF'i Tablete İndir", data=buffer, file_name="interlock_rapor.pdf", mime="application/pdf")

# MODÜL 2: IMO VE PORT TABANLI HARİTA
elif menu == "🚢 IMO / Port Gemi Takibi":
    st.title("🚢 IMO & Port Odaklı Canlı Gemi Takibi")
    ship_search = st.text_input("Gemi Adı, IMO Numarası veya Liman (Port) Bilgisi Girin:", placeholder="Örn: 9411446 veya MSC TESSA")
    
    if ship_search:
        st.info(f"IMO/Gemi: {ship_search} için canlı koordinatlar aranıyor...")
        
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=8)
    folium.Marker([41.03, 29.02], popup="Aranan Gemi / Liman").add_to(m)
    st_folium(m, width=1100, height=500)

# MODÜL 3: EVRAK SAHTECİLİĞİ VE GTİP
elif menu == "📄 Evrak Sahtecilik & GTİP":
    st.title("📄 Evrak Doğrulama & GTİP (HS Code) Arama Motoru")
    
    st.subheader("🔍 1. Akıllı GTİP Arama")
    gtip_query = st.text_input("Ürün ismi yazarak GTİP kodu bulun:", placeholder="Örn: Beyaz şeker, ham alüminyum...")
    if gtip_query:
        st.code("GTİP Kodu: 1701.99.10.00.11 (Beyaz Şeker İçin Örnektir)")
        
    st.subheader("📸 2. Evrak Sahteciliği Kontrol Modülü")
    uploaded_file = st.file_uploader("Kontrol edilecek Proforma, SGS veya Konşimento (PDF/Görsel) yükleyin", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.warning("Yapay zeka evrak üzerindeki mühür, imza ve metin tutarlılığını inceliyor. (OCR Aktif Edilecek)")
        st.metric(label="Güvenilirlik Skoru", value="%94", delta="Güvenli Evrak")

# MODÜL 4: AKREDİTİF SİHİRBAZI
elif menu == "⚖️ Akreditif & Sözleşme":
    st.title("⚖️ Akıllı Akreditif (L/C) & Sözleşme Sihirbazı")
    st.caption("UCP 600 standartlarında uluslararası ticaret sözleşme taslakları")
    st.text_input("Alıcı Firma / Ülke:")
    st.text_input("Satıcı Firma / Ülke:")
    if st.button("Uluslararası SPA Sözleşme Taslağı Üret"):
        st.text_area("Sözleşme Metni", "CONTRACT FOR SALE AND PURCHASE OF COMMODITIES...\n\nArticle 1: Subject...", height=200)
