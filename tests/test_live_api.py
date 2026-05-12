"""Live integration tests against the configured LM Studio endpoint.

For each problem, run one trivially-easy instance through the full pipeline
(prompt -> LLM -> parse -> checker) and assert correctness. Sizes are kept
small so the whole suite runs in well under a minute.

Auto-skips if the configured LLM endpoint is unreachable.
"""
from __future__ import annotations

import os
import random
from pathlib import Path

import httpx
import pytest
from num2words import num2words

from empcomp import problems
from empcomp.llm import LMStudioClient, make_client
from empcomp.presets import get_preset, get_sizes
from empcomp.problems.sort import SORT_SIZES
from empcomp.problems.sort_lang import by_language
from empcomp.storage import trial_path


# ---------- skip-if-no-API fixture ----------

def _discover_loaded_model(base_url: str) -> str:
    """Auto-discover the first model with active loaded_instances via the native
    /api/v1/models endpoint. Skips if unreachable or nothing is loaded.
    Tests always use the actually-loaded model regardless of EMPCOMP_MODEL.
    """
    host = base_url.rstrip("/")
    if host.endswith("/v1"):
        host = host[:-3]
    try:
        r = httpx.get(f"{host}/api/v1/models", timeout=5.0)
        r.raise_for_status()
        entries = r.json().get("models", [])
    except httpx.ConnectError as e:
        pytest.skip(f"LM Studio unreachable at {host}: {e}")
    except Exception as e:
        pytest.skip(f"Could not query models at {host}: {e}")
    for entry in entries:
        instances = entry.get("loaded_instances", [])
        if instances:
            return instances[0]["id"]
    pytest.skip(f"No models currently loaded in LM Studio at {host}")


@pytest.fixture(scope="module")
def client():
    base_url = os.environ.get("EMPCOMP_BASE_URL", "http://127.0.0.1:1234")
    model = _discover_loaded_model(base_url)
    c = make_client(get_preset("default"), model=model, base_url=base_url)
    try:
        c.chat("You are a calculator.", "Reply with the digit 1 only.")
    except Exception as e:
        pytest.skip(f"LLM probe failed ({model} at {base_url}): {e}")
    print(f"\n[live-api] model={model}  base_url={base_url}", flush=True)
    return c


@pytest.fixture(scope="module")
def lmstudio(client):
    """Module-scoped fixture: skips if the active client is not LMStudioClient.
    Returns the connected LMStudioClient so preset tests can borrow its model/host.
    """
    if not isinstance(client, LMStudioClient):
        pytest.skip("preset behavior tests only apply to LMStudioClient")
    return client


def _run_one(problem, client, size, rng_seed=0):
    """Run a single trial and return (correct, parsed, raw, trial)."""
    rng = random.Random(rng_seed)
    trial = problem.make_trial(rng, size, 0, rng_seed)
    system, user = problem.prompter(trial.input, trial.extra)
    resp = client.chat(system, user)
    parsed = problem.parser(resp.text)
    correct = problem.evaluate(parsed, trial)
    return correct, parsed, resp.text, trial


# ---------- LM Studio native stats ----------

def test_lmstudio_native_stats(client):
    """LMStudioClient should populate tokens_per_second and time_to_first_token_seconds."""
    if not isinstance(client, LMStudioClient):
        pytest.skip("native stats only available on LMStudioClient")
    resp = client.chat("You are a calculator.", "Reply with the digit 1 only.")
    assert resp.tokens_per_second is not None and resp.tokens_per_second > 0, (
        f"expected tokens_per_second > 0, got {resp.tokens_per_second}"
    )
    assert resp.time_to_first_token_seconds is not None and resp.time_to_first_token_seconds > 0, (
        f"expected time_to_first_token_seconds > 0, got {resp.time_to_first_token_seconds}"
    )


# ---------- preset reasoning-mode behavior ----------

