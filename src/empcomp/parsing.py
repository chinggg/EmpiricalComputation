"""Lenient parsers for free-form LLM output."""
from __future__ import annotations

import ast
import re
from typing import Any


_LIST_RE = re.compile(r"\[[\s\S]*?\]")
_INT_RE = re.compile(r"-?\d+")


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
    try:
        v = ast.literal_eval(s)
        if isinstance(v, list):
            return v
    except Exception:
        pass
    m = _LIST_RE.search(s)
    if m:
        try:
            v = ast.literal_eval(m.group(0))
            if isinstance(v, list):
                return v
        except Exception:
            return None
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
