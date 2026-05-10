from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

csrf = CSRFProtect(app)

limiter = Limiter(key_func=get_remote_address, app=app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


from . import models,routes