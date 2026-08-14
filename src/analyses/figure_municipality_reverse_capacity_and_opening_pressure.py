"""Visualize municipality reverse capacity and shelter-opening pressure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize, PowerNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
from shapely import from_wkb
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[2]
MUNICIPALITY_RESULTS = (
    ROOT / "data/exp/capacity-threshold-estimate/municipality_capacity_thresholds.csv"
)
BOUNDARY_PATH = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
OUTPUT_PATH = (
    ROOT
    / "data/results/figures/Figure_municipality_reverse_capacity_and_opening_pressure.png"
)

PRIMARY_SCENARIO = "Observed-use stress, high housing-loss weighted"
HYPOCENTER_LAT = 32 + 37.5 / 60
HYPOCENTER_LON = 130 + 40.7 / 60

ENGLISH_NAMES = {
    "43100": "Kumamoto City",
    "43202": "Yatsushiro",
    "43204": "Arao",
    "43206": "Tamana",
    "43211": "Uto",
    "43213": "Uki",
    "43216": "Koshi",
    "43348": "Misato",
    "43404": "Kikuyo",
    "43443": "Mashiki",
    "43468": "Hikawa",
}


def polygon_exteriors(geometry: object) -> list[np.ndarray]:
    if geometry is None or geometry.is_empty:
        return []
    parts = geometry.geoms if geometry.geom_type == "MultiPolygon" else (geometry,)
    return [np.asarray(part.exterior.coords) for part in parts]


def municipality_code(code: str) -> str:
    """Collapse Kumamoto City's five ward codes to its municipality code."""
    return "43100" if code.startswith("4310") else code


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


def add_pressure_labels(
    ax: plt.Axes,
    geometries: dict[str, object],
    values: pd.Series,
    codes: list[str],
    suffix: str,
) -> None:
    offsets = {
        "43100": (28, 17),
        "43202": (-56, -6),
        "43213": (34, 13),
        "43468": (-52, 20),
    }
    for code in codes:
        point = geometries[code].representative_point()
        dx, dy = offsets.get(code, (24, 12))
        ax.annotate(
            f"{ENGLISH_NAMES.get(code, code)}  {values.loc[code]:.0f}{suffix}",
            xy=(point.x, point.y),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.2,
            fontweight="bold",
            color="#252525",
            ha="left" if dx >= 0 else "right",
            va="center",
            arrowprops={"arrowstyle": "-", "color": "#4f4f4f", "lw": 0.55},
            bbox={"facecolor": "white", "edgecolor": "#9b9b9b", "lw": 0.4, "alpha": 0.9, "pad": 1.8},
            zorder=13,
        )


