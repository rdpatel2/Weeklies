"""
Unit tests for the allergen and opening-hours helpers in proj2/meal_swap.py.

These helpers intentionally duplicate the rules in menu_generation.filter_allergens and
menu_generation.filter_closed_restaurants, so the equivalence tests below check that a
single-item swap check and the generator's DataFrame filters always agree.
"""

import json

import pandas as pd
import pytest

from proj2.meal_swap import is_restaurant_open, parse_allergens
from proj2.menu_generation import filter_allergens, filter_closed_restaurants


class TestParseAllergens:
    def test_strips_and_casefolds(self):
        assert parse_allergens("Gluten, Soy ,SESAME") == {"gluten", "soy", "sesame"}

    def test_drops_empty_entries(self):
        assert parse_allergens("Peanuts,, ,") == {"peanuts"}

    @pytest.mark.parametrize("value", [None, "", float("nan")])
    def test_missing_values(self, value):
        assert parse_allergens(value) == set()


class TestIsRestaurantOpen:
    @staticmethod
    def hours(times):
        return json.dumps({"Mon": times})

    def test_open_within_window(self):
        assert is_restaurant_open(self.hours([1000, 2000]), "Mon", 1200) is True

    def test_open_on_boundaries(self):
        assert is_restaurant_open(self.hours([1000, 2000]), "Mon", 1000) is True
        assert is_restaurant_open(self.hours([1000, 2000]), "Mon", 2000) is True

    def test_open_in_second_window(self):
        assert is_restaurant_open(self.hours([800, 1100, 1700, 2200]), "Mon", 2000) is True

    def test_closed_between_windows(self):
        assert is_restaurant_open(self.hours([800, 1100, 1700, 2200]), "Mon", 1400) is False

    def test_closed_when_no_hours(self):
        assert is_restaurant_open(self.hours([]), "Mon", 1200) is False

    def test_closed_when_odd_times(self):
        assert is_restaurant_open(self.hours([1000, 2000, 2100]), "Mon", 1200) is False

    @pytest.mark.parametrize(
        "hours",
        ["9-21", "", None, json.dumps({"Tue": [1000, 2000]}), json.dumps({"Mon": ["10", "20"]})],
    )
    def test_unparseable_missing_day_or_non_numeric_is_closed(self, hours):
        assert is_restaurant_open(hours, "Mon", 1400) is False


## Item allergen values and user allergy strings covering spacing, case, empty and missing values
ITEM_ALLERGENS = ["Gluten, Soy", "Dairy, Coconut", "peanuts", "", None, float("nan"), "Fish ,SESAME"]
USER_ALLERGIES = ["", "soy", " Coconut ", "PEANUTS, fish", "sesame,gluten", None]


@pytest.mark.parametrize("user_allergies", USER_ALLERGIES)
def test_allergen_rules_match_generator_filter(user_allergies):
    items = pd.DataFrame({"itm_id": range(len(ITEM_ALLERGENS)), "allergens": ITEM_ALLERGENS})
    kept_by_generator = set(filter_allergens(items, user_allergies)["itm_id"])

    blocked = parse_allergens(user_allergies)
    kept_by_swap = {
        i for i, value in enumerate(ITEM_ALLERGENS) if not (parse_allergens(value) & blocked)
    }
    assert kept_by_swap == kept_by_generator


## Restaurant hours covering open, closed, multi-window, empty, odd, non-numeric and malformed
RESTAURANT_HOURS = [
    json.dumps({"Mon": [1000, 2000]}),
    json.dumps({"Mon": [1700, 2200]}),
    json.dumps({"Mon": [800, 1100, 1700, 2200]}),
    json.dumps({"Mon": []}),
    json.dumps({"Mon": [1000, 2000, 2100]}),
    json.dumps({"Mon": ["10", "20"]}),
    json.dumps({"Tue": [1000, 2000]}),
    "9-21",
]


@pytest.mark.parametrize("time", [800, 1000, 1400, 2000, 2300])
def test_hours_rules_match_generator_filter(time):
    restaurants = pd.DataFrame({"rtr_id": range(len(RESTAURANT_HOURS)), "hours": RESTAURANT_HOURS})
    kept_by_generator = set(filter_closed_restaurants(restaurants, "Mon", time)["rtr_id"])

    kept_by_swap = {
        i for i, hours in enumerate(RESTAURANT_HOURS) if is_restaurant_open(hours, "Mon", time)
    }
    assert kept_by_swap == kept_by_generator
