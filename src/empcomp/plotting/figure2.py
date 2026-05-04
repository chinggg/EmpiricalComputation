"""Figure 2: per-language correctness vs size."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def render_figure2(
    per_language: dict[str, pd.DataFrame],
    out_path: Path,
    language_order: list[str] | None = None,
) -> Path:
    """`per_language` maps lang code → summary df with size, mean_correctness."""
    if language_order is None:
        language_order = list(per_language.keys())

    fig, ax = plt.subplots(figsize=(10, 7))
    for lang in language_order:
        df = per_language.get(lang)
        if df is None or df.empty:
            continue
        ax.plot(
            df["size"],
            df["mean_correctness"],
            marker="o",
            markersize=5,
            label=f"correctness ({lang})",
        )

    ax.set_xlabel("Size")
    ax.set_ylabel("Average Correctness")
    ax.set_title("Average Correctness by Size for Each Language", fontweight="bold")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.5)
    ax.legend(title="Languages", loc="upper right")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
