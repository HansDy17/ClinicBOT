from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .models.admin_models import User
import os
from app.config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY, BOOTSTRAP_SERVE_LOCAL, OPENAI_API_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

mail = Mail()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    mail.init_app(app)
    csrf = CSRFProtect(app)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DATABASE=DB_NAME,
        MYSQL_HOST=DB_HOST, 
        OPENAI_API_KEY=OPENAI_API_KEY,
        BOOTSTRAP_SERVE_LOCAL=BOOTSTRAP_SERVE_LOCAL,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_PORT=MAIL_PORT,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_DEBUG=True,
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_DEFAULT_SENDER=MAIL_USERNAME,
    )

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(username):
        return User(username)

    app.config["SAML_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saml")
          
    from .routes.index import index_bp
    from .routes.auth import auth_bp
    from .routes.scheduler import appointment_bp
    from .routes.admin import admin_bp

    app.register_blueprint(index_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(appointment_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')

    return app