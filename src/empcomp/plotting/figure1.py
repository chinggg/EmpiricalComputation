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
    summaries_map: dict[str, dict[str, pd.DataFrame]],
    selfgen_map: dict[str, pd.DataFrame],
    out_path: Path,
    log_scale: bool = False,
) -> Path:
    """`summaries_map` is {preset_name: {problem_name: summary_df}}.
    `selfgen_map` is {preset_name: selfgen_df}.
    """
    fig, axes = plt.subplots(3, 5, figsize=(16, 9))

    presets = sorted(summaries_map.keys())

    for col, (key, title) in enumerate(COLUMNS):
        ax_t, ax_c, ax_f = axes[0, col], axes[1, col], axes[2, col]

        for preset in presets:
            df = summaries_map[preset].get(key, pd.DataFrame())
            if not df.empty:
                ax_t.plot(df["size"], df["mean_time"], "o-", markersize=4, label=preset)
                ax_c.plot(df["size"], df["mean_correctness"], "o-", markersize=4, label=preset)
                ax_f.plot(df["size"], df["time_to_first"], "o-", markersize=4, label=preset)

        ax_t.set_title(title)
        for ax, ylabel in (
            (ax_t, "Time (seconds)"),
            (ax_c, "Average Correctness"),
            (ax_f, "Time to First Correct Solution"),
        ):
            ax.set_xlabel("Size")
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            
            if log_scale and ax in (ax_t, ax_f):
                ax.set_yscale("log")

        ax_c.set_ylim(-0.05, 1.05)

    if len(presets) > 1:
        # Put legend in the bottom-right axis to keep it "inside" the layout
        handles, labels = axes[0, 0].get_legend_handles_labels()
        if handles:
            axes[2, 4].legend(handles, labels, loc="lower right", title="Presets", frameon=True)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
