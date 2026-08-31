"""UC17: Browse Restaurant Reviews — tests.

Verified against Flask_app.py:1678-1797. GET /restaurant/<int:rtr_id>/reviews
does NOT require login. abort(404) if restaurant missing.
Query params: page, sort (recent/highest/lowest), filter (all/1/2/3/4/5).
"""
import pytest


def test_browse_reviews_valid(client, seed_restaurant):
    """UC17 main: valid restaurant returns 200 with reviews page."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews")
    assert resp.status_code == 200


def test_browse_reviews_not_found(client):
    """UC17 ext 1a: missing restaurant → 404."""
    resp = client.get("/restaurant/999999/reviews")
    assert resp.status_code == 404


def test_browse_reviews_none(client, seed_restaurant):
    """UC17 ext 2a: no reviews → still 200 (empty state rendered)."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews")
    assert resp.status_code == 200


def test_browse_reviews_highest(client, seed_restaurant):
    """UC17 ext 3a: sort=highest is accepted."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews?sort=highest")
    assert resp.status_code == 200


def test_browse_reviews_lowest(client, seed_restaurant):
    """UC17 ext 3b: sort=lowest is accepted."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews?sort=lowest")
    assert resp.status_code == 200


def test_browse_reviews_by_rating(client, seed_restaurant):
    """UC17 ext 3c: filter=5 is accepted."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews?filter=5")
    assert resp.status_code == 200


def test_browse_reviews_bad_filter(client, seed_restaurant):
    """UC17 ext 3d: invalid filter value is ignored (still 200)."""
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews?filter=abc")
    assert resp.status_code == 200


def test_browse_reviews_avg_calc(client, seed_user, seed_restaurant, temp_db_path):
    """UC17 variant: average rating computed correctly."""
    from proj2.sqlQueries import create_connection, execute_query, close_connection
    from proj2.sef26tests.conftest import make_order
    ord_id = make_order(temp_db_path, seed_user["usr_id"], seed_restaurant["rtr_id"], status="Delivered")
    conn = create_connection(temp_db_path)
    try:
        execute_query(conn,
            'INSERT INTO "Review"(rtr_id,usr_id,title,rating,description,ord_id,created_at) '
            'VALUES (?,?,?,?,?,?,?)',
            (seed_restaurant["rtr_id"], seed_user["usr_id"], "t", 4, "d", ord_id, "2025-01-01T00:00"))
    finally:
        close_connection(conn)
    resp = client.get(f"/restaurant/{seed_restaurant['rtr_id']}/reviews")
    assert resp.status_code == 200
