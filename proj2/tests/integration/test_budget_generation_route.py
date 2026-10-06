import json
import sqlite3
from unittest.mock import Mock

import pytest

from proj2.menu_generation import DAYS_OF_WEEK, MenuGenerator


@pytest.fixture
def budget_catalog(app, temp_db_path, seed_minimal_data, monkeypatch):
    """Use a temporary catalog and fake only model output, not budget calculations."""
    snapshot = sqlite3.connect(":memory:")
    with sqlite3.connect(temp_db_path) as conn:
        conn.backup(snapshot)
        restaurant = seed_minimal_data["rtr_id"]
        conn.execute(
            'UPDATE Restaurant SET hours=?, status="Open" WHERE rtr_id=?',
            (json.dumps({day: [0, 2359] for day in DAYS_OF_WEEK}), restaurant),
        )
        conn.execute(
            'UPDATE "User" SET generated_menu="" WHERE usr_id=?', (seed_minimal_data["usr_id"],)
        )
        item = conn.execute(
            "SELECT itm_id FROM MenuItem WHERE rtr_id=? ORDER BY itm_id LIMIT 1", (restaurant,)
        ).fetchone()[0]
        conn.execute("UPDATE MenuItem SET instock=0")
        conn.execute(
            'UPDATE MenuItem SET price=500, instock=1, allergens="" WHERE itm_id=?', (item,)
        )
    llm = Mock()
    llm.generate.return_value = f"<|start_of_role|>assistant<|end_of_role|>{item}<|end_of_text|>"
    monkeypatch.setattr("proj2.menu_generation.llm_toolkit.LLM", Mock(return_value=llm))
    yield item, llm
    with sqlite3.connect(temp_db_path) as conn:
        snapshot.backup(conn)
    snapshot.close()


def test_generator_uses_supplied_catalog_and_keeps_prices_for_unavailable_items(
    budget_catalog, temp_db_path
):
    gen = MenuGenerator(database_path=temp_db_path)
    assert gen.menu_items.itm_id.tolist() == [budget_catalog[0]]
    assert gen.item_prices[budget_catalog[0]] == 500
    assert len(gen.item_prices) > len(gen.menu_items)
