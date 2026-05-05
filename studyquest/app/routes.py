from app import app,db
from flask import render_template, request, redirect, url_for, flash, session, g
from app.models import User,Quest
from datetime import datetime, date
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/") 
@app.route("/dashboard")
@login_required
def dashboard():
    # Query database for active quests with due dates, ordered by due date
    active_quests = Quest.query.filter_by(status="In Progress")\
        .filter(Quest.due_date.isnot(None))\
        .order_by(Quest.due_date.asc()).all()
        
    return render_template('dashboard.html', quests=active_quests)

@app.route("/my-quests")
@login_required
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
@login_required
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Username does not exist.", "danger")
            return redirect(url_for("login"))

        if not user.check_password(password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["username"] = user.username

        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

