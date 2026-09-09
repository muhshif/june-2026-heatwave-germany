"""
Download ERA5-Land data for the June 2026 heatwave project.

Domain:
    47–55°N, 5–16°E

Period:
    1–30 June 2026

Variables:
    - 2 m temperature
    - Volumetric soil water layer 1

Data source:
    Copernicus Climate Data Store (CDS)
"""

from pathlib import Path

import cdsapi


# ---------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "era5land_june2026.nc"


# ---------------------------------------------------------------------
# CDS request
# ---------------------------------------------------------------------

dataset = "reanalysis-era5-land"

request = {
    "variable": [
        "2m_temperature",
        "volumetric_soil_water_layer_1",
    ],
    "year": "2026",
    "month": "06",
    "day": [
        f"{day:02d}" for day in range(1, 31)
    ],
    "time": [
        f"{hour:02d}:00" for hour in range(24)
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",

    # CDS area convention:
    # [North, West, South, East]
    "area": [
        55,
        5,
        47,
        16,
    ],
}


# ---------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------

print("Submitting ERA5-Land request...")
print(f"Output: {OUTPUT_FILE}")

client = cdsapi.Client()
client.retrieve(dataset, request, str(OUTPUT_FILE))

print("Download completed.")