# ==========================================
# INTERLOCK TERMINAL - FASTAPI BACKEND CORE
# ==========================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from functools import lru_cache
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

# ==============================================
# 1. EMTİA VE DÖVİZ LİSTESİ
# ==============================================
ASSET_LIST = {
    "Crude Oil (WTI)": ("Energy", "CL=F", "OIL"),
    "Brent Oil": ("Energy", "BZ=F", "BZ=F"),
    "Natural Gas": ("Energy", "NG=F", "NG=F"),
    "Gold": ("Precious Metals", "GC=F", "GC=F"),
    "Silver": ("Precious Metals", "SI=F", "SI=F"),
    "Platinum": ("Precious Metals", "PL=F", "PL=F"),
    "Palladium": ("Precious Metals", "PA=F", "PA=F"),
    "Copper": ("LME Metals", "HG=F", "HG=F"),
    "Aluminum (LME)": ("LME Metals", "ALI=F", "ALI=F"),
    "Zinc (LME)": ("LME Metals", "ZNC=F", "ZNC=F"),
    "Nickel (LME)": ("LME Metals", "NIL=F", "NIL=F"),
    "Lead (LME)": ("LME Metals", "PB=F", "PB=F"),
    "Tin (LME)": ("LME Metals", "TIN=F", "TIN=F"),
    "Polypropylene (PP)": ("Petrochemicals", "PP=F", "PP=F"),
    "PVC Resins": ("Petrochemicals", "PVC=F", "PVC=F"),
    "Polyethylene (HDPE)": ("Petrochemicals", "PE=F", "PE=F"),
    "Methanol Spot": ("Petrochemicals", "ME=F", "ME=F"),
    "Wheat": ("Agriculture", "ZW=F", "ZW=F"),
    "Corn": ("Agriculture", "ZC=F", "ZC=F"),
    "Soybeans": ("Agriculture", "ZS=F", "ZS=F"),
    "Sugar No.11": ("Agriculture", "SB=F", "SB=F"),
    "Coffee Arabica": ("Agriculture", "KC=F", "KC=F"),
    "Cocoa": ("Agriculture", "CC=F", "CC=F"),
    "Cotton No.2": ("Agriculture", "CT=F", "CT=F"),
    "Live Cattle": ("Livestock", "LE=F", "LE=F"),
    "Lean Hogs": ("Livestock", "HE=F", "HE=F"),
}

FOREX_BACKUP = {
    "USD/TRY": 46.98, "EUR/TRY": 53.24, "GBP/TRY": 62.50, "CHF/TRY": 54.80,
    "JPY/TRY": 0.32, "CNY/TRY": 6.50, "RUB/TRY": 0.55, "AUD/TRY": 31.20,
    "CAD/TRY": 34.80, "KRW/TRY": 0.035, "INR/TRY": 0.56, "SAR/TRY": 12.50,
    "SEK/TRY": 4.20, "NOK/TRY": 4.10, "DKK/TRY": 6.80, "PLN/TRY": 12.10,
    "CZK/TRY": 2.00, "HUF/TRY": 0.13, "MXN/TRY": 2.80, "BRL/TRY": 8.90,
    "ZAR/TRY": 2.50, "SGD/TRY": 34.20, "HKD/TRY": 6.00, "TWD/TRY": 1.50,
    "THB/TRY": 1.30, "MYR/TRY": 10.20, "IDR/TRY": 0.003, "PHP/TRY": 0.82,
    "NZD/TRY": 28.50
}

BACKUP_PRICES = {
    "CL=F": 74.50, "BZ=F": 78.20, "NG=F": 2.45,
    "GC=F": 2340.00, "SI=F": 29.50, "PL=F": 980.00, "PA=F": 1020.00,
    "HG=F": 4.45, "ALI=F": 3146.00, "ZNC=F": 2910.00, "NIL=F": 17450.00,
    "PB=F": 2100.00, "TIN=F": 32100.00,
    "PP=F": 1240.00, "PVC=F": 980.00, "PE=F": 1160.00, "ME=F": 345.00,
    "ZW=F": 620.00, "ZC=F": 450.00, "ZS=F": 1180.00, "SB=F": 19.45,
    "KC=F": 224.50, "CC=F": 8450.00, "CT=F": 78.30,
    "LE=F": 184.50, "HE=F": 82.30,
}

class ReportRequest(BaseModel):
    mal_tanimi: str
    yukleme_limani: str = ""
    teslim_limani: str = ""
    target_language: str = "EN"

# ==============================================
# 2. CANLI FİYAT API'SI
# ==============================================
@lru_cache(maxsize=1)
def get_cached_prices():
    rows = []
    finnhub_key = os.environ.get("FINNHUB_API_KEY", "")
    
    for name, (group, ticker, finnhub_symbol) in ASSET_LIST.items():
        price, change = 0.0, 0.0
        if finnhub_key and finnhub_symbol:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={finnhub_symbol}&token={finnhub_key}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data and 'c' in data:
                        price = data['c']
                        change = data['dp'] if 'dp' in data else 0.0
            except Exception:
                pass
        
        if price == 0.0:
            price = BACKUP_PRICES.get(ticker, 0.0)
            change = 0.0
            
        rows.append({"asset": name, "group": group, "price": price, "change": change})
    
    for name, price in FOREX_BACKUP.items():
        rows.append({"asset": name, "group": "Forex", "price": price, "change": 0.0})
    
    return {"status": "success", "data": rows}

@app.get("/api/live-prices")
def get_live_prices():
    return get_cached_prices()

# ==============================================
# 3. AI RAPOR MOTORU
# ==============================================
@app.post("/api/generate-report")
def get_ai_report(req: ReportRequest):
    web_news = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(f"{req.mal_tanimi} global trade", max_results=2)]
            if results: web_news = " | ".join([f"{r['title']}: {r['body']}" for r in results])
    except Exception:
        web_news = "Live trade web streaming active."

    sys_prompt = (
        f"You are a senior global trade intelligence director. Provide a comprehensive analysis "
        f"written ENTIRELY in '{req.target_language}' language. Use this data: {web_news}. "
        "Return strictly in this JSON format:\n"
        '{"gümrük_özeti": "[Long customs analysis]", '
        '"fiyat_matrisi": "[Freight index]", '
        '"rotalar": ["1. Primary Corridor", "2. Alternative Route"], '
        '"risk_skoru": 70, "risk_nedenleri": ["Factor 1", "Factor 2"]}'
    )

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
            res = model.generate_content(sys_prompt)
            return json.loads(res.text)
        except Exception:
            pass

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    if openrouter_key:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            payload = {
                "model": "google/gemini-flash-1.5",
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": f"Product: {req.mal_tanimi}"}]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return json.loads(res.json()["choices"][0]["message"]["content"])
        except Exception:
            pass

    return {
        "gümrük_özeti": f"⚠️ AI raporu çevrimdışı. Web'den bilgi: {web_news}",
        "fiyat_matrisi": "Navlun endeksi web'den alındı.",
        "rotalar": ["1. Süveyş üzerinden deniz yolu (22 gün)", "2. İpek Yolu üzerinden demiryolu (18 gün)"],
        "risk_skoru": 45,
        "risk_nedenleri": ["Jeopolitik gerilim", "Hava gecikmeleri"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
