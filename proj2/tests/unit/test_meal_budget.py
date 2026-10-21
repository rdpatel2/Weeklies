import pytest

from proj2.meal_budget import parse_weekly_cap, weekly_item_totals, week_start


@pytest.mark.parametrize("value, expected", [(None, None), ("", None), ("10.01", 1001), (0, 0)])
def test_parse_cap_in_exact_cents(value, expected):
    assert parse_weekly_cap(value) == expected


@pytest.mark.parametrize("value", ["-1", "1.001", "NaN", "Infinity", True, "oops"])
def test_reject_invalid_cap(value):
    with pytest.raises(ValueError, match="Weekly cap"):
        parse_weekly_cap(value)


def test_week_boundary_and_repeated_saved_servings():
    menu = "[2026-12-27,1,3],[2026-12-28,1,1],[2027-01-01,1,3],[2027-01-03,2]"
    assert week_start("2027-01-03") == "2026-12-28"
    assert weekly_item_totals(menu, {1: 1001, 2: 499}) == {
        "2026-12-21": 1001,
        "2026-12-28": 2501,
    }


def test_only_requested_weeks_require_known_prices():
    menu = "[2026-10-04,99,3],[2026-10-05,1,3]"
    assert weekly_item_totals(menu, {1: 500}, ["2026-10-05"]) == {"2026-10-05": 500}
    with pytest.raises(ValueError, match="no longer in the catalog"):
        weekly_item_totals(menu, {1: 500})
