#!/usr/bin/env python3
"""Print deterministic fictional planning sessions, never real product timings."""

import csv
import sys

from eval_m0 import FIELDS


def main() -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for index in range(10):
        # Seven dinners: browse/select manually; generate/review/correct with Weeklies.
        manual = 35 + 7 * (60 + 5 * index + 25)
        assisted = 90 + (60 + 20 * index) + 7 * 45 + (index % 4) * 60
        budget = 10000 + 500 * (index % 3)
        writer.writerow(
            {
                "participant_id": f"sim-{index + 1:02d}",
                "data_kind": "synthetic",
                "baseline_first": "true" if index % 2 == 0 else "false",
                "baseline_seconds": manual,
                "baseline_valid_meals": 7,
                "weeklies_seconds": assisted,
                # One fictional participant cannot finish a suitable plan.
                "weeklies_valid_meals": 5 if index == 7 else 7,
                "budget_cents": budget,
                "baseline_cost_cents": budget - 500 if index < 5 else budget + 1000,
                "weeklies_cost_cents": budget + 500 if index in (2, 6, 9) else budget - 800,
                "evidence_ref": f"scripts/simulate_m0.py:profile-{index}",
            }
        )


if __name__ == "__main__":
    main()
