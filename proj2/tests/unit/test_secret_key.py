"""Session signing key must come from the environment, never a fixed string.

The key used to be hard-coded as "your_secret_key_here", so anyone reading
the repo could forge a session cookie and log in as any user.
"""
import logging
import os

import pytest
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


# ---- key_file: saved local key so restarts and auto-reloads keep logins ----

def test_key_file_created_when_missing(tmp_path):
    key_file = tmp_path / "instance" / "secret_key"
    key = load_secret_key({}, key_file=str(key_file))
    assert len(key) == 64
    assert key_file.read_text().strip() == key


def test_key_file_reused_on_next_start(tmp_path):
    key_file = str(tmp_path / "secret_key")
    assert load_secret_key({}, key_file=key_file) == load_secret_key({}, key_file=key_file)


def test_existing_key_file_used_without_warning(tmp_path, caplog):
    key_file = tmp_path / "secret_key"
    key_file.write_text("  saved-key\n")
    with caplog.at_level(logging.WARNING):
        assert load_secret_key({}, key_file=str(key_file)) == "saved-key"
    assert SECRET_KEY_ENV not in caplog.text


def test_env_key_wins_over_key_file(tmp_path):
    key_file = tmp_path / "secret_key"
    key_file.write_text("saved-key")
    assert load_secret_key({SECRET_KEY_ENV: "from-env"}, key_file=str(key_file)) == "from-env"
    assert key_file.read_text() == "saved-key"  # untouched


def test_env_key_set_does_not_create_key_file(tmp_path):
    key_file = tmp_path / "secret_key"
    load_secret_key({SECRET_KEY_ENV: "from-env"}, key_file=str(key_file))
    assert not key_file.exists()


def test_empty_key_file_is_regenerated(tmp_path):
    key_file = tmp_path / "secret_key"
    key_file.write_text("   \n")
    key = load_secret_key({}, key_file=str(key_file))
    assert len(key) == 64
    assert key_file.read_text().strip() == key


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_key_file_is_owner_only(tmp_path):
    key_file = tmp_path / "secret_key"
    load_secret_key({}, key_file=str(key_file))
    assert key_file.stat().st_mode & 0o777 == 0o600


def test_unwritable_key_file_falls_back_to_random_key(tmp_path, caplog):
    """If the key can't be saved (e.g. read-only checkout), still start with a safe key."""
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("x")  # a file where the directory should be
    key_file = str(blocker / "secret_key")
    with caplog.at_level(logging.WARNING):
        key = load_secret_key({}, key_file=key_file)
    assert len(key) == 64 and key != OLD_HARDCODED_KEY
    assert "random key" in caplog.text
