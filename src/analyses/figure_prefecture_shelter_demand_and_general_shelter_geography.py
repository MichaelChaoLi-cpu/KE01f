"""Map prefecture-wide shelter demand and designated-shelter geography.

The three 10,467-person surfaces are alternative spatial stress tests. They are
not observations of evacuees' home locations or shelter destinations.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import PowerNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
MESH_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
)
SHELTER_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
BOUNDARY_PATH = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
OUTPUT_PATH = (
    ROOT
    / "data/results/figures/Figure_prefecture_shelter_demand_and_general_shelter_geography.png"
)

# JMA CMT hypocenter for the 28 July 2026 16:27 earthquake.
HYPOCENTER_LAT = 32 + 37.5 / 60
HYPOCENTER_LON = 130 + 40.7 / 60

PANELS = (
    (
        "Housing-Loss Shelter Demand High",
        "High housing-loss demand (persons / 125 m mesh)",
        "housing_loss",
        "High housing-loss demand",
    ),
    (
        "Observed-Use Stress Demand Population Weighted",
        "10,467 stress: population-weighted (persons / mesh)",
        "observed_use_stress",
        "Population-weighted stress",
    ),
    (
        "Observed-Use Stress Demand Central Housing-Loss Weighted",
        "10,467 stress: central-loss-weighted (persons / mesh)",
        "observed_use_stress",
        "Central-loss-weighted stress",
    ),
    (
        "Observed-Use Stress Demand High Housing-Loss Weighted",
        "10,467 stress: high-loss-weighted (persons / mesh)",
        "observed_use_stress",
        "High-loss-weighted stress",
    ),
)


def polygon_exteriors(geometries: np.ndarray) -> list[np.ndarray]:
    """Return exterior coordinate arrays from Polygon or MultiPolygon objects."""
    exteriors: list[np.ndarray] = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
        for part in parts:
            exteriors.append(np.asarray(part.exterior.coords))
    return exteriors


def add_north_arrow(ax: plt.Axes) -> None:
    ax.annotate(
        "N",
        xy=(0.955, 0.955),
        xytext=(0.955, 0.865),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#313131", "lw": 1.0},
        zorder=12,
    )


def add_scale_bar(ax: plt.Axes, latitude: float, length_km: float = 25.0) -> None:
    """Draw an approximate longitude-based scale bar for this prefecture map."""
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    length_degrees = length_km / (111.32 * np.cos(np.deg2rad(latitude)))
    x_start = x_min + 0.055 * (x_max - x_min)
    y_start = y_min + 0.055 * (y_max - y_min)
    ax.plot(
        [x_start, x_start + length_degrees],
        [y_start, y_start],
        color="#252525",
        linewidth=2.2,
        solid_capstyle="butt",
        zorder=12,
    )
    ax.plot(
        [x_start, x_start, x_start + length_degrees, x_start + length_degrees],
        [
            y_start - 0.006,
            y_start + 0.006,
            y_start - 0.006,
            y_start + 0.006,
        ],
        color="#252525",
        linewidth=0.8,
        zorder=12,
    )
    ax.text(
        x_start + length_degrees / 2,
        y_start + 0.012,
        f"{length_km:g} km",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#252525",
        zorder=12,
    )


def degree_formatter(value: float, _position: int) -> str:
    return f"{value:.2f}°"


def main() -> None:
    mesh_columns = ["Mesh Geometry", *(panel[0] for panel in PANELS)]
    mesh = pd.read_parquet(MESH_PATH, columns=mesh_columns)
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=["Longitude", "Latitude", "Shelter Service Class"],
    )
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])

    mesh_geometries = from_wkb(mesh["Mesh Geometry"].to_numpy())
    boundary_geometries = from_wkb(boundaries["Geometry"].to_numpy())
    mesh_polygons = polygon_exteriors(mesh_geometries)
    boundary_polygons = polygon_exteriors(boundary_geometries)

    all_bounds = np.asarray([geometry.bounds for geometry in boundary_geometries])
    x_min, y_min = all_bounds[:, [0, 1]].min(axis=0)
    x_max, y_max = all_bounds[:, [2, 3]].max(axis=0)
    x_padding = 0.018 * (x_max - x_min)
    y_padding = 0.018 * (y_max - y_min)
    extent = (
        x_min - x_padding,
        x_max + x_padding,
        y_min - y_padding,
        y_max + y_padding,
    )
    mean_latitude = (y_min + y_max) / 2

    housing_values = mesh[PANELS[0][0]].to_numpy(dtype=float)
    stress_values = np.concatenate(
        [mesh[column].to_numpy(dtype=float) for column, _, group, _ in PANELS if group == "observed_use_stress"]
    )
    color_limits = {
        "housing_loss": float(np.nanquantile(housing_values, 0.995)),
        "observed_use_stress": float(np.nanquantile(stress_values, 0.995)),
    }

    general = shelters["Shelter Service Class"].eq("general")
    welfare = shelters["Shelter Service Class"].eq("welfare_specific")

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.edgecolor": "#5a5a5a",
            "axes.linewidth": 0.7,
            "xtick.color": "#4a4a4a",
            "ytick.color": "#4a4a4a",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(14.2, 11.2), constrained_layout=False)
    fig.subplots_adjust(left=0.055, right=0.985, top=0.985, bottom=0.080, wspace=0.08, hspace=0.18)

    for index, (ax, (column, colorbar_label, group, descriptor)) in enumerate(zip(axes.flat, PANELS)):
        values = mesh[column].to_numpy(dtype=float)
        norm = PowerNorm(gamma=0.48, vmin=0.0, vmax=color_limits[group], clip=False)

        land = PolyCollection(
            boundary_polygons,
            facecolors="#f1f1ef",
            edgecolors="none",
            zorder=0,
        )
        ax.add_collection(land)

        demand_layer = PolyCollection(
            mesh_polygons,
            array=values,
            cmap="YlOrRd",
            norm=norm,
            edgecolors="none",
            linewidths=0,
            rasterized=True,
            zorder=2,
        )
        ax.add_collection(demand_layer)

        ax.add_collection(
            LineCollection(
                boundary_polygons,
                colors="#777777",
                linewidths=0.28,
                alpha=0.8,
                zorder=5,
            )
        )

        ax.scatter(
            shelters.loc[general, "Longitude"],
            shelters.loc[general, "Latitude"],
            s=4.5,
            marker="o",
            color="#176B87",
            alpha=0.62,
            linewidths=0,
            zorder=7,
        )
        ax.scatter(
            shelters.loc[welfare, "Longitude"],
            shelters.loc[welfare, "Latitude"],
            s=13,
            marker="^",
            facecolor="#7851A9",
            edgecolor="white",
            linewidth=0.25,
            alpha=0.9,
            zorder=8,
        )
        ax.scatter(
            HYPOCENTER_LON,
            HYPOCENTER_LAT,
            s=78,
            marker="*",
            facecolor="#CE1B28",
            edgecolor="white",
            linewidth=0.65,
            zorder=10,
        )

        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.set_aspect(1 / np.cos(np.deg2rad(mean_latitude)))
        ax.xaxis.set_major_locator(MultipleLocator(0.25))
        ax.yaxis.set_major_locator(MultipleLocator(0.20))
        ax.xaxis.set_major_formatter(FuncFormatter(degree_formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(degree_formatter))
        ax.tick_params(labelsize=7.5, length=2.5, pad=2)
        ax.grid(color="#d6d6d6", linewidth=0.35, linestyle=(0, (2, 3)), zorder=1)

        ax.text(
            0.0,
            1.025,
            f"{chr(ord('a') + index)}: {descriptor}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=9.2,
            fontweight="bold",
            color="#222222",
            clip_on=False,
            zorder=13,
        )
        total = float(np.nansum(values))
        total_text = f"Mapped total: {total:,.1f} persons" if index == 0 else f"Scenario total: {total:,.0f} persons"
        ax.text(
            0.982,
            0.025,
            total_text,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7.6,
            color="#303030",
            bbox={"facecolor": "white", "edgecolor": "#b5b5b5", "alpha": 0.86, "pad": 2.4},
            zorder=13,
        )

        colorbar = fig.colorbar(
            demand_layer,
            ax=ax,
            orientation="horizontal",
            fraction=0.038,
            pad=0.035,
            aspect=34,
            extend="max",
        )
        colorbar.set_label(colorbar_label, fontsize=8, labelpad=3)
        colorbar.ax.tick_params(labelsize=7, length=2)
        colorbar.outline.set_linewidth(0.45)

        add_north_arrow(ax)
        if index == 0:
            add_scale_bar(ax, mean_latitude)

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor="#176B87",
            markeredgecolor="none",
            markersize=4.5,
            label=f"General shelters (n={int(general.sum()):,})",
        ),
        Line2D(
            [0],
            [0],
            marker="^",
            linestyle="none",
            markerfacecolor="#7851A9",
            markeredgecolor="white",
            markeredgewidth=0.35,
            markersize=6,
            label=f"Welfare-specific shelters (n={int(welfare.sum()):,})",
        ),
        Line2D(
            [0],
            [0],
            marker="*",
            linestyle="none",
            markerfacecolor="#CE1B28",
            markeredgecolor="white",
            markeredgewidth=0.45,
            markersize=9,
            label="Official hypocenter",
        ),
        Line2D(
            [0],
            [0],
            color="#777777",
            linewidth=0.7,
            label="Municipality / ward boundary",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.012),
        ncol=4,
        frameon=False,
        fontsize=8.2,
        handletextpad=0.5,
        columnspacing=1.5,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