def draw_map(
    ax: plt.Axes,
    geometries: dict[str, object],
    values: pd.Series,
    norm: Normalize,
    colorbar_label: str,
    panel_label: str,
    panel_descriptor: str,
    label_codes: list[str],
    label_suffix: str,
    extent: tuple[float, float, float, float],
    mean_latitude: float,
) -> None:
    cmap = plt.get_cmap("YlOrRd")
    polygons: list[np.ndarray] = []
    facecolors: list[object] = []
    for code, geometry in geometries.items():
        parts = polygon_exteriors(geometry)
        polygons.extend(parts)
        color = cmap(norm(float(values.loc[code])))
        facecolors.extend([color] * len(parts))

    ax.add_collection(
        PolyCollection(
            polygons,
            facecolors=facecolors,
            edgecolors="#777777",
            linewidths=0.42,
            zorder=2,
        )
    )

    for code in label_codes:
        ax.add_collection(
            PolyCollection(
                polygon_exteriors(geometries[code]),
                facecolors="none",
                edgecolors="#222222",
                linewidths=1.15,
                zorder=7,
            )
        )

    ax.scatter(
        HYPOCENTER_LON,
        HYPOCENTER_LAT,
        s=82,
        marker="*",
        facecolor="#CE1B28",
        edgecolor="white",
        linewidth=0.65,
        zorder=10,
    )
    add_pressure_labels(ax, geometries, values, label_codes, label_suffix)

    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_aspect(1 / np.cos(np.deg2rad(mean_latitude)))
    ax.xaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_major_locator(MultipleLocator(0.20))
    ax.xaxis.set_major_formatter(FuncFormatter(degree_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(degree_formatter))
    ax.tick_params(labelsize=7.3, length=2.5, pad=2)
    ax.grid(color="#d8d8d8", linewidth=0.35, linestyle=(0, (2, 3)), zorder=0)
    add_north_arrow(ax)
    add_panel_heading(ax, panel_label, panel_descriptor)

    colorbar = plt.colorbar(
        ScalarMappable(norm=norm, cmap=cmap),
        ax=ax,
        orientation="horizontal",
        fraction=0.038,
        pad=0.035,
        aspect=32,
    )
    colorbar.set_label(colorbar_label, fontsize=8.2, labelpad=3)
    colorbar.ax.tick_params(labelsize=7.2, length=2)
    colorbar.outline.set_linewidth(0.45)


def main() -> None:
    municipality_results = pd.read_csv(MUNICIPALITY_RESULTS, dtype={"Municipality Code": str})
    primary = municipality_results.loc[
        municipality_results["Demand Scenario"].eq(PRIMARY_SCENARIO)
    ].copy()
    primary["Municipality Code"] = primary["Municipality Code"].str.zfill(5)
    primary = primary.set_index("Municipality Code")

    boundary = pd.read_parquet(
        BOUNDARY_PATH,
        columns=["Municipality Code", "Municipality Name", "Geometry"],
    )
    boundary["Municipality Code"] = (
        boundary["Municipality Code"].astype(str).map(municipality_code)
    )
    boundary["Geometry Decoded"] = from_wkb(boundary["Geometry"].to_numpy())
    geometries = {
        code: unary_union(group["Geometry Decoded"].tolist())
        for code, group in boundary.groupby("Municipality Code", sort=True)
    }
    missing = set(primary.index) - set(geometries)
    if missing:
        raise ValueError(f"Missing municipality geometries: {sorted(missing)}")

    all_bounds = np.asarray([geometry.bounds for geometry in geometries.values()])
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

    required_capacity = primary["Required Capacity if All General Shelters Open"]
    minimum_openings_50 = primary["Minimum Open Shelters Required at 50 Persons"]
    minimum_openings_100 = primary["Minimum Open Shelters Required at 100 Persons"]

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
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.28, 0.78],
        left=0.045,
        right=0.985,
        top=0.98,
        bottom=0.080,
        wspace=0.12,
        hspace=0.38,
    )
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, :])

    draw_map(
        ax_a,
        geometries,
        required_capacity,
        Normalize(vmin=0, vmax=50),
        "Required average capacity if all local general shelters open (persons)",
        "a",
        "Average capacity required under high-loss weighting",
        ["43202", "43213", "43468"],
        "",
        extent,
        mean_latitude,
    )
    draw_map(
        ax_b,
        geometries,
        minimum_openings_100,
        PowerNorm(gamma=0.62, vmin=0, vmax=35),
        "Minimum local general shelters to open at 100 persons each",
        "b",
        "Minimum openings under the 100-person central case",
        ["43100", "43202", "43213"],
        "",
        extent,
        mean_latitude,
    )

    top = primary.nlargest(10, "Required Capacity if All General Shelters Open").copy()
    top["English Municipality"] = [
        ENGLISH_NAMES.get(code, code) for code in top.index
    ]
    top = top.sort_values("Required Capacity if All General Shelters Open")
    y = np.arange(len(top))
    height = 0.34
    bars_50 = ax_c.barh(
        y - height / 2,
        top["Minimum Open Shelters Required at 50 Persons"],
        height=height,
        color="#D77A2D",
        edgecolor="#8C4B17",
        linewidth=0.55,
        label="50-person conservative stress case",
        zorder=3,
    )
    bars_100 = ax_c.barh(
        y + height / 2,
        top["Minimum Open Shelters Required at 100 Persons"],
        height=height,
        color="#176B87",
        edgecolor="#0D485D",
        linewidth=0.55,
        label="100-person central capacity case",
        zorder=3,
    )
    for bars in (bars_50, bars_100):
        for bar in bars:
            value = int(round(bar.get_width()))
            ax_c.text(
                value + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{value}",
                ha="left",
                va="center",
                fontsize=7.5,
                color="#303030",
            )
    ax_c.set_yticks(y, top["English Municipality"])
    ax_c.invert_yaxis()
    ax_c.set_xlim(0, 75)
    ax_c.set_xlabel("Municipality-contained minimum general-shelter openings", fontsize=8.6)
    ax_c.tick_params(axis="y", labelsize=8.2, length=0, pad=8)
    ax_c.tick_params(axis="x", labelsize=8, length=3)
    ax_c.xaxis.set_major_locator(MultipleLocator(10))
    ax_c.grid(axis="x", color="#d5d5d5", linewidth=0.5, linestyle=(0, (2, 3)), zorder=0)
    ax_c.spines[["top", "right", "left"]].set_visible(False)
    ax_c.legend(loc="lower right", frameon=False, fontsize=8.0)
    add_panel_heading(ax_c, "c", "Opening requirements for one high-loss-weighted scenario")

    legend_handles = [
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
            color="#222222",
            linewidth=1.15,
            label="Labeled high-pressure municipality",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.405),
        ncol=2,
        frameon=False,
        fontsize=8.2,
        handletextpad=0.5,
        columnspacing=1.6,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
