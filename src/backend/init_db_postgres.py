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

MODEM_MODELS = [
    "Huawei HG255s", "ZTE H298A", "TP-Link Archer C5v", "Keenetic Omni DSL", "Asus DSL-AC51"
]

TECHNICIANS = [
    ("Ahmet Yılmaz", "Fiber Uzmanı", "Active"),
    ("Mehmet Demir", "Saha Operasyonu", "Active"),
    ("Ayşe Kaya", "Ağ Mühendisi", "Busy"),
    ("Canan Yıldız", "Müşteri Destek", "Active"),
    ("Burak Çelik", "Kablo Teknisyeni", "Offline")
]

def generate_tr_phone():
    """Gerçekçi Türk telefon numarası üret"""
    prefixes = ['530', '531', '532', '533', '535', '536', '541', '542', '543', '544', '545', '555', '505', '506']
    prefix = random.choice(prefixes)
    
    part1 = random.randint(100, 999)
    part2 = random.randint(10, 99)
    part3 = random.randint(10, 99)
    
    return f"+90 {prefix} {part1} {part2} {part3}"

def generate_ip():
    return f"192.168.1.{random.randint(2, 254)}"

def generate_uptime():
    days = random.randint(0, 30)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return f"{days}g {hours}s {minutes}dk"

def create_database():
    print("PostgreSQL'e bağlanılıyor...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Eski tabloları sil (Sırası önemli, referanslar yüzünden)
        cursor.execute("DROP TABLE IF EXISTS tickets;")
        cursor.execute("DROP TABLE IF EXISTS technicians;")
        cursor.execute("DROP TABLE IF EXISTS subscriber_status;")
        cursor.execute("DROP TABLE IF EXISTS customers;")
        
        # 1. Customers tablosu (Gelişmiş)
        create_customers_table = """
        CREATE TABLE customers (
            subscriber_id INTEGER PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            gender VARCHAR(10),
            phone_number VARCHAR(20),
            subscription_plan VARCHAR(50),
            region_id VARCHAR(50),
            telegram_chat_id VARCHAR(50),
            is_vip BOOLEAN DEFAULT FALSE,
            modem_model VARCHAR(50),
            ip_address VARCHAR(20),
            uptime VARCHAR(20)
        );
        """
        cursor.execute(create_customers_table)
        print("✅ 'customers' tablosu oluşturuldu")
        
        # 2. Subscriber Status tablosu
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

        # 3. Technicians Table
        create_tech_table = """
        CREATE TABLE technicians (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            expertise VARCHAR(100),
            status VARCHAR(20) DEFAULT 'Active'
        );
        """
        cursor.execute(create_tech_table)
        print("✅ 'technicians' tablosu oluşturuldu")

        # 4. Tickets Table (Arıza Kayıtları) - YENİ TASARIM
        create_tickets_table = """
        CREATE TABLE tickets (
            ticket_id SERIAL PRIMARY KEY,
            subscriber_id INTEGER REFERENCES customers(subscriber_id),
            status VARCHAR(20) DEFAULT 'CREATED',
            priority VARCHAR(10) NOT NULL,
            fault_type VARCHAR(50),
            scope VARCHAR(20),
            technician_note TEXT,
            assigned_to VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            resolved_at TIMESTAMP,
            resolution_note TEXT
        );
        """
        cursor.execute(create_tickets_table)
        print("✅ 'tickets' tablosu oluşturuldu")

        # 5. Ticket Status History Table (Durum Geçmişi)
        create_status_history = """
        CREATE TABLE ticket_status_history (
            history_id SERIAL PRIMARY KEY,
            ticket_id INTEGER REFERENCES tickets(ticket_id) ON DELETE CASCADE,
            old_status VARCHAR(20),
            new_status VARCHAR(20) NOT NULL,
            changed_by VARCHAR(100),
            changed_at TIMESTAMP DEFAULT NOW(),
            note TEXT
        );
        """
        cursor.execute(create_status_history)
        print("✅ 'ticket_status_history' tablosu oluşturuldu")

        # Index'ler
        cursor.execute("CREATE INDEX idx_tickets_subscriber ON tickets(subscriber_id);")
        cursor.execute("CREATE INDEX idx_tickets_status ON tickets(status);")
        cursor.execute("CREATE INDEX idx_history_ticket ON ticket_status_history(ticket_id);")
        print("✅ Ticket index'leri oluşturuldu")

        # 6. Action Log Table (İşlem Logları)
        create_action_log = """
        CREATE TABLE action_log (
            id SERIAL PRIMARY KEY,
            subscriber_id INTEGER,
            action_type VARCHAR(50),
            new_status VARCHAR(50),
            note TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        """
        cursor.execute(create_action_log)
        cursor.execute("CREATE INDEX idx_action_log_subscriber ON action_log(subscriber_id);")
        print("✅ 'action_log' tablosu oluşturuldu")

        # --- DATA GENERATION ---

        # Technicians
        insert_tech = "INSERT INTO technicians (name, expertise, status) VALUES (%s, %s, %s)"
        cursor.executemany(insert_tech, TECHNICIANS)
        print(f"✅ {len(TECHNICIANS)} teknisyen eklendi.")

        print("500 Müşteri verisi üretiliyor...")
        customers_data = []
        
        # Admin profili - Sibel Akkurt
        sibel_profile = (
            1001, 
            "Sibel Akkurt", 
            "Kadın", 
            "+90 536 625 16 52", 
            "1000 Mbps Fiber Platin", 
            "Kadıköy/Moda", 
            "", 
            True,
            "Huawei HG255s",
            "192.168.1.100",
            "14g 5s"
        )
        customers_data.append(sibel_profile)
        
        plans = ["24 Mbps VDSL", "35 Mbps VDSL", "100 Mbps Fiber", "500 Mbps Fiber", "1000 Mbps Gamer"]
        
        for i in range(1, TOTAL_SUBSCRIBERS):
            sub_id = 1001 + i
            region = random.choice(DISTRICTS)
            plan = random.choice(plans)
            is_vip = "Gamer" in plan or "Platin" in plan
            phone = generate_tr_phone()
            modem = random.choice(MODEM_MODELS)
            ip = generate_ip()
            uptime = generate_uptime()
            
            gender_choice = random.choice(["Kadın", "Erkek"])
            name = fake.name_female() if gender_choice == "Kadın" else fake.name_male()
            
            customers_data.append((sub_id, name, gender_choice, phone, plan, region, "", is_vip, modem, ip, uptime))
            
        insert_sql = """
        INSERT INTO customers (subscriber_id, full_name, gender, phone_number, subscription_plan, region_id, telegram_chat_id, is_vip, modem_model, ip_address, uptime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        
        
        print(f"✅ İŞLEM TAMAM! {len(customers_data)} müşteri kaydedildi.")
        conn.close()

    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    create_database()