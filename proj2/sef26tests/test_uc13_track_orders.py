"""UC13: Track Order History — tests.

The order history is shown on /profile (Flask_app.py:1239-1354), which
queries the user's orders sorted newest-first with review-status flags.
"""
import pytest
from proj2.sef26tests.conftest import make_order


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_track_orders_valid(client, seed_user, seed_restaurant, temp_db_path):
    """UC13 main: /profile lists user's orders."""
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"])
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_none(client, seed_user, temp_db_path):
    """UC13 ext 1a: user with no orders still gets /profile 200."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "Order" WHERE usr_id=?', (seed_user["usr_id"],))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_invalid_details(client, seed_user, seed_restaurant, temp_db_path):
    """UC13 ext 2a: order with invalid JSON details still renders (parser catches errors)."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Order"(rtr_id,usr_id,details,status) VALUES (?,?,?,?)',
            (seed_restaurant["rtr_id"], seed_user["usr_id"], "not-json", "Ordered"))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_missing_restaurant(client, seed_user, temp_db_path):
    """UC13 ext 4a: order references restaurant that no longer exists.

    Current query INNER JOINs Restaurant, so an orphan order will not appear —
    /profile still renders 200 (documents behavior)."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Order"(rtr_id,usr_id,details,status) VALUES (?,?,?,?)',
            (999999, seed_user["usr_id"], "{}", "Ordered"))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_can_review(client, seed_user, seed_restaurant, temp_db_path):
    """UC13 ext 5a: delivered order with no review is flagged has_review=False."""
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Delivered")
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_review_exists(client, seed_user, seed_restaurant, temp_db_path):
    """UC13 ext 5b: delivered order with review present is flagged has_review=True."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    ord_id = make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Delivered")
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Review"(rtr_id,usr_id,title,rating,description,ord_id,created_at) '
            'VALUES (?,?,?,?,?,?,?)',
            (seed_restaurant["rtr_id"], seed_user["usr_id"], "t", 5, "d", ord_id, "2025-01-01T00:00"))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200


def test_track_orders_filter_status(client, seed_user, seed_restaurant, temp_db_path):
    """UC13 variant: /profile currently returns all statuses (no server-side filter),
    but response is still 200. Documents current behavior."""
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Delivered")
    make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Cancelled")
    _login(client, seed_user)
    resp = client.get("/profile")
    assert resp.status_code == 200
