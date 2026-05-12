"""Unit tests for the presets system. No LLM required."""
from __future__ import annotations

import pytest

from empcomp.presets import PRESETS, SIZE_PRESETS, Preset, get_preset, get_sizes
from empcomp.problems.sort import SORT_SIZES
from empcomp.problems.search import SEARCH_SIZES
from empcomp.problems.ssp import SSP_SIZES
from empcomp.problems.substring import SUBSTRING_SIZES
from empcomp.problems.sort_lang import LANG_SIZES
from empcomp.problems.sort_familiar import FAMILIAR_SIZES


# ---------- Preset lookup ----------

def test_get_preset_known():
    p = get_preset("default")
    assert isinstance(p, Preset)
    assert p.name == "default"


def test_get_preset_unknown():
    with pytest.raises(KeyError, match="Unknown preset"):
        get_preset("does_not_exist")


def test_all_presets_present():
    for name in ("default", "thinking", "deterministic"):
        assert name in PRESETS


# ---------- Preset values ----------

def test_deterministic_low_temp():
    p = get_preset("deterministic")
    assert p.temperature == 0.0
    assert p.thinking is False


def test_default_no_thinking():
    p = get_preset("default")
    assert p.temperature is None
    assert p.thinking is False


def test_thinking_preset_omits_temp_and_thinking_on():
    p = get_preset("thinking")
    assert p.temperature is None
    assert p.thinking is True


# ---------- Size presets ----------

def test_get_sizes_full_returns_defaults():
    assert get_sizes("full", "sort", SORT_SIZES) == SORT_SIZES
    assert get_sizes("full", "ssp", SSP_SIZES) == SSP_SIZES


def test_get_sizes_quick_is_subset_of_full():
    cases = [
        ("sort",            SORT_SIZES),
        ("sorted_search",   SEARCH_SIZES),
        ("unsorted_search", SEARCH_SIZES),
        ("ssp",             SSP_SIZES),
        ("substring",       SUBSTRING_SIZES),
        ("sort_lang",       LANG_SIZES),
        ("sort_familiar",   FAMILIAR_SIZES),
    ]
    for name, full in cases:
        quick = get_sizes("quick", name, full)
        assert set(quick).issubset(set(full)), (
            f"quick sizes for {name!r} contain values not in full: "
            f"{set(quick) - set(full)}"
        )


def test_get_sizes_quick_is_smaller_than_full():
    for name, full in [
        ("sort", SORT_SIZES),
        ("ssp", SSP_SIZES),
        ("substring", SUBSTRING_SIZES),
    ]:
        quick = get_sizes("quick", name, full)
        assert len(quick) < len(full), f"{name}: quick ({len(quick)}) should be < full ({len(full)})"


def test_get_sizes_unknown_preset_falls_back():
    assert get_sizes("nonexistent", "sort", SORT_SIZES) == SORT_SIZES


def test_get_sizes_unknown_problem_falls_back():
    assert get_sizes("quick", "new_problem", [1, 2, 3]) == [1, 2, 3]
