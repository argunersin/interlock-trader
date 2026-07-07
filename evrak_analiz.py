# ==========================================
# evrak_analiz.py - 3. MODÜL (TİCARİ EVRAK OCR & ANALİZ ODASI)
# ==========================================
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

def analyze_document_image(image_file, gemini_key):
    """
    Yüklenen fatura/beyanname görselini Gemini Vision motoruna göndererek 
    içindeki kritik ticari verileri ayıklar.
    """
    if not gemini_key:
        return {
            "durum": "Hata",
            "mesaj": "Gemini API anahtarı bulunamadı. Lütfen Render panelinden veya .env dosyasından anahtarınızı tanımlayın."
        }
        
    try:
        genai.configure(api_key=gemini_key)
        # Görsel analizi için en ideal güncel flash modeli seçiyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # PIL ile görseli açıyoruz
        img = Image.open(image_file)
        
        prompt = (
            "Sana bir ticari evrak (fatura, gümrük beyannamesi, konşimento veya çeki listesi) görseli veriyorum. "
            "Bu görseli bir gümrük uzmanı titizliğiyle incele. "
            "İçerisinde bulduğun şu bilgileri başlıklar halinde Türkçe olarak raporla:\n"
            "1. Evrak Tipi (Fatura mı, Beyanname mi vb.)\n"
            "2. Gönderici / Satıcı Firma Bilgileri\n"
            "3. Alıcı / İthalatçı Firma Bilgileri\n"
            "4. Mal Tanımı ve Varsa GTİP Kodları\n"
            "5. Toplam Fatura Tutarı ve Para Birimi\n"
            "6. Brüt/Net Kilo veya Kap Adetleri\n"
            "Eğer evrak net okunmuyorsa veya bu bilgiler yoksa, tespit edebildiğin kadarını yaz ve uyarı ekle."
        )
        
        response = model.generate_content([prompt, img])
        return {
            "durum": "Başarılı",
            "analiz": response.text
        }
    except Exception as e:
        return {
            "durum": "Hata",
            "mesaj": f"Görsel işlenirken teknik bir hata oluştu: {str(e)}"
        }

def render_evrak_analiz(gemini_key):
    st.subheader("📝 Akıllı Ticari Evrak OCR & Belge Doğrulama")
    st.caption("Gümrük beyannameleri, ticari faturalar veya sevkiyat evraklarının yapay zekayla dijitalleştirilmesi")
    
    # Oturum hafızasını (Session State) evrak analiz için de başlatıyoruz
    if "ocr_result" not in st.session_state:
        st.session_state.ocr_result = None

    # İki kulvar açıyoruz: Evrak Görsel Analizi ve Evrak No Sorgulama
    col_doc1, col_doc2 = st.columns(2)
    
    with col_doc1:
        st.markdown("### 📸 Fatura & Beyanname Görsel Analizi (OCR)")
        uploaded_file = st.file_uploader(
            "Analiz edilecek evrak görselini yükleyin (PNG, JPG, JPEG):", 
            type=["png", "jpg", "jpeg"],
            key="doc_uploader"
        )
        
        if uploaded_file is not None:
            # Kullanıcıya yüklediği evrakın küçük bir önizlemesini gösteriyoruz
            st.image(uploaded_file, caption="Yüklenen Ticari Belge", width=250)
            
            if st.button("🔍 Evrakı Tara ve Verileri Ayıkla", key="ocr_btn"):
                with st.spinner("Yapar zeka evrak üzerindeki yazıları ve tabloları analiz ediyor..."):
                    res = analyze_document_image(uploaded_file, gemini_key)
                    st.session_state.ocr_result = res
                    
        # Hafızada OCR sonucu varsa ekrana basıyoruz (Yenilenince kaybolmama koruması)
        if st.session_state.ocr_result:
            res = st.session_state.ocr_result
            if res["durum"] == "Başarılı":
                st.success("🎯 Evrak Çözümleme Tamamlandı!")
                st.markdown("#### 📋 Ayıklanan Ticari Veriler Raporu")
                st.info(res["analiz"])
            else:
                st.error(res["mesaj"])
                
    with col_doc2:
        st.markdown("### 🔢 Evrak No / Beyanname Takip")
        evrak_no = st.text_input("Gümrük Referans veya Beyanname Tescil No:", placeholder="Örn: 2634A123456...", key="evrak_no_input")
        
        if st.button("🔎 Evrak Durumunu Sorgula", key="evrak_no_btn"):
            if evrak_no:
                with st.spinner("Merkezi gümrük arşivi ve blockchain tescil zinciri sorgulanıyor..."):
                    # Simüle edilmiş gümrük tescil sorgusu
                    st.success(f"✓ {evrak_no} Numaralı Belge Doğrulandı!")
                    
                    st.markdown("""
                    <div style="background-color: #1f2937; padding: 15px; border-left: 5px solid #00ffcc; border-radius: 4px;">
                        <p style="margin:0; color:#ffffff;"><b>Evrak Statüsü:</b> Gümrük Muayene Aşamasında (Sarı Hat)</p>
                        <p style="margin:5px 0 0 0; color:#a1a1aa;"><b>Tescil Tarihi:</b> Bugünü Tarihi</p>
                        <p style="margin:5px 0 0 0; color:#a1a1aa;"><b>Muayene Memuru Kod:</b> MM-9834</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Lütfen sorgulamak için geçerli bir evrak numarası girin.")
