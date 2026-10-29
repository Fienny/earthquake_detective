
from pathlib import Path
import json

import pandas as pd


def transform_earthquakes(input_path: Path) -> Path:
    """
    Read raw USGS GeoJSON, transform it into
    a clean dataset, and save it as Parquet.

    Returns:
        Path to the generated Parquet file.
    """

    records = []

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    for event in data.get("features", []):
        properties = event.get("properties") or {}
        geometry = event.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []

        record = {
            "event_id": event.get("id"),
            "event_time": properties.get("time"),
            "latitude": coordinates[1] if len(coordinates) > 1 else None,
            "longitude": coordinates[0] if len(coordinates) > 0 else None,
            "depth_km": coordinates[2] if len(coordinates) > 2 else None,
            "magnitude": properties.get("mag"),
            "place": properties.get("place"),
            "updated_at": properties.get("updated"),
        }

        records.append(record)

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("No earthquakes found in the input data.")

    # Convert numeric fields
    for column in ["latitude", "longitude", "magnitude", "depth_km"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert USGS Unix milliseconds into UTC timestamps
    for column in ["event_time", "updated_at"]:
        df[column] = pd.to_datetime(
            df[column],
            unit="ms",
            utc=True,
            errors="coerce",
        )

    # Keep the latest version of each earthquake
    df = (
        df.sort_values("updated_at", ascending=False)
        .drop_duplicates(subset=["event_id"], keep="first")
        .reset_index(drop=True)
    )

    # Validate event IDs, coordinates and timestamps
    df = df[
        df["event_id"].notna()
        & df["event_id"].astype("string").str.strip().ne("")
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & df["event_time"].notna()
        & df["updated_at"].notna()
    ].copy()

    if df.empty:
        raise ValueError("No valid earthquake records after validation.")

    # Save the Silver dataset
    output_path = Path("data/silver/earthquakes.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        output_path,
        engine="pyarrow",
        index=False,
    )

    print(f"Transformed {len(df)} earthquake records")
    print(f"Saved Silver dataset to: {output_path}")

    return output_path


if __name__ == "__main__":
    bronze_files = sorted(Path("data/bronze").glob("*.json"))

    if not bronze_files:
        raise FileNotFoundError("No Bronze JSON files found.")

    latest_file = bronze_files[-1]
    print(f"Processing: {latest_file}")

    transform_earthquakes(latest_file)
