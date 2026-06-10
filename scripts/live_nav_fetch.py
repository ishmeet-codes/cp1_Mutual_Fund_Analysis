from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


@dataclass(frozen=True)
class Scheme:
    code: int
    label: str


DEFAULT_SCHEMES: list[Scheme] = [
    Scheme(125497, "HDFC Top 100 Direct"),
    Scheme(119551, "SBI Bluechip"),
    Scheme(120503, "ICICI Bluechip"),
    Scheme(118632, "Nippon Large Cap"),
    Scheme(119092, "Axis Bluechip"),
    Scheme(120841, "Kotak Bluechip"),
]


def fetch_nav_history(scheme: Scheme) -> pd.DataFrame:
    url = f"https://api.mfapi.in/mf/{scheme.code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    frame = pd.DataFrame(payload.get("data", []))
    if frame.empty:
        frame = pd.DataFrame(columns=["scheme_code", "scheme_label", "date", "nav"])
    else:
        frame["scheme_code"] = scheme.code
        frame["scheme_label"] = scheme.label
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce", dayfirst=True)
        if "nav" in frame.columns:
            frame["nav"] = pd.to_numeric(frame["nav"], errors="coerce")
        ordered = [column for column in ["scheme_code", "scheme_label", "date", "nav"] if column in frame.columns]
        frame = frame[ordered + [column for column in frame.columns if column not in ordered]]

    output_path = RAW_DIR / f"nav_{scheme.code}.csv"
    frame.to_csv(output_path, index=False)
    print(f"Saved {output_path.name} with shape {frame.shape}")
    return frame


def fetch_many(schemes: Iterable[Scheme]) -> dict[int, pd.DataFrame]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[int, pd.DataFrame] = {}
    for scheme in schemes:
        results[scheme.code] = fetch_nav_history(scheme)
    return results


def main() -> None:
    fetch_many(DEFAULT_SCHEMES)


if __name__ == "__main__":
    main()