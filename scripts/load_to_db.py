"""Load processed CSVs into SQLite data warehouse tables.

This script maps processed CSVs to the schema in sql/schema.sql and inserts rows.
It uses a simple date_key = YYYYMMDD integer convention.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
PROC = PROJECT_ROOT / "data" / "processed"


def date_to_key(dt: pd.Series) -> pd.Series:
    return dt.dt.strftime("%Y%m%d").astype(int)


def upsert_dim_date(conn, dates):
    cur = conn.cursor()
    unique_dates = pd.Series(dates.dropna().unique()).sort_values()
    for d in unique_dates:
        if pd.isna(d):
            continue
        date = pd.to_datetime(d)
        date_key = int(date.strftime("%Y%m%d"))
        cur.execute(
            "INSERT OR IGNORE INTO dim_date (date_key, date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend, is_month_end) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                date_key,
                date.strftime("%Y-%m-%d"),
                date.year,
                (date.month - 1) // 3 + 1,
                date.month,
                date.strftime("%B"),
                date.day,
                date.weekday(),
                date.strftime("%A"),
                1 if date.weekday() >= 5 else 0,
                1 if (date + pd.offsets.MonthEnd(0)).day == date.day else 0,
            ),
        )
    conn.commit()


def load_dim_fund(conn):
    path = PROC / "cleaned_01_fund_master.csv"
    if not path.exists():
        print("Skipping dim_fund: file not found", path)
        return
    df = pd.read_csv(path)
    df = df.rename(columns={c: c.strip() for c in df.columns})
    cols = [
        "amfi_code",
        "fund_house",
        "scheme_name",
        "category",
        "sub_category",
        "plan",
        "launch_date",
        "benchmark",
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
        "fund_manager",
        "risk_category",
        "sebi_category_code",
    ]
    insert_cols = [c for c in cols if c in df.columns]
    cur = conn.cursor()
    for _, row in df.iterrows():
        values = [row.get(c, None) for c in insert_cols]
        placeholders = ",".join(["?"] * len(insert_cols))
        cur.execute(
            f"INSERT OR REPLACE INTO dim_fund ({','.join(insert_cols)}) VALUES ({placeholders})",
            values,
        )
    conn.commit()


def load_fact_nav(conn):
    path = PROC / "cleaned_02_nav_history.csv"
    if not path.exists():
        print("Skipping fact_nav: file not found", path)
        return
    df = pd.read_csv(path, parse_dates=["date"])

    upsert_dim_date(conn, df["date"])
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO fact_nav (amfi_code, date_key, nav, is_forward_filled) VALUES (?,?,?,?)",
            (int(row["amfi_code"]), int(row["date_key"]), float(row["nav"]), int(row.get("is_forward_filled", 0))),
        )
    conn.commit()


def load_fact_performance(conn):
    path = PROC / "cleaned_07_scheme_performance.csv"
    if not path.exists():
        print("Skipping fact_performance: file not found", path)
        return
    df = pd.read_csv(path)
    cur = conn.cursor()
    cols = [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "plan",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade",
    ]
    insert_cols = [c for c in cols if c in df.columns]
    for _, row in df.iterrows():
        values = [row.get(c, None) for c in insert_cols]
        placeholders = ",".join(["?"] * len(insert_cols))
        cur.execute(
            f"INSERT OR REPLACE INTO fact_performance ({','.join(insert_cols)}) VALUES ({placeholders})",
            values,
        )
    conn.commit()


def load_fact_transactions(conn):
    path = PROC / "cleaned_08_investor_transactions.csv"
    if not path.exists():
        print("Skipping fact_transactions: file not found", path)
        return
    df = pd.read_csv(path, parse_dates=["transaction_date"])

    upsert_dim_date(conn, df["transaction_date"])
    df["date_key"] = df["transaction_date"].dt.strftime("%Y%m%d").astype(int)
    cur = conn.cursor()
    for idx, row in df.iterrows():
        tx_id = f"TX_{idx}_{int(row['date_key'])}"
        cur.execute(
            "INSERT OR REPLACE INTO fact_transactions (transaction_id, investor_id, date_key, amfi_code, transaction_type, amount_inr, state, city, city_tier, age_group, gender, annual_income_lakh, payment_mode, kyc_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                tx_id,
                row.get("investor_id"),
                int(row["date_key"]),
                int(row.get("amfi_code", 0)),
                row.get("transaction_type"),
                float(row.get("amount_inr", 0)) if not pd.isna(row.get("amount_inr")) else None,
                row.get("state"),
                row.get("city"),
                row.get("city_tier"),
                row.get("age_group"),
                row.get("gender"),
                float(row.get("annual_income_lakh")) if not pd.isna(row.get("annual_income_lakh")) else None,
                row.get("payment_mode"),
                row.get("kyc_status"),
            ),
        )
    conn.commit()


def load_fact_portfolio_holdings(conn):
    path = PROC / "cleaned_09_portfolio_holdings.csv"
    if not path.exists():
        print("Skipping fact_portfolio_holdings: file not found", path)
        return
    df = pd.read_csv(path, parse_dates=["portfolio_date"])

    upsert_dim_date(conn, df["portfolio_date"])
    df["portfolio_date_key"] = df["portfolio_date"].dt.strftime("%Y%m%d").astype(int)
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO fact_portfolio_holdings (amfi_code, stock_symbol, stock_name, sector, weight_pct, market_value_cr, current_price_inr, portfolio_date_key) VALUES (?,?,?,?,?,?,?,?)",
            (
                int(row.get("amfi_code", 0)),
                row.get("stock_symbol"),
                row.get("stock_name"),
                row.get("sector"),
                float(row.get("weight_pct", 0)) if not pd.isna(row.get("weight_pct")) else None,
                float(row.get("market_value_cr", 0)) if not pd.isna(row.get("market_value_cr")) else None,
                float(row.get("current_price_inr", 0)) if not pd.isna(row.get("current_price_inr")) else None,
                int(row.get("portfolio_date_key")),
            ),
        )
    conn.commit()


def main():
    if not DB_PATH.exists():
        print("DB not found at", DB_PATH)
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        load_dim_fund(conn)
        load_fact_nav(conn)
        load_fact_performance(conn)
        load_fact_transactions(conn)
        load_fact_portfolio_holdings(conn)
        print("Data loaded into DB")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
