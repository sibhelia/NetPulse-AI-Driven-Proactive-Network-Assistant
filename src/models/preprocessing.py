import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os
import sys

# Dosya yollarini tanimla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'netpulse_telemetry_final.csv')
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'models', 'saved_objects')

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("Veri Onisleme Basliyor...")
print(f"Ham Veri: {RAW_DATA_PATH}")

# Veriyi yukle
try:
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Veri Yuklendi. Boyut: {df.shape}")
except FileNotFoundError:
    print("HATA: Ham veri dosyasi bulunamadi! Lutfen once 'generate_data.py' calistirin.")
    sys.exit()

# Egitim ve test ayirimi
X = df.drop(columns=['root_cause', 'label', 'timestamp', 'subscriber_id', 'region_id'])
y = df['root_cause']

print("Veri Egitim (%80) ve Test (%20) olarak ayriliyor...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Kategorik verileri kodla
print("Kategorik veriler kodlaniyor...")

le_infra = LabelEncoder()
X_train['infra_type_encoded'] = le_infra.fit_transform(X_train['infra_type'])
X_test['infra_type_encoded'] = le_infra.transform(X_test['infra_type'])

X_train = X_train.drop(columns=['infra_type'])
X_test = X_test.drop(columns=['infra_type'])

joblib.dump(le_infra, os.path.join(ARTIFACTS_DIR, 'infra_encoder.pkl'))

# Sayisal verileri olcekle
print("Sayisal veriler olcekleniyor (StandardScaler)...")

numeric_cols = [
    'distance_to_cabinet_m', 'download_usage_mbps', 'upload_usage_mbps',
    'signal_strength_rssi', 'latency_ms', 'jitter_ms', 'packet_loss_ratio',
    'snr_margin_db', 'modem_cpu_usage', 'modem_ram_usage'
]

scaler = StandardScaler()
scaler.fit(X_train[numeric_cols])

X_train[numeric_cols] = scaler.transform(X_train[numeric_cols])
X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])

joblib.dump(scaler, os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))

# Islenmis veriyi kaydet
print("Islenmis veriler kaydediliyor...")

train_df = pd.concat([X_train, y_train], axis=1)
test_df = pd.concat([X_test, y_test], axis=1)

train_path = os.path.join(PROCESSED_DATA_DIR, 'train_data.csv')
test_path = os.path.join(PROCESSED_DATA_DIR, 'test_data.csv')

train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print("ISLEM TAMAMLANDI!")
print(f"Egitim Seti: {train_path} ({train_df.shape})")
print(f"Test Seti: {test_path} ({test_df.shape})")
print(f"Objeler: {ARTIFACTS_DIR} klasorune kaydedildi.")