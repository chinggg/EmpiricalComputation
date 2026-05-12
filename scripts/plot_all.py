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


def _summary_for(model: str, preset: str, problem: str, variant: str = "base") -> pd.DataFrame:
    p = trial_path(TRIALS, model, preset, problem, variant)
    df = load_trials(p)
    summary = summarize(df)
    if not summary.empty:
        dest = CSV_DIR / f"{model}__{preset}" / f"{problem}__{variant}.csv"
        write_summary_csv(summary, dest)
    return summary


def _trials_for(model: str, preset: str, problem: str, variant: str = "base") -> pd.DataFrame:
    return load_trials(trial_path(TRIALS, model, preset, problem, variant))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mock")
    ap.add_argument("--preset", default="default",
                    help="preset name used when the trials were collected")
    ap.add_argument("--suffix", default="",
                    help="extra suffix appended to figure filenames")
    ap.add_argument("--combined", action="store_true",
                    help="combine all available presets for this model in Figure 1")
    ap.add_argument("--logscale", action="store_true",
                    help="use log scale for y-axis on time-based plots")
    args = ap.parse_args()

    if args.combined:
        # Discover presets from directory names: <model>__<preset>
        model_dirs = list(TRIALS.glob(f"{args.model}__*"))
        presets = sorted([d.name.split("__")[1] for d in model_dirs])
        if not presets:
            print(f"No presets found for model {args.model} in {TRIALS}")
            return
        tag = args.suffix or f"{args.model}__combined"
    else:
        presets = [args.preset]
        tag = args.suffix or f"{args.model}__{args.preset}"

    suffix = f"_{tag}"

    summaries_map = {}
    selfgen_map = {}
    for p in presets:
        summaries_map[p] = {
            name: _summary_for(args.model, p, name)
            for name in ("sort", "sorted_search", "unsorted_search", "ssp", "substring")
        }
        selfgen_map[p] = _summary_for(args.model, p, "sort_familiar", "familiar")

    fig1_path = render_figure1(
        summaries_map,
        selfgen_map,
        FIG_DIR / f"figure1{suffix}.pdf",
        log_scale=args.logscale
    )
    print(f"Figure 1 → {fig1_path}")

    if args.combined:
        print("Skipping Figure 2 and Table 1 for --combined mode.")
        return

    per_lang = {
        lang: _summary_for(args.model, args.preset, "sort_lang", f"lang={lang}")
        for lang in LANGUAGES
    }
    fig2_path = render_figure2(per_lang, FIG_DIR / f"figure2{suffix}.pdf",
                               language_order=list(LANGUAGES))
    print(f"Figure 2 → {fig2_path}")

    random_trials = _trials_for(args.model, args.preset, "sort", "base")
    familiar_trials = _trials_for(args.model, args.preset, "sort_familiar", "familiar")
    tbl = table1_dataframe(random_trials, familiar_trials)
    tbl_path = render_table1(tbl, FIG_DIR / f"table1{suffix}.csv")
    print(f"Table 1 → {tbl_path} (and .md)")
    print(tbl.to_string(index=False))


if __name__ == "__main__":
    main()
