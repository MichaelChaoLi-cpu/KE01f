"""Plot capacity-threshold and facility-unavailability robustness results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
THRESHOLD_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/capacity_threshold_sensitivity.csv"
)
UNAVAILABILITY_PATH = (
    ROOT / "data/exp/shelter-robustness/facility_unavailability_sensitivity.csv"
)
CRITICAL_PATH = ROOT / "data/exp/shelter-robustness/critical_single_shelter_loss.csv"
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
    / "data/results/figures/Figure_threshold_and_facility_unavailability_robustness.png"
)

HYPOCENTER_LAT = 32 + 37.5 / 60
HYPOCENTER_LON = 130 + 40.7 / 60

COLOR_415 = "#176B87"
COLOR_ALL = "#E07A2D"
COLOR_RANDOM = "#5B8DB8"
COLOR_TARGETED = "#C43B52"

SHORT_NAMES = {
    "E4321300034111": "Toyofuku Elem. Gym (Uki)",
    "E4321300010111": "Ogawa Disaster Base (Uki)",
    "E4321300011111": "Rapport Cultural Ctr. (Uki)",
    "E4320200016111": "Kagami Elem. (Yatsushiro)",
    "E4320200004111": "Matsutaka Elem. (Yatsushiro)",
    "E4321300027111": "Industrial Training Hall (Uki)",
    "E4321300019111": "Ogawa Technical H.S. (Uki)",
    "E4320200056111": "Yatsushiro No. 2 J.H.S.",
    "E4310000080111": "Hakuzan Elem. (Kumamoto)",
    "E4321300020111": "Matsubase H.S. (Uki)",
}


def polygon_exteriors(geometries: np.ndarray) -> list[np.ndarray]:
    exteriors: list[np.ndarray] = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
        for part in parts:
            exteriors.append(np.asarray(part.exterior.coords))
    return exteriors


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


def main() -> None:
    threshold = pd.read_csv(THRESHOLD_PATH)
    unavailable = pd.read_csv(UNAVAILABILITY_PATH)
    critical = pd.read_csv(CRITICAL_PATH, dtype={"Shelter ID": str})
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=[
            "Shelter ID",
            "Longitude",
            "Latitude",
            "Shelter Service Class",
        ],
    )
    shelters = shelters.loc[shelters["Shelter Service Class"].eq("general")].copy()
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])
    boundary_geometries = from_wkb(boundaries["Geometry"].to_numpy())
    boundary_polygons = polygon_exteriors(boundary_geometries)

    critical = critical.merge(
        shelters[["Shelter ID", "Longitude", "Latitude"]],
        on="Shelter ID",
        how="left",
        validate="1:1",
    )
    if critical[["Longitude", "Latitude"]].isna().any().any():
        raise ValueError("At least one critical shelter has no mapped coordinates")

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
    fig = plt.figure(figsize=(14.2, 11.0))
    outer = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.78, 1.20],
        left=0.065,
        right=0.985,
        top=0.955,
        bottom=0.070,
        wspace=0.16,
        hspace=0.29,
    )
    ax_a = fig.add_subplot(outer[0, 0])
    ax_b = fig.add_subplot(outer[0, 1])
    lower = outer[1, :].subgridspec(1, 2, width_ratios=[1.18, 0.82], wspace=0.22)
    ax_c = fig.add_subplot(lower[0, 0])
    ax_rank = fig.add_subplot(lower[0, 1])

    # Panel a: capacity threshold sensitivity.
    opening_labels = {
        "At most 415 modeled openings": (COLOR_415, "At most 415 openings"),
        "All 1,156 general shelters available": (COLOR_ALL, "All 1,156 shelters available"),
    }
    for opening_constraint, (color, label) in opening_labels.items():
        frame = threshold.loc[threshold["Opening Constraint"].eq(opening_constraint)].sort_values(
            "Capacity per Open Shelter"
        )
        ax_a.plot(
            frame["Capacity per Open Shelter"],
            frame["Unmet Demand"],
            color=color,
            linewidth=2.0,
            marker="o",
            markersize=5.5,
            label=label,
            zorder=4,
        )
    geographic_floor = float(
        threshold["Scenario Demand"].iloc[0]
        - threshold["Geographically Reachable Demand"].iloc[0]
    )
    ax_a.axhline(
        geographic_floor,
        color="#5F6265",
        linewidth=1.2,
        linestyle=(0, (5, 3)),
        label="15-min geographic minimum unmet",
        zorder=2,
    )
    ax_a.axvline(50, color="#333333", linewidth=0.9, linestyle=(0, (2, 3)), zorder=2)
    ax_a.text(
        53,
        5000,
        "Primary threshold",
        fontsize=7.7,
        color="#333333",
        rotation=90,
        va="top",
    )
    ax_a.scatter(
        [25],
        threshold.loc[
            threshold["Opening Constraint"].eq("At most 415 modeled openings")
            & threshold["Capacity per Open Shelter"].eq(25),
            "Unmet Demand",
        ],
        s=46,
        facecolor="white",
        edgecolor=COLOR_415,
        linewidth=1.2,
        zorder=5,
    )
    ax_a.text(
        29,
        4920,
        "25-person result: 0.21% MIP gap",
        fontsize=7.4,
        color=COLOR_415,
        ha="left",
        va="center",
    )
    ax_a.set_xlim(15, 210)
    ax_a.set_ylim(4050, 5100)
    ax_a.set_xlabel("Standardized capacity per open general shelter (persons)")
    ax_a.set_ylabel("Unmet high-loss-weighted stress demand (persons)")
    ax_a.xaxis.set_major_locator(MultipleLocator(25))
    ax_a.yaxis.set_major_locator(MultipleLocator(200))
    ax_a.grid(color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    ax_a.legend(loc="upper right", bbox_to_anchor=(0.99, 0.88), frameon=False, fontsize=7.7)
    add_panel_heading(ax_a, "a", "Capacity-threshold sensitivity")

    # Panel b: unavailable-facility sensitivity.
    baseline = float(
        unavailable.loc[unavailable["Failure Mode"].eq("baseline"), "Served Percent"].iloc[0]
    )
    random = unavailable.loc[unavailable["Failure Mode"].eq("random")]
    random_summary = random.groupby("Unavailability Share")["Served Percent"].agg(
        mean="mean", minimum="min", maximum="max"
    )
    targeted = unavailable.loc[
        unavailable["Failure Mode"].eq("targeted_high_reachable_pressure")
    ].set_index("Unavailability Share")
    shares = np.array([0.1, 0.2, 0.3])
    x = shares * 100
    width = 3.4
    random_means = random_summary.loc[shares, "mean"].to_numpy()
    random_errors = np.vstack(
        [
            random_means - random_summary.loc[shares, "minimum"].to_numpy(),
            random_summary.loc[shares, "maximum"].to_numpy() - random_means,
        ]
    )
    ax_b.bar(
        x - width / 2,
        random_means,
        width=width,
        color=COLOR_RANDOM,
        edgecolor="#315B78",
        linewidth=0.55,
        yerr=random_errors,
        capsize=3,
        error_kw={"elinewidth": 0.9, "ecolor": "#315B78"},
        label="Random removal (30 draws; mean and range)",
        zorder=3,
    )
    targeted_values = targeted.loc[shares, "Served Percent"].to_numpy()
    ax_b.bar(
        x + width / 2,
        targeted_values,
        width=width,
        color=COLOR_TARGETED,
        edgecolor="#7D2436",
        linewidth=0.55,
        label="Highest reachable-pressure removal",
        zorder=3,
    )
    ax_b.axhline(
        baseline,
        color="#333333",
        linewidth=1.1,
        linestyle=(0, (5, 3)),
        label=f"No removal baseline ({baseline:.1f}%)",
        zorder=2,
    )
    for xpos, value in zip(x + width / 2, targeted_values):
        ax_b.text(
            xpos,
            value + 1.0,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=7.6,
            fontweight="bold",
            color="#5E1D2B",
        )
    ax_b.set_xlim(4, 36)
    ax_b.set_ylim(0, 62)
    ax_b.set_xticks(x, ["10%", "20%", "30%"])
    ax_b.set_xlabel("General shelters unavailable")
    ax_b.set_ylabel("Maximum served demand (%)")
    ax_b.yaxis.set_major_locator(MultipleLocator(10))
    ax_b.grid(axis="y", color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    ax_b.legend(loc="upper right", bbox_to_anchor=(0.99, 0.88), frameon=False, fontsize=7.5)
    add_panel_heading(ax_b, "b", "Facility-unavailability sensitivity")

    # Panel c: locations and ranked losses for the screened critical shelters.
    all_bounds = np.asarray([geometry.bounds for geometry in boundary_geometries])
    x_min, y_min = all_bounds[:, [0, 1]].min(axis=0)
    x_max, y_max = all_bounds[:, [2, 3]].max(axis=0)
    x_padding = 0.018 * (x_max - x_min)
    y_padding = 0.018 * (y_max - y_min)
    mean_latitude = (y_min + y_max) / 2

    ax_c.add_collection(
        PolyCollection(
            boundary_polygons,
            facecolors="#f2f2ef",
            edgecolors="#737373",
            linewidths=0.32,
            zorder=0,
        )
    )
    ax_c.scatter(
        shelters["Longitude"],
        shelters["Latitude"],
        s=3.2,
        marker="o",
        color="#9BA4AA",
        alpha=0.52,
        linewidths=0,
        zorder=3,
    )
    loss = critical["Single-Shelter Service-Loss Lower Bound"].to_numpy(float)
    loss_norm = Normalize(vmin=0, vmax=50)
    bubbles = ax_c.scatter(
        critical["Longitude"],
        critical["Latitude"],
        s=20 + 2.5 * loss,
        c=loss,
        cmap="YlOrRd",
        norm=loss_norm,
        edgecolor="#54201C",
        linewidth=0.55,
        alpha=0.92,
        zorder=7,
    )
    ax_c.scatter(
        HYPOCENTER_LON,
        HYPOCENTER_LAT,
        s=85,
        marker="*",
        facecolor="#CE1B28",
        edgecolor="white",
        linewidth=0.65,
        zorder=10,
    )
    ax_c.set_xlim(x_min - x_padding, x_max + x_padding)
    ax_c.set_ylim(y_min - y_padding, y_max + y_padding)
    ax_c.set_aspect(1 / np.cos(np.deg2rad(mean_latitude)))
    ax_c.xaxis.set_major_locator(MultipleLocator(0.25))
    ax_c.yaxis.set_major_locator(MultipleLocator(0.20))
    ax_c.xaxis.set_major_formatter(FuncFormatter(degree_formatter))
    ax_c.yaxis.set_major_formatter(FuncFormatter(degree_formatter))
    ax_c.tick_params(labelsize=7.3, length=2.5, pad=2)
    ax_c.grid(color="#d6d6d6", linewidth=0.35, linestyle=(0, (2, 3)), zorder=1)
    add_north_arrow(ax_c)
    add_panel_heading(ax_c, "c", "Screened single-shelter criticality")
    colorbar = fig.colorbar(
        bubbles,
        ax=ax_c,
        orientation="horizontal",
        fraction=0.038,
        pad=0.035,
        aspect=30,
    )
    colorbar.set_label("Service-loss lower bound after one shelter is removed (persons)", fontsize=8)
    colorbar.ax.tick_params(labelsize=7, length=2)
    colorbar.outline.set_linewidth(0.45)

    top_ten = critical.sort_values(
        "Single-Shelter Service-Loss Lower Bound", ascending=False
    ).head(10).copy()
    top_ten["Short Name"] = top_ten["Shelter ID"].map(SHORT_NAMES).fillna(top_ten["Shelter ID"])
    top_ten = top_ten.sort_values("Single-Shelter Service-Loss Lower Bound")
    rank_colors = plt.get_cmap("YlOrRd")(loss_norm(top_ten["Single-Shelter Service-Loss Lower Bound"]))
    bars = ax_rank.barh(
        np.arange(len(top_ten)),
        top_ten["Single-Shelter Service-Loss Lower Bound"],
        color=rank_colors,
        edgecolor="#6E3027",
        linewidth=0.45,
        height=0.62,
    )
    ax_rank.set_yticks(np.arange(len(top_ten)), top_ten["Short Name"])
    ax_rank.set_xlim(0, 54)
    ax_rank.set_xlabel("Service-loss lower bound (persons)")
    ax_rank.tick_params(axis="y", labelsize=7.5, length=0, pad=6)
    ax_rank.tick_params(axis="x", labelsize=7.5)
    ax_rank.xaxis.set_major_locator(MultipleLocator(10))
    ax_rank.grid(axis="x", color="#d6d6d6", linewidth=0.4, linestyle=(0, (2, 3)), zorder=0)
    ax_rank.spines[["top", "right", "left"]].set_visible(False)
    for bar, value in zip(bars, top_ten["Single-Shelter Service-Loss Lower Bound"]):
        ax_rank.text(
            value + 0.7,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            ha="left",
            fontsize=7.4,
            color="#303030",
        )
    add_panel_heading(ax_rank, "d", "Ten largest confirmed losses")

    map_legend = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor="#9BA4AA",
            markeredgecolor="none",
            markersize=4,
            label=f"All general shelters (n={len(shelters):,})",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor="#F46D43",
            markeredgecolor="#54201C",
            markeredgewidth=0.4,
            markersize=6,
            label="Screened critical shelters (n=30)",
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
    ]
    fig.legend(
        handles=map_legend,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.014),
        ncol=3,
        frameon=False,
        fontsize=8.1,
        handletextpad=0.5,
        columnspacing=1.5,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