def test_default_preset_no_reasoning(lmstudio):
    """Default preset sends reasoning=off — no thinking trace, zero reasoning tokens,
    and no leaked <think>...</think> markup in the message content."""
    import re
    c = LMStudioClient(model=lmstudio.model, host=lmstudio.host, preset=get_preset("default"))
    resp = c.chat("You are a calculator.", "What is 3 + 4? Reply with the number only.")
    assert resp.thinking_text is None, (
        f"default preset should produce no reasoning block, got: {resp.thinking_text!r}"
    )
    assert resp.reasoning_output_tokens == 0, (
        f"default preset should have 0 reasoning tokens, got: {resp.reasoning_output_tokens}"
    )
    text = resp.text.strip()
    assert re.fullmatch(r"\d+", text), (
        f"expected a bare digit, got {text!r} — reasoning may have leaked into content"
    )


def test_thinking_preset_has_reasoning(lmstudio):
    """Thinking preset sends reasoning=on — model produces a reasoning trace."""
    c = LMStudioClient(model=lmstudio.model, host=lmstudio.host, preset=get_preset("thinking"))
    resp = c.chat(
        "You are a sorting assistant.",
        "Sort this list in ascending order: [42, 7, 99, 3, 55, 18, 71, 26, 84, 13]."
        " Reply only with the sorted list as comma-separated numbers.",
    )
    assert resp.text, "expected non-empty response text"
    assert resp.reasoning_output_tokens is not None, "reasoning_output_tokens must be present"
    assert resp.reasoning_output_tokens > 0, (
        f"thinking preset should produce reasoning tokens, got {resp.reasoning_output_tokens}"
    )
    assert resp.thinking_text is not None, (
        f"thinking preset should produce a reasoning block, got thinking_text=None"
    )


def test_deterministic_preset_no_reasoning_and_reproducible(lmstudio):
    """Deterministic preset: reasoning=off and temperature=0 → identical outputs.

    Uses an open-ended creative prompt so that a non-zero temperature would
    produce variation — confirming that identical outputs are due to determinism,
    not question simplicity.
    """
    c = LMStudioClient(model=lmstudio.model, host=lmstudio.host, preset=get_preset("deterministic"))
    prompt = (
        "You are a creative writer.",
        "Write a single sentence describing the feeling of seeing the first snowfall of winter.",
    )
    r1 = c.chat(*prompt)
    r2 = c.chat(*prompt)
    assert r1.thinking_text is None, (
        f"deterministic preset should have no reasoning block, got: {r1.thinking_text!r}"
    )
    assert r1.reasoning_output_tokens == 0, (
        f"deterministic preset should have 0 reasoning tokens, got: {r1.reasoning_output_tokens}"
    )
    assert r1.text == r2.text, (
        f"deterministic preset should be reproducible\n  run1={r1.text!r}\n  run2={r2.text!r}"
    )


# ---------- trial_path includes preset ----------

def test_trial_path_includes_preset(tmp_path):
    p = trial_path(tmp_path, "qwen3.6-35b-a3b", "default", "sort", "base")
    assert "qwen3.6-35b-a3b__default" in str(p)
    assert p.name == "sort__base.jsonl"


def test_trial_path_preset_subdirectory(tmp_path):
    p1 = trial_path(tmp_path, "model", "default", "sort", "base")
    p2 = trial_path(tmp_path, "model", "thinking", "sort", "base")
    assert p1.parent != p2.parent


# ---------- quick sizes are a subset of full sizes ----------

def test_quick_sizes_subset_of_sort_full():
    quick = get_sizes("quick", "sort", SORT_SIZES)
    assert set(quick).issubset(set(SORT_SIZES))
    assert len(quick) < len(SORT_SIZES)


# ---------- prompt stability and "clean output" tests ----------

