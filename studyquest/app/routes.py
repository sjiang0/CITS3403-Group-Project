from app import app
from flask import render_template, redirect, url_for, flash, request
from datetime import datetime

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

@app.route('/create-quest', methods=['GET', 'POST'])
def create_quest():
    print(request.method)
    if request.method == 'POST':
        # Debugging TODO: remove
        print("Form Submitted!")
        print("Title:", request.form.get('title'))
        print("Description:", request.form.get('description'))
        print("Quest Type:", request.form.get('quest_type'))
        print("Difficulty:", request.form.get('difficulty'))

        # Extract the form data
        title = request.form.get('title')
        description = request.form.get('description')
        quest_type = request.form.get('quest_type')
        difficulty = request.form.get('difficulty')
        due_date = request.form.get('due_date')

        # Validation: Ensure required fields are filled out
        if not title or not description or not quest_type or not difficulty:
            flash('All fields must be filled out!', 'error')
            return render_template('create_quest.html')

        flash('Quest created successfully!', 'success')

        return redirect(url_for('dashboard')) #TODO: decide where to redirect
    return render_template("create_quest.html")