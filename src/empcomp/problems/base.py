"""Problem abstraction.

A Problem is a callable bundle of (generator, prompter, parser, oracle).
The runner is intentionally generic so adding a new problem only means
writing one of these.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Trial:
    """A single problem instance to evaluate."""
    problem: str
    variant: str
    size: int
    trial: int
    seed: int
    input: Any                      # problem-specific input data
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrialOutcome:
    parsed: Any                     # may be None on parse failure
    correct: bool                   # False on parse failure


# A prompter returns (system, user). A parser returns the parsed value or None.
# An oracle returns the ground-truth answer (used for instrumentation).
# A checker returns True iff the parsed value is correct.

PrompterFn = Callable[[Any, dict], tuple[str, str]]
ParserFn = Callable[[str], Any]
OracleFn = Callable[[Any], Any]
CheckerFn = Callable[[Any, Any], bool]
GeneratorFn = Callable[[random.Random, int], tuple[Any, dict]]
"""Returns (input, extra). `extra` carries auxiliary state needed by the prompter
or oracle (e.g. the search target) so the input itself stays clean."""


@dataclass
class Problem:
    name: str
    variant: str                    # e.g. "base" / "lang=en" / "familiar"
    sizes: list[int]
    generator: GeneratorFn
    prompter: PrompterFn
    parser: ParserFn
    oracle: OracleFn
    checker: CheckerFn

    def make_trial(self, rng: random.Random, size: int, trial_idx: int, seed: int) -> Trial:
        inp, extra = self.generator(rng, size)
        return Trial(
            problem=self.name,
            variant=self.variant,
            size=size,
            trial=trial_idx,
            seed=seed,
            input=inp,
            extra=extra,
        )

    def evaluate(self, parsed: Any, trial: Trial) -> bool:
        if parsed is None:
            return False
        try:
            return bool(self.checker(parsed, {"input": trial.input, **trial.extra}))
        except Exception:
            return False
