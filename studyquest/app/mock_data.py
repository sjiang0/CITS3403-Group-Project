from datetime import date, timedelta
from .models import Quest, User
from . import db

DEFAULT_STATUS = "In Progress"

def create_mock_quests():
    # Check if the specific mock user exists
    user = User.query.filter_by(username="mockuser").first()
    if not user:
        user = User(username="mockuser")
        user.set_password("password")  # Set a default password
        db.session.add(user)
        db.session.commit()  # Commit to get user.id

    # Check if the specific quests already exist for this user
    existing_titles = {q.title for q in Quest.query.filter_by(user_id=user.id).all()}
    
    mock_quests_data = [
        {
            "title": "Labwork",
            "description": "Complete weekly lab tasks",
            "quest_type": "study",
            "difficulty": "easy",
            "start_date": date.today() - timedelta(days=4),
            "due_date": date.today() - timedelta(days=1),
        },
        {
            "title": "Essay draft",
            "description": "Write first essay draft",
            "quest_type": "assignment",
            "difficulty": "medium",
            "start_date": date.today() - timedelta(days=2),
        },
        {
            "title": "Midsem revision",
            "description": "Revise lecture material",
            "quest_type": "exam",
            "difficulty": "hard",
            "start_date": date.today(),
            "due_date": date.today() + timedelta(days=2),
        },
        {
            "title": "Group project",
            "description": "Finish report section",
            "quest_type": "assignment",
            "difficulty": "medium",
            "start_date": date.today(),
            "due_date": date.today() + timedelta(days=10),
        },
    ]

    # Only create quests that don't already exist for this user
    new_quests = []
    for data in mock_quests_data:
        if data["title"] not in existing_titles:
            new_quests.append(Quest(user_id=user.id, status=DEFAULT_STATUS, **data))

    if not new_quests:
        print("All mock quests already exist. Skipping creation.")
        return

    db.session.add_all(new_quests)
    db.session.commit()
    print(f"Added {len(new_quests)} new mock quest(s) for {user.username}!")
