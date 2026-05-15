from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .config import DeploymentConfig
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user
from .xp_helpers import xp_to_level, level_title, avatar_emoji


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
login_manager.login_view = "main.login"

def create_app(config_class=DeploymentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    from app.blueprints import main
    app.register_blueprint(main)

    # Context processor for base.html
    @app.context_processor
    def inject_xp_vars():
        if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
            user_level = xp_to_level(current_user.xp)
            avatar = avatar_emoji(current_user.username)
            level_name = level_title(user_level)
            return {
                "user_level": user_level,
                "avatar": avatar,
                "level_name": level_name,
            }
        return {
            "user_level": 0,
            "avatar": "",
            "level_name": "",
        }

    return app


