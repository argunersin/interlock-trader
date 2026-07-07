# ==========================================
# borsa_ekrani.py - 1. MODÜL (CANLI PİYASA & HESAP MAKİNESİ)
# ==========================================
import streamlit as st
import pandas as pd
import yfinance as yf

def render_borsa_ekrani(df_market):
    """
    Ana sayfada ilk açılan, 60 kalem canlı emtia matrisini 
    ve zengin döviz hesap makinesini çalıştıran bağımsız modül.
    """
    st.subheader("📈 Küresel Piyasa Fiyat Matrisi (60 Kalem Canlı Motor)")
    
    if not df_market.empty:
        # Kullanıcının gruplara göre filtreleme yapabilmesi için temiz arayüz
        available_groups = df_market["Grup"].unique()
        selected_group = st.selectbox("İncelemek İstediğiniz Sektörü Seçin:", available_groups, key="sector_select")
        
        filtered_df = df_market[df_market["Grup"] == selected_group].copy()
        
        # Gösterimi güzelleştirmek için renklendirilmiş veri tablosu
        def style_change(val):
            color = '#00ffcc' if val >= 0 else '#ff3366'
            return f'color: {color}; font-weight: bold;'

        styled_df = filtered_df.style.map(style_change, subset=['Günlük Değişim (%)']).format({
            'Son Fiyat': '{:,.2f}',
            'Günlük Değişim (%)': '{:+.2f}%'
        })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.error("Veri motoru şu anda yfinance servislerine bağlanamadı. Lütfen sayfayı yenileyiniz.")

    st.markdown("---")
    st.subheader("🧮 Çoklu Kur Ticaret Paneli & Döviz Hesap Makinesi")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        source_currency = st.selectbox("Kaynak Para Birimi / Emtia:", [
            "USD (Amerikan Doları)", "EUR (Euro)", "GBP (İngiliz Sterlini)", 
            "RUB (Rus Rublesi)", "CNY (Çin Yuanı)", "JPY (Japon Yeni)", 
            "CHF (İsviçre Frangı)", "TRY (Türk Lirası)"
        ], key="src_curr")
        amount = st.number_input("Çevrilmek İstenen Tutar:", min_value=0.0, value=1000.0, step=100.0, key="calc_amount")
        
    with col_calc2:
        target_currency = st.selectbox("Hedef Para Birimi / Emtia:", [
            "TRY (Türk Lirası)", "USD (Amerikan Doları)", "EUR (Euro)", 
            "GBP (İngiliz Sterlini)", "RUB (Rus Rublesi)", "CNY (Çin Yuanı)", 
            "JPY (Japon Yeni)", "CHF (İsviçre Frangı)"
        ], key="tgt_curr")
        
        src_code = source_currency.split(" ")[0]
        tgt_code = target_currency.split(" ")[0]
        
        calculated_result = amount 
        exchange_rate = 1.0
        
        if src_code != tgt_code:
            pair_ticker = f"{src_code}{tgt_code}=X"
            if src_code == "TRY": 
                pair_ticker = f"{tgt_code}{src_code}=X"
            
            try:
                rate_data = yf.Ticker(pair_ticker).history(period="1d")
                if not rate_data.empty:
                    exchange_rate = float(rate_data['Close'].iloc[-1])
                    if src_code == "TRY":
                        exchange_rate = 1.0 / exchange_rate
                    calculated_result = amount * exchange_rate
                else:
                    backup_rates = {"USDTRY": 34.50, "EURTRY": 36.20, "USDCNY": 7.25, "USDRUB": 98.0}
                    calculated_result = amount * backup_rates.get(f"{src_code}{tgt_code}", 1.0)
            except Exception:
                calculated_result = amount * 1.0
                
        st.metric(label="Hesaplanan Dönüşüm Tutarı", value=f"{calculated_result:,.2f} {tgt_code}")
        st.caption(f"Anlık Çevrim Katsayısı: 1 {src_code} = {exchange_rate:.4f} {tgt_code}")
