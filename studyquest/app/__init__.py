from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .config import DeploymentConfig
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()

def create_app(config_class=DeploymentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager.login_view = "login"
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login"

    from app.blueprints import main
    app.register_blueprint(main)

    return app