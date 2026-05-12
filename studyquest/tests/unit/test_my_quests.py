import unittest
from app import create_app, db
from app.config import TestConfig
from .resuable_test_data import *
from flask import url_for
from datetime import date

class MyQuestsUnitTests(unittest.TestCase):
    """Unit tests for the My Quests page"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.user = create_test_user()
        self.quests = create_test_quests(self.user)

        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_my_quests_loads(self):
        """My Quests page loads successfully"""
        response = self.client.get("/my-quests")
        self.assertEqual(
            response.status_code, 200,
            "GET /my-quests did not return 200 OK"
        )

    def test_quest_counts_rendered(self):
        """Quest counts are displayed correctly"""
        response = self.client.get("/my-quests")
        data = response.data.decode()

        # overdue quests are not included in active count, as they are counted for themselves in overdue count
        active_count = len([
            q for q in self.quests 
            if q.status == "In Progress" and (q.due_date is None or q.due_date >= date.today())
        ])

        self.assertIn(f'id="total-count">{len(self.quests)}<', data,
                      "Total quest count not rendered correctly")
        self.assertIn(f'id="active-count">{active_count}<', data,
                      "Active quest count not rendered correctly")
        self.assertIn(f'id="completed-count">{len([q for q in self.quests if q.status=="Completed"])}<', data,
                      "Completed quest count not rendered correctly")
        self.assertIn(f'id="overdue-count">{len([q for q in self.quests if q.due_date and q.due_date<date.today() and q.status!="Completed"])}<', data,
                      "Overdue quest count not rendered correctly")

    def test_complete_quest(self):
        """Quest is successfully marked as completed"""
        quest = [q for q in self.quests if q.status=="In Progress"][0]
        response = self.client.post(f"/quest/{quest.id}/complete", follow_redirects=True)
        db.session.refresh(quest)

        self.assertEqual(quest.status, "Completed", "Quest was not marked as completed")
        self.assertIsNotNone(quest.date_completed, "date_completed was not set")
        self.assertIn("Quest completed!", response.data.decode(), "Completion flash message missing")

    def test_uncomplete_quest(self):
        """Completed Quest is successfully marked as uncompleted"""
        quest = [q for q in self.quests if q.status=="Completed"][0]
        response = self.client.post(f"/quest/{quest.id}/uncomplete", follow_redirects=True)
        db.session.refresh(quest)

        self.assertEqual(quest.status, "In Progress", "Quest was not reverted to active")
        self.assertIsNone(quest.date_completed, "date_completed was not cleared")
        self.assertIn("Quest moved back to active.", response.data.decode(), "Uncomplete flash message missing")

    def test_delete_quest(self):
        """Quest is successfully deleted from db"""
        quest = self.quests[0]
        response = self.client.post(f"/quest/{quest.id}/delete", follow_redirects=True)
        quest_in_db = Quest.query.get(quest.id)

        self.assertIsNone(quest_in_db, "Quest was not deleted from database")
        self.assertIn("Quest deleted.", response.data.decode(), "Delete flash message missing")

    def test_filter_buttons_present(self):
        """All Quest filter buttons are present on My Quests page"""
        response = self.client.get("/my-quests")
        data = response.data.decode()
        for section in ["all-btn", "active", "completed", "overdue"]:
            self.assertIn(section, data, f"Filter button '{section}' missing")
        for difficulty in ["easy", "medium", "hard"]:
            self.assertIn(f'data-filter-difficulty="{difficulty}"', data,
                        f"Difficulty filter '{difficulty}' missing")

if __name__ == "__main__":
    unittest.main()