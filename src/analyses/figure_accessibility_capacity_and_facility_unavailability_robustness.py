#!/usr/bin/env python3
"""Accessibility, Capacity, and Facility-Unavailability Robustness.

Plan: Compare matched mode, capacity, and facility-availability constraints.
Framework: Sections 5-7 use the high-loss-weighted stress surface, 15 minutes,
4 km/h walking, 0.50 motorized speed factor, and at most 415 openings. Walking
and vehicle-enabled demand share the same shelter capacity.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "data/exp/shared-capacity-multimodal-allocation/shared_capacity_mode_and_capacity_sensitivity_refined.csv"
OPENING_PATH = ROOT / "data/exp/shared-capacity-multimodal-allocation/matched_multimodal_opening_scale_sensitivity.csv"
FAILURE_PATH = ROOT / "data/exp/shared-capacity-multimodal-allocation/matched_multimodal_facility_unavailability.csv"
CRITICAL_PATH = ROOT / "data/exp/shelter-robustness/critical_single_shelter_loss.csv"
SHELTER_PATH = ROOT / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
BOUNDARY_PATH = ROOT / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
OUTPUT_PATH = ROOT / "data/results/figures/Figure_accessibility_capacity_and_facility_unavailability_robustness.png"

HYPOCENTER_LAT = 32 + 37.5 / 60
HYPOCENTER_LON = 130 + 40.7 / 60
COLOR_ACCESS = "#176B87"
COLOR_50 = "#D77A2D"
COLOR_100 = "#176B87"
COLOR_RANDOM = "#5B8DB8"
COLOR_TARGETED = "#C43B52"


def polygon_exteriors(geometries: np.ndarray) -> list[np.ndarray]:
    output: list[np.ndarray] = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
        for part in parts:
            output.append(np.asarray(part.exterior.coords))
    return output


def add_panel_heading(ax: plt.Axes, label: str, descriptor: str) -> None:
    ax.text(
        0.0, 1.025, f"{label}: {descriptor}", transform=ax.transAxes,
        ha="left", va="bottom", fontsize=9.2, fontweight="bold",
        color="#222222", clip_on=False, zorder=14,
    )


def degree_formatter(value: float, _position: int) -> str:
    return f"{value:.2f}°"


def add_north_arrow(ax: plt.Axes) -> None:
    ax.annotate(
        "N", xy=(0.955, 0.955), xytext=(0.955, 0.865), xycoords="axes fraction",
        ha="center", va="center", fontsize=9, fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#313131", "lw": 1.0}, zorder=12,
    )


def main() -> None:
    core = pd.read_csv(CORE_PATH)
    opening = pd.read_csv(OPENING_PATH)
    failure = pd.read_csv(FAILURE_PATH)
    critical = pd.read_csv(CRITICAL_PATH, dtype={"Shelter ID": str})
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=["Shelter ID", "Longitude", "Latitude", "Shelter Service Class"],
    )
    shelters = shelters.loc[shelters["Shelter Service Class"].eq("general")].copy()
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])
    boundary_geometries = from_wkb(boundaries["Geometry"].to_numpy())
    boundary_polygons = polygon_exteriors(boundary_geometries)
    critical = critical.merge(
        shelters[["Shelter ID", "Longitude", "Latitude"]],
        on="Shelter ID", how="left", validate="1:1",
    )
    if critical[["Longitude", "Latitude"]].isna().any().any():
        raise RuntimeError("At least one screened shelter has no mapped coordinates")

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.edgecolor": "#5a5a5a", "axes.linewidth": 0.7,
        "xtick.color": "#4a4a4a", "ytick.color": "#4a4a4a",
    })
    fig, axes = plt.subplots(2, 2, figsize=(14.2, 11.0), constrained_layout=False)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.955, bottom=0.075, wspace=0.18, hspace=0.28)
    ax_a, ax_b, ax_c, ax_d = axes.flat

    # a: shared-capacity service under the central 100-person capacity.
    central = core.loc[core["Capacity per Open Shelter"].eq(100.0)].sort_values(
        "Vehicle-Enabled Demand Share"
    )
    x_mode = 100 * central["Vehicle-Enabled Demand Share"].to_numpy(float)
    y_mode = central["Served Percent"].to_numpy(float)
    upper_mode = 100 * central["MIP Dual Bound Served Demand"].to_numpy(float) / 10467.0
    ax_a.plot(x_mode, y_mode, color=COLOR_ACCESS, linewidth=2.3, marker="o", markersize=6, zorder=4)
    ax_a.fill_between(x_mode, 50, y_mode, color="#8FC5D8", alpha=0.25, zorder=1)
    last_gap = upper_mode[-1] - y_mode[-1]
    ax_a.errorbar(
        x_mode[-1], y_mode[-1],
        yerr=np.array([[0.0], [last_gap]]),
        fmt="none", ecolor="#5F6265", elinewidth=1.2, capsize=3,
        label="Reported lower bound and solver upper bound", zorder=5,
    )
    for index, (x_value, y_value) in enumerate(zip(x_mode, y_mode)):
        ax_a.text(x_value, y_value + 1.25, f"{y_value:.1f}%", ha="center", va="bottom", fontsize=7.8)
    ax_a.set_xlim(-3, 103); ax_a.set_ylim(50, 102)
    ax_a.set_xlabel("Vehicle-enabled share of stress demand")
    ax_a.set_ylabel("Capacity-constrained assigned stress demand")
    ax_a.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_a.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_a.grid(color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    ax_a.legend(loc="upper left", frameon=False, fontsize=7.5)
    add_panel_heading(ax_a, "a", "Shared-capacity service by mode availability")

    # b: matched capacity and opening-scale comparisons at p=0.50.
    capacity_50 = core.loc[
        core["Vehicle-Enabled Demand Share"].eq(0.5)
        & core["Capacity per Open Shelter"].eq(50.0)
    ].iloc[0]
    capacity_100 = core.loc[
        core["Vehicle-Enabled Demand Share"].eq(0.5)
        & core["Capacity per Open Shelter"].eq(100.0)
    ].iloc[0]
    all_open = opening.loc[
        opening["Opening Scenario"].eq("All 1,156 shelters selectable")
    ].iloc[0]
    values = np.array([
        float(capacity_50["Served Percent"]),
        float(capacity_100["Served Percent"]),
        float(all_open["Served Percent"]),
    ])
    upper_50 = 100.0 * float(capacity_50["MIP Dual Bound Served Demand"]) / 10467.0
    upper_error = np.array([max(0.0, upper_50 - values[0]), 0.0, 0.0])
    positions = np.arange(3)
    bars = ax_b.bar(
        positions, values, width=0.62,
        color=[COLOR_50, COLOR_100, "#5B8DB8"],
        edgecolor=["#8C4B17", "#0D536C", "#315B78"], linewidth=0.55,
        yerr=np.vstack([np.zeros(3), upper_error]), capsize=3,
        error_kw={"elinewidth": 0.9, "ecolor": "#5F6265"}, zorder=3,
    )
    for bar, value in zip(bars, values):
        ax_b.text(bar.get_x() + bar.get_width() / 2, value + 0.45, f"{value:.1f}%", ha="center", va="bottom", fontsize=7.8)
    ax_b.text(
        0, 75.7, "lower bound", ha="center", va="top", fontsize=7.0,
        color="#6E3C16",
    )
    ax_b.set_xticks(
        positions,
        ["50 persons\n415 openings", "100 persons\n415 openings", "100 persons\nall selectable"],
    )
    ax_b.set_ylim(74, 81)
    ax_b.set_ylabel("Capacity-constrained assigned stress demand")
    ax_b.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_b.grid(axis="y", color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    add_panel_heading(ax_b, "b", "Capacity and opening-scale gains under matched access")

    # c: matched facility unavailability at p=0.50 and c=100.
    baseline = float(failure.loc[failure["Failure Mode"].eq("baseline"), "Served Percent"].iloc[0])
    random = failure.loc[failure["Failure Mode"].eq("random")]
    random_summary = random.groupby("Unavailability Share")["Served Percent"].agg(mean="mean", minimum="min", maximum="max")
    targeted = failure.loc[failure["Failure Mode"].eq("targeted_mixed_reachable_pressure")].set_index("Unavailability Share")
    shares = np.array([0.1, 0.2, 0.3]); x = shares * 100; width = 3.4
    random_means = random_summary.loc[shares, "mean"].to_numpy()
    random_errors = np.vstack([
        random_means - random_summary.loc[shares, "minimum"].to_numpy(),
        random_summary.loc[shares, "maximum"].to_numpy() - random_means,
    ])
    ax_c.bar(x - width / 2, random_means, width=width, color=COLOR_RANDOM, edgecolor="#315B78", linewidth=0.55, yerr=random_errors, capsize=3, error_kw={"elinewidth": 0.9, "ecolor": "#315B78"}, label="Random removal (30 draws; mean and range)", zorder=3)
    targeted_values = targeted.loc[shares, "Served Percent"].to_numpy()
    targeted_upper = 100 * targeted.loc[shares, "MIP Dual Bound Served Demand"].to_numpy() / 10467.0
    targeted_error = np.maximum(0, targeted_upper - targeted_values)
    ax_c.bar(x + width / 2, targeted_values, width=width, color=COLOR_TARGETED, edgecolor="#7D2436", linewidth=0.55, yerr=np.vstack([np.zeros(3), targeted_error]), capsize=3, error_kw={"elinewidth": 0.9, "ecolor": "#7D2436"}, label="Mixed-pressure removal (lower bound)", zorder=3)
    ax_c.axhline(baseline, color="#333333", linewidth=1.1, linestyle=(0, (5, 3)), label=f"No-removal baseline ({baseline:.1f}%)")
    for xpos, value in zip(x + width / 2, targeted_values):
        ax_c.text(xpos, value + 1.0, f"{value:.1f}%", ha="center", va="bottom", fontsize=7.6, fontweight="bold", color="#5E1D2B")
    ax_c.set_xlim(4, 36); ax_c.set_ylim(0, 82)
    ax_c.set_xticks(x, ["10%", "20%", "30%"])
    ax_c.set_xlabel("General shelters unavailable")
    ax_c.set_ylabel("Capacity-constrained assigned stress demand")
    ax_c.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_c.grid(axis="y", color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    ax_c.legend(loc="lower left", frameon=False, fontsize=7.2)
    add_panel_heading(ax_c, "c", "Facility loss under the central mixed-mode case")

    # d: conservative walking 50-person single-shelter loss screen.
    all_bounds = np.asarray([geometry.bounds for geometry in boundary_geometries])
    x_min, y_min = all_bounds[:, [0, 1]].min(axis=0)
    x_max, y_max = all_bounds[:, [2, 3]].max(axis=0)
    x_padding = 0.018 * (x_max - x_min); y_padding = 0.018 * (y_max - y_min)
    mean_latitude = (y_min + y_max) / 2
    ax_d.add_collection(PolyCollection(boundary_polygons, facecolors="#f2f2ef", edgecolors="#737373", linewidths=0.32, zorder=0))
    ax_d.scatter(shelters["Longitude"], shelters["Latitude"], s=3.2, color="#9BA4AA", alpha=0.52, linewidths=0, zorder=3)
    loss = critical["Single-Shelter Service-Loss Lower Bound"].to_numpy(float)
    bubbles = ax_d.scatter(critical["Longitude"], critical["Latitude"], s=20 + 2.5 * loss, c=loss, cmap="YlOrRd", norm=Normalize(vmin=0, vmax=50), edgecolor="#54201C", linewidth=0.55, alpha=0.92, zorder=7)
    ax_d.scatter(HYPOCENTER_LON, HYPOCENTER_LAT, s=85, marker="*", facecolor="#CE1B28", edgecolor="white", linewidth=0.65, zorder=10)
    ax_d.set_xlim(x_min - x_padding, x_max + x_padding); ax_d.set_ylim(y_min - y_padding, y_max + y_padding)
    ax_d.set_aspect(1 / np.cos(np.deg2rad(mean_latitude)))
    ax_d.xaxis.set_major_locator(MultipleLocator(0.25)); ax_d.yaxis.set_major_locator(MultipleLocator(0.20))
    ax_d.xaxis.set_major_formatter(FuncFormatter(degree_formatter)); ax_d.yaxis.set_major_formatter(FuncFormatter(degree_formatter))
    ax_d.tick_params(labelsize=7.3, length=2.5, pad=2)
    ax_d.grid(color="#d6d6d6", linewidth=0.35, linestyle=(0, (2, 3)), zorder=1)
    add_north_arrow(ax_d)
    add_panel_heading(ax_d, "d", "Secondary walking single-shelter screen")
    colorbar = fig.colorbar(bubbles, ax=ax_d, orientation="horizontal", fraction=0.038, pad=0.035, aspect=30)
    colorbar.set_label("Assigned-demand loss after one shelter is removed (persons)", fontsize=8)
    colorbar.ax.tick_params(labelsize=7, length=2); colorbar.outline.set_linewidth(0.45)

    map_legend = [
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor="#9BA4AA", markeredgecolor="none", markersize=4, label=f"All general shelters (n={len(shelters):,})"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor="#F46D43", markeredgecolor="#54201C", markeredgewidth=0.4, markersize=6, label="Screened shelters (n=30)"),
        Line2D([0], [0], marker="*", linestyle="none", markerfacecolor="#CE1B28", markeredgecolor="white", markeredgewidth=0.45, markersize=9, label="Official hypocenter"),
    ]
    fig.legend(handles=map_legend, loc="lower center", bbox_to_anchor=(0.75, 0.012), ncol=3, frameon=False, fontsize=8.0, handletextpad=0.5, columnspacing=1.3)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
