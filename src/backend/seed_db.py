import psycopg2
import random
from datetime import datetime, timedelta

# DB Config
DB_CONFIG = {
    "dbname": "netpulse_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def seed_database_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🌱 Seeding database with realistic initial state...")
        
        # 1. Reset everyone to GREEN first
        cursor.execute("""
            UPDATE subscriber_status
            SET current_status = 'GREEN',
                previous_status = NULL,
                fault_type = NULL,
                estimated_fix_time = NULL,
                status_changed_at = NOW(),
                last_checked = NOW(),
                sms_sent = FALSE
        """)
        
        # 2. Get all subscriber IDs
        cursor.execute("SELECT subscriber_id FROM customers")
        all_ids = [row[0] for row in cursor.fetchall()]
        
        if len(all_ids) < 30:
            print("❌ Not enough subscribers to seed!")
            return

        # 3. Select random victims
        # Target: 25 RED (Peak Hour Fault), 45 YELLOW (Proactive Detection)
        targets_red = random.sample(all_ids, 25)
        remaining_ids = list(set(all_ids) - set(targets_red))
        targets_yellow = random.sample(remaining_ids, 45)
        
        print(f"🎯 Selected {len(targets_red)} for RED and {len(targets_yellow)} for YELLOW")

        # 4. Update RED subscribers
        # Arıza YENİ başlamış olsun ki persistence (10dk) korusun ve silinmesin!
        for sub_id in targets_red:
            changed_at = datetime.now() # Şimdi başladı
            estimated_fix = datetime.now() + timedelta(hours=random.randint(2, 4))
            
            cursor.execute("""
                UPDATE subscriber_status
                SET current_status = 'RED',
                    previous_status = 'GREEN',
                    fault_type = 'packet_loss',
                    estimated_fix_time = %s,
                    status_changed_at = %s,
                    last_checked = NOW()
                WHERE subscriber_id = %s
            """, (estimated_fix, changed_at, sub_id))

        # 5. Update YELLOW subscribers
        # Sorun YENİ başlamış olsun (5dk persistence koruması)
        for sub_id in targets_yellow:
            changed_at = datetime.now()
            
            cursor.execute("""
                UPDATE subscriber_status
                SET current_status = 'YELLOW',
                    previous_status = 'GREEN',
                    fault_type = 'high_latency',
                    status_changed_at = %s,
                    last_checked = NOW()
                WHERE subscriber_id = %s
            """, (changed_at, sub_id))

        conn.commit()
        print("✅ Database seeding complete!")
        print(f"🔴 RED: {len(targets_red)}")
        print(f"🟡 YELLOW: {len(targets_yellow)}")
        print(f"🟢 GREEN: {len(all_ids) - len(targets_red) - len(targets_yellow)}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error seeding DB: {e}")

if __name__ == "__main__":
    seed_database_status()
