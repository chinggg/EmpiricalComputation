"""Figure 1: 5 rows × 5 cols comparison plot.

Row 0: Time (s) — non-thinking presets
Row 1: Time (s) — thinking preset
Row 2: Average Correctness — all presets
Row 3: Time to First Correct — non-thinking presets
Row 4: Time to First Correct — thinking preset
Cols: Sorting | Sorted Search | Unsorted Search | SSP | Substring

Thinking is separated into its own rows so the y-scale difference does not
hide the linear behaviour of the other presets.
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

MAX_SIZES = {
    "sorted_search": 200,
    "unsorted_search": 200,
    "ssp": 51,
}

PRESET_STYLES = {
    "thinking":      {"color": "C1", "linewidth": 2.2, "markersize": 4, "zorder": 10},
    "default":       {"color": "#7f7f7f", "linewidth": 1.2, "markersize": 3, "alpha": 0.7},
    "deterministic": {"color": "#1f77b4", "linewidth": 1.2, "markersize": 3, "alpha": 0.7},
}


def render_figure1(
    summaries_map: dict[str, dict[str, pd.DataFrame]],
    selfgen_map: dict[str, pd.DataFrame],
    out_path: Path,
    log_scale: bool = False,
) -> Path:
    """`summaries_map` is {preset_name: {problem_name: summary_df}}.
    `selfgen_map` is {preset_name: selfgen_df}.
    """
    fig, axes = plt.subplots(5, 5, figsize=(16, 9))

    presets = sorted(summaries_map.keys())
    thinking_presets = [p for p in presets if p == "thinking"]
    other_presets    = [p for p in presets if p != "thinking"]

    def _plot_group(group, col, key, ax_t, ax_c, ax_f):
        for preset in group:
            df = summaries_map[preset].get(key, pd.DataFrame())
            if df.empty:
                continue
            if key in MAX_SIZES:
                df = df[df["size"] <= MAX_SIZES[key]]
            style = PRESET_STYLES.get(preset, {})
            color = style.get("color", "black")
            ax_t.plot(df["size"], df["mean_time"],        "o-", label=preset, **style)
            ax_c.plot(df["size"], df["mean_correctness"], "o-", label=preset, **style)
            ax_f.plot(df["size"], df["time_to_first"],    "o-", label=preset, **style)
            last = df.iloc[-1]
            lx, lt, lc, lf = last["size"], last["mean_time"], last["mean_correctness"], last["time_to_first"]
            ax_t.text(lx, lt, f" {lt:.1f}s", color=color, va="center", fontsize=7, fontweight="bold")
            ax_c.text(lx, lc, f" {lc:.1f}",  color=color, va="center", fontsize=7, fontweight="bold")
            if not pd.isna(lf):
                ax_f.text(lx, lf, f" {lf:.1f}s", color=color, va="center", fontsize=7, fontweight="bold")

    for col, (key, title) in enumerate(COLUMNS):
        # rows: 0=Time(other), 1=Time(thinking), 2=Correctness, 3=TTF(other), 4=TTF(thinking)
        ax_t_o, ax_t_k, ax_c, ax_f_o, ax_f_k = (
            axes[0, col], axes[1, col], axes[2, col], axes[3, col], axes[4, col]
        )

        _plot_group(other_presets,    col, key, ax_t_o, ax_c, ax_f_o)
        _plot_group(thinking_presets, col, key, ax_t_k, ax_c, ax_f_k)

        ax_t_o.set_title(title)
        for ax, ylabel in (
            (ax_t_o, "Time (s)"),
            (ax_t_k, "Time (s) [thinking]"),
            (ax_c,   "Avg Correctness"),
            (ax_f_o, "Time to First (s)"),
            (ax_f_k, "Time to First (s) [thinking]"),
        ):
            ax.set_xlabel("Size")
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            curr_xlim = ax.get_xlim()
            ax.set_xlim(curr_xlim[0], curr_xlim[1] * 1.15)
            if log_scale and ax in (ax_t_o, ax_t_k, ax_f_o, ax_f_k):
                ax.set_yscale("log")

        # # to display outlier datapoint with broken axis
        # if key == "ssp":
        #     # Folded axis for SSP Thinking outlier at size 400
        #     if "thinking" in summaries_map:
        #         df_full = summaries_map["thinking"].get(key, pd.DataFrame())
        #         p400 = df_full[df_full["size"] == 400]
        #         p51 = df_full[df_full["size"] == 51]
                
        #         if not p400.empty and not p51.empty:
        #             # Virtual x-position for the folded point
        #             vx = 62 
        #             th_color = PRESET_STYLES["thinking"]["color"]
                    
        #             # Set x-limits and ticks for the fold
        #             for ax in (ax_t, ax_c, ax_f):
        #                 ax.set_xlim(-2, 68)
        #                 xticks = [0, 10, 20, 30, 40, 50, vx]
        #                 ax.set_xticks(xticks)
        #                 ax.set_xticklabels(["0", "10", "20", "30", "40", "50", "400"])
                        
        #                 # Draw break marks on the x-axis (bottom spine)
        #                 # Position in data coords, height in axes coords
        #                 bx = 56
        #                 d = 0.015
        #                 kwargs = dict(color='k', clip_on=False, linewidth=1)
        #                 ax.plot([bx-1, bx+1], [-d, d], transform=ax.get_xaxis_transform(), **kwargs)
        #                 ax.plot([bx, bx+2], [-d, d], transform=ax.get_xaxis_transform(), **kwargs)

        #             # Plot the folded points and dashed connection
        #             # Correctness
        #             y_c_51 = p51["mean_correctness"].iloc[0]
        #             y_c_400 = p400["mean_correctness"].iloc[0]
        #             ax_c.plot([51, vx], [y_c_51, y_c_400], "--", color=th_color, alpha=0.4, linewidth=1)
        #             ax_c.plot(vx, y_c_400, "o", color=th_color, markersize=5)

        #             # Time (needs y-fold if > 150)
        #             y_t_51 = p51["mean_time"].iloc[0]
        #             y_t_400 = p400["mean_time"].iloc[0]
        #             y_max_normal = 150 
                    
        #             if y_t_400 > y_max_normal and not log_scale:
        #                 ax_t.set_ylim(0, y_max_normal)
        #                 vy_t = y_max_normal * 0.92
        #                 ax_t.plot([51, vx], [y_t_51, vy_t], "--", color=th_color, alpha=0.4, linewidth=1)
        #                 ax_t.plot(vx, vy_t, "o", color=th_color, markersize=5)
                        
        #                 # Clean ceiling for the tick label
        #                 y_t_ceil = ((y_t_400 // 50) + 1) * 50
        #                 ax_t.set_yticks([0, 50, 100, vy_t])
        #                 ax_t.set_yticklabels(["0", "50", "100", f"{y_t_ceil:.0f}"])
                        
        #                 # Exact value label near the point
        #                 ax_t.text(vx - 1, vy_t, f"{y_t_400:.0f}s ", color=th_color, ha="right", va="center", fontsize=7, fontweight="bold")
                        
        #                 # Y-break mark
        #                 by = vy_t - 12
        #                 ax_t.plot([-d, d], [by-2, by+2], transform=ax_t.get_yaxis_transform(), **kwargs)
        #                 ax_t.plot([-d, d], [by, by+4], transform=ax_t.get_yaxis_transform(), **kwargs)
        #             else:
        #                 ax_t.plot([51, vx], [y_t_51, y_t_400], "--", color=th_color, alpha=0.4, linewidth=1)
        #                 ax_t.plot(vx, y_t_400, "o", color=th_color, markersize=5)

        #             # Time to First (similar to Time)
        #             y_f_51 = p51["time_to_first"].iloc[0]
        #             y_f_400 = p400["time_to_first"].iloc[0]
        #             if not pd.isna(y_f_400) and y_f_400 > y_max_normal and not log_scale:
        #                 ax_f.set_ylim(0, y_max_normal)
        #                 vy_f = y_max_normal * 0.92
        #                 ax_f.plot([51, vx], [y_f_51, vy_f], "--", color=th_color, alpha=0.4, linewidth=1)
        #                 ax_f.plot(vx, vy_f, "o", color=th_color, markersize=5)
                        
        #                 # Clean ceiling for the tick label
        #                 y_f_ceil = ((y_f_400 // 50) + 1) * 50
        #                 ax_f.set_yticks([0, 50, 100, vy_f])
        #                 ax_f.set_yticklabels(["0", "50", "100", f"{y_f_ceil:.0f}"])
                        
        #                 # Exact value label near the point
        #                 ax_f.text(vx - 1, vy_f, f"{y_f_400:.0f}s ", color=th_color, ha="right", va="center", fontsize=7, fontweight="bold")
                        
        #                 # Y-break mark
        #                 by_f = vy_f - 12
        #                 ax_f.plot([-d, d], [by_f-2, by_f+2], transform=ax_f.get_yaxis_transform(), **kwargs)
        #                 ax_f.plot([-d, d], [by_f, by_f+4], transform=ax_f.get_yaxis_transform(), **kwargs)
        #             elif not pd.isna(y_f_400):
        #                 ax_f.plot([51, vx], [y_f_51, y_f_400], "--", color=th_color, alpha=0.4, linewidth=1)
        #                 ax_f.plot(vx, y_f_400, "o", color=th_color, markersize=5)

        ax_c.set_ylim(-0.05, 1.05)

    if len(presets) > 1:
        # Put legend in the bottom-right axis to keep it "inside" the layout
        handles, labels = axes[0, 0].get_legend_handles_labels()
        think_h, think_l = axes[1, 0].get_legend_handles_labels()
        all_handles = handles + [h for h, l in zip(think_h, think_l) if l not in labels]
        all_labels  = labels  + [l for l in think_l if l not in labels]
        if all_handles:
            axes[4, 4].legend(all_handles, all_labels, loc="lower right", title="Presets", frameon=True)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
