-- Q1: Top 5 funds by AUM
SELECT fund_house, SUM(aum_crore) as total_aum
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum DESC
LIMIT 5;

-- Q2: Average NAV per month
SELECT strftime('%Y-%m', date) as month,
       ROUND(AVG(nav), 2) as avg_nav
FROM fact_nav
GROUP BY month
ORDER BY month;

-- Q3: SIP inflow YoY growth
SELECT strftime('%Y', month) as year,
       ROUND(SUM(sip_inflow_crore), 2) as total_sip
FROM fact_sip_industry
GROUP BY year
ORDER BY year;

-- Q4: Transactions by state
SELECT state, COUNT(*) as tx_count,
       SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- Q5: Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Top 5 funds by Sharpe Ratio
SELECT f.scheme_name, p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

-- Q7: SIP count by age group
SELECT age_group, COUNT(*) as sip_count,
       ROUND(AVG(amount_inr), 0) as avg_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY age_group
ORDER BY age_group;

-- Q8: Funds with Max Drawdown worse than -20%
SELECT f.scheme_name, p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.max_drawdown_pct < -20
ORDER BY p.max_drawdown_pct ASC;

-- Q9: T30 vs B30 split
SELECT city_tier,
       COUNT(*) as tx_count,
       SUM(amount_inr) as total_invested
FROM fact_transactions
GROUP BY city_tier;

-- Q10: Monthly NAV for HDFC Top 100
SELECT strftime('%Y-%m', date) as month,
       ROUND(AVG(nav), 2) as avg_nav
FROM fact_nav
WHERE amfi_code = '125497'
GROUP BY month
ORDER BY month;