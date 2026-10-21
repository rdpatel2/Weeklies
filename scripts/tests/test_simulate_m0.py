"""Verify reproducibility and that totals come from completed simulated actions."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulate_m0 import SessionClock, render_csv, sensitivity, simulate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


class SimulationTests(unittest.TestCase):
    def test_seed_repeats_but_different_seed_changes_sample(self):
        self.assertEqual(simulate(510), simulate(510))
        self.assertNotEqual(simulate(510)[0], simulate(511)[0])

    def test_costs_eligibility_and_elapsed_time_reconcile(self):
        for seed in range(510, 515):
            rows, trace = simulate(seed)
            items = {item["item_id"]: item for item in trace["catalog"]}
            self.assertEqual(
                trace["input_sha256"], hashlib.sha256(render_csv(rows).encode()).hexdigest()
            )
            for row, person in zip(rows, trace["traces"]):
                profile = person["profile"]
                self.assertEqual(row["budget_cents"], profile["budget_cents"])
                for method, session in person["sessions"].items():
                    events = session["events"]
                    selections = session["selections"]
                    self.assertEqual(
                        round(session["seconds"] * 100),
                        sum(round(event["seconds"] * 100) for event in events),
                    )
                    self.assertLessEqual(session["seconds"], profile["patience_seconds"])
                    self.assertEqual(row[f"{method}_valid_meals"], len(selections))
                    self.assertEqual(row[f"{method}_seconds"], session["seconds"])
                    self.assertEqual(
                        row[f"{method}_cost_cents"],
                        sum(items[choice["item_id"]]["price_cents"] for choice in selections),
                    )
                    self.assertEqual(
                        len(selections),
                        sum(event["phase"] == "record" and event["completed"] for event in events),
                    )
                    for choice in selections:
                        item = items[choice["item_id"]]
                        self.assertEqual(choice["price_cents"], item["price_cents"])
                        self.assertNotIn(profile["avoided_allergen"], item["allergens"])
                        if profile["vegetarian"]:
                            self.assertTrue(item["vegetarian"])
                    # Budget repairs must actually choose a cheaper eligible item.
                    for swap in (event for event in events if event["phase"] == "budget_swap"):
                        self.assertLess(
                            items[swap["new_item_id"]]["price_cents"],
                            items[swap["old_item_id"]]["price_cents"],
                        )
                    if session["stop_reason"] == "time_limit":
                        self.assertFalse(events[-1]["completed"])
                        self.assertEqual(session["seconds"], profile["patience_seconds"])

    def test_task_order_balanced_and_practice_applied_to_second_task(self):
        rows, trace = simulate()
        self.assertEqual(sum(row["baseline_first"] == "true" for row in rows), 5)
        for row, person in zip(rows, trace["traces"]):
            self.assertEqual(
                person["sessions"]["baseline"]["second_task"], row["baseline_first"] == "false"
            )
            self.assertEqual(
                person["sessions"]["weeklies"]["second_task"], row["baseline_first"] == "true"
            )

    def test_deadline_exact_limit_and_truncated_action(self):
        clock = SessionClock(1)
        self.assertTrue(clock.spend("record", 1))
        self.assertFalse(clock.spend("record", 1))
        self.assertEqual(clock.elapsed, 100)
        clock = SessionClock(1)
        self.assertFalse(clock.spend("browse", 2))
        self.assertEqual(clock.events[0]["seconds"], 1)

    def test_sample_exercises_waits_corrections_and_abandonment(self):
        sessions = [
            session
            for seed in range(510, 515)
            for person in simulate(seed)[1]["traces"]
            for session in person["sessions"].values()
        ]
        events = [event for session in sessions for event in session["events"]]
        for phase in ("backtrack", "replacement_browse", "replacement_review", "budget_swap"):
            self.assertTrue(any(event["phase"] == phase for event in events), phase)
        self.assertTrue(any(event.get("long_wait") for event in events))
        self.assertTrue(any(session["valid_meals"] < 7 for session in sessions))

    def test_cli_reproduces_all_saved_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "simulation.json"
            sweep = Path(directory) / "sensitivity.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/simulate_m0.py"),
                    "--trace",
                    str(trace),
                    "--sensitivity-output",
                    str(sweep),
                ],
                capture_output=True,
                check=True,
            )
            self.assertEqual(result.stdout, (ROOT / "evals/m0/synthetic.csv").read_bytes())
            for actual in (trace, sweep):
                self.assertEqual(
                    actual.read_bytes(), (ROOT / "evals/m0" / actual.name).read_bytes()
                )
            report = json.loads(sweep.read_text())
            self.assertEqual([run["seed"] for run in report["runs"]], list(range(510, 515)))
            self.assertEqual(
                report["passes"], sum(run["verdict"] == "PASS" for run in report["runs"])
            )
            self.assertEqual(report, sensitivity())

    def test_invalid_population_and_impossible_catalog_fail(self):
        with self.assertRaises(ValueError):
            simulate(participants=0)
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.csv"
            catalog.write_text(
                "item_id,name,cuisine,price_cents,allergens,vegetarian\n1,Expensive,Any,20000,,true\n"
            )
            with self.assertRaisesRegex(ValueError, "seven-meal budget"):
                simulate(catalog_path=catalog)
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/simulate_m0.py"), "--catalog", str(catalog)],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
