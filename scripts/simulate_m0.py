#!/usr/bin/env python3
"""Seeded fictional users; timings and selection rules are assumptions, not evidence."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import random
import sys

from eval_m0 import FIELDS, evaluate

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evals/m0/catalog.csv"
VERSION = "seeded-planning-v1"
ASSUMPTIONS = {
    "provenance": "Fictional users and menu; neither the app nor a model is executed.",
    "prices": "One serving per dinner; no taxes or fees; all items available and restaurants open.",
    "pace": "Lognormal(0, 0.25), clamped to 0.55..1.9; shared across both tasks.",
    "carefulness": "Lognormal(0, 0.25), clamped to 0.6..1.7; shared across both tasks.",
    "budget_attention": "Uniform(0.35, 0.9); probability of trying to repair an over-budget plan.",
    "patience_seconds": "Uniform integer 700..1200; shared across tasks; truncate last event.",
    "budget_cents": [6500, 8000, 9500, 11000],
    "preferences": "30% vegetarian; one restriction sampled from none, milk, peanuts, wheat.",
    "selection": "Shared item tastes uniform(0.5,1.5); preferred cuisine doubles weight. Weight = taste * cuisine factor / dollar price ** pressure; pressure is attention * 0.8 manually and attention * 2 with Weeklies. Repeats allowed.",
    "practice": "Human actions in the second task take 92% as long; generation waits unaffected.",
    "manual": "Setup uniform(20,50); each meal browse lognormal(log(60),0.5), review triangular(8,35,18), record uniform(8,18). 15% chance of backtracking uniform(30,80).",
    "weeklies": "Setup uniform(35,75); wait lognormal(log(45),0.6), with 12% chance of a uniform(3,6) multiplier. Each meal review triangular(10,50,20), record uniform(5,12). Shared rejection chance uniform(0.12,0.38); replacement browse triangular(25,130,55) followed by another review.",
    "budget_repair": "Check triangular(10,50,20). With budget-attention probability attempt 1..3 cheaper swaps of the most expensive dinner. Each swap takes lognormal(log(50),0.5) browsing plus 15 seconds review, scaled by personal traits.",
    "scaling": "Browsing/setup/recording use pace; reviews/checks use carefulness; all human actions include practice multiplier.",
}


def load_catalog(path):
    with path.open(newline="") as stream:
        items = list(csv.DictReader(stream))
    for item in items:
        item["price_cents"] = int(item["price_cents"])
        if item["vegetarian"] not in ("true", "false"):
            raise ValueError("vegetarian must be true or false")
        item["vegetarian"] = item["vegetarian"] == "true"
        item["allergens"] = item["allergens"].split(",") if item["allergens"] else []
        if item["price_cents"] <= 0 or not item["item_id"]:
            raise ValueError("catalog needs positive prices and item IDs")
    if not items or len({item["item_id"] for item in items}) != len(items):
        raise ValueError("catalog must be nonempty with unique IDs")
    return items


class SessionClock:
    """Use hundredths of a second so event sums reproduce CSV timings exactly."""

    def __init__(self, limit):
        self.limit = limit * 100
        self.elapsed = 0
        self.events = []

    def spend(self, phase, seconds, **details):
        requested = max(1, round(seconds * 100))
        spent = min(requested, self.limit - self.elapsed)
        self.elapsed += spent
        complete = spent == requested
        self.events.append(dict(phase=phase, seconds=spent / 100, completed=complete, **details))
        return complete


def run_session(rng, profile, eligible, method, second):
    clock = SessionClock(profile["patience_seconds"])
    pace = profile["pace"] * (0.92 if second else 1)
    care = profile["carefulness"] * (0.92 if second else 1)
    selected = []

    def choose(items):
        pressure = profile["budget_attention"] * (0.8 if method == "baseline" else 2)
        weights = [
            profile["tastes"][item["item_id"]]
            * (2 if item["cuisine"] == profile["preferred_cuisine"] else 1)
            / (item["price_cents"] / 100) ** pressure
            for item in items
        ]
        return rng.choices(items, weights=weights, k=1)[0]

    def result():
        return {
            "method": method,
            "second_task": second,
            "seconds": clock.elapsed / 100,
            "valid_meals": len(selected),
            "cost_cents": sum(item["price_cents"] for item in selected),
            "stop_reason": (
                "time_limit"
                if any(not event["completed"] for event in clock.events)
                else "task_finished"
            ),
            "events": clock.events,
            "selections": [
                {"slot": i + 1, "item_id": item["item_id"], "price_cents": item["price_cents"]}
                for i, item in enumerate(selected)
            ],
        }

    setup = rng.uniform(20, 50) if method == "baseline" else rng.uniform(35, 75)
    if not clock.spend("setup", setup * pace):
        return result()
    if method == "weeklies":
        wait = rng.lognormvariate(math.log(45), 0.6)
        long_wait = rng.random() < 0.12
        if long_wait:
            wait *= rng.uniform(3, 6)
        if not clock.spend("generation_wait", wait, long_wait=long_wait):
            return result()
    for slot in range(1, 8):
        if method == "baseline" and not clock.spend(
            "browse", rng.lognormvariate(math.log(60), 0.5) * pace, slot=slot
        ):
            return result()
        item = choose(eligible)
        review = rng.triangular(8, 35, 18) if method == "baseline" else rng.triangular(10, 50, 20)
        if not clock.spend("review", review * care, slot=slot):
            return result()
        probability = 0.15 if method == "baseline" else profile["rejection_probability"]
        if rng.random() < probability:
            duration = rng.uniform(30, 80) if method == "baseline" else rng.triangular(25, 130, 55)
            replacement = choose(
                [candidate for candidate in eligible if candidate != item] or eligible
            )
            if not clock.spend(
                "backtrack" if method == "baseline" else "replacement_browse",
                duration * pace,
                slot=slot,
                old_item_id=item["item_id"],
                new_item_id=replacement["item_id"],
            ):
                return result()
            item = replacement
            if method == "weeklies" and not clock.spend(
                "replacement_review", rng.triangular(10, 50, 20) * care, slot=slot
            ):
                return result()
        record = rng.uniform(8, 18) if method == "baseline" else rng.uniform(5, 12)
        if not clock.spend("record", record * pace, slot=slot):
            return result()
        selected.append(item)
    if not clock.spend("budget_check", rng.triangular(10, 50, 20) * care):
        return result()
    if (
        sum(item["price_cents"] for item in selected) > profile["budget_cents"]
        and rng.random() < profile["budget_attention"]
    ):
        for _ in range(rng.randint(1, 3)):
            slot = max(range(len(selected)), key=lambda i: selected[i]["price_cents"])
            old = selected[slot]
            cheaper = [item for item in eligible if item["price_cents"] < old["price_cents"]]
            if not cheaper:
                break
            new = choose(cheaper)
            duration = rng.lognormvariate(math.log(50), 0.5) * pace + 15 * care
            if not clock.spend(
                "budget_swap",
                duration,
                slot=slot + 1,
                old_item_id=old["item_id"],
                new_item_id=new["item_id"],
            ):
                return result()
            selected[slot] = new
            if sum(item["price_cents"] for item in selected) <= profile["budget_cents"]:
                break
    return result()


def render_csv(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def simulate(seed=510, participants=10, catalog_path=CATALOG):
    if participants < 1:
        raise ValueError("participants must be positive")
    catalog = load_catalog(catalog_path)
    rng = random.Random(seed)
    orders = [i % 2 == 0 for i in range(participants)]
    rng.shuffle(orders)
    rows, traces = [], []
    for index, baseline_first in enumerate(orders):
        profile = {
            "pace": min(1.9, max(0.55, rng.lognormvariate(0, 0.25))),
            "carefulness": min(1.7, max(0.6, rng.lognormvariate(0, 0.25))),
            "budget_attention": rng.uniform(0.35, 0.9),
            "patience_seconds": rng.randint(700, 1200),
            "budget_cents": rng.choice([6500, 8000, 9500, 11000]),
            "vegetarian": rng.random() < 0.3,
            "avoided_allergen": rng.choice([None, "milk", "peanuts", "wheat"]),
            "preferred_cuisine": rng.choice(sorted({item["cuisine"] for item in catalog})),
            "rejection_probability": rng.uniform(0.12, 0.38),
            "tastes": {item["item_id"]: rng.uniform(0.5, 1.5) for item in catalog},
        }
        eligible = [
            item
            for item in catalog
            if (not profile["vegetarian"] or item["vegetarian"])
            and profile["avoided_allergen"] not in item["allergens"]
        ]
        if (
            not eligible
            or min(item["price_cents"] for item in eligible) * 7 > profile["budget_cents"]
        ):
            raise ValueError("catalog cannot support this participant's seven-meal budget")
        order = ["baseline", "weeklies"] if baseline_first else ["weeklies", "baseline"]
        sessions = {
            method: run_session(rng, profile, eligible, method, position == 1)
            for position, method in enumerate(order)
        }
        participant = f"sim-{index + 1:02d}"
        row = dict(
            participant_id=participant,
            data_kind="synthetic",
            baseline_first=str(baseline_first).lower(),
            budget_cents=profile["budget_cents"],
            evidence_ref=f"simulation:{VERSION}:seed={seed}:participant={participant}",
        )
        for method, session in sessions.items():
            for field in ("seconds", "valid_meals", "cost_cents"):
                row[f"{method}_{field}"] = session[field]
        rows.append(row)
        traces.append(dict(participant_id=participant, profile=profile, sessions=sessions))
    trace = dict(
        version=VERSION,
        seed=seed,
        participants=participants,
        assumptions=ASSUMPTIONS,
        catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
        input_sha256=hashlib.sha256(render_csv(rows).encode()).hexdigest(),
        catalog=catalog,
        traces=traces,
    )
    return rows, trace


def sensitivity(seed=510, participants=10, catalog_path=CATALOG):
    runs = []
    for current in range(seed, seed + 5):
        rows, _ = simulate(current, participants, catalog_path)
        report = evaluate(render_csv(rows).encode())
        runs.append(
            {"seed": current, **{key: value for key, value in report.items() if key != "pairs"}}
        )
    return dict(
        version=VERSION,
        interpretation="Fictional sensitivity check, not evidence of user benefit; all five consecutive seeds retained.",
        runs=runs,
        passes=sum(run["verdict"] == "PASS" for run in runs),
    )


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=510)
    parser.add_argument("--participants", type=int, default=10)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--sensitivity-output", type=Path)
    args = parser.parse_args()
    try:
        rows, trace = simulate(args.seed, args.participants, args.catalog)
        if args.trace:
            write_json(args.trace, trace)
        if args.sensitivity_output:
            write_json(
                args.sensitivity_output, sensitivity(args.seed, args.participants, args.catalog)
            )
        sys.stdout.write(render_csv(rows))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Simulation error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
