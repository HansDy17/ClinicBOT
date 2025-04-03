from flask import Flask
from flask_cors import CORS
#from flask_mysql_connector import MySQL
# from flask_bootstrap import Bootstrap
import os
from app.config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY, BOOTSTRAP_SERVE_LOCAL, OPENAI_API_KEY

# mysql = MySQL()
# bootstrap = Bootstrap()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DATABASE=DB_NAME,
        MYSQL_HOST=DB_HOST, 
        OPENAI_API_KEY=OPENAI_API_KEY,
        BOOTSTRAP_SERVE_LOCAL=BOOTSTRAP_SERVE_LOCAL
    )

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