import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os
import sys

# ==========================================
# ⚙️ AYARLAR VE DOSYA YOLLARI
# ==========================================
# Kodun çalıştığı yere göre yolları dinamik bul
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Şu anki dosyanın yeri
PROJECT_ROOT = os.path.dirname(BASE_DIR)              # Proje ana klasörü

# Girdi: Ham Veri
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'netpulse_telemetry_final.csv')

# Çıktı: İşlenmiş Veriler ve Modeller
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'models', 'saved_objects')

# Klasörleri oluştur
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("🚀 Veri Önişleme (Preprocessing) Başlıyor...")
print(f"📂 Ham Veri: {RAW_DATA_PATH}")

# ==========================================
# 1. ADIM: VERİYİ YÜKLE
# ==========================================
try:
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"✅ Veri Yüklendi. Boyut: {df.shape}")
except FileNotFoundError:
    print("❌ HATA: Ham veri dosyası bulunamadı! Lütfen önce 'generate_data.py' çalıştırın.")
    sys.exit()

# ==========================================
# 2. ADIM: EĞİTİM VE TEST AYRIMI (SPLITTING)
# ==========================================
# Önemli Kural: Scaler ve Encoder'ı eğitmeden önce veriyi ayırmalıyız.
# Böylece Test setindeki bilgiler eğitim sürecine sızmaz (Data Leakage Önleme).

X = df.drop(columns=['root_cause', 'label', 'timestamp', 'subscriber_id', 'region_id']) # Girdiler
y = df['root_cause'] # Hedef (Çıktı)

# Stratify=y diyerek her arıza tipinden (y) eğitim ve test setine eşit oranda dağıtıyoruz.
print("✂️  Veri Eğitim (%80) ve Test (%20) olarak ayrılıyor...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ==========================================
# 3. ADIM: ENCODING (KATEGORİK -> SAYISAL)
# ==========================================
print("🔢 Kategorik veriler kodlanıyor...")

# infra_type sütununu (Fiber/VDSL) sayıya çevir
le_infra = LabelEncoder()

# Sadece train setindeki değerleri öğren (fit), sonra hem train hem test'i dönüştür (transform)
X_train['infra_type_encoded'] = le_infra.fit_transform(X_train['infra_type'])
X_test['infra_type_encoded'] = le_infra.transform(X_test['infra_type'])

# Artık string olan 'infra_type' sütununa ihtiyacımız yok
X_train = X_train.drop(columns=['infra_type'])
X_test = X_test.drop(columns=['infra_type'])

# Encoder'ı kaydet (API'de kullanacağız)
joblib.dump(le_infra, os.path.join(ARTIFACTS_DIR, 'infra_encoder.pkl'))

# ==========================================
# 4. ADIM: SCALING (STANDARTLAŞTIRMA)
# ==========================================
print("⚖️  Sayısal veriler ölçekleniyor (StandardScaler)...")

# Ölçeklenecek sütunlar (Tüm sayısal sütunlar)
numeric_cols = [
    'distance_to_cabinet_m', 'download_usage_mbps', 'upload_usage_mbps',
    'signal_strength_rssi', 'latency_ms', 'jitter_ms', 'packet_loss_ratio',
    'snr_margin_db', 'modem_cpu_usage', 'modem_ram_usage'
]

scaler = StandardScaler()

# Scaler'ı SADECE X_TRAIN üzerinde eğit (fit)
scaler.fit(X_train[numeric_cols])

# Öğrenilen ortalama ve sapmayı kullanarak hem Train hem Test'i dönüştür
X_train[numeric_cols] = scaler.transform(X_train[numeric_cols])
X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])

# Scaler'ı kaydet (Çok önemli!)
joblib.dump(scaler, os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))

# ==========================================
# 5. ADIM: İŞLENMİŞ VERİYİ BİRLEŞTİR VE KAYDET
# ==========================================
print("💾 İşlenmiş veriler kaydediliyor...")

# X ve y'yi tekrar birleştirip CSV olarak kaydedelim ki train.py kolayca okusun
train_df = pd.concat([X_train, y_train], axis=1)
test_df = pd.concat([X_test, y_test], axis=1)

train_path = os.path.join(PROCESSED_DATA_DIR, 'train_data.csv')
test_path = os.path.join(PROCESSED_DATA_DIR, 'test_data.csv')

train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print(f"✅ İŞLEM TAMAMLANDI!")
print(f"   Eğitim Seti: {train_path} ({train_df.shape})")
print(f"   Test Seti:   {test_path} ({test_df.shape})")
print(f"   Objeler:     {ARTIFACTS_DIR} klasörüne kaydedildi.")