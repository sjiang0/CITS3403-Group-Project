from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quest_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)

    start_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(50), default="In Progress")
    date_completed = db.Column(db.Date, nullable=True)

    xp_reward = db.Column(db.Integer, default=10)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='quests')

    def mark_completed(self):
        self.status = "Completed"
        self.date_completed = date.today()

        xp_map = {
            "easy": 10,
            "medium": 20,
            "hard": 40
        }

        reward = xp_map.get(self.difficulty, 10)

        self.user.xp = (self.user.xp or 0) + reward

        self.user.last_active = date.today()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, nullable=True)

    quests = db.relationship('Quest', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)