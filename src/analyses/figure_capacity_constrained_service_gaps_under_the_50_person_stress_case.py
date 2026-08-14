"""Map explanation gaps under the conservative 50-person walking rules."""

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

from estimate_demand_access_sensitivity import solve_maximum_service


ROOT = Path(__file__).resolve().parents[2]
DEMAND_PATH = (
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
PAIR_PATH = ROOT / "data/exp/shelter-robustness/demand_shelter_pairs_within_2km.parquet"
SENSITIVITY_PATH = ROOT / "data/exp/shelter-robustness/demand_access_sensitivity.csv"
PRIMARY_ALLOCATION_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/primary_positive_demand_shelter_allocation.parquet"
)
PRIMARY_OPENINGS_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/primary_modeled_shelter_openings.csv"
)
OUTPUT_PATH = (
    ROOT
    / "data/results/figures/Figure_capacity_constrained_service_gaps_under_the_50_person_stress_case.png"
)

CAPACITY_PER_SHELTER = 50.0
MAXIMUM_OPEN_SHELTERS = 415
MAXIMUM_WALKING_DISTANCE_M = 1000.0

PANELS = (
    (
        "population_weighted",
        "Observed-Use Stress Demand Population Weighted",
        "Population-weighted stress",
    ),
    (
        "central_loss_weighted",
        "Observed-Use Stress Demand Central Housing-Loss Weighted",
        "Central-loss-weighted stress",
    ),
    (
        "high_loss_weighted",
        "Observed-Use Stress Demand High Housing-Loss Weighted",
        "High-loss-weighted stress",
    ),
)

NO_DEMAND_COLOR = "#F2F2EF"
FULLY_SERVED_COLOR = "#2B83BA"
PARTLY_SERVED_COLOR = "#FDAE61"
UNSERVED_COLOR = "#C43B52"
OPEN_SHELTER_COLOR = "#172C3C"
OTHER_SHELTER_COLOR = "#A0A7AC"


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


def add_panel_heading(ax: plt.Axes, label: str, descriptor: str) -> None:
    ax.text(
        0.0,
        1.025,
        f"{label}: {descriptor}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.2,
        fontweight="bold",
        color="#222222",
        clip_on=False,
        zorder=14,
    )


