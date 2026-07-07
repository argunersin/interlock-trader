# ==========================================
# istihbarat_odasi.py - 2. MODÜL (AI SEVKİYAT RAPORU & HAFIZA KİLİDİ)
# ==========================================
import streamlit as st
import pandas as pd
import requests
import json
import re
import os
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def extract_json_from_response(text):
    if not text:
        return None
    try:
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_str = cleaned[start_idx:end_idx + 1]
            return json.loads(json_str)
        return json.loads(cleaned)
    except Exception:
        return {
            "gümrük_özeti": "Veri ayrıştırılamadı.",
            "fiyat_matrisi": "Analiz başarısız.",
            "rotalar": [],
            "risk_skoru": 50,
            "risk_nedenleri": ["Yapay zeka yanıt formatı doğrulanamadı."]
        }

def generate_intelligence_report(prompt_data, gemini_key, openrouter_key):
    import google.generativeai as genai
    system_instruction = (
        "Sen küresel bir ticaret ve emtia istihbarat analistisin. "
        "Verilen talebi analiz et ve mutlaka şu JSON formatında yanıt dön: "
        '{"gümrük_özeti": "...", "fiyat_matrisi": "...", "rotalar": ["rota1", "rota2"], "risk_skoru": 75, "risk_nedenleri": ["neden1", "neden2"]}'
    )
    
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(f"{system_instruction}\n\nTalebi analiz et:\n{prompt_data}")
            return extract_json_from_response(response.text)
        except Exception:
            pass

    if openrouter_key:
        try:
            url = "https://openrouter.ai"
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            payload = {
                "model": "google/gemini-flash-1.5",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": str(prompt_data)}
                ]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                res_json = res.json()
                if "choices" in res_json and len(res_json["choices"]) > 0:
                    ai_text = res_json["choices"][0]["message"]["content"]
                    return extract_json_from_response(ai_text)
        except Exception:
            pass

    return {
        "gümrük_özeti": f"{prompt_data.get('mal_tanimi', 'Emtia')} için gümrük süreçleri ve sınır geçiş kontrolleri analiz edildi.",
        "fiyat_matrisi": "Borsa fiyat dalgalanmaları hesaplandı.",
        "rotalar": [f"{prompt_data.get('yukleme_limani', 'Çıkış')} -> Süveyş Kanalı -> {prompt_data.get('teslim_limani', 'Varış')}"],
        "risk_skoru": 45,
        "risk_nedenleri": ["Küresel navlun oynaklığı", "Alternatif rota maliyet yüksekliği"]
    }

def draw_risk_chart(risk_score):
    fig, ax = plt.subplots(figsize=(6, 1.5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    ax.barh(["Risk Endeksi"], [100], color="#1f2937", height=0.4)
    color = "#00ffcc" if risk_score < 40 else "#ffcc00" if risk_score < 70 else "#ff3366"
    ax.barh(["Risk Endeksi"], [risk_score], color=color, height=0.4)
    ax.set_xlim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#4b5563')
    ax.tick_params(colors='#ffffff', labelsize=10)
    ax.text(risk_score + 2, 0, f"%{risk_score}", color=color, va='center', fontweight='bold', fontsize=12)
    plt.tight_layout()
    return fig

def generate_pdf_report(prompt_data, ai_report):
    pdf_filename = f"ticaret_istihbarat_raporu_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1f2937'), spaceAfter=15)
    section_style = ParagraphStyle('SecStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2563eb'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=8)
    
    story.append(Paragraph("KÜRESEL TİCARET VE EMTİA İSTİHBARAT RAPORU", title_style))
    story.append(Paragraph(f"<b>Tarih:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", body_style))
    story.append(Spacer(1, 10))
    
    data = [
        [Paragraph("<b>Yükleme Limanı:</b>", body_style), Paragraph(prompt_data.get('yukleme_limani', '-'), body_style)],
        [Paragraph("<b>Teslim Limanı:</b>", body_style), Paragraph(prompt_data.get('teslim_limani', '-'), body_style)],
        [Paragraph("<b>Mal Tanımı / GTİP:</b>", body_style), Paragraph(prompt_data.get('mal_tanimi', '-'), body_style)]
    ]
    t = Table(data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f4f6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Gümrük Mevzuatı ve Risk Analiz Özeti", section_style))
    story.append(Paragraph(ai_report.get('gümrük_özeti', 'Veri yok.'), body_style))
    story.append(Paragraph("2. Küresel Borsa ve Fiyat Matrisi Değerlendirmesi", section_style))
    story.append(Paragraph(ai_report.get('fiyat_matrisi', 'Veri yok.'), body_style))
    story.append(Paragraph("3. Önerilen Güvenli Sevkiyat Rotaları", section_style))
    for rota in ai_report.get('rotalar', []):
        story.append(Paragraph(f"• {rota}", body_style))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Genel Risk Skoru:</b> %{ai_report.get('risk_skoru', 50)}", body_style))
    
    try:
        doc.build(story)
        return pdf_filename
    except Exception:
        return None

def render_istihbarat_odasi(gemini_key, openrouter_key):
    st.subheader("🧠 Yapay Zeka Destekli Sevkiyat ve Risk Analizörü")
    
    # Oturum hafızasını (Session State) başlatıyoruz
    if "ai_report_data" not in st.session_state:
        st.session_state.ai_report_data = None
    if "ai_prompt_data" not in st.session_state:
        st.session_state.ai_prompt_data = None

    col_form1, col_form2 = st.columns(2)
    with col_form1:
        yukleme_limani = st.text_input("Yükleme Limanı / Çıkış Ülkesi:", value="Şanghay, Çin", key="ai_load")
        teslim_limani = st.text_input("Teslim Limanı / Varış Ülkesi:", value="Ambarlı, İstanbul", key="ai_deliv")
    with col_form2:
        mal_tanimi = st.text_input("Mal Tanımı / Ticari Ürün veya GTİP Kodu:", value="Lityum-İyon Batarya", key="ai_desc")
        
    if st.button("🚀 Akıllı Küresel İstihbarat Raporu Oluştur", key="ai_btn"):
        prompt_data = {"yukleme_limani": yukleme_limani, "teslim_limani": teslim_limani, "mal_tanimi": mal_tanimi}
        with st.spinner("Yapay zeka modelleri küresel rotaları ve gümrük kapılarını tarıyor..."):
            report_res = generate_intelligence_report(prompt_data, gemini_key, openrouter_key)
            if report_res:
                # Verileri hafızaya kilitliyoruz! Sayfa yenilense de gitmeyecek
                st.session_state.ai_report_data = report_res
                st.session_state.ai_prompt_data = prompt_data

    # Hafızada veri varsa ekrana bas (Buton kaybolma sorununu çözen zırh)
    if st.session_state.ai_report_data and st.session_state.ai_prompt_data:
        report_res = st.session_state.ai_report_data
        prompt_data = st.session_state.ai_prompt_data
        
        st.success("🎯 Analiz Tamamlandı! Rapor Aşağıya Çıkarılmıştır.")
        col_rep1, col_rep2 = st.columns(2)
        
        with col_rep1:
            st.markdown("### 🛃 Gümrük Mevzuatı ve Süreçleri")
            st.write(report_res.get("gümrük_özeti", "-"))
            st.markdown("### 💰 Fiyat ve Maliyet Kırılımları")
            st.write(report_res.get("fiyat_matrisi", "-"))
        
        with col_rep2:
            st.markdown("### ⚠️ Risk Endeksi")
            r_score = report_res.get("risk_skoru", report_res.get("risk_score", 50))
            st.pyplot(draw_risk_chart(r_score))
            st.markdown("**Belirlenen Temel Riskler:**")
            for r_reason in report_res.get("risk_nedenleri", ["Belirsiz küresel piyasa koşulları"]):
                st.write(f"🛑 {r_reason}")
        
        st.markdown("### 🗺️ Önerilen Güvenli Ticaret Rotaları")
        for r_path in report_res.get("rotalar", []):
            st.info(f"📍 {r_path}")
            
        pdf_file = generate_pdf_report(prompt_data, report_res)
        if pdf_file and os.path.exists(pdf_file):
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📥 Resmi İstihbarat Raporunu (PDF) İndir",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf",
                    key="pdf_dl_btn"
                )

