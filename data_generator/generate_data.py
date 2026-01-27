import pandas as pd
import numpy as np
import datetime
import os

# ==========================================
# ⚙️ KONFİGÜRASYON VE SABİTLER
# ==========================================
NUM_REGIONS = 5
HOUSES_PER_REGION = 100
TOTAL_HOUSES = NUM_REGIONS * HOUSES_PER_REGION
START_TIME = datetime.datetime(2026, 2, 1, 0, 0, 0)
DURATION_HOURS = 24
INTERVAL_MINUTES = 5 

# Dosya Kayıt Yolları (Otomatik Ayarlanır)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # Kodun olduğu yer
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)              # Bir üst klasör (Repo kökü)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')            # data/ klasörü
OUTPUT_FILE = os.path.join(DATA_DIR, 'netpulse_telemetry_final.csv')

# Klasör yoksa oluştur
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"📁 '{DATA_DIR}' klasörü oluşturuldu.")

print(f"--- 📡 NETPULSE TELEKOM SİMÜLASYONU (ULTIMATE VERSION) ---")
print(f"Hedef: {TOTAL_HOUSES} Hane | {DURATION_HOURS} Saat | Kayıt Yeri: {OUTPUT_FILE}")

# ==========================================
# 1. ADIM: ENVANTER VE ALTYAPI OLUŞTURMA
# ==========================================
infra_types = ['FIBER', 'VDSL']
house_inventory = []

for r in range(1, NUM_REGIONS + 1):
    for h in range(1, HOUSES_PER_REGION + 1):
        house_id = (r * 1000) + h
        infra = np.random.choice(infra_types, p=[0.4, 0.6]) # %40 Fiber, %60 VDSL
        
        # Altyapıya göre fiziksel özellikler
        if infra == 'FIBER':
            dist = 0 # Fiberde mesafe önemsizdir (teorik olarak)
            base_snr = 45 # Çok temiz hat
            max_speed = 1000
        else:
            dist = np.random.randint(50, 800) # Saha dolabına 50m ile 800m arası
            # Mesafe arttıkça SNR (sinyal kalitesi) düşer
            base_snr = 30 - (dist * 0.02) 
            max_speed = 100 if dist < 300 else (50 if dist < 600 else 24)

        house_inventory.append({
            'subscriber_id': house_id,
            'region_id': f"Region_{r}",
            'infra_type': infra,
            'distance_m': dist,
            'baseline_snr': base_snr,
            'max_speed_mbps': max_speed
        })

# ==========================================
# 2. ADIM: ZAMAN SERİSİ SİMÜLASYONU
# ==========================================
total_steps = int((DURATION_HOURS * 60) / INTERVAL_MINUTES)
timestamps = [START_TIME + datetime.timedelta(minutes=i*INTERVAL_MINUTES) for i in range(total_steps)]
data_list = []

print("⏳ Veri üretiliyor (Bu işlem fiziksel hesaplamalar içerir)...")

for ts in timestamps:
    # GÜN DÖNGÜSÜ (Traffic Pattern)
    hour = ts.hour
    is_prime_time = 1 if 19 <= hour <= 23 else 0
    base_load = 0.3 + (0.7 * is_prime_time) # Akşamları yoğunluk %100'e yaklaşır
    
    for house in house_inventory:
        noise = np.random.normal(0, 1)
        
        # --- A. KULLANIM VERİLERİ ---
        # Download ve Upload (Kullanıcı davranışı)
        # Bazen upload download'dan fazla olabilir (Yedekleme, Yayın açma)
        active_factor = np.random.choice([0.1, 0.5, 0.9], p=[0.7, 0.2, 0.1]) # Çoğu zaman boşta
        
        download_usage = house['max_speed_mbps'] * base_load * active_factor * abs(np.random.normal(1, 0.2))
        upload_usage = (download_usage * 0.1) + abs(noise) # Genelde download'un %10'u
        
        # --- B. DONANIM VERİLERİ (CPE) ---
        # Modem CPU: Trafik arttıkça artar
        cpu_load = 15 + (download_usage * 0.4) + abs(noise * 2)
        ram_load = 40 + (download_usage * 0.1) + abs(noise)
        
        # --- C. FİZİKSEL HAT (PHY LAYER) ---
        current_snr = house['baseline_snr'] + np.random.normal(0, 0.5)
        # VDSL'de akşamları 'Crosstalk' (hatlar arası parazit) olur, SNR düşer
        if house['infra_type'] == 'VDSL' and is_prime_time:
            current_snr -= 2.5
            
        # --- D. WI-FI SİNYALİ (YENİ!) ---
        # -30dBm (Mükemmel) ile -90dBm (Kopuk) arası
        # Evin içinde dolaşıyor gibi rastgele değişir
        wifi_rssi = np.random.normal(-50, 10) 
        
        # --- E. SONUÇ METRİKLERİ (NETWORK QOS) ---
        
        # Latency Hesaplama:
        # Baz Gecikme + Trafik Yoğunluğu + Wi-Fi Kötüyse Ek Gecikme
        base_latency = 5 if house['infra_type'] == 'FIBER' else (10 + house['distance_m']*0.01)
        wifi_penalty = 0 if wifi_rssi > -70 else (abs(wifi_rssi) - 70) * 2 # Wi-Fi kötüyse ping artar
        
        latency = base_latency + (download_usage * 0.05) + wifi_penalty + abs(noise)
        jitter = abs(np.random.normal(2, 1)) + (wifi_penalty * 0.5)
        
        # Packet Loss Hesaplama:
        # SNR kötüyse VEYA Wi-Fi çok kötüyse (-80 altı) paket kaybı başlar
        packet_loss = 0
        if current_snr < 8: packet_loss += np.random.uniform(1, 10)
        if wifi_rssi < -80: packet_loss += np.random.uniform(5, 15)
        
        # Kayıt Hazırlığı
        row = {
            'timestamp': ts,
            'subscriber_id': house['subscriber_id'],
            'region_id': house['region_id'],
            'infra_type': house['infra_type'],
            'distance_to_cabinet_m': house['distance_m'], # YENİ (Mühendislik detayı)
            'download_usage_mbps': round(download_usage, 2),
            'upload_usage_mbps': round(upload_usage, 2),  # YENİ
            'signal_strength_rssi': round(wifi_rssi, 1),  # YENİ (Wi-Fi Gücü)
            'latency_ms': round(latency, 2),
            'jitter_ms': round(jitter, 2),
            'packet_loss_ratio': round(packet_loss, 2),
            'snr_margin_db': round(current_snr, 1),
            'modem_cpu_usage': round(min(100, cpu_load), 1),
            'modem_ram_usage': round(min(100, ram_load), 1),
            'link_status': 1,
            'label': 0,          # 0: Normal
            'root_cause': 'Normal'
        }
        data_list.append(row)

