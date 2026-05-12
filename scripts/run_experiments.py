"""Drive the full experiment suite.

Usage examples:
  uv run python scripts/run_experiments.py --problems sort --preset default --n 30
  uv run python scripts/run_experiments.py --all --preset thinking --sizes-preset quick --n 10
  uv run python scripts/run_experiments.py --all --n 30
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from empcomp.llm import make_client
from empcomp.presets import PRESETS, get_preset, get_sizes
from empcomp import problems
from empcomp.problems.sort_lang import sort_lang_problems
from empcomp.problems.sort_familiar import (
    FAMILIAR_SIZES,
    generate_request,
    make_familiar_problem,
)
from empcomp.parsing import parse_list
from empcomp.runner import run_problem
from empcomp.storage import trial_path, write_record


REPO_ROOT = Path(__file__).resolve().parents[1]
TRIALS = REPO_ROOT / "results" / "trials"

CORE = ["sort", "sorted_search", "unsorted_search", "ssp", "substring"]


def _generate_familiar_lists(
    client,
    sizes: list[int],
    per_size: int,
    min_returned: int = 2,
    max_attempts_per_list: int = 3,
):
    """Ask the LLM to generate one list per slot. Caches to disk.

    Accepts lists with len >= min_returned (model may undershoot the requested
    size). Only retries on API error, unparseable response, or degenerate output.
    """
    cache = trial_path(TRIALS, client.model, client.preset.name, "sort_familiar", "_genlists")
    cached_by_size: dict[int, list[list[int]]] = {s: [] for s in sizes}
    if cache.exists():
        from empcomp.storage import read_records
        for r in read_records(cache):
            s = r.get("size")
            if s in cached_by_size:
                cached_by_size[s].append(r["parsed"])
    print(f"familiar/genlists cached: {{{', '.join(f'{s}:{len(v)}' for s, v in cached_by_size.items())}}}")

    for s in sizes:
        while len(cached_by_size[s]) < per_size:
            attempts = 0
            parsed: list[int] | None = None
            resp = None
            while attempts < max_attempts_per_list:
                attempts += 1
                system, user = generate_request(s)
                try:
                    resp = client.chat(system, user)
                except Exception as e:
                    print(f"  ! generate API failure size={s}: {e}")
                    continue
                p = parse_list(resp.text) or []
                p = [int(x) for x in p if isinstance(x, (int, float))]
                if len(p) >= min_returned:
                    parsed = p
                    break
                print(f"  ! unparseable / too-short at size={s} (attempt {attempts}, got {len(p)})")

            if parsed is None:
                print(f"  ! giving up on size={s} after {max_attempts_per_list} attempts")
                cached_by_size[s].append([])
                break

            if len(parsed) != s:
                print(f"  ~ size={s}: model returned {len(parsed)} numbers")
            write_record(
                cache,
                {
                    "problem": "sort_familiar",
                    "variant": "_genlists",
                    "model": client.model,
                    "preset": client.preset.name,
                    "size": s,
                    "trial": len(cached_by_size[s]),
                    "seed": 0,
                    "input": None,
                    "raw_response": resp.text if resp else "",
                    "parsed": parsed,
                    "actual_size": len(parsed),
                    "correct": True,
                    "elapsed_s": resp.elapsed_s if resp else 0.0,
                },
            )
            cached_by_size[s].append(parsed)
    return {s: [lst for lst in lists if lst] for s, lists in cached_by_size.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30, help="repeats per size")
    ap.add_argument(
        "--preset",
        choices=list(PRESETS),
        default="default",
        help="experiment preset: default | thinking | deterministic",
    )
    ap.add_argument(
        "--sizes-preset",
        choices=["quick", "full"],
        default="full",
        help="quick = small subset for fast runs; full = all problem sizes",
    )
    ap.add_argument(
        "--problems", nargs="+", default=None,
        help="subset of: " + ", ".join(CORE + ["sort_lang", "sort_familiar"]),
    )
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sizes", nargs="+", type=int, default=None,
                    help="explicit size override (ignores --sizes-preset for selected problems)")
    ap.add_argument("--languages", nargs="+", default=None,
                    help="subset of language codes (sort_lang only)")
    ap.add_argument("--familiar-sizes", nargs="+", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    selected = set(CORE + ["sort_lang", "sort_familiar"]) if args.all else set(args.problems or [])
    if not selected:
        ap.error("specify --all or --problems")

    preset = get_preset(args.preset)
    client = make_client(preset)
    print(f"# model={client.model}  preset={preset.name}  "
          f"temperature={preset.temperature}  thinking={preset.thinking}")
    print(f"# base_url={client.base_url}  n={args.n}  sizes={args.sizes_preset}")
    overall_t0 = time.perf_counter()

    for name in CORE:
        if name not in selected:
            continue
        problem = problems.get(name)
        if args.sizes:
            sizes = args.sizes
        else:
            sizes = get_sizes(args.sizes_preset, name, problem.sizes)
        print(f"\n=== {name} sizes={sizes} ===")
        run_problem(problem, client, args.n, TRIALS, sizes=sizes, seed=args.seed)

    if "sort_lang" in selected:
        langs = args.languages or [p.variant.split("=")[1] for p in sort_lang_problems]
        print(f"\n=== sort_lang langs={langs} ===")
        for p in sort_lang_problems:
            lang = p.variant.split("=")[1]
            if lang not in langs:
                continue
            print(f"--- {p.variant} ---")
            lang_sizes = get_sizes(args.sizes_preset, "sort_lang", p.sizes)
            run_problem(p, client, args.n, TRIALS, sizes=lang_sizes, seed=args.seed)

    if "sort_familiar" in selected:
        if args.familiar_sizes:
            sizes = args.familiar_sizes
        else:
            sizes = get_sizes(args.sizes_preset, "sort_familiar", FAMILIAR_SIZES)
        print(f"\n=== sort_familiar (gen) sizes={sizes} ===")
        generated = _generate_familiar_lists(client, sizes, per_size=args.n)
        generated = {s: lists for s, lists in generated.items() if lists}
        if not generated:
            print("  no usable generated lists — skipping sort step")
        else:
            problem = make_familiar_problem(generated)
            sort_sizes = list(generated.keys())
            print(f"=== sort_familiar (sort) sizes={sort_sizes} ===")
            run_problem(problem, client, args.n, TRIALS, sizes=sort_sizes, seed=args.seed)

    print(f"\nDone in {time.perf_counter() - overall_t0:.0f}s")


if __name__ == "__main__":
    main()
