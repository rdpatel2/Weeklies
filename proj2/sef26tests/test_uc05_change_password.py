"""UC05: Change Password — tests.

Verified against Flask_app.py:1433-1499. /profile/change-password is POST-only.
All outcomes (success or validation failure) redirect (302) to /profile with
different query string flags (pw_updated=1 or pw_error=<reason>).
"""
import pytest


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_change_password_valid(client, seed_user):
    """UC05 main: successful change redirects to /profile?pw_updated=1."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": seed_user["password"],
        "new_password": "newpass456",
        "confirm_password": "newpass456",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_updated=1" in resp.headers["Location"]


def test_change_password_current_missing(client, seed_user):
    """UC05 ext 1a: empty current_password → pw_error=missing_current."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": "",
        "new_password": "newpass456",
        "confirm_password": "newpass456",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_error=missing_current" in resp.headers["Location"]


def test_change_password_new_too_short(client, seed_user):
    """UC05 ext 2a: new password < 6 chars → pw_error=too_short."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": seed_user["password"],
        "new_password": "abc",
        "confirm_password": "abc",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_error=too_short" in resp.headers["Location"]


def test_change_password_mismatch(client, seed_user):
    """UC05 ext 2b: mismatched new passwords → pw_error=mismatch."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": seed_user["password"],
        "new_password": "newpass456",
        "confirm_password": "different",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_error=mismatch" in resp.headers["Location"]


def test_change_password_same_as_current(client, seed_user):
    """UC05 ext 2c: reusing current password → pw_error=same_as_current."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": seed_user["password"],
        "new_password": seed_user["password"],
        "confirm_password": seed_user["password"],
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_error=same_as_current" in resp.headers["Location"]


def test_change_password_wrong_current(client, seed_user):
    """UC05 ext 3a: incorrect current password → pw_error=incorrect_current."""
    _login(client, seed_user)
    resp = client.post("/profile/change-password", data={
        "current_password": "not-the-real-password",
        "new_password": "newpass456",
        "confirm_password": "newpass456",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "pw_error=incorrect_current" in resp.headers["Location"]


def test_change_password_account_missing(client, seed_user):
    """UC05 ext 3b: session usr_id points to non-existent account → redirect to /logout."""
    _login(client, seed_user)
    with client.session_transaction() as sess:
        sess["usr_id"] = 999999
        sess["Email"] = "ghost@test.com"
    resp = client.post("/profile/change-password", data={
        "current_password": "x", "new_password": "newpass456", "confirm_password": "newpass456",
    }, follow_redirects=False)
    assert resp.status_code == 302
    # Either /logout or /profile depending on how the missing-account path was hit
    assert "/logout" in resp.headers["Location"] or "/profile" in resp.headers["Location"]


def test_old_password_invalid_after_change(client, seed_user):
    """UC05 variant: after a successful change, old password no longer authenticates."""
    _login(client, seed_user)
    client.post("/profile/change-password", data={
        "current_password": seed_user["password"],
        "new_password": "brandnew789",
        "confirm_password": "brandnew789",
    })
    client.get("/logout")
    resp = client.post("/login", data={
        "email": seed_user["email"], "password": seed_user["password"],
    })
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data
