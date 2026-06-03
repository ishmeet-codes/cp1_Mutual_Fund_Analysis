# Mutual Fund Data Dictionary

This dictionary documents the cleaned datasets loaded into SQLite.

## dim_fund
Source file: `01_fund_master.csv`
Cleaned file: `cleaned_01_fund_master.csv`
Purpose: Core fund master dimension.

| Column | Type | Business definition |
| --- | --- | --- |
| amfi_code | INTEGER | Unique AMFI scheme code used across fund datasets. |
| fund_house | TEXT | Asset management company or fund house. |
| scheme_name | TEXT | Official scheme name. |
| category | TEXT | High-level fund category such as Equity or Debt. |
| sub_category | TEXT | More specific strategy bucket for the scheme. |
| plan | TEXT | Plan type such as Regular or Direct. |
| launch_date | DATE | Scheme launch date parsed to ISO date. |
| benchmark | TEXT | Reference benchmark used by the fund. |
| expense_ratio_pct | REAL | Annual expense ratio percentage. |
| exit_load_pct | REAL | Exit load percentage applicable on redemption. |
| min_sip_amount | REAL | Minimum SIP investment amount. |
| min_lumpsum_amount | REAL | Minimum lumpsum investment amount. |
| fund_manager | TEXT | Primary fund manager name. |
| risk_category | TEXT | Risk label assigned to the fund. |
| sebi_category_code | INTEGER | Internal category code used for grouping funds. |

## fact_nav
Source file: `02_nav_history.csv`
Cleaned file: `cleaned_02_nav_history.csv`
Purpose: Daily NAV fact table with calendar gaps filled by forward fill.

| Column | Type | Business definition |
| --- | --- | --- |
| amfi_code | INTEGER | Foreign key to dim_fund. |
| date | DATE | Daily observation date in ISO format. |
| nav | REAL | Net asset value for the scheme on the given date. |
| is_forward_filled | INTEGER | 1 when the row was created by forward-filling a holiday or weekend gap. |

## fact_aum
Source file: `03_aum_by_fund_house.csv`
Cleaned file: `cleaned_03_aum_by_fund_house.csv`
Purpose: Fund-house AUM snapshot table.

| Column | Type | Business definition |
| --- | --- | --- |
| date | DATE | Snapshot date in ISO format. |
| fund_house | TEXT | Fund house that owns the AUM snapshot. |
| aum_lakh_crore | REAL | AUM in lakh crore units. |
| aum_crore | REAL | AUM in crore units. |
| num_schemes | INTEGER | Count of schemes managed by the fund house. |

## fact_monthly_sip
Source file: `04_monthly_sip_inflows.csv`
Cleaned file: `cleaned_04_monthly_sip_inflows.csv`
Purpose: Monthly SIP inflow fact table.

| Column | Type | Business definition |
| --- | --- | --- |
| month | DATE | Month start date for the observation. |
| sip_inflow_crore | REAL | SIP inflows in crore. |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore. |
| new_sip_accounts_lakh | REAL | New SIP accounts in lakh. |
| sip_aum_lakh_crore | REAL | SIP-linked AUM in lakh crore. |
| yoy_growth_pct | REAL | Year-over-year SIP inflow growth percentage. |

## fact_category_inflows
Source file: `05_category_inflows.csv`
Cleaned file: `cleaned_05_category_inflows.csv`
Purpose: Monthly category-wise net inflows.

| Column | Type | Business definition |
| --- | --- | --- |
| month | DATE | Month start date for the observation. |
| category | TEXT | Fund category bucket. |
| net_inflow_crore | REAL | Net inflow amount in crore. |

## fact_industry_folio_count
Source file: `06_industry_folio_count.csv`
Cleaned file: `cleaned_06_industry_folio_count.csv`
Purpose: Monthly folio counts across the industry.

