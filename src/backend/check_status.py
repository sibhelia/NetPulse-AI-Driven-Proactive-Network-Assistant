import psycopg2
from collections import Counter

# DB Config
DB_CONFIG = {
    "dbname": "netpulse_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def check_status_distribution():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("📊 Checking database status distribution...")
        
        cursor.execute("SELECT current_status FROM subscriber_status")
        statuses = [row[0] for row in cursor.fetchall()]
        
        counts = Counter(statuses)
        total = len(statuses)
        
        print(f"Total Records: {total}")
        for status, count in counts.items():
            print(f"- {status}: {count} ({count/total*100:.1f}%)")
            
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        print(f"Total Customers: {customer_count}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error checking DB: {e}")

if __name__ == "__main__":
    check_status_distribution()
