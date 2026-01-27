import pandas as pd
import numpy as np
import joblib
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'netpulse_telemetry_final.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'src', 'models', 'saved_objects')

os.makedirs(MODEL_DIR, exist_ok=True)

print(f"LSTM (Zaman Serisi) Egitimi Basliyor...\nVeri Yolu: {DATA_PATH}")

def train_lstm_model():
    if not os.path.exists(DATA_PATH):
        print("HATA: CSV dosyasi bulunamadi! Lutfen once veri uretin.")
        return

    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    df_sample = df[df['region_id'] == 'Region_1'].copy()
    
    print(f"Veri Hazir: {len(df_sample)} satir zaman serisi isleniyor.")

    features = ['latency_ms', 'packet_loss_ratio', 'snr_margin_db', 'download_usage_mbps']
    
    encoder = LabelEncoder()
    df_sample['root_cause_code'] = encoder.fit_transform(df_sample['root_cause'])
    
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df_sample[features])

    X, y = [], []
    window_size = 12 

    for i in range(window_size, len(data_scaled)):
        X.append(data_scaled[i-window_size:i])
        y.append(df_sample['root_cause_code'].iloc[i])

    X, y = np.array(X), np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    print(f"Model Tasarlaniyor... (Girdi Sekli: {X_train.shape})")

    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    
    model.add(LSTM(32, return_sequences=False))
    model.add(Dropout(0.2))
    
    num_classes = len(np.unique(y))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    print("Egitim basladi...")
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

    model.save(os.path.join(MODEL_DIR, 'netpulse_lstm.h5'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'lstm_scaler.pkl'))
    joblib.dump(encoder, os.path.join(MODEL_DIR, 'lstm_encoder.pkl'))

    print("\n" + "="*50)
    print("LSTM Modeli Kaydedildi.")
    print(f"Yer: {MODEL_DIR}")
    print("="*50)

if __name__ == "__main__":
    train_lstm_model()