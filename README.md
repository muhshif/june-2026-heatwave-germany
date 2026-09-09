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

### Study scope

- **Context period:** 1–30 June 2026
- **Heatwave period:** 18–30 June 2026
- **Domain:** 47–55°N, 5–16°E
- **Dataset:** ERA5-Land
- **Variables:**
  - 2 m temperature
  - Volumetric soil water layer 1

The full month of June is used to provide context for the evolution of
temperature and soil moisture, while 18–30 June 2026 is treated as the
heatwave analysis period.

Raw ERA5-Land data are not stored in this repository. A Python download script
is provided so that the input dataset can be reproduced from CDS.

## Repository structure

```text
data/       Information about input data
scripts/    Data download, analysis and plotting scripts
figures/    Figures produced by the analysis
results/    Derived numerical results