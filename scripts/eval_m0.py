#!/usr/bin/env python3
"""Evaluate paired planning sessions. Python standard library only; see docs/m0.md."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import sys


POLICY = {
    "version": "m0-time-budget-v2",
    "target_meals": 7,
    "timeout_seconds": 1200,
    "minimum_pairs": 5,
    "minimum_median_reduction": 0.30,
    "minimum_completion_rate": 0.80,
    "minimum_budget_success_rate": 0.80,
    "minimum_budget_lift_percentage_points": 20,
}
FIELDS = [
    "participant_id",
    "data_kind",
    "baseline_first",
    "baseline_seconds",
    "baseline_valid_meals",
    "weeklies_seconds",
    "weeklies_valid_meals",
    "budget_cents",
    "baseline_cost_cents",
    "weeklies_cost_cents",
    "evidence_ref",
]


def evaluate(data: bytes) -> dict:
    """Validate every pair, then score without dropping incomplete sessions."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    if reader.fieldnames != FIELDS:
        raise ValueError(f"CSV columns must be exactly: {','.join(FIELDS)}")
    pairs = []
    seen = set()
    kinds = set()
    for line, row in enumerate(reader, start=2):
        if None in row or any(value is None or not value.strip() for value in row.values()):
            raise ValueError(f"line {line}: missing or extra cells")
        row = {key: value.strip() for key, value in row.items()}
        participant = row["participant_id"]
        if participant in seen:
            raise ValueError(f"line {line}: duplicate participant_id {participant}")
        seen.add(participant)
        if row["data_kind"] not in {"synthetic", "pilot"}:
            raise ValueError(f"line {line}: data_kind must be synthetic or pilot")
        kinds.add(row["data_kind"])
        if row["baseline_first"] not in {"true", "false"}:
            raise ValueError(f"line {line}: baseline_first must be true or false")
        budget = int(row["budget_cents"])
        if budget <= 0:
            raise ValueError(f"line {line}: budget_cents must be a positive integer")
        pair = {
            "participant_id": participant,
            "baseline_first": row["baseline_first"] == "true",
            "evidence_ref": row["evidence_ref"],
            "budget_cents": budget,
        }
        for method in ("baseline", "weeklies"):
            seconds = float(row[f"{method}_seconds"])
            meals = int(row[f"{method}_valid_meals"])
            if not math.isfinite(seconds) or not 0 < seconds <= POLICY["timeout_seconds"]:
                raise ValueError(f"line {line}: {method}_seconds must be finite and in (0, 1200]")
            if not 0 <= meals <= POLICY["target_meals"]:
                raise ValueError(f"line {line}: {method}_valid_meals must be in [0, 7]")
            complete = meals == POLICY["target_meals"]
            cost = int(row[f"{method}_cost_cents"])
            if cost < 0 or (complete and cost == 0):
                raise ValueError(f"line {line}: cost must be nonnegative, positive for a full plan")
            pair[f"{method}_cost_cents"] = cost
            pair[f"{method}_within_budget"] = complete and cost <= budget
            pair[f"{method}_complete"] = complete
            pair[f"{method}_observed_seconds"] = seconds
            pair[f"{method}_scored_seconds"] = (
                seconds if complete else POLICY["timeout_seconds"]
            )
        pair["reduction"] = (
            1 - pair["weeklies_scored_seconds"] / pair["baseline_scored_seconds"]
        )
        pairs.append(pair)
    if not pairs:
        raise ValueError("CSV must contain at least one paired session")
    if len(kinds) != 1:
        raise ValueError("Do not pool synthetic and pilot evidence")

    median_reduction = statistics.median(pair["reduction"] for pair in pairs)
    completion = {
        method: sum(pair[f"{method}_complete"] for pair in pairs) / len(pairs)
        for method in ("baseline", "weeklies")
    }
    budget_successes = {
        method: sum(pair[f"{method}_within_budget"] for pair in pairs)
        for method in ("baseline", "weeklies")
    }
    budget_rates = {method: count / len(pairs) for method, count in budget_successes.items()}
    budget_lift_points = (
        100 * (budget_successes["weeklies"] - budget_successes["baseline"]) / len(pairs)
    )
    checks = {
        "enough_pairs": len(pairs) >= POLICY["minimum_pairs"],
        "median_reduction": median_reduction >= POLICY["minimum_median_reduction"],
        "baseline_completion": completion["baseline"] >= POLICY["minimum_completion_rate"],
        "weeklies_completion": completion["weeklies"] >= POLICY["minimum_completion_rate"],
        "weeklies_budget_success": (
            budget_rates["weeklies"] >= POLICY["minimum_budget_success_rate"]
        ),
        # Compare counts to avoid floating-point error at the exact 20-point boundary.
        "budget_lift": (
            100 * (budget_successes["weeklies"] - budget_successes["baseline"])
            >= POLICY["minimum_budget_lift_percentage_points"] * len(pairs)
        ),
    }
    return {
        "policy": POLICY,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "data_kind": next(iter(kinds)),
        "interpretation": (
            "Synthetic instrument demonstration; no real-user benefit established."
            if kinds == {"synthetic"}
            else "Observed pilot sample; not a population-level conclusion."
        ),
        "sample_size": len(pairs),
        "median_reduction": median_reduction,
        "median_seconds": {
            method: statistics.median(pair[f"{method}_scored_seconds"] for pair in pairs)
            for method in ("baseline", "weeklies")
        },
        "completion_rate": completion,
        "budget_success_rate": budget_rates,
        "budget_lift_percentage_points": budget_lift_points,
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "pairs": pairs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Paired session CSV (synthetic or pilot)")
    parser.add_argument("--output", type=Path, help="Write the reproducible JSON report")
    args = parser.parse_args()
    try:
        report = evaluate(args.input.read_bytes())
        rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"M0 input/output error: {exc}", file=sys.stderr)
        return 2
    print(rendered, end="")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
