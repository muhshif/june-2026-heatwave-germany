# Data

Input data for this project are obtained from the Copernicus Climate Data Store
(CDS).

The analysis uses ERA5-Land reanalysis data for June 2026.

Raw NetCDF files are intentionally excluded from version control because they
can be reproduced using:

```text
scripts/download_era5land.py
```