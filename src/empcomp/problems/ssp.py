"""Subset-sum: pick elements summing to a goal.

Inputs are sampled per-trial. To guarantee solvability we pick a random subset
first, sum it as the goal, then shuffle the remaining elements with the chosen
subset to form the prompt. The oracle stays simple: any subset that sums to the
goal and uses only multi-set elements from the input is correct.
"""
from __future__ import annotations

import random
from collections import Counter

from ..parsing import parse_list
from ..prompts import SYSTEM_PROMPT, SSP_USER
from .base import Problem


SSP_SIZES = list(range(2, 32)) + list(range(33, 53, 2))  # [2..31 step 1] + [33..51 step 2]


def _generate(rng: random.Random, size: int):
    items = [rng.randint(1, 100) for _ in range(size)]
    k = rng.randint(1, max(1, size - 1))
    subset = rng.sample(items, k)
    goal = sum(subset)
    return items, {"goal": goal}


def _prompt(items, ctx):
    return SYSTEM_PROMPT, SSP_USER.format(items=items, goal=ctx["goal"])


def _check(parsed, ctx) -> bool:
    items = ctx["input"]
    goal = ctx["goal"]
    if not isinstance(parsed, list) or not parsed:
        return False
    # Multi-set membership: every element in the answer must be available in input
    # at least as many times as it is used.
    avail = Counter(items)
    for x in parsed:
        if avail[x] <= 0:
            return False
        avail[x] -= 1
    try:
        return sum(parsed) == goal
    except TypeError:
        return False


ssp_problem = Problem(
    name="ssp",
    variant="base",
    sizes=SSP_SIZES,
    generator=_generate,
    prompter=_prompt,
    parser=parse_list,
    oracle=lambda items: None,
    checker=_check,
)
