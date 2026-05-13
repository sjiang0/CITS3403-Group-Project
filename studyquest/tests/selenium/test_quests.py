import unittest
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import create_app, db
from app.config import TestConfig
from tests.reusable_test_data import *

localHost = "http://127.0.0.1:5000/"

class QuestSeleniumTests(unittest.TestCase):
    """Selenium tests shared Flask server."""

    @classmethod
    def setUpClass(cls):
        # Create Flask app once
        cls.testApp = create_app(TestConfig)
        cls.app_context = cls.testApp.app_context()
        cls.app_context.push()

        db.create_all()
        cls.user = create_test_user()
        cls.quests = create_test_quests(cls.user)

        # use Daemon thread so it's automatically killed after test runner finishes
        cls.server_thread = threading.Thread(
            target=cls.testApp.run,
            kwargs={"use_reloader": False, "debug": False, "host": "127.0.0.1", "port": 5000},
            daemon=True
        )
        cls.server_thread.start()

        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
        )
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.driver.get(localHost)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_login_redirects_to_dashboard(self):
        self.driver.get(localHost + "login")

        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.wait.until(EC.url_contains("/dashboard"))

        self.assertIn(
            "/dashboard",
            self.driver.current_url,
            "User was not redirected to /dashboard after login"
        )

if __name__ == "__main__":
    unittest.main()