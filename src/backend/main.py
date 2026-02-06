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
from src.backend import llm_service, sms_sender
from src.backend.lstm_service import (
    LSTMPredictionService,
    HybridEnsembleModel,
    PredictionResult
)
from src.backend.status_tracker import StatusTracker
from src.backend.background_monitor import BackgroundMonitor

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

# --- 1. ENDPOINT: TEKİL ANALİZ (Detay Sayfası İçin) - LSTM ENTEGRE ---
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
    
    # ===== HYBRID ENSEMBLE PREDICTION =====
    
    # 1. Add measurement to LSTM cache
    if lstm_service.is_available:
        lstm_service.add_measurement(subscriber_id, live_data)
        lstm_result = lstm_service.predict(subscriber_id)
    else:
        lstm_result = None
    
    # 2. Random Forest prediction
    prediction_code = 0
    rf_confidence = 0.5
    
    if model:
        try:
            prediction_code = int(model.predict(pd.DataFrame([live_data]))[0])
            rf_proba = model.predict_proba(pd.DataFrame([live_data]))
            rf_confidence = float(rf_proba.max())
        except:
            prediction_code = 0
    
    if is_faulty and prediction_code == 0:
        prediction_code = 1
    
    # Create RF result object
    rf_result = PredictionResult(
        model_name="RandomForest",
        prediction_class=prediction_code,
        confidence=rf_confidence,
        probabilities=[],
        timestamp=datetime.now()
    )
    
    # 3. Hybrid ensemble decision
    final_risk, segment_color, ensemble_reason = hybrid_model.combine_predictions(
        rf_result, lstm_result
    )
    
    # Override with old logic if needed (backward compatibility)
    if not lstm_service.is_available:
        segment_color = classify_subscriber_status(live_data, prediction_code)
        ensemble_reason = "LSTM unavailable, using RF only"
    
    status_text = "Normal" if segment_color == "GREEN" else "Risk/Arıza"
    
    # ===== LLM MESSAGE GENERATION =====
    llm_message = ""
    if segment_color in ["RED", "YELLOW"]:
        if not fault_details:
            fault_details = generate_fault_scenario("ping")
        llm_message = llm_service.generate_proactive_message(
            name, plan, fault_details, gender, severity=segment_color
        )
    else:
        llm_message = "Hizmet değerleri ideal seviyede."

    # ===== PROACTIVE SMS NOTIFICATION =====
    # Durum değişikliklerini track et ve SMS gönder
    conn_status = get_db_connection()
    sms_info = {"sent": False, "message": None}
    
    if conn_status:
        try:
            tracker = StatusTracker(conn_status)
            
            # Arıza türünü belirle
            fault_type = None
            if segment_color == "YELLOW":
                if live_data.get('latency', 0) > 80:
                    fault_type = "yüksek_ping"
                elif live_data.get('jitter', 0) > 30:
                    fault_type = "bağlantı_dalgalanması"
                else:
                    fault_type = "risk_tespit_edildi"
            elif segment_color == "RED":
                if live_data.get('packet_loss', 0) > 5:
                    fault_type = "paket_kaybı"
                elif live_data.get('download_speed', 100) < 5:
                    fault_type = "hız_düşüşü"
                else:
                    fault_type = "hat_arızası"
            
            # Durumu güncelle ve değişiklik var mı kontrol et
            change = tracker.update_status(
                subscriber_id,
                segment_color,
                fault_type=fault_type,
                estimated_fix_hours=2 if segment_color == "YELLOW" else 4
            )
            
            # Durum değişti ve SMS gönderilmeli mi?
            if change["should_send_sms"]:
                # Müşteri telefon numarasını al
                cursor = conn_status.cursor()
                cursor.execute(
                    "SELECT phone_number, full_name FROM customers WHERE subscriber_id = %s",
                    (subscriber_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    phone, cust_name = result
                    
                    # SMS mesajı oluştur
                    if segment_color in ["YELLOW", "RED"]:
                        # Arıza/Risk SMS'i - Gemini AI mesajını kullan
                        sms_message = llm_message
                    else:
                        # Düzelme SMS'i (Profesyonel format: Sayın Ad Soyad)
                        sms_message = f"Sayın {cust_name}, internet bağlantınız normale döndü. İyi kullanımlar! - NetPulse"
                    
                    # SMS gönder
                    success = sms_sender.send_sms(phone, sms_message)
                    
                    if success:
                        tracker.mark_sms_sent(subscriber_id)
                        sms_info = {
                            "sent": True,
                            "message": sms_message,
                            "transition": f"{change['old_status']} → {change['new_status']}",
                            "phone": phone
                        }
                        logger.info(f"📱 SMS gönderildi: {subscriber_id} ({change['old_status']} → {change['new_status']})")
            
            conn_status.close()
        
        except Exception as e:
            logger.error(f"Status tracking error: {e}")
            if conn_status:
                conn_status.close()

    return {
        "subscriber_id": subscriber_id,
        "customer_info": {"name": name, "plan": plan, "region": region, "gender": gender},
        "live_metrics": live_data,
        "ai_analysis": {
            # Snapshot (Random Forest)
            "snapshot": {
                "model": "RandomForest",
                "prediction": prediction_code,
                "confidence": rf_confidence,
                "status": "Normal" if prediction_code == 0 else "Anomaly"
            },
            # Trend (LSTM)
            "trend": {
                "model": "LSTM",
                "available": lstm_result is not None,
                "prediction": lstm_result.prediction_class if lstm_result else None,
                "confidence": lstm_result.confidence if lstm_result else None,
                "measurements_cached": len(lstm_service.measurement_cache.get(subscriber_id, [])) if lstm_service.is_available else 0
            },
            # Final Decision (Ensemble)
            "final_decision": {
                "risk_score": final_risk,
                "segment": segment_color,
                "reason": ensemble_reason,
                "explanation": llm_message
            },
            # Legacy fields (backward compatibility)
            "status_code": prediction_code,
            "status_text": status_text,
            "segment": segment_color,
            "explanation": llm_message,
            "fault_details": fault_details
        },
        "sms_notification": sms_info  # SMS gönderimi bilgisi
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
        
        # Listeye Ekle (ARTIK TÜM ABONELER EKLENİYOR)
        issue_text = "Stabil"
        if color == "YELLOW": issue_text = "Yüksek Ping"
        elif color == "RED": issue_text = "Bağlantı Kopuk"
        
        results["lists"][color].append({
            "id": sub_id,
            "name": name,
            "region": region,
            "issue": issue_text,
            "metrics": metrics
        })
            
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
