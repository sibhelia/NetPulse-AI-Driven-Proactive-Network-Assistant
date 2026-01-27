import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import joblib
import os
import sys
import time

# Yol tanimlari
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

TRAIN_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'train_data.csv')
TEST_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'test_data.csv')

MODEL_DIR = os.path.join(PROJECT_ROOT, 'models', 'saved_objects')
MODEL_PATH = os.path.join(MODEL_DIR, 'netpulse_classifier.pkl')

print("NetPulse AI Egitim Modulu Baslatiliyor...")

# Islenmis veriyi yukle
if not os.path.exists(TRAIN_DATA_PATH):
    print("HATA: Islenmis veri bulunamadi! Lutfen once 'src/preprocessing.py' calistirin.")
    sys.exit()

print("\nVeriler yukleniyor...")
train_df = pd.read_csv(TRAIN_DATA_PATH)
test_df = pd.read_csv(TEST_DATA_PATH)

target_col = 'root_cause'
X_train = train_df.drop(columns=[target_col])
y_train = train_df[target_col]

X_test = test_df.drop(columns=[target_col])
y_test = test_df[target_col]

print(f"Egitim Seti: {X_train.shape}")
print(f"Test Seti: {X_test.shape}")

# Hiperparametre izgarasi
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'class_weight': ['balanced', None]
}

# Cross-validation ile egitim
print("\nGrid Search & Cross Validation Basliyor...")

start_time = time.time()

rf = RandomForestClassifier(random_state=42)
cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=cv_strategy,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

elapsed_time = time.time() - start_time
print(f"\nEgitim Tamamlandi! Sure: {elapsed_time:.2f} saniye")
print(f"EN IYI PARAMETRELER: {grid_search.best_params_}")
print(f"EN IYI CV SKORU (F1-Macro): {grid_search.best_score_:.4f}")

best_model = grid_search.best_estimator_

# Test seti uzerinde degerlendirme
print("\nFinal Testi...")
y_pred = best_model.predict(X_test)

print("\n" + "="*60)
print("SINIFLANDIRMA RAPORU (CLASSIFICATION REPORT)")
print("="*60)
print(classification_report(y_test, y_pred))

print("\nKARMASIKLIK MATRISI (CONFUSION MATRIX)")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Ozellik onemi
print("\n" + "="*60)
print("OZELLIK ONEM DUZEYLERI")
print("="*60)

feature_importances = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': best_model.feature_importances_
}).sort_values(by='Importance', ascending=False)

print(feature_importances)

top_feature = feature_importances.iloc[0]['Feature']
print(f"\nSONUC: Model kararlarini en cok '{top_feature}' verisine bakarak veriyor.")

# Modeli kaydet
print(f"\nEn iyi model kaydediliyor: {MODEL_PATH}")
joblib.dump(best_model, MODEL_PATH)

print("BUTUN SURECLER BASARIYLA TAMAMLANDI.")