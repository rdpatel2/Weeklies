import json
from unittest.mock import Mock

import pandas as pd
import pytest

from proj2.menu_generation import DAYS_OF_WEEK, MenuGenerator


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
