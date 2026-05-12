"""JSONL → tidy CSV summaries used by the plotting code."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .storage import read_records


def load_trials(path: Path) -> pd.DataFrame:
    rows = list(read_records(path))
    if not rows:
        return pd.DataFrame(
            columns=["size", "trial", "correct", "elapsed_s", "variant", "model",
                     "tokens_per_second", "reasoning_output_tokens"]
        )
    df = pd.DataFrame(rows)
    # Fix bias: timeouts recorded as 0.0 should be the timeout value (600s).
    if "error" in df.columns and "elapsed_s" in df.columns:
        is_timeout = df["error"].str.contains("Timeout", na=False, case=False)
        df.loc[is_timeout, "elapsed_s"] = 600.0
    return df


def summarize(df: pd.DataFrame, size_col: str = "size") -> pd.DataFrame:
    """Per-size aggregate.

    Columns: size, n, mean_correctness, mean_time, time_to_first,
             mean_tps, mean_reasoning_tokens.

    `size_col` lets the caller bin by `actual_size` instead of the requested
    `size` (useful for the familiarity selfgen panel).
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "size", "n", "mean_correctness", "mean_time", "time_to_first",
            "mean_tps", "mean_reasoning_tokens",
        ])
    df = df.copy()

    # Bias fix: Only count trials that were successfully parsed.
    # Timeouts (parsed=None) are excluded to avoid skewing average time/correctness.
    if "parsed" in df.columns:
        df = df[df["parsed"].notnull()].copy()

    if df.empty:
        return pd.DataFrame(columns=[
            "size", "n", "mean_correctness", "mean_time", "time_to_first",
            "mean_tps", "mean_reasoning_tokens",
        ])

    df["correct"] = df["correct"].astype(bool).astype(int)

    if size_col != "size":
        if "extra" in df.columns:
            df[size_col] = df["extra"].apply(
                lambda e: (e or {}).get(size_col) if isinstance(e, dict) else None
            )
        df[size_col] = df[size_col].fillna(df["size"]).astype(int)

    # Optional stat columns may be absent in older or mock data.
    for col in ("tokens_per_second", "reasoning_output_tokens"):
        if col not in df.columns:
            df[col] = np.nan

    g = df.groupby(size_col)
    out = g.agg(
        n=("trial", "count"),
        mean_correctness=("correct", "mean"),
        mean_time=("elapsed_s", "mean"),
        mean_tps=("tokens_per_second", "mean"),
        mean_reasoning_tokens=("reasoning_output_tokens", "mean"),
    ).reset_index().rename(columns={size_col: "size"})

    # Expected time to first correct solution: t / p (geometric); inf if p == 0.
    with np.errstate(divide="ignore", invalid="ignore"):
        ttf = out["mean_time"] / out["mean_correctness"].replace(0, np.nan)
    out["time_to_first"] = ttf
    return out.sort_values("size").reset_index(drop=True)


def write_summary_csv(df: pd.DataFrame, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
