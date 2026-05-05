from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

@app.context_processor
def inject_auth():
    return {
        "is_logged_in": "user_id" in session,
        "username": session.get("username")
    }

from . import routes,models