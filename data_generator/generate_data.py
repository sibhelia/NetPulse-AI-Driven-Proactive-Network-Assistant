import pandas as pd
import numpy as np
import datetime
import os

# Konfigurasyon
NUM_REGIONS = 5
HOUSES_PER_REGION = 100
TOTAL_HOUSES = NUM_REGIONS * HOUSES_PER_REGION
START_TIME = datetime.datetime(2026, 2, 1, 0, 0, 0)
DURATION_HOURS = 24
INTERVAL_MINUTES = 5 

# Dosya yollari
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'netpulse_telemetry_final.csv')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"'{DATA_DIR}' klasoru olusturuldu.")

print(f"--- NETPULSE TELEKOM SIMULASYONU ---")
print(f"Hedef: {TOTAL_HOUSES} Hane | {DURATION_HOURS} Saat | Kayit Yeri: {OUTPUT_FILE}")

# Envanter ve altyapi olusturma
infra_types = ['FIBER', 'VDSL']
house_inventory = []

for r in range(1, NUM_REGIONS + 1):
    for h in range(1, HOUSES_PER_REGION + 1):
        house_id = (r * 1000) + h
        infra = np.random.choice(infra_types, p=[0.4, 0.6])
        
        if infra == 'FIBER':
            dist = 0
            base_snr = 45
            max_speed = 1000
        else:
            dist = np.random.randint(50, 800)
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

# Zaman serisi simulasyonu
total_steps = int((DURATION_HOURS * 60) / INTERVAL_MINUTES)
timestamps = [START_TIME + datetime.timedelta(minutes=i*INTERVAL_MINUTES) for i in range(total_steps)]
data_list = []

print("Veri uretiliyor...")

for ts in timestamps:
    hour = ts.hour
    is_prime_time = 1 if 19 <= hour <= 23 else 0
    base_load = 0.3 + (0.7 * is_prime_time)
    
    for house in house_inventory:
        noise = np.random.normal(0, 1)
        
        # Kullanim verileri
        active_factor = np.random.choice([0.1, 0.5, 0.9], p=[0.7, 0.2, 0.1])
        
        download_usage = house['max_speed_mbps'] * base_load * active_factor * abs(np.random.normal(1, 0.2))
        upload_usage = (download_usage * 0.1) + abs(noise)
        
        # Donanim verileri
        cpu_load = 15 + (download_usage * 0.4) + abs(noise * 2)
        ram_load = 40 + (download_usage * 0.1) + abs(noise)
        
        # Fiziksel hat verileri
        current_snr = house['baseline_snr'] + np.random.normal(0, 0.5)
        if house['infra_type'] == 'VDSL' and is_prime_time:
            current_snr -= 2.5
            
        # Wi-Fi sinyali
        wifi_rssi = np.random.normal(-50, 10) 
        
        # Sonuc metrikleri
        base_latency = 5 if house['infra_type'] == 'FIBER' else (10 + house['distance_m']*0.01)
        wifi_penalty = 0 if wifi_rssi > -70 else (abs(wifi_rssi) - 70) * 2
        
        latency = base_latency + (download_usage * 0.05) + wifi_penalty + abs(noise)
        jitter = abs(np.random.normal(2, 1)) + (wifi_penalty * 0.5)
        
        packet_loss = 0
        if current_snr < 8: packet_loss += np.random.uniform(1, 10)
        if wifi_rssi < -80: packet_loss += np.random.uniform(5, 15)
        
        row = {
            'timestamp': ts,
            'subscriber_id': house['subscriber_id'],
            'region_id': house['region_id'],
            'infra_type': house['infra_type'],
            'distance_to_cabinet_m': house['distance_m'],
            'download_usage_mbps': round(download_usage, 2),
            'upload_usage_mbps': round(upload_usage, 2),
            'signal_strength_rssi': round(wifi_rssi, 1),
            'latency_ms': round(latency, 2),
            'jitter_ms': round(jitter, 2),
            'packet_loss_ratio': round(packet_loss, 2),
            'snr_margin_db': round(current_snr, 1),
            'modem_cpu_usage': round(min(100, cpu_load), 1),
            'modem_ram_usage': round(min(100, ram_load), 1),
            'link_status': 1,
            'label': 0,
            'root_cause': 'Normal'
        }
        data_list.append(row)

df = pd.DataFrame(data_list)
print("Normal veri seti olusturuldu. Arizalar enjekte ediliyor...")

# Ariza senaryolari

# Senaryo 1: Wi-Fi interference
wifi_issues = np.random.choice(df.index, size=int(len(df)*0.02), replace=False)
df.loc[wifi_issues, 'signal_strength_rssi'] -= np.random.uniform(30, 40)
df.loc[wifi_issues, 'latency_ms'] += np.random.uniform(50, 150)
df.loc[wifi_issues, 'packet_loss_ratio'] += np.random.uniform(2, 8)
df.loc[wifi_issues, 'label'] = 0
df.loc[wifi_issues, 'root_cause'] = 'Poor_WiFi_Coverage'

# Senaryo 2: Modem asiri yuk
cpu_issues = np.random.choice(df.index, size=int(len(df)*0.01), replace=False)
df.loc[cpu_issues, 'modem_cpu_usage'] = np.random.uniform(95, 100)
df.loc[cpu_issues, 'latency_ms'] += np.random.uniform(100, 300)
df.loc[cpu_issues, 'label'] = 1
df.loc[cpu_issues, 'root_cause'] = 'Modem_Overheat'

# Senaryo 3: Fiziksel hat arizasi (sadece VDSL)
vdsl_idx = df[df['infra_type'] == 'VDSL'].index
line_issues = np.random.choice(vdsl_idx, size=int(len(vdsl_idx)*0.01), replace=False)
df.loc[line_issues, 'snr_margin_db'] = np.random.uniform(0, 6)
df.loc[line_issues, 'packet_loss_ratio'] = np.random.uniform(10, 25)
df.loc[line_issues, 'download_usage_mbps'] *= 0.1
df.loc[line_issues, 'label'] = 1
df.loc[line_issues, 'root_cause'] = 'Physical_Line_Fault'

# Senaryo 4: Bolgesel kesinti
region_fault_mask = (df['region_id'] == 'Region_5') & (df['timestamp'].dt.hour == 21)
df.loc[region_fault_mask, 'link_status'] = 0
df.loc[region_fault_mask, 'latency_ms'] = 0
df.loc[region_fault_mask, 'snr_margin_db'] = 0
df.loc[region_fault_mask, 'label'] = 2
df.loc[region_fault_mask, 'root_cause'] = 'Regional_Outage'

# Kaydet
df.to_csv(OUTPUT_FILE, index=False)

print(f"\nISLEM TAMAMLANDI!")
print(f"Toplam Satir: {len(df)}")
print(f"Dosya Kaydedildi: {OUTPUT_FILE}")
print("\nOrnek Veri (Ilk 3 Satir):")
print(df[['timestamp', 'infra_type', 'snr_margin_db', 'signal_strength_rssi', 'root_cause']].head(3))