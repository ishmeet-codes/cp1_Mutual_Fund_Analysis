from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_DIR = PROJECT_ROOT / "data" / "db"
DB_PATH = DB_DIR / "bluestock_mf.db"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def init_db(db_path: Path, schema_path: Path) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Initializing SQLite DB at %s", db_path)
    with sqlite3.connect(db_path) as conn:
        sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(sql)
    logging.info("DB initialized using schema %s", schema_path)


def run_full_etl():
    # Import here to keep module import cheap when init-only
    from scripts.live_nav_fetch import DEFAULT_SCHEMES, fetch_many
    from scripts.data_ingestion import main as ingestion_main

    logging.info("Fetching NAVs for default schemes")
    try:
        fetch_many(DEFAULT_SCHEMES)
    except Exception as exc:  # pragma: no cover - network call
        logging.exception("NAV fetch failed: %s", exc)

    logging.info("Running data ingestion checks and generating processed outputs")
    try:
        ingestion_main()
    except Exception:
        logging.exception("Data ingestion failed")

    logging.info("ETL complete; you can extend to load processed CSVs into the DB")


def parse_args():
    p = argparse.ArgumentParser(description="ETL pipeline wrapper for Bluestock MF capstone")
    p.add_argument("--init-db-only", action="store_true", help="Only initialize SQLite DB from schema and exit")
    return p.parse_args()


def main():
    init_logging()
    args = parse_args()
    if args.init_db_only:
        init_db(DB_PATH, SCHEMA_SQL)
        return

    # default: init DB if missing, then run full ETL
    if not DB_PATH.exists():
        init_db(DB_PATH, SCHEMA_SQL)
    run_full_etl()


if __name__ == "__main__":
    main()
