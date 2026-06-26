# Data Dictionary — Bluestock MF Capstone

## 01_fund_master.csv
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | Unique AMFI scheme code |
| fund_house | TEXT | AMC name |
| scheme_name | TEXT | Full scheme name |
| category | TEXT | Equity/Debt/Hybrid |
| expense_ratio_pct | REAL | Annual expense ratio % |
| risk_category | TEXT | Low/Moderate/High/Very High |

## 02_nav_history.csv
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | TEXT | Foreign key to fund_master |
| date | DATE | Business day only |
| nav | REAL | NAV in Rs. |

## 08_investor_transactions.csv
| Column | Type | Description |
|--------|------|-------------|
| investor_id | TEXT | Unique ID |
| transaction_type | TEXT | SIP/Lumpsum/Redemption |
| amount_inr | INT | Transaction amount Rs. |
| state | TEXT | Investor state |
| kyc_status | TEXT | Verified/Pending |