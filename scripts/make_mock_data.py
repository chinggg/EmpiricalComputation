"""Synthesize JSONL records that look like real trials, so we can validate the
plot pipeline before any LLM is called.

The fabricated outcomes follow the qualitative trends shown in the paper:
- Correctness decays roughly sigmoidally with size.
- Mean time grows linearly for sort, near-flat for search.
- 'Familiar' beats 'Random' at sizes 30+.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from empcomp import problems
from empcomp.problems.sort_lang import LANG_SIZES, LANGUAGES, sort_lang_problems
from empcomp.problems.sort_familiar import FAMILIAR_SIZES, make_familiar_problem
from empcomp.storage import trial_path, write_record


MOCK_MODEL = "mock"
N = 30
RESULTS = Path(__file__).resolve().parents[1] / "results" / "trials"


def sigmoid_correctness(size: int, half: float, slope: float = 0.15) -> float:
    return 1.0 / (1.0 + math.exp(slope * (size - half)))


def time_for(name: str, size: int) -> float:
    if name == "sort":
        return 0.4 + 0.025 * size
    if name in ("sorted_search", "unsorted_search"):
        return 0.5 + 0.001 * size
    if name == "ssp":
        return 0.6 + 0.02 * size
    if name == "substring":
        return 0.5 + 0.01 * size
    return 0.5


HALFLIVES = {
    "sort": 55.0,
    "sorted_search": 55.0,
    "unsorted_search": 55.0,
    "ssp": 6.0,
    "substring": 4.0,
}


def fabricate(rng: random.Random, problem, n: int, lang_offset: float = 0.0) -> None:
    out = trial_path(RESULTS, MOCK_MODEL, problem.name, problem.variant)
    if out.exists():
        out.unlink()
    name = problem.name
    half = HALFLIVES.get(name, 30.0) + lang_offset
    for size in problem.sizes:
        p_correct = sigmoid_correctness(size, half)
        for i in range(n):
            t_mean = time_for(name, size)
            elapsed = max(0.05, rng.gauss(t_mean, t_mean * 0.15))
            correct = rng.random() < p_correct
            record = {
                "problem": name,
                "variant": problem.variant,
                "model": MOCK_MODEL,
                "size": size,
                "trial": i,
                "seed": 0,
                "input": None,
                "extra": {},
                "raw_response": "[mocked]",
                "parsed": "[mocked]" if correct else None,
                "correct": correct,
                "elapsed_s": elapsed,
                "tokens_in": None,
                "tokens_out": None,
                "error": None,
            }
            write_record(out, record)


# Per-language difficulty offset (higher = harder = curve drops sooner).
LANG_OFFSETS = {
    "en":  4.0,
    "ja": -1.0,
    "es": -3.0,
    "ar": -4.0,
    "ru": -4.0,
    "ro": -4.0,
    "pl": -5.0,
    "fr": -5.0,
    "ko": -7.0,
    "de": -8.0,
}


def main() -> None:
    rng = random.Random(7)

    # Core problems for Figure 1.
    for name in ("sort", "sorted_search", "unsorted_search", "ssp", "substring"):
        fabricate(rng, problems.get(name), N)

    # Multilingual sort for Figure 2 — one Problem per language.
    for p in sort_lang_problems:
        lang = p.variant.split("=")[1]
        fabricate(rng, p, N, lang_offset=LANG_OFFSETS.get(lang, -3.0))

    # Familiar sort for Table 1 + selfgen panel.
    sizes = [10, 20, 30, 40, 50, 100, 150, 200]
    fake_lists = {s: [[0] * s] * N for s in sizes}
    fam = make_familiar_problem(fake_lists)
    # The default registry version has empty pools so trials would fail; build a
    # parallel mock with the right size grid.
    out_fam = trial_path(RESULTS, MOCK_MODEL, fam.name, fam.variant)
    if out_fam.exists():
        out_fam.unlink()
    rng2 = random.Random(11)
    # Familiar should be more correct at mid sizes than random sort.
    for s in sizes:
        # Random baseline correctness vs familiar follows paper Table 1 values.
        p_familiar = {10: 1.00, 20: 1.00, 30: 0.95, 40: 0.67,
                      50: 0.70, 100: 0.40, 150: 0.10, 200: 0.02}.get(s, 0.5)
        for i in range(N):
            elapsed = 0.4 + 0.025 * s + rng2.gauss(0, 0.1)
            correct = rng2.random() < p_familiar
            record = {
                "problem": fam.name,
                "variant": fam.variant,
                "model": MOCK_MODEL,
                "size": s,
                "trial": i,
                "seed": 0,
                "input": None,
                "extra": {},
                "raw_response": "[mocked]",
                "parsed": "[mocked]" if correct else None,
                "correct": correct,
                "elapsed_s": max(0.1, elapsed),
                "tokens_in": None,
                "tokens_out": None,
                "error": None,
            }
            write_record(out_fam, record)
    print(f"Wrote mock trials to {RESULTS}/")


if __name__ == "__main__":
    main()
