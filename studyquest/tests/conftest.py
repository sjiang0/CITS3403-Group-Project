"""
Shared pytest fixtures for the studyquest tests.

The Flask app is created at module-import time and binds to the database URI
from `Config` immediately, so we must set DATABASE_URL via env BEFORE the
first `from app import ...` happens. That's why the env tweaks below run at
top of file, before any other import.
"""
import os
import sys
import tempfile
from pathlib import Path

# Make `from app import app` resolvable when pytest is run from anywhere.
_HERE = Path(__file__).resolve().parent
_STUDYQUEST_DIR = _HERE.parent
sys.path.insert(0, str(_STUDYQUEST_DIR))

# Use a throwaway sqlite file just for tests, so we never touch app.db.
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="sq_test_")
os.close(_test_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from app import app as flask_app, db
from app.models import User, Quest

flask_app.config["TESTING"] = True
flask_app.config["WTF_CSRF_ENABLED"] = False


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """Create tables once for the whole test run, drop them at the end."""
    with flask_app.app_context():
        db.create_all()
    yield
    with flask_app.app_context():
        db.drop_all()
    try:
        os.unlink(_test_db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _clean_db():
    """Wipe data between tests so each one starts from an empty DB."""
    with flask_app.app_context():
        db.session.query(Quest).delete()
        db.session.query(User).delete()
        db.session.commit()
        yield


@pytest.fixture
def client():
    """A bare Flask test client (anonymous)."""
    return flask_app.test_client()


@pytest.fixture
def make_user():
    """Factory: create a User row with a known password and return it."""
    def _make(username="alice", password="password1!", xp=0, streak=0):
        u = User(username=username.lower(), xp=xp, streak=streak)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        return u
    return _make


@pytest.fixture
def login_as(client):
    """Helper to populate the test client's session as if `user` had logged in."""
    def _login(user):
        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["username"] = user.username
    return _login
