"""Map nearest-general-shelter walking access and geographic gaps."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
ACCESS_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_nearest_shelter_walking_access_preprocessed.parquet"
)
SHELTER_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
BOUNDARY_PATH = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
SUMMARY_PATH = (
    ROOT
    / "data/exp/prefecture-shelter-walking-access/prefecture_walking_access_coverage_summary.csv"
)
OUTPUT_PATH = (
    ROOT
    / "data/exp/legacy-outputs/Figure_network_walking_access_and_geographic_gaps.png"
)

HIGH_STRESS_MEASURE = "Observed-Use Stress Demand High Housing-Loss Weighted"
PANELS = (
    (4, 10, "4 km/h · 10 min"),
    (4, 15, "4 km/h · 15 min"),
    (4, 30, "4 km/h · 30 min"),
    (3, 15, "3 km/h · 15 min mobility sensitivity"),
)

REACHABLE_COLOR = "#9ECAE1"
GAP_COLOR = "#C43B52"
SHELTER_COLOR = "#173B52"


def polygon_exteriors(geometries: np.ndarray) -> list[np.ndarray]:
    exteriors: list[np.ndarray] = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
        for part in parts:
            exteriors.append(np.asarray(part.exterior.coords))
    return exteriors


def degree_formatter(value: float, _position: int) -> str:
    return f"{value:.2f}°"


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


def coverage_percent(
    summary: pd.DataFrame,
    speed: int,
    threshold: int,
    measure: str,
) -> float:
    match = summary.loc[
        summary["Walking Speed (km/h)"].eq(speed)
        & summary["Time Threshold (min)"].eq(threshold)
        & summary["Coverage Measure"].eq(measure),
        "Coverage Percent",
    ]
    if len(match) != 1:
        raise ValueError(
            f"Expected one coverage result for speed={speed}, threshold={threshold}, "
            f"measure={measure}; found {len(match)}"
        )
    return float(match.iloc[0])


def main() -> None:
    reach_columns = [f"Reachable within {threshold} min at {speed} km/h" for speed, threshold, _ in PANELS]
    access = pd.read_parquet(
        ACCESS_PATH,
        columns=["Mesh Geometry", *reach_columns],
    )
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=["Longitude", "Latitude", "Shelter Service Class"],
    )
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])
    summary = pd.read_csv(SUMMARY_PATH)

    mesh_geometries = from_wkb(access["Mesh Geometry"].to_numpy())
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

    general = shelters["Shelter Service Class"].eq("general")

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
    fig, axes = plt.subplots(2, 2, figsize=(14.2, 11.0), constrained_layout=False)
    fig.subplots_adjust(left=0.055, right=0.985, top=0.985, bottom=0.075, wspace=0.08, hspace=0.08)

    for index, (ax, (speed, threshold, scenario_label)) in enumerate(zip(axes.flat, PANELS)):
        reach_column = f"Reachable within {threshold} min at {speed} km/h"
        reachable = access[reach_column].fillna(False).to_numpy(dtype=bool)
        facecolors = np.where(reachable, REACHABLE_COLOR, GAP_COLOR)

        ax.add_collection(
            PolyCollection(
                boundary_polygons,
                facecolors="#f2f2ef",
                edgecolors="none",
                zorder=0,
            )
        )
        ax.add_collection(
            PolyCollection(
                mesh_polygons,
                facecolors=facecolors,
                edgecolors="none",
                linewidths=0,
                rasterized=True,
                zorder=2,
            )
        )
        ax.add_collection(
            LineCollection(
                boundary_polygons,
                colors="#6f6f6f",
                linewidths=0.30,
                alpha=0.82,
                zorder=5,
            )
        )
        ax.scatter(
            shelters.loc[general, "Longitude"],
            shelters.loc[general, "Latitude"],
            s=4.2,
            marker="o",
            color=SHELTER_COLOR,
            alpha=0.62,
            linewidths=0,
            zorder=7,
        )

        population_coverage = coverage_percent(summary, speed, threshold, "Total Population")
        stress_coverage = coverage_percent(summary, speed, threshold, HIGH_STRESS_MEASURE)
        ax.text(
            0.025,
            0.965,
            chr(ord("a") + index),
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=12,
            fontweight="bold",
            color="#222222",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 2.0},
            zorder=13,
        )
        ax.text(
            0.50,
            0.965,
            scenario_label,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color="#252525",
            bbox={"facecolor": "white", "edgecolor": "#b7b7b7", "lw": 0.4, "alpha": 0.88, "pad": 2.2},
            zorder=13,
        )
        ax.text(
            0.982,
            0.025,
            f"Population {population_coverage:.1f}%  |  High-stress demand {stress_coverage:.1f}%",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7.5,
            color="#303030",
            bbox={"facecolor": "white", "edgecolor": "#b5b5b5", "lw": 0.4, "alpha": 0.88, "pad": 2.3},
            zorder=13,
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
        add_north_arrow(ax)
        if index == 0:
            add_scale_bar(ax, mean_latitude)

    legend_handles = [
        Patch(facecolor=REACHABLE_COLOR, edgecolor="none", label="Reachable populated mesh"),
        Patch(facecolor=GAP_COLOR, edgecolor="none", label="Unreachable populated mesh"),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=SHELTER_COLOR,
            markeredgecolor="none",
            markersize=4.5,
            label=f"General shelter (n={int(general.sum()):,})",
        ),
        Line2D(
            [0],
            [0],
            color="#6f6f6f",
            linewidth=0.7,
            label="Municipality / ward boundary",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.018),
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
