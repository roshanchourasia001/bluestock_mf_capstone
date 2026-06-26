import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
PROCESSED = Path("data/processed")
RAW       = Path("data/raw")
REPORTS   = Path("reports")
REPORTS.mkdir(exist_ok=True)

# Style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ─────────────────────────────────────────
# DATA LOAD
# ─────────────────────────────────────────
print("Loading data...")
nav         = pd.read_csv(PROCESSED / "clean_nav.csv", parse_dates=['date'])
funds       = pd.read_csv(PROCESSED / "clean_fund_master.csv")
aum         = pd.read_csv(PROCESSED / "clean_aum.csv", parse_dates=['date'])
sip         = pd.read_csv(PROCESSED / "clean_sip_inflows.csv")
transactions= pd.read_csv(PROCESSED / "clean_transactions.csv")
performance = pd.read_csv(PROCESSED / "clean_performance.csv")
benchmark   = pd.read_csv(RAW / "10_benchmark_indices.csv", parse_dates=['date'])
category    = pd.read_csv(PROCESSED / "clean_category_inflows.csv")
folio       = pd.read_csv(PROCESSED / "clean_folio_count.csv")
print("✅ All data loaded!")

# ─────────────────────────────────────────
# CHART 1 — NAV TREND (Top 6 Funds)
# ─────────────────────────────────────────
print("\n📊 Chart 1: NAV Trends...")

top_funds = [119551, 120503, 118632, 119092, 120841, 125497]
nav_top = nav[nav['amfi_code'].isin(top_funds)].copy()
nav_top = nav_top.merge(funds[['amfi_code','scheme_name']], on='amfi_code')
nav_top['scheme_short'] = nav_top['scheme_name'].str[:25]

fig, ax = plt.subplots(figsize=(14, 6))
for code, grp in nav_top.groupby('amfi_code'):
    name = grp['scheme_short'].iloc[0]
    ax.plot(grp['date'], grp['nav'], label=name, linewidth=1.5)

