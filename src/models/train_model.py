import pandas as pd
import numpy as np
import joblib
import os
import sys
import time
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# --- 1. YOL AYARLARI (KRİTİK KISIM) ---
# Şu anki dosya: src/models/train_model.py
# 3 üst klasöre çıkarsak proje ana dizinine (NetPulse) geliriz.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Veri Yolu
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'train_data.csv')

# Model Kayıt Yeri (ARTIK ANA DİZİNDEKİ saved_models)
MODEL_DIR = os.path.join(BASE_DIR, 'saved_models')

# Klasör yoksa oluştur
os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 NetPulse AI (Random Forest) Eğitim Modülü Başlatılıyor...")
print(f"📂 Hedef Klasör: {MODEL_DIR}")

def train_rf_model():
    start_time = time.time()

    # --- 2. VERİ YÜKLEME ---
    if not os.path.exists(DATA_PATH):
        # Yedek plan: Processed yoksa ham veriye bak
        ALT_DATA_PATH = os.path.join(BASE_DIR, 'data', 'netpulse_telemetry_final.csv')
        if os.path.exists(ALT_DATA_PATH):
             print(f"⚠️ Processed veri bulunamadı, ham veri kullanılıyor: {ALT_DATA_PATH}")
             df = pd.read_csv(ALT_DATA_PATH)
        else:
            print(f"❌ HATA: Veri dosyası bulunamadı! ({DATA_PATH})")
            sys.exit()
    else:
        print(f"📊 Veri yükleniyor: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)

    # --- 3. ÖN İŞLEME ---
    # Gereksiz sütunları at (Eğer varsa)
    drop_cols = ['timestamp', 'device_id', 'modem_temperature', 'customer_id'] 
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

    # Hedef ve Özellikleri Ayır
    target_col = 'root_cause'
    if target_col not in df.columns:
        print(f"❌ HATA: '{target_col}' sütunu bulunamadı.")
        return

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Hedef Değişkeni Kodla (Label Encoding: String -> Sayı)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Sınıf isimlerini saklayalım
    class_names = list(le.classes_)
    print(f"🎯 Hedef Sınıflar: {class_names}")

    # Eğitim/Test Ayrımı
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    # --- 4. PIPELINE KURULUMU (Profesyonel Standart) ---
    # Sayısal ve Kategorik sütunları otomatik bul
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object']).columns

    # Dönüştürücüler
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Pipeline: Önce İşle -> Sonra Eğit
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    # --- 5. GRID SEARCH (HİPERPARAMETRE OPTİMİZASYONU) ---
    print("\n🔍 Grid Search ile en iyi parametreler aranıyor...")
    
    param_grid = {
        'classifier__n_estimators': [100, 200],      # Ağaç sayısı
        'classifier__max_depth': [None, 10, 20],    # Derinlik
        'classifier__min_samples_split': [2, 5],
        'classifier__class_weight': ['balanced', None]
    }

    grid_search = GridSearchCV(
        pipeline, 
        param_grid, 
        cv=3, 
        n_jobs=-1, 
        scoring='f1_macro',
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)

    # --- 6. SONUÇLAR VE RAPOR ---
    elapsed_time = time.time() - start_time
    print(f"\n✅ Eğitim Tamamlandı! Süre: {elapsed_time:.2f} sn")
    print(f"🏆 En İyi Parametreler: {grid_search.best_params_}")
    print(f"🌟 En İyi CV Skoru: {grid_search.best_score_:.4f}")

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    print("\n" + "="*60)
    print("SINIFLANDIRMA RAPORU")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=class_names))

    # --- 7. KAYDETME (CRITICAL FIX) ---
    # Modeli kaydet (Pipeline olduğu için scaler içinde!)
    model_path = os.path.join(MODEL_DIR, 'netpulse_classifier.pkl')
    joblib.dump(best_model, model_path)
    
    # Label Encoder'ı kaydet (Çıktıyı 'Modem Arızası' diye okumak için şart)
    encoder_path = os.path.join(MODEL_DIR, 'infra_encoder.pkl')
    joblib.dump(le, encoder_path)
    
    print(f"\n💾 DOSYALAR KAYDEDİLDİ:")
    print(f"   1. Model:   {model_path}")
    print(f"   2. Encoder: {encoder_path}")

if __name__ == "__main__":
    train_rf_model()