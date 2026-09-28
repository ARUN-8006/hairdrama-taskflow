from flask import Flask
from flask_cors import CORS
from .config import settings
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY=settings.JWT_SECRET)

    allowed_origins = [
        "https://hairdrama-taskflow.vercel.app",
    ]

    if settings.FRONTEND_URL:
        allowed_origins.extend(
            origin.strip().rstrip("/")
            for origin in settings.FRONTEND_URL.split(",")
            if origin.strip()
        )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": list(set(allowed_origins)),
                "methods": ["GET", "POST", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    app.register_blueprint(api, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
