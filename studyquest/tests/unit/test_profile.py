import unittest

from app import create_app, db
from app.config import TestConfig
from app.models import User


class ProfileTests(unittest.TestCase):
    """Integration tests for the /profile and /profile/<username> routes."""

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.testApp.test_client()

        self.alice = User(username="alice", xp=200)
        self.alice.set_password("password1!")
        self.bob = User(username="bob", xp=80)
        self.bob.set_password("password1!")
        db.session.add_all([self.alice, self.bob])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self, user):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get("/profile", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_own_profile_shows_my_journal(self):
        self._login(self.alice)
        body = self.client.get("/profile").get_data(as_text=True)
        self.assertIn("My Journal", body)

    def test_other_user_profile_shows_their_username_in_title(self):
        self._login(self.alice)
        body = self.client.get("/profile/bob").get_data(as_text=True)
        # Jinja escapes the apostrophe, accept either form
        self.assertTrue(
            "bob&#39;s Journal" in body or "bob's Journal" in body,
            "Expected 'bob's Journal' in profile page title",
        )

    def test_profile_returns_404_for_unknown_username(self):
        self._login(self.alice)
        response = self.client.get("/profile/ghost")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
