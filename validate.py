"""
validate.py
-----------
Checks the cleaned CSV files for obvious problems, and writes a simple
report to data/processed/validation_report.json.

This file does ONE job: catch mistakes before anyone trusts the data.
Each check just prints PASS or FAIL and adds a line to the report.
"""

import json

import pandas as pd

EXPECTED_FILES = [
    "profit_loss.csv",
    "quarterly_profit_loss.csv",
    "balance_sheet.csv",
    "cash_flow.csv",
    "ratios.csv",
]

# A real Screener table should have at least this many rows (metrics).
# If it has way fewer, the scraper probably grabbed the wrong thing.
MIN_ROWS = 5


def check(results, name, passed, detail):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")
    results.append({"check": name, "passed": bool(passed), "detail": detail})


def run_checks():
    results = []

    for filename in EXPECTED_FILES:
        path = f"data/processed/{filename}"

        # Check 1: does the file exist at all?
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            check(results, "file_exists", False, f"{filename} is missing.")
            continue
        check(results, "file_exists", True, f"{filename} found.")

        # Check 2: does it have a reasonable number of rows?
        n_metrics = df["metric"].nunique()
        check(
            results,
            "enough_rows",
            n_metrics >= MIN_ROWS,
            f"{filename} has {n_metrics} distinct metrics (expected at least {MIN_ROWS}).",
        )

        # Check 3: is the value column actually numbers?
        is_numeric = pd.api.types.is_numeric_dtype(df["value"])
        check(
            results,
            "value_is_numeric",
            is_numeric,
            f"{filename}: value column type is {df['value'].dtype}.",
        )

        # Check 4: how much data is missing?
        missing_rate = df["value"].isna().mean()
        check(
            results,
            "missing_data_rate",
            missing_rate < 0.4,
            f"{filename}: {missing_rate:.0%} of values are missing.",
        )

        # Check 5: any exact duplicate rows?
        dupes = df.duplicated(subset=["metric", "period"]).sum()
        check(
            results,
            "no_duplicates",
            dupes == 0,
            f"{filename}: {dupes} duplicate metric+period rows found.",
        )

    return results


def main():
    results = run_checks()

    passed = sum(r["passed"] for r in results)
    total = len(results)
    print(f"\n{passed}/{total} checks passed.")

    with open("data/processed/validation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved data/processed/validation_report.json")


if __name__ == "__main__":
    main()
