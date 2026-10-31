from pathlib import Path
import subprocess

# Import your existing extraction and transformation functions
from src.extract import extract_earthquake
from src.transform import transform_earthquakes

def run_pipeline():
    project_root = Path(__file__).resolve().parent.parent
    dbt_dir = project_root / "earthquake_dbt"

    # Step 1: Extract
    extract_path = extract_earthquake()
    print(f"Bronze saved: {extract_path}")

    # Step 2: Transform
    transform_path = transform_earthquakes(extract_path)
    print(f"Silver saved: {transform_path}")
    # Step 3: Execute dbt
    subprocess.run(
        ["dbt", "build", "--profiles-dir", "."],
        cwd=dbt_dir,
        check=True,
    )
    # Step 4: Success message
    print("Pipeline executed successfully!")

if __name__ == "__main__":
    run_pipeline()