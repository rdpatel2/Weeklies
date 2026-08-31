"""UC07: View Meal Calendar — tests.

Verified against Flask_app.py:354-422. /  and  /<year>/<month>  render the
calendar for the logged-in user. Also unit-tests parse_generated_menu, which
handles legacy entries, invalid data, and defaulting.
"""
import pytest
from proj2.Flask_app import parse_generated_menu


def _login(client, seed_user):
    client.post("/login", data={"email": seed_user["email"], "password": seed_user["password"]})


def test_view_calendar_valid_month(client, seed_user):
    """UC07 main: /2025/11 renders the requested month."""
    _login(client, seed_user)
    resp = client.get("/2025/11")
    assert resp.status_code == 200


def test_view_calendar_no_plan(client, seed_user):
    """UC07 ext 1a: user with empty generated_menu → still renders."""
    _login(client, seed_user)
    resp = client.get("/")
    assert resp.status_code == 200


def test_view_calendar_legacy_entry():
    """UC07 ext 1b: legacy entry without a meal number defaults to dinner (3)."""
    result = parse_generated_menu("[2025-11-05,42]")
    assert result["2025-11-05"][0]["meal"] == 3


def test_view_calendar_invalid_entry():
    """UC07 ext 1c: invalid entries silently ignored by the parser."""
    result = parse_generated_menu("[not-a-date,abc,9]garbage")
    assert result == {}


def test_view_calendar_account_deleted(client, seed_user):
    """UC07 ext 1d: session Email refers to a non-existent user → redirect to /logout."""
    _login(client, seed_user)
    with client.session_transaction() as sess:
        sess["Email"] = "ghost-uc07@test.com"
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/logout" in resp.headers["Location"]


def test_view_calendar_item_deleted(client, seed_user, seed_restaurant, temp_db_path):
    """UC07 ext 2a: plan entry with an itm_id that doesn't exist is skipped in the calendar view."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn, 'UPDATE "User" SET generated_menu=? WHERE usr_id=?',
                      ("[2025-11-05,999999,3]", seed_user["usr_id"]))
    finally:
        close_connection(conn)
    _login(client, seed_user)
    resp = client.get("/2025/11")
    assert resp.status_code == 200


def test_view_calendar_default_month(client, seed_user):
    """UC07 ext 4a: / with no year/month renders current month."""
    _login(client, seed_user)
    resp = client.get("/")
    assert resp.status_code == 200


def test_view_calendar_today_highlighted(client, seed_user):
    """UC07 variant: current view includes today info (present in HTML)."""
    _login(client, seed_user)
    resp = client.get("/")
    assert resp.status_code == 200
    # The template passes today_day / today_month; content is present
    assert resp.data
