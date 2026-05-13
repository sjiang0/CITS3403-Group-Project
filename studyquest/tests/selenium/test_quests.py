import unittest
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import create_app, db
from app.config import TestConfig

from tests.reusable_test_data import *

localHost = "http://localhost:5000/"

class QuestSeleniumTests(unittest.TestCase):
    """Skeleton for Quest-related Selenium Webdriver tests"""
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        
        db.create_all()
        self.user = create_test_user()
        self.quests = create_test_quests(self.user)

        self.server_thread = threading.Thread(
            target=self.testApp.run,
            kwargs={
                "use_reloader": False,
                "debug": False,
                "host": "127.0.0.1",
                "port": 5000
            }
        )

        self.server_thread.daemon = True
        self.server_thread.start()

        time.sleep(2) # give server time to boot up

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install())
        )
        self.driver.get(localHost)

        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


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