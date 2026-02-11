import psycopg2

conn = psycopg2.connect(
    dbname='netpulse_db', user='postgres', 
    password='admin', host='localhost', port='5432'
)
cur = conn.cursor()

# Check customers table columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'customers'")
print("Customers columns:", [r[0] for r in cur.fetchall()])

# Check tickets count
cur.execute("SELECT COUNT(*) FROM tickets")
print("Tickets count:", cur.fetchone()[0])

# Check if any tickets exist
cur.execute("SELECT ticket_id, subscriber_id, status, priority FROM tickets LIMIT 5")
rows = cur.fetchall()
print("Tickets:")
for r in rows:
    print(f"  #{r[0]} sub:{r[1]} status:{r[2]} priority:{r[3]}")

conn.close()
