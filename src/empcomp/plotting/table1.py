"""Table 1: correctness on Random vs Familiar instances at sizes 10..50.

Both columns are bucketed by the *requested* size. The model's actual
returned length only differs from the request by a few items (gemma asked
for 50 returns 46), and those small offsets land in the same bucket
naturally — so we don't bother with a tolerance window. Each row is the
mean over N>=30 trials. The paper's parenthesized N count is intentionally
omitted: with a fixed N per row it carries no information.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


TABLE1_SIZES = [10, 25, 50, 75, 100]


def table1_dataframe(
    random_df: pd.DataFrame,
    familiar_df: pd.DataFrame,
) -> pd.DataFrame:
    r = _by_size(random_df)
    f = _by_size(familiar_df)
    rows = []
    for s in TABLE1_SIZES:
        rand_mean, rand_n = r.get(s, (None, 0))
        fam_mean, fam_n = f.get(s, (None, 0))
        rows.append(
            {
                "Array Size": s,
                "Random": _fmt(rand_mean),
                "Familiar": _fmt(fam_mean),
                "Random_n": rand_n,
                "Familiar_n": fam_n,
            }
        )
    return pd.DataFrame(rows)


def render_table1(df: pd.DataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    paper = df[["Array Size", "Random", "Familiar"]]

    md_lines = [
        "| " + " | ".join(paper.columns) + " |",
        "|" + "|".join(["---"] * len(paper.columns)) + "|",
    ]
    for _, row in paper.iterrows():
        md_lines.append("| " + " | ".join(str(v) for v in row.values) + " |")
    md = "\n".join(md_lines) + "\n"

    if out_path.suffix == ".md":
        out_path.write_text(md, encoding="utf-8")
    else:
        # Save the full df (with N columns for QA) to CSV, plus a printable .md.
        df.to_csv(out_path, index=False)
        out_path.with_suffix(".md").write_text(md, encoding="utf-8")
    return out_path


def _by_size(df: pd.DataFrame) -> dict[int, tuple[float, int]]:
    if df.empty:
        return {}
    df = df.copy()
    df["correct"] = df["correct"].astype(bool).astype(int)
    out = {}
    for size, sub in df.groupby("size"):
        out[int(size)] = (sub["correct"].mean(), int(len(sub)))
    return out


def _fmt(v: float | None) -> str:
    return "—" if v is None else f"{v:.2f}"
