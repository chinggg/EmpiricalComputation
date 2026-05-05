"""Unit tests for problem checkers — verify the oracle logic isolated from the LLM.

These would have caught the alphabetical-vs-numerical sort bug in sort_lang
without needing to run a single inference.
"""
from num2words import num2words

from empcomp import problems
from empcomp.problems.sort_lang import by_language


# ---------- sort ----------

def test_sort_checker_accepts_correct():
    p = problems.get("sort")
    assert p.checker([1, 2, 3], {"input": [3, 1, 2]})


def test_sort_checker_rejects_wrong():
    p = problems.get("sort")
    assert not p.checker([1, 3, 2], {"input": [3, 1, 2]})


# ---------- search ----------

def test_sorted_search_checker():
    p = problems.get("sorted_search")
    items = [10, 20, 30, 40]
    assert p.checker(2, {"input": items, "target": 30})
    assert not p.checker(0, {"input": items, "target": 30})


def test_unsorted_search_checker():
    p = problems.get("unsorted_search")
    items = [50, 10, 30, 20, 40]
    assert p.checker(2, {"input": items, "target": 30})


# ---------- ssp ----------

def test_ssp_checker_accepts_valid_subset():
    p = problems.get("ssp")
    assert p.checker([3, 5], {"input": [1, 3, 5, 7], "goal": 8})


def test_ssp_checker_rejects_wrong_sum():
    p = problems.get("ssp")
    assert not p.checker([1, 3], {"input": [1, 3, 5, 7], "goal": 8})


def test_ssp_checker_rejects_nonmember():
    p = problems.get("ssp")
    # 99 is not in input; reject even though it sums correctly.
    assert not p.checker([99], {"input": [1, 3, 5, 7], "goal": 99})


# ---------- substring ----------

def test_substring_checker_accepts_longest_palindrome():
    p = problems.get("substring")
    assert p.checker("aba", {"input": "xabaz"})


def test_substring_checker_rejects_short_palindrome():
    p = problems.get("substring")
    # 'a' is a palindrome substring of 'xabaz', but 'aba' is longer.
    assert not p.checker("a", {"input": "xabaz"})


def test_substring_checker_rejects_non_substring():
    p = problems.get("substring")
    assert not p.checker("xyz", {"input": "abcdef"})


# ---------- sort_lang (the bug we just fixed) ----------

def test_sort_lang_accepts_numerical_sort():
    """The whole point of the language experiment: numbers spelled in words
    should sort by their numeric value, not alphabetically."""
    p = by_language("en")
    ints = [3, 1, 2]
    words = [num2words(i, lang="en") for i in ints]  # ['three', 'one', 'two']
    expected_numerical = [num2words(i, lang="en") for i in sorted(ints)]
    # ['one', 'two', 'three']
    assert p.checker(expected_numerical, {"input": words, "ints": ints, "lang": "en"})


def test_sort_lang_rejects_alphabetical_sort():
    """Alphabetical sort of ['three','one','two'] is ['one','three','two']
    which is NOT numerically sorted — the checker must reject it."""
    p = by_language("en")
    ints = [3, 1, 2]
    words = [num2words(i, lang="en") for i in ints]
    alphabetical = sorted(words)  # ['one', 'three', 'two']
    assert alphabetical != [num2words(i, lang="en") for i in sorted(ints)]
    assert not p.checker(alphabetical, {"input": words, "ints": ints, "lang": "en"})


def test_sort_lang_korean_numerical_sort():
    p = by_language("ko")
    ints = [100, 5, 50]
    words = [num2words(i, lang="ko") for i in ints]
    expected = [num2words(i, lang="ko") for i in sorted(ints)]
    assert p.checker(expected, {"input": words, "ints": ints, "lang": "ko"})
