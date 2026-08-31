"""UC27: Read Customer Reviews (Owner) — tests.

Verified against Flask_app.py:740-855. /restaurant/reviews is protected by
@restaurant_required. Query params: page, sort (recent/highest/lowest),
filter (all/1..5).
"""
import pytest


def _login_owner(client, seed_restaurant):
    client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    })


def test_owner_reviews_valid(client, seed_restaurant):
    """UC27 main: authenticated owner sees reviews page."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews")
    assert resp.status_code == 200


def test_owner_reviews_no_auth(client):
    """UC27 ext 1a: no session → redirect to /restaurant/login."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/restaurant/reviews", follow_redirects=False)
    assert resp.status_code == 302
    assert "/restaurant/login" in resp.headers["Location"]


def test_owner_reviews_none(client, seed_restaurant, temp_db_path):
    """UC27 ext 2a: no reviews → empty state 200."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'DELETE FROM "Review" WHERE rtr_id=?', (seed_restaurant["rtr_id"],))
    finally:
        close_connection(conn)
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews")
    assert resp.status_code == 200


def test_owner_reviews_highest(client, seed_restaurant):
    """UC27 ext 3a: sort=highest accepted."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews?sort=highest")
    assert resp.status_code == 200


def test_owner_reviews_lowest(client, seed_restaurant):
    """UC27 ext 3b: sort=lowest accepted."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews?sort=lowest")
    assert resp.status_code == 200


def test_owner_reviews_by_rating(client, seed_restaurant):
    """UC27 ext 3b: filter=5 accepted (valid 1-5)."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews?filter=5")
    assert resp.status_code == 200


def test_owner_reviews_bad_filter(client, seed_restaurant):
    """UC27 ext 3c: invalid filter value is ignored (still 200)."""
    _login_owner(client, seed_restaurant)
    resp = client.get("/restaurant/reviews?filter=notanumber")
    assert resp.status_code == 200
