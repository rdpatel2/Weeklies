"""UC02: Sign In as Customer — tests.

Verified against Flask_app.py:426-460. Success sets session keys
including 'Username', 'usr_id', 'Email' and redirects to /.
Failure re-renders login.html with status 200 and "Invalid credentials".
"""
import pytest


def test_login_valid_credentials(client, seed_user):
    """UC02 main: valid credentials produce redirect + session."""
    resp = client.post("/login", data={
        "email": seed_user["email"], "password": seed_user["password"],
    }, follow_redirects=False)
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("Username") is not None
        assert sess.get("usr_id") == seed_user["usr_id"]


def test_login_unknown_email(client):
    """UC02 ext 2a: unknown email re-renders login with error."""
    resp = client.post("/login", data={
        "email": "nobody-uc02@nowhere.com", "password": "whatever",
    })
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_login_wrong_password(client, seed_user):
    """UC02 ext 2b: correct email but wrong password rejected."""
    resp = client.post("/login", data={
        "email": seed_user["email"], "password": "not-the-real-password",
    })
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_login_session_expiry(client, seed_user):
    """UC02 ext 3a: no session ⇒ protected page redirects to /login."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/profile", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_login_creates_session_object(client, seed_user):
    """UC02 variant: session contains the identifying fields after login."""
    client.post("/login", data={
        "email": seed_user["email"], "password": seed_user["password"],
    })
    with client.session_transaction() as sess:
        assert sess.get("usr_id") == seed_user["usr_id"]
        assert sess.get("Email") == seed_user["email"]
        assert sess.get("Username")
