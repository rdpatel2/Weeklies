"""UC29: Swap a Single Planned Meal — tests.

Seeds the shared sef26 customer with a known plan and allergies, plus a
restaurant with JSON hours (the shared seed_restaurant uses legacy "9-21"
hours, which swaps treat as closed). The customer's plan and allergies are
restored after each test so other UC tests see the original account.
"""
import json
import pytest

from proj2.Flask_app import parse_generated_menu
from proj2.sqlQueries import create_connection, close_connection, execute_query, fetch_all, fetch_one
from proj2.sef26tests.conftest import login_as_user

## 2025-11-05 is a Wednesday
DAY = "2025-11-05"
NEXT_DAY = "2025-11-06"
ALL_DAY = json.dumps({d: [800, 2200] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]})
DINNER_ONLY = json.dumps({d: [1700, 2200] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]})


def _insert(conn, sql, params):
    execute_query(conn, sql, params)
    return fetch_one(conn, "SELECT last_insert_rowid()")[0]


@pytest.fixture()
def swap_world(temp_db_path, seed_user):
    conn = create_connection(temp_db_path)
    try:
        original = fetch_one(
            conn, 'SELECT allergies, generated_menu FROM "User" WHERE usr_id=?', (seed_user["usr_id"],)
        )
        open_rtr = _insert(conn, 'INSERT INTO "Restaurant"(name,status,hours) VALUES (?,?,?)',
                           ("UC29 Bistro", "Open", ALL_DAY))
        late_rtr = _insert(conn, 'INSERT INTO "Restaurant"(name,status,hours) VALUES (?,?,?)',
                           ("UC29 Late", "Open", DINNER_ONLY))
        shut_rtr = _insert(conn, 'INSERT INTO "Restaurant"(name,status,hours) VALUES (?,?,?)',
                           ("UC29 Shut", "Closed", ALL_DAY))

        def item(rtr_id, name, instock=1, allergens=""):
            return _insert(
                conn,
                'INSERT INTO "MenuItem"(rtr_id,name,description,price,calories,instock,allergens) '
                "VALUES (?,?,?,?,?,?,?)",
                (rtr_id, name, "", 1100, 450, instock, allergens),
            )

        ids = {
            "b": item(open_rtr, "Pancakes"),
            "l": item(open_rtr, "Wrap"),
            "d": item(open_rtr, "Lasagna"),
            "next": item(open_rtr, "Soup"),
            "ok": item(open_rtr, "Grain Bowl", allergens="Sesame"),
            "allergen": item(open_rtr, "Shrimp Tacos", allergens="Gluten, Shellfish"),
            "sold_out": item(open_rtr, "Sold Out Cake", instock=0),
            "late": item(late_rtr, "Late Ribs"),
            "shut": item(shut_rtr, "Shut Stew"),
        }
        menu = f"[{DAY},{ids['b']},1],[{DAY},{ids['l']},2],[{DAY},{ids['d']},3],[{NEXT_DAY},{ids['next']},1]"
        execute_query(conn, 'UPDATE "User" SET allergies=?, generated_menu=? WHERE usr_id=?',
                      ("shellfish", menu, seed_user["usr_id"]))
    finally:
        close_connection(conn)

    yield {"usr_id": seed_user["usr_id"], "menu": menu, "ids": ids}

    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'UPDATE "User" SET allergies=?, generated_menu=? WHERE usr_id=?',
                      (original[0], original[1], seed_user["usr_id"]))
    finally:
        close_connection(conn)


@pytest.fixture()
def customer(client, seed_user, swap_world):
    login_as_user(client, seed_user)
    return client


def _menu(temp_db_path, usr_id):
    conn = create_connection(temp_db_path)
    try:
        return fetch_one(conn, 'SELECT generated_menu FROM "User" WHERE usr_id=?', (usr_id,))[0]
    finally:
        close_connection(conn)


def _swap(client, date, meal, itm_id, **extra):
    return client.post("/menu/swap", json={"date": date, "meal": meal, "itm_id": itm_id, **extra})


def test_swap_meal_valid(customer, swap_world, temp_db_path):
    """UC29 main: the chosen slot gets the new item."""
    resp = _swap(customer, DAY, 2, swap_world["ids"]["ok"])
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
    assert {"itm_id": swap_world["ids"]["ok"], "meal": 2} in parse_generated_menu(
        _menu(temp_db_path, swap_world["usr_id"]))[DAY]


