'''
Configuration settings for Football Prediction API
'''
import os
from pathlib import Path

# Base paths
BASE_DIR = Path("/var/www/html/pyethone/scripts/bet2")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Python virtual environment
VENV_PATH = "/var/www/html/pyethone/pye_venv/bin/python"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 5001
API_DEBUG = True  # Set to False in production

# Available competitions
COMPETITIONS = ["premier_league"]

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "python_api.log"

# Model settings
MIN_MATCHES_FOR_TRAINING = 100
DEFAULT_SEASON = "2025-2026"

# Feature engineering settings
ROLLING_WINDOWS = [3, 5, 10]
CORRELATION_THRESHOLD = 0.95

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
