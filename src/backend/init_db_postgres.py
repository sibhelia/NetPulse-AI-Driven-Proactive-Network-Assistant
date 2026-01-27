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

def generate_tr_phone():
    prefixes = ['530', '531', '532', '533', '535', '536', '541', '542', '543', '544', '545', '555', '505', '506']
    prefix = random.choice(prefixes)
    
    part1 = random.randint(100, 999)
    part2 = random.randint(10, 99)
    part3 = random.randint(10, 99)
    
    return f"+90 {prefix} {part1} {part2} {part3}"

def create_database():
    print("PostgreSQL'e baglaniliyor...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS customers;")
        
        # Gender sutunu eklendi
        create_table_sql = """
        CREATE TABLE customers (
            subscriber_id INTEGER PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            gender VARCHAR(10),
            phone_number VARCHAR(20),
            subscription_plan VARCHAR(50),
            region_id VARCHAR(20),
            telegram_chat_id VARCHAR(50),
            is_vip BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_table_sql)
        print("'customers' tablosu olusturuldu (Gender sutunu ile).")

        print("500 Musteri verisi uretiliyor...")
        customers_data = []
        
        # Admin profili (Cinsiyet: Kadın)
        my_profile = (1001, "Sibel (Admin)", "Kadın", "+90 555 111 22 33", "1000 Mbps Fiber Platin", "Region_1", "", True)
        customers_data.append(my_profile)
        
        plans = ["24 Mbps VDSL", "35 Mbps VDSL", "100 Mbps Fiber", "500 Mbps Fiber", "1000 Mbps Gamer"]
        
        for i in range(1, TOTAL_SUBSCRIBERS):
            sub_id = 1001 + i
            region = f"Region_{(i // 100) + 1}"
            plan = random.choice(plans)
            is_vip = "Gamer" in plan
            phone = generate_tr_phone()
            
            # Cinsiyet ve ona uygun isim secimi
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
        
        print(f"ISLEM TAMAM! {len(customers_data)} adet veri kaydedildi.")
        conn.close()

    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    create_database()