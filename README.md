# StudyQuest

StudyQuest is a gamified study tracker that turns your tasks into quests. Complete assignments, exams, or personal study goals to earn XP, maintain a daily streak, and level up. Track your progress, compete on a leaderboard, and explore other users’ profiles in a fun, interactive way.

Built for CITS3403 (Agile Web Development) at UWA, Sem 1 2026.

## What it does

StudyQuest turns studying into quests. You sign up, log in, and add study tasks ("quests") with a type (study / assignment / exam / personal), difficulty, and optional due date. Marking a quest as completed gives you XP (easy 10, medium 25, hard 50), which moves you up levels and keeps your daily streak going.

Additional features include:
- Leaderboard to see class rankings
- Search to view other users’ profiles and stats
- My Quests filtering: filter tasks by type or difficulty

The app is server-side rendered, with some client-side interactions using AJAX:
- Leaderboard search results update as you type
- "My Quests" filtering by type/difficulty

Login is handled by Flask-Login with salted password hashes (Werkzeug), all forms are CSRF-protected with Flask-WTF, and the login route is rate-limited via Flask-Limiter.


## Tech Stack
- **Backend:** Flask, SQLAlchemy
- **Frontend:** Jinja templates, Tailwind CSS, custom CSS (`style.css`)
- **Database:** SQLite
- **Authentication:** Flask-Login, Werkzeug password hashing
- **Forms & Security:** Flask-WTF, CSRF protection
- **Rate limiting:** Flask-Limiter
- **Testing:** unittest (unit + Selenium), webdriver_manager


## How to use

1. Open the app and register a new account.
2. Log in. You'll land on the dashboard.
3. Click "Plant Quest" in the navigation bar and add a study task — pick a type, difficulty, and optional due date.
4. When you finish a task, mark it completed from "My Quests" to earn XP, level up, and bump your daily streak.
5. Open Leaderboard to see the class ranking, or use the search bar to look up another user's profile.

## Group members

| UWA ID | Name | GitHub |
| --- | --- | --- |
| 24282424 | Synne Wikborg | sjiang0 |
| 23940384 | Jacob Popal | jacobpopal1 |
| 24504922 | Fariya Zehrin | Fariya-Zehrin |
| 24280987 | Nuowei Dong | nuoweidong |

## Prerequisites

Before running the app, make sure you have:
- Python 3.10 or higher
- pip installed
- Google Chrome (required for Selenium tests)

## Running the app

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

Copy `.env.example` to `.env` in the repo root and set a secret key:

```bash
cp .env.example .env
```

Then edit `.env` so `SECRET_KEY` is something long and random:

```
SECRET_KEY=anything-long-and-random
```

The app loads `.env` automatically and will refuse to start if `SECRET_KEY` is not set.

Then from inside `studyquest/`:

```bash
cd studyquest # make sure you're in root folder
flask --app run db upgrade
flask --app run run
```

Open http://127.0.0.1:5000/ in the browser.

## Running the tests

From the root folder `studyquest/` with your venv active.

Unit tests (in-memory SQLite, won't touch your dev db):

```bash
python -m unittest discover -s tests/unit_tests -v
```

Selenium tests spin up the Flask app on port 5000 in the background, so make sure nothing else is using it. `webdriver_manager` will pull a matching ChromeDriver automatically.

```bash
python -m unittest discover -s tests/selenium_tests -v
```

Test coverage: 
- Unit tests: 39 tests covering profile, leaderboard, dashboard, my_quests, and create/edit quests functionality
- Selenium tests: 7 tests covering key workflows such as leaderboard interactions and quest completion