df = pd.DataFrame(data_list)
print("✅ Normal veri seti oluşturuldu. Arızalar enjekte ediliyor...")

# ==========================================
# 3. ADIM: DETAYLI ARIZA SENARYOLARI (SCENARIOS)
# ==========================================

# SENARYO 1: WI-FI INTERFERENCE (Operatör Kaynaklı Olmayan Sorun)
# Kullanıcı "internetim kötü" der ama hat değerleri (SNR) mükemmeldir.
# Amaç: Yapay Zekanın "Sorun bizde değil, müşterinin Wi-Fi'ında" demesini sağlamak.
wifi_issues = np.random.choice(df.index, size=int(len(df)*0.02), replace=False)
df.loc[wifi_issues, 'signal_strength_rssi'] -= np.random.uniform(30, 40) # RSSI -85'lere düşer
df.loc[wifi_issues, 'latency_ms'] += np.random.uniform(50, 150)          # Ping artar
df.loc[wifi_issues, 'packet_loss_ratio'] += np.random.uniform(2, 8)      # Kayıp artar
df.loc[wifi_issues, 'label'] = 0 # DİKKAT: Bu bir "Arıza" etiketi değil (1), çünkü hat sağlam!
df.loc[wifi_issues, 'root_cause'] = 'Poor_WiFi_Coverage'

# SENARYO 2: MODEM AŞIRI YÜK (Hardware Fault)
cpu_issues = np.random.choice(df.index, size=int(len(df)*0.01), replace=False)
df.loc[cpu_issues, 'modem_cpu_usage'] = np.random.uniform(95, 100)
df.loc[cpu_issues, 'latency_ms'] += np.random.uniform(100, 300)
df.loc[cpu_issues, 'label'] = 1
df.loc[cpu_issues, 'root_cause'] = 'Modem_Overheat'

# SENARYO 3: FİZİKSEL HAT KOPUKLUĞU / OKSİTLENME (Physical Fault)
# Sadece VDSL hatlarda
vdsl_idx = df[df['infra_type'] == 'VDSL'].index
line_issues = np.random.choice(vdsl_idx, size=int(len(vdsl_idx)*0.01), replace=False)
df.loc[line_issues, 'snr_margin_db'] = np.random.uniform(0, 6) # SNR kritik seviyeye iner
df.loc[line_issues, 'packet_loss_ratio'] = np.random.uniform(10, 25)
df.loc[line_issues, 'download_usage_mbps'] *= 0.1 # Hız sürünür
df.loc[line_issues, 'label'] = 1
df.loc[line_issues, 'root_cause'] = 'Physical_Line_Fault'

# SENARYO 4: BÖLGESEL KESİNTİ (Regional Outage)
# Region_5'te ana switch arızası. 
region_fault_mask = (df['region_id'] == 'Region_5') & (df['timestamp'].dt.hour == 21)
df.loc[region_fault_mask, 'link_status'] = 0
df.loc[region_fault_mask, 'latency_ms'] = 0
df.loc[region_fault_mask, 'snr_margin_db'] = 0
df.loc[region_fault_mask, 'label'] = 2
df.loc[region_fault_mask, 'root_cause'] = 'Regional_Outage'

# ==========================================
# 4. ADIM: KAYIT
# ==========================================
df.to_csv(OUTPUT_FILE, index=False)

print(f"\n🎉 İŞLEM TAMAMLANDI!")
print(f"📊 Toplam Satır: {len(df)}")
print(f"💾 Dosya Kaydedildi: {OUTPUT_FILE}")
print("\nÖrnek Veri (İlk 3 Satır):")
print(df[['timestamp', 'infra_type', 'snr_margin_db', 'signal_strength_rssi', 'root_cause']].head(3))