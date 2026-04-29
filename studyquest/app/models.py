from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from typing import Optional
from datetime import date
    
@dataclass
class Quest:
    id: int
    title: str
    description: str
    quest_type: str
    difficulty: str
    due_date: Optional[date] = None
    status: str = "In Progress"
    date_completed: Optional[date] = None 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)