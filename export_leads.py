import psycopg2
import csv
from datetime import datetime
from backend.app.core.config import settings

conn = psycopg2.connect(
    host=settings.DB_HOST,
    port=5432,
    database="postgres",
    user="postgres.hmnemhywnkbfgeaisyjq",
    password=settings.DB_PASSWORD
)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        split_part(email, '@', 1) as name,
        email,
        url,
        website_url,
        score,
        grade,
        master_score,
        audit_score,
        pillar_scores,
        source,
        status,
        consent_at,
        org_id,
        job_id,
        ip_address,
        created_at
    FROM leads 
    WHERE email IS NOT NULL
    AND consent_at IS NOT NULL
    AND org_id IS NOT NULL
    AND master_score IS NOT NULL
    ORDER BY created_at DESC
""")

rows = cursor.fetchall()
headers = [
    'name', 'email', 'url', 'website_url',
    'score', 'grade', 'master_score', 'audit_score',
    'pillar_scores', 'source', 'status',
    'consent_at', 'org_id', 'job_id',
    'ip_address', 'created_at'
]

filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ Exported {len(rows)} clean leads to {filename}")
for row in rows:
    print(f"  → {row[0]} | score={row[3]} | consent={row[10]} | {row[14]}")

cursor.close()
conn.close()