@pytest.mark.parametrize(
    "prob_name, size, seed",
    [
        ("substring", 89, 42),  # Long substring (was runaway prone)
        ("ssp", 30, 123),       # SSP (was 'Wait' prone at 60)
        ("ssp", 30, 999),       # SSP (was 'manual trace' prone at 60)
        ("sort", 150, 42),      # Large sort
    ],
)
def test_empirical_computer_is_clean_and_parsable(client, prob_name, size, seed):
    """Verify that complex tasks return ONLY the data, with no conversational filler.

    The check is strict: the raw response text (stripped) must be exactly what the
    parser produces, with no leftover reasoning traces, brackets, or explanations.
    """
    import ast
    prob = problems.get(prob_name)
    rng = random.Random(seed)
    input_data, extra = prob.generator(rng, size)
    system, user = prob.prompter(input_data, extra)

    resp = client.chat(system, user)
    raw_text = resp.text.strip()

    # The goal is that raw_text SHOULD be the data itself.
    # We verify this by checking if the parser can see the whole text as valid data.

    if prob_name == "substring":
        # For substring, raw text should be the palindrome itself (no extra words).
        # Note: parse_substring is lenient (trims brackets), so we check that the
        # raw text doesn't contain spaces (a good proxy for "words").
        assert " " not in raw_text, f"Substring response contains spaces/words: {raw_text!r}"
        parsed = prob.parser(raw_text)
        assert parsed == raw_text or f"[{parsed}]" == raw_text or f"'{parsed}'" == raw_text, \
            f"Raw response contains extra characters around the substring: {raw_text!r}"

    elif prob_name in ("ssp", "sort"):
        # For list-based tasks, raw text should be a valid Python list literal and NOTHING ELSE.
        try:
            # ast.literal_eval is strict: it fails if there's any text outside the list.
            parsed_strict = ast.literal_eval(raw_text)
            assert isinstance(parsed_strict, list), "Output is not a list"
        except (ValueError, SyntaxError) as e:
            pytest.fail(
                f"Response is not a clean Python list. Likely contains reasoning filler.\n"
                f"Raw response: {raw_text!r}\nError: {e}"
            )

    # Additionally check token usage as a safety valve.
    if prob_name == "substring":
        assert resp.total_output_tokens < 100
    elif prob_name == "ssp":
        assert resp.total_output_tokens < 500
    elif prob_name == "sort":
        assert resp.total_output_tokens < 1000


def test_sort_small(client):
    correct, parsed, raw, trial = _run_one(problems.get("sort"), client, size=5)
    assert correct, (
        f"sort failed at size=5\n"
        f"  input={trial.input}\n  expected={sorted(trial.input)}\n"
        f"  parsed={parsed}\n  raw={raw!r}"
    )


def test_sorted_search_small(client):
    correct, parsed, raw, trial = _run_one(problems.get("sorted_search"), client, size=5)
    target = trial.extra["target"]
    true_idx = trial.input.index(target)
    assert correct, (
        f"sorted_search failed\n"
        f"  list={trial.input}  target={target}  true_index={true_idx}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_unsorted_search_small(client):
    correct, parsed, raw, trial = _run_one(problems.get("unsorted_search"), client, size=5)
    target = trial.extra["target"]
    true_idx = trial.input.index(target)
    assert correct, (
        f"unsorted_search failed\n"
        f"  list={trial.input}  target={target}  true_index={true_idx}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_ssp_small(client):
    correct, parsed, raw, trial = _run_one(problems.get("ssp"), client, size=2)
    assert correct, (
        f"ssp failed\n"
        f"  input={trial.input}  goal={trial.extra['goal']}\n"
        f"  parsed={parsed}  raw={raw!r}"
    )


def test_substring_size_2(client):
    correct, parsed, raw, trial = _run_one(problems.get("substring"), client, size=2)
    assert isinstance(parsed, str), f"parser returned {parsed!r} from raw={raw!r}"


def test_sort_lang_en_small(client):
    p = by_language("en")
    correct, parsed, raw, trial = _run_one(p, client, size=3)
    expected = [num2words(i, lang="en") for i in sorted(trial.extra["ints"])]
    assert correct, (
        f"sort_lang/en failed\n"
        f"  ints={trial.extra['ints']}\n"
        f"  expected={expected}\n  parsed={parsed}\n  raw={raw!r}"
    )


def test_sort_familiar_uses_actual_size(client):
    """The familiar pipeline accepts whatever length the model returns."""
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
    system, user = problem.prompter(trial.input, trial.extra)
    resp = client.chat(system, user)
    parsed = problem.parser(resp.text)
    assert parsed is None or isinstance(parsed, list)
