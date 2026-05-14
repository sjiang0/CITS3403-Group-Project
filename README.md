# StudyQuest

A gamified study tracker we built for CITS3403 (Agile Web Development) at UWA, Sem 1 2026.

## What it does

StudyQuest turns studying into quests. You sign up, log in, and add study tasks ("quests") with a type (study / assignment / exam / personal), difficulty, and optional due date. Marking a quest as completed gives you XP (easy 10, medium 25, hard 50), which moves you up levels and keeps your daily streak going.

There's also a leaderboard so you can see how everyone in the class is doing, and a search so you can pull up another user's profile and check their stats.

The app is a Flask + SQLite project using SQLAlchemy for the ORM and Jinja for the templates. Styling uses Tailwind CSS alongside a custom design system in `style.css`. The leaderboard search uses AJAX so results show up as you type. Login is handled by Flask-Login with salted password hashes (Werkzeug), all forms are CSRF-protected with Flask-WTF, and the login route is rate-limited via Flask-Limiter.

## How to use

1. Open the app and register a new account.
2. Log in. You'll land on the dashboard.
3. Click "Plant Quest" (or go to Create Quest) and add a study task — pick a type, difficulty, and optional due date.
4. When you finish a task, mark it completed from "My Quests" to earn XP, level up, and bump your daily streak.
5. Open Leaderboard to see the class ranking, or use the search bar to look up another user's profile.

## Group members

| UWA ID | Name | GitHub |
| --- | --- | --- |
| 24282424 | Synne Wikborg | sjiang0 |
| 23940384 | Jacob Popal | jacobpopal1 |
| 24504922 | Fariya Zehrin | Fariya-Zehrin |
| 24280987 | Nuowei Dong | nuoweidong |

## Running the app

You'll need Python 3.10+ and Chrome if you also want to run the Selenium tests.

```bash
git clone https://github.com/sjiang0/CITS3403-Group-Project.git
cd CITS3403-Group-Project

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Set a secret key (or stick it in a `.env` file in the repo root):

```
SECRET_KEY=anything-long-and-random
```

Then from inside `studyquest/`:

```bash
cd studyquest
flask --app run db upgrade
flask --app run run
```

Open http://127.0.0.1:5000/ in the browser.

## Running the tests

From `studyquest/` with your venv active.

Unit tests (in-memory SQLite, won't touch your dev db):

```bash
python -m unittest discover -s tests/unit -v
```

Selenium tests spin up the Flask app on port 5000 in the background, so make sure nothing else is using it. `webdriver_manager` will pull a matching ChromeDriver automatically.

```bash
python -m unittest discover -s tests/selenium -v
```
