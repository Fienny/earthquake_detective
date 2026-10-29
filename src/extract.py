import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

PARAMS = {
    "format": "geojson",
    "starttime": "2025-01-01",
    "endtime": "2025-02-01",
    "minlatitude": 35,
    "maxlatitude": 46,
    "minlongitude": 55,
    "maxlongitude": 85,
    "minmagnitude": 2.5,
    "orderby": "time",
}

OUTPUT_DIR = Path("data/bronze")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

def extract_earthquake() -> Path:
    logger.info("Extracting earthquake data from USGS API...")

    response = requests.get(
        API_URL,
        params=PARAMS,
        timeout=30
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("type") != "FeatureCollection":
        raise ValueError("Unexpected USGS response format")

    events = payload.get("features")

    if not isinstance(events, list):
        raise ValueError("Missing earthquake features")

    logger.info(f"Received {len(events)} earthquake features")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    output_path = OUTPUT_DIR / f"earthquake_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    logger.info(f"Raw data saved: {output_path}")

    return output_path

if __name__ == "__main__":
    extract_earthquake()