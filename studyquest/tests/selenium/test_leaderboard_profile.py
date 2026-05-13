"""
Selenium end-to-end tests for the leaderboard, profile, and AJAX user-search flows.

Covers the routes owned by Nuowei in app/routes.py
(see the "Leaderboard, Profile & User Search" section):
    GET /leaderboard
    GET /profile, GET /profile/<username>
    GET /search_users          (AJAX backing for the leaderboard search box)

Each test drives a real Chrome browser against a Flask server bound to a
shared SQLite file, so seeded fixtures are visible to both the test process
and the server thread.
"""

import os
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from app import create_app, db
from app.config import TestConfig
from app.models import Quest, User


# Use a non-default port so a developer running `flask run` on 5000 doesn't clash.
PORT = 5050
BASE_URL = f"http://localhost:{PORT}"


class _ServerThread(threading.Thread):
    """Run werkzeug's WSGI server on a background thread so Selenium can hit it."""

    def __init__(self, app):
        super().__init__(daemon=True)
        self.srv = make_server("localhost", PORT, app)

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def _wait_for_server(url, timeout=10):
    """Block until the Flask dev server is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except (urllib.error.URLError, ConnectionError, socket.timeout):
            time.sleep(0.2)
    raise RuntimeError(f"Flask server at {url} did not start within {timeout}s")


class LeaderboardProfileSearchSeleniumTests(unittest.TestCase):
    """
    Browser-driven tests for /leaderboard, /profile, and /search_users.

    Uses setUpClass / tearDownClass (rather than the per-test setUp pattern in
    test_quests.py) because starting Chrome + a Flask server per test would add
    several seconds of overhead per case for no isolation benefit — these tests
    are read-only against the seeded DB.
    """

    @classmethod
    def setUpClass(cls):
        # File-backed SQLite so the test process and the server thread share state.
        fd, cls.db_path = tempfile.mkstemp(suffix=".db", prefix="selenium_studyquest_")
        os.close(fd)

        class _SeleniumConfig(TestConfig):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{cls.db_path}"

        cls.app = create_app(_SeleniumConfig)

        with cls.app.app_context():
            db.create_all()
            cls._seed_users_and_quest()

        cls.server = _ServerThread(cls.app)
        cls.server.start()
        _wait_for_server(f"{BASE_URL}/login")

        # Headless Chrome keeps tests portable to CI / machines without a display.
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1280,900")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=opts)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass
        try:
            cls.server.shutdown()
            cls.server.join(timeout=3)
        except Exception:
            pass
        try:
            os.unlink(cls.db_path)
        except OSError:
            pass

    @classmethod
    def _seed_users_and_quest(cls):
        """Four users at distinct XP tiers plus one completed quest for `testme`."""
        alice = User(username="alice", xp=300, last_active=date.today())
        bob = User(username="bob", xp=200, last_active=date.today())
        testme = User(username="testme", xp=150, last_active=date.today())
        charlie = User(username="charlie", xp=100, last_active=date.today())
        for u in (alice, bob, testme, charlie):
            u.set_password("password1!")
        db.session.add_all([alice, bob, testme, charlie])
        db.session.commit()

        quest = Quest(
            title="Read chapter 1",
            description="Read chapter 1 of the textbook for selenium testing",
            quest_type="study",
            difficulty="easy",
            status="Completed",
            start_date=date.today(),
            date_completed=date.today(),
            user_id=testme.id,
        )
        db.session.add(quest)
        db.session.commit()

    def setUp(self):
        # Reset session between tests, then log in fresh as `testme`.
        self.driver.delete_all_cookies()
        self._login_as("testme")

    def _login_as(self, username, password="password1!"):
        d = self.driver
        d.get(f"{BASE_URL}/login")
        d.find_element(By.NAME, "username").send_keys(username)
        d.find_element(By.NAME, "password").send_keys(password)
        d.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
        WebDriverWait(d, 5).until(EC.url_contains("/dashboard"))

    # ── Tests ────────────────────────────────────────────────

    def test_leaderboard_renders_users_in_xp_descending_order(self):
        """Leaderboard rows should appear top-to-bottom in XP-descending order."""
        self.driver.get(f"{BASE_URL}/leaderboard")

        rows = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".leaderboard-row")
        )
        usernames = []
        for row in rows:
            link = row.find_element(By.CSS_SELECTOR, ".leaderboard-username a")
            # Current user's anchor text is "username (you)" — take the first token.
            usernames.append(link.text.split()[0])

        self.assertEqual(
            usernames[:4],
            ["alice", "bob", "testme", "charlie"],
            f"Expected XP-desc order [alice, bob, testme, charlie], got {usernames}",
        )

    def test_current_user_row_is_visually_highlighted(self):
        """The logged-in user's row should carry the `.current-user` class."""
        self.driver.get(f"{BASE_URL}/leaderboard")

        highlighted = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".leaderboard-row.current-user"))
        )
        username_text = highlighted.find_element(
            By.CSS_SELECTOR, ".leaderboard-username"
        ).text.lower()

        self.assertIn(
            "testme",
            username_text,
            "The .current-user row should belong to the logged-in user (testme)",
        )

    def test_ajax_user_search_renders_matching_results(self):
        """Typing in #user-search should AJAX-fetch matches and render them in #search-results."""
        self.driver.get(f"{BASE_URL}/leaderboard")
        search = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "user-search"))
        )
        search.send_keys("ali")  # 'alice' is the only match

        # leaderboard.js debounces 200 ms before issuing the fetch.
        results = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "search-results"))
        )
        WebDriverWait(self.driver, 5).until(
            lambda d: "alice" in results.text.lower()
        )

        self.assertIn(
            "alice",
            results.text.lower(),
            "Query 'ali' should AJAX-render a result row containing 'alice'",
        )

    def test_clicking_search_result_navigates_to_that_users_profile(self):
        """Clicking a result row in the AJAX search results should land on /profile/<username>."""
        self.driver.get(f"{BASE_URL}/leaderboard")
        self.driver.find_element(By.ID, "user-search").send_keys("bob")

        link = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#search-results a[href='/profile/bob']")
            )
        )
        link.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("/profile/bob"))

        page_title = self.driver.find_element(By.CSS_SELECTOR, ".page-title").text.lower()
        self.assertIn(
            "bob",
            page_title,
            f"After clicking 'bob' the profile header should mention bob — got '{page_title}'",
        )

    def test_profile_shows_current_users_xp_and_recently_completed_quest(self):
        """Visiting /profile should show the user's total XP and recently-completed quests."""
        self.driver.get(f"{BASE_URL}/profile")

        stat_values = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".stat-value")
        )
        stat_texts = [s.text.strip() for s in stat_values]
        self.assertIn(
            "150",
            stat_texts,
            f"Profile stat grid should display total XP=150 for testme, got {stat_texts}",
        )

        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn(
            "Read chapter 1",
            body_text,
            "Profile 'Recently Completed' should list the seeded quest 'Read chapter 1'",
        )


if __name__ == "__main__":
    unittest.main()
