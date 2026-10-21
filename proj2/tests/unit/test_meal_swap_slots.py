"""
Unit tests for the menu-string slot helpers in proj2/meal_swap.py
"""

import pytest

from proj2.Flask_app import parse_generated_menu
from proj2.meal_swap import SlotNotFoundError, find_slot_item, replace_menu_slot

MENU = "[2025-11-05,10,1],[2025-11-05,11,2],[2025-11-05,12,3],[2025-11-06,13,1]"


class TestFindSlotItem:
    def test_finds_planned_item(self):
        assert find_slot_item(MENU, "2025-11-05", 2) == 11

    def test_empty_slot_returns_none(self):
        assert find_slot_item(MENU, "2025-11-06", 3) is None

    def test_empty_menu_returns_none(self):
        assert find_slot_item("", "2025-11-05", 1) is None
        assert find_slot_item(None, "2025-11-05", 1) is None

    def test_legacy_entry_defaults_to_dinner(self):
        assert find_slot_item("[2025-11-05,42]", "2025-11-05", 3) == 42
        assert find_slot_item("[2025-11-05,42]", "2025-11-05", 1) is None


class TestReplaceMenuSlot:
    def test_replaces_only_target_slot(self):
        updated = replace_menu_slot(MENU, "2025-11-05", 2, 99)
        assert updated == "[2025-11-05,10,1],[2025-11-05,99,2],[2025-11-05,12,3],[2025-11-06,13,1]"

    def test_other_slots_stay_intact(self):
        before = parse_generated_menu(MENU)
        after = parse_generated_menu(replace_menu_slot(MENU, "2025-11-05", 3, 77))

        assert after["2025-11-06"] == before["2025-11-06"]
        same_day_others = [e for e in after["2025-11-05"] if e["meal"] != 3]
        assert same_day_others == [e for e in before["2025-11-05"] if e["meal"] != 3]
        assert {"itm_id": 77, "meal": 3} in after["2025-11-05"]

    def test_same_item_different_day_not_touched(self):
        menu = "[2025-11-05,10,1],[2025-11-06,10,1]"
        assert replace_menu_slot(menu, "2025-11-06", 1, 5) == "[2025-11-05,10,1],[2025-11-06,5,1]"

    def test_preserves_separator_style(self):
        menu = "[2025-11-05,10,1][2025-11-05,11,2]"
        assert replace_menu_slot(menu, "2025-11-05", 1, 3) == "[2025-11-05,3,1][2025-11-05,11,2]"

    def test_legacy_entry_rewritten_with_explicit_meal(self):
        menu = "[2025-11-05,42],[2025-11-05,10,1]"
        assert replace_menu_slot(menu, "2025-11-05", 3, 7) == "[2025-11-05,7,3],[2025-11-05,10,1]"

    def test_missing_slot_raises(self):
        with pytest.raises(SlotNotFoundError):
            replace_menu_slot(MENU, "2025-11-06", 2, 5)

    def test_empty_menu_raises(self):
        with pytest.raises(SlotNotFoundError):
            replace_menu_slot("", "2025-11-05", 1, 5)
