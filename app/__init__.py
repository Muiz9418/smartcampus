from flask import Flask

from config import config_map
from .extensions import db, bcrypt, login_manager
from .routes import auth_bp, student_bp, lecturer_bp, admin_bp, frontend_bp


def create_app(config_name: str = 'default') -> Flask:
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialise extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(lecturer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(frontend_bp)  # keep last — catches all remaining routes

    return app
