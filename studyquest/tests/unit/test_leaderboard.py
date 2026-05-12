import re
import unittest

from app import create_app, db
from app.config import TestConfig
from app.models import User


class LeaderboardTests(unittest.TestCase):
    """Integration tests for the /leaderboard route."""

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
        self.me = User(username="me", xp=120)
        self.me.set_password("password1!")
        db.session.add_all([self.alice, self.bob, self.me])
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
        response = self.client.get("/leaderboard", follow_redirects=False)
        self.assertEqual(
            response.status_code, 302,
            "Anonymous user hitting /leaderboard should be redirected (302), not served the page"
        )
        self.assertIn(
            "/login", response.headers["Location"],
            "Redirect target for unauthenticated /leaderboard should point at /login"
        )

    def test_ranking_is_xp_descending(self):
        self._login(self.me)
        response = self.client.get("/leaderboard")
        self.assertEqual(
            response.status_code, 200,
            "Logged-in user should get a 200 OK from /leaderboard"
        )
        body = response.get_data(as_text=True)
        # Each row links to /profile/<username>; document order = row order
        order = re.findall(r"/profile/([a-z0-9]+)", body)
        self.assertEqual(
            order[:3], ["alice", "me", "bob"],
            "Leaderboard rows should be ordered by xp descending (alice 200, me 120, bob 80)"
        )

    def test_current_user_row_has_highlight_class(self):
        self._login(self.me)
        body = self.client.get("/leaderboard").get_data(as_text=True)
        self.assertIn(
            "current-user", body,
            "The logged-in user's row should carry the 'current-user' CSS class for highlight"
        )

    def test_top_three_get_medal_emojis(self):
        self._login(self.me)
        body = self.client.get("/leaderboard").get_data(as_text=True)
        self.assertIn(
            "🥇", body,
            "Rank 1 row should render the gold medal emoji"
        )
        self.assertIn(
            "🥈", body,
            "Rank 2 row should render the silver medal emoji"
        )
        self.assertIn(
            "🥉", body,
            "Rank 3 row should render the bronze medal emoji"
        )


if __name__ == "__main__":
    unittest.main()
