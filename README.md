# Empirical Computation — clean re-implementation

Re-implements the experiments from *Empirical Computation: Prompting versus
Programming* in a way that is small, resumable, and easy to extend with new
problems, models, or prompts. Drop-in target: a single overnight run on a
local LLM (e.g. Gemma 4 via LM Studio) producing Figures 1–2 and Table 1
identical in layout to the paper.

## Layout

```
newcode/
├── pyproject.toml           uv-managed
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
└── results/{trials,csv,figures}/
```

## Setup

```bash
cd newcode
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
uv run pytest                    # full suite (39 unit + 14 live-API)
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
| A new computational problem | add a `Problem` in `src/empcomp/problems/` and register |
| A new language for sort_lang | add the code to `LANGUAGES` in `sort_lang.py` |
| A new metric | extend `aggregate.summarize` |
| A new plot | drop a module under `plotting/` |

These hooks are the points the rejection reviews repeatedly asked for: model
swap, prompt-engineering variants (CoT, etc.), problem-set extension beyond toy
algorithms, and instance-encoding variation. The code does not implement any of
those new variants — it just doesn't fight you when you want to add them.

## Sizing the overnight run

Measured with `benchmark_latency.py --n 2` on Gemma-4-26B-A4B (~60 tok/s,
LM Studio, `default` preset, reasoning off).

| Problem          | Default sizes                      | Trials | Calls | Est.   |
|------------------|------------------------------------|-------:|------:|-------:|
| sort             | 5, 10, 15, …, 150 (step=5, 30 pts) | 30     | 900   | ~100 m |
| sorted_search    | 5, 10, 15, …, 150 (step=5, 30 pts) | 30     | 900   | ~13 m  |
| unsorted_search  | 5, 10, 15, …, 150 (step=5, 30 pts) | 30     | 900   | ~13 m  |
| ssp              | 2, 4, …, 60 (step=2, 30 pts)       | 30     | 900   | ~21 m  |
| substring        | 2, 5, …, 89 (step=3, 30 pts)       | 30     | 900   | ~5 m   |
| sort_lang        | 8 sizes × 10 langs                 | 30     | 2 400 | ~75 m  |
| sort_familiar    | 10, 25, 50, 75, 100 (gen + sort)   | 30     | ~300  | ~23 m  |
| **total**        |                                    |        | ~7 170 | ~4 h   |

The paper used more sizes to as we found reasoning LLM is really capable of solving these problems when size is small. The runner is resumable so partial overnight runs aren't lost.
