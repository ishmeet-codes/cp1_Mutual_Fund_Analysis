from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def normalize_label(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def find_matching_column(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_label(column): column for column in frame.columns}
    for candidate in candidates:
        candidate_key = normalize_label(candidate)
        if candidate_key in normalized:
            return normalized[candidate_key]
    for column in frame.columns:
        lowered = column.lower()
        if any(token in lowered for token in candidates):
            return column
    return None


def load_csv_datasets(raw_dir: Path) -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    csv_files = sorted(raw_dir.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV file(s) in {raw_dir}")

    for csv_path in csv_files:
        frame = pd.read_csv(csv_path)
        datasets[csv_path.stem] = frame
        print(f"\n=== {csv_path.name} ===")
        print("shape:", frame.shape)
        print("dtypes:")
        print(frame.dtypes)
        print("head:")
        print(frame.head())

        anomalies: list[str] = []
        if frame.columns.duplicated().any():
            anomalies.append("duplicate column names")
        unnamed_columns = [column for column in frame.columns if str(column).startswith("Unnamed")]
        if unnamed_columns:
            anomalies.append(f"unnamed columns: {unnamed_columns}")
        duplicate_rows = int(frame.duplicated().sum())
        if duplicate_rows:
            anomalies.append(f"{duplicate_rows} duplicated row(s)")
        missing_counts = frame.isna().sum().sort_values(ascending=False)
        missing_counts = missing_counts[missing_counts > 0]
        if not missing_counts.empty:
            anomalies.append(f"missing values in {list(missing_counts.index)}")

        if anomalies:
            print("anomalies:", "; ".join(anomalies))
        else:
            print("anomalies: none detected by the basic checks")

    if not csv_files:
        print("No CSV datasets were available in data/raw.")

    return datasets


def explore_fund_master(frame: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    column_groups = {
        "fund_house": ["fund_house", "fund house"],
        "category": ["category"],
        "sub_category": ["sub_category", "sub-category", "sub category"],
        "risk_grade": ["risk", "risk_grade", "risk grade"],
    }

    for label, aliases in column_groups.items():
        column = find_matching_column(frame, aliases)
        if column:
            unique_values = sorted(frame[column].dropna().astype(str).unique().tolist())
            summary[label] = {"column": column, "unique_values": unique_values}
            print(f"Unique values for {column}:")
            print(unique_values)

    possible_code_columns = [
        column
        for column in frame.columns
        if any(token in column.lower() for token in ["amfi", "scheme_code", "scheme code", "code"])
    ]
    print("Possible AMFI code columns:", possible_code_columns)
    summary["possible_code_columns"] = possible_code_columns
    return summary


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> dict[str, Any]:
    fund_code_column = find_matching_column(fund_master, ["amfi_code", "scheme_code", "scheme code", "code"])
    nav_code_column = find_matching_column(nav_history, ["amfi_code", "scheme_code", "scheme code", "code"])

    if not fund_code_column or not nav_code_column:
        return {
            "status": "skipped",
            "reason": "expected AMFI/code columns were not found",
            "fund_code_column": fund_code_column,
            "nav_code_column": nav_code_column,
        }

    fund_codes = pd.to_numeric(fund_master[fund_code_column], errors="coerce").dropna().astype(int)
    nav_codes = pd.to_numeric(nav_history[nav_code_column], errors="coerce").dropna().astype(int)

    fund_set = set(fund_codes.tolist())
    nav_set = set(nav_codes.tolist())
    missing_codes = sorted(fund_set - nav_set)

    print(f"AMFI code count in fund_master: {len(fund_set)}")
    print(f"AMFI code count in nav_history: {len(nav_set)}")
    print(f"Codes in fund_master but not nav_history: {len(missing_codes)}")
    print("Sample missing codes:", missing_codes[:20])

    return {
        "status": "complete",
        "fund_code_column": fund_code_column,
        "nav_code_column": nav_code_column,
        "fund_code_count": len(fund_set),
        "nav_code_count": len(nav_set),
        "missing_codes": missing_codes,
    }


def build_summary(datasets: dict[str, pd.DataFrame]) -> dict[str, Any]:
    summary_rows = []
    for name, frame in datasets.items():
        summary_rows.append(
            {
                "dataset": name,
                "shape": frame.shape,
                "missing_cells": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
                "duplicate_columns": [column for column in frame.columns[frame.columns.duplicated()]] or None,
                "unnamed_columns": [column for column in frame.columns if str(column).startswith("Unnamed")] or None,
            }
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("dataset")
    print(summary_df.to_string(index=False))

    anomaly_notes: list[str] = []
    for _, row in summary_df.iterrows():
        notes: list[str] = []
        if row["missing_cells"]:
            notes.append(f"{row['missing_cells']} missing cell(s)")
        if row["duplicate_rows"]:
            notes.append(f"{row['duplicate_rows']} duplicate row(s)")
        if row["duplicate_columns"]:
            notes.append("duplicate column names")
        if row["unnamed_columns"]:
            notes.append("unnamed columns present")
        if notes:
            anomaly_notes.append(f"{row['dataset']}: {', '.join(notes)}")

    if anomaly_notes:
        print("Anomaly notes:")
        for note in anomaly_notes:
            print(f"- {note}")
    else:
        print("Anomaly notes: none detected by the basic checks")

    return {
        "datasets_found": len(datasets),
        "datasets": summary_rows,
        "anomaly_notes": anomaly_notes,
    }


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    datasets = load_csv_datasets(RAW_DIR)
    summary: dict[str, Any] = build_summary(datasets)

    fund_master = datasets.get("01_fund_master")
    nav_history = datasets.get("02_nav_history")
    if fund_master is not None:
        summary["fund_master"] = explore_fund_master(fund_master)
    if fund_master is not None and nav_history is not None:
        summary["amfi_validation"] = validate_amfi_codes(fund_master, nav_history)

    output_path = PROCESSED_DIR / "data_quality_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"Saved summary to {output_path}")


if __name__ == "__main__":
    main()