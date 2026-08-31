"""UC03: Sign Out as Customer — tests.

Verified against Flask_app.py:464-485. /logout pops user session keys
and redirects (302) to /login.
"""
import pytest


def test_logout_signed_in_user(client, seed_user):
    """UC03 main: /logout redirects to /login."""
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_logout_already_expired(client):
    """UC03 ext 2a: /logout still redirects to /login when no session exists."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_logout_clears_session_data(client, seed_user):
    """UC03 variant: Username key removed after logout."""
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})
    client.get("/logout")
    with client.session_transaction() as sess:
        assert sess.get("Username") is None
