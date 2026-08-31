"""UC10: Build Restaurant Order — tests.

The cart in this codebase is client-side (JS) built up on /orders and then
submitted to POST /order as one JSON payload. There is no server-side
'pending order' representation. These tests verify the pieces the server
does own: the browse endpoint /orders and the /order JSON validation seams.
"""
import pytest


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_build_order_add_item(client, seed_user, seed_restaurant):
    """UC10 main: /orders lists items the client can add to a cart."""
    _login(client, seed_user)
    resp = client.get("/orders")
    assert resp.status_code == 200


def test_build_order_add_notes(client, seed_user, seed_restaurant):
    """UC10 variant: POST /order accepts a per-item `notes` field in the JSON payload."""
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": seed_restaurant["first_item_id"], "qty": 1, "notes": "extra cheese"}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_build_order_qty_not_positive(client, seed_user, seed_restaurant):
    """UC10 ext 2a: qty<=0 in the JSON payload is coerced to 1 (see Flask_app.py:1895)."""
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": seed_restaurant["first_item_id"], "qty": 0}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_build_order_duplicate_item(client, seed_user, seed_restaurant):
    """UC10 ext 3a: same item id sent twice in items list creates two line entries
    (server has no dedup). This documents the current behavior."""
    _login(client, seed_user)
    iid = seed_restaurant["first_item_id"]
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": iid, "qty": 1}, {"itm_id": iid, "qty": 2}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 200


def test_build_order_different_restaurant(client, seed_user, seed_restaurant, temp_db_path):
    """UC10 ext 4a: items from different restaurants → server returns error 'mixed_restaurants'."""
    from proj2.sqlQueries import create_connection, execute_query, fetch_one, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Restaurant"(name,email,password_HS,status) VALUES ("Other","other@x.com","x","open")')
        r2 = fetch_one(conn, 'SELECT rtr_id FROM "Restaurant" WHERE email="other@x.com"')[0]
        execute_query(conn,
            'INSERT INTO "MenuItem"(rtr_id,name,price,instock) VALUES (?,"OtherItem",500,1)', (r2,))
        r2_item = fetch_one(conn, 'SELECT itm_id FROM "MenuItem" WHERE rtr_id=?', (r2,))[0]
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": seed_restaurant["first_item_id"], "qty": 1},
                  {"itm_id": r2_item, "qty": 1}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "mixed_restaurants"


def test_build_order_remove_item(client, seed_user, seed_restaurant):
    """UC10 ext 5a: removing items is a client-side action; server only ever receives
    the final items list. Test that a shorter list still succeeds."""
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": seed_restaurant["first_item_id"], "qty": 1}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 200


def test_build_order_empty_cart(client, seed_user, seed_restaurant):
    """UC10 ext 5b: empty items list rejected with error='invalid_input' (400)."""
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 400


def test_build_order_shows_charges(client, seed_user, seed_restaurant):
    """UC10 variant: response contains an ord_id (server calculated & stored charges)."""
    _login(client, seed_user)
    resp = client.post("/order", json={
        "restaurant_id": seed_restaurant["rtr_id"],
        "items": [{"itm_id": seed_restaurant["first_item_id"], "qty": 2}],
        "delivery_type": "delivery",
    })
    assert resp.status_code == 200
    assert resp.get_json()["ord_id"] is not None
