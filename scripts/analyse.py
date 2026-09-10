"""
Analyse ERA5-Land temperature and soil moisture for June 2026.

Calculations
------------
1. Convert hourly 2 m temperature from K to degC.
2. Calculate daily maximum 2 m temperature.
3. Calculate daily mean surface soil moisture.
4. Calculate area-weighted domain-mean time series.
5. Compare the pre-heatwave and heatwave periods.
6. Calculate the spatial correlation between soil moisture and temperature.

Heatwave period:
    18-30 June 2026

Pre-heatwave period:
    1-17 June 2026
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

INPUT_FILE = Path("data/raw/era5land_june2026.nc")

PROCESSED_DIR = Path("data/processed")
RESULTS_DIR = Path("results")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_FILE = PROCESSED_DIR / "era5land_daily_june2026.nc"
DAILY_CSV = RESULTS_DIR / "daily_domain_mean.csv"
SUMMARY_CSV = RESULTS_DIR / "event_summary.csv"


# ---------------------------------------------------------------------
# Analysis periods
# ---------------------------------------------------------------------

PRE_START = "2026-06-01"
PRE_END = "2026-06-17"

HEATWAVE_START = "2026-06-18"
HEATWAVE_END = "2026-06-30"


# ---------------------------------------------------------------------
# Read hourly ERA5-Land data
# ---------------------------------------------------------------------

print(f"Opening {INPUT_FILE} ...")

ds = xr.open_dataset(INPUT_FILE)

print("Input variables:", list(ds.data_vars))
print("Input dimensions:", dict(ds.sizes))


# ---------------------------------------------------------------------
# Temperature: Kelvin -> degrees Celsius
# ---------------------------------------------------------------------

t2m_c = ds["t2m"] - 273.15

t2m_c.attrs["long_name"] = "2 metre temperature"
t2m_c.attrs["units"] = "degC"


# ---------------------------------------------------------------------
# Daily statistics
# ---------------------------------------------------------------------

daily_tmax = t2m_c.resample(valid_time="1D").max()

daily_sm = ds["swvl1"].resample(valid_time="1D").mean()

daily_tmax.name = "tmax"
daily_tmax.attrs["long_name"] = "Daily maximum 2 metre temperature"
daily_tmax.attrs["units"] = "degC"

daily_sm.name = "swvl1"
daily_sm.attrs["long_name"] = "Daily mean volumetric soil water layer 1"
daily_sm.attrs["units"] = "m3 m-3"


# ---------------------------------------------------------------------
# Area-weighted domain averages
#
# Latitude weighting accounts approximately for the changing grid-cell
# area with latitude.
# ---------------------------------------------------------------------

weights = np.cos(np.deg2rad(ds["latitude"]))

domain_tmax = daily_tmax.weighted(weights).mean(
    dim=("latitude", "longitude")
)

domain_sm = daily_sm.weighted(weights).mean(
    dim=("latitude", "longitude")
)


# ---------------------------------------------------------------------
# Save daily domain-mean time series
# ---------------------------------------------------------------------

daily_df = pd.DataFrame(
    {
        "date": pd.to_datetime(daily_tmax["valid_time"].values),
        "tmax_c": domain_tmax.values,
        "soil_moisture_m3_m3": domain_sm.values,
    }
)

daily_df.to_csv(DAILY_CSV, index=False)

print(f"Saved {DAILY_CSV}")


# ---------------------------------------------------------------------
# Heatwave and pre-heatwave fields
# ---------------------------------------------------------------------

pre_tmax = daily_tmax.sel(
    valid_time=slice(PRE_START, PRE_END)
).mean("valid_time")

pre_sm = daily_sm.sel(
    valid_time=slice(PRE_START, PRE_END)
).mean("valid_time")

heatwave_tmax = daily_tmax.sel(
    valid_time=slice(HEATWAVE_START, HEATWAVE_END)
).mean("valid_time")

heatwave_sm = daily_sm.sel(
    valid_time=slice(HEATWAVE_START, HEATWAVE_END)
).mean("valid_time")

soil_moisture_change = heatwave_sm - pre_sm

soil_moisture_change.name = "soil_moisture_change"
soil_moisture_change.attrs["long_name"] = (
    "Heatwave minus pre-heatwave mean surface soil moisture"
)
soil_moisture_change.attrs["units"] = "m3 m-3"


# ---------------------------------------------------------------------
# Spatial correlation:
# event-mean soil moisture versus event-mean Tmax
# ---------------------------------------------------------------------

x = heatwave_sm.values.ravel()
y = heatwave_tmax.values.ravel()

valid = np.isfinite(x) & np.isfinite(y)

correlation_r = np.corrcoef(
    x[valid],
    y[valid],
)[0, 1]


# ---------------------------------------------------------------------
# Domain-mean event statistics
# ---------------------------------------------------------------------

hw_mask = (
    (daily_df["date"] >= HEATWAVE_START)
    & (daily_df["date"] <= HEATWAVE_END)
)

pre_mask = (
    (daily_df["date"] >= PRE_START)
    & (daily_df["date"] <= PRE_END)
)

hw_df = daily_df.loc[hw_mask]
pre_df = daily_df.loc[pre_mask]

peak_index = hw_df["tmax_c"].idxmax()

peak_date = daily_df.loc[peak_index, "date"]
peak_tmax = daily_df.loc[peak_index, "tmax_c"]

mean_hw_tmax = hw_df["tmax_c"].mean()
mean_hw_sm = hw_df["soil_moisture_m3_m3"].mean()
mean_pre_sm = pre_df["soil_moisture_m3_m3"].mean()

summary_df = pd.DataFrame(
    [
        {
            "heatwave_start": HEATWAVE_START,
            "heatwave_end": HEATWAVE_END,
            "mean_heatwave_tmax_c": mean_hw_tmax,
            "peak_domain_tmax_c": peak_tmax,
            "peak_domain_tmax_date": peak_date.strftime("%Y-%m-%d"),
            "mean_preheatwave_soil_moisture_m3_m3": mean_pre_sm,
            "mean_heatwave_soil_moisture_m3_m3": mean_hw_sm,
            "soil_moisture_change_m3_m3": mean_hw_sm - mean_pre_sm,
            "spatial_sm_tmax_correlation_r": correlation_r,
        }
    ]
)

summary_df.to_csv(SUMMARY_CSV, index=False)

print(f"Saved {SUMMARY_CSV}")


# ---------------------------------------------------------------------
# Save processed fields
# ---------------------------------------------------------------------

processed = xr.Dataset(
    {
        "daily_tmax": daily_tmax,
        "daily_soil_moisture": daily_sm,
        "preheatwave_mean_tmax": pre_tmax,
        "preheatwave_mean_soil_moisture": pre_sm,
        "heatwave_mean_tmax": heatwave_tmax,
        "heatwave_mean_soil_moisture": heatwave_sm,
        "soil_moisture_change": soil_moisture_change,
    }
)

processed.attrs["title"] = (
    "ERA5-Land daily diagnostics for the June 2026 heatwave"
)
processed.attrs["heatwave_period"] = (
    f"{HEATWAVE_START} to {HEATWAVE_END}"
)
processed.attrs["preheatwave_period"] = (
    f"{PRE_START} to {PRE_END}"
)

processed.to_netcdf(PROCESSED_FILE)

print(f"Saved {PROCESSED_FILE}")


# ---------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------

print()
print("--------------------------------------------------")
print("June 2026 heatwave summary")
print("--------------------------------------------------")

print(
    f"Mean heatwave domain Tmax: "
    f"{mean_hw_tmax:.2f} degC"
)

print(
    f"Peak domain-mean Tmax: "
    f"{peak_tmax:.2f} degC on {peak_date:%Y-%m-%d}"
)

print(
    f"Mean pre-heatwave soil moisture: "
    f"{mean_pre_sm:.3f} m3 m-3"
)

print(
    f"Mean heatwave soil moisture: "
    f"{mean_hw_sm:.3f} m3 m-3"
)

print(
    f"Soil-moisture change: "
    f"{mean_hw_sm - mean_pre_sm:+.3f} m3 m-3"
)

print(
    f"Descriptive spatial SM-Tmax correlation: "
    f"r = {correlation_r:.3f}"
)

print("--------------------------------------------------")
print("Analysis completed.")