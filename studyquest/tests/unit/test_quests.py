import unittest
from app import create_app, db
from app.config import TestConfig

class QuestUnitTests(unittest.TestCase):
    """Skeleton for Quest-related unit tests"""
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        # db.create_all()
        # add_test_data_to_db()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()