def test_swap_meal_other_slots_intact(customer, swap_world, temp_db_path):
    """UC29 postcondition: every other date/meal entry is unchanged."""
    ids = swap_world["ids"]
    _swap(customer, DAY, 2, ids["ok"])
    assert _menu(temp_db_path, swap_world["usr_id"]) == (
        f"[{DAY},{ids['b']},1],[{DAY},{ids['ok']},2],[{DAY},{ids['d']},3],[{NEXT_DAY},{ids['next']},1]"
    )


def test_swap_meal_options_listed(customer, swap_world):
    """UC29 step 2: only qualifying items are offered."""
    resp = customer.get(f"/menu/swap/options?date={DAY}&meal=2")
    listed = {o["itm_id"] for o in resp.get_json()["options"]}
    ids = swap_world["ids"]
    assert ids["ok"] in listed
    assert not listed & {ids["l"], ids["allergen"], ids["sold_out"], ids["late"], ids["shut"]}


def test_swap_meal_invalid_slot(customer, swap_world, temp_db_path):
    """UC29 ext 1a: invalid date or meal period."""
    assert _swap(customer, "2025-02-30", 2, swap_world["ids"]["ok"]).status_code == 400
    assert _swap(customer, DAY, 5, swap_world["ids"]["ok"]).status_code == 400
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]


def test_swap_meal_empty_slot(customer, swap_world, temp_db_path):
    """UC29 ext 1b: nothing planned in that slot."""
    resp = _swap(customer, NEXT_DAY, 3, swap_world["ids"]["ok"])
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "slot_not_found"
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]


def test_swap_meal_no_alternatives(customer, swap_world, temp_db_path):
    """UC29 ext 2a: no other item qualifies → empty option list."""
    conn = create_connection(temp_db_path)
    stock = fetch_all(conn, 'SELECT itm_id, instock FROM "MenuItem"')
    try:
        execute_query(conn, 'UPDATE "MenuItem" SET instock=0 WHERE itm_id != ?', (swap_world["ids"]["l"],))
        resp = customer.get(f"/menu/swap/options?date={DAY}&meal=2")
    finally:
        for itm_id, instock in stock:
            execute_query(conn, 'UPDATE "MenuItem" SET instock=? WHERE itm_id=?', (instock, itm_id))
        close_connection(conn)
    assert resp.status_code == 200
    assert resp.get_json()["options"] == []


def test_swap_meal_same_item(customer, swap_world, temp_db_path):
    """UC29 ext 3a: the item is already planned in that slot."""
    resp = _swap(customer, DAY, 2, swap_world["ids"]["l"])
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "same_item"


def test_swap_meal_unknown_item(customer, swap_world, temp_db_path):
    """UC29 ext 4a: the item does not exist."""
    resp = _swap(customer, DAY, 2, 987654)
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "item_not_found"
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]


def test_swap_meal_out_of_stock(customer, swap_world, temp_db_path):
    """UC29 ext 4b: the item is out of stock."""
    resp = _swap(customer, DAY, 2, swap_world["ids"]["sold_out"])
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "out_of_stock"
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]


def test_swap_meal_restaurant_not_open(customer, swap_world, temp_db_path):
    """UC29 ext 4c: restaurant not open for business, or closed at that meal time."""
    assert _swap(customer, DAY, 2, swap_world["ids"]["shut"]).get_json()["error"] == "restaurant_unavailable"
    assert _swap(customer, DAY, 2, swap_world["ids"]["late"]).get_json()["error"] == "restaurant_closed"
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]
    assert _swap(customer, DAY, 3, swap_world["ids"]["late"]).status_code == 200


def test_swap_meal_allergen(customer, swap_world, temp_db_path):
    """UC29 ext 4d: stored allergies are enforced even if the request claims none."""
    resp = _swap(customer, DAY, 2, swap_world["ids"]["allergen"], allergens="")
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "allergen"
    assert _menu(temp_db_path, swap_world["usr_id"]) == swap_world["menu"]


def test_swap_meal_requires_login(client):
    """UC29 ext 1c: authentication is absent."""
    assert client.post("/menu/swap", json={"date": DAY, "meal": 1, "itm_id": 1}).status_code == 401
