import psycopg2
import os

# DB Config (same as main.py)
DB_CONFIG = {
    "dbname": "netpulse_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def reset_all_statuses():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔄 Resetting all subscriber statuses to GREEN...")
        
        # Reset everyone to GREEN, clear fault types and fix times
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
        
        rows_affected = cursor.rowcount
        conn.commit()
        print(f"✅ Successfully reset {rows_affected} subscribers to GREEN.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error resetting statuses: {e}")

if __name__ == "__main__":
    reset_all_statuses()
