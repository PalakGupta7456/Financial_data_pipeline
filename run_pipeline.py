"""
run_pipeline.py
----------------
Runs the whole pipeline, in order:
  1. scrape the website
  2. clean the raw data
  3. check the cleaned data for problems
  4. copy the results into the dashboard folder

Just run: python run_pipeline.py
"""

import shutil
from pathlib import Path

import scraper
import clean
import validate

DASHBOARD_DATA = Path("dashboard/data")


def main():
    print("=== STEP 1: Scraping ===")
    scraper.scrape_all()

    print("\n=== STEP 2: Cleaning ===")
    clean.clean_all()

    print("\n=== STEP 3: Validating ===")
    validate.main()

    print("\n=== STEP 4: Copying data to dashboard ===")
    DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)
    files_to_copy = [
        "profit_loss.csv",
        "quarterly_profit_loss.csv",
        "balance_sheet.csv",
        "cash_flow.csv",
        "ratios.csv",
        "validation_report.json",
    ]
    for filename in files_to_copy:
        src = Path("data/processed") / filename
        if src.exists():
            shutil.copy(src, DASHBOARD_DATA / filename)
            print(f"  copied {filename}")
        else:
            print(f"  skipped {filename} (not found)")

    print("\nDone! Open dashboard/index.html with a local server to view the results.")


if __name__ == "__main__":
    main()
