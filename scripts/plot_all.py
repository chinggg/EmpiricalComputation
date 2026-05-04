"""Render Figure 1, Figure 2, and Table 1 from JSONL trial records."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from empcomp.aggregate import load_trials, summarize, write_summary_csv
from empcomp.plotting import (
    render_figure1,
    render_figure2,
    render_table1,
    table1_dataframe,
)
from empcomp.problems.sort_lang import LANGUAGES
from empcomp.storage import trial_path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRIALS = REPO_ROOT / "results" / "trials"
CSV_DIR = REPO_ROOT / "results" / "csv"
FIG_DIR = REPO_ROOT / "results" / "figures"


def _summary_for(model: str, problem: str, variant: str = "base") -> pd.DataFrame:
    p = trial_path(TRIALS, model, problem, variant)
    df = load_trials(p)
    summary = summarize(df)
    if not summary.empty:
        write_summary_csv(summary, CSV_DIR / f"{model}__{problem}__{variant}.csv")
    return summary


def _trials_for(model: str, problem: str, variant: str = "base") -> pd.DataFrame:
    return load_trials(trial_path(TRIALS, model, problem, variant))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mock")
    ap.add_argument("--suffix", default="", help="suffix appended to figure filenames")
    args = ap.parse_args()

    suffix = f"_{args.suffix}" if args.suffix else f"_{args.model}"

    summaries = {
        name: _summary_for(args.model, name)
        for name in ("sort", "sorted_search", "unsorted_search", "ssp", "substring")
    }

    # Selfgen panel: bucket by *actual* returned size, since gemma rarely
    # produces exactly N (paper's footnote: "Number of instances actually
    # returned with that size").
    fam_trials = load_trials(trial_path(TRIALS, args.model, "sort_familiar", "familiar"))
    fam = summarize(fam_trials, size_col="actual_size")
    fig1_path = render_figure1(summaries, fam, FIG_DIR / f"figure1{suffix}.pdf")
    print(f"Figure 1 → {fig1_path}")

    per_lang = {
        lang: _summary_for(args.model, "sort_lang", f"lang={lang}") for lang in LANGUAGES
    }
    fig2_path = render_figure2(per_lang, FIG_DIR / f"figure2{suffix}.pdf",
                               language_order=list(LANGUAGES))
    print(f"Figure 2 → {fig2_path}")

    random_trials = _trials_for(args.model, "sort", "base")
    familiar_trials = _trials_for(args.model, "sort_familiar", "familiar")
    tbl = table1_dataframe(random_trials, familiar_trials)
    tbl_path = render_table1(tbl, FIG_DIR / f"table1{suffix}.csv")
    print(f"Table 1 → {tbl_path} (and .md)")
    print(tbl.to_string(index=False))


if __name__ == "__main__":
    main()
