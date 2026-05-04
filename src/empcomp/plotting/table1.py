"""Table 1: correctness on Random vs Familiar instances at sizes 10..50."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


TABLE1_SIZES = [10, 20, 30, 40, 50]


def table1_dataframe(
    random_df: pd.DataFrame,
    familiar_df: pd.DataFrame,
    bucket_width: int = 5,
) -> pd.DataFrame:
    """Build the dataframe shown in Table 1.

    Columns: Array Size, Random, Familiar, Familiar_n.
    Random is bucketed by `size` (the requested input length, which equals
    the actual length for `random.sample`). Familiar is bucketed by the
    *actual* returned length (the paper's "Number of instances actually
    returned with that size"), within ±bucket_width of the row label —
    because gemma-4 rarely returns *exactly* 50 numbers when asked for 50.
    """
    r = _by_size(random_df)
    f_actual = _familiar_by_actual_size(familiar_df)
    rows = []
    for s in TABLE1_SIZES:
        rand_mean, _ = r.get(s, (None, 0))
        fam_mean, fam_n = _bucket(f_actual, s, bucket_width)
        rows.append(
            {
                "Array Size": s,
                "Random": _fmt(rand_mean),
                "Familiar": _fmt(fam_mean),
                "Familiar_n": fam_n,
            }
        )
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


def _familiar_by_actual_size(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-trial dataframe of (actual_size, correct) for familiar trials.

    Falls back to the requested `size` if `actual_size` isn't recorded.
    """
    if df.empty:
        return pd.DataFrame(columns=["actual_size", "correct"])
    df = df.copy()
    df["correct"] = df["correct"].astype(bool).astype(int)
    if "extra" in df.columns:
        df["actual_size"] = df["extra"].apply(
            lambda e: (e or {}).get("actual_size") if isinstance(e, dict) else None
        )
    if "actual_size" not in df.columns or df["actual_size"].isna().all():
        df["actual_size"] = df["size"]
    df["actual_size"] = df["actual_size"].fillna(df["size"]).astype(int)
    return df[["actual_size", "correct"]]


def _bucket(
    df: pd.DataFrame, center: int, half_width: int
) -> tuple[float | None, int]:
    if df.empty:
        return (None, 0)
    sub = df[
        (df["actual_size"] >= center - half_width)
        & (df["actual_size"] <= center + half_width)
    ]
    if sub.empty:
        return (None, 0)
    return (float(sub["correct"].mean()), int(len(sub)))


def _fmt(v: float | None) -> str:
    return "—" if v is None else f"{v:.2f}"
