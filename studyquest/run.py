from app import create_app, db
from app.config import DeploymentConfig
from flask_migrate import Migrate

app = create_app(DeploymentConfig)
migrate = Migrate(app, db)