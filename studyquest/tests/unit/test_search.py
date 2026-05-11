import unittest

from app import create_app, db
from app.config import TestConfig
from app.models import User


class SearchUsersTests(unittest.TestCase):
    """Integration tests for the /search_users JSON endpoint."""

    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.testApp.test_client()

        self.me = User(username="me", xp=10)
        self.me.set_password("password1!")
        db.session.add(self.me)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self, user):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    def _add_user(self, username, xp=0):
        u = User(username=username, xp=xp)
        u.set_password("password1!")
        db.session.add(u)
        db.session.commit()
        return u

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get("/search_users?q=al", follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_empty_query_returns_empty_results(self):
        self._login(self.me)
        response = self.client.get("/search_users?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"results": []})

    def test_substring_match_returns_matching_users_only(self):
        self._add_user("alice", xp=100)
        self._add_user("alfred", xp=50)
        self._add_user("bob", xp=10)
        self._login(self.me)

        data = self.client.get("/search_users?q=al").get_json()
        names = [r["username"] for r in data["results"]]
        self.assertIn("alice", names)
        self.assertIn("alfred", names)
        self.assertNotIn("bob", names)

    def test_results_carry_a_profile_url(self):
        self._add_user("findable")
        self._login(self.me)
        data = self.client.get("/search_users?q=find").get_json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["url"], "/profile/findable")

    def test_results_capped_at_ten_per_query(self):
        for i in range(15):
            self._add_user(f"user{i:02d}", xp=i)
        self._login(self.me)
        data = self.client.get("/search_users?q=user").get_json()
        self.assertEqual(len(data["results"]), 10)


if __name__ == "__main__":
    unittest.main()
