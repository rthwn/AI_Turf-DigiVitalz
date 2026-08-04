"""
migrate_production.py

Run this ONCE after Railway deploys to create all tables in Supabase.

Usage (Windows):
  set DATABASE_URL=postgresql://postgres:PASSWORD@db.XXXX.supabase.co:5432/postgres
  python migrate_production.py
"""

import os
import sys

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    print("Run:  set DATABASE_URL=your_supabase_url")
    sys.exit(1)

if "sqlite" in DATABASE_URL:
    print("WARNING: You are pointing at SQLite, not Supabase")
    print("Make sure DATABASE_URL is your Supabase URL")

print(f"\nConnecting to: {DATABASE_URL[:50]}...")

try:
    from backend.app.db.session import Base, engine
    from backend.app.db.models.audit import Audit
    from backend.app.db.models.lead  import Lead

    # ── Create all tables ─────────────────────────────────
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created")

    # ── Run Change 6 migration (add new columns safely) ───
    from sqlalchemy import text, inspect

    inspector   = inspect(engine)
    lead_cols   = [c["name"] for c in inspector.get_columns("leads")]

    new_columns = [
        ("source",         "VARCHAR(20)  NOT NULL DEFAULT 'seo_audit'"),
        ("master_score",   "INTEGER"),
        ("pillar_scores",  "TEXT"),
        ("weakest_pillar", "VARCHAR(50)"),
        ("business_type",  "VARCHAR(50)"),
        ("business_name",  "VARCHAR(255)"),
    ]

    with engine.begin() as conn:
        for col_name, col_type in new_columns:
            if col_name not in lead_cols:
                conn.execute(
                    text(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
                )
                print(f"  ✓ Added column: leads.{col_name}")
            else:
                print(f"  · Already exists: leads.{col_name}")

        conn.execute(
            text("UPDATE leads SET source = 'seo_audit' WHERE source IS NULL")
        )

    print("\n✓ Migration complete — Supabase is ready\n")

except Exception as e:
    print(f"\nERROR: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    