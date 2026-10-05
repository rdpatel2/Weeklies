"""Customer-facing order progress (UC13 extension).

Maps the single `status` column on "Order" onto the lifecycle stages so the
profile page can draw a stepper instead of one status word.

Lifecycle (driven by the restaurant routes in Flask_app.py):
    Ordered -> Accepted -> Preparing -> Ready -> Delivered
Cancelled is a side-exit reachable from Ordered/Accepted/Preparing.

There is no status-history table, so for a Cancelled order we cannot tell
which stage it reached before being cancelled; every stage is shown as
"cancelled" rather than guessing.
"""

STAGES = [
    ("ordered", "Ordered"),
    ("accepted", "Accepted"),
    ("preparing", "Preparing"),
    ("ready", "Ready"),
    ("delivered", "Delivered"),
]

_STAGE_INDEX = {key: i for i, (key, _label) in enumerate(STAGES)}

# Accept the US spelling too, in case it is ever written by hand or a seed script.
_ALIASES = {"canceled": "cancelled"}


def normalize_status(status):
    """
    Normalize a raw status value to a lowercase key.
    Args:
        status: Raw value from the "Order".status column (may be None).
    Returns:
        str: Lowercase, trimmed key ("" for None/blank).
    """
    if status is None:
        return ""
    key = str(status).strip().lower()
    return _ALIASES.get(key, key)


def order_progress(status):
    """
    Build the stepper view model for one order.
    Args:
        status: Raw value from the "Order".status column (may be None/unknown).
    Returns:
        dict: {
            "key": normalized status key, or "unknown",
            "label": text for the status badge,
            "known": False when the status is not part of the lifecycle,
            "cancelled": True for Cancelled orders,
            "percent": 0-100 progress through the lifecycle,
            "steps": [{"key", "label", "state"}] where state is
                     "done" | "current" | "upcoming" | "cancelled",
        }
    """
    key = normalize_status(status)

    if key == "cancelled":
        return {
            "key": "cancelled",
            "label": "Cancelled",
            "known": True,
            "cancelled": True,
            "percent": 0,
            "steps": [{"key": k, "label": lbl, "state": "cancelled"} for k, lbl in STAGES],
        }

    if key in _STAGE_INDEX:
        current = _STAGE_INDEX[key]
        steps = []
        for i, (k, lbl) in enumerate(STAGES):
            if i < current:
                state = "done"
            elif i == current:
                state = "current"
            else:
                state = "upcoming"
            steps.append({"key": k, "label": lbl, "state": state})
        return {
            "key": key,
            "label": STAGES[current][1],
            "known": True,
            "cancelled": False,
            "percent": round(100 * current / (len(STAGES) - 1)),
            "steps": steps,
        }

    # Unknown, blank or NULL status: degrade to a neutral badge, no stepper position.
    raw = "" if status is None else str(status).strip()
    return {
        "key": "unknown",
        "label": raw or "Unknown",
        "known": False,
        "cancelled": False,
        "percent": 0,
        "steps": [{"key": k, "label": lbl, "state": "upcoming"} for k, lbl in STAGES],
    }
