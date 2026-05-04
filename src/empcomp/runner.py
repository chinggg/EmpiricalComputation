"""Generic trial runner. Drives a Problem at a list of sizes, N trials per size,
and writes one JSONL record per trial. Resumable: skips trials already on disk.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from .llm import LLMClient
from .problems.base import Problem, Trial
from .storage import count_done, trial_path, write_record


def run_problem(
    problem: Problem,
    client: LLMClient,
    n_repeats: int,
    out_root: Path,
    sizes: Iterable[int] | None = None,
    seed: int = 0,
    resume: bool = True,
) -> Path:
    """Run a problem and write trial JSONL. Returns the path to the JSONL file."""
    sizes = list(sizes) if sizes is not None else problem.sizes
    out_path = trial_path(out_root, client.model, problem.name, problem.variant)

    label = f"{problem.name}/{problem.variant}"
    bar = tqdm(total=len(sizes) * n_repeats, desc=label, ncols=80, leave=False)
    for size in sizes:
        already = count_done(out_path, size) if resume else 0
        # Advance the per-(problem,size) RNG deterministically across resumes.
        rng = random.Random(f"{seed}|{problem.name}|{problem.variant}|{size}")
        # Skip the trials already done by re-drawing their inputs.
        for i in range(already):
            problem.make_trial(rng, size, i, seed)
        bar.update(already)

        for i in range(already, n_repeats):
            trial = problem.make_trial(rng, size, i, seed)
            record = _run_one(problem, trial, client)
            write_record(out_path, record)
            bar.update(1)
    bar.close()
    return out_path


def _run_one(problem: Problem, trial: Trial, client: LLMClient) -> dict:
    system, user = problem.prompter(trial.input, trial.extra)
    try:
        resp = client.chat(system, user)
        text = resp.text
        elapsed = resp.elapsed_s
        tokens_in = resp.tokens_in
        tokens_out = resp.tokens_out
        error = None
    except Exception as e:
        text = ""
        elapsed = 0.0
        tokens_in = tokens_out = None
        error = repr(e)

    parsed = problem.parser(text) if text else None
    correct = problem.evaluate(parsed, trial)
    return {
        "problem": trial.problem,
        "variant": trial.variant,
        "model": client.model,
        "size": trial.size,
        "trial": trial.trial,
        "seed": trial.seed,
        "input": trial.input,
        "extra": trial.extra,
        "system": system,
        "user": user,
        "raw_response": text,
        "parsed": parsed,
        "correct": correct,
        "elapsed_s": elapsed,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "error": error,
    }
