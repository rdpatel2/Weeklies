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


def payload(**overrides):
    data = {
        "start_date": "2026-10-05",
        "meal_numbers": [3],
        "number_of_days": 2,
        "weekly_cap": "10.00",
    }
    data.update(overrides)
    return data


def test_exact_limit_json_returns_totals_and_saves_plan(
    client, login_session, budget_catalog, temp_db_path
):
    response = client.post("/menu/generate", json=payload())
    assert response.status_code == 200
    data = response.get_json()
    assert data["weekly_cap_cents"] == data["item_total_cents"] == 1000
    assert data["weekly_item_totals_cents"] == {"2026-10-05": 1000}
    with sqlite3.connect(temp_db_path) as conn:
        saved = conn.execute(
            'SELECT generated_menu FROM "User" WHERE email="test@x.com"'
        ).fetchone()[0]
    assert saved == data["generated_menu"]


def test_impossible_budget_does_not_change_saved_plan(
    client, login_session, budget_catalog, temp_db_path
):
    item, llm = budget_catalog
    existing = f"[2026-10-11,{item},3]"
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute('UPDATE "User" SET generated_menu=? WHERE email="test@x.com"', (existing,))
    with client.session_transaction() as session:
        session["GeneratedMenu"] = existing
    response = client.post("/menu/generate", json=payload(weekly_cap="14.99"))
    assert response.status_code == 422
    assert "$15.00" in response.get_json()["error"]
    llm.generate.assert_not_called()
    with sqlite3.connect(temp_db_path) as conn:
        assert (
            conn.execute('SELECT generated_menu FROM "User" WHERE email="test@x.com"').fetchone()[0]
            == existing
        )
    with client.session_transaction() as session:
        assert session["GeneratedMenu"] == existing


@pytest.mark.parametrize("cap", ["-1", "NaN", "10.001", True])
def test_invalid_cap_returns_400(client, login_session, budget_catalog, cap):
    response = client.post("/menu/generate", json=payload(weekly_cap=cap))
    assert response.status_code == 400
    assert "Weekly cap" in response.get_json()["error"]
    budget_catalog[1].generate.assert_not_called()


def test_form_can_request_json_and_receive_budget_errors(client, login_session, budget_catalog):
    response = client.post(
        "/menu/generate",
        data={"start_date": "2026-10-05", "days": "2", "meal3": "on", "weekly_cap": "9.99"},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 422
    assert "weekly cap" in response.get_json()["error"]


def test_omitted_cap_keeps_generation_optional(client, login_session, budget_catalog):
    response = client.post("/menu/generate", json=payload(weekly_cap=None))
    assert response.status_code == 200
    assert response.get_json()["weekly_cap_cents"] is None
    assert response.get_json()["item_total_cents"] == 1000
