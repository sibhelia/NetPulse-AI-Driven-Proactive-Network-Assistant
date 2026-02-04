from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
import joblib
import os
import random
import time
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
    "password": "admin",
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

# --- YARDIMCI FONKSİYONLAR ---

def generate_fault_scenario(scenario_type):
    """Arıza türüne göre mantıklı bir SEBEP, AKSİYON ve SÜRE üretir."""
    if scenario_type == "ping":
        return {"cause": "Bölgesel veri trafiği yoğunluğu", "action": "Yük dengeleme aktif edildi", "eta": "30 dk"}
    elif scenario_type == "speed":
        return {"cause": "Ana fiber omurgada sinyal zayıflaması", "action": "Santral optimizasyonu başlatıldı", "eta": "1 saat"}
    elif scenario_type == "loss":
        return {"cause": "Saha dolabında donanım arızası", "action": "Saha ekibi yönlendirildi", "eta": "3 saat"}
    else:
        return {"cause": "Planlı bakım çalışması", "action": "Sistem güncelleniyor", "eta": "15 dk"}

def simulate_metrics_single(plan, force_trouble=False):
    """Tekil kullanıcı için detaylı simülasyon (Eski fonksiyonumuz)"""
    is_problem = random.random() < 0.2 or force_trouble
    
    metrics = {
        "latency": random.uniform(10, 50),
        "packet_loss": random.uniform(0, 0.05),
        "jitter": random.uniform(1, 10),
        "download_speed": 100.0,
        "upload_speed": 20.0,
        "signal_strength": random.uniform(-60, -30),
        "connected_devices": random.randint(1, 10)
    }
    
    fault_details = None

    if "1000" in plan: metrics["download_speed"] = random.uniform(800, 1000)
    elif "100" in plan: metrics["download_speed"] = random.uniform(80, 100)
    else: metrics["download_speed"] = random.uniform(20, 50)

    if is_problem:
        scenario_type = random.choice(["ping", "speed", "loss"])
        if force_trouble: scenario_type = "loss"
        
        if scenario_type == "ping":
            metrics["latency"] = random.uniform(150, 400)
            metrics["jitter"] = random.uniform(50, 150)
        elif scenario_type == "speed":
            metrics["download_speed"] = random.uniform(1, 10)
        elif scenario_type == "loss":
            metrics["packet_loss"] = random.uniform(10, 40)
            metrics["signal_strength"] = random.uniform(-90, -80)
            
        fault_details = generate_fault_scenario(scenario_type)

    return metrics, fault_details, is_problem

# --- YENİ EKLENEN KISIM: TRAFFIC LIGHT SEGMENTASYONU ---

def classify_subscriber_status(metrics, ai_prediction):
    """
    Traffic Light Algoritması:
    Ham verileri ve AI tahminini birleştirip RENK kararı verir.
    """
    # 1. Kırmızı Kuralı (Kritik)
    if ai_prediction in [2, 3] or metrics['packet_loss'] > 5 or metrics['download_speed'] < 5:
        return "RED"
    
    # 2. Sarı Kuralı (Riskli / Warning)
    # AI 'Normal' dese bile Ping yüksekse veya Hız dalgalıysa SARI yak.
    # Bu, "Kestirimci Bakım" (Predictive) özelliğidir.
    if metrics['latency'] > 80 or metrics['jitter'] > 30 or ai_prediction == 1:
        return "YELLOW"
    
    # 3. Yeşil Kuralı (Normal)
    return "GREEN"

@app.get("/")
def home():
    return {"status": "active", "mode": "Enterprise NOC"}

# --- 1. ENDPOINT: TEKİL ANALİZ (Detay Sayfası İçin) ---
@app.get("/api/simulate/{subscriber_id}")
def simulate_network(subscriber_id: int, force_trouble: bool = False):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Database fail")
    
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, subscription_plan, region_id, gender FROM customers WHERE subscriber_id = %s", (subscriber_id,))
    customer = cursor.fetchone()
    conn.close()

    if not customer: raise HTTPException(status_code=404, detail="User not found")

    name, plan, region, gender = customer
    live_data, fault_details, is_faulty = simulate_metrics_single(plan, force_trouble)
    
    prediction_code = 0
    status_text = "Normal"
    
    if model:
        try:
            prediction_code = int(model.predict(pd.DataFrame([live_data]))[0])
        except: prediction_code = 0

    if is_faulty and prediction_code == 0: prediction_code = 1
    
    # Renk Kodunu Belirle
    segment_color = classify_subscriber_status(live_data, prediction_code)

    llm_message = ""
    if segment_color in ["RED", "YELLOW"]:
        status_text = "Risk/Arıza"
        if not fault_details: fault_details = generate_fault_scenario("ping")
        llm_message = llm_service.generate_proactive_message(
            name, plan, fault_details, gender, severity=segment_color
        )
    else:
        llm_message = "Hizmet değerleri ideal seviyede."

    return {
        "subscriber_id": subscriber_id,
        "customer_info": {"name": name, "plan": plan, "region": region, "gender": gender},
        "live_metrics": live_data,
        "ai_analysis": {
            "status_code": prediction_code,
            "status_text": status_text,
            "segment": segment_color,  # Frontend'e rengi gönderiyoruz
            "explanation": llm_message,
            "fault_details": fault_details
        }
    }

# --- 2. ENDPOINT: TOPLU TARAMA (Dashboard İçin) ---
@app.get("/api/scan_network")
def scan_network_batch():
    """
    Tüm aboneleri (veya ilk 500'ü) tarar, anlık durumlarını simüle eder 
    ve gruplandırır.
    """
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Database fail")
    
    cursor = conn.cursor()
    # Performans için sadece gerekli kolonları çekiyoruz
    cursor.execute("SELECT subscriber_id, full_name, subscription_plan, region_id FROM customers LIMIT 500")
    customers = cursor.fetchall()
    conn.close()
    
    results = {
        "total": len(customers),
        "counts": {"GREEN": 0, "YELLOW": 0, "RED": 0},
        "lists": {"GREEN": [], "YELLOW": [], "RED": []}
    }
    
    # Toplu Simülasyon Döngüsü
    for cust in customers:
        sub_id, name, plan, region = cust
        
        # Gerçekçi Dağılım İçin Zar Atıyoruz:
        # %90 Yeşil, %7 Sarı, %3 Kırmızı
        rand_val = random.randint(0, 100)
        
        # Hızlı simülasyon (Tekil fonksiyondan daha basit veriler)
        metrics = {
            "latency": random.uniform(10, 40),
            "packet_loss": 0,
            "download_speed": 100,
            "jitter": random.uniform(1, 5)
        }
        
        ai_pred = 0
        
        # Kırmızı Durumu Simüle Et (%3)
        if rand_val > 97:
            metrics["packet_loss"] = random.uniform(10, 30)
            metrics["download_speed"] = 2.0
            ai_pred = 2
        # Sarı Durumu Simüle Et (%7)
        elif rand_val > 90:
            metrics["latency"] = random.uniform(90, 180) # Ping yükselmiş
            metrics["jitter"] = random.uniform(20, 50)
            ai_pred = 0 # AI henüz hata demiyor ama biz RISK görüyoruz
            
        # Segmentasyon Fonksiyonunu Çağır
        color = classify_subscriber_status(metrics, ai_pred)
        
        # İstatistiklere Ekle
        results["counts"][color] += 1
        
        # Eğer sorunluysa listeye detay ekle (Dashboard'da göstermek için)
        if color != "GREEN":
            results["lists"][color].append({
                "id": sub_id,
                "name": name,
                "region": region,
                "issue": "Yüksek Ping" if color == "YELLOW" else "Bağlantı Kopuk",
                "metrics": metrics
            })
            
    return results