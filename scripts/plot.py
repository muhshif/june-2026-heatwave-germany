"""
Create figures for the June 2026 Germany heatwave analysis.

Figures
-------
1. Daily domain-mean Tmax and surface soil moisture.
2. Mean Tmax during the 18-30 June 2026 heatwave.
3. Spatial relationship between soil moisture and Tmax.
4. Mean surface soil moisture during the heatwave.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from cartopy.io import shapereader


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

DAILY_FILE = Path("results/daily_domain_mean.csv")
PROCESSED_FILE = Path("data/processed/era5land_daily_june2026.nc")
FIGURE_DIR = Path("figures")

FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Heatwave period
# ---------------------------------------------------------------------

HEATWAVE_START = pd.Timestamp("2026-06-18")
HEATWAVE_END = pd.Timestamp("2026-06-30")

DOMAIN = [5, 16, 47, 55]


# ---------------------------------------------------------------------
# Helper functions for Natural Earth boundaries
# ---------------------------------------------------------------------

def plot_geometry_boundary(
    ax,
    geometry,
    linewidth=0.6,
    color="black",
    zorder=5,
):
    """Plot a Shapely geometry on ordinary lon-lat Matplotlib axes."""

    geometry_type = geometry.geom_type

    if geometry_type == "Polygon":
        x, y = geometry.exterior.xy
        ax.plot(
            x,
            y,
            linewidth=linewidth,
            color=color,
            zorder=zorder,
        )

    elif geometry_type == "MultiPolygon":
        for polygon in geometry.geoms:
            plot_geometry_boundary(
                ax,
                polygon,
                linewidth=linewidth,
                color=color,
                zorder=zorder,
            )

    elif geometry_type == "LineString":
        x, y = geometry.xy
        ax.plot(
            x,
            y,
            linewidth=linewidth,
            color=color,
            zorder=zorder,
        )

    elif geometry_type == "MultiLineString":
        for line in geometry.geoms:
            plot_geometry_boundary(
                ax,
                line,
                linewidth=linewidth,
                color=color,
                zorder=zorder,
            )

    elif geometry_type == "GeometryCollection":
        for part in geometry.geoms:
            plot_geometry_boundary(
                ax,
                part,
                linewidth=linewidth,
                color=color,
                zorder=zorder,
            )


def add_country_boundaries(ax):
    """
    Add Natural Earth national boundaries.

    Germany is drawn slightly thicker than neighbouring countries.
    """

    countries_file = shapereader.natural_earth(
        resolution="50m",
        category="cultural",
        name="admin_0_countries",
    )

    reader = shapereader.Reader(countries_file)

    west, east, south, north = DOMAIN

    for record in reader.records():

        geometry = record.geometry

        minx, miny, maxx, maxy = geometry.bounds

        # Skip countries completely outside the study domain
        if (
            maxx < west
            or minx > east
            or maxy < south
            or miny > north
        ):
            continue

        country_name = record.attributes.get("ADMIN", "")

        if country_name == "Germany":
            linewidth = 1.4
        else:
            linewidth = 0.6

        plot_geometry_boundary(
            ax,
            geometry,
            linewidth=linewidth,
        )


def format_map_axes(ax):
    """Apply common lon-lat formatting to map figures."""

    ax.set_xlim(DOMAIN[0], DOMAIN[1])
    ax.set_ylim(DOMAIN[2], DOMAIN[3])

    ax.set_xticks([5, 7, 9, 11, 13, 15])
    ax.set_yticks([47, 49, 51, 53, 55])

    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    ax.grid(
        alpha=0.25,
        linewidth=0.5,
    )

    add_country_boundaries(ax)


# =====================================================================
# Figure 1: Daily evolution
# =====================================================================

daily = pd.read_csv(
    DAILY_FILE,
    parse_dates=["date"],
)

fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(
    daily["date"],
    daily["tmax_c"],
    marker="o",
    linewidth=1.5,
    color="tab:red",
    label="Daily Tmax",
)

ax1.set_xlabel("Date")
ax1.set_ylabel(
    "Daily maximum 2 m temperature (°C)",
    color="tab:red",
)

ax1.tick_params(
    axis="y",
    labelcolor="tab:red",
)

ax1.axvspan(
    HEATWAVE_START,
    HEATWAVE_END,
    alpha=0.15,
    color="tab:orange",
    label="Heatwave period",
)

ax2 = ax1.twinx()

ax2.plot(
    daily["date"],
    daily["soil_moisture_m3_m3"],
    marker="s",
    linewidth=1.5,
    color="tab:blue",
    label="Surface soil moisture",
)

ax2.set_ylabel(
    r"Volumetric soil moisture (m$^3$ m$^{-3}$)",
    color="tab:blue",
)

ax2.tick_params(
    axis="y",
    labelcolor="tab:blue",
)

ax1.set_title(
    "Temperature and surface soil moisture during June 2026"
)

ax1.grid(alpha=0.25)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="best",
)

fig.autofmt_xdate()
fig.tight_layout()

output = FIGURE_DIR / "june_timeseries.png"

fig.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)

print(f"Saved {output}")


# =====================================================================
# Read processed fields
# =====================================================================

ds = xr.open_dataset(PROCESSED_FILE)

tmax = ds["heatwave_mean_tmax"]
soil_moisture = ds["heatwave_mean_soil_moisture"]


# =====================================================================
# Figure 2: Heatwave Tmax spatial field
# =====================================================================

fig, ax = plt.subplots(figsize=(9, 7))

mesh = ax.pcolormesh(
    tmax["longitude"],
    tmax["latitude"],
    tmax.values,
    shading="auto",
    cmap="inferno",
)

format_map_axes(ax)

cbar = fig.colorbar(
    mesh,
    ax=ax,
    pad=0.03,
)

cbar.set_label(
    "Mean daily Tmax (°C)"
)

ax.set_title(
    "Mean daily maximum 2 m temperature\n"
    "18–30 June 2026"
)

fig.tight_layout()

output = FIGURE_DIR / "heatwave_temperature.png"

fig.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)

print(f"Saved {output}")


# =====================================================================
# Figure 3: Soil moisture vs Tmax
# =====================================================================

x = soil_moisture.values.ravel()
y = tmax.values.ravel()

valid = np.isfinite(x) & np.isfinite(y)

x = x[valid]
y = y[valid]

r = np.corrcoef(
    x,
    y,
)[0, 1]

fig, ax = plt.subplots(figsize=(7, 6))

ax.scatter(
    x,
    y,
    s=12,
    alpha=0.30,
    color="tab:blue",
)

slope, intercept = np.polyfit(
    x,
    y,
    1,
)

x_line = np.linspace(
    x.min(),
    x.max(),
    100,
)

y_line = slope * x_line + intercept

ax.plot(
    x_line,
    y_line,
    linewidth=2,
    color="black",
)

ax.set_xlabel(
    r"Mean surface soil moisture (m$^3$ m$^{-3}$)"
)

ax.set_ylabel(
    "Mean daily Tmax (°C)"
)

ax.set_title(
    "Spatial soil-moisture–temperature relationship\n"
    "18–30 June 2026"
)

ax.text(
    0.04,
    0.95,
    f"Descriptive r = {r:.3f}",
    transform=ax.transAxes,
    va="top",
)

ax.grid(alpha=0.25)

fig.tight_layout()

output = FIGURE_DIR / "soilmoisture_temperature.png"

fig.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)

print(f"Saved {output}")


# =====================================================================
# Figure 4: Heatwave surface soil moisture
# =====================================================================

fig, ax = plt.subplots(figsize=(9, 7))

mesh = ax.pcolormesh(
    soil_moisture["longitude"],
    soil_moisture["latitude"],
    soil_moisture.values,
    shading="auto",
    cmap="YlGnBu",
)

format_map_axes(ax)

cbar = fig.colorbar(
    mesh,
    ax=ax,
    pad=0.03,
)

cbar.set_label(
    r"Mean surface soil moisture (m$^3$ m$^{-3}$)"
)

ax.set_title(
    "Mean surface soil moisture\n"
    "18–30 June 2026"
)

fig.tight_layout()

output = FIGURE_DIR / "heatwave_soil_moisture.png"

fig.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)

print(f"Saved {output}")


# =====================================================================
# Finish
# =====================================================================

ds.close()

print("All figures created.")