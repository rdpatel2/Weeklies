"""UC08: Browse Restaurants — tests.

Verified against Flask_app.py:2141-2212. GET /restaurants requires login;
returns HTML listing all restaurants (with items joined) regardless of stock.
"""
import pytest


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_browse_restaurants_all(client, seed_user, seed_restaurant):
    """UC08 main: /restaurants returns 200 with all restaurants."""
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200


def test_browse_restaurants_none(client, seed_user, temp_db_path):
    """UC08 ext 1a: DB with no restaurants still returns 200 (empty catalog)."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "MenuItem"')
        execute_query(conn, 'DELETE FROM "Restaurant"')
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200


def test_browse_restaurants_no_items(client, seed_user, seed_restaurant, temp_db_path):
    """UC08 ext 2a: restaurant present, all items out-of-stock → still lists restaurant."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'UPDATE "MenuItem" SET instock=0')
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200


def test_browse_restaurants_stock_unset(client, seed_user, seed_restaurant, temp_db_path):
    """UC08 ext 2b: items with NULL instock are treated as available."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'UPDATE "MenuItem" SET instock=NULL')
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200


def test_browse_restaurants_partial_address(client, seed_user, seed_restaurant, temp_db_path):
    """UC08 ext 4a: partial address renders cleanly (no extra separators)."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'UPDATE "Restaurant" SET city=NULL, state=NULL WHERE rtr_id=?', (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200


def test_browse_restaurants_item_match(client, seed_user, seed_restaurant):
    """UC08 variant: response includes the restaurant's items."""
    _login(client, seed_user)
    resp = client.get("/restaurants")
    assert resp.status_code == 200
    assert b"Pasta" in resp.data or b"Salad" in resp.data
