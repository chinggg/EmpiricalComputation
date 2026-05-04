"""Table 1: correctness on Random vs Familiar instances at sizes 10..50."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


TABLE1_SIZES = [10, 20, 30, 40, 50]


def table1_dataframe(random_df: pd.DataFrame, familiar_df: pd.DataFrame) -> pd.DataFrame:
    """Build the dataframe shown in Table 1.

    Columns: Array Size, Random, Familiar, Familiar_n
    Familiar's count is the number of trials actually returned at that size
    (which can differ from the requested size when the LLM ignores the count).
    """
    r = _by_size(random_df)
    f = _by_size(familiar_df)
    rows = []
    for s in TABLE1_SIZES:
        row = {
            "Array Size": s,
            "Random": _fmt(r.get(s, (None, 0))[0]),
            "Familiar": _fmt(f.get(s, (None, 0))[0]),
            "Familiar_n": f.get(s, (None, 0))[1],
        }
        rows.append(row)
    return pd.DataFrame(rows)


def render_table1(df: pd.DataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Render exactly as in the paper: "0.70 (161)" in the Familiar column.
    paper = df.copy()
    paper["Familiar"] = [
        f"{v} ({n})" if v != "—" else "—"
        for v, n in zip(paper["Familiar"], paper["Familiar_n"])
    ]
    paper = paper[["Array Size", "Random", "Familiar"]]

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
        # Save both: csv next to the chosen path, plus a printable .md.
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
