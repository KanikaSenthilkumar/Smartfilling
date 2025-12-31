"""
Smart Filling Frontend - Flask Application Package
"""

import os
from flask import Flask
from config import get_config

def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_DIR'], exist_ok=True)

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app