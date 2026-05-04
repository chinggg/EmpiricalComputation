"""Problem registry. Each problem is a Problem dataclass with everything the
runner needs: input generation, prompt building, response parsing, correctness
oracle. To add a new problem, define a Problem and register() it here.
"""
from __future__ import annotations

from .base import Problem, Trial, TrialOutcome
from .sort import sort_problem
from .search import sorted_search_problem, unsorted_search_problem
from .ssp import ssp_problem
from .substring import substring_problem
from .sort_lang import sort_lang_problem
from .sort_familiar import sort_familiar_problem


_REGISTRY: dict[str, Problem] = {}


def register(p: Problem) -> Problem:
    _REGISTRY[p.name] = p
    return p


def get(name: str) -> Problem:
    return _REGISTRY[name]


def all_problems() -> list[Problem]:
    return list(_REGISTRY.values())


def names() -> list[str]:
    return list(_REGISTRY.keys())


for _p in (
    sort_problem,
    sorted_search_problem,
    unsorted_search_problem,
    ssp_problem,
    substring_problem,
    sort_lang_problem,
    sort_familiar_problem,
):
    register(_p)


__all__ = ["Problem", "Trial", "TrialOutcome", "register", "get", "all_problems", "names"]
