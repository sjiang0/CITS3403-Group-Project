import unittest
import multiprocessing
from selenium import webdriver
from app import create_app, db
from app.config import TestConfig

localHost = "http://localhost:5000/"

class QuestSeleniumTests(unittest.TestCase):
    """Skeleton for Quest-related Selenium Webdriver tests"""
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        # db.create_all()
        # add_test_data_to_db()

        self.server_thread = multiprocessing.Process(target=self.testApp.run)
        self.server_thread.start()

        self.driver = webdriver.Chrome()
        self.driver.get(localHost)

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        # db.drop_all()
        self.app_context.pop()
    
if __name__ == "__main__":
    unittest.main()