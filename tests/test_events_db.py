import psycopg2
import os
import dotenv

dotenv.load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PGDB_HOST", "pg-tribevibe-tribevibe.b.aivencloud.com"),
    port=os.getenv("PGDB_PORT", 28769),
    user=os.getenv("PGDB_USER", "avnadmin"),
    password=os.getenv("PGDB_PASSWORD", "set password in .env file"),
    dbname=os.getenv("PGDB_NAME", "tribevibe"),
    sslmode=os.getenv("PGDB_SSLMODE", "require")
)
print("Connected to the database successfully.")
cur = conn.cursor()
cur.execute("""
    SELECT id, title, description, date, time, location, organizer_id, created_at
    FROM events
    ORDER BY date, time
""")
events = cur.fetchall()
print("Events:")
for event in events:
    print(f"ID: {event[0]}, Title: {event[1]}, Description: {event[2]}, Date: {event[3]}, Time: {event[4]}, Location: {event[5]}, Organizer ID: {event[6]}, Created At: {event[7]}")

cur.close()
conn.close()
