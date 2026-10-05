"""UC13 extension: order progress stepper — unit tests for proj2/order_progress.py.

Pure-function tests (no DB, no Flask): every lifecycle status maps to the right
stage, and bad/unknown status values degrade instead of raising.
"""
import pytest
from proj2.order_progress import STAGES, normalize_status, order_progress

STAGE_KEYS = [k for k, _ in STAGES]


# ---- Expected cases: each lifecycle stage ----

@pytest.mark.parametrize("status,index", [
    ("Ordered", 0), ("Accepted", 1), ("Preparing", 2), ("Ready", 3), ("Delivered", 4),
])
def test_stage_is_current(status, index):
    p = order_progress(status)
    assert p["key"] == status.lower()
    assert p["label"] == status
    assert p["known"] is True
    assert p["cancelled"] is False
    assert [s["state"] for s in p["steps"]].index("current") == index


@pytest.mark.parametrize("status,index", [
    ("Ordered", 0), ("Accepted", 1), ("Preparing", 2), ("Ready", 3), ("Delivered", 4),
])
def test_earlier_stages_done_later_upcoming(status, index):
    states = [s["state"] for s in order_progress(status)["steps"]]
    assert states[:index] == ["done"] * index
    assert states[index + 1:] == ["upcoming"] * (len(STAGES) - index - 1)


@pytest.mark.parametrize("status,percent", [
    ("Ordered", 0), ("Accepted", 25), ("Preparing", 50), ("Ready", 75), ("Delivered", 100),
])
def test_percent_progress(status, percent):
    assert order_progress(status)["percent"] == percent


def test_exactly_one_current_step():
    for key, label in STAGES:
        states = [s["state"] for s in order_progress(label)["steps"]]
        assert states.count("current") == 1, key


def test_steps_follow_lifecycle_order():
    p = order_progress("Preparing")
    assert [s["key"] for s in p["steps"]] == STAGE_KEYS
    assert [s["label"] for s in p["steps"]] == ["Ordered", "Accepted", "Preparing", "Ready", "Delivered"]


def test_delivered_has_no_upcoming():
    states = [s["state"] for s in order_progress("Delivered")["steps"]]
    assert "upcoming" not in states


# ---- Cancelled side-exit ----

def test_cancelled_flags():
    p = order_progress("Cancelled")
    assert p["key"] == "cancelled"
    assert p["label"] == "Cancelled"
    assert p["cancelled"] is True
    assert p["known"] is True


def test_cancelled_has_no_current_or_done_step():
    """No history table, so we must not claim the order reached any stage."""
    states = {s["state"] for s in order_progress("Cancelled")["steps"]}
    assert states == {"cancelled"}


def test_cancelled_percent_zero():
    assert order_progress("Cancelled")["percent"] == 0


def test_us_spelling_canceled_maps_to_cancelled():
    assert order_progress("Canceled")["key"] == "cancelled"


# ---- Normalization ----

@pytest.mark.parametrize("raw", ["ready", "READY", " Ready ", "rEaDy\n"])
def test_case_and_whitespace_insensitive(raw):
    p = order_progress(raw)
    assert p["key"] == "ready"
    assert p["label"] == "Ready"


@pytest.mark.parametrize("raw,expected", [
    (None, ""), ("", ""), ("   ", ""), ("Ordered", "ordered"), (" CANCELED ", "cancelled"), (3, "3"),
])
def test_normalize_status(raw, expected):
    assert normalize_status(raw) == expected


# ---- Failure cases: unknown / missing status degrades gracefully ----

@pytest.mark.parametrize("raw", [None, "", "   "])
def test_missing_status_is_unknown(raw):
    p = order_progress(raw)
    assert p["key"] == "unknown"
    assert p["label"] == "Unknown"
    assert p["known"] is False


@pytest.mark.parametrize("raw", ["Pending", "Shipped", "Refunded", "Out for delivery"])
def test_unrecognized_status_keeps_raw_label(raw):
    p = order_progress(raw)
    assert p["key"] == "unknown"
    assert p["label"] == raw
    assert p["known"] is False
    assert p["cancelled"] is False


def test_unknown_status_has_no_current_step():
    states = {s["state"] for s in order_progress("Shipped")["steps"]}
    assert states == {"upcoming"}
    assert order_progress("Shipped")["percent"] == 0


@pytest.mark.parametrize("raw", [0, 42, 3.5, b"Ready", ["Ready"]])
def test_non_string_status_does_not_raise(raw):
    p = order_progress(raw)
    assert p["known"] is False
    assert len(p["steps"]) == len(STAGES)


def test_unknown_label_is_trimmed():
    assert order_progress("  Shipped  ")["label"] == "Shipped"


def test_markup_in_status_is_returned_unchanged():
    """Escaping is the template's job (Jinja autoescape); the helper must not mangle it."""
    raw = "<script>alert(1)</script>"
    assert order_progress(raw)["label"] == raw


def test_returns_fresh_steps_each_call():
    a = order_progress("Ready")
    a["steps"][0]["state"] = "mutated"
    assert order_progress("Ready")["steps"][0]["state"] == "done"
