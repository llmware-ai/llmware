from flask import Flask, request
from .config import configure_logging


def create_app():
    app = Flask(__name__)

    configure_logging()

    from .api.routes import main as main_routes
    app.register_blueprint(main_routes)

    return app
