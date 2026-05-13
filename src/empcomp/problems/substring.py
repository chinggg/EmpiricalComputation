"""Longest palindromic substring on a random lowercase string."""
from __future__ import annotations

import random
import string

from ..parsing import parse_substring
from ..prompts import SYSTEM_PROMPT, SUBSTRING_USER
from .base import Problem


SUBSTRING_SIZES = list(range(2, 92, 3))  # [2, 5, ..., 89] — step=3, 30 points


def _generate(rng: random.Random, size: int):
    text = "".join(rng.choices(string.ascii_lowercase, k=size))
    return text, {}


def _prompt(text, _ctx):
    return SYSTEM_PROMPT, SUBSTRING_USER.format(text=text)


def _longest_palindrome_len(s: str) -> int:
    if not s:
        return 0
    best = 1
    for c in range(len(s)):
        for lo, hi in ((c, c), (c, c + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                best = max(best, hi - lo + 1)
                lo -= 1
                hi += 1
    return best


def _is_palindrome(s: str) -> bool:
    return s == s[::-1]


def _check(parsed, ctx) -> bool:
    text = ctx["input"]
    if not isinstance(parsed, str):
        return False
    return (
        parsed in text
        and _is_palindrome(parsed)
        and len(parsed) == _longest_palindrome_len(text)
    )


substring_problem = Problem(
    name="substring",
    variant="base",
    sizes=SUBSTRING_SIZES,
    generator=_generate,
    prompter=_prompt,
    parser=parse_substring,
    oracle=lambda text: None,
    checker=_check,
)
