"""
Aggregate per-trial text outputs into a CSV with averaged metrics.

- Input: a model/experiment OUTDIR produced by scripts, e.g.,
  output_models/<model_tag>/<experiment_tag>/
- Output: a CSV with columns compatible with plotting and optional
  normalized correctness when available.

Usage:
  python analysis/aggregate_results.py --outdir path/to/OUTDIR \
      --output-csv analysis/aggregates/<name>.csv

Notes:
- The script autodetects file names:
  * sizes:    any file matching pattern contains 'size' (case-insensitive)
  * times:    any file starting with 'time' or containing '/time'
  * correctness (strict): first file containing 'correctness' but not 'normalized'
  * correctness (normalized): file containing 'correctness' and 'normalized' (optional)
- If multiple candidates exist per kind, the first match will be used.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd


def _read_lines(path: Path) -> List[str]:
    with path.open("r") as f:
        return [line.strip() for line in f.read().splitlines() if line.strip() != ""]


def _detect_files(outdir: Path) -> Dict[str, Path]:
    candidates: Dict[str, List[Path]] = {
        "sizes": [],
        "times": [],
        "correctness": [],
        "correctness_normalized": [],
    }
    for p in sorted(outdir.glob("*")):
        name_lower = p.name.lower()
        if not p.is_file():
            continue
        if "size" in name_lower:
            candidates["sizes"].append(p)
        if name_lower.startswith("time") or name_lower.endswith("/time.txt") or name_lower == "time.txt":
            candidates["times"].append(p)
        if "correctness" in name_lower:
            if "normalized" in name_lower:
                candidates["correctness_normalized"].append(p)
            else:
                candidates["correctness"].append(p)

    selected: Dict[str, Path] = {}
    for key in ["sizes", "times", "correctness"]:
        if len(candidates[key]) == 0:
            raise FileNotFoundError(f"Could not find required file for '{key}' in {outdir}")
        selected[key] = candidates[key][0]
    if len(candidates["correctness_normalized"]) > 0:
        selected["correctness_normalized"] = candidates["correctness_normalized"][0]
    return selected


def _to_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def _to_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None


def aggregate(outdir: Path) -> pd.DataFrame:
    files = _detect_files(outdir)
    sizes_raw = _read_lines(files["sizes"])  # list of sizes for each trial in order
    times_raw = _read_lines(files["times"])  # list of seconds for each trial in order
    corr_raw = _read_lines(files["correctness"])  # list of 0/1 per trial
    corr_norm_raw: Optional[List[str]] = None
    if "correctness_normalized" in files:
        corr_norm_raw = _read_lines(files["correctness_normalized"])  # list of 0/1 per trial

    # Parse and align lengths (truncate to min length if needed)
    n = min(len(sizes_raw), len(times_raw), len(corr_raw))
    if corr_norm_raw is not None:
        n = min(n, len(corr_norm_raw))
    sizes = [v for v in ( _to_int(x) for x in sizes_raw[:n] ) if v is not None]
    times = [v for v in ( _to_float(x) for x in times_raw[:n] ) if v is not None]
    corr = [v for v in ( _to_int(x) for x in corr_raw[:n] ) if v is not None]
    corr_norm: Optional[List[int]] = None
    if corr_norm_raw is not None:
        corr_norm = [v for v in ( _to_int(x) for x in corr_norm_raw[:n] ) if v is not None]

    # Build DataFrame of trials
    df = pd.DataFrame({
        "Size": sizes[:len(corr)],
        "Correct": corr[:len(sizes)],
        "Time": times[:len(sizes)],
    })
    # Group by size and compute means
    grouped = df.groupby("Size").agg(
        **{
            "Average Correctness": ("Correct", "mean"),
            "Average Timing": ("Time", "mean"),
        }
    ).reset_index()

    # Attach normalized correctness if present
    if corr_norm is not None:
        df_norm = pd.DataFrame({
            "Size": sizes[:len(corr_norm)],
            "Correct_Norm": corr_norm[:len(sizes)],
        })
        grouped_norm = df_norm.groupby("Size").agg(
            **{
                "Average Correctness (Normalized)": ("Correct_Norm", "mean"),
            }
        ).reset_index()
        grouped = pd.merge(grouped, grouped_norm, on="Size", how="left")

    # Include placeholder for Inverse Multiplication to keep plotting code compatible
    grouped["Inverse Multiplication"] = pd.NA
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True, help="Path to output_models/<model>/<experiment> directory")
    parser.add_argument("--output-csv", required=True, help="Path to write aggregated CSV")
    args = parser.parse_args()

    outdir = Path(args.outdir).resolve()
    if not outdir.exists() or not outdir.is_dir():
        print(f"OUTDIR does not exist or is not a directory: {outdir}", file=sys.stderr)
        sys.exit(1)

    df = aggregate(outdir)
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()

