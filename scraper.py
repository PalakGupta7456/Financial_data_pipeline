"""
scraper.py
----------
Downloads the Reliance Industries page from Screener.in and saves
the raw financial tables to data/raw/ as JSON files.

This file does ONE job: get the data off the page and save it,
exactly as found. No cleaning happens here.
"""

import json
import time

import requests
from bs4 import BeautifulSoup

URL = "https://www.screener.in/company/RELIANCE/consolidated/"

# The id of each table section on the Screener page, and what we want to call it.
SECTIONS = {
    "profit_loss": "profit-loss",
    "quarters": "quarters",
    "balance_sheet": "balance-sheet",
    "cash_flow": "cash-flow",
    "ratios": "ratios",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_page():
    """Download the page and return a BeautifulSoup object."""
    print(f"Fetching {URL} ...")
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    # Save the raw HTML so we always have proof of exactly what we scraped.
    with open("data/raw/full_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    time.sleep(1)  # be polite to the server
    return BeautifulSoup(response.text, "lxml")


def read_one_table(soup, section_id):
    """
    Find the table for one section (e.g. "profit-loss") and read it into
    a simple structure: a list of periods (column headers) and a dict of
    {row_label: [values]}.
    """
    section = soup.find(id=section_id)
    if section is None:
        print(f"  WARNING: could not find section '{section_id}' on the page.")
        return None

    table = section.find("table")
    if table is None:
        print(f"  WARNING: no table found inside section '{section_id}'.")
        return None

    # Read the column headers (the periods, e.g. "Mar 2023", "Mar 2024").
    # We read these from the actual header row instead of guessing, so this
    # still works even if Screener adds or removes a year.
    header_row = table.find("thead").find_all("tr")[-1]
    header_cells = header_row.find_all(["th", "td"])
    periods = [cell.get_text(strip=True) for cell in header_cells[1:]]

    # Read every data row. The first cell is the row label (e.g. "Sales"),
    # the rest are the values for each period.
    rows = {}
    for tr in table.find("tbody").find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        label = " ".join(cells[0].get_text().split())  # clean up whitespace
        if not label:
            continue
        values = [cell.get_text(strip=True) for cell in cells[1:]]
        rows[label] = values

    return {"periods": periods, "rows": rows}


def scrape_all():
    soup = get_page()

    for name, section_id in SECTIONS.items():
        print(f"Reading section: {name}")
        table_data = read_one_table(soup, section_id)

        if table_data is None:
            print(f"  -> SKIPPED (section missing)")
            continue

        out_path = f"data/raw/{name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(table_data, f, indent=2)
        print(f"  -> saved to {out_path}")


if __name__ == "__main__":
    scrape_all()
