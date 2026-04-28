from app import app
from flask import render_template
from datetime import datetime

### TODO: remove/edit when DB is implemented
from app.mock_data import mock_quests

active_quests = [q for q in mock_quests if q.status == "In Progress"]
completed_quests = [q for q in mock_quests if q.status == "Completed"]

# Sort quests by due_date (ascending)
active_quests_with_due_date = sorted(
    [q for q in active_quests if q.due_date], key=lambda x: x.due_date
)
completed_quests_with_due_date = sorted(
    [q for q in completed_quests if q.due_date], key=lambda x: x.due_date
)
# Quests with no due date
active_quests_no_due_date = [q for q in active_quests if not q.due_date]
completed_quests_no_due_date = [q for q in completed_quests if not q.due_date]
# Overdue quests (ensure due_date exists)
overdue_quests = [
    q for q in mock_quests if q.due_date and q.due_date.date() < datetime.now().date() and q.status != "Completed"
]
overdue_quests_sorted = sorted(overdue_quests, key=lambda x: x.due_date)

# Count quests
total_quests = len(mock_quests)
active_count = len(active_quests)
completed_count = len(completed_quests)
overdue_count = len(overdue_quests)

###

@app.route("/")  # TODO: Change when login is properly implemented
@app.route("/dashboard")
def dashboard():
    return render_template(
        'dashboard.html', quests=active_quests_with_due_date
    )

@app.route("/my-quests")
def my_quests():
    return render_template(
        "my_quests.html",
        active_quests_with_due_date=active_quests_with_due_date,
        active_quests_no_due_date=active_quests_no_due_date,
        completed_quests_with_due_date=completed_quests_with_due_date,
        completed_quests_no_due_date=completed_quests_no_due_date,
        overdue_quests=overdue_quests_sorted,
        total_quests=total_quests,
        active_count=active_count,
        completed_count=completed_count,
        overdue_count=overdue_count
    )

@app.route("/create-quest")
def create_quest():
    return render_template("create_quest.html")