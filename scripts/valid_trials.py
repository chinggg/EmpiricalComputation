#!/usr/bin/env python3
"""Validate (and optionally fix/sort) JSONL trial files.

Warnings issued for:
  - entries with parsed=null
  - duplicate entries: same (problem, variant, model, preset, size, trial) + same input
  - per-size valid-unique count not a multiple of 5

--fix            removes null and duplicate entries in-place
--sort           sorts all entries by (size, trial, ts) in-place
--inplace SUFFIX write fixed/sorted output to <file><SUFFIX> instead of
                 overwriting the original (e.g. --inplace .bak)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ERROR: line {lineno} JSON parse failure: {e}", file=sys.stderr)
    return records


def _trial_key(r: dict) -> tuple:
    return (r.get("problem"), r.get("variant"), r.get("model"), r.get("preset"),
            r.get("size"), r.get("trial"))


def validate_file(path: Path, *, fix: bool, sort: bool, inplace: str | None = None) -> bool:
    records = load_records(path)
    if not records:
        return True

    warnings: list[str] = []

    # --- null check ---
    null_records = [r for r in records if r.get("parsed") is None]
    if null_records:
        warnings.append(f"{len(null_records)} null-parsed entr{'y' if len(null_records)==1 else 'ies'}")

    valid = [r for r in records if r.get("parsed") is not None]

    # --- duplicate check ---
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in valid:
        groups[_trial_key(r)].append(r)

    kept: list[dict] = []
    dup_count = 0
    for key, group in groups.items():
        if len(group) == 1:
            kept.append(group[0])
            continue
        canonical_input = json.dumps(group[0].get("input"), sort_keys=True)
        same_input = all(json.dumps(g.get("input"), sort_keys=True) == canonical_input for g in group)
        if same_input:
            dup_count += len(group) - 1
            kept.append(group[0])
        else:
            # Different inputs on same trial ID — keep all, surface as a harder error
            warnings.append(
                f"CONFLICT: key={key} has {len(group)} entries with differing inputs"
            )
            kept.extend(group)

    if dup_count:
        warnings.append(
            f"{dup_count} duplicate entr{'y' if dup_count==1 else 'ies'} "
            f"(same trial id + input, keeping first)"
        )

    # --- sort order check ---
    sort_key = lambda r: (r.get("size") or 0, r.get("trial") or 0, r.get("ts") or "")
    if records != sorted(records, key=sort_key):
        warnings.append("entries are not sorted by (size, trial, ts)")

    # --- per-size count check (after dedup) ---
    size_counts: dict[tuple, int] = defaultdict(int)
    for r in kept:
        size_key = (r.get("problem"), r.get("variant"), r.get("model"), r.get("preset"), r.get("size"))
        size_counts[size_key] += 1

    bad_sizes = [(k, n) for k, n in size_counts.items() if n % 5 != 0]
    if bad_sizes:
        for (problem, variant, model, preset, size), n in sorted(bad_sizes):
            warnings.append(f"size={size} has {n} valid unique trials (not a multiple of 5)")

    # --- report ---
    if warnings:
        print(f"{path}:")
        for w in warnings:
            print(f"  WARNING: {w}")

    # --- apply fixes ---
    if fix or sort:
        out_records = kept if fix else records
        if sort:
            out_records = sorted(
                out_records,
                key=lambda r: (r.get("size") or 0, r.get("trial") or 0, r.get("ts") or ""),
            )
        out_path = Path(str(path) + inplace) if inplace else path
        with out_path.open("w", encoding="utf-8") as f:
            for r in out_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        actions = []
        if fix:
            removed = len(null_records) + dup_count
            actions.append(f"removed {removed} entr{'y' if removed==1 else 'ies'}")
        if sort:
            actions.append("sorted")
        dest = f" → {out_path.name}" if inplace else ""
        print(f"  FIXED ({', '.join(actions)}): {len(out_records)} entries remain{dest}")

    return not warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSONL trial files.")
    parser.add_argument("path", help="JSONL file or folder containing JSONL files")
    parser.add_argument("--fix", action="store_true",
                        help="Remove null and duplicate entries in-place")
    parser.add_argument("--sort", action="store_true",
                        help="Sort entries by (size, trial, ts) in-place")
    parser.add_argument("--inplace", metavar="SUFFIX",
                        help="Write output to <file><SUFFIX> instead of overwriting original "
                             "(e.g. --inplace .bak); requires --fix or --sort")
    args = parser.parse_args()

    if args.inplace and not (args.fix or args.sort):
        parser.error("--inplace requires --fix or --sort")

    target = Path(args.path)
    if target.is_dir():
        files = sorted(target.rglob("*.jsonl"))
        if not files:
            print(f"No JSONL files found under {target}", file=sys.stderr)
            sys.exit(1)
    elif target.is_file():
        files = [target]
    else:
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    all_clean = True
    for f in files:
        if not validate_file(f, fix=args.fix, sort=args.sort, inplace=args.inplace):
            all_clean = False

    if all_clean:
        print("All files OK")
    sys.exit(0 if all_clean else 1)


if __name__ == "__main__":
    main()
