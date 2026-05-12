import unittest
from datetime import date
from app import create_app, db
from app.config import TestConfig
from .resuable_test_data import create_test_user, create_test_quests

class DashboardUnitTests(unittest.TestCase):
    """Unit tests for the dashboard page"""

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()

        db.create_all()
        self.user = create_test_user()
        self.quests = create_test_quests(self.user)

        self.client = self.testApp.test_client()
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_dashboard_loads(self):
        """Dashboard page should load successfully"""
        response = self.client.get("/dashboard")
        self.assertEqual(
            response.status_code, 200,
            "Dashboard did not return 200 OK"
        )

    def test_dashboard_quests_rendered(self):
        """Dashboard should display active quests in correct order"""
        response = self.client.get("/dashboard")
        data = response.data.decode()

        # Check all quest titles are rendered
        for quest in self.quests:
            self.assertIn(
                quest.title, data,
                f"Quest title '{quest.title}' not found in dashboard HTML"
            )

        # Check order: overdue first, then upcoming, then no due date
        overdue_index = data.find("Overdue Quest")
        upcoming_index = data.find("Upcoming Quest")
        no_due_index = data.find("No Due Date Quest")
        self.assertTrue(
            overdue_index < upcoming_index < no_due_index,
            "Quests are not displayed in correct priority order: overdue → upcoming → no due date"
        )

    def test_dashboard_xp_and_level(self):
        """Dashboard should render user's XP and level correctly"""
        response = self.client.get("/dashboard")
        data = response.data.decode()

        # User XP = 150 → level 2, xp_into_level = 50
        self.assertIn(
            "Level 2", data,
            "User level 'Level 2' not found on dashboard"
        )
        self.assertIn(
            "50 / 100 XP", data,
            "User XP '50 / 100 XP' not correctly displayed on dashboard"
        )

    def test_dashboard_overdue_icon(self):
        """Overdue quest should display ❌ in template"""
        response = self.client.get("/dashboard")
        data = response.data.decode()

        self.assertIn(
            "❌", data,
            "Overdue icon '❌' not displayed for overdue quest"
        )
        self.assertIn(
            "Overdue Quest", data,
            "Overdue quest title 'Overdue Quest' not displayed on dashboard"
        )

if __name__ == "__main__":
    unittest.main()