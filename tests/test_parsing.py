"""Pure unit tests for the response parsers.

These exist specifically to lock in the bug-fixes uncovered by the audit:
nested-list unwrap and leading-zero tolerance. If they regress, every
sort/SSP/sort_lang result is silently mis-labeled.
"""
from empcomp.parsing import parse_int, parse_list, parse_substring


# ---------- parse_list ----------

def test_parse_list_plain():
    assert parse_list("[1, 2, 3]") == [1, 2, 3]


def test_parse_list_text_prefix():
    # The model often prepends "Sure: " or "Answer: ".
    assert parse_list("Answer: [1, 2, 3]") == [1, 2, 3]


def test_parse_list_code_fence():
    assert parse_list("```json\n[1, 2, 3]\n```") == [1, 2, 3]


def test_parse_list_unwraps_nested_singleton():
    # Bug found in SSP audit: gemma returns [[8]] when the answer is [8].
    # Not unwrapping caused 50/87 wrong SSP trials to be false negatives.
    assert parse_list("[[8]]") == [8]
    assert parse_list("[[1, 2, 3]]") == [1, 2, 3]


def test_parse_list_does_not_unwrap_real_nested():
    # A list of two lists is genuinely nested — leave alone.
    assert parse_list("[[1, 2], [3, 4]]") == [[1, 2], [3, 4]]


def test_parse_list_octal_safe():
    # Python 3 forbids leading zeros in int literals, so naive ast.literal_eval
    # crashes on "[007, 12]". Strip the leading zeros first.
    assert parse_list("[007, 12, 003]") == [7, 12, 3]


def test_parse_list_truncated():
    # Truncation at max_tokens is common. Recover the prefix, drop the
    # last (probably half-cut) token.
    out = parse_list("[10, 20, 30, 4")
    assert out == [10, 20, 30]


def test_parse_list_unparseable():
    assert parse_list("nope") is None
    assert parse_list("") is None


# ---------- parse_int ----------

def test_parse_int_clean():
    assert parse_int("42") == 42


def test_parse_int_text_wrapped():
    assert parse_int("index: 17") == 17


def test_parse_int_negative():
    assert parse_int("-1") == -1


def test_parse_int_unparseable():
    assert parse_int("") is None
    assert parse_int("hello") is None


# ---------- parse_substring ----------

def test_parse_substring_strips_quotes():
    assert parse_substring('"abc"') == "abc"
    assert parse_substring("'abc'") == "abc"


def test_parse_substring_strips_brackets():
    assert parse_substring("[abc]") == "abc"
    assert parse_substring("(abc)") == "abc"


def test_parse_substring_plain():
    assert parse_substring("aba") == "aba"
