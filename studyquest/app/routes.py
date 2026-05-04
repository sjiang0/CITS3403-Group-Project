from app import app, db
from flask import render_template
from datetime import date
from app.models import Quest  

@app.route("/") 
@app.route("/dashboard")
def dashboard():
    # Query database for active quests with due dates, ordered by due date
    active_quests = Quest.query.filter_by(status="In Progress")\
        .filter(Quest.due_date.isnot(None))\
        .order_by(Quest.due_date.asc()).all()
        
    return render_template('dashboard.html', quests=active_quests)

@app.route("/my-quests")
def my_quests():
    active_q = Quest.query.filter_by(status="In Progress").all()
    completed_q = Quest.query.filter_by(status="Completed").all()
    
    active_with_due = sorted([q for q in active_q if q.due_date], key=lambda x: x.due_date)
    active_no_due = [q for q in active_q if not q.due_date]
    
    completed_with_due = sorted([q for q in completed_q if q.due_date], key=lambda x: x.due_date)
    completed_no_due = [q for q in completed_q if not q.due_date]
    
    overdue_quests = Quest.query.filter(
        Quest.status != "Completed",
        Quest.due_date < date.today()
    ).order_by(Quest.due_date.asc()).all()

    counts = {
        "total": Quest.query.count(),
        "active": len(active_q),
        "completed": len(completed_q),
        "overdue": len(overdue_quests)
    }

    return render_template(
        "my_quests.html",
        active_quests_with_due_date=active_with_due,
        active_quests_no_due_date=active_no_due,
        completed_quests_with_due_date=completed_with_due,
        completed_quests_no_due_date=completed_no_due,
        overdue_quests=overdue_quests,
        total_quests=counts["total"],
        active_count=counts["active"],
        completed_count=counts["completed"],
        overdue_count=counts["overdue"]
    )

@app.route("/create-quest")
def create_quest():
    return render_template("create_quest.html")