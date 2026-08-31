"""UC20: View Restaurant Dashboard — tests.

Verified against Flask_app.py:577-642. /restaurant/dashboard is protected by
@restaurant_required. Renders order-status counts + review summary for the
signed-in restaurant.
"""
import pytest


def _login_owner(client, seed_restaurant):
    client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    })


def test_dashboard_valid(client, seed_restaurant):
    """UC20 main: authenticated owner sees dashboard."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/dashboard")
    assert resp.status_code == 200


def test_dashboard_no_auth(client):
    """UC20 ext 1a: no session → redirect to /restaurant/login."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/restaurant/dashboard", follow_redirects=False)
    assert resp.status_code == 302
    assert "/restaurant/login" in resp.headers["Location"]


def test_dashboard_no_orders(client, seed_restaurant, temp_db_path):
    """UC20 ext 2a: dashboard renders with zero counts when no orders exist."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "Order" WHERE rtr_id=?', (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/dashboard")
    assert resp.status_code == 200


def test_dashboard_no_reviews(client, seed_restaurant, temp_db_path):
    """UC20 ext 3a: dashboard renders with zero review state when no reviews exist."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "Review" WHERE rtr_id=?', (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/dashboard")
    assert resp.status_code == 200


def test_dashboard_own_restaurant(client, seed_restaurant):
    """UC20 variant: dashboard uses session rtr_id only."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/dashboard")
    assert resp.status_code == 200
    # RestaurantName from session appears in template
    assert b"SEF Cafe" in resp.data
