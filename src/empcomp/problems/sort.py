"""Sorting: ascending sort of a random integer list."""
from __future__ import annotations

import random

from ..parsing import parse_list
from ..prompts import SYSTEM_PROMPT, SORT_USER
from .base import Problem


SORT_SIZES = list(range(5, 155, 5))  # [5, 10, 15, ..., 150] — step=5, 30 points


def _generate(rng: random.Random, size: int):
    items = rng.sample(range(0, 1000), size)
    return items, {}


def _prompt(items, _ctx) -> tuple[str, str]:
    return SYSTEM_PROMPT, SORT_USER.format(items=items)


def _check(parsed, ctx) -> bool:
    return parsed == sorted(ctx["input"])


sort_problem = Problem(
    name="sort",
    variant="base",
    sizes=SORT_SIZES,
    generator=_generate,
    prompter=_prompt,
    parser=parse_list,
    oracle=lambda items: sorted(items),
    checker=_check,
)
