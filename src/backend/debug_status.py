import psycopg2

try:
    conn = psycopg2.connect(
        dbname="netpulse_db",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Check total count
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    print(f"Total Customers: {total_customers}")

    # Check non-green statuses
    cursor.execute("""
        SELECT c.subscriber_id, c.full_name, ss.current_status, ss.fault_type
        FROM customers c
        JOIN subscriber_status ss ON c.subscriber_id = ss.subscriber_id
        WHERE ss.current_status != 'GREEN'
    """)
    rows = cursor.fetchall()
    
    print(f"\nFaulty Subscribers ({len(rows)}):")
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | Status: {r[2]} | Fault: {r[3]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
