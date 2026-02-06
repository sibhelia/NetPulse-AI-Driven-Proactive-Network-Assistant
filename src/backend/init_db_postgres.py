import psycopg2
import random
from faker import Faker
import os

DB_NAME = "netpulse_db"
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

TOTAL_SUBSCRIBERS = 500
fake = Faker('tr_TR')

# Gerçek İstanbul mahalle isimleri
DISTRICTS = [
    "Kadıköy/Moda", "Kadıköy/Fenerbahçe", "Kadıköy/Göztepe",
    "Beşiktaş/Etiler", "Beşiktaş/Levent", "Beşiktaş/Bebek",
    "Üsküdar/Acıbadem", "Üsküdar/Çengelköy", "Üsküdar/Kuzguncuk",
    "Şişli/Nişantaşı", "Şişli/Mecidiyeköy", "Şişli/Osmanbey",
    "Bakırköy/Ataköy", "Bakırköy/Yeşilköy", "Bakırköy/Florya"
]

def generate_tr_phone():
    """Gerçekçi Türk telefon numarası üret"""
    prefixes = ['530', '531', '532', '533', '535', '536', '541', '542', '543', '544', '545', '555', '505', '506']
    prefix = random.choice(prefixes)
    
    part1 = random.randint(100, 999)
    part2 = random.randint(10, 99)
    part3 = random.randint(10, 99)
    
    return f"+90 {prefix} {part1} {part2} {part3}"

def create_database():
    print("PostgreSQL'e bağlanılıyor...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Eski tabloları sil
        cursor.execute("DROP TABLE IF EXISTS subscriber_status;")
        cursor.execute("DROP TABLE IF EXISTS customers;")
        
        # Customers tablosu
        create_customers_table = """
        CREATE TABLE customers (
            subscriber_id INTEGER PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            gender VARCHAR(10),
            phone_number VARCHAR(20),
            subscription_plan VARCHAR(50),
            region_id VARCHAR(50),
            telegram_chat_id VARCHAR(50),
            is_vip BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_customers_table)
        print("✅ 'customers' tablosu oluşturuldu")
        
        # Subscriber Status tablosu (YENİ!)
        create_status_table = """
        CREATE TABLE subscriber_status (
            subscriber_id INTEGER PRIMARY KEY REFERENCES customers(subscriber_id),
            current_status VARCHAR(10) DEFAULT 'GREEN',
            previous_status VARCHAR(10),
            last_checked TIMESTAMP DEFAULT NOW(),
            status_changed_at TIMESTAMP,
            fault_type VARCHAR(50),
            estimated_fix_time TIMESTAMP,
            sms_sent BOOLEAN DEFAULT FALSE,
            sms_sent_at TIMESTAMP
        );
        """
        cursor.execute(create_status_table)
        print("✅ 'subscriber_status' tablosu oluşturuldu")

        print("500 Müşteri verisi üretiliyor...")
        customers_data = []
        
        # Admin profili - Sibel Akkurt
        sibel_profile = (
            1001, 
            "Sibel Akkurt", 
            "Kadın", 
            "+90 536 625 16 52", 
            "1000 Mbps Fiber Platin", 
            "Kadıköy/Moda",  # Gerçek mahalle
            "", 
            True
        )
        customers_data.append(sibel_profile)
        
        plans = ["24 Mbps VDSL", "35 Mbps VDSL", "100 Mbps Fiber", "500 Mbps Fiber", "1000 Mbps Gamer"]
        
        for i in range(1, TOTAL_SUBSCRIBERS):
            sub_id = 1001 + i
            region = random.choice(DISTRICTS)  # Gerçek mahalle isimleri
            plan = random.choice(plans)
            is_vip = "Gamer" in plan or "Platin" in plan
            phone = generate_tr_phone()
            
            # Cinsiyet ve ona uygun isim seçimi
            gender_choice = random.choice(["Kadın", "Erkek"])
            if gender_choice == "Kadın":
                name = fake.name_female()
            else:
                name = fake.name_male()
            
            customers_data.append((sub_id, name, gender_choice, phone, plan, region, "", is_vip))
            
        insert_sql = """
        INSERT INTO customers (subscriber_id, full_name, gender, phone_number, subscription_plan, region_id, telegram_chat_id, is_vip)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, customers_data)
        
        # Tüm kullanıcıları başlangıçta GREEN olarak işaretle
        print("Tüm kullanıcılar başlangıç durumuna (GREEN) alınıyor...")
        for customer in customers_data:
            sub_id = customer[0]
            cursor.execute(
                "INSERT INTO subscriber_status (subscriber_id, current_status) VALUES (%s, 'GREEN')",
                (sub_id,)
            )
        
        print(f"✅ İŞLEM TAMAM! {len(customers_data)} müşteri + {len(customers_data)} status kaydedildi.")
        print(f"✅ Sibel Akkurt profili: {sibel_profile[3]}")
        conn.close()

    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    create_database()