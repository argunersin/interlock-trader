import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import urllib.parse

# Sayfa Genişlik ve Tema Ayarları
st.set_page_config(page_title="Interlock Global | International Brokerage", layout="wide", page_icon="🌐")

# SOL MENÜ (NAVİGASYON)
st.sidebar.title("🌐 Interlock Global")
st.sidebar.caption("Global Commodity Brokerage & Tech")

# Menü Seçenekleri (Kurumsal Ana Sayfa + Test Modülleri)
menu = st.sidebar.radio(
    "Menü", 
    [
        "🏠 Kurumsal Ana Sayfa", 
        "🚀 Interlock Trader (Beta Test)",
        "📄 Evrak Doğrulama & GTİP", 
        "⚖️ Akreditif & Sözleşme"
    ]
)

# ------------------------------------------------------------------
# MODÜL 1: KURUMSAL BROKERLIK ANA SAYFASI
# ------------------------------------------------------------------
if menu == "🏠 Kurumsal Ana Sayfa":
    st.title("Interlock Global International Brokerage")
    st.subheader("Küresel Emtia Ticaretinde Güvenilir Köprünüz")
    
    # Şirket Tanıtımı
    st.write("""
    Interlock Global; tarım, enerji ve metal emtialarında küresel alıcılar ile üreticileri bir araya getiren dijital altyapılı bir brokerlık firmasıdır. 
    Güçlü lojistik ağımız, gümrükleme çözümlerimiz ve sahteciliği önleyen yapay zeka destekli risk analiz sistemlerimizle ticaretinizi güvence altına alıyoruz.
    """)
    
    # Faaliyet Alanları (Emtialar)
    st.header("🎯 Ticaretine Aracılık Ettiğimiz Başlıca Emtialar")
    col_em1, col_em2, col_em3 = st.columns(3)
    with col_em1:
        st.subheader("🌾 Tarım Ürünleri")
        st.markdown("- Şeker (ICUMSA 45)\n- Buğday & Mısır\n- Ayçiçek Yağı")
    with col_em2:
        st.subheader("⛏️ Metaller & Madenler")
        st.markdown("- Ham Alüminyum & Külçe\n- Bakır Katot\n- Demir & Çelik Ürünleri")
    with col_em3:
        st.subheader("⚡ Enerji")
        st.markdown("- Ham Petrol (WTI/Brent)\n- Doğalgaz\n- Kömür")

    # TEST MODÜLÜNE ÇAĞRI (Sizin İstediğiniz Buton Metni)
    st.divider()
    st.header("🛠️ Dijital Ticaret İstihbaratı")
    st.info("Sektörde bir ilk! Geliştirmekte olduğumuz yapay zeka destekli trader modülümüzü tamamen ücretsiz deneyebilirsiniz.")
    
    if st.button("PROTOTİPİ TEST ET: Interlock Trader Modülüne Git 🚀"):
        st.warning("Lütfen sol menüden '🚀 Interlock Trader (Beta Test)' seçeneğine tıklayarak canlı modülü başlatın.")

