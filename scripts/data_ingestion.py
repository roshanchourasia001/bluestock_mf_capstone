import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

files = {
    "fund_master":        "01_fund_master.csv",
    "nav_history":        "02_nav_history.csv",
    "aum_by_fund_house":  "03_aum_by_fund_house.csv",
    "monthly_sip":        "04_monthly_sip_inflows.csv",
    "category_inflows":   "05_category_inflows.csv",
    "folio_count":        "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_tx":        "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices":  "10_benchmark_indices.csv",
}

print("=" * 55)
print("BLUESTOCK MF — DATA INGESTION REPORT")
print("=" * 55)

for name, filename in files.items():
    filepath = RAW / filename
    if filepath.exists():
        df = pd.read_csv(filepath)
        print(f"\n📂 {filename}")
        print(f"   Shape   : {df.shape}")
        print(f"   Columns : {list(df.columns)}")
        print(f"   Nulls   : {df.isnull().sum().sum()}")
        print(f"   Dupes   : {df.duplicated().sum()}")
        print(df.head(2).to_string())
    else:
        print(f"\n❌ Not found: {filename}")

print("\n✅ Ingestion complete!")