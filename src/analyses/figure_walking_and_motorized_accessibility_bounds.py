"""Plot walking, motorized, and mixed-mode shelter-accessibility bounds."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
ACCESS_PATH = (
    ROOT
    / "data/exp/prefecture-shelter-multimodal-access/nearest_shelter_motorized_access_corrected.parquet"
)
SHELTER_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
BOUNDARY_PATH = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
MIXED_PATH = (
    ROOT
    / "data/exp/prefecture-shelter-multimodal-access/mixed_mode_accessibility_summary.csv"
)
MUNICIPALITY_PATH = (
    ROOT
    / "data/exp/prefecture-shelter-multimodal-access/municipality_mixed_mode_accessibility.csv"
)
OUTPUT_PATH = (
    ROOT
    / "data/results/figures/Figure_walking_and_motorized_accessibility_bounds.png"
)

DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
WALK_COLUMN = "Walking Reachable in Central Comparison"
MOTOR_COLUMN = "Motorized Reachable in Central Comparison"
REACHABLE_COLOR = "#8FC5D8"
GAP_COLOR = "#C7475B"
SHELTER_COLOR = "#173B52"
LINE_COLOR = "#176B87"
GAIN_COLOR = "#D77A2D"

ENGLISH_MUNICIPALITY_NAMES = {
    "43100": "Kumamoto City", "43202": "Yatsushiro", "43203": "Hitoyoshi",
    "43204": "Arao", "43205": "Minamata", "43206": "Tamana", "43208": "Yamaga",
    "43210": "Kikuchi", "43211": "Uto", "43212": "Kami-Amakusa", "43213": "Uki",
    "43214": "Aso", "43215": "Amakusa", "43216": "Koshi", "43348": "Misato",
    "43364": "Gyokuto", "43367": "Nankan", "43368": "Nagasu", "43369": "Nagomi",
    "43403": "Ozu", "43404": "Kikuyo", "43423": "Minamioguni", "43424": "Oguni",
    "43425": "Ubuyama", "43428": "Takamori", "43432": "Nishihara", "43433": "Minamiaso",
    "43441": "Mifune", "43442": "Kashima", "43443": "Mashiki", "43444": "Kosa",
    "43447": "Yamato", "43468": "Hikawa", "43482": "Ashikita", "43484": "Tsunagi",
    "43501": "Nishiki", "43505": "Taragi", "43506": "Yunomae", "43507": "Mizukami",
    "43510": "Sagara", "43511": "Itsuki", "43512": "Yamae", "43513": "Kuma",
    "43514": "Asagiri", "43531": "Reihoku",
}


def polygon_exteriors(geometries: np.ndarray) -> list[np.ndarray]:
    output: list[np.ndarray] = []
    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
        for part in parts:
            output.append(np.asarray(part.exterior.coords))
    return output


def degree_formatter(value: float, _position: int) -> str:
    return f"{value:.2f}°"


def add_panel_heading(ax: plt.Axes, label: str, descriptor: str) -> None:
    ax.text(
        0.0, 1.025, f"{label}: {descriptor}", transform=ax.transAxes,
        ha="left", va="bottom", fontsize=9.2, fontweight="bold", color="#222222",
        clip_on=False,
    )


def add_north_arrow(ax: plt.Axes) -> None:
    ax.annotate(
        "N", xy=(0.955, 0.955), xytext=(0.955, 0.865), xycoords="axes fraction",
        ha="center", va="center", fontsize=9, fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#313131", "lw": 1.0}, zorder=12,
    )


def add_scale_bar(ax: plt.Axes, latitude: float, length_km: float = 25.0) -> None:
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    length_degrees = length_km / (111.32 * np.cos(np.deg2rad(latitude)))
    x_start = x_min + 0.055 * (x_max - x_min)
    y_start = y_min + 0.055 * (y_max - y_min)
    ax.plot([x_start, x_start + length_degrees], [y_start, y_start], color="#252525", lw=2.2)
    ax.text(x_start + length_degrees / 2, y_start + 0.012, f"{length_km:g} km",
            ha="center", va="bottom", fontsize=7.5, color="#252525")


def main() -> None:
    access = pd.read_parquet(
        ACCESS_PATH,
        columns=["Mesh Geometry", DEMAND_COLUMN, WALK_COLUMN, MOTOR_COLUMN],
    )
    shelters = pd.read_parquet(
        SHELTER_PATH,
        columns=["Longitude", "Latitude", "Shelter Service Class"],
    )
    boundaries = pd.read_parquet(BOUNDARY_PATH, columns=["Geometry"])
    mixed = pd.read_csv(MIXED_PATH)
    municipality = pd.read_csv(MUNICIPALITY_PATH, dtype={"Municipality Code": "string"})

    mesh_geometries = from_wkb(access["Mesh Geometry"].to_numpy())
    boundary_geometries = from_wkb(boundaries["Geometry"].to_numpy())
    mesh_polygons = polygon_exteriors(mesh_geometries)
    boundary_polygons = polygon_exteriors(boundary_geometries)
    all_bounds = np.asarray([geometry.bounds for geometry in boundary_geometries])
    x_min, y_min = all_bounds[:, [0, 1]].min(axis=0)
    x_max, y_max = all_bounds[:, [2, 3]].max(axis=0)
    extent = (
        x_min - 0.018 * (x_max - x_min), x_max + 0.018 * (x_max - x_min),
        y_min - 0.018 * (y_max - y_min), y_max + 0.018 * (y_max - y_min),
    )
    mean_latitude = (y_min + y_max) / 2
    general = shelters["Shelter Service Class"].eq("general")

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.edgecolor": "#5a5a5a", "axes.linewidth": 0.7,
        "xtick.color": "#4a4a4a", "ytick.color": "#4a4a4a",
    })
    fig, axes = plt.subplots(2, 2, figsize=(14.2, 11.0), constrained_layout=False)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.955, bottom=0.085, wspace=0.16, hspace=0.28)

    for index, (ax, column, descriptor) in enumerate((
        (axes[0, 0], WALK_COLUMN, "15-min walking bound"),
        (axes[0, 1], MOTOR_COLUMN, "15-min motorized bound"),
    )):
        reachable = access[column].to_numpy(bool)
        colors = np.where(reachable, REACHABLE_COLOR, GAP_COLOR)
        ax.add_collection(PolyCollection(boundary_polygons, facecolors="#f2f2ef", edgecolors="none", zorder=0))
        ax.add_collection(PolyCollection(mesh_polygons, facecolors=colors, edgecolors="none", rasterized=True, zorder=2))
        ax.add_collection(LineCollection(boundary_polygons, colors="#6f6f6f", linewidths=0.30, alpha=0.82, zorder=5))
        ax.scatter(shelters.loc[general, "Longitude"], shelters.loc[general, "Latitude"],
                   s=4.0, color=SHELTER_COLOR, alpha=0.62, linewidths=0, zorder=7)
        accessible_percent = 100 * access.loc[reachable, DEMAND_COLUMN].sum() / access[DEMAND_COLUMN].sum()
        ax.text(0.98, 0.025, f"Accessible stress load: {accessible_percent:.1f}%",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8.0,
                bbox={"facecolor": "white", "edgecolor": "#b5b5b5", "lw": 0.4, "alpha": 0.90, "pad": 2.3})
        ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
        ax.set_aspect(1 / np.cos(np.deg2rad(mean_latitude)))
        ax.xaxis.set_major_locator(MultipleLocator(0.25)); ax.yaxis.set_major_locator(MultipleLocator(0.20))
        ax.xaxis.set_major_formatter(FuncFormatter(degree_formatter)); ax.yaxis.set_major_formatter(FuncFormatter(degree_formatter))
        ax.tick_params(labelsize=7.5, length=2.5, pad=2)
        ax.grid(color="#d6d6d6", linewidth=0.35, linestyle=(0, (2, 3)), zorder=1)
        add_north_arrow(ax)
        if index == 0:
            add_scale_bar(ax, mean_latitude)
        add_panel_heading(ax, chr(ord("a") + index), descriptor)

    ax_c = axes[1, 0]
    ax_c.plot(
        100 * mixed["Vehicle-Enabled Demand Share"], mixed["Accessible Percent"],
        color=LINE_COLOR, marker="o", linewidth=2.2, markersize=6, zorder=4,
    )
    ax_c.fill_between(
        100 * mixed["Vehicle-Enabled Demand Share"], 0, mixed["Accessible Percent"],
        color=REACHABLE_COLOR, alpha=0.24, zorder=1,
    )
    for row in mixed.itertuples(index=False):
        ax_c.text(100 * row[0], row[6] + 1.5, f"{row[6]:.1f}%", ha="center", va="bottom", fontsize=8)
    ax_c.set_xlim(-3, 103); ax_c.set_ylim(50, 103)
    ax_c.set_xlabel("Vehicle-enabled share of stress demand")
    ax_c.set_ylabel("Accessible stress load")
    ax_c.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_c.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax_c.grid(color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    add_panel_heading(ax_c, "c", "Mixed-mode accessibility envelope")

    ax_d = axes[1, 1]
    wide = municipality.pivot_table(
        index=["Municipality Code", "Municipality"],
        columns="Vehicle-Enabled Demand Share", values="Accessible Percent",
    ).reset_index()
    wide["Gain"] = wide[1.0] - wide[0.0]
    wide["English Municipality"] = wide["Municipality Code"].map(ENGLISH_MUNICIPALITY_NAMES)
    top = wide.nlargest(10, "Gain").sort_values("Gain")
    ax_d.barh(top["English Municipality"], top["Gain"], color=GAIN_COLOR, edgecolor="#8C4B17", linewidth=0.5)
    for y, value in enumerate(top["Gain"]):
        ax_d.text(value + 0.7, y, f"+{value:.1f} pp", va="center", fontsize=7.8)
    ax_d.set_xlim(0, max(55, float(top["Gain"].max()) + 8))
    ax_d.set_xlabel("Gain from walking-only to vehicle-enabled bound (percentage points)")
    ax_d.grid(axis="x", color="#d7d7d7", linewidth=0.45, linestyle=(0, (2, 3)), zorder=0)
    add_panel_heading(ax_d, "d", "Municipalities with largest mode-access gain")

    legend_handles = [
        Patch(facecolor=REACHABLE_COLOR, edgecolor="none", label="Reachable populated mesh"),
        Patch(facecolor=GAP_COLOR, edgecolor="none", label="Unreachable populated mesh"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=SHELTER_COLOR,
               markeredgecolor="none", markersize=4.5, label=f"General shelter (n={int(general.sum()):,})"),
        Line2D([0], [0], color="#6f6f6f", linewidth=0.7, label="Municipality / ward boundary"),
    ]
    fig.legend(handles=legend_handles, loc="center", bbox_to_anchor=(0.5, 0.515),
               ncol=4, frameon=False, fontsize=8.2, handletextpad=0.5, columnspacing=1.5)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
