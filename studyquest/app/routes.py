from app import app
from flask import render_template

from datetime import datetime

### TODO: remove/edit when DB is implemented
from app.mock_data import mock_quests  

active_quests = [q for q in mock_quests if q.status == "In Progress"]  # TODO: replace with database query once DB is implemented
completed_quests = [q for q in mock_quests if q.status == "Completed"]
overdue_quests = [
    q for q in mock_quests # Make sure due_date is not None before comparing with the current date
    if q.due_date and q.due_date.date() < datetime.now().date() and q.status != "Completed"
]

total_quests = len(mock_quests)
active_count = len(active_quests)
completed_count = len(completed_quests)
overdue_count = len(overdue_quests)
###

@app.route("/")  # TODO: Change when login is properly implemented
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html', quests=active_quests)

@app.route("/my-quests")
def my_quests():
    return render_template("my_quests.html", 
                           active_quests=active_quests,
                           completed_quests=completed_quests,
                           overdue_quests=overdue_quests,
                           total_quests=total_quests,
                           active_count=active_count,
                           completed_count=completed_count,
                           overdue_count=overdue_count)

@app.route("/create-quest")
def create_quest():
    return render_template("create_quest.html")