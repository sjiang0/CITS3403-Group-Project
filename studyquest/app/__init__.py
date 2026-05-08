from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

csrf = CSRFProtect(app)

limiter = Limiter(key_func=get_remote_address, app=app)

@app.context_processor
def inject_auth():
    return {
        "is_logged_in": "user_id" in session,
        "username": session.get("username")
    }

from . import routes,models