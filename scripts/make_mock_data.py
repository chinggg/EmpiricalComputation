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
MOCK_PRESET = "default"
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


def fabricate(rng: random.Random, problem, n: int, preset: str, lang_offset: float = 0.0) -> None:
    out = trial_path(RESULTS, MOCK_MODEL, preset, problem.name, problem.variant)
    if out.exists():
        out.unlink()
    name = problem.name
    # Variation between presets: 'thinking' is slightly better, 'deterministic' is baseline.
    preset_bonus = {"thinking": 5.0, "default": 0.0, "deterministic": -5.0}.get(preset, 0.0)
    half = HALFLIVES.get(name, 30.0) + lang_offset + preset_bonus
    
    for size in problem.sizes:
        p_correct = sigmoid_correctness(size, half)
        for i in range(n):
            t_mean = time_for(name, size)
            if preset == "thinking":
                t_mean *= 1.5 # thinking takes longer
            elapsed = max(0.05, rng.gauss(t_mean, t_mean * 0.15))
            correct = rng.random() < p_correct
            record = {
                "problem": name,
                "variant": problem.variant,
                "model": MOCK_MODEL,
                "preset": preset,
                "size": size,
                "trial": i,
                "seed": 0,
                "input": None,
                "extra": {},
                "raw_response": "[mocked]",
                "parsed": "[mocked]" if correct else None,
                "correct": correct,
                "elapsed_s": elapsed,
                "input_tokens": None,
                "total_output_tokens": None,
                "reasoning_output_tokens": 100 if preset == "thinking" else 0,
                "tokens_per_second": None,
                "time_to_first_token_seconds": None,
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
    presets = ["default", "thinking", "deterministic"]

    for preset in presets:
        print(f"Generating mock data for preset: {preset}")
        for name in ("sort", "sorted_search", "unsorted_search", "ssp", "substring"):
            fabricate(rng, problems.get(name), N, preset)

        for p in sort_lang_problems:
            lang = p.variant.split("=")[1]
            fabricate(rng, p, N, preset, lang_offset=LANG_OFFSETS.get(lang, -3.0))

        sizes = [10, 20, 30, 40, 50, 100, 150, 200]
        fake_lists = {s: [[0] * s] * N for s in sizes}
        fam = make_familiar_problem(fake_lists)
        out_fam = trial_path(RESULTS, MOCK_MODEL, preset, fam.name, fam.variant)
        if out_fam.exists():
            out_fam.unlink()
        rng2 = random.Random(11)
        # Variation for familiar sort
        bonus = {"thinking": 10, "default": 0, "deterministic": -10}.get(preset, 0)
        for s in sizes:
            base_p = {10: 1.00, 20: 1.00, 30: 0.95, 40: 0.67,
                          50: 0.70, 100: 0.40, 150: 0.10, 200: 0.02}.get(s, 0.5)
            # crude way to shift probability
            p_familiar = max(0.0, min(1.0, base_p + bonus / 100.0))
            
            for i in range(N):
                t_mean = 0.4 + 0.025 * s
                if preset == "thinking":
                    t_mean *= 1.5
                elapsed = t_mean + rng2.gauss(0, 0.1)
                correct = rng2.random() < p_familiar
                record = {
                    "problem": fam.name,
                    "variant": fam.variant,
                    "model": MOCK_MODEL,
                    "preset": preset,
                    "size": s,
                    "trial": i,
                    "seed": 0,
                    "input": None,
                    "extra": {},
                    "raw_response": "[mocked]",
                    "parsed": "[mocked]" if correct else None,
                    "correct": correct,
                    "elapsed_s": max(0.1, elapsed),
                    "input_tokens": None,
                    "total_output_tokens": None,
                    "reasoning_output_tokens": 100 if preset == "thinking" else 0,
                    "tokens_per_second": None,
                    "time_to_first_token_seconds": None,
                    "error": None,
                }
                write_record(out_fam, record)
    print(f"Wrote mock trials to {RESULTS}/")


if __name__ == "__main__":
    main()
