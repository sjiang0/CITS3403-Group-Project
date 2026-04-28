import os
import secrets
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

db = SQLAlchemy(app)

@app.context_processor
def inject_auth():
    return {
        "is_logged_in": "user_id" in session,
        "username": session.get("username")
    }

from app import routes, models