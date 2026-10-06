import json
from unittest.mock import Mock

import pandas as pd
import pytest

from proj2.menu_generation import DAYS_OF_WEEK, MenuGenerator
from proj2.meal_budget import BudgetExceededError


@pytest.fixture
def generator():
    gen = MenuGenerator.__new__(MenuGenerator)
    gen.menu_items = pd.DataFrame(
        [
            {
                "itm_id": item,
                "rtr_id": 1,
                "name": f"Meal {item}",
                "description": "Dinner",
                "price": price,
                "calories": 500,
                "instock": 1,
                "allergens": "",
            }
            for item, price in [(1, 1000), (2, 500), (3, 500)]
        ]
    )
    gen.restaurants = pd.DataFrame(
        [{"rtr_id": 1, "hours": json.dumps({day: [0, 2359] for day in DAYS_OF_WEEK})}]
    )
    gen.generator = Mock()
    gen.item_prices = dict(zip(gen.menu_items.itm_id, gen.menu_items.price))
    return gen


def test_rank_affordable_candidates_including_exact_limit(generator):
    candidates = generator._eligible_candidates("", "Mon", 2000, 500)
    assert candidates.itm_id.tolist() == [2, 3]
    assert generator._eligible_candidates("", "Mon", 2000, 499).empty


def test_eligibility_rejects_stock_allergens_missing_restaurants_and_bad_prices(generator):
    generator.menu_items.loc[0, "allergens"] = " Peanuts, MILK "
    generator.menu_items.loc[1, "instock"] = 0
    generator.menu_items.loc[2, "rtr_id"] = 99
    assert generator._eligible_candidates("milk", "Mon", 2000).empty
    generator.menu_items.loc[1, "instock"] = 1
    generator.menu_items.loc[1, "price"] = -1
    assert generator._eligible_candidates("milk", "Mon", 2000).empty


@pytest.mark.parametrize("hours", ['{"Mon": []}', "bad json", '{"Tue": [0, 2359]}'])
def test_unavailable_hours_exclude_candidates(generator, hours):
    generator.restaurants.loc[0, "hours"] = hours
    assert generator._eligible_candidates("", "Mon", 2000).empty


def test_picker_only_accepts_an_affordable_offered_item(generator):
    candidates = generator._eligible_candidates("", "Mon", 2000, 500)
    generator.generator.generate.side_effect = [
        "<|start_of_role|>assistant<|end_of_role|>1<|end_of_text|>",
        "<|start_of_role|>assistant<|end_of_role|>3<|end_of_text|>",
    ]
    assert generator._MenuGenerator__pick_menu_item("", "", "Mon", 3, candidates) == 3
    for call in generator.generator.generate.call_args_list:
        prompt = call.args[1]
        assert "1,Meal 1" not in prompt
        assert prompt.index("2,Meal 2") < prompt.index("3,Meal 3")


def test_empty_candidates_fail_before_model_generation(generator):
    candidates = generator._eligible_candidates("", "Mon", 2000, 499)
    with pytest.raises(RuntimeError, match="No eligible"):
        generator._MenuGenerator__pick_menu_item("", "", "Mon", 3, candidates)
    generator.generator.generate.assert_not_called()


def generate(generator, **overrides):
    args = dict(
        menu="",
        preferences="",
        allergens="",
        date="2026-10-05",
        meal_numbers=[3],
        number_of_days=2,
        weekly_cap_cents=1000,
    )
    args.update(overrides)
    return generator.update_menu(**args)


def test_plan_fits_exact_cap_and_reserves_later_meals(generator):
    generator.generator.generate.return_value = (
        "<|start_of_role|>assistant<|end_of_role|>2<|end_of_text|>"
    )
    assert generate(generator) == "[2026-10-05,2,3],[2026-10-06,2,3]"
    assert generator.item_total_cents == 1000
    assert generator.weekly_totals_cents == {"2026-10-05": 1000}
    assert all(
        "1,Meal 1" not in call.args[1] for call in generator.generator.generate.call_args_list
    )


def test_impossible_budget_is_rejected_before_generation(generator):
    with pytest.raises(BudgetExceededError, match=r"needs at least \$10.00"):
        generate(generator, weekly_cap_cents=999)
    generator.generator.generate.assert_not_called()


def test_existing_meals_outside_requested_dates_consume_weekly_budget(generator):
    # Sunday's saved dinner still belongs to the week of the Monday request.
    existing = "[2026-10-11,1,3]"
    with pytest.raises(BudgetExceededError, match=r"needs at least \$20.00"):
        generate(generator, menu=existing)
    generator.generator.generate.assert_not_called()
    assert existing == "[2026-10-11,1,3]"


def test_each_calendar_week_has_its_own_cap(generator):
    generator.generator.generate.return_value = (
        "<|start_of_role|>assistant<|end_of_role|>2<|end_of_text|>"
    )
    generate(generator, date="2026-10-11", weekly_cap_cents=500)
    assert generator.weekly_totals_cents == {"2026-10-05": 500, "2026-10-12": 500}


def test_existing_legacy_dinner_is_preserved_and_counted_once(generator):
    existing = "[2026-10-05,2]"
    assert generate(generator, menu=existing, number_of_days=1, weekly_cap_cents=500) == existing
    assert generator.item_total_cents == 500
    generator.generator.generate.assert_not_called()
