"""Generic trial runner. Drives a Problem at a list of sizes, N trials per size,
and writes one JSONL record per trial. Resumable: skips trials already on disk.
"""
from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from .llm import LMStudioClient, OpenAICompatClient
from .problems.base import Problem, Trial
from .storage import done_trial_ids, trial_path, write_record


def run_problem(
    problem: Problem,
    client: LMStudioClient | OpenAICompatClient,
    n_repeats: int,
    out_root: Path,
    sizes: Iterable[int] | None = None,
    seed: int = 0,
    resume: bool = True,
) -> Path:
    """Run a problem and write trial JSONL. Returns the path to the JSONL file."""
    sizes = list(sizes) if sizes is not None else problem.sizes
    out_path = trial_path(out_root, client.model, client.preset.name, problem.name, problem.variant)

    label = f"{problem.name}/{problem.variant}"
    bar = tqdm(total=len(sizes) * n_repeats, desc=label, ncols=80, leave=False)
    for size in sizes:
        done = done_trial_ids(out_path, size) if resume else set()
        bar.update(len(done))
        rng = random.Random(f"{seed}|{problem.name}|{problem.variant}|{size}")
        for i in range(n_repeats):
            trial = problem.make_trial(rng, size, i, seed)
            if i in done:
                continue
            record = _run_one(problem, trial, client)
            write_record(out_path, record)
            bar.update(1)
    bar.close()
    return out_path


def _run_one(problem: Problem, trial: Trial, client: LMStudioClient | OpenAICompatClient) -> dict:
    system, user = problem.prompter(trial.input, trial.extra)
    t0 = time.perf_counter()
    try:
        resp = client.chat(system, user)
        elapsed = resp.elapsed_s
        error = None
    except Exception as e:
        elapsed = time.perf_counter() - t0
        resp = None
        error = repr(e)

    text = resp.text if resp else ""
    parsed = problem.parser(text) if text else None
    correct = problem.evaluate(parsed, trial)
    return {
        "problem": trial.problem,
        "variant": trial.variant,
        "model": client.model,
        "preset": client.preset.name,
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
        "input_tokens": resp.input_tokens if resp else None,
        "total_output_tokens": resp.total_output_tokens if resp else None,
        "reasoning_output_tokens": resp.reasoning_output_tokens if resp else None,
        "tokens_per_second": resp.tokens_per_second if resp else None,
        "time_to_first_token_seconds": resp.time_to_first_token_seconds if resp else None,
        "thinking_text": resp.thinking_text if resp else None,
        "stop_reason": resp.stop_reason if resp else None,
        "error": error,
    }
