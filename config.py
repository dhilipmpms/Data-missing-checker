"""
config.py
---------
Application configuration settings.
All environment-specific settings should be placed here.
"""

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""

    # Secret key for session management (change this in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'data-quality-checker-secret-key-2024'

    # Folder to store uploaded files temporarily
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # Maximum file size allowed: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

    # Number of rows to preview in the data preview table
    PREVIEW_ROWS = 10

    # Debug mode (set to False in production)
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in environment


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
