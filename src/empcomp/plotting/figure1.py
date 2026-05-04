"""Figure 1: 4 rows × 5 cols comparison plot.

Row 0: Time (seconds)              Row 1: Average Correctness
Row 2: Time to First Correct       Row 3: Selfgen Sort (left col only)
Cols: Sorting | Sorted Search | Unsorted Search | SSP | Substring

Matches the layout shown in paper/comparison_plots.pdf.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


COLUMNS = [
    ("sort",            "Sorting"),
    ("sorted_search",   "Sorted Search"),
    ("unsorted_search", "Unsorted Search"),
    ("ssp",             "SSP"),
    ("substring",       "Substring"),
]


def render_figure1(
    summaries: dict[str, pd.DataFrame],
    selfgen: pd.DataFrame | None,
    out_path: Path,
) -> Path:
    """`summaries` keys are problem names (sort, sorted_search, ...).
    `selfgen` is the per-size correctness for the familiar-sort variant.
    """
    fig, axes = plt.subplots(4, 5, figsize=(16, 11))

    for col, (key, title) in enumerate(COLUMNS):
        df = summaries.get(key, pd.DataFrame())
        ax_t, ax_c, ax_f = axes[0, col], axes[1, col], axes[2, col]

        if not df.empty:
            ax_t.plot(df["size"], df["mean_time"], "o-", markersize=4)
            ax_c.plot(df["size"], df["mean_correctness"], "o-", markersize=4)
            ax_f.plot(df["size"], df["time_to_first"], "o-", markersize=4)

        ax_t.set_title(title)
        for ax, ylabel in (
            (ax_t, "Time (seconds)"),
            (ax_c, "Average Correctness"),
            (ax_f, "Time to First Correct Solution"),
        ):
            ax.set_xlabel("Size")
            ax.set_ylabel(ylabel)
        ax_c.set_ylim(0.0, 1.0)

    # Selfgen panel: bottom-left, others hidden.
    sg_ax = axes[3, 0]
    for col in range(1, 5):
        axes[3, col].axis("off")
    if selfgen is not None and not selfgen.empty:
        sg_ax.plot(selfgen["size"], selfgen["mean_correctness"], "-", linewidth=1)
    sg_ax.set_xlabel("Size")
    sg_ax.set_ylabel("Selfgen Sort\nAverage Correctness")
    sg_ax.set_ylim(0.0, 1.0)
    sg_ax.grid(True, alpha=0.3)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
