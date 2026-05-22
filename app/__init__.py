"""Flask application factory."""
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
