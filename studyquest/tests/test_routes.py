"""Integration tests for the leaderboard, profile, and search routes I added."""
import re


def test_leaderboard_redirects_to_login_when_anonymous(client):
    resp = client.get("/leaderboard", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_leaderboard_lists_users_in_xp_descending_order(client, make_user, login_as):
    make_user("bob", xp=50)
    make_user("alice", xp=200)
    me = make_user("yui", xp=120)
    login_as(me)

    resp = client.get("/leaderboard")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # Extract /profile/<username> links in document order — that's the row order.
    rows_in_order = re.findall(r"/profile/([a-z0-9]+)", body)
    assert rows_in_order[:3] == ["alice", "yui", "bob"]


def test_leaderboard_highlights_current_user_row(client, make_user, login_as):
    make_user("other", xp=300)
    me = make_user("me", xp=100)
    login_as(me)

    body = client.get("/leaderboard").get_data(as_text=True)
    # the current-user css class only appears on the row of the logged-in user
    assert "current-user" in body


def test_profile_without_username_shows_my_journal(client, make_user, login_as):
    me = make_user("me", xp=200)
    login_as(me)
    resp = client.get("/profile")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "My Journal" in body


def test_profile_with_other_username_shows_their_username_in_title(client, make_user, login_as):
    make_user("other", xp=300)
    me = make_user("me", xp=50)
    login_as(me)

    resp = client.get("/profile/other")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # Jinja escapes the apostrophe; accept either form
    assert "other&#39;s Journal" in body or "other's Journal" in body


def test_profile_returns_404_for_unknown_username(client, make_user, login_as):
    me = make_user("me")
    login_as(me)
    resp = client.get("/profile/ghost")
    assert resp.status_code == 404


def test_search_users_returns_empty_results_for_blank_query(client, make_user, login_as):
    me = make_user("me")
    login_as(me)
    resp = client.get("/search_users?q=")
    assert resp.status_code == 200
    assert resp.get_json() == {"results": []}


def test_search_users_returns_substring_matches(client, make_user, login_as):
    make_user("alice", xp=100)
    make_user("alfred", xp=50)
    make_user("bob", xp=10)
    me = make_user("me")
    login_as(me)

    data = client.get("/search_users?q=al").get_json()
    names = [r["username"] for r in data["results"]]
    assert "alice" in names
    assert "alfred" in names
    assert "bob" not in names


def test_search_users_results_carry_profile_url(client, make_user, login_as):
    make_user("findable")
    me = make_user("me")
    login_as(me)

    data = client.get("/search_users?q=find").get_json()
    assert len(data["results"]) == 1
    assert data["results"][0]["url"] == "/profile/findable"


def test_search_users_caps_at_ten_results(client, make_user, login_as):
    for i in range(15):
        make_user(f"user{i:02d}", xp=i)
    me = make_user("me")
    login_as(me)

    data = client.get("/search_users?q=user").get_json()
    assert len(data["results"]) == 10
