"""
Configuration File
Central configuration for the Bank Teller Chatbot
"""

import os
from pathlib import Path

# Base directory - go up 3 levels from config.py (app/config.py -> app -> backend -> project_root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'bank_demo.db')

# Model paths
MODELS_DIR = os.path.join(BASE_DIR, 'data', 'models')
INTENT_CLASSIFIER_PATH = os.path.join(MODELS_DIR, 'intent_classifier.h5')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'vectorizer.pkl')
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.pkl')
INTENT_MAPPING_PATH = os.path.join(BASE_DIR, 'data', 'intent_mapping.json')

# spaCy model
SPACY_MODEL = 'en_core_web_sm'

# Session configuration
SESSION_TIMEOUT_MINUTES = 30
MAX_SESSION_TURNS = 10

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True  # Set to False in production

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

# Intent confidence threshold
MIN_INTENT_CONFIDENCE = 0.60

# Entity validation limits
MIN_TRANSFER_AMOUNT = 1.0
MAX_TRANSFER_AMOUNT = 1_000_000.0

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Application metadata
APP_NAME = "Bank Teller Chatbot"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered banking assistant with natural language interface"

# Feature flags
ENABLE_LOGGING = True
ENABLE_SESSION_CLEANUP = True
ENABLE_RATE_LIMITING = False  # For future implementation


def get_config():
    """Get configuration dictionary"""
    return {
        'database_path': DATABASE_PATH,
        'models_dir': MODELS_DIR,
        'session_timeout': SESSION_TIMEOUT_MINUTES,
        'api_host': API_HOST,
        'api_port': API_PORT,
        'min_confidence': MIN_INTENT_CONFIDENCE,
        'app_name': APP_NAME,
        'app_version': APP_VERSION
    }


def print_config():
    """Print current configuration"""
    config = get_config()
    print("=" * 70)
    print(" " * 20 + "CONFIGURATION")
    print("=" * 70)
    
    for key, value in config.items():
        print(f"  {key:20s}: {value}")
    
    print("=" * 70)


if __name__ == "__main__":
    print_config()