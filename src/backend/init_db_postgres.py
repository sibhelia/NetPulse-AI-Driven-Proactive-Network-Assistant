import psycopg2
import random
from faker import Faker
import os

# --- AYARLAR ---
DB_NAME = "netpulse_db"
DB_USER = "postgres"
DB_PASSWORD = "admin"     # <-- Senin şifren
DB_HOST = "localhost"
DB_PORT = "5432"

TOTAL_SUBSCRIBERS = 500
fake = Faker('tr_TR')

# --- ÖZEL FONKSİYON: Gerçekçi Türk Numarası Üretici ---
def generate_tr_phone():
    # Gerçek operatör kodları
    prefixes = ['530', '531', '532', '533', '535', '536', '541', '542', '543', '544', '545', '555', '505', '506']
    prefix = random.choice(prefixes)
    
    part1 = random.randint(100, 999) # XXX
    part2 = random.randint(10, 99)   # XX
    part3 = random.randint(10, 99)   # XX
    
    # Format: +90 532 123 45 67 (Toplam 17 Karakter)
    return f"+90 {prefix} {part1} {part2} {part3}"

def create_database():
    print("🔌 PostgreSQL'e bağlanılıyor...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Bağlantı başarılı!")

        # 1. Temizlik
        cursor.execute("DROP TABLE IF EXISTS customers;")
        
        # 2. Tablo Oluşturma (Standartlara Uygun)
        # Telefon için VARCHAR(20) yeterli çünkü bizim formatımız sabit 17 karakter.
        create_table_sql = """
        CREATE TABLE customers (
            subscriber_id INTEGER PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(20),       -- +90 5XX ... formatı için ideal
            subscription_plan VARCHAR(50),
            region_id VARCHAR(20),
            telegram_chat_id VARCHAR(50),
            is_vip BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_table_sql)
        print("✅ 'customers' tablosu oluşturuldu (Standart TR Formatı).")

        # 3. Veri Üretimi
        print("🌱 500 Müşteri verisi standartlara uygun üretiliyor...")
        customers_data = []
        
        # SEN (ID 1001)
        my_profile = (1001, "Sibel (Admin)", "+90 555 111 22 33", "1000 Mbps Fiber Platin", "Region_1", "", True)
        customers_data.append(my_profile)
        
        # Diğerleri
        plans = ["24 Mbps VDSL", "35 Mbps VDSL", "100 Mbps Fiber", "500 Mbps Fiber", "1000 Mbps Gamer"]
        
        for i in range(1, TOTAL_SUBSCRIBERS):
            sub_id = 1001 + i
            region = f"Region_{(i // 100) + 1}"
            plan = random.choice(plans)
            is_vip = "Gamer" in plan
            
            # Özel fonksiyonumuzu kullanıyoruz
            phone = generate_tr_phone()
            
            customers_data.append((sub_id, fake.name(), phone, plan, region, "", is_vip))
            
        # 4. Kaydet
        insert_sql = """
        INSERT INTO customers (subscriber_id, full_name, phone_number, subscription_plan, region_id, telegram_chat_id, is_vip)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, customers_data)
        
        print(f"🎉 İŞLEM TAMAM! {len(customers_data)} adet standart veri kaydedildi.")
        conn.close()

    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    create_database()