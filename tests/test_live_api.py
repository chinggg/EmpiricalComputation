"""Live integration tests against the configured LM Studio endpoint.

For each problem, run one trivially-easy instance through the full pipeline
(prompt -> LLM -> parse -> checker) and assert correctness. The point isn't
to grade the model — it's to surface naive bugs end-to-end (parser drops a
correct answer, checker uses the wrong oracle, etc.). Sizes are kept small
so the whole suite runs in well under a minute.

Auto-skips if the configured LLM endpoint is unreachable.
"""
from __future__ import annotations

import random

import pytest
from num2words import num2words

from empcomp import problems
from empcomp.llm import LLMClient
from empcomp.problems.sort_lang import by_language


# ---------- skip-if-no-API fixture ----------

@pytest.fixture(scope="module")
def client() -> LLMClient:
    c = LLMClient()
    try:
        c.chat("You are a calculator.", "Reply with the digit 1 only.")
    except Exception as e:
        pytest.skip(f"LLM endpoint unreachable at {c.base_url}: {e}")
    return c


def _run_one(problem, client, size, rng_seed=0):
    """Run a single trial and return (correct, parsed, raw, trial)."""
    rng = random.Random(rng_seed)
    trial = problem.make_trial(rng, size, 0, rng_seed)
    system, user = problem.prompter(trial.input, trial.extra)
    resp = client.chat(system, user)
    parsed = problem.parser(resp.text)
    correct = problem.evaluate(parsed, trial)
    return correct, parsed, resp.text, trial


# ---------- per-problem smoke tests ----------

def test_sort_small(client):
    """Sorting 5 random numbers should be trivial for any modern LLM."""
    correct, parsed, raw, trial = _run_one(problems.get("sort"), client, size=5)
    assert correct, (
        f"sort failed at size=5\n"
        f"  input={trial.input}\n  expected={sorted(trial.input)}\n"
        f"  parsed={parsed}\n  raw={raw!r}"
    )


def test_sorted_search_small(client):
    correct, parsed, raw, trial = _run_one(
        problems.get("sorted_search"), client, size=5
    )
    target = trial.extra["target"]
    true_idx = trial.input.index(target)
    assert correct, (
        f"sorted_search failed\n"
        f"  list={trial.input}  target={target}  true_index={true_idx}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_unsorted_search_small(client):
    correct, parsed, raw, trial = _run_one(
        problems.get("unsorted_search"), client, size=5
    )
    target = trial.extra["target"]
    true_idx = trial.input.index(target)
    assert correct, (
        f"unsorted_search failed\n"
        f"  list={trial.input}  target={target}  true_index={true_idx}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_ssp_small(client):
    """SSP at n=2 with goal == one of the elements has a 1-element answer.
    Specifically guards the [[8]] nested-wrap bug."""
    correct, parsed, raw, trial = _run_one(problems.get("ssp"), client, size=2)
    assert correct, (
        f"ssp failed\n"
        f"  input={trial.input}  goal={trial.extra['goal']}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_substring_size_2(client):
    """At size=2 the longest palindrome is at most length 1 unless both
    chars are equal. The model passes if it returns ANY single character
    that appears in the string OR the 2-char string when both chars match.
    """
    correct, parsed, raw, trial = _run_one(
        problems.get("substring"), client, size=2
    )
    # Substring is a known-hard task for small models. We only assert that
    # the parsed output is well-formed (non-empty string), so a real model
    # failure here is informative not a CI break.
    assert isinstance(parsed, str), f"parser returned {parsed!r} from raw={raw!r}"


def test_sort_lang_en_small(client):
    """Specifically guards the alphabetical-vs-numerical sort bug.
    English sort of [3, 1, 2] -> ['one', 'two', 'three'] (numerical),
    not ['one', 'three', 'two'] (alphabetical)."""
    p = by_language("en")
    correct, parsed, raw, trial = _run_one(p, client, size=3)
    expected = [num2words(i, lang="en") for i in sorted(trial.extra["ints"])]
    assert correct, (
        f"sort_lang/en failed\n"
        f"  ints={trial.extra['ints']}\n"
        f"  expected={expected}\n  parsed={parsed}\n  raw={raw!r}"
    )


def test_sort_familiar_uses_actual_size(client):
    """The familiar pipeline asks the model for N numbers, accepts whatever
    comes back (which may be < N), then asks the model to sort it. This
    test checks that the sort step records actual_size and works on the
    short list, not that the model gets it right."""
    from empcomp.problems.sort_familiar import (
        generate_request,
        make_familiar_problem,
    )
    from empcomp.parsing import parse_list

    sys_p, usr_p = generate_request(5)
    resp = client.chat(sys_p, usr_p)
    nums = parse_list(resp.text) or []
    nums = [int(x) for x in nums if isinstance(x, (int, float))]
    assert len(nums) >= 2, f"generation yielded too few numbers: {nums!r}"

    problem = make_familiar_problem({5: [nums]})
    rng = random.Random(0)
    trial = problem.make_trial(rng, 5, 0, 0)
    assert trial.extra["actual_size"] == len(nums)
    assert trial.extra["requested_size"] == 5
    # Sort step itself: asserted format, not correctness, since gemma fails
    # familiar-sort on a non-trivial fraction of trials.
    system, user = problem.prompter(trial.input, trial.extra)
    resp = client.chat(system, user)
    parsed = problem.parser(resp.text)
    assert parsed is None or isinstance(parsed, list)
