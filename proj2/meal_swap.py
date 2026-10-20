"""
Single-meal swaps: replace one date/meal slot of a user's generated menu.

The generated menu is stored on the User row as a string of entries like
"[YYYY-MM-DD,itm_id,meal]" where meal is 1 (breakfast), 2 (lunch) or 3 (dinner).
Legacy entries without a meal number are treated as dinner, matching
Flask_app.parse_generated_menu.
"""

import re

## Matches one menu entry; the meal number is optional for legacy entries
SLOT_PATTERN = re.compile(r"\[\s*(\d{4}-\d{2}-\d{2})\s*,\s*([0-9]+)\s*(?:,\s*([123])\s*)?\]")

## Meal number assumed for entries that do not store one
DEFAULT_MEAL = 3


class SlotNotFoundError(LookupError):
    """Raised when the requested date/meal slot is not in the user's menu"""

    pass


def find_slot_item(menu: str, date: str, meal: int):
    """
    Finds the item currently planned for a date/meal slot

    Args:
        menu (str): The generated menu string (can be empty or None)
        date (str): The slot date in YYYY-MM-DD format
        meal (int): The slot meal number (1, 2, or 3)

    Returns:
        int | None: The planned itm_id, or None if the slot is empty
    """
    for match in SLOT_PATTERN.finditer(menu or ""):
        d, itm_id, m = match.groups()
        if d == date and int(m or DEFAULT_MEAL) == meal:
            return int(itm_id)
    return None


def replace_menu_slot(menu: str, date: str, meal: int, new_itm_id: int) -> str:
    """
    Replaces the item in one date/meal slot, leaving every other entry untouched

    Args:
        menu (str): The generated menu string
        date (str): The slot date in YYYY-MM-DD format
        meal (int): The slot meal number (1, 2, or 3)
        new_itm_id (int): The replacement menu item ID

    Returns:
        str: The menu string with only the matching slot rewritten as "[date,new_itm_id,meal]"

    Raises:
        SlotNotFoundError: if the menu has no entry for that date/meal
    """
    found = False

    def _swap(match):
        nonlocal found
        d, _, m = match.groups()
        if d == date and int(m or DEFAULT_MEAL) == meal:
            found = True
            return f"[{date},{int(new_itm_id)},{meal}]"
        return match.group(0)

    updated = SLOT_PATTERN.sub(_swap, menu or "")
    if not found:
        raise SlotNotFoundError(f"No planned meal {meal} on {date}")
    return updated
