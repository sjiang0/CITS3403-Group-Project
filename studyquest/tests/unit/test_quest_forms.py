import unittest
from datetime import date, timedelta
from flask import url_for
from app import create_app, db
from app.models import Quest
from app.config import TestConfig
from .reusable_test_data import create_test_user


class QuestFormsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig) 
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = create_test_user(username="formuser")
        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_quest_form_renders(self):
        """Create quest page loads successfully"""
        with self.app.test_request_context():
            url = url_for("main.create_quest")
        with self.client:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Create Quest did not return 200 OK")
        self.assertIn(b"Create Quest", response.data, "Create Quest page heading was not found in the response.")

    def test_create_quest_success(self):
        """Submitting valid form creates a quest"""
        due = (date.today() + timedelta(days=5)).isoformat()

        with self.app.test_request_context():
            url = url_for("main.create_quest")
        with self.client:
            response = self.client.post(
                url,
                data={
                    "title": "New Quest",
                    "description": "This is a valid quest description",
                    "quest_type": "study",
                    "difficulty": "medium",
                    "due_date": due
                },
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200, "Valid quest submission did not return status code 200 OK.")
        self.assertIn(b"Quest created successfully!",response.data,"Quest creation success message was not displayed.")

        quest = Quest.query.filter_by(title="New Quest").first()
        self.assertIsNotNone(quest, "Quest was not created in the database.")
        self.assertEqual(quest.user_id, self.user.id, "Quest user_id does not match the logged-in user.")
        self.assertEqual(quest.difficulty, "medium", "Quest difficulty was not saved correctly.")
        self.assertEqual(quest.quest_type, "study", "Quest type was not saved correctly.")
        self.assertEqual(quest.due_date.isoformat(), due, "Quest due date was not saved correctly.")

    def test_create_quest_validation_errors(self):
        """Submitting invalid form shows errors"""
        with self.app.test_request_context():
            url = url_for("main.create_quest")
        with self.client:
            response = self.client.post(
                url,
                data={
                    "title": "",  
                    "description": "short",  
                    "quest_type": "invalid",
                    "difficulty": "invalid",
                    "due_date": "2020-01-01"  
                },
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200, "Invalid form submission did not return 200 OK.")
        self.assertIn(b"Title is required.", response.data, "Missing title validation error was not displayed.")
        self.assertIn(b"Description must be at least 10 characters.", response.data, "Description length validation error was not displayed.")
        self.assertIn(b"Invalid quest type selected.", response.data, "Invalid quest type validation error was not displayed.")
        self.assertIn(b"Invalid difficulty selected.", response.data, "Invalid difficulty validation error was not displayed.")
        self.assertIn(b"Due date cannot be in the past.", response.data, "Past due date validation error was not displayed.")

    def test_edit_quest_form_renders(self):
        """Edit quest page loads successfully with pre-filled data"""
        quest = Quest(
            title="Edit Me",
            description="Original description",
            quest_type="study",
            difficulty="easy",
            user_id=self.user.id
        )
        db.session.add(quest)
        db.session.commit()

        with self.app.test_request_context():
            url = url_for("main.edit_quest", quest_id=quest.id)
        with self.client:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Edit Quest page did not return status code 200 OK.")
        self.assertIn(b"Edit Quest", response.data, "Edit Quest page heading was not found in the response.")
        self.assertIn(b"Edit Me", response.data, "Quest title was not pre-filled in the edit form.")
        self.assertIn(b"Original description", response.data, "Quest description was not pre-filled in the edit form.")

    def test_edit_quest_success(self):
        """Editing a quest with valid data updates it"""
        quest = Quest(
            title="Edit Me",
            description="Original description",
            quest_type="study",
            difficulty="easy",
            user_id=self.user.id
        )
        db.session.add(quest)
        db.session.commit()

        new_due = (date.today() + timedelta(days=7)).isoformat()

        with self.app.test_request_context():
            url = url_for("main.edit_quest", quest_id=quest.id)
        with self.client:
            response = self.client.post(
                url,
                data={
                    "title": "Updated Title",
                    "description": "Updated description with enough length",
                    "quest_type": "assignment",
                    "difficulty": "hard",
                    "due_date": new_due
                },
                follow_redirects=True
            )

        self.assertEqual(response.status_code, 200, "Edit quest submission did not return status code 200 OK.")
        self.assertIn(b"Quest updated.", response.data, "Quest update success message was not displayed.")

        quest = Quest.query.get(quest.id)

        self.assertEqual(quest.title, "Updated Title", "Quest title was not updated correctly.")
        self.assertEqual(
            quest.description,
            "Updated description with enough length",
            "Quest description was not updated correctly."
        )
        self.assertEqual(quest.quest_type, "assignment", "Quest type was not updated correctly.")
        self.assertEqual(quest.difficulty, "hard", "Quest difficulty was not updated correctly.")
        self.assertEqual(
            quest.due_date.isoformat(),
            new_due,
            "Quest due date was not updated correctly."
        )

    def test_edit_quest_validation_errors(self):
        """Submitting invalid edit shows errors"""
        quest = Quest(
            title="Edit Me",
            description="Original description",
            quest_type="study",
            difficulty="easy",
            user_id=self.user.id
        )
        db.session.add(quest)
        db.session.commit()

        with self.app.test_request_context():
            url = url_for("main.edit_quest", quest_id=quest.id)
        with self.client:
            response = self.client.post(
                url,
                data={
                    "title": "",
                    "description": "short",
                    "quest_type": "invalid",
                    "difficulty": "invalid",
                    "due_date": "2020-01-01"
                },
                follow_redirects=True
            )

        self.assertEqual(response.status_code, 200, "Invalid edit quest submission did not return status code 200 OK.")
        self.assertIn(b"Title is required.", response.data, "Missing title validation error was not displayed.")
        self.assertIn(b"Description must be at least 10 characters.",response.data,"Description length validation error was not displayed.")
        self.assertIn(b"Invalid quest type selected.",response.data,"Invalid quest type validation error was not displayed.")
        self.assertIn(b"Invalid difficulty selected.",response.data,"Invalid difficulty validation error was not displayed.")
        self.assertIn(b"Due date cannot be in the past.",response.data,"Past due date validation error was not displayed.")

if __name__ == "__main__":
    unittest.main()