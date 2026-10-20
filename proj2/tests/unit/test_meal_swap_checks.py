"""
Unit tests for the availability and allergen checks in proj2/meal_swap.py
"""

import json
import sqlite3

import pytest

from proj2.meal_swap import (
    list_swap_options,
    load_swap_item,
    slot_weekday_and_time,
    swap_rejection,
)

## 2025-11-03 is a Monday; lunch (meal 2) is checked at 1400
MONDAY = "2025-11-03"
ALL_WEEK = json.dumps({d: [800, 2200] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]})
DINNER_ONLY = json.dumps({d: [1700, 2200] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]})


def make_item(**overrides):
    item = {
        "itm_id": 1,
        "rtr_id": 1,
        "name": "Pho",
        "instock": 1,
        "allergens": "Gluten, Soy",
        "restaurant_status": "Open",
        "hours": ALL_WEEK,
    }
    item.update(overrides)
    return item


class TestSlotWeekdayAndTime:
    def test_maps_date_and_meal(self):
        assert slot_weekday_and_time(MONDAY, 1) == ("Mon", 1000)
        assert slot_weekday_and_time("2025-11-09", 3) == ("Sun", 2000)

    @pytest.mark.parametrize("date,meal", [("2025-13-01", 1), ("not-a-date", 1), (MONDAY, 4)])
    def test_invalid_slot_raises(self, date, meal):
        with pytest.raises(ValueError):
            slot_weekday_and_time(date, meal)


class TestSwapRejection:
    def test_eligible_item_passes(self):
        assert swap_rejection(make_item(), "Peanuts", MONDAY, 2) is None

    def test_missing_item(self):
        assert swap_rejection(None, "", MONDAY, 2)[0] == "item_not_found"

    def test_out_of_stock(self):
        assert swap_rejection(make_item(instock=0), "", MONDAY, 2)[0] == "out_of_stock"

    @pytest.mark.parametrize("status", ["Closed", "", None])
    def test_restaurant_not_open_status(self, status):
        code, _ = swap_rejection(make_item(restaurant_status=status), "", MONDAY, 2)
        assert code == "restaurant_unavailable"

    def test_restaurant_status_case_insensitive(self):
        assert swap_rejection(make_item(restaurant_status="open"), "", MONDAY, 2) is None

    def test_restaurant_closed_at_meal_time(self):
        item = make_item(hours=DINNER_ONLY)
        assert swap_rejection(item, "", MONDAY, 2)[0] == "restaurant_closed"
        assert swap_rejection(item, "", MONDAY, 3) is None

    def test_malformed_hours_treated_as_closed(self):
        assert swap_rejection(make_item(hours="9-21"), "", MONDAY, 2)[0] == "restaurant_closed"

    def test_allergen_conflict(self):
        code, message = swap_rejection(make_item(), "soy", MONDAY, 2)
        assert code == "allergen"
        assert "soy" in message

    def test_allergen_check_ignores_spacing(self):
        assert swap_rejection(make_item(allergens="Dairy, Coconut"), " Coconut ", MONDAY, 2)[0] == "allergen"

    def test_item_without_allergens(self):
        assert swap_rejection(make_item(allergens=None), "Peanuts", MONDAY, 2) is None


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(
        """
        CREATE TABLE Restaurant (rtr_id INTEGER PRIMARY KEY, name TEXT, status TEXT, hours TEXT);
        CREATE TABLE MenuItem (itm_id INTEGER PRIMARY KEY, rtr_id INTEGER, name TEXT,
                               instock INTEGER, allergens TEXT);
        """
    )
    c.execute("INSERT INTO Restaurant VALUES (1, 'Open All Day', 'Open', ?)", (ALL_WEEK,))
    c.execute("INSERT INTO Restaurant VALUES (2, 'Dinner Spot', 'Open', ?)", (DINNER_ONLY,))
    c.execute("INSERT INTO Restaurant VALUES (3, 'Shut', 'Closed', ?)", (ALL_WEEK,))
    c.executemany(
        "INSERT INTO MenuItem VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, "Current", 1, ""),
            (2, 1, "Peanut Noodles", 1, "Peanuts"),
            (3, 1, "Rice Bowl", 1, "Soy"),
            (4, 1, "Sold Out", 0, ""),
            (5, 2, "Steak", 1, ""),
            (6, 3, "Closed Soup", 1, ""),
        ],
    )
    yield c
    c.close()


class TestLoadSwapItem:
    def test_loads_item_with_restaurant_fields(self, conn):
        item = load_swap_item(conn, 5)
        assert item["name"] == "Steak"
        assert item["rtr_id"] == 2
        assert item["restaurant_status"] == "Open"
        assert item["hours"] == DINNER_ONLY

    def test_unknown_item(self, conn):
        assert load_swap_item(conn, 999) is None


class TestListSwapOptions:
    def test_lunch_options_respect_all_checks(self, conn):
        options = list_swap_options(conn, "peanuts", MONDAY, 2, exclude_itm_id=1)
        assert [o["itm_id"] for o in options] == [3]

    def test_dinner_includes_dinner_only_restaurant(self, conn):
        options = list_swap_options(conn, "", MONDAY, 3)
        assert [o["itm_id"] for o in options] == [1, 2, 3, 5]

    def test_every_option_passes_rejection_check(self, conn):
        for option in list_swap_options(conn, "soy", MONDAY, 3):
            assert swap_rejection(option, "soy", MONDAY, 3) is None
