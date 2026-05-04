"""Self-generated ('familiar') sort.

The paper's familiarity experiment first asks the LLM to generate a random list
of N numbers, then asks it to sort that list. Implemented in two stages so the
runner can checkpoint between them.

Stage 1 (`generate_familiar_lists`): produce M lists per size by prompting the
model. Returns a dict {size: [list, list, ...]}.
Stage 2: each generated list becomes the input of one sort trial.
"""
from __future__ import annotations

import random
from typing import Any, Sequence

from ..parsing import parse_list
from ..prompts import (
    GENERATE_NUMS_SYSTEM,
    GENERATE_NUMS_USER,
    SORT_SYSTEM,
    SORT_USER,
)
from .base import Problem


# Sizes shown in Table 1 (10..50) plus a few larger sizes like the paper's
# selfgen panel (which extends to ~200).
# Table 1 sizes (10..50) plus larger sizes for the selfgen panel.
FAMILIAR_SIZES = [10, 20, 30, 40, 50, 100, 150]


def make_familiar_problem(generated: dict[int, Sequence[Sequence[int]]]) -> Problem:
    """Build a Problem whose generator pulls from already-generated lists."""

    counters: dict[int, int] = {s: 0 for s in generated}

    def gen(_rng: random.Random, size: int):
        pool = generated.get(size, [])
        if not pool:
            raise RuntimeError(f"no generated lists for size {size}")
        idx = counters[size] % len(pool)
        counters[size] += 1
        items = list(pool[idx])
        return items, {}

    def prompt(items, _ctx):
        return SORT_SYSTEM, SORT_USER.format(items=items)

    def check(parsed, ctx) -> bool:
        return parsed == sorted(ctx["input"])

    sizes = sorted(generated.keys())
    return Problem(
        name="sort_familiar",
        variant="familiar",
        sizes=sizes,
        generator=gen,
        prompter=prompt,
        parser=parse_list,
        oracle=lambda items: sorted(items),
        checker=check,
    )


def generate_request(size: int) -> tuple[str, str]:
    """The system+user prompt asking the LLM to produce a random list of `size`."""
    return GENERATE_NUMS_SYSTEM.format(n=size), GENERATE_NUMS_USER.format(
        n=size, max_value=999
    )


# Placeholder Problem so the registry has a stable entry; the real one is built
# at runtime from generated lists.
sort_familiar_problem = make_familiar_problem({s: [] for s in FAMILIAR_SIZES})