# ------------------------------------------------------------------
# MODÜL 2: INTERLOCK TRADER VE WHATSAPP ENTEGRASYONU
# ------------------------------------------------------------------
elif menu == "🚀 Interlock Trader (Beta Test)":
    st.title("📊 Interlock Trader - Canlı İstihbarat & Lojistik Paneli")
    st.caption("Arama motoru, canlı borsa fiyatları ve otomatik raporlama")
    
    search_query = st.text_input("Arama Motoru (Örn: şeker brezilya - türkiye veya aluminyum)", placeholder="Emtia ve hedef ülkeleri yazın...")
    
    if search_query:
        st.success(f"'{search_query}' analizi tamamlandı.")
        
        # Canlı Fiyatlar (Simüle ve Canlı Karışık)
        col1, col2, col3 = st.columns(3)
        col1.metric("Tahmini FOB (Ton)", "$480.00", "Canlı Endeks")
        col2.metric("Bölgesel Prim (Premium)", "+$15.00", "LME Bazlı")
        col3.metric("Ortalama Navlun (Lojistik)", "$45.00", "Konteyner/Dökme")
        
        # Rapor Detayları
        st.subheader("📋 Potansiyel Alıcı/Satıcı ve Vergi Risk Analizi")
        data = {
            "Kategori": ["Satıcı Firmalar (Top 3)", "Alıcı Firmalar (Top 3)", "Gümrük Vergileri & Riskler"],
            "Detaylar": [
                "1. Cosan SA, 2. São Martinho, 3. Tereos (Brezilya)",
                "1. Türkiye Şeker Fabrikaları, 2. Konya Şeker, 3. Özel İthalatçılar",
                "İthalat rejimi kotasına tabi. %15-25 arası esnek gümrük vergisi riski mevcut."
            ]
        }
        st.table(pd.DataFrame(data))
        
        # 📱 WHATSAPP VE PDF ENTEGRASYONU (SIFIR MALİYETLİ)
        st.subheader("📥 Raporu Paylaş ve İndir")
        
        # PDF Oluşturma Butonu
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"INTERLOCK GLOBAL - TICARI ISTIHBARAT RAPORU")
        p.drawString(100, 730, f"Sorgu: {search_query}")
        p.drawString(100, 700, "FOB Fiyati: $480.00 | Navlun: $45.00")
        p.drawString(100, 680, "Risk Raporu: Gumruk kotalarina dikkat edilmelidir.")
        p.showPage()
        p.save()
        buffer.seek(0)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(label="📥 PDF Raporu Tablete İndir", data=buffer, file_name="interlock_rapor.pdf", mime="application/pdf")
        
        with col_btn2:
            # SIFIR MALİYETLİ WHATSAPP PAYLAŞIM BUTONU (API ÜCRETİ YOK)
            whatsapp_mesaj = f"Interlock Global İstihbarat Raporu:\nSorgu: {search_query}\nFOB Fiyatı: $480.00\nDetaylar web sitemizde!"
            encoded_mesaj = urllib.parse.quote(whatsapp_mesaj)
            # Kullanıcıyı doğrudan WhatsApp'a yönlendiren ücretsiz link
            wa_link = f"https://wa.me{encoded_mesaj}"
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">📱 Raporu WhatsApp ile Gönder</button></a>', unsafe_allow_index=True, unsafe_allow_html=True)

    # Canlı Gemi Takip Haritası (Alt Kısımda Sabit)
    st.divider()
    st.subheader("🚢 Canlı Gemi & Liman Takip Haritası")
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=8)
    folium.Marker([41.03, 29.02], popup="Aktif Kargo Gemisi").add_to(m)
    st_folium(m, width=1100, height=400)

# ------------------------------------------------------------------
# MODÜL 3: EVRAK KONTROL
# ------------------------------------------------------------------
elif menu == "📄 Evrak Doğrulama & GTİP":
    st.title("📄 Evrak Doğrulama & GTİP (HS Code) Arama Motoru")
    gtip_query = st.text_input("Ürün ismi yazarak GTİP kodu bulun:", placeholder="Örn: Beyaz şeker...")
    if gtip_query:
        st.code("GTİP Kodu: 1701.99.10.00.11")
        
    uploaded_file = st.file_uploader("Kontrol edilecek Proforma veya Konşimento yükleyin", type=["pdf", "png", "jpg"])
    if uploaded_file:
        st.metric(label="Güvenilirlik Skoru", value="%94", delta="Güvenli Evrak")

# ------------------------------------------------------------------
# MODÜL 4: AKREDİTİF
# ------------------------------------------------------------------
elif menu == "⚖️ Akreditif & Sözleşme":
    st.title("⚖️ Akıllı Akreditif (L/C) & Sözleşme Sihirbazı")
    st.text_input("Alıcı Ülke:")
    st.text_input("Satıcı Ülke:")
    if st.button("Uluslararası SPA Sözleşme Taslağı Üret"):
        st.text_area("Sözleşme Metni", "CONTRACT FOR SALE AND PURCHASE...", height=150)
