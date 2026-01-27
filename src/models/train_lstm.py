import pandas as pd
import numpy as np
import joblib
import os
# TensorFlow uyarılarını gizleyelim (Kafa karıştırmasın)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# --- AYARLAR ---
# Dosya yollarını dinamik bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'netpulse_telemetry_final.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'src', 'models', 'saved_objects')

# Klasör yoksa oluştur
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"🚀 LSTM (Zaman Serisi) Eğitimi Başlıyor...\n📂 Veri Yolu: {DATA_PATH}")

def train_lstm_model():
    # 1. VERİYİ YÜKLE
    if not os.path.exists(DATA_PATH):
        print("❌ HATA: CSV dosyası bulunamadı! Lütfen önce veri üretin.")
        return

    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp') # Zaman sırasına dizmek ŞART!

    # Sadece Region_1 verisini alalım (Eğitim net olsun)
    df_sample = df[df['region_id'] == 'Region_1'].copy()
    
    print(f"📊 Veri Hazır: {len(df_sample)} satır zaman serisi işleniyor.")

    # 2. ÖZELLİKLERİ HAZIRLA
    features = ['latency_ms', 'packet_loss_ratio', 'snr_margin_db', 'download_usage_mbps']
    
    # Hedefi Sayıya Çevir (Arıza Türleri: 0, 1, 2...)
    encoder = LabelEncoder()
    df_sample['root_cause_code'] = encoder.fit_transform(df_sample['root_cause'])
    
    # Verileri 0-1 arasına sıkıştır (LSTM, küçük sayıları sever)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df_sample[features])

    # 3. ZAMAN PENCERESİ (Sliding Window)
    # Mantık: Geçmiş 12 veriye bak (1 saat) -> Gelecek durumu tahmin et.
    X, y = [], []
    window_size = 12 

    for i in range(window_size, len(data_scaled)):
        X.append(data_scaled[i-window_size:i]) # Geçmiş 12 adım (Girdi)
        y.append(df_sample['root_cause_code'].iloc[i]) # Şu anki durum (Çıktı)

    X, y = np.array(X), np.array(y)

    # %80 Eğitim, %20 Test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    print(f"🧠 Model Tasarlanıyor... (Girdi Şekli: {X_train.shape})")

    # 4. LSTM MODELİNİ KUR (YAPAY SİNİR AĞI)
    model = Sequential()
    # Katman 1: LSTM (Hafıza Hücresi)
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2)) # Ezberlemeyi önle
    
    # Katman 2: LSTM
    model.add(LSTM(32, return_sequences=False))
    model.add(Dropout(0.2))
    
    # Çıktı Katmanı: Kaç çeşit arıza varsa o kadar çıkış ver
    num_classes = len(np.unique(y))
    model.add(Dense(num_classes, activation='softmax'))

    # Modeli Derle
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # 5. EĞİTİMİ BAŞLAT
    print("⏳ Eğitim başladı... (Bilgisayarın fanları biraz çalışabilir!)")
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

    # 6. KAYDET
    model.save(os.path.join(MODEL_DIR, 'netpulse_lstm.h5'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'lstm_scaler.pkl'))
    joblib.dump(encoder, os.path.join(MODEL_DIR, 'lstm_encoder.pkl'))

    print("\n" + "="*50)
    print(f"✅ TEBRİKLER! Geleceği Gören Model (LSTM) Kaydedildi.")
    print(f"📂 Yer: {MODEL_DIR}")
    print("="*50)

if __name__ == "__main__":
    train_lstm_model()