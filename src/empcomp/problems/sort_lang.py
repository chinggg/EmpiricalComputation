"""Multilingual sorting: numbers spelled out in non-digit form.

We expose this as one Problem per language. The runner treats each variant
identically. To add a language, drop a code into LANGUAGES — num2words handles
the rest.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

from num2words import num2words

from ..parsing import parse_list
from ..prompts import SORT_SYSTEM, SORT_USER
from .base import Problem


# Paper Figure 2 languages, kept in the same order so the legend matches.
LANGUAGES: tuple[str, ...] = ("ja", "ko", "en", "de", "ru", "ro", "ar", "es", "pl", "fr")
# Trimmed from the paper's 15-point grid for budget; --sizes overrides.
LANG_SIZES = [1, 3, 5, 8, 12, 17, 25, 30]


def _make_problem(lang: str) -> Problem:
    def gen(rng: random.Random, size: int):
        ints = [rng.randint(0, 999) for _ in range(size)]
        words = [num2words(n, lang=lang) for n in ints]
        return words, {"ints": ints, "lang": lang}

    def prompt(words, _ctx):
        return SORT_SYSTEM, SORT_USER.format(items=words)

    def check(parsed, ctx) -> bool:
        return parsed == sorted(ctx["input"])

    return Problem(
        name="sort_lang",
        variant=f"lang={lang}",
        sizes=LANG_SIZES,
        generator=gen,
        prompter=prompt,
        parser=parse_list,
        oracle=lambda items: sorted(items),
        checker=check,
    )


# A Problem-per-language list. The single exported `sort_lang_problem` is the
# default (en) so the registry has one canonical entry; the runner script
# enumerates `sort_lang_problems` to actually run all 10.
sort_lang_problems: list[Problem] = [_make_problem(l) for l in LANGUAGES]
sort_lang_problem = next(p for p in sort_lang_problems if p.variant == "lang=en")


def by_language(lang: str) -> Problem:
    for p in sort_lang_problems:
        if p.variant == f"lang={lang}":
            return p
    raise KeyError(lang)
