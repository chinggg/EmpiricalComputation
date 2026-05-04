"""Lenient parsers for free-form LLM output."""
from __future__ import annotations

import ast
import re
from typing import Any


_LIST_RE = re.compile(r"\[[\s\S]*?\]")
_INT_RE = re.compile(r"-?\d+")
# Python 3 forbids leading zeros in int literals (e.g. `007`), which crashes
# ast.literal_eval on otherwise-valid lists. Strip them before parsing.
_LEADING_ZEROS_RE = re.compile(r"(?<![\d.])0+(\d)")


def parse_list(text: str) -> list[Any] | None:
    """Extract a Python list from a model response.

    Tries strict literal_eval first, then falls back to the first bracketed
    region. Returns None on failure.
    """
    s = text.strip()
    # Strip code fences.
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    # Sanitize "007"-style integers that ast.literal_eval rejects in Python 3.
    s_clean = _LEADING_ZEROS_RE.sub(r"\1", s)

    for candidate in (s_clean, s):
        try:
            v = ast.literal_eval(candidate)
            if isinstance(v, list):
                return v
        except Exception:
            pass

    m = _LIST_RE.search(s_clean) or _LIST_RE.search(s)
    if m:
        try:
            v = ast.literal_eval(m.group(0))
            if isinstance(v, list):
                return v
        except Exception:
            pass
    # Last resort: pull out every integer-looking token in the bracketed region.
    bracket = _LIST_RE.search(s_clean)
    if bracket:
        nums = [int(t) for t in _INT_RE.findall(bracket.group(0))]
        if nums:
            return nums
    # Truncated list (open bracket, no close): grab everything after the first '['.
    if "[" in s_clean and "]" not in s_clean:
        tail = s_clean[s_clean.index("[") + 1 :]
        nums = [int(t) for t in _INT_RE.findall(tail)]
        if nums:
            # Drop the last item — likely cut off mid-token.
            return nums[:-1] if len(nums) > 1 else nums
    return None


def parse_int(text: str) -> int | None:
    s = text.strip()
    try:
        return int(s)
    except Exception:
        pass
    m = _INT_RE.search(s)
    return int(m.group(0)) if m else None


def parse_substring(text: str) -> str:
    """Substring tasks return a raw string; trim quotes/brackets if present."""
    s = text.strip()
    while len(s) >= 2 and s[0] in "[(\"'" and s[-1] in "])\"'":
        s = s[1:-1].strip()
    return s
