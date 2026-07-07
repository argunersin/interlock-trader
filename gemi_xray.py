# ==========================================
# gemi_xray.py - 4. MODÜL (GEMI X-RAY & CANLI LOJİSTİK TAKİP)
# ==========================================
import streamlit as st
import folium
from streamlit_folium import st_folium

def render_gemi_xray():
    st.subheader("🚢 Gemi X-Ray & Canlı Konteyner Lojistik Takip")
    st.caption("Küresel deniz hatlarındaki gemilerin anlık takibi, rota anomalileri ve gümrük X-Ray risk analizleri")

    # Oturum hafızasını (Session State) lojistik sorgular için de başlatıyoruz
    if "gemi_sorgu_sonuc" not in st.session_state:
        st.session_state.gemi_sorgu_sonuc = None

    col_ship1, col_ship2 = st.columns(2)

    with col_ship1:
        st.markdown("### 🔍 Konteyner / Gemi Kimlik Sorgulama")
        search_type = st.radio("Sorgulama Türü:", ["Konteyner No (BIC Kodu)", "Gemi Adı / IMO Numarası"], key="ship_search_type")
        
        if search_type == "Konteyner No (BIC Kodu)":
            input_val = st.text_input("Konteyner Numarasını Girin:", value="MSCU3489210", placeholder="Örn: MSCU1234567...", key="ship_input_bic")
        else:
            input_val = st.text_input("Gemi Adı veya IMO No Girin:", value="MSC OSCAR (IMO: 9703318)", placeholder="Örn: OOCL Germany...", key="ship_input_imo")

        if st.button("🚢 Yükü ve Rotayı Canlı Takip Et", key="ship_track_btn"):
            with st.spinner("Küresel AIS uydu verileri ve liman tescil sistemleri taranıyor..."):
                # Simüle edilmiş canlı AIS takip verisi hafızaya kilitleniyor
                st.session_state.gemi_sorgu_sonuc = {
                    "hedef": input_val,
                    "gemi_adi": "MSC OSCAR" if "MSC" in input_val or "MSCU" in input_val else "GLOBAL TRADER",
                    "mevcut_konum": "Kızıldeniz Girişi (Babülmendep Açıkları)",
                    "hiz": "18.4 Knot",
                    "rota_durumu": "Normal Rota (Anomali Yok)",
                    "xray_statusu": "Yüksek Riskli Bölge - Süveyş Girişinde Detaylı X-Ray Taraması Gerekebilir"
                }

    with col_ship2:
        st.markdown("### 🛡️ Gümrük X-Ray Muayene İstihbaratı")
        if st.session_state.gemi_sorgu_sonuc:
            res = st.session_state.gemi_sorgu_sonuc
            st.success(f"🎯 {res['hedef']} Başarıyla Konumlandırıldı!")
            
            st.markdown(f"""
            <div style="background-color: #1f2937; padding: 15px; border-left: 5px solid #00ffcc; border-radius: 4px; margin-bottom: 15px;">
                <p style="margin:0; color:#ffffff;"><b>Takip Edilen Unsur:</b> {res['gemi_adi']}</p>
                <p style="margin:5px 0 0 0; color:#a1a1aa;"><b>Anlık Konum:</b> {res['mevcut_konum']}</p>
                <p style="margin:5px 0 0 0; color:#a1a1aa;"><b>Seyir Hızı:</b> {res['hiz']}</p>
                <p style="margin:5px 0 0 0; color:#a1a1aa;"><b>Rota Güvenliği:</b> {res['rota_durumu']}</p>
                <p style="margin:10px 0 0 0; color:#ffcc00;">⚠️ <b>X-Ray Risk Raporu:</b> {res['xray_statusu']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Canlı konum haritasını ve X-Ray istihbaratını görmek için sol taraftan sorgulama başlatın.")

    # Altta geniş interaktif harita görünümü
    st.markdown("### 🗺️ Küresel Lojistik Koridor ve Canlı Rota Görünümü")
    
    # Haritayı oluşturuyoruz
    m = folium.Map(location=[24.0, 54.0], zoom_start=3, tiles="CartoDB positron")
    
    # Şanghay - Süveyş - İstanbul rotasını çizen interaktif çizgi
    trade_route = [[31.23, 121.47], [1.35, 103.87], [12.78, 45.01], [30.60, 32.50], [40.97, 28.72]]
    folium.PolyLine(locations=trade_route, color="#2563eb", weight=4, opacity=0.8, tooltip="Planlanan Sevkiyat Rotası").add_to(m)
    
    # Eğer sorgu yapıldıysa haritaya anlık gemi konumu ve X-Ray noktası basılıyor
    if st.session_state.gemi_sorgu_sonuc:
        # Anlık gemi konumu (Babülmendep açıkları)
        folium.Marker(
            location=[12.78, 45.01],
            popup="<b>MSC OSCAR</b><br>Durum: Seyir Halinde<br>Hız: 18.4 Knot",
            icon=folium.Icon(color="blue", icon="ship", prefix="fa")
        ).add_to(m)
        
        # Süveyş Gümrük X-Ray Kontrol Noktası
        folium.Marker(
            location=[30.60, 32.50],
            popup="<b>Süveyş Kanalı X-Ray İstasyonu</b><br>Risk Skoru: Yüksek<br>Zorunlu Tarama Alanı",
            icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")
        ).add_to(m)
        
    st_folium(m, width="100%", height=450, key="gemi_xray_live_map")
