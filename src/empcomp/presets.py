"""Named experiment presets for LLM configuration and problem size subsets."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    name: str
    temperature: float | None  # None = use model default; 0.0 = deterministic
    thinking: bool             # True = reasoning=on; False = reasoning=off


PRESETS: dict[str, Preset] = {
    # Model default temperature, reasoning off — fast direct answers.
    "default":       Preset("default",       temperature=None, thinking=False),
    # Model default temperature, reasoning on — extended thinking trace.
    "thinking":      Preset("thinking",      temperature=None, thinking=True),
    # Greedy — fully reproducible, reasoning off.
    "deterministic": Preset("deterministic", temperature=0.0,  thinking=False),
}

# Smaller size subsets for quick verification; None → use each problem's defaults.
SIZE_PRESETS: dict[str, dict[str, list[int]] | None] = {
    "quick": {
        "sort":            [10, 50, 100, 150],
        "sorted_search":   [10, 50, 100, 150],
        "unsorted_search": [10, 50, 100, 150],
        "ssp":             [2, 10, 20, 30],
        "substring":       [2, 20, 50, 89],
        "sort_lang":       [1, 5, 17],
        "sort_familiar":   [10, 50],
    },
    "full": None,
}


def get_preset(name: str) -> Preset:
    if name not in PRESETS:
        raise KeyError(f"Unknown preset {name!r}. Choose from: {list(PRESETS)}")
    return PRESETS[name]


def get_sizes(sizes_preset: str, problem_name: str, default: list[int]) -> list[int]:
    """Return the size list for this preset+problem, falling back to problem defaults."""
    mapping = SIZE_PRESETS.get(sizes_preset)
    if mapping is None:
        return default
    return mapping.get(problem_name, default)
