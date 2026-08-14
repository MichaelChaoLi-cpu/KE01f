#!/usr/bin/env python3
"""Existing Shelter Capacity and Earthquake-Related Demand.

Plan: Render high housing-loss demand on true 125 m mesh polygons and compare its
geography with safe spacious and central shelter capacity.
Framework: Section 5 demand and capacity identification; Section 6 demand scenarios;
Section 7 spatial-demand construction and bounded shelter-capacity audit.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns
import shapely
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
DEMAND_INPUT = ROOT / "data/processed/kumamoto_shelter_demand_125m_map_preprocessed.parquet"
WARD_INPUT = ROOT / "data/processed/kumamoto_city_ward_boundaries_preprocessed.parquet"
SHELTER_INPUT = ROOT / "data/processed/kumamoto_shelter_network_access_preprocessed.parquet"
PNG_OUTPUT = ROOT / "data/exp/legacy-outputs/Figure_existing_shelter_capacity_and_earthquake_related_demand.png"
SVG_OUTPUT = PNG_OUTPUT.with_suffix(".svg")
OBSERVED_USE = 2_344

BOUNDARY_COLOR = "#475467"
WARD_COLOR = "#667085"
SAFE_COLOR = "#1565C0"
CENTRAL_COLOR = "#00897B"
MISSING_COLOR = "#B42318"


def polygon_vertices(geometry: np.ndarray) -> list[np.ndarray]:
    """Return exterior polygon coordinates for a Matplotlib PolyCollection."""
    vertices: list[np.ndarray] = []
    for item in geometry:
        for polygon in shapely.get_parts(item):
            ring = shapely.get_exterior_ring(polygon)
            coordinates = shapely.get_coordinates(ring)[:, :2]
            if len(coordinates) >= 4:
                vertices.append(coordinates)
    return vertices


def boundary_segments(geometry: np.ndarray) -> list[np.ndarray]:
    """Return exterior boundary segments for polygon and multipolygon arrays."""
    segments: list[np.ndarray] = []
    for item in geometry:
        for polygon in shapely.get_parts(item):
            ring = shapely.get_exterior_ring(polygon)
            coordinates = shapely.get_coordinates(ring)[:, :2]
            if len(coordinates) >= 4:
                segments.append(coordinates)
    return segments


def capacity_marker_area(capacity: float | np.ndarray, maximum: float) -> float | np.ndarray:
    """Encode capacity linearly as marker area, using one scale across panels."""
    return 12 + 310 * np.asarray(capacity) / maximum


def add_map_frame(ax: plt.Axes, extent: tuple[float, float, float, float]) -> None:
    west, east, south, north = extent
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_aspect(1 / np.cos(np.deg2rad((south + north) / 2)))
    ax.set_xticks(np.arange(np.ceil(west * 20) / 20, east + 0.001, 0.05))
    ax.set_yticks(np.arange(np.ceil(south * 20) / 20, north + 0.001, 0.05))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.2f}°E"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.2f}°N"))
    ax.tick_params(axis="both", labelsize=7, colors="#475467", length=3, width=0.7)
    ax.set_xlabel("Longitude", fontsize=8.2, color="#344054", labelpad=4)
    ax.set_ylabel("Latitude", fontsize=8.2, color="#344054", labelpad=4)
    ax.grid(True, color="#98A2B3", linewidth=0.45, linestyle=(0, (3, 3)), alpha=0.55)
    ax.set_axisbelow(False)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.85)
        spine.set_color("#344054")


def add_scale_and_north_arrow(ax: plt.Axes, extent: tuple[float, float, float, float]) -> None:
    west, east, south, north = extent
    mean_latitude = (south + north) / 2
    five_km_degrees = 5 / (111.32 * np.cos(np.deg2rad(mean_latitude)))
    start_x = west + 0.065 * (east - west)
    start_y = south + 0.07 * (north - south)
    ax.plot(
        [start_x, start_x + five_km_degrees],
        [start_y, start_y],
        color="#172033",
        linewidth=2.8,
        solid_capstyle="butt",
        zorder=30,
    )
    tick_height = 0.006 * (north - south)
    for x in (start_x, start_x + five_km_degrees):
        ax.plot([x, x], [start_y - tick_height, start_y + tick_height], color="#172033", linewidth=1, zorder=30)
    ax.text(
        start_x + five_km_degrees / 2,
        start_y + 0.014 * (north - south),
        "5 km",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#172033",
        zorder=30,
    )
    ax.annotate(
        "N",
        xy=(0.94, 0.94),
        xytext=(0.94, 0.83),
        xycoords="axes fraction",
        textcoords="axes fraction",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color="#172033",
        arrowprops={"arrowstyle": "-|>", "color": "#172033", "linewidth": 1.2},
        zorder=30,
    )


def add_annotation(ax: plt.Axes, text: str) -> None:
    ax.text(
        0.018,
        0.982,
        text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="bold",
        color="#172033",
        bbox={
            "boxstyle": "round,pad=0.30",
            "facecolor": "white",
            "edgecolor": "#D0D5DD",
            "alpha": 0.94,
        },
        zorder=40,
    )


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.035,
        1.015,
        label,
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        color="#172033",
        ha="left",
        va="bottom",
    )


def main() -> None:
    sns.set_theme(style="white", context="paper")
    demand = pd.read_parquet(DEMAND_INPUT)
    wards = pd.read_parquet(WARD_INPUT)
    shelters = pd.read_parquet(SHELTER_INPUT)

    mesh_geometry = from_wkb(demand["125 m Mesh Geometry WKB"].to_numpy())
    ward_geometry = from_wkb(wards["Ward Boundary Geometry WKB"].to_numpy())
    city_union = shapely.union_all(ward_geometry)
    city_geometry = np.asarray([city_union], dtype=object)
    mesh_vertices = polygon_vertices(mesh_geometry)
    ward_segments = boundary_segments(ward_geometry)
    city_segments = boundary_segments(city_geometry)
    city_polygons = polygon_vertices(city_geometry)

    high_demand = demand["Housing-Loss Shelter Demand High at 125 m"].to_numpy(dtype=float)
    positive = high_demand[high_demand > 0]
    lower = float(np.quantile(positive, 0.01))
    upper = float(np.quantile(positive, 0.995))
    demand_norm = LogNorm(vmin=lower, vmax=upper, clip=True)
    demand_cmap = plt.get_cmap("magma_r").copy()
    demand_cmap.set_bad("#F2F4F7")
    masked_demand = np.ma.masked_less_equal(high_demand, 0)

    min_x, min_y, max_x, max_y = shapely.bounds(city_union)
    pad_x = (max_x - min_x) * 0.025
    pad_y = (max_y - min_y) * 0.025
    extent = (min_x - pad_x, max_x + pad_x, min_y - pad_y, max_y + pad_y)

    fig = plt.figure(figsize=(14.8, 5.9), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.045], hspace=0.03, wspace=0.07)
    axes = np.array([fig.add_subplot(grid[0, column]) for column in range(3)])
    colorbar_axis = fig.add_subplot(grid[1, :])

    demand_collections: list[PolyCollection] = []
    for index, axis in enumerate(axes):
        axis.set_facecolor("#F8FAFC")
        axis.add_collection(
            PolyCollection(city_polygons, facecolors="#F8FAFC", edgecolors="none", zorder=1)
        )
        collection = PolyCollection(
            mesh_vertices,
            array=masked_demand,
            cmap=demand_cmap,
            norm=demand_norm,
            edgecolors="none",
            linewidths=0,
            alpha=1.0 if index == 0 else 0.72,
            rasterized=True,
            zorder=3,
        )
        axis.add_collection(collection)
        demand_collections.append(collection)
        axis.add_collection(
            LineCollection(ward_segments, colors=WARD_COLOR, linewidths=0.48, alpha=0.88, zorder=12)
        )
        axis.add_collection(
            LineCollection(city_segments, colors=BOUNDARY_COLOR, linewidths=1.05, alpha=0.98, zorder=13)
        )
        add_map_frame(axis, extent)
        add_panel_label(axis, "abc"[index])

    ward_label_points = shapely.point_on_surface(ward_geometry)
    for axis in axes:
        for label, point in zip(wards["Ward Label"], ward_label_points):
            text = axis.text(
                shapely.get_x(point),
                shapely.get_y(point),
                str(label).replace(" Ward", ""),
                ha="center",
                va="center",
                fontsize=6.7,
                color="#475467",
                fontweight="bold",
                alpha=0.82,
                zorder=14,
            )
            text.set_path_effects([path_effects.withStroke(linewidth=2.2, foreground="white", alpha=0.9)])

    axes[0].scatter(
        shelters["Shelter Longitude"],
        shelters["Shelter Latitude"],
        s=10,
        marker="^",
        c=SAFE_COLOR,
        edgecolors="white",
        linewidths=0.25,
        alpha=0.90,
        zorder=20,
    )
    axes[0].legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="^",
                color="none",
                markerfacecolor=SAFE_COLOR,
                markeredgecolor="white",
                markersize=6,
                label="Designated shelter",
            )
        ],
        loc="lower right",
        fontsize=7.2,
        frameon=True,
        framealpha=0.94,
    )
    add_annotation(
        axes[0],
        "Housing-loss high scenario\n"
        f"City demand: {high_demand.sum():,.0f} persons\n"
        f"Reported-use anchor: {OBSERVED_USE:,} persons\n"
        "Anchor uses the same spatial weights",
    )
    add_scale_and_north_arrow(axes[0], extent)

    maximum_capacity = float(shelters["Central Capacity (persons)"].max())
    capacity_specs = [
        (axes[1], "Safe Spacious Capacity (persons)", SAFE_COLOR, "Safe spacious capacity"),
        (axes[2], "Central Capacity (persons)", CENTRAL_COLOR, "Central capacity"),
    ]
    for axis, column, color, label in capacity_specs:
        capacity = shelters[column].to_numpy(dtype=float)
        known = ~shelters["Capacity Area Missing"].to_numpy()
        axis.scatter(
            shelters.loc[known, "Shelter Longitude"],
            shelters.loc[known, "Shelter Latitude"],
            s=capacity_marker_area(capacity[known], maximum_capacity),
            marker="o",
            c=color,
            edgecolors="white",
            linewidths=0.45,
            alpha=0.78,
            zorder=20,
        )
        missing = shelters["Capacity Area Missing"].to_numpy()
        axis.scatter(
            shelters.loc[missing, "Shelter Longitude"],
            shelters.loc[missing, "Shelter Latitude"],
            s=42,
            marker="X",
            c=MISSING_COLOR,
            edgecolors="white",
            linewidths=0.55,
            zorder=22,
        )
        add_annotation(
            axis,
            f"{label}\n"
            f"Known-source total: {capacity.sum():,.0f} persons\n"
            "Marker area is proportional to capacity",
        )

    legend_capacities = [250, 1_000, 2_500]
    capacity_handles = [
        axes[2].scatter(
            [],
            [],
            s=capacity_marker_area(value, maximum_capacity),
            c=CENTRAL_COLOR,
            edgecolors="white",
            linewidths=0.45,
            alpha=0.78,
            label=f"{value:,} persons",
        )
        for value in legend_capacities
    ]
    capacity_handles.append(
        Line2D(
            [0],
            [0],
            marker="X",
            linestyle="none",
            markerfacecolor=MISSING_COLOR,
            markeredgecolor="white",
            markersize=7,
            label="Area evidence missing",
        )
    )
    axes[2].legend(
        handles=capacity_handles,
        loc="lower right",
        fontsize=7.0,
        frameon=True,
        framealpha=0.94,
        title="Shelter capacity",
        title_fontsize=7.4,
        borderpad=0.55,
    )

    colorbar = fig.colorbar(
        ScalarMappable(norm=demand_norm, cmap=demand_cmap),
        cax=colorbar_axis,
        orientation="horizontal",
    )
    colorbar.set_label("Housing-loss shelter demand per 125 m mesh (persons, log scale)", fontsize=8.5)
    colorbar.ax.tick_params(labelsize=7.5)

    PNG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SVG_OUTPUT, format="svg", bbox_inches="tight", facecolor="white")
    fig.savefig(PNG_OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved SVG: {SVG_OUTPUT.relative_to(ROOT)}")
    print(f"Saved PNG (300 dpi): {PNG_OUTPUT.relative_to(ROOT)}")
    print(f"Mesh polygons shown: {len(demand):,}")
    print(f"Ward boundaries shown: {len(wards)}")
    print(f"Shelters shown: {len(shelters)}")


if __name__ == "__main__":
    main()
