"""Check the decision boundary, unhelpful outcomes, and corrupt evidence."""

import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval_m0 import FIELDS, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def dataset(**overrides):
    rows = []
    for index in range(5):
        row = {
            "participant_id": f"p{index}",
            "data_kind": "synthetic",
            "baseline_first": "true",
            "baseline_seconds": "1000",
            "baseline_valid_meals": "7",
            "weeklies_seconds": "700",
            "weeklies_valid_meals": "7",
            "budget_cents": "10000",
            "baseline_cost_cents": "11000",
            "weeklies_cost_cents": "9000",
            "evidence_ref": "test",
        }
        row.update(overrides)
        rows.append(row)
    return rows


def encode(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


class EvaluationTests(unittest.TestCase):
    def test_threshold_and_slower_outcomes(self):
        self.assertEqual(evaluate(encode(dataset()))["verdict"], "PASS")
        for seconds in ("701", "1000", "1100"):
            with self.subTest(seconds=seconds):
                self.assertEqual(
                    evaluate(encode(dataset(weeklies_seconds=seconds)))["verdict"], "FAIL"
                )

    def test_incomplete_sessions_are_retained_and_penalized(self):
        rows = dataset(weeklies_seconds="100")
        rows[0]["weeklies_valid_meals"] = "0"
        report = evaluate(encode(rows))
        self.assertEqual(report["completion_rate"]["weeklies"], 0.8)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["pairs"][0]["weeklies_scored_seconds"], 1200)
        self.assertFalse(report["pairs"][0]["weeklies_within_budget"])
        rows[1]["weeklies_valid_meals"] = "6"
        self.assertEqual(evaluate(encode(rows))["verdict"], "FAIL")
        rows = dataset(baseline_valid_meals="6", weeklies_seconds="100")
        self.assertEqual(evaluate(encode(rows))["verdict"], "FAIL")

    def test_paired_reduction_is_not_ratio_of_medians(self):
        rows = dataset()
        for row, baseline, weeklies in zip(rows, [100, 200, 400, 800, 1000], [90, 20, 360, 80, 900]):
            row.update(baseline_seconds=str(baseline), weeklies_seconds=str(weeklies))
        self.assertAlmostEqual(evaluate(encode(rows))["median_reduction"], 0.1)

    def test_too_few_pairs_cannot_pass(self):
        self.assertEqual(evaluate(encode(dataset()[:4]))["verdict"], "FAIL")

    def test_budget_thresholds_and_exact_cost_boundary(self):
        rows = dataset(weeklies_cost_cents="10000")
        for row in rows[:3]:
            row["baseline_cost_cents"] = "10000"
        rows[-1]["weeklies_cost_cents"] = "10001"
        report = evaluate(encode(rows))
        self.assertEqual(report["budget_success_rate"], {"baseline": 0.6, "weeklies": 0.8})
        self.assertEqual(report["budget_lift_percentage_points"], 20)
        self.assertEqual(report["verdict"], "PASS")
        rows[3]["baseline_cost_cents"] = "10000"
        self.assertFalse(evaluate(encode(rows))["checks"]["budget_lift"])
        rows = dataset()
        rows[0]["weeklies_cost_cents"] = "10001"
        rows[1]["weeklies_cost_cents"] = "10001"
        report = evaluate(encode(rows))
        self.assertTrue(report["checks"]["budget_lift"])
        self.assertFalse(report["checks"]["weeklies_budget_success"])
        self.assertEqual(report["verdict"], "FAIL")

    def test_incomplete_free_plan_cannot_count_as_budget_success(self):
        report = evaluate(encode(dataset(weeklies_valid_meals="0", weeklies_cost_cents="0")))
        self.assertEqual(report["budget_success_rate"]["weeklies"], 0)
        self.assertEqual(report["verdict"], "FAIL")

    def test_bad_evidence_is_rejected(self):
        for changes in (
            {"weeklies_seconds": "nan"},
            {"weeklies_seconds": "inf"},
            {"baseline_seconds": "0"},
            {"weeklies_seconds": "1201"},
            {"weeklies_seconds": "-1"},
            {"weeklies_valid_meals": "8"},
            {"baseline_valid_meals": "1.5"},
            {"baseline_first": "yes"},
            {"data_kind": "real-ish"},
            {"evidence_ref": ""},
            {"participant_id": "duplicate"},
            {"budget_cents": "0"},
            {"budget_cents": "-100"},
            {"budget_cents": "nan"},
            {"baseline_cost_cents": "-1"},
            {"weeklies_cost_cents": "0"},
            {"weeklies_cost_cents": "9000.50"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                evaluate(encode(dataset(**changes)))
        with self.assertRaises(ValueError):
            evaluate(encode([]))
        rows = dataset()
        rows[0]["data_kind"] = "pilot"
        with self.assertRaises(ValueError):
            evaluate(encode(rows))
        with self.assertRaises(ValueError):
            evaluate(b"wrong,columns\n1,2\n")
        with self.assertRaises(ValueError):
            evaluate(encode(dataset()) + b"missing,cells\n")

    def test_pilot_uses_the_same_policy(self):
        report = evaluate(encode(dataset(data_kind="pilot")))
        self.assertEqual(report["data_kind"], "pilot")
        self.assertEqual(report["verdict"], "PASS")

    def test_cli_exit_codes_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.csv"
            output = Path(directory) / "result.json"
            for data, expected in (
                (encode(dataset()), 0),
                (encode(dataset(weeklies_seconds="1100")), 1),
                (b"broken", 2),
            ):
                source.write_bytes(data)
                output.unlink(missing_ok=True)
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/eval_m0.py"), str(source),
                     "--output", str(output)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected != 2:
                    self.assertEqual(json.loads(result.stdout), json.loads(output.read_text()))
                else:
                    self.assertFalse(output.exists())

    def test_checked_in_demo_is_reproducible(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/simulate_m0.py")],
            capture_output=True, check=True,
        )
        data = (ROOT / "evals/m0/synthetic.csv").read_bytes()
        self.assertEqual(result.stdout, data)
        report = evaluate(data)
        self.assertEqual(report, json.loads((ROOT / "evals/m0/result.json").read_text()))
        self.assertEqual(report["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
