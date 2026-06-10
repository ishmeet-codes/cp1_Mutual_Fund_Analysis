# Bluestock Mutual Fund Analysis (Capstone)

Repository for the mutual fund analytics capstone: data ingestion, cleaning, performance metrics, investor cohort analysis, portfolio concentration, and recommender functionality.

## What’s included
- `data/raw/` — original CSVs and NAV files.
- `data/processed/` — cleaned CSVs used by notebooks and loaders.
- `data/db/` — SQLite data warehouse (created by scripts; not recommended to commit).
- `notebooks/` — analysis notebooks (EDA, performance, advanced analytics).
- `scripts/` — utility scripts:
  - `etl_pipeline.py` — ETL wrapper (DB init + fetch + ingestion)
  - `load_to_db.py` — load processed CSVs into SQLite `dim_`/`fact_` tables
  - `recommender.py` — simple risk-based recommender (CLI)
  - `generate_presentation.py` — create a starter PPTX from charts
  - `live_nav_fetch.py` — fetch NAVs from `mfapi.in`
- `sql/schema.sql` — SQLite schema for the data warehouse.
- `reports/` — generated charts and starter `Presentation.pptx`.
- `.github/workflows/etl_schedule.yml` — scheduled ETL (weekdays 20:00 UTC).

## Quickstart

1. Create and activate a Python virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Initialize the SQLite schema (creates `data/db/bluestock_mf.db`):

```powershell
python scripts/etl_pipeline.py --init-db-only
```

3. Run full ETL (fetch default NAVs and run ingestion checks):

```powershell
python scripts/etl_pipeline.py
```

4. Load processed CSVs into the SQLite warehouse (populate `dim_`/`fact_` tables):

```powershell
python scripts/load_to_db.py
```

5. Run the recommender:

```powershell
python scripts/recommender.py Moderate 3
```

6. Generate starter presentation:

```powershell
python scripts/generate_presentation.py
```

## Notebooks
- Open notebooks in `notebooks/` (e.g., `notebooks/05_advanced_analytics.ipynb`) to reproduce plots and CSV outputs like `var_cvar_report.csv`, `rolling_sharpe_chart.png`, `investor_cohort_summary.csv`, `sip_continuity.csv`, and `top_hhi_funds.csv`.

## Git / repository hygiene
- `.gitignore` includes `*.db` and other common ignores. If a DB was committed, remove it from the index before pushing:

```bash
git rm --cached data/db/bluestock_mf.db
git commit -m "Remove committed SQLite DB and ignore *.db"
git push
```

## Deliverables mapping (evaluation)
- D1 ETL: `scripts/etl_pipeline.py`, `live_nav_fetch.py`.
- D2 DB: `data/db/bluestock_mf.db` (schema in `sql/schema.sql`), loaded via `scripts/load_to_db.py`.
- D3 EDA: notebooks in `notebooks/`.
- D4 Performance metrics: `notebooks/Performance_Analytics.ipynb` and CSVs in project root.
- D5 Dashboard: `dashboard/bluestock_mf.pbix` (Power BI file).
- D6 Advanced analytics: `notebooks/05_advanced_analytics.ipynb`, outputs in root.
- D7 Reports/Slides: `reports/Presentation.pptx` (starter).

## Bonus tasks (available to implement)
- B1: Scheduled ETL — implemented via GitHub Actions in `.github/workflows/etl_schedule.yml`.
- B2: Streamlit app — not yet implemented (I can scaffold `app.py`).
- B3: Monte Carlo NAV projection — not yet implemented.
- B4: Markowitz optimization — not yet implemented.
- B5: HTML email report generator — not yet implemented.

## Notes & recommendations
- Avoid committing `.db` files — share `sql/schema.sql` instead.
- Use `Path` for file paths in scripts — existing code follows this convention.
- Ensure `requirements.txt` reflects runtime needs (added `python-pptx`).

If you want, I can:
- Remove the DB from Git history and commit the removal.
- Scaffold any bonus task (pick one to start).
- Expand the final report and convert it to PDF.

---
Updated: 2026-06-10
