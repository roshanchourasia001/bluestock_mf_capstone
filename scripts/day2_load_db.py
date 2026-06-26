import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

PROCESSED = Path("data/processed")
DB_PATH = "data/db/bluestock_mf.db"
Path("data/db").mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")

# Schema create karo
with engine.connect() as conn:
    with open("sql/schema.sql") as f:
        for stmt in f.read().split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
    conn.commit()
print("✅ Schema created!")

# Tables load karo
tables = {
    "dim_fund":          "clean_fund_master.csv",
    "fact_nav":          "clean_nav.csv",
    "fact_transactions": "clean_transactions.csv",
    "fact_performance":  "clean_performance.csv",
    "fact_aum":          "clean_aum.csv",
    "fact_sip_industry": "clean_sip_inflows.csv",
}

for table, filename in tables.items():
    try:
        df = pd.read_csv(PROCESSED / filename)
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"✅ {table}: {len(df)} rows loaded")
    except Exception as e:
        print(f"❌ {table} failed: {e}")

print("\n🎉 Database ready:", DB_PATH)