"""
app/__init__.py
---------------
Flask Application Factory.
Creates and configures the Flask application instance.
"""

import os
from flask import Flask


def create_app(config_class=None):
    """
    Application factory function.
    Creates a new Flask application instance with the given configuration.

    Args:
        config_class: Configuration class to use (from config.py)

    Returns:
        Configured Flask application instance
    """
    # Create the Flask app, pointing templates and static to correct folders
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        # Default to development config
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