def solve_spatial_allocation(
    scenario: str,
    demand_values: np.ndarray,
    pairs: pd.DataFrame,
    shelter_count: int,
    sensitivity: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return mesh-level service, selected openings, and validated served total."""
    expected_row = sensitivity.loc[
        sensitivity["Sensitivity Dimension"].eq("Demand geography")
        & sensitivity["Scenario"].eq(scenario)
    ]
    if len(expected_row) != 1:
        raise ValueError(f"Expected one stored sensitivity row for {scenario}")
    expected_served = float(expected_row.iloc[0]["Maximum Served Demand"])

    result, served_total, _ = solve_maximum_service(
        pairs,
        demand_values,
        shelter_count,
        time_limit=180.0,
    )
    if not bool(result.status == 0):
        raise RuntimeError(f"Allocation for {scenario} was not proven optimal: {result.message}")
    if not np.isclose(served_total, expected_served, atol=0.02):
        raise ValueError(
            f"Allocation total for {scenario} ({served_total}) does not match "
            f"stored result ({expected_served})"
        )

    pair_count = len(pairs)
    flow = np.clip(result.x[:pair_count], 0, None)
    served_by_mesh = np.bincount(
        pairs["Demand Position"].to_numpy(np.int64),
        weights=flow,
        minlength=len(demand_values),
    )
    open_shelters = result.x[pair_count:] >= 0.5
    return served_by_mesh, open_shelters, served_total


def primary_spatial_allocation(
    demand_count: int,
    shelters: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, float]:
    allocation = pd.read_parquet(PRIMARY_ALLOCATION_PATH)
    served_by_mesh = np.bincount(
        allocation["Demand Position"].to_numpy(np.int64),
        weights=allocation["Assigned Demand"].to_numpy(float),
        minlength=demand_count,
    )
    openings = pd.read_csv(PRIMARY_OPENINGS_PATH, dtype={"Shelter ID": str})
    open_ids = set(openings.loc[openings["Modeled Open Shelter"], "Shelter ID"])
    open_shelters = shelters["Shelter ID"].isin(open_ids).to_numpy(dtype=bool)
    if int(open_shelters.sum()) != MAXIMUM_OPEN_SHELTERS:
        raise ValueError(
            f"Expected {MAXIMUM_OPEN_SHELTERS} primary openings; found {open_shelters.sum()}"
        )
    return served_by_mesh, open_shelters, float(served_by_mesh.sum())


def service_colors(demand: np.ndarray, served: np.ndarray) -> np.ndarray:
    colors = np.full(len(demand), NO_DEMAND_COLOR, dtype=object)
    positive = demand > 1e-10
    ratio = np.zeros(len(demand), dtype=float)
    ratio[positive] = np.clip(served[positive] / demand[positive], 0, 1)
    colors[positive & (ratio <= 1e-6)] = UNSERVED_COLOR
    colors[positive & (ratio > 1e-6) & (ratio < 1 - 1e-6)] = PARTLY_SERVED_COLOR
    colors[positive & (ratio >= 1 - 1e-6)] = FULLY_SERVED_COLOR
    return colors


def main() -> None:
    demand_columns = [column for _, column, _ in PANELS]
    demand = pd.read_parquet(
        DEMAND_PATH,
        columns=["Mesh Geometry", *demand_columns],
    ).reset_index(drop=True)
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=[
            "Shelter ID",
            "Longitude",
            "Latitude",
            "Shelter Service Class",
            "Walking Network Snap Accepted",
        ],
    )
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])
    sensitivity = pd.read_csv(SENSITIVITY_PATH)
    pairs = pd.read_parquet(PAIR_PATH)
    pairs = pairs.loc[
        pairs["Walking Distance (m)"].le(MAXIMUM_WALKING_DISTANCE_M + 1e-9)
    ].reset_index(drop=True)

    mesh_geometries = from_wkb(demand["Mesh Geometry"].to_numpy())
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

    allocations: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    for scenario, demand_column, _ in PANELS[:2]:
        allocations[scenario] = solve_spatial_allocation(
            scenario,
            demand[demand_column].to_numpy(float),
            pairs,
            len(shelters),
            sensitivity,
        )
    allocations["high_loss_weighted"] = primary_spatial_allocation(len(demand), shelters)

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
    fig, axes = plt.subplots(1, 3, figsize=(16.8, 6.65), constrained_layout=False)
    fig.subplots_adjust(left=0.045, right=0.985, top=0.930, bottom=0.125, wspace=0.09)

    for index, (ax, (scenario, demand_column, scenario_label)) in enumerate(zip(axes, PANELS)):
        demand_values = demand[demand_column].to_numpy(float)
        served_by_mesh, open_shelters, served_total = allocations[scenario]
        total_demand = float(demand_values.sum())
        explanation_gap = total_demand - served_total
        assigned_percent = 100 * served_total / total_demand

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
                facecolors=service_colors(demand_values, served_by_mesh),
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
            shelters.loc[~open_shelters, "Longitude"],
            shelters.loc[~open_shelters, "Latitude"],
            s=3.2,
            marker="o",
            color=OTHER_SHELTER_COLOR,
            alpha=0.55,
            linewidths=0,
            zorder=6,
        )
        ax.scatter(
            shelters.loc[open_shelters, "Longitude"],
            shelters.loc[open_shelters, "Latitude"],
            s=7.5,
            marker="o",
            color=OPEN_SHELTER_COLOR,
            alpha=0.78,
            linewidths=0,
            zorder=7,
        )

        add_panel_heading(ax, chr(ord("a") + index), scenario_label)
        ax.text(
            0.982,
            0.025,
            f"Assigned {assigned_percent:.1f}%  |  Explanation gap {explanation_gap:,.0f}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7.6,
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
        ax.tick_params(labelsize=7.2, length=2.5, pad=2)
        ax.grid(color="#d6d6d6", linewidth=0.35, linestyle=(0, (2, 3)), zorder=1)
        add_north_arrow(ax)
        if index == 0:
            add_scale_bar(ax, mean_latitude)

    legend_handles = [
        Patch(facecolor=FULLY_SERVED_COLOR, edgecolor="none", label="Stress demand fully assigned"),
        Patch(facecolor=PARTLY_SERVED_COLOR, edgecolor="none", label="Stress demand partly assigned"),
        Patch(facecolor=UNSERVED_COLOR, edgecolor="none", label="Stress demand outside modeled assignment"),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=OPEN_SHELTER_COLOR,
            markeredgecolor="none",
            markersize=5,
            label=f"Modeled open general shelter (n={MAXIMUM_OPEN_SHELTERS})",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=OTHER_SHELTER_COLOR,
            markeredgecolor="none",
            markersize=4,
            label="Other general shelter",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.065),
        ncol=5,
        frameon=False,
        fontsize=8.1,
        handletextpad=0.5,
        columnspacing=1.35,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
