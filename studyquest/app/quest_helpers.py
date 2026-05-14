from datetime import datetime, date

VALID_TYPES = ["study", "assignment", "exam", "personal"]
VALID_DIFFICULTIES = ["easy", "medium", "hard"]

def validate_quest_form(title, description, quest_type, difficulty, due_date_str):
    """
    Returns a tuple: (errors_list, due_date_obj)
    """
    errors = []

    if not title:
        errors.append("Title is required.")

    if not description:
        errors.append("Description is required.")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters.")

    if quest_type not in VALID_TYPES:
        errors.append("Invalid quest type selected.")

    if difficulty not in VALID_DIFFICULTIES:
        errors.append("Invalid difficulty selected.")

    due_date_obj = None
    if due_date_str:
        try:
            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date_obj < date.today():
                errors.append("Due date cannot be in the past.")
        except ValueError:
            errors.append("Invalid due date format.")

    return errors, due_date_obj