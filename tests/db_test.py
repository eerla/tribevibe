import psycopg2

# Update these with your actual credentials
conn = psycopg2.connect(
    host="pg-tribevibe-tribevibe.b.aivencloud.com",
    port=28769,
    user="avnadmin",
    password="AVNS_hHzR9EDrlesC9fjCo7Y",
    dbname="tribevibe",
    sslmode="require"
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