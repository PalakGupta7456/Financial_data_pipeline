"""
crosscheck.py
-------------
Compares our scraped Q1 FY27 (June 2026) figures against the numbers
in RIL's official press release:

  Q1 FY2026-27 Financial & Operational Performance
  https://www.ril.com/sites/default/files/2026-07/Media_Release_RIL_Q1_FY2026-27_Financial_and_Operational_Performance.pdf

HOW TO USE:
1. Open the PDF above and find the figures listed below.
2. Type them into OFFICIAL_FIGURES.
3. Run this script. It prints a table comparing our data to the official numbers.
"""

import pandas as pd

# The period label as it appears in quarterly_profit_loss.csv -- check your
# actual file and adjust if Screener labels it differently.
TARGET_PERIOD = "Jun 2026"

# Fill these in from the official PDF (values in INR crore).
OFFICIAL_FIGURES = {
    "Sales": None,           # Revenue
    "Operating Profit": None,  # EBITDA
    "Depreciation": None,
    "Interest": None,        # Finance costs
    "Profit before tax": None,
    "Tax": None,
    "Net Profit": None,
}


def run():
    df = pd.read_csv("data/processed/quarterly_profit_loss.csv")

    print(f"{'Metric':<20} {'Screener':>12} {'Official':>12} {'Difference':>12}")
    for metric, official_value in OFFICIAL_FIGURES.items():
        row = df[(df["metric"] == metric) & (df["period"] == TARGET_PERIOD)]
        screener_value = row.iloc[0]["value"] if not row.empty else None

        if official_value is None:
            diff = "fill in official figure"
        elif screener_value is None:
            diff = "not found in scraped data"
        else:
            diff = round(screener_value - official_value, 1)

        print(f"{metric:<20} {str(screener_value):>12} {str(official_value):>12} {str(diff):>12}")


if __name__ == "__main__":
    run()
