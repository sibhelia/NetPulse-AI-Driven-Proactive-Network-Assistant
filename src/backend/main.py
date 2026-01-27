from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
import joblib
import os
import random
from src.backend import llm_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'netpulse_classifier.pkl')

DB_CONFIG = {
    "dbname": "netpulse_db",
    "user": "postgres",
    "password": "admin", # Şifreni kontrol et
    "host": "localhost",
    "port": "5432"
}

model = None
try:
    model = joblib.load(MODEL_PATH)
except:
    pass

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except:
        return None

def simulate_metrics(plan):
    # Normal simülasyon (%30 ihtimal)
    is_problem = random.random() < 0.3
    
    metrics = {
        "latency": random.uniform(10, 50),
        "packet_loss": random.uniform(0, 1),
        "jitter": random.uniform(1, 10),
        "download_speed": 100.0,
        "upload_speed": 20.0,
        "signal_strength": random.uniform(-60, -30),
        "connected_devices": random.randint(1, 10)
    }

    if "1000" in plan:
        metrics["download_speed"] = random.uniform(800, 1000)
    elif "100" in plan:
        metrics["download_speed"] = random.uniform(80, 100)
    else:
        metrics["download_speed"] = random.uniform(20, 50)

    if is_problem:
        scenario = random.choice(["ping", "speed", "loss"])
        if scenario == "ping":
            metrics["latency"] = random.uniform(150, 500)
            metrics["jitter"] = random.uniform(50, 200)
        elif scenario == "speed":
            metrics["download_speed"] = random.uniform(1, 10)
        elif scenario == "loss":
            metrics["packet_loss"] = random.uniform(15, 50)
            metrics["signal_strength"] = random.uniform(-90, -80)

    return metrics

@app.get("/")
def home():
    return {"status": "active"}

# ÖNEMLİ KISIM: 'force_trouble' parametresi ekledik
@app.get("/api/simulate/{subscriber_id}")
def simulate_network(subscriber_id: int, force_trouble: bool = False):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, subscription_plan, region_id, gender FROM customers WHERE subscriber_id = %s", (subscriber_id,))
    customer = cursor.fetchone()
    conn.close()

    if not customer:
        raise HTTPException(status_code=404, detail="User not found")

    name, plan, region, gender = customer
    live_data = simulate_metrics(plan)
    
    prediction_code = 0
    
    # --- MODEL TAHMİNİ ---
    if model:
        try:
            df_pred = pd.DataFrame([live_data])
            prediction_code = int(model.predict(df_pred)[0])
        except:
            prediction_code = 0

    # --- HİLE MODU (Kesin Arıza Gösterir) Test İçin ---
    # Eğer linkin sonuna ?force_trouble=true yazarsak burası çalışır
    if force_trouble:
        live_data["latency"] = 450.5  # Pingi zorla yükselt
        live_data["jitter"] = 120.2
        prediction_code = 1           # Zorla 'Bölgesel Yoğunluk' hatası ver
    # ----------------------------------------

    llm_message = ""
    if prediction_code != 0:
        llm_message = llm_service.generate_explanation(prediction_code, name, plan, region, gender)
    else:
        llm_message = "Hizmet değerleri normal."

    return {
        "subscriber_id": subscriber_id,
        "customer_info": {
            "name": name,
            "gender": gender,
            "plan": plan,
            "region": region
        },
        "live_metrics": live_data,
        "ai_analysis": {
            "status_code": prediction_code,
            "status_text": "Risk" if prediction_code != 0 else "Normal",
            "explanation": llm_message
        }
    }