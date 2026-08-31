"""UC19: Sign Out as Restaurant Owner — tests.

Verified against Flask_app.py:561-574. /restaurant/logout pops restaurant
session keys and redirects (302) to /restaurant/login.
"""
import pytest


def test_rest_logout_valid(client, seed_restaurant):
    """UC19 main: logged-in owner → /restaurant/logout clears session and redirects."""
    client.post("/restaurant/login", data={
        "email": seed_restaurant["email"], "password": seed_restaurant["password"],
    })
    resp = client.get("/restaurant/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/restaurant/login" in resp.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("restaurant_mode") is None
        assert sess.get("rtr_id") is None


def test_rest_logout_expired(client):
    """UC19 ext 2a: /restaurant/logout with no session still redirects to signin."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/restaurant/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/restaurant/login" in resp.headers["Location"]
