# June 2026 Heatwave over Germany

A small, reproducible analysis of near-surface temperature and soil-moisture
conditions during the June 2026 heatwave over Germany using ERA5-Land
reanalysis data.

## Objectives

This project examines the evolution of:

- 2-m air temperature
- surface soil moisture

during June 2026 over Germany.

The project is designed as a compact and reproducible climate-data analysis
workflow using Python and data from the Copernicus Climate Data Store.

## Data

ERA5-Land reanalysis data are obtained from the Copernicus Climate Data Store
(CDS).

The initial analysis uses:

- 2 m temperature
- volumetric soil water layer 1
- 1–30 June 2026
- a geographic domain covering Germany and its immediate surroundings

Raw ERA5-Land data are not stored in this repository. A Python download script
is provided so that the input dataset can be reproduced from CDS.

## Repository structure

```text
data/       Information about input data
scripts/    Data download, analysis and plotting scripts
figures/    Figures produced by the analysis
results/    Derived numerical results



pwd
cat > data/README.md <<'EOF'
# Data

Input data for this project are obtained from the Copernicus Climate Data Store
(CDS).

The analysis uses ERA5-Land reanalysis data for June 2026.

Raw NetCDF files are intentionally excluded from version control because they
can be reproduced using the download script in:

scripts/download_era5land.py
