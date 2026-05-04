"""JSONL trial-record store. Append-only; safe under crash."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


def trial_path(root: Path, model: str, problem: str, variant: str) -> Path:
    safe_variant = variant.replace("/", "_")
    return root / f"{model}__{problem}__{safe_variant}.jsonl"


def write_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=_default))
        f.write("\n")


def read_records(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def count_done(path: Path, size: int) -> int:
    """How many trials at this size are already recorded — for resuming a run."""
    return sum(1 for r in read_records(path) if r.get("size") == size)


def _default(o: Any):
    # Catch numpy scalars and similar without taking on numpy as a dep here.
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(f"not serializable: {type(o).__name__}")
