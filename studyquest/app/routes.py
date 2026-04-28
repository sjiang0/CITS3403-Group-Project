from app import app
from flask import render_template

from app.mock_data import mock_quests  ## TODO: remove when DB is implemented

@app.route("/")  # TODO: Change when login is properly implemented
@app.route("/dashboard")
def dashboard():
    active_quests = [q for q in mock_quests if q.status == "In Progress"]  # TODO: replace with database query once DB is implemented
    return render_template('dashboard.html', quests=active_quests)

@app.route("/my-quests")
def my_quests():
    return render_template("my_quests.html", quests=mock_quests)

@app.route("/create-quest")
def create_quest():
    return render_template("create_quest.html")