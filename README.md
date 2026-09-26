# Reliance Industries — Financial Data Pipeline (Simple Version)

A small pipeline that scrapes Reliance Industries' financial data from
Screener.in, cleans it, checks it for errors, and shows it on a basic
web dashboard.

## Files

```
scraper.py         -- downloads the page, saves raw tables to data/raw/
clean.py            -- turns raw data into clean CSVs in data/processed/
validate.py          -- checks the clean data for problems
crosscheck.py        -- compares one quarter against the official RIL filing
run_pipeline.py       -- runs all of the above in order
dashboard/            -- simple HTML/CSS/JS page to view the results
```

## Setup

```
pip install -r requirements.txt
```

## Run everything

```
python run_pipeline.py
```

This will:
1. Scrape Screener.in and save raw data to `data/raw/`
2. Clean it into `data/processed/*.csv`
3. Run checks and save `data/processed/validation_report.json`
4. Copy everything into `dashboard/data/` so the dashboard can show it

## View the dashboard

Browsers won't load local files with `fetch()`, so you need a simple server:

```
cd dashboard
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Cross-check against the official filing

1. Open the RIL official Q1 FY27 PDF.
2. Fill in the real numbers in `OFFICIAL_FIGURES` inside `crosscheck.py`.
3. Run:
```
python crosscheck.py
```

## Data format

Every CSV file has the same columns:

| column      | meaning                                   |
|-------------|--------------------------------------------|
| metric      | the row name, e.g. "Sales"                 |
| period      | the reporting period, e.g. "Mar 2024"      |
| period_type | "annual" or "quarterly"                    |
| value       | the number (blank if missing, never 0)     |
| unit        | "crore" or "percent"                       |
