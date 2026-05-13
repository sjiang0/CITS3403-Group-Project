import unittest
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoAlertPresentException
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

        # Start Flask server in a daemon thread
        cls.server_thread = threading.Thread(
            target=cls.testApp.run,
            kwargs={"use_reloader": False, "debug": False, "host": "127.0.0.1", "port": 5000},
            daemon=True
        )
        cls.server_thread.start()

        # Start WebDriver
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.driver.get(localHost)

        # Perform login once
        cls._login(cls.driver, cls.wait)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    @classmethod
    def _login(cls, driver, wait, username="testuser", password="password"):
        """Class method login for use in setUpClass."""
        driver.get(localHost)
        time.sleep(2)  # pause to see landing page

        driver.delete_all_cookies()
        driver.get(localHost + "login")

        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(username)

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        wait.until(EC.url_contains("/dashboard"))
        time.sleep(1)  # pause to see dashboard

    def test_01_login_redirects_to_dashboard(self):
        """User is redirected to dashboard after login (already logged in)."""
        # Already logged in via setUpClass
        current_url = self.driver.current_url
        self.assertIn("/dashboard", current_url, "User was not redirected to /dashboard after login")
        time.sleep(1)  # pause to see dashboard

    def test_02_complete_quest_from_dashboard(self):
        """Completing an active quest moves it to the Completed section."""
        # Go to My Quests page
        dashboard_link = self.driver.find_element(By.LINK_TEXT, "My Quests")
        dashboard_link.click()
        time.sleep(2)  # pause to see My Quests page

        # Handle unexpected alert (during testing, kept getting password found in breach alert)
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except NoAlertPresentException:
            pass

        # Find first active quest
        active_section = self.driver.find_element(By.ID, "active-section")
        first_active_quest = active_section.find_element(By.CLASS_NAME, "quest-item")
        complete_form = first_active_quest.find_element(By.CLASS_NAME, "complete-form")
        complete_button = complete_form.find_element(By.TAG_NAME, "button")

        # Scroll into view and click Complete
        self.driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
        time.sleep(0.5)
        complete_button.click()

        # Wait for the quest to either disappear or change status
        self.wait.until(lambda driver: (
            first_active_quest.get_attribute("data-status") == "completed"
            or first_active_quest not in active_section.find_elements(By.CLASS_NAME, "quest-item")
        ))

        # Wait for it to appear in Completed section
        completed_section = self.driver.find_element(By.ID, "completed-section")
        self.wait.until(lambda driver: any(
            q.get_attribute("data-status") == "completed"
            for q in completed_section.find_elements(By.CLASS_NAME, "quest-item")
        ))

        # Final assertion
        completed_quests = completed_section.find_elements(By.CLASS_NAME, "quest-item")
        self.assertTrue(
            any(q.get_attribute("data-status") == "completed" for q in completed_quests),
            "Quest did not move to Completed section after clicking Complete"
        )

        time.sleep(2)  # pause to see completed quests

if __name__ == "__main__":
    unittest.main()