# Earthquake Detective

A small, end-to-end **batch data engineering project** built to practice API ingestion, data transformation, analytical modeling, data quality testing, and Python orchestration.

The pipeline retrieves historical earthquake events from the **USGS Earthquake API**, stores raw GeoJSON, transforms it into Parquet, and builds an analytical dataset using **DuckDB and dbt**.

> This is a learning project, not a real-time earthquake monitoring service.

## Architecture

```text
USGS Earthquake API
        |
        v
Python extraction (src/extract.py)
        |
        v
Bronze: timestamped raw GeoJSON
        |
        v
Pandas transformation (src/transform.py)
        |
        v
Silver: validated, deduplicated Parquet
        |
        v
DuckDB + dbt
        |
        +--> stg_earthquakes (view)
        |         |
        |         +--> data quality tests
        |         |
        |         v
        +--> mart_earthquake_daily (table)
```

The entire process can be run through `src/pipeline.py`.

## Technology stack

- **Python** and **requests** — USGS API ingestion
- **pandas** — cleaning, type conversion, and deduplication
- **Parquet / PyArrow** — columnar storage for the Silver dataset
- **DuckDB** — local analytical database and Parquet queries
- **dbt Core + dbt-duckdb** — SQL models, dependencies, and tests
- **Git / GitHub** — version control

## Dataset

The extraction is configured for **January 1–31, 2025** (API range: `2025-01-01` to `2025-02-01`), within:

- Latitude: **35 to 46**
- Longitude: **55 to 85**
- Minimum magnitude: **2.5**

Source: [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/).

A successful local run on October 31, 2026 retrieved **36 earthquake features** and transformed **36 records**. Results may differ if the upstream catalog is revised.

## Project structure

```text
earthquake_detective/
├── src/
│   ├── extract.py              # Fetch and save raw USGS GeoJSON
│   ├── transform.py            # Validate and write Silver Parquet
│   └── pipeline.py             # Run extraction, transformation, and dbt
├── earthquake_dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_earthquakes.sql
│   │   │   └── schema.yml
│   │   └── marts/
│   │       └── mart_earthquake_daily.sql
│   └── tests/
│       └── assert_valid_coordinates.sql
├── analysis/
├── requirements.txt
└── README.md
```

The pipeline creates `data/bronze/`, `data/silver/`, and the local DuckDB database as needed. Generated data and database files are not committed.

## Getting started

Requires **Python 3.12** and a local terminal. Commands below assume a macOS/Linux shell.

```bash
git clone https://github.com/Fienny/earthquake_detective.git
cd earthquake_detective

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the full pipeline **from the repository root**:

```bash
python -m src.pipeline
```

This command:
1. Calls the USGS API and saves timestamped Bronze JSON.
2. Cleans, converts, validates, and deduplicates earthquake records.
3. Writes `data/silver/earthquakes.parquet`.
4. Runs `dbt build` from the `earthquake_dbt` directory, creating the staging view, executing tests, and building the daily mart.

To run dbt separately:

```bash
cd earthquake_dbt
dbt debug --profiles-dir .
dbt build --profiles-dir .
dbt show --select mart_earthquake_daily --profiles-dir .
```

**Note:** Run `python -m src.pipeline` from the repository root: the extraction and transformation modules currently use relative data paths. Run the full pipeline at least once before invoking dbt directly, so the Parquet input exists.

## Data transformations

The Silver transformation:
- Flattens USGS GeoJSON properties and coordinates into columns.
- Converts earthquake and update timestamps from Unix milliseconds to UTC.
- Coerces numeric columns into numeric types.
- Keeps the most recently updated record per earthquake event ID.
- Rejects records with missing/blank event IDs, invalid coordinates, or missing event/update timestamps.

The staging model reads the Parquet file and filters to non-null magnitudes of at least 2.5.

The Gold model, `mart_earthquake_daily`, aggregates events by date:

| Column | Description |
| --- | --- |
| `event_date` | UTC event date |
| `earthquake_count` | Number of events on that date |
| `avg_magnitude` | Average magnitude, rounded to two decimals |
| `max_magnitude` | Maximum magnitude |
| `avg_depth_km` | Average depth in kilometers, rounded to two decimals |

## Data quality

dbt includes generic tests for required fields and unique event IDs, plus a custom SQL test for coordinate validity.

The latest verified full pipeline run completed with **11/11 successful dbt results**: **2 models and 9 tests**.

## Limitations and next steps

- The extraction currently uses a **fixed historical date range**, not a live rolling window.
- The database and Parquet files are local; there is no cloud deployment or scheduled execution.
- Paths for generated data are relative to the launch directory.
- The project is intentionally small and focuses on core batch data engineering concepts.

## Why I built this

I built Earthquake Detective as a hands-on exercise to understand how data moves from an external API through raw and curated storage into tested analytical models. The goal was to implement and connect the components myself, rather than add infrastructure that a small dataset does not need.
