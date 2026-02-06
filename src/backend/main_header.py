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
INFRA_ENCODER_PATH = os.path.join(BASE_DIR, 'saved_models', 'infra_encoder.pkl')

# Database configuration
DB_NAME = "netpulse_db"
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

# Random Forest Model
model = None
try:
    model = joblib.load(MODEL_PATH)
    logger.info("✅ Random Forest model loaded")
except Exception as e:
    logger.warning(f"⚠️ Random Forest load failed: {e}")

# Initialize LSTM Service
lstm_service = LSTMPredictionService(
    LSTM_MODEL_PATH, LSTM_SCALER_PATH, INFRA_ENCODER_PATH
)

# Initialize Hybrid Ensemble Model
hybrid_model = HybridEnsembleModel()

# Background Monitor (initialized at startup)
background_monitor = None


# === Database Helper ===
def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT
        )
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        return None


# === Simulation Helper ===
def simulate_metrics_single(plan, force_trouble=False):
    """Simulates live network metrics for a given plan"""
    is_faulty = force_trouble or (random.random() < 0.15)
    
    if is_faulty:
        latency = random.uniform(100, 300)
        packet_loss = random.uniform(3, 15)
        download_speed = random.uniform(1, 15)
        jitter = random.uniform(25, 80)
        snr = random.uniform(2, 8)
        
        fault_types = ["Yüksek Ping", "Paket Kaybı", "Hızın Çok Düşmesi", "Sinyalin Zayıf Olması"]
        fault_details = {
            "cause": random.choice(fault_types),
            "eta": "2-4 saat",
            "action": "Alan ekibi yönlendirildi"
        }
    else:
        latency = random.uniform(10, 60)
        packet_loss = random.uniform(0, 2)
        download_speed = random.uniform(50, 120 if "Fiber" in plan else 80)
        jitter = random.uniform(1, 15)
        snr = random.uniform(12, 25)
        fault_details = None
    
    live_data = {
        "latency_ms": latency,
        "packet_loss_ratio": packet_loss,
        "snr_margin_db": snr,
        "download_usage_mbps": download_speed,
        # Legacy fields
        "latency": latency,
        "packet_loss": packet_loss,
        "download_speed": download_speed,
        "jitter": jitter,
        "infrastructure_type": "Fiber" if "Fiber" in plan else "VDSL"
    }
    
    return live_data, fault_details, is_faulty


# === Traffic Light Algorithm ===
def classify_subscriber_status(metrics, ai_prediction):
    if ai_prediction in [2, 3] or metrics['packet_loss'] > 5 or metrics['download_speed'] < 5:
        return "RED"
    if ai_prediction == 1 or metrics['latency'] > 80 or metrics['jitter'] > 30:
        return "YELLOW"
    return "GREEN"


# === STARTUP EVENT: Background Monitoring ===
@app.on_event("startup")
async def startup_event():
    """
    Backend başlatıldığında:
    1. Tüm aboneler için LSTM cache oluştur
    2. Periyodik monitoring başlat
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
        logger.info("✅ Background monitoring aktif!")
    else:
        logger.warning("⚠️ LSTM unavailable, background monitoring disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Backend kapatılırken monitoring durdur"""
    if background_monitor:
        background_monitor.stop()
    logger.info("👋 NetPulse Backend kapatıldı")


# === REST API ENDPOINTS ===
# (Mevcut endpoint'ler burada devam ediyor...)
