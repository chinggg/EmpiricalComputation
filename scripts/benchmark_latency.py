"""Probe the configured LLM at a few sizes to budget the overnight run.

Reports per-problem mean/median time at small/medium/large sizes. Use the output
to choose final size grids for `run_experiments.py`.
"""
from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

from empcomp.llm import LLMClient
from empcomp import problems
from empcomp.problems.sort_lang import sort_lang_problems
import random


PROBES: list[tuple[str, list[int]]] = [
    ("sort",            [10, 50, 100, 150]),
    ("sorted_search",   [10, 50, 150]),
    ("unsorted_search", [10, 50, 150]),
    ("ssp",             [5, 10, 20]),
    ("substring",       [5, 10, 20]),
]
LANG_PROBES = [(lang, [5, 15, 30]) for lang in ("en", "de", "ko")]


def probe(client: LLMClient, problem, size: int, n: int) -> list[float]:
    rng = random.Random(f"42|{problem.name}|{problem.variant}|{size}")
    times = []
    for i in range(n):
        trial = problem.make_trial(rng, size, i, 42)
        system, user = problem.prompter(trial.input, trial.extra)
        t0 = time.perf_counter()
        try:
            client.chat(system, user)
        except Exception as e:
            print(f"  ! error at {problem.name}/{size}: {e}")
            return times
        times.append(time.perf_counter() - t0)
    return times


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3, help="probes per (problem, size)")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parents[1]
                    / "results" / "latency_probe.txt")
    args = ap.parse_args()

    client = LLMClient()
    print(f"model={client.model} base_url={client.base_url}")

    lines = [f"# benchmark — model={client.model}, base_url={client.base_url}", ""]
    total_t = 0.0
    total_calls = 0
    for name, sizes in PROBES:
        problem = problems.get(name)
        for s in sizes:
            ts = probe(client, problem, s, args.n)
            if not ts:
                continue
            mean = statistics.fmean(ts)
            med = statistics.median(ts)
            lines.append(
                f"{name:18s} size={s:>4d}  n={len(ts)}  mean={mean:6.2f}s "
                f"median={med:6.2f}s  total={sum(ts):.1f}s"
            )
            total_t += sum(ts)
            total_calls += len(ts)

    for lang, sizes in LANG_PROBES:
        problem = next(p for p in sort_lang_problems if p.variant == f"lang={lang}")
        for s in sizes:
            ts = probe(client, problem, s, args.n)
            if not ts:
                continue
            mean = statistics.fmean(ts)
            med = statistics.median(ts)
            lines.append(
                f"sort_lang/{lang:2s}        size={s:>4d}  n={len(ts)}  mean={mean:6.2f}s "
                f"median={med:6.2f}s  total={sum(ts):.1f}s"
            )
            total_t += sum(ts)
            total_calls += len(ts)

    lines.append("")
    lines.append(f"# total calls={total_calls}  total elapsed={total_t:.1f}s")
    body = "\n".join(lines) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body, encoding="utf-8")
    print(body)
    print(f"saved → {args.out}")


if __name__ == "__main__":
    main()
