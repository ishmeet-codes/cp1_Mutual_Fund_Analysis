CREATE TABLE IF NOT EXISTS dim_fund (
        amfi_code INTEGER PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        plan TEXT,
        launch_date TEXT,
        benchmark TEXT,
        expense_ratio_pct REAL,
        exit_load_pct REAL,
        min_sip_amount REAL,
        min_lumpsum_amount REAL,
        fund_manager TEXT,
        risk_category TEXT,
        sebi_category_code INTEGER
    );

CREATE TABLE IF NOT EXISTS dim_date (
        date_key INTEGER PRIMARY KEY,
        date TEXT UNIQUE,
        year INTEGER,
        quarter INTEGER,
        month INTEGER,
        month_name TEXT,
        day INTEGER,
        day_of_week INTEGER,
        day_name TEXT,
        is_weekend INTEGER,
        is_month_end INTEGER
    );

CREATE TABLE IF NOT EXISTS fact_nav (
        nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER NOT NULL,
        date_key INTEGER NOT NULL,
        nav REAL NOT NULL,
        is_forward_filled INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_aum (
        aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_key INTEGER NOT NULL,
        fund_house TEXT NOT NULL,
        aum_lakh_crore REAL,
        aum_crore REAL,
        num_schemes INTEGER,
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_monthly_sip (
        month_key INTEGER PRIMARY KEY,
        month TEXT UNIQUE NOT NULL,
        sip_inflow_crore REAL,
        active_sip_accounts_crore REAL,
        new_sip_accounts_lakh REAL,
        sip_aum_lakh_crore REAL,
        yoy_growth_pct REAL,
        FOREIGN KEY (month_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_category_inflows (
        category_inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_key INTEGER NOT NULL,
        category TEXT NOT NULL,
        net_inflow_crore REAL,
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_industry_folio_count (
        folio_snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_key INTEGER NOT NULL,
        total_folios_crore REAL,
        equity_folios_crore REAL,
        debt_folios_crore REAL,
        hybrid_folios_crore REAL,
        others_folios_crore REAL,
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_performance (
        amfi_code INTEGER NOT NULL,
        scheme_name TEXT,
        fund_house TEXT,
        category TEXT,
        plan TEXT,
        return_1yr_pct REAL,
        return_3yr_pct REAL,
        return_5yr_pct REAL,
        benchmark_3yr_pct REAL,
        alpha REAL,
        beta REAL,
        sharpe_ratio REAL,
        sortino_ratio REAL,
        std_dev_ann_pct REAL,
        max_drawdown_pct REAL,
        aum_crore REAL,
        expense_ratio_pct REAL,
        morningstar_rating INTEGER,
        risk_grade TEXT,
        PRIMARY KEY (amfi_code, plan),
        FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
    );

CREATE TABLE IF NOT EXISTS fact_transactions (
        transaction_id TEXT PRIMARY KEY,
        investor_id TEXT,
        date_key INTEGER NOT NULL,
        amfi_code INTEGER NOT NULL,
        transaction_type TEXT,
        amount_inr REAL,
        state TEXT,
        city TEXT,
        city_tier TEXT,
        age_group TEXT,
        gender TEXT,
        annual_income_lakh REAL,
        payment_mode TEXT,
        kyc_status TEXT,
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key),
        FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
    );

CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
        holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER NOT NULL,
        stock_symbol TEXT,
        stock_name TEXT,
        sector TEXT,
        weight_pct REAL,
        market_value_cr REAL,
        current_price_inr REAL,
        portfolio_date_key INTEGER NOT NULL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
        FOREIGN KEY (portfolio_date_key) REFERENCES dim_date (date_key)
    );

CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
        benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_key INTEGER NOT NULL,
        index_name TEXT NOT NULL,
        close_value REAL,
        FOREIGN KEY (date_key) REFERENCES dim_date (date_key)
    );