| Column | Type | Business definition |
| --- | --- | --- |
| month | DATE | Month start date for the observation. |
| total_folios_crore | REAL | Total folios in crore. |
| equity_folios_crore | REAL | Equity folios in crore. |
| debt_folios_crore | REAL | Debt folios in crore. |
| hybrid_folios_crore | REAL | Hybrid folios in crore. |
| others_folios_crore | REAL | Other folios in crore. |

## fact_performance
Source file: `07_scheme_performance.csv`
Cleaned file: `cleaned_07_scheme_performance.csv`
Purpose: Scheme performance snapshot fact table.

| Column | Type | Business definition |
| --- | --- | --- |
| amfi_code | INTEGER | Foreign key to dim_fund. |
| scheme_name | TEXT | Scheme name repeated for easy reporting. |
| fund_house | TEXT | Fund house name repeated for easy reporting. |
| category | TEXT | Fund category. |
| plan | TEXT | Plan type. |
| return_1yr_pct | REAL | Trailing 1-year return percentage. |
| return_3yr_pct | REAL | Trailing 3-year return percentage. |
| return_5yr_pct | REAL | Trailing 5-year return percentage. |
| benchmark_3yr_pct | REAL | 3-year benchmark return percentage. |
| alpha | REAL | Alpha over the comparison benchmark. |
| beta | REAL | Beta relative to the benchmark. |
| sharpe_ratio | REAL | Sharpe ratio. |
| sortino_ratio | REAL | Sortino ratio. |
| std_dev_ann_pct | REAL | Annualized standard deviation percentage. |
| max_drawdown_pct | REAL | Maximum drawdown percentage. |
| aum_crore | REAL | Assets under management in crore. |
| expense_ratio_pct | REAL | Expense ratio percentage. |
| morningstar_rating | INTEGER | Morningstar rating score. |
| risk_grade | TEXT | Risk grade assigned to the scheme. |

## fact_transactions
Source file: `08_investor_transactions.csv`
Cleaned file: `cleaned_08_investor_transactions.csv`
Purpose: Investor transaction fact table.

| Column | Type | Business definition |
| --- | --- | --- |
| investor_id | TEXT | Pseudonymous investor identifier. |
| transaction_date | DATE | Date of the transaction in ISO format. |
| amfi_code | INTEGER | Foreign key to dim_fund. |
| transaction_type | TEXT | Canonical transaction type: SIP, Lumpsum, or Redemption. |
| amount_inr | REAL | Transaction amount in INR. |
| state | TEXT | Investor state. |
| city | TEXT | Investor city. |
| city_tier | TEXT | City tier label such as T30 or B30. |
| age_group | TEXT | Investor age bucket. |
| gender | TEXT | Investor gender label. |
| annual_income_lakh | REAL | Annual income in lakh. |
| payment_mode | TEXT | Payment channel used for the transaction. |
| kyc_status | TEXT | KYC completion status. |

## fact_portfolio_holdings
Source file: `09_portfolio_holdings.csv`
Cleaned file: `cleaned_09_portfolio_holdings.csv`
Purpose: Portfolio holdings fact table.

| Column | Type | Business definition |
| --- | --- | --- |
| amfi_code | INTEGER | Foreign key to dim_fund. |
| stock_symbol | TEXT | Stock ticker symbol. |
| stock_name | TEXT | Company name. |
| sector | TEXT | Economic sector. |
| weight_pct | REAL | Portfolio weight percentage. |
| market_value_cr | REAL | Market value in crore. |
| current_price_inr | REAL | Latest observed stock price in INR. |
| portfolio_date | DATE | Portfolio snapshot date. |

## fact_benchmark_indices
Source file: `10_benchmark_indices.csv`
Cleaned file: `cleaned_10_benchmark_indices.csv`
Purpose: Benchmark index price history.

| Column | Type | Business definition |
| --- | --- | --- |
| date | DATE | Observation date in ISO format. |
| index_name | TEXT | Benchmark index name. |
| close_value | REAL | Closing index level. |
