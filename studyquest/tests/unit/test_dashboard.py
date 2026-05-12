import unittest
from datetime import date
from app import create_app, db
from app.config import TestConfig
from .reusable_test_data import create_test_user, create_test_quests

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
        """Dashboard should display top 3 active quests in correct priority order"""
        response = self.client.get("/dashboard")
        data = response.data.decode()

        today = date.today()

        # Replicates the route logic
        overdue_quests = [q for q in self.quests if q.status == "In Progress" and q.due_date and q.due_date < today]
        overdue_quests.sort(key=lambda q: q.due_date)

        upcoming_quests = [q for q in self.quests if q.status == "In Progress" and q.due_date and q.due_date >= today]
        upcoming_quests.sort(key=lambda q: q.due_date)

        no_due_quests = [q for q in self.quests if q.status == "In Progress" and not q.due_date]

        active_quests = (overdue_quests + upcoming_quests + no_due_quests)[:3]

        # Check that only these 3 quests are rendered
        for quest in active_quests:
            self.assertIn(
                quest.title, data,
                f"Quest title '{quest.title}' not found in dashboard HTML"
            )

        # Make sure quests outside the top 3 are not rendered
        other_quests = set(self.quests) - set(active_quests)
        for quest in other_quests:
            self.assertNotIn(
                quest.title, data,
                f"Quest title '{quest.title}' should not appear in dashboard HTML (not in top 3 active)"
            )

        # Check priority order
        indices = [data.find(q.title) for q in active_quests]
        self.assertTrue(
            indices == sorted(indices),
            "Active quests are not displayed in correct priority order: overdue → upcoming → no due date"
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