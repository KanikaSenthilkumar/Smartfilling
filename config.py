import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_LIFETIME = timedelta(hours=1)

    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # OCR settings
    USE_REAL_OCR = True

    # Data directories
    DATA_DIR = 'data'
    CONFIG_DIR = os.path.join(DATA_DIR, 'config')
    MOCK_DIR = os.path.join(DATA_DIR, 'mock')
    OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

    # Static directories
    STATIC_DIR = 'static'
    CSS_DIR = os.path.join(STATIC_DIR, 'css')
    JS_DIR = os.path.join(STATIC_DIR, 'js')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    FORMS_DIR = os.path.join(STATIC_DIR, 'forms')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])