import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────
# 1. CLEAN nav_history.csv
# ─────────────────────────────────────────
def clean_nav():
    df = pd.read_csv(RAW / "02_nav_history.csv")
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort
    df = df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # Forward-fill missing NAV (holidays/weekends)
    df = df.set_index('date').groupby('amfi_code')['nav']\
           .apply(lambda x: x.resample('B').last().ffill())\
           .reset_index()
    
    # Validate NAV > 0
    df = df[df['nav'] > 0]
    
    df.to_csv(PROCESSED / "clean_nav.csv", index=False)
    print(f"✅ NAV cleaned: {df.shape}")
    return df

# ─────────────────────────────────────────
# 2. CLEAN investor_transactions.csv
# ─────────────────────────────────────────
def clean_transactions():
    df = pd.read_csv(RAW / "08_investor_transactions.csv")
    
    # Standardise transaction_type
    df['transaction_type'] = df['transaction_type'].str.strip().str.title()
    valid_types = ['Sip', 'Lumpsum', 'Redemption']
    df = df[df['transaction_type'].isin(valid_types)]
    
    # Validate amount > 0
    df = df[df['amount_inr'] > 0]
    
    # Fix date format
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Check KYC status
    df = df[df['kyc_status'].isin(['Verified', 'Pending'])]
    
    df.to_csv(PROCESSED / "clean_transactions.csv", index=False)
    print(f"✅ Transactions cleaned: {df.shape}")
    return df

# ─────────────────────────────────────────
# 3. CLEAN scheme_performance.csv
# ─────────────────────────────────────────
def clean_performance():
    df = pd.read_csv(RAW / "07_scheme_performance.csv")
    
    # Validate numeric return columns
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
                   'sharpe_ratio', 'alpha', 'beta']
    for col in return_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Flag negative Sharpe ratios
    df['sharpe_flag'] = df['sharpe_ratio'] < 0
    
    # Validate expense ratio range
    df = df[df['expense_ratio_pct'].between(0.1, 2.5)]
    
    df.to_csv(PROCESSED / "clean_performance.csv", index=False)
    print(f"✅ Performance cleaned: {df.shape}")
    return df

# ─────────────────────────────────────────
# 4. CLEAN remaining CSV files
# ─────────────────────────────────────────
def clean_remaining():
    files = {
        "01_fund_master.csv":        "clean_fund_master.csv",
        "03_aum_by_fund_house.csv":  "clean_aum.csv",
        "04_monthly_sip_inflows.csv":"clean_sip_inflows.csv",
        "05_category_inflows.csv":   "clean_category_inflows.csv",
        "06_industry_folio_count.csv":"clean_folio_count.csv",
        "09_portfolio_holdings.csv": "clean_portfolio.csv",
        "10_benchmark_indices.csv":  "clean_benchmark.csv",
    }
    
    for raw_file, clean_file in files.items():
        df = pd.read_csv(RAW / raw_file)
        
        # Date columns fix karo
        for col in df.columns:
            if 'date' in col.lower() or 'month' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Fill nulls
        df = df.fillna(method='ffill')
        
        df.to_csv(PROCESSED / clean_file, index=False)
        print(f"✅ {raw_file} → {clean_file} | Shape: {df.shape}")

if __name__ == "__main__":
    print("=" * 50)
    print("DAY 2 — DATA CLEANING")
    print("=" * 50)
    clean_nav()
    clean_transactions()
    clean_performance()
    clean_remaining()
    print("\n🎉 All files cleaned!")