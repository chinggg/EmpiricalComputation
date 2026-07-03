# [ASE '26 NIER] Artifact of "Empirical Computation: Prompting versus Programming"

This repository contains the official replication package and artifact for our paper:

**Empirical Computation: Prompting versus Programming** [[PDF]](https://mboehme.github.io/paper/ASE26-empirical.pdf)

```bibtex
@inproceedings{ASE26-empirical,
  author       = {Tang, Eric and Liu, Jing and B{\"o}hme, Marcel},
  booktitle    = {Proceedings of the 41st IEEE/ACM International Conference on Automated Software Engineering (NIER track)},
  numpages     = {5},
  series       = {ASE'26 (NIER)},
  title        = {Empirical Computation: Prompting versus Programming},
  year         = {2026},
}
```

It provides the complete implementation to reproduce the experiments, extend them with new models/problems/prompts, and regenerate the tables and figures shown in the paper. The actual results of our experiments are compressed in `results.7z`.

## Layout

```
├── pyproject.toml           uv-managed
├── results.7z               Compressed experimental trials and data from the paper
├── src/empcomp/
│   ├── llm.py               LM Studio native client + OpenAI-compat fallback
│   ├── presets.py           named experiment presets (default / thinking / deterministic)
│   ├── prompts.py           every prompt template (single edit point)
│   ├── parsing.py           lenient response parsers
│   ├── problems/            one Problem per task
│   ├── runner.py            generic, resumable trial driver
│   ├── storage.py           append-only JSONL records
│   ├── aggregate.py         JSONL → tidy CSV
│   └── plotting/            figure1 / figure2 / table1
├── scripts/
│   ├── make_mock_data.py    synthesize trials to validate the plot pipeline
│   ├── benchmark_latency.py probe model timing for sizing the run budget
│   ├── run_experiments.py   drive the full suite (resumable)
│   └── plot_all.py          render all figures from JSONL
└── results/{trials,csv,figures}/ Empty placeholders (populate via results.7z or new runs)
```

## Setup

```bash
uv sync                  # runtime deps
uv sync --group dev      # + pytest for the test suite
```

## Presets

Three named presets control temperature and reasoning mode sent to LM Studio:

| Preset          | Temperature       | Reasoning |
|-----------------|-------------------|-----------|
| `default`       | model default     | off       |
| `thinking`      | model default     | on        |
| `deterministic` | 0.0 (greedy)      | off       |

`default` and `thinking` omit the temperature field so LM Studio applies the
model's own recommended value. `reasoning=off` gives direct answers with no
thinking overhead; `reasoning=on` produces a separate reasoning trace captured
in `thinking_text` and `reasoning_output_tokens`.

## Tests

```bash
uv run pytest                    # full suite (39 unit + 18 live-API)
uv run pytest tests/test_parsing.py tests/test_presets.py tests/test_problems.py  # unit-only, no LLM
uv run pytest tests/test_live_api.py -v -s  # live tests (prints model name)
```

`tests/test_live_api.py` auto-discovers the model currently loaded in LM Studio
(via `/api/v1/models`) and auto-skips if nothing is loaded or the endpoint is
unreachable. It covers:
- one end-to-end trial per problem (prompt → LLM → parse → checker)
- preset behavior: `default` produces no reasoning trace; `thinking` produces one;
  `deterministic` produces identical output on two identical prompts

## Validate plot layout with mock data (no LLM needed)

```bash
uv run python scripts/make_mock_data.py
uv run python scripts/plot_all.py --model mock
```

Outputs `results/figures/figure1_mock.pdf`, `figure2_mock.pdf`, `table1_mock.csv`/`.md`.

## Run with a local model via LM Studio

```bash
export EMPCOMP_BASE_URL=http://127.0.0.1:1234/v1
export EMPCOMP_API_KEY=lm-studio
export EMPCOMP_MODEL=gemma-4-26b-a4b   # set to whichever model is loaded

# quick trials
uv run python scripts/benchmark_latency.py --n 3  # try three trials for benchmark speed
uv run python scripts/run_experiments.py --problems sort --preset thinking --sizes-preset quick --n 2  # quickly see reasoning times by sorting a few sizes

# full experiment
uv run python scripts/run_experiments.py --all --n 30  # default preset run all problems
uv run python scripts/run_experiments.py --preset deterministic --n 30 --problems sort sorted_search unsorted_search ssp substring  # deterministic preset run core problems in figure 1
uv run python scripts/run_experiments.py --preset thinking --n 15 --problems sort sorted_search unsorted_search ssp substring  # thinking preset run core problems in figure 1, with only 15 trials to save time

# generate trials,csv,figures under results/
uv run python scripts/plot_all.py --model gemma-4-26b-a4b  # implies --preset default
uv run python scripts/plot_all.py --model gemma-4-26b-a4b --preset thinking
uv run python scripts/plot_all.py --model gemma-4-26b-a4b --combined  # combine all presets in same figure
uv run python scripts/plot_all.py --model gemma-4-26b-a4b --combined --logscale  # combine all presets in same figure with log scale
```

`run_experiments.py` is idempotent — re-running picks up where the last run left
off (records are appended to `results/trials/*.jsonl` and the runner counts
existing trials per size before issuing new calls). Trial files are stored under
`results/trials/<model>__<preset>/`.

## Trial record schema (JSONL, one line per trial)

```json
{
  "problem": "sort",
  "variant": "base",
  "model": "gemma-4-26b-a4b",
  "preset": "default",
  "size": 30,
  "trial": 0,
  "seed": 0,
  "input": [...],
  "extra": {},
  "system": "...",
  "user": "...",
  "raw_response": "...",
  "parsed": [...],
  "correct": true,
  "elapsed_s": 1.23,
  "input_tokens": 240,
  "total_output_tokens": 88,
  "reasoning_output_tokens": 0,
  "tokens_per_second": 61.4,
  "time_to_first_token_seconds": 0.31,
  "thinking_text": null,
  "stop_reason": null,
  "error": null
}
```

`reasoning_output_tokens` and `thinking_text` are non-zero/non-null only for
the `thinking` preset. `error` is non-null when the LLM call itself failed.

## Extending

| To add | Touch |
|---|---|
| A new model | set `EMPCOMP_MODEL` / `EMPCOMP_BASE_URL` env vars |
| A new prompt phrasing | edit `src/empcomp/prompts.py` |
| A new computational problem | add a `Problem` subclass in `src/empcomp/problems/` and register it |
| A new language for sort_lang | add the language code to `LANGUAGES` in `src/empcomp/problems/sort_lang.py` |
| A new metric | extend `summarize` in `src/empcomp/aggregate.py` |
| A new plot | drop a module under `src/empcomp/plotting/` |

These extension points make this replication package highly flexible and extensible. Researchers can easily swap models, test different prompt-engineering variants (such as CoT), extend the problem set, or vary instance encodings.

