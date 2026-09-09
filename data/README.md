# Data

Input data for this project are obtained from the Copernicus Climate Data Store
(CDS).

## Dataset

ERA5-Land reanalysis.

## Study period and domain

- Context period: 1–30 June 2026
- Heatwave period: 18–30 June 2026
- Domain: 47–55°N, 5–16°E

## Variables

- 2 m temperature
- Volumetric soil water layer 1

Raw NetCDF files are intentionally excluded from version control because they
can be reproduced using:

```text
scripts/download_era5land.py