ax.set_title('NAV Trends — Top 6 Funds (2022–2026)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('NAV (Rs.)')
ax.legend(fontsize=7, loc='upper left')
plt.tight_layout()
plt.savefig(REPORTS / "chart1_nav_trends.png", dpi=150)
plt.show()
print("✅ Chart 1 saved!")

# ─────────────────────────────────────────
# CHART 2 — AUM GROWTH BY FUND HOUSE
# ─────────────────────────────────────────
print("\n📊 Chart 2: AUM Growth...")

fig, ax = plt.subplots(figsize=(14, 6))
aum_pivot = aum.pivot_table(
    index='date', columns='fund_house', values='aum_crore', aggfunc='sum'
)
aum_pivot.plot(kind='bar', ax=ax, width=0.8)
ax.set_title('AUM Growth by Fund House (2022–2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Quarter')
ax.set_ylabel('AUM (Rs. Crore)')
ax.legend(fontsize=7, bbox_to_anchor=(1.01, 1))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(REPORTS / "chart2_aum_growth.png", dpi=150)
plt.show()
print("✅ Chart 2 saved!")

# ─────────────────────────────────────────
# CHART 3 — SIP INFLOW TREND
# ─────────────────────────────────────────
print("\n📊 Chart 3: SIP Inflow Trend...")

sip['month'] = pd.to_datetime(sip['month'])
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(sip['month'], sip['sip_inflow_crore'],
        color='royalblue', linewidth=2, marker='o', markersize=3)
ax.axhline(y=31002, color='red', linestyle='--', label='ATH: Rs.31,002 Cr (Dec 2025)')
ax.fill_between(sip['month'], sip['sip_inflow_crore'], alpha=0.3)
ax.set_title('Monthly SIP Inflow (Jan 2022 – Dec 2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('SIP Inflow (Rs. Crore)')
ax.legend()
plt.tight_layout()
plt.savefig(REPORTS / "chart3_sip_trend.png", dpi=150)
plt.show()
print("✅ Chart 3 saved!")

# ─────────────────────────────────────────
# CHART 4 — CATEGORY INFLOW HEATMAP
# ─────────────────────────────────────────
print("\n📊 Chart 4: Category Heatmap...")

category['month'] = pd.to_datetime(category['month'])
cat_pivot = category.pivot_table(
    index='category', columns='month', values='net_inflow_crore'
)
fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(cat_pivot, cmap='RdYlGn', ax=ax,
            linewidths=0.5, fmt='.0f', annot=False)
ax.set_title('Category-wise Net Inflows Heatmap (FY 2024-25)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(REPORTS / "chart4_category_heatmap.png", dpi=150)
plt.show()
print("✅ Chart 4 saved!")

# ─────────────────────────────────────────
# CHART 5 — INVESTOR AGE GROUP PIE
# ─────────────────────────────────────────
print("\n📊 Chart 5: Age Group Distribution...")

age_dist = transactions['age_group'].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].pie(age_dist.values, labels=age_dist.index,
            autopct='%1.1f%%', startangle=90)
axes[0].set_title('Investor Age Group Distribution', fontweight='bold')

age_sip = transactions[transactions['transaction_type']=='Sip']\
          .groupby('age_group')['amount_inr'].mean().sort_index()
axes[1].bar(age_sip.index, age_sip.values, color='steelblue')
axes[1].set_title('Average SIP Amount by Age Group', fontweight='bold')
axes[1].set_xlabel('Age Group')
axes[1].set_ylabel('Avg Amount (Rs.)')
plt.tight_layout()
plt.savefig(REPORTS / "chart5_demographics.png", dpi=150)
plt.show()
print("✅ Chart 5 saved!")

# ─────────────────────────────────────────
# CHART 6 — GEOGRAPHIC DISTRIBUTION
# ─────────────────────────────────────────
print("\n📊 Chart 6: Geographic Distribution...")

state_data = transactions.groupby('state')['amount_inr']\
             .sum().sort_values(ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].barh(state_data.index, state_data.values, color='teal')
axes[0].set_title('Total Investment by State', fontweight='bold')
axes[0].set_xlabel('Total Amount (Rs.)')

tier_data = transactions.groupby('city_tier')['amount_inr'].sum()
axes[1].pie(tier_data.values, labels=tier_data.index,
            autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
axes[1].set_title('T30 vs B30 City Split', fontweight='bold')

plt.tight_layout()
plt.savefig(REPORTS / "chart6_geographic.png", dpi=150)
plt.show()
print("✅ Chart 6 saved!")

# ─────────────────────────────────────────
# CHART 7 — FOLIO COUNT GROWTH
# ─────────────────────────────────────────
print("\n📊 Chart 7: Folio Count Growth...")

folio['month'] = pd.to_datetime(folio['month'])
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(folio['month'], folio['total_folios_crore'],
        color='purple', linewidth=2.5, marker='o')
ax.fill_between(folio['month'], folio['total_folios_crore'], alpha=0.2, color='purple')
ax.set_title('Total MF Folios Growth (2022–2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Folios (Crore)')
ax.annotate('26.12 Cr\n(Dec 2025)',
            xy=(folio['month'].iloc[-1], folio['total_folios_crore'].iloc[-1]),
            xytext=(-60, -30), textcoords='offset points',
            arrowprops=dict(arrowstyle='->'), fontsize=10, color='purple')
plt.tight_layout()
plt.savefig(REPORTS / "chart7_folio_growth.png", dpi=150)
plt.show()
print("✅ Chart 7 saved!")

# ─────────────────────────────────────────
# CHART 8 — CORRELATION MATRIX
# ─────────────────────────────────────────
print("\n📊 Chart 8: Correlation Matrix...")

top10_codes = nav['amfi_code'].unique()[:10]
nav_pivot = nav[nav['amfi_code'].isin(top10_codes)]\
            .pivot_table(index='date', columns='amfi_code', values='nav')
nav_returns = nav_pivot.pct_change().dropna()
corr = nav_returns.corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
            ax=ax, linewidths=0.5, vmin=-1, vmax=1)
ax.set_title('NAV Returns Correlation Matrix (Top 10 Funds)',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(REPORTS / "chart8_correlation.png", dpi=150)
plt.show()
print("✅ Chart 8 saved!")

# ─────────────────────────────────────────
# CHART 9 — SECTOR ALLOCATION
# ─────────────────────────────────────────
print("\n📊 Chart 9: Sector Allocation...")

portfolio = pd.read_csv(PROCESSED / "clean_portfolio.csv")
sector_wt = portfolio.groupby('sector')['weight_pct'].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(sector_wt.values, labels=sector_wt.index,
       autopct='%1.1f%%', startangle=90,
       pctdistance=0.85)
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
ax.add_artist(centre_circle)
ax.set_title('Sector Allocation Across Equity Funds', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(REPORTS / "chart9_sector.png", dpi=150)
plt.show()
print("✅ Chart 9 saved!")

# ─────────────────────────────────────────
# CHART 10 — BENCHMARK vs NAV
# ─────────────────────────────────────────
print("\n📊 Chart 10: Benchmark Comparison...")

nifty = benchmark[benchmark['index_name']=='NIFTY50'].copy()
nifty['normalized'] = nifty['close_value'] / nifty['close_value'].iloc[0] * 100

sbi_nav = nav[nav['amfi_code']==119551].copy()
sbi_nav['normalized'] = sbi_nav['nav'] / sbi_nav['nav'].iloc[0] * 100

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(nifty['date'], nifty['normalized'],
        label='NIFTY 50', color='orange', linewidth=2)
ax.plot(sbi_nav['date'], sbi_nav['normalized'],
        label='SBI Bluechip', color='blue', linewidth=2)
ax.set_title('SBI Bluechip vs NIFTY 50 (Normalized to 100)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Normalized Value (Base=100)')
ax.legend()
plt.tight_layout()
plt.savefig(REPORTS / "chart10_benchmark.png", dpi=150)
plt.show()
print("✅ Chart 10 saved!")

print("\n" + "="*50)
print("🎉 ALL 10 CHARTS COMPLETE!")
print(f"📁 Saved in: {REPORTS}")
print("="*50)