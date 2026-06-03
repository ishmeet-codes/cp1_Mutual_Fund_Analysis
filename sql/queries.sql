-- 1. Top 5 funds by AUM
SELECT
    amfi_code,
    scheme_name,
    aum_crore,
    expense_ratio_pct
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT
    substr(d.date, 1, 7) AS month,
    ROUND(AVG(f.nav), 4) AS avg_nav
FROM fact_nav AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY substr(d.date, 1, 7)
ORDER BY month;

-- 3. SIP YoY growth
SELECT
    month,
    yoy_growth_pct,
    sip_inflow_crore
FROM fact_monthly_sip
ORDER BY month;

-- 4. Transactions by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY transaction_count DESC, total_amount_inr DESC;

-- 5. Funds with expense_ratio < 1%
SELECT
    amfi_code,
    scheme_name,
    expense_ratio_pct,
    risk_grade
FROM fact_performance
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct ASC, scheme_name;

-- 6. Highest Sharpe ratio schemes
SELECT
    amfi_code,
    scheme_name,
    sharpe_ratio,
    sortino_ratio
FROM fact_performance
ORDER BY sharpe_ratio DESC, sortino_ratio DESC
LIMIT 10;

-- 7. Monthly transaction mix
SELECT
    substr(d.date, 1, 7) AS month,
    transaction_type,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount_inr), 2) AS amount_inr
FROM fact_transactions AS t
JOIN dim_date AS d
    ON t.date_key = d.date_key
GROUP BY substr(d.date, 1, 7), transaction_type
ORDER BY month, transaction_type;

-- 8. AUM by fund house trend
SELECT
    d.date,
    f.fund_house,
    ROUND(f.aum_crore, 2) AS aum_crore,
    f.num_schemes
FROM fact_aum AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
ORDER BY d.date, f.aum_crore DESC;

-- 9. Category inflows ranking
SELECT
    month,
    category,
    net_inflow_crore
FROM fact_category_inflows
ORDER BY month DESC, net_inflow_crore DESC;

-- 10. Portfolio sector concentration
SELECT
    sector,
    ROUND(SUM(weight_pct), 2) AS total_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC;
