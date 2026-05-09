"""
End-to-end browser tests using Selenium.

These tests boot a real Flask server in a background subprocess on port 5050
with a throwaway sqlite DB seeded with two users (alice, bob), then drive
headless Chrome against it.

Requirements:
    pip install selenium
    Chrome (or Chromium) installed locally.
    Selenium 4.6+ has Selenium Manager built in, so chromedriver is fetched
    automatically — no separate install needed.

Run:
    cd studyquest
    pytest tests/test_selenium.py
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

selenium = pytest.importorskip("selenium")
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PORT = 5050
BASE_URL = f"http://localhost:{PORT}"
STUDYQUEST_DIR = Path(__file__).resolve().parent.parent
SELENIUM_DB = STUDYQUEST_DIR / "selenium_test.db"


def _wait_for_port(host, port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _seed_database():
    """Seed two users into the selenium-test DB by spawning a small subprocess
    that imports the app — that way we don't have to keep a duplicate schema
    in sync with `models.py`."""
    seed_code = (
        f'import os\n'
        f'os.environ["DATABASE_URL"] = "sqlite:///{SELENIUM_DB.as_posix()}"\n'
        f'from app import app, db\n'
        f'from app.models import User\n'
        f'with app.app_context():\n'
        f'    db.create_all()\n'
        f'    if not User.query.filter_by(username="alice").first():\n'
        f'        a = User(username="alice", xp=200)\n'
        f'        a.set_password("password1!")\n'
        f'        b = User(username="bob", xp=80)\n'
        f'        b.set_password("password1!")\n'
        f'        db.session.add_all([a, b])\n'
        f'        db.session.commit()\n'
    )
    subprocess.run(
        [sys.executable, "-c", seed_code],
        cwd=str(STUDYQUEST_DIR),
        check=True,
    )


@pytest.fixture(scope="module")
def live_server():
    """Start a real Flask server in a subprocess for the duration of the module."""
    if SELENIUM_DB.exists():
        SELENIUM_DB.unlink()
    _seed_database()

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{SELENIUM_DB.as_posix()}"
    env["SECRET_KEY"] = "selenium-test-secret"
    env["FLASK_APP"] = "run.py"

    proc = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--port", str(PORT), "--no-reload"],
        cwd=str(STUDYQUEST_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_port("localhost", PORT, timeout=15):
        proc.kill()
        pytest.fail(f"Flask server failed to start on port {PORT}")

    yield BASE_URL

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    if SELENIUM_DB.exists():
        try:
            SELENIUM_DB.unlink()
        except OSError:
            pass


@pytest.fixture(scope="module")
def driver(live_server):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    try:
        drv = webdriver.Chrome(options=options)
    except WebDriverException as e:
        pytest.skip(f"Chrome / chromedriver not available: {e}")
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


def _login(driver, base_url, username="alice", password="password1!"):
    driver.get(base_url + "/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/dashboard"))


def test_login_redirects_to_dashboard(driver, live_server):
    _login(driver, live_server)
    assert "/dashboard" in driver.current_url


def test_leaderboard_shows_seeded_users(driver, live_server):
    _login(driver, live_server)
    driver.get(live_server + "/leaderboard")
    body = driver.page_source
    assert "alice" in body
    assert "bob" in body


def test_profile_self_shows_my_journal(driver, live_server):
    _login(driver, live_server)
    driver.get(live_server + "/profile")
    title = driver.find_element(By.CLASS_NAME, "page-title").text
    assert "My Journal" in title


def test_profile_other_user_shows_their_username(driver, live_server):
    _login(driver, live_server)
    driver.get(live_server + "/profile/bob")
    title = driver.find_element(By.CLASS_NAME, "page-title").text
    assert "bob" in title.lower()


def test_search_box_filters_users_via_ajax(driver, live_server):
    _login(driver, live_server)
    driver.get(live_server + "/leaderboard")
    box = driver.find_element(By.ID, "user-search")
    box.clear()
    box.send_keys("bo")
    WebDriverWait(driver, 5).until(
        lambda d: "bob" in d.find_element(By.ID, "search-results").text
    )


def test_clicking_username_in_leaderboard_navigates_to_profile(driver, live_server):
    _login(driver, live_server)
    driver.get(live_server + "/leaderboard")
    link = driver.find_element(By.CSS_SELECTOR, "a[href='/profile/bob']")
    link.click()
    WebDriverWait(driver, 5).until(EC.url_contains("/profile/bob"))
    assert "bob" in driver.find_element(By.CLASS_NAME, "page-title").text.lower()
