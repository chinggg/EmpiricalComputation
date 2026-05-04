"""Search: return the index of a target known to be in the list."""
from __future__ import annotations

import random

from ..parsing import parse_int
from ..prompts import SEARCH_SYSTEM, SORTED_SEARCH_USER, UNSORTED_SEARCH_USER
from .base import Problem


SEARCH_SIZES = [10, 25, 50, 75, 100, 125, 150]


def _generate_unsorted(rng: random.Random, size: int):
    items = rng.sample(range(0, 1000), size)
    target = rng.choice(items)
    return items, {"target": target}


def _generate_sorted(rng: random.Random, size: int):
    items, extra = _generate_unsorted(rng, size)
    items.sort()
    return items, extra


def _prompt_sorted(items, ctx):
    return SEARCH_SYSTEM, SORTED_SEARCH_USER.format(items=items, target=ctx["target"])


def _prompt_unsorted(items, ctx):
    return SEARCH_SYSTEM, UNSORTED_SEARCH_USER.format(items=items, target=ctx["target"])


def _check(parsed, ctx) -> bool:
    items = ctx["input"]
    target = ctx["target"]
    return parsed == items.index(target)


sorted_search_problem = Problem(
    name="sorted_search",
    variant="base",
    sizes=SEARCH_SIZES,
    generator=_generate_sorted,
    prompter=_prompt_sorted,
    parser=parse_int,
    oracle=lambda items: None,  # depends on target; not used by runner
    checker=_check,
)

unsorted_search_problem = Problem(
    name="unsorted_search",
    variant="base",
    sizes=SEARCH_SIZES,
    generator=_generate_unsorted,
    prompter=_prompt_unsorted,
    parser=parse_int,
    oracle=lambda items: None,
    checker=_check,
)
