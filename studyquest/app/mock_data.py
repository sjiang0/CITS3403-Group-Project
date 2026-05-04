from datetime import date, timedelta
from .models import Quest

DEFAULT_STATUS = "In Progress"

mock_quests = [
    Quest(
        id=1,
        title="Labwork",
        description="Complete weekly lab tasks",
        quest_type="study",
        difficulty="easy",
        due_date=date.today() - timedelta(days=1),  
        status=DEFAULT_STATUS,
        start_date=date.today() - timedelta(days=4)
    ),

    Quest(
        id=2,
        title="Essay draft",
        description="Write first essay draft",
        quest_type="assignment",
        difficulty="medium",
        status=DEFAULT_STATUS,
        start_date=date.today() - timedelta(days=2)
    ),

    Quest(
        id=3,
        title="Midsem revision",
        description="Revise lecture material",
        quest_type="exam",
        difficulty="hard",
        due_date=date.today() + timedelta(days=2),  # Use date instead of datetime
        status=DEFAULT_STATUS,
        start_date=date.today() 
    ),
    
    Quest(
        id=4,
        title="Group project",
        description="Finish report section",
        quest_type="assignment",
        difficulty="medium",
        due_date=date.today() + timedelta(days=10),  # Use date instead of datetime
        status=DEFAULT_STATUS,
        start_date=date.today() 
    )
]