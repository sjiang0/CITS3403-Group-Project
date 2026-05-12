from datetime import date, timedelta
from app import db
from app.models import User, Quest

def create_test_user(
    username="testuser",
    password="password",
    xp=150,
    streak=3,
    last_active=None
):
    """Create and return a test user with password set"""
    user = User(
        username=username,
        xp=xp,
        streak=streak,
        last_active=last_active or date.today()
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def create_test_quests(user):
    """Create test quests covering overdue, active, no due date, and completed"""
    today = date.today()

    # 1. Overdue quest
    quest_overdue = Quest(
        title="Overdue Quest",
        description="Overdue quest description",
        quest_type="task",
        difficulty="easy",
        status="In Progress",
        start_date=today - timedelta(days=5),
        due_date=today - timedelta(days=2),
        user_id=user.id
    )

    # 2. Active quest
    quest_active = Quest(
        title="Upcoming Quest",
        description="Upcoming quest description",
        quest_type="task",
        difficulty="medium",
        status="In Progress",
        start_date=today,
        due_date=today + timedelta(days=3),
        user_id=user.id
    )

    # 3. No due date quest
    quest_no_due = Quest(
        title="No Due Date Quest",
        description="No due date quest description",
        quest_type="task",
        difficulty="hard",
        status="In Progress",
        start_date=today,
        due_date=None,
        user_id=user.id
    )

    # 4. Completed quest
    quest_completed = Quest(
        title="Completed Quest",
        description="Completed quest description",
        quest_type="task",
        difficulty="medium",
        status="Completed",
        start_date=today - timedelta(days=10),
        due_date=today - timedelta(days=5),
        date_completed=today - timedelta(days=1),
        user_id=user.id
    )

    db.session.add_all([quest_overdue, quest_active, quest_no_due, quest_completed])
    db.session.commit()

    return quest_overdue, quest_active, quest_no_due, quest_completed