import psycopg2
import os
import dotenv

dotenv.load_dotenv()
# Update these with your actual credentials
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
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
""")
tables = cur.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

cur.close()
conn.close()