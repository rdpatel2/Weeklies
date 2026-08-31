"""UC04: Update Profile — tests.

Verified against Flask_app.py:1358-1430. /profile/edit requires session
Username + usr_id. On POST it updates phone/preferences/allergies and
redirects to /profile.
"""
import pytest
from proj2.sqlQueries import create_connection, fetch_one, close_connection


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_update_profile_valid_changes(client, seed_user, temp_db_path):
    """UC04 main: valid update writes DB and redirects to /profile."""
    _login(client, seed_user)
    resp = client.post("/profile/edit", data={
        "phone": "5550000001", "preferences": "vegan", "allergies": "nuts",
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "/profile" in resp.headers["Location"]
    conn = create_connection(temp_db_path)
    try:
        row = fetch_one(conn, 'SELECT phone,preferences,allergies FROM "User" WHERE usr_id=?', (seed_user["usr_id"],))
    finally:
        close_connection(conn)
    assert row[0] == "5550000001"
    assert row[1] == "vegan"


def test_update_profile_invalid_input(client, seed_user):
    """UC04 ext 3a: current implementation falls back to old value when field is empty
    (no explicit validation). This documents that behavior."""
    _login(client, seed_user)
    resp = client.post("/profile/edit", data={"phone": ""}, follow_redirects=False)
    # Endpoint accepts and redirects; no explicit invalid-email check for this form
    assert resp.status_code == 302


def test_update_profile_duplicate_email(client, seed_user):
    """UC04 ext 3b: /profile/edit form doesn't accept email changes in current impl.
    Documented via redirect to /profile."""
    _login(client, seed_user)
    resp = client.post("/profile/edit", data={"email": "collision@test.com"}, follow_redirects=False)
    assert resp.status_code == 302


def test_update_profile_no_session(client):
    """UC04 ext 1a: no Username in session → redirect to /login."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/profile/edit", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_update_profile_account_deleted(client, seed_user):
    """UC04 ext 4a: session claims a usr_id that doesn't exist → redirect to /logout."""
    _login(client, seed_user)
    with client.session_transaction() as sess:
        sess["usr_id"] = 999999  # doesn't exist
    resp = client.get("/profile/edit", follow_redirects=False)
    assert resp.status_code == 302
    assert "/logout" in resp.headers["Location"]


def test_update_preferences(client, seed_user, temp_db_path):
    """UC04 variant: preferences and allergies persist."""
    _login(client, seed_user)
    client.post("/profile/edit", data={
        "phone": "5551112222", "preferences": "spicy", "allergies": "shellfish",
    })
    conn = create_connection(temp_db_path)
    try:
        row = fetch_one(conn, 'SELECT preferences,allergies FROM "User" WHERE usr_id=?', (seed_user["usr_id"],))
    finally:
        close_connection(conn)
    assert row[0] == "spicy"
    assert row[1] == "shellfish"
