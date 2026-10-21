"""Session signing key must come from the environment, never a fixed string.

The key used to be hard-coded as "your_secret_key_here", so anyone reading
the repo could forge a session cookie and log in as any user.
"""
import logging

from flask import Flask
from flask.sessions import SecureCookieSessionInterface

import proj2.Flask_app as Flask_app
from proj2.Flask_app import SECRET_KEY_ENV, load_secret_key

OLD_HARDCODED_KEY = "your_secret_key_here"


def _forge_session_cookie(key, data):
    """Sign a session payload the way Flask would with the given key."""
    forger = Flask("forger")
    forger.secret_key = key
    return SecureCookieSessionInterface().get_signing_serializer(forger).dumps(data)


# ---- load_secret_key: expected cases ----

def test_uses_env_key_when_set():
    assert load_secret_key({SECRET_KEY_ENV: "from-env-123"}) == "from-env-123"


def test_strips_whitespace_from_env_key():
    assert load_secret_key({SECRET_KEY_ENV: "  padded-key \n"}) == "padded-key"


def test_no_warning_when_env_key_set(caplog):
    with caplog.at_level(logging.WARNING):
        load_secret_key({SECRET_KEY_ENV: "from-env-123"})
    assert SECRET_KEY_ENV not in caplog.text


# ---- load_secret_key: missing / bad configuration ----

def test_missing_env_key_gives_random_key():
    key = load_secret_key({})
    assert key != OLD_HARDCODED_KEY
    assert len(key) == 64
    int(key, 16)  # hex-encoded random bytes


def test_blank_env_key_treated_as_missing():
    for blank in ("", "   ", "\n"):
        key = load_secret_key({SECRET_KEY_ENV: blank})
        assert len(key) == 64


def test_random_key_differs_each_call():
    assert load_secret_key({}) != load_secret_key({})


def test_missing_env_key_logs_warning(caplog):
    with caplog.at_level(logging.WARNING):
        load_secret_key({})
    assert SECRET_KEY_ENV in caplog.text


def test_reads_os_environ_by_default(monkeypatch):
    monkeypatch.setenv(SECRET_KEY_ENV, "os-env-key")
    assert load_secret_key() == "os-env-key"


# ---- the running app ----

def test_app_key_is_not_old_hardcoded_value():
    assert Flask_app.app.config["SECRET_KEY"] != OLD_HARDCODED_KEY


def test_cookie_forged_with_old_key_is_rejected(client, seed_minimal_data):
    """A session signed with the old public key must not log anyone in."""
    payload = {"Username": "Test User", "Email": seed_minimal_data["usr_email"]}
    client.set_cookie("session", _forge_session_cookie(OLD_HARDCODED_KEY, payload))
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_cookie_signed_with_real_key_is_accepted(client, seed_minimal_data):
    """Control for the test above: the same payload signed with the app's key works,
    so the rejection really is about the key."""
    payload = {"Username": "Test User", "Email": seed_minimal_data["usr_email"]}
    real_key = Flask_app.app.config["SECRET_KEY"]
    client.set_cookie("session", _forge_session_cookie(real_key, payload))
    resp = client.get("/profile")
    assert resp.status_code == 200
