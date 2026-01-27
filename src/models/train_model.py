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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'train_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'saved_models')

os.makedirs(MODEL_DIR, exist_ok=True)

print("NetPulse AI (Random Forest) Egitim Modulu Baslatiliyor...")
print(f"Hedef Klasor: {MODEL_DIR}")

def train_rf_model():
    start_time = time.time()

    if not os.path.exists(DATA_PATH):
        ALT_DATA_PATH = os.path.join(BASE_DIR, 'data', 'netpulse_telemetry_final.csv')
        if os.path.exists(ALT_DATA_PATH):
             print(f"Processed veri bulunamadi, ham veri kullaniliyor: {ALT_DATA_PATH}")
             df = pd.read_csv(ALT_DATA_PATH)
        else:
            print(f"HATA: Veri dosyasi bulunamadi! ({DATA_PATH})")
            sys.exit()
    else:
        print(f"Veri yukleniyor: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)

    drop_cols = ['timestamp', 'device_id', 'modem_temperature', 'customer_id'] 
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

    target_col = 'root_cause'
    if target_col not in df.columns:
        print(f"HATA: '{target_col}' sutunu bulunamadi.")
        return

    X = df.drop(columns=[target_col])
    y = df[target_col]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    class_names = list(le.classes_)
    print(f"Hedef Siniflar: {class_names}")

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object']).columns

    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    print("\nGrid Search ile en iyi parametreler araniyor...")
    
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [None, 10, 20],
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

    elapsed_time = time.time() - start_time
    print(f"\nEgitim Tamamlandi! Sure: {elapsed_time:.2f} sn")
    print(f"En Iyi Parametreler: {grid_search.best_params_}")
    print(f"En Iyi CV Skoru: {grid_search.best_score_:.4f}")

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    print("\n" + "="*60)
    print("SINIFLANDIRMA RAPORU")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=class_names))

    model_path = os.path.join(MODEL_DIR, 'netpulse_classifier.pkl')
    joblib.dump(best_model, model_path)
    
    encoder_path = os.path.join(MODEL_DIR, 'infra_encoder.pkl')
    joblib.dump(le, encoder_path)
    
    print(f"\nDOSYALAR KAYDEDILDI:")
    print(f"   1. Model:   {model_path}")
    print(f"   2. Encoder: {encoder_path}")

if __name__ == "__main__":
    train_rf_model()