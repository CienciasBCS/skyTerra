from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_marshmallow import Marshmallow

from config import Config

login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
ma = Marshmallow()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.solarbeam import bp as solarbeam_bp
    app.register_blueprint(solarbeam_bp)

    from app.solarbeam.admin import bp as solarbeam_admin_app
    app.register_blueprint(solarbeam_admin_app)

    from app.solarbeam.comprador import bp as solarbeam_comprador_app
    app.register_blueprint(solarbeam_comprador_app)

    from app.solarbeam.integrador import bp as solarbeam_integrador_bp
    app.register_blueprint(solarbeam_integrador_bp)

    from app.solarbeam.gestor import bp as solarbeam_gestor_bp
    app.register_blueprint(solarbeam_gestor_bp)

    from app.solarbeam.api import bp as solarbeam_api_bp
    app.register_blueprint(solarbeam_api_bp)


    return app


from app import models