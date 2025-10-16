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

# Model Configuration
MODEL_TYPE = 'ensemble'  # Options: 'xgboost', 'randomforest', 'ensemble'
ENSEMBLE_WEIGHTS = {
    'xgboost': 0.4,
    'randomforest': 0.6
}

# Model Hyperparameters
MODEL_PARAMS = {
    'xgboost': {
        'match_result': {
            'objective': 'multi:softprob',
            'num_class': 3,
            'n_estimators': 150,
            'max_depth': 5,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        },
        'binary': {  # For goals/cards
            'objective': 'binary:logistic',
            'n_estimators': 100,
            'max_depth': 4,
            'learning_rate': 0.05,
            'random_state': 42
        }
    },
    'randomforest': {
        'match_result': {
            'n_estimators': 200,
            'max_depth': 12,  # Use the better one
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'random_state': 42,
            'n_jobs': -1
        },
        'binary': {  # For goals/cards
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42,
            'n_jobs': -1
        }
    }
}
