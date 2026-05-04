"""Sorting: ascending sort of a random integer list."""
from __future__ import annotations

import random

from ..parsing import parse_list
from ..prompts import SORT_SYSTEM, SORT_USER
from .base import Problem


# Trimmed for the 4B-model 8h budget; sizes 10/20/30/40/50 are kept so the
# same trials feed Table 1's Random column. Override via `--sizes`.
SORT_SIZES = [10, 20, 30, 40, 50, 75, 100, 125, 150]


def _generate(rng: random.Random, size: int):
    items = rng.sample(range(0, 1000), size)
    return items, {}


def _prompt(items, _ctx) -> tuple[str, str]:
    return SORT_SYSTEM, SORT_USER.format(items=items)


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
