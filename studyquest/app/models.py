from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from typing import Optional
from datetime import date
    
class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quest_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="In Progress")
    date_completed = db.Column(db.Date, nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)