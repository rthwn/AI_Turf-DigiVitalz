import psycopg2, json
from backend.app.core.config import settings

conn = psycopg2.connect(
    host=settings.DB_HOST,
    port=5432,
    database="postgres",
    user="postgres",
    password=settings.DB_PASSWORD
)
cursor = conn.cursor()
cursor.execute("SELECT raw_result FROM audits ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()
raw = row[0]
print("ai_meta:", raw.get("ai_meta"))
print("usage:", raw.get("usage"))
print("performance:", raw.get("performance"))
conn.close()