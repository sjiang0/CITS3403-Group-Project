from datetime import datetime, timedelta
from .models import Quest

mock_quests = [
    Quest(
        id=1,
        title="Labwork",
        description="Complete weekly lab tasks",
        quest_type="study",
        difficulty="easy",
        due_date=datetime.now() + timedelta(days=-1)  
    ),

    Quest(
        id=2,
        title="Essay draft",
        description="Write first essay draft",
        quest_type="assignment",
        difficulty="medium",
    ),

    Quest(
        id=3,
        title="Midsem revision",
        description="Revise lecture material",
        quest_type="exam",
        difficulty="hard",
        due_date=datetime.now() + timedelta(days=2)  
    ),
    
    Quest(
        id=4,
        title="Group project",
        description="Finish report section",
        quest_type="assignment",
        difficulty="medium",
        due_date=datetime.now() + timedelta(days=10)  
    )
]