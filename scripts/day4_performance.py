import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
PROCESSED = Path("data/processed")
RAW       = Path("data/raw")
REPORTS   = Path("reports")

# ─────────────────────────────────────────
# DATA LOAD
# ─────────────────────────────────────────
print("Loading data...")
nav         = pd.read_csv(PROCESSED / "clean_nav.csv", parse_dates=['date'])
funds       = pd.read_csv(PROCESSED / "clean_fund_master.csv")
performance = pd.read_csv(PROCESSED / "clean_performance.csv")
benchmark   = pd.read_csv(RAW / "10_benchmark_indices.csv", parse_dates=['date'])
print("✅ Data loaded!")

# Risk free rate (RBI repo rate proxy)
RF = 0.065 / 252  # Daily risk free rate

# ─────────────────────────────────────────
# STEP 1 — DAILY RETURNS
# ─────────────────────────────────────────
print("\n📊 Computing daily returns...")

nav = nav.sort_values(['amfi_code', 'date'])
nav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()
nav = nav.dropna(subset=['daily_return'])

nav.to_csv(PROCESSED / "returns_computed.csv", index=False)
print(f"✅ Daily returns computed: {nav.shape}")

# ─────────────────────────────────────────
# STEP 2 — CAGR CALCULATION
# ─────────────────────────────────────────
print("\n📊 Computing CAGR...")

def compute_cagr(nav_df, years):
    results = []
    for code, grp in nav_df.groupby('amfi_code'):
        grp = grp.sort_values('date')
        end_date = grp['date'].max()
        start_date = end_date - pd.DateOffset(years=years)
        period = grp[grp['date'] >= start_date]
        
        if len(period) < 50:
            continue
            
        nav_start = period['nav'].iloc[0]
        nav_end   = period['nav'].iloc[-1]
        n_years   = years
        
        cagr = (nav_end / nav_start) ** (1 / n_years) - 1
        results.append({
            'amfi_code': code,
            f'cagr_{years}yr': round(cagr * 100, 2)
        })
    return pd.DataFrame(results)

cagr_1yr = compute_cagr(nav, 1)
cagr_3yr = compute_cagr(nav, 3)
cagr_5yr = compute_cagr(nav, 5)

cagr_report = cagr_1yr.merge(cagr_3yr, on='amfi_code', how='outer')\
                       .merge(cagr_5yr, on='amfi_code', how='outer')\
                       .merge(funds[['amfi_code','scheme_name','fund_house']], 
                              on='amfi_code', how='left')

cagr_report.to_csv(PROCESSED / "cagr_report.csv", index=False)
print(f"✅ CAGR computed!")
print(cagr_report[['scheme_name','cagr_1yr','cagr_3yr','cagr_5yr']].head(5).to_string())

# ─────────────────────────────────────────
# STEP 3 — SHARPE RATIO
# ─────────────────────────────────────────
print("\n📊 Computing Sharpe Ratio...")

sharpe_list = []
for code, grp in nav.groupby('amfi_code'):
    returns = grp['daily_return'].dropna()
    if len(returns) < 50:
        continue
    
    excess_return = returns.mean() - RF
    std_dev       = returns.std()
    sharpe        = (excess_return / std_dev) * np.sqrt(252)
    
    sharpe_list.append({
        'amfi_code': code,
        'sharpe_ratio': round(sharpe, 4),
        'ann_return':   round(returns.mean() * 252 * 100, 2),
        'ann_std':      round(std_dev * np.sqrt(252) * 100, 2)
    })

sharpe_df = pd.DataFrame(sharpe_list)
sharpe_df.to_csv(PROCESSED / "sharpe_values.csv", index=False)
print(f"✅ Sharpe Ratio computed!")
print(sharpe_df.head(5).to_string())

# ─────────────────────────────────────────
# STEP 4 — SORTINO RATIO
# ─────────────────────────────────────────
print("\n📊 Computing Sortino Ratio...")

sortino_list = []
for code, grp in nav.groupby('amfi_code'):
    returns = grp['daily_return'].dropna()
    if len(returns) < 50:
        continue
    
    excess_return  = returns.mean() - RF
    downside       = returns[returns < 0]
    downside_std   = downside.std()
    sortino        = (excess_return / downside_std) * np.sqrt(252)
    
    sortino_list.append({
        'amfi_code':     code,
        'sortino_ratio': round(sortino, 4)
    })

sortino_df = pd.DataFrame(sortino_list)
sortino_df.to_csv(PROCESSED / "sortino_values.csv", index=False)
print(f"✅ Sortino Ratio computed!")

# ─────────────────────────────────────────
# STEP 5 — ALPHA & BETA
# ─────────────────────────────────────────
print("\n📊 Computing Alpha & Beta...")

# Nifty 100 benchmark returns
nifty100 = benchmark[benchmark['index_name'] == 'NIFTY100'].copy()
if len(nifty100) == 0:
    nifty100 = benchmark[benchmark['index_name'] == 'NIFTY50'].copy()

nifty100 = nifty100.sort_values('date')
nifty100['bench_return'] = nifty100['close_value'].pct_change()
nifty100 = nifty100.dropna()

alpha_beta_list = []
for code, grp in nav.groupby('amfi_code'):
    grp = grp.sort_values('date')
    merged = grp.merge(
        nifty100[['date', 'bench_return']], 
        on='date', how='inner'
    )
    
    if len(merged) < 50:
        continue
    
    slope, intercept, r_val, p_val, std_err = stats.linregress(
        merged['bench_return'], merged['daily_return']
    )
    
    beta  = round(slope, 4)
    alpha = round(intercept * 252 * 100, 4)
    
    alpha_beta_list.append({
        'amfi_code': code,
        'alpha':     alpha,
        'beta':      beta,
        'r_squared': round(r_val**2, 4)
    })

alpha_beta_df = pd.DataFrame(alpha_beta_list)
alpha_beta_df.to_csv(PROCESSED / "alpha_beta.csv", index=False)
print(f"✅ Alpha & Beta computed!")
print(alpha_beta_df.head(5).to_string())

# ─────────────────────────────────────────
# STEP 6 — MAX DRAWDOWN
# ─────────────────────────────────────────
print("\n📊 Computing Max Drawdown...")

drawdown_list = []
for code, grp in nav.groupby('amfi_code'):
    grp = grp.sort_values('date')
    nav_series   = grp['nav']
    running_max  = nav_series.cummax()
    drawdown     = (nav_series / running_max - 1)
    max_dd       = drawdown.min()
    
    drawdown_list.append({
        'amfi_code':      code,
        'max_drawdown':   round(max_dd * 100, 2)
    })

drawdown_df = pd.DataFrame(drawdown_list)
drawdown_df.to_csv(PROCESSED / "max_drawdown.csv", index=False)
print(f"✅ Max Drawdown computed!")

# ─────────────────────────────────────────
# STEP 7 — FUND SCORECARD
# ─────────────────────────────────────────
print("\n📊 Building Fund Scorecard...")

# Sab metrics merge karo
scorecard = cagr_report[['amfi_code','scheme_name','fund_house','cagr_3yr']]\
    .merge(sharpe_df[['amfi_code','sharpe_ratio']], on='amfi_code', how='left')\
    .merge(alpha_beta_df[['amfi_code','alpha','beta']], on='amfi_code', how='left')\
    .merge(drawdown_df[['amfi_code','max_drawdown']], on='amfi_code', how='left')\
    .merge(funds[['amfi_code','expense_ratio_pct']], on='amfi_code', how='left')

scorecard = scorecard.dropna()

# Rankings (higher = better rank = 1)
scorecard['rank_return']   = scorecard['cagr_3yr'].rank(ascending=False)
scorecard['rank_sharpe']   = scorecard['sharpe_ratio'].rank(ascending=False)
scorecard['rank_alpha']    = scorecard['alpha'].rank(ascending=False)
scorecard['rank_expense']  = scorecard['expense_ratio_pct'].rank(ascending=True)
scorecard['rank_drawdown'] = scorecard['max_drawdown'].rank(ascending=False)

# Composite Score (0-100)
n = len(scorecard)
scorecard['score'] = (
    0.30 * (1 - scorecard['rank_return']  / n) * 100 +
    0.25 * (1 - scorecard['rank_sharpe']  / n) * 100 +
    0.20 * (1 - scorecard['rank_alpha']   / n) * 100 +
    0.15 * (1 - scorecard['rank_expense'] / n) * 100 +
    0.10 * (1 - scorecard['rank_drawdown']/ n) * 100
).round(2)

scorecard = scorecard.sort_values('score', ascending=False)
scorecard.to_csv(PROCESSED / "fund_scorecard.csv", index=False)

print("\n🏆 TOP 10 FUNDS BY SCORECARD:")
print(scorecard[['scheme_name','cagr_3yr','sharpe_ratio',
                 'alpha','expense_ratio_pct','score']]\
      .head(10).to_string())

# ─────────────────────────────────────────
# STEP 8 — BENCHMARK CHART
# ─────────────────────────────────────────
print("\n📊 Chart: Top 5 vs Benchmark...")

top5_codes = scorecard['amfi_code'].head(5).tolist()
top5_nav   = nav[nav['amfi_code'].isin(top5_codes)].copy()
top5_nav   = top5_nav.merge(funds[['amfi_code','scheme_name']], on='amfi_code')

nifty50 = benchmark[benchmark['index_name']=='NIFTY50'].copy()
cutoff  = top5_nav['date'].min()
nifty50 = nifty50[nifty50['date'] >= cutoff]

fig, ax = plt.subplots(figsize=(14, 7))

# Normalize to 100
for code, grp in top5_nav.groupby('amfi_code'):
    grp  = grp.sort_values('date')
    name = grp['scheme_name'].iloc[0][:25]
    norm = grp['nav'] / grp['nav'].iloc[0] * 100
    ax.plot(grp['date'], norm, linewidth=1.8, label=name)

# Nifty 50
norm_nifty = nifty50['close_value'] / nifty50['close_value'].iloc[0] * 100
ax.plot(nifty50['date'], norm_nifty,
        color='black', linewidth=2.5,
        linestyle='--', label='NIFTY 50 (Benchmark)')

ax.set_title('Top 5 Funds vs NIFTY 50 — Normalized (Base=100)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Normalized Value')
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(REPORTS / "chart_benchmark.png", dpi=150)
plt.show()
print("✅ Benchmark chart saved!")

# ─────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────
print("\n" + "="*55)
print("🎉 DAY 4 COMPLETE!")
print("="*55)
print("Files saved:")
print("  ✅ returns_computed.csv")
print("  ✅ cagr_report.csv")
print("  ✅ sharpe_values.csv")
print("  ✅ sortino_values.csv")
print("  ✅ alpha_beta.csv")
print("  ✅ max_drawdown.csv")
print("  ✅ fund_scorecard.csv")
print("  ✅ chart_benchmark.png")