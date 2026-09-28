from flask import Flask
from flask_cors import CORS
from .config import settings
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY=settings.JWT_SECRET)
    CORS(app, resources={r"/api/*": {"origins": settings.FRONTEND_URL.split(",")}})
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
