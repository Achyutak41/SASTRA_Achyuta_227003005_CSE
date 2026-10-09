import os

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.database import init_db
from app.routes.conversations import conversations_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-secret"
    )

    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY",
        "development-jwt-secret"
    )

    CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"]
        }
    },
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

    init_db()

    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.chat import chat_bp


    app.register_blueprint(chat_bp)

    app.register_blueprint(
        health_bp
    )
    app.register_blueprint(conversations_bp)

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        documents_bp
    )

    return app