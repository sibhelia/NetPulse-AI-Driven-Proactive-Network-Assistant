from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import pandas as pd
import joblib
import os
import random
import time
import logging
from datetime import datetime
import llm_service, sms_sender
from lstm_service import (
    LSTMPredictionService,
    HybridEnsembleModel,
    PredictionResult
)
from status_tracker import StatusTracker
from background_monitor import BackgroundMonitor

logger = logging.getLogger(__name__)

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

# LSTM Model Paths
LSTM_MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'netpulse_lstm.h5')
LSTM_SCALER_PATH = os.path.join(BASE_DIR, 'saved_models', 'lstm_scaler.pkl')
LSTM_ENCODER_PATH = os.path.join(BASE_DIR, 'saved_models', 'lstm_encoder.pkl')

DB_CONFIG = {
    "dbname": "netpulse_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# Load Random Forest Model
model = None
try:
    model = joblib.load(MODEL_PATH)
    logger.info("✅ Random Forest model loaded")
except Exception as e:
    logger.warning(f"⚠️ Random Forest load failed: {e}")

# Initialize LSTM Service
lstm_service = LSTMPredictionService(
    LSTM_MODEL_PATH, LSTM_SCALER_PATH, LSTM_ENCODER_PATH
)

# Initialize Hybrid Ensemble Model
hybrid_model = HybridEnsembleModel(rf_weight=0.6, lstm_weight=0.4)

# Background Monitor (initialized at startup)
background_monitor = None

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
    return {
        "status": "active", 
        "mode": "Enterprise NOC",
        "lstm_available": lstm_service.is_available
    }

from pydantic import BaseModel
from typing import List, Optional

# --- Pydantic Models ---
class TicketRequest(BaseModel):
    subscriber_id: int
    technician_id: int
    issue_type: str
    notes: str

# --- YARDIMCI ENDPOINTLER ---

@app.get("/api/technicians")
def get_technicians():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, expertise, status FROM technicians")
    techs = cursor.fetchall()
    conn.close()
    return [{"id": t[0], "name": t[1], "expertise": t[2], "status": t[3]} for t in techs]

@app.post("/api/tickets")
def create_ticket(ticket: TicketRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (subscriber_id, technician_id, issue_type, status, notes)
        VALUES (%s, %s, %s, 'Open', %s) RETURNING ticket_id
    """, (ticket.subscriber_id, ticket.technician_id, ticket.issue_type, ticket.notes))
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"ticket_id": new_id, "status": "Created"}

@app.post("/api/actions/{action_type}")
def perform_action(action_type: str, subscriber_id: int = 0):
    # Simulate action
    time.sleep(1) # Fake delay
    return {"status": "Success", "message": f"{action_type} işlemi başarıyla tamamlandı."}

# --- 1. ENDPOINT: TEKİL ANALİZ (Gelişmiş) ---
@app.get("/api/simulate/{subscriber_id}")
def simulate_network(subscriber_id: int, force_trouble: bool = False):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Database fail")
    
    cursor = conn.cursor()
    # Fetch extended info
    cursor.execute("""
        SELECT full_name, subscription_plan, region_id, gender, phone_number, modem_model, ip_address, uptime 
        FROM customers WHERE subscriber_id = %s
    """, (subscriber_id,))
    customer = cursor.fetchone()
    
    if not customer: 
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    name, plan, region, gender, phone, modem, ip, uptime = customer
    
    # Fetch Recent Tickets
    cursor.execute("""
        SELECT t.created_at, t.issue_type, t.status, tech.name 
        FROM tickets t 
        LEFT JOIN technicians tech ON t.technician_id = tech.id
        WHERE t.subscriber_id = %s 
        ORDER BY t.created_at DESC LIMIT 5
    """, (subscriber_id,))
    history = cursor.fetchall()
    
    # Analyze Region Status (For Storytelling)
    # Count faulty users in same region
    cursor.execute("""
        SELECT COUNT(*) FROM customers c
        JOIN subscriber_status ss ON c.subscriber_id = ss.subscriber_id
        WHERE c.region_id = %s AND ss.current_status IN ('RED', 'YELLOW')
    """, (region,))
    region_fault_count = cursor.fetchone()[0]
    
    # Simulate Live Metrics
    # [NEW] SYNC WITH DB STATUS
    # List sayfasında ne görünüyorsa detayda da o görünmeli.
    cursor.execute("SELECT current_status FROM subscriber_status WHERE subscriber_id = %s", (subscriber_id,))
    row = cursor.fetchone()
    db_status = row[0] if row else None
    
    conn.close()

    # Eğer DB'de bir sorun kaydı varsa, simülasyonu ona göre zorla
    force_metrics_state = None
    if db_status == "RED" or db_status == "YELLOW":
        force_metrics_state = db_status

    live_data, fault_details, is_faulty = simulate_metrics_single(plan, force_trouble=(force_trouble or force_metrics_state is not None))
    
    # Override metrics if specific state needed to match DB
    if force_metrics_state == "RED":
        live_data["packet_loss"] = random.uniform(15, 40)
        live_data["download_speed"] = random.uniform(0.1, 3.0)
    elif force_metrics_state == "YELLOW":
        live_data["latency"] = random.uniform(90, 250)
        live_data["jitter"] = random.uniform(30, 80)
    
    # ... (Rest of AI logic same as before, condensed for brevity) ...
    # Re-implementing simplified AI logic just for this response to ensure flow consistency
    # In real file, we would keep the existing LSTM/RF logic. 
    # Since I'm replacing the whole function block, I need to include it or reference it.
    
    # Let's re-use the existing global objects: lstm_service, model, hybrid_model
    
    # 1. LSTM
    lstm_result = None
    if lstm_service and lstm_service.is_available:
        lstm_service.add_measurement(subscriber_id, live_data)
        lstm_result = lstm_service.predict(subscriber_id)
        
    # 2. RF
    prediction_code = 0
    rf_confidence = 0.5
    try:
        prediction_code = int(model.predict(pd.DataFrame([live_data]))[0]) if model else 0
    except: pass
    
    rf_result = PredictionResult("RandomForest", prediction_code, rf_confidence, [], datetime.now())
    
    # 3. Hybrid
    final_risk, segment_color, ensemble_reason = hybrid_model.combine_predictions(rf_result, lstm_result) if hybrid_model else (0, "GREEN", "System Log")
    
    # [KRITIK] DB'de kayıtlı durum varsa onu kullan (Liste ile senkronize olması için)
    # Liste sayfasında ne görünüyorsa detayda da o görünmeli
    if db_status and db_status in ["RED", "YELLOW", "GREEN"]:
        segment_color = db_status
        ensemble_reason = f"DB synchronized status ({db_status})"
    
    # --- DETAILED NARRATIVE ANALYSIS ---
    analysis_story = ""
    estimated_fix = "Belirsiz"
    
    if segment_color == "GREEN":
        analysis_story = f"{region} bölgesindeki altyapı analiz edildi ve tüm parametreler normal aralıkta tespit edildi. Hattınızda herhangi bir fiziksel veya yazılımsal sorun bulunmamaktadır. LSTM trend analizi ve Random Forest sınıflandırma modelleri de bağlantınızın stabil olduğunu doğruluyor. Sistem sürekli izleme altındadır."
        estimated_fix = "Gerekli değil"
    else:
        # Story logic
        if region_fault_count > 5:
            analysis_story = f"{region} bölgesinde kritik seviyede altyapı sorunu tespit edildi. Sorun sadece sizin hattınızda değil, bölge genelindeki {region_fault_count} aboneyi etkiliyor. Analiz sonuçları ana dağıtım noktasında (MDF/ODF) fiziksel veya konfigürasyon problemi olduğunu gösteriyor. Saha ekiplerimiz acil müdahale için görevlendirilmiştir. Fiber altyapı testi ve dağıtım noktası kontrolü yapılacaktır. Bu tür bölgesel arızalar genellikle 2-4 saat içinde çözülmektedir."
            estimated_fix = "2-4 Saat"
        else:
            # Determine specific issue type
            issue_type = "yüksek gecikme (latency)" if live_data['latency'] > 50 else "paket kaybı"
            issue_value = f"{live_data['latency']:.0f} ms" if live_data['latency'] > 50 else f"%{live_data.get('packet_loss', 0):.1f}"
            
            analysis_story = f"{region} bölgesinde yaygın bir sorun tespit edilmedi. Modem ({modem}, IP: {ip}) ile santral arasındaki sinyal kalitesinde degradasyon görülmektedir. Hat değerlerinizde anlık {issue_type} ({issue_value}) ölçülmüştür. Bölgede başka abone etkilenmediğinden, problem müşteri lokasyonu ile sınırlıdır. Saha teknisyeni göndererek iç tesisat kontrolü ve modem sinyal seviyesi ölçümü yaptırmanızı öneriyoruz. Gerekirse ekipman değişimi planlanabilir. Bu tür tekil hat arızalarının çözümü ortalama 45 dakika sürmektedir."
            estimated_fix = "45 Dakika"


    sms_info = {"sent": False, "message": None}

    return {
        "subscriber_id": subscriber_id,
        "customer_info": {
            "name": name, "plan": plan, "region": region, "phone": phone,
            "modem": modem, "ip": ip, "uptime": uptime
        },
        "live_metrics": live_data,
        "ai_analysis": {
            "segment": segment_color,
            "risk_score": final_risk,
            "reason": ensemble_reason,
            "story": analysis_story,
            "estimated_fix": estimated_fix
        },
        "history": [
            {"date": h[0].strftime("%d.%m.%Y %H:%M"), "event": h[1], "status": h[2], "tech": h[3]} 
            for h in history
        ],
        "sms_notification": sms_info
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
        
        # [NEW] DURUMU VERİTABANINA KAYDET (Senkronizasyon İçin)
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO subscriber_status (subscriber_id, current_status, last_checked)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (subscriber_id) 
                    DO UPDATE SET current_status = EXCLUDED.current_status, last_checked = NOW()
                """, (sub_id, color))
                conn.commit()
        except Exception as e:
            print(f"Status update error: {e}")
            conn.rollback()

        # İstatistiklere Ekle
        results["counts"][color] += 1
        
        # Listeye Ekle (ARTIK TÜM ABONELER EKLENİYOR)
        issue_text = "Stabil"
        if color == "YELLOW": issue_text = "Yüksek Ping"
        elif color == "RED": issue_text = "Bağlantı Kopuk"
        
        results["lists"][color].append({
            "id": sub_id,
            "name": name,
            "region": region, 
            "plan": plan,
            "issue": issue_text,
            "metrics": metrics
        })
    
    conn.close()
    return results


# --- 3. ENDPOINT: LSTM TREND ANALİZİ (YENİ!) ---
@app.get("/api/trend/{subscriber_id}")
def get_trend_analysis(subscriber_id: int):
    """
    LSTM-based trend analysis for proactive monitoring
    Returns detailed risk forecast and trend direction
    """
    if not lstm_service.is_available:
        raise HTTPException(
            status_code=503, 
            detail="LSTM service unavailable. Model not loaded."
        )
    
    # Get trend analysis
    trend = lstm_service.analyze_trend(subscriber_id)
    
    if not trend:
        # Not enough data yet
        cache_size = len(lstm_service.measurement_cache.get(subscriber_id, []))
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data for trend analysis. Have {cache_size}/12 measurements. Need 1 hour of data."
        )
    
    # Get customer info
    conn = get_db_connection()
    customer_name = "Unknown"
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM customers WHERE subscriber_id = %s", (subscriber_id,))
        result = cursor.fetchone()
        if result:
            customer_name = result[0]
        conn.close()
    
    return {
        "subscriber_id": subscriber_id,
        "customer_name": customer_name,
        "analysis": {
            "current_risk": round(trend.current_risk, 3),
            "trend_direction": trend.trend_direction,
            "forecast_30min": round(trend.forecast_30min, 3),
            "risk_chart": [round(r, 3) for r in trend.risk_chart],
            "recommendation": trend.recommendation,
            "severity": "HIGH" if trend.forecast_30min > 0.7 else ("MEDIUM" if trend.forecast_30min > 0.4 else "LOW")
        },
        "metadata": {
            "measurements_count": len(trend.risk_chart),
            "window_size": lstm_service.window_size,
            "model_status": "active",
            "model_name": "LSTM"
        }
    }
# === STARTUP & SHUTDOWN EVENTS ===

@app.on_event("startup")
async def startup_event():
    """
    Backend başlangıcında:
    1. Tüm 500 abone için LSTM cache oluştur (12 ölçüm)
    2. Otomatik periodic monitoring başlat (her 5 dakika)
    """
    global background_monitor
    
    logger.info("🚀 NetPulse Backend başlatılıyor...")
    
    if lstm_service and lstm_service.is_available:
        background_monitor = BackgroundMonitor(
            get_db_func=get_db_connection,
            lstm_service=lstm_service,
            simulate_func=simulate_metrics_single
        )
        
        await background_monitor.start()
        logger.info("✅ Background monitoring aktif! (500 abone)")
    else:
        logger.warning("⚠️ LSTM unavailable, background monitoring disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Backend kapatılırken monitoring durdur"""
    if background_monitor:
        background_monitor.stop()
    logger.info("👋 NetPulse Backend kapatıldı")
