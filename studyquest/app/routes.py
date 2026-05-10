from app import app, db, limiter
from flask import render_template, jsonify, request, redirect, url_for, flash
from app.models import User, Quest
from datetime import datetime, date
from app.security import is_strong_password
from flask_limiter.errors import RateLimitExceeded
from flask_login import login_user, logout_user, login_required, current_user

#flash rate limit error instead of causing 429 too many requests -jacob
@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    flash(str(e.description), "flash-error")
    return redirect(request.referrer or url_for("login"))


@app.route("/") 
@app.route("/dashboard")
@login_required
def dashboard():
    # extract 3 active quests. 
    # priority order: overdue > active with due date > active no due date
    today = date.today()

    overdue_quests = Quest.query.filter(
        Quest.user_id == current_user.id,
        Quest.status == "In Progress",
        Quest.due_date < today
    ).order_by(Quest.due_date.asc()).all()

    upcoming_quests = Quest.query.filter(
        Quest.user_id == current_user.id,
        Quest.status == "In Progress",
        Quest.due_date >= today
    ).order_by(Quest.due_date.asc()).all()

    no_due_quests = Quest.query.filter(
        Quest.user_id == current_user.id,
        Quest.status == "In Progress",
        Quest.due_date == None
    ).all()

    active_quests = (overdue_quests + upcoming_quests + no_due_quests)[:3]

    # XP + Level
    xp = current_user.xp or 0
    level = (xp // 100) + 1
    xp_into_level = xp % 100
    xp_percent = round((xp_into_level / 100) * 100)

    # Streak
    streak = current_user.streak or 0

    # Rank
    all_users = User.query.order_by(User.xp.desc()).all()
    rank = next(
        (i + 1 for i, u in enumerate(all_users) if u.id == current_user.id),
        None
    )

    # Completed quests (for weekly stats)
    completed_quests = Quest.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).all()

    today = date.today()

    completed_week_count = sum(
        1 for q in completed_quests
        if q.date_completed and (today - q.date_completed).days <= 7
    )

    total_quests = Quest.query.filter_by(user_id=current_user.id).count()
    completion_rate = int((len(completed_quests) / total_quests) * 100) if total_quests else 0

    return render_template(
        "dashboard.html",
        quests=active_quests,
        xp=xp,
        level=level,
        rank=rank,
        xp_into_level=xp_into_level,
        xp_percent=xp_percent,
        streak=streak,
        completed_week_count=completed_week_count,
        completion_rate=completion_rate
    )

@app.route("/my-quests")
@login_required
def my_quests():
    today = date.today()

    active_q = Quest.query.filter(
        Quest.user_id == current_user.id,
        Quest.status == "In Progress",
        (Quest.due_date == None) | (Quest.due_date >= today)
    ).all()

    completed_q = Quest.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).all()

    active_with_due = sorted(
        [q for q in active_q if q.due_date],
        key=lambda x: x.due_date
    )
    active_no_due = [q for q in active_q if not q.due_date]

    completed_with_due = sorted(
        [q for q in completed_q if q.due_date],
        key=lambda x: x.due_date
    )
    completed_no_due = [q for q in completed_q if not q.due_date]

    overdue_quests = Quest.query.filter(
        Quest.user_id == current_user.id,
        Quest.status != "Completed",
        Quest.due_date < today
    ).order_by(Quest.due_date.asc()).all()

    counts = {
        "total": Quest.query.filter_by(user_id=current_user.id).count(),
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

        errors = []

        # Validation
        if not title:
            errors.append("Title is required.")
        if not description:
            errors.append("Description is required.")
        elif len(description) < 10:
            errors.append("Description must be at least 10 characters.")
        valid_types = ["study", "assignment", "exam", "personal"]
        if quest_type not in valid_types:
            errors.append("Invalid quest type selected.")
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            errors.append("Invalid difficulty selected.")
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()

                if due_date_obj < date.today():
                    errors.append("Due date cannot be in the past.")

            except ValueError:
                errors.append("Invalid due date format.")

        # display errors
        if errors:
            for e in errors:
                flash(e, "flash-error")
            return redirect(url_for("create_quest"))
        
        new_quest = Quest(
            title=title,
            description=description,
            quest_type=quest_type,
            difficulty=difficulty,
            due_date=due_date_obj,
            user_id=current_user.id,
            status="In Progress"
        )

        db.session.add(new_quest)
        db.session.commit()

        flash('Quest created successfully!', 'flash-success')

        return redirect(url_for('my_quests')) #TODO: decide where to redirect
    return render_template("create_quest.html")


@app.route("/quest/<int:quest_id>/delete", methods=["POST"])
@login_required
def delete_quest(quest_id):
    quest = Quest.query.filter_by(id=quest_id, user_id=current_user.id).first_or_404()

    db.session.delete(quest)
    db.session.commit()

    # AJAX 
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    # fallback
    flash("Quest deleted.", "flash-success")
    return redirect(url_for("my_quests"))


@app.route("/quest/<int:quest_id>/complete", methods=["POST"])
@login_required
def complete_quest(quest_id):
    quest = Quest.query.filter_by(id=quest_id, user_id=current_user.id).first_or_404()

    # mark quest complete + award XP + update last_active
    quest.mark_completed()

    # update streak logic
    today = date.today()

    if current_user.last_active:
        if (today - current_user.last_active).days == 1:
            current_user.streak += 1
        elif current_user.last_active != today:
            current_user.streak = 1
    else:
        current_user.streak = 1

    current_user.last_active = today

    db.session.commit()

    # AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "quest_id": quest.id,
            "status": "completed"
        })
    
    # fallback
    flash("Quest completed!", "flash-success")
    return redirect(url_for("my_quests"))

@app.route("/quest/<int:quest_id>/uncomplete", methods=["POST"])
@login_required
def uncomplete_quest(quest_id):
    quest = Quest.query.filter_by(id=quest_id, user_id=current_user.id).first_or_404()

    quest.status = "In Progress"
    quest.date_completed = None

    db.session.commit()

    # AJAX response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "quest_id": quest.id,
            "status": "active"
        })

    # fallback 
    flash("Quest moved back to active.", "flash-success")
    return redirect(url_for("my_quests"))

@app.route("/quest/<int:quest_id>/edit", methods=["GET", "POST"])
@login_required
def edit_quest(quest_id):
    quest = Quest.query.filter_by(id=quest_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        quest_type = request.form.get("quest_type")
        difficulty = request.form.get("difficulty")
        due_date = request.form.get("due_date")

        # validation (same rules as create)
        errors = []

        if not title:
            errors.append("Title is required.")
        if not description:
            errors.append("Description is required.")
        elif len(description) < 10:
            errors.append("Description must be at least 10 characters.")

        valid_types = ["study", "assignment", "exam", "personal"]
        if quest_type not in valid_types:
            errors.append("Invalid quest type selected.")

        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            errors.append("Invalid difficulty selected.")

        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()

                if due_date_obj < date.today():
                    errors.append("Due date cannot be in the past.")

            except ValueError:
                errors.append("Invalid due date format.")

        if errors:
            for e in errors:
                flash(e, "flash-error")
            return redirect(url_for("edit_quest", quest_id=quest.id))

        # update fields directly (no need for model method)
        quest.title = title
        quest.description = description
        quest.quest_type = quest_type
        quest.difficulty = difficulty
        quest.due_date = due_date_obj

        db.session.commit()

        flash("Quest updated.", "flash-success")
        return redirect(url_for("my_quests"))

    return render_template("edit_quest.html", quest=quest)


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"], error_message="Too many login attempts, please try again in a minute.")
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Username does not exist.", "flash-error")
            return redirect(url_for("login"))

        if not user.check_password(password):
            flash("Incorrect password.", "flash-error")
            return redirect(url_for("login"))

        login_user(user)

        flash("Logged in successfully!", "flash-success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("You have been logged out.", "flash-info")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("20 per hour", methods=["POST"], error_message="Too many registrations, please try again in an hour.")
def register():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        if len(username) < 3: #added username must be atleast 3 digits check
            flash("Username must be at least 3 characters.", "flash-error")
            return redirect(url_for("register"))
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "flash-error")
            return redirect(url_for("register"))

        if not is_strong_password(password):
            flash("Password must be at least 8 characters and include letters, numbers, and special characters.", "flash-error")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "flash-error")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "flash-success")
        return redirect(url_for("login"))

    return render_template("register.html")