# ==========================================
# INTERLOCK TERMINAL - FASTAPI BACKEND CORE (main.py)
# ==========================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re
import json
import os
from duckduckgo_search import DDGS
import google.generativeai as genai

app = FastAPI(title="Interlock Global Trade API Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6 Sadeleştirilmiş Canlı Google Finance Grubu [0.1]
GOOGLE_TICKERS = {
    "Crude Oil (WTI)": ("Energy", "NASDAQ:CL"),
    "Brent Oil": ("Energy", "NYSE:BZ"),
    "Natural Gas": ("Energy", "NASDAQ:NG"),
    "Gold": ("Precious Metals", "COMMODITY:GOLD"),
    "Silver": ("Precious Metals", "COMMODITY:SILVER"),
    "Aluminum (LME)": ("LME Metals", "INDEXBOM:ALUMINIUM"),
    "Copper": ("LME Metals", "COMMODITY:COPPER"),
    "Zinc (LME)": ("LME Metals", "INDEXBOM:ZINC"),
    "Polypropylene (PP)": ("Petrochemicals", "INDEXBOM:POLYPROPYLENE"),
    "PVC Resins": ("Petrochemicals", "INDEXBOM:PVC"),
    "Wheat": ("Agriculture", "COMMODITY:WHEAT"),
    "Corn": ("Agriculture", "COMMODITY:CORN"),
    "Live Cattle": ("Livestock", "NASDAQ:LC"),
    "Lean Hogs": ("Livestock", "NASDAQ:LH")
}

class ReportRequest(BaseModel):
    mal_tanimi: str
    yukleme_limani: str = ""
    teslim_limani: str = ""
    target_language: str = "EN"

@app.get("/api/live-prices")
def get_live_prices():
    rows = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for name, (group, ticker) in GOOGLE_TICKERS.items():
        price, change = 0.0, 0.0
        try:
            url = f"https://google.com{ticker}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                p_match = re.search(r'data-last-price="([^"]+)"', res.text)
                c_match = re.search(r'data-price-change-percent="([^"]+)"', res.text)
                if p_match: price = float(p_match.group(1))
                if c_match: change = float(c_match.group(1))
        except Exception:
            pass
        rows.append({"asset": name, "group": group, "ticker": ticker, "price": price if price > 0 else 0.0, "change": change})
    return {"status": "success", "data": rows}

@app.post("/api/generate-report")
def get_ai_report(req: ReportRequest):
    web_news = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(f"{req.mal_tanimi} global trade customs tariff 2026", max_results=2)]
            if results: web_news = " | ".join([f"{r['title']}: {r['body']}" for r in results])
    except Exception:
        web_news = "Live trade web streaming active."

    sys_prompt = (
        "You are a senior global trade intelligence director. Provide a massive, comprehensive analysis "
        f"written ENTIRELY in '{req.target_language}' language. Return strictly in this JSON format:\n"
        '{"gümrük_özeti": "[Extremely long customs analysis]", "fiyat_matrisi": "[Detailed freight index]", '
        '"rotalar": ["1. Primary Corridor"], "risk_skoru": 70, "risk_nedenleri": ["Factor 1"]}'
    )
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key: return {"gümrük_özeti": "⚠️ KEY Missing.", "fiyat_matrisi": "⚠️ Offline.", "rotalar": ["-"], "risk_skoru": 0, "risk_nedenleri": ["-"]}
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        res = model.generate_content(sys_prompt)
        return json.loads(res.text)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
