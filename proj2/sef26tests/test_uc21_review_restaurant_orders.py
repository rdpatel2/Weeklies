"""UC21: Review Restaurant Orders (owner order management) — tests.

Verified against Flask_app.py:645-737. /restaurant/orders is protected by
@restaurant_required and groups orders by status.
"""
import pytest
from proj2.sef26tests.conftest import make_order


def _login_owner(client, seed_restaurant):
    client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    })


def test_rest_orders_valid(client, seed_user, seed_restaurant, temp_db_path):
    """UC21 main: /restaurant/orders returns 200 with orders."""
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Ordered")
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/orders")
    assert resp.status_code == 200


def test_rest_orders_none(client, seed_restaurant, temp_db_path):
    """UC21 ext 1a: empty status groups when no orders exist."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "Order" WHERE rtr_id=?', (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/orders")
    assert resp.status_code == 200


def test_rest_orders_no_auth(client):
    """UC21 ext 1b: no owner session → redirect to /restaurant/login."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/restaurant/orders", follow_redirects=False)
    assert resp.status_code == 302
    assert "/restaurant/login" in resp.headers["Location"]


def test_rest_orders_invalid_details(client, seed_user, seed_restaurant, temp_db_path):
    """UC21 ext 3a: order with malformed details JSON still renders (parse falls back to {})."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Order"(rtr_id,usr_id,details,status) VALUES (?,?,?,?)',
            (seed_restaurant["rtr_id"], seed_user["usr_id"], "not-json", "Ordered"))
    finally:
        close_connection(conn)
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/orders")
    assert resp.status_code == 200


def test_rest_orders_unknown_status(client, seed_user, seed_restaurant, temp_db_path):
    """UC21 ext 4a: unknown status goes into 'Other' bucket (see Flask_app.py:729)."""
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Weird")
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/orders")
    assert resp.status_code == 200
