"""
clean.py
--------
Reads the raw JSON files from data/raw/ and turns each one into a clean
CSV file in data/processed/.

This file does ONE job: turn messy text ("1,23,456", "12%", "-") into
clean numbers, and save the result as a tidy table.

Output format (same shape for every file, one row per metric+period):
    metric, period, period_type, value, unit
"""

import json
import re

import pandas as pd

# raw filename (without .json) -> (output csv name, is this annual or quarterly?)
SECTION_MAP = {
    "profit_loss": ("profit_loss.csv", "annual"),
    "quarters": ("quarterly_profit_loss.csv", "quarterly"),
    "balance_sheet": ("balance_sheet.csv", "annual"),
    "cash_flow": ("cash_flow.csv", "annual"),
    "ratios": ("ratios.csv", "annual"),
}


def clean_number(text):
    """
    Turn a raw cell like "1,23,456" or "12.5%" or "-" into a number.
    Returns (value, unit).

    If the cell has no real number in it (blank, "-", "NA"), we return
    None instead of 0 -- missing data and zero are NOT the same thing.
    """
    text = text.strip()

    if text in ("", "-", "--", "NA", "N/A"):
        return None, "crore"

    unit = "percent" if "%" in text else "crore"

    # Keep only digits, minus sign, and decimal point. This removes
    # commas, %, currency symbols, spaces, etc.
    digits_only = re.sub(r"[^0-9.\-]", "", text)

    if digits_only in ("", "-", "."):
        return None, unit

    try:
        return float(digits_only), unit
    except ValueError:
        print(f"  Could not read value: {text!r}")
        return None, unit


def clean_one_section(section_key):
    raw_path = f"data/raw/{section_key}.json"
    try:
        with open(raw_path, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"Raw file not found, skipping: {raw_path}")
        return None

    csv_name, period_type = SECTION_MAP[section_key]
    periods = raw["periods"]

    # Turn the wide {metric: [values]} shape into a long list of rows,
    # one row per (metric, period) pair.
    rows = []
    for metric, values in raw["rows"].items():
        if len(values) != len(periods):
            # If the number of values doesn't match the number of periods,
            # something went wrong when scraping. Skip it instead of
            # guessing which value belongs to which period.
            print(f"  Skipping '{metric}': {len(values)} values but {len(periods)} periods.")
            continue

        for period, raw_value in zip(periods, values):
            value, unit = clean_number(raw_value)
            rows.append({
                "metric": metric,
                "period": period,
                "period_type": period_type,
                "value": value,
                "unit": unit,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        print(f"  No data produced for '{section_key}'.")
        return df

    # Make sure the value column is really numeric (not text).
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    out_path = f"data/processed/{csv_name}"
    df.to_csv(out_path, index=False)
    print(f"  Wrote {out_path} ({len(df)} rows)")
    return df


def clean_all():
    for section_key in SECTION_MAP:
        print(f"Cleaning: {section_key}")
        clean_one_section(section_key)


if __name__ == "__main__":
    clean_all()
