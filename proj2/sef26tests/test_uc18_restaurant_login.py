"""UC18: Sign In as Restaurant Owner — tests.

Verified against Flask_app.py:522-558. POST /restaurant/login sets session
restaurant_mode=True + rtr_id and redirects to /restaurant/dashboard.
Invalid creds re-render restaurant_login.html with 'Invalid credentials'.
"""
import pytest


def test_rest_login_valid(client, seed_restaurant):
    """UC18 main: valid creds → redirect + session[restaurant_mode] set."""
    resp = client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    }, follow_redirects=False)
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("restaurant_mode") is True
        assert sess.get("rtr_id") == seed_restaurant["rtr_id"]


def test_rest_login_unknown_email(client):
    """UC18 ext 2a: unknown email → re-render 200 with Invalid credentials."""
    resp = client.post("/restaurant/login", data={
        "email": "nobody-uc18@nowhere.com", "password": "x",
    })
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_rest_login_wrong_password(client, seed_restaurant):
    """UC18 ext 2b: wrong password → 200 Invalid credentials."""
    resp = client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": "wrong",
    })
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_rest_login_closed_status(client, seed_restaurant, temp_db_path):
    """UC18 ext 2c: restaurant with status='closed' can still log in (no status gate in login)."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, "UPDATE Restaurant SET status='closed' WHERE rtr_id=?", (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    resp = client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    }, follow_redirects=False)
    assert resp.status_code == 302
    # Reset for other tests
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, "UPDATE Restaurant SET status='open' WHERE rtr_id=?", (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)


def test_rest_login_session_id(client, seed_restaurant):
    """UC18 variant: session has restaurant_mode + rtr_id after login."""
    client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    })
    with client.session_transaction() as sess:
        assert sess.get("rtr_id") == seed_restaurant["rtr_id"]
        assert sess.get("restaurant_mode") is True
