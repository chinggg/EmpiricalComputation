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
│   ├── llm.py               OpenAI-compatible client (single swap point)
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

## Tests

```bash
uv run pytest                    # full suite (28 unit + 7 live-API)
uv run pytest tests/test_parsing.py tests/test_problems.py  # unit-only, no LLM
```

`tests/test_live_api.py` calls the configured LM Studio endpoint with one
trivial-size instance per problem and asserts correctness end-to-end —
it is the regression net for naive bugs (parser drops a valid answer,
checker uses the wrong oracle, etc.). It auto-skips if the endpoint is
unreachable.

## Validate plot layout with mock data (no LLM needed)

```bash
uv run python scripts/make_mock_data.py
uv run python scripts/plot_all.py --model mock
```

Outputs `results/figures/figure1_mock.pdf`, `figure2_mock.pdf`, `table1_mock.csv`/`.md`.

## Run with the local Gemma-4 via LM Studio

```bash
export EMPCOMP_MODEL=gemma-4-e4b
export EMPCOMP_BASE_URL=http://127.0.0.1:1234/v1
export EMPCOMP_API_KEY=lm-studio

uv run python scripts/benchmark_latency.py --n 3
uv run python scripts/run_experiments.py --all --n 30
uv run python scripts/plot_all.py --model gemma-4-e4b
```

`run_experiments.py` is idempotent — re-running picks up where the last run left
off (records are appended to `results/trials/*.jsonl` and the runner counts
existing trials per size before issuing new calls).

## Trial record schema (JSONL, one line per trial)

```json
{
  "problem": "sort", "variant": "base", "model": "gemma-4-e4b",
  "size": 30, "trial": 0, "seed": 0,
  "input": [...], "extra": {...},
  "system": "...", "user": "...",
  "raw_response": "...", "parsed": [...],
  "correct": true, "elapsed_s": 1.23,
  "tokens_in": 240, "tokens_out": 88, "ts": "2026-05-04T22:01:09+00:00"
}
```

## Extending

| To add | Touch |
|---|---|
| A new model | construct a different `LLMClient` (or change env vars) |
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

The defaults are tuned for `gemma-4-e4b` on local LM Studio (single GPU, ~60
tok/s, ~10 s/call mean once the model decides to "think"). Measured with
`benchmark_latency.py --n 2`:

| Problem          | Default sizes                       | Trials | Calls | Est.  |
|------------------|-------------------------------------|-------:|------:|------:|
| sort             | 10, 25, 50, 75, 100, 125, 150       | 30     | 210   | ~30 m |
| sorted_search    | 10, 25, 50, 75, 100, 125, 150       | 30     | 210   | ~25 m |
| unsorted_search  | 10, 25, 50, 75, 100, 125, 150       | 30     | 210   | ~20 m |
| ssp              | 2, 5, 8, 11, 14, 17, 20             | 30     | 210   | ~50 m |
| substring        | 2..20 (19)                          | 30     | 570   | ~3 m  |
| sort_lang        | 8 sizes × 10 langs                  | 30     | 2 400 | ~5 h  |
| sort_familiar    | 5 sizes (10..50, gen + sort)        | 30     | ~300  | ~25 m |
| **total**        |                                     |        | ~4 110 | ~7.5 h |

The paper used finer grids (step=5 for sort/search, all 15 lang sizes). Pass
`--sizes ...` or `--languages ...` to `run_experiments.py` to recover them when
budget allows. The runner is resumable so partial overnight runs aren't lost.
