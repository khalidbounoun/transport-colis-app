import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Veuillez vous connecter pour accéder à cette page.'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.shipments import bp as shipments_bp
    app.register_blueprint(shipments_bp, url_prefix='/shipments')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.clients import bp as clients_bp
    app.register_blueprint(clients_bp, url_prefix='/clients')

    from app.carriers import bp as carriers_bp
    app.register_blueprint(carriers_bp, url_prefix='/carriers')

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/shipping_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Shipping App startup')

    @app.context_processor
    def inject_now():
        return {'year': datetime.now().year}

    return app

from app import models