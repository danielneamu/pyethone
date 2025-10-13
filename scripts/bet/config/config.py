"""
Configuration file for Football Prediction System
"""
import os

# Base paths
BASE_DIR = "/var/www/html/pyethone/scripts/bet"
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models/saved_models")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Data files
MATCHES_FILE = os.path.join(DATA_DIR, "E0_1926_consolidated.csv")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.csv")
PROCESSED_DATA = os.path.join(DATA_DIR, "processed/features.csv")

# Model parameters
RECENT_MATCHES_WEIGHT = 1.5  # Weight multiplier for recent season data
FORM_WINDOW = 5             # Last N matches for form calculation
H2H_WINDOW = 10             # Last N head-to-head matches

# Training parameters
TEST_SIZE = 0.15             # 15% data for validation
RANDOM_STATE = 42
N_ESTIMATORS = 1000          # XGBoost trees
LEARNING_RATE = 0.01
MAX_DEPTH = 5

# Prediction thresholds
CONFIDENCE_THRESHOLD = 0.65  # Minimum confidence for "high" rating

# Model file names
MODEL_FILES = {
    '1x2': 'model_1x2.pkl',
    '1x': 'model_1x.pkl',
    '12': 'model_12.pkl',
    'x2': 'model_x2.pkl',
    'over_05': 'model_over_05.pkl',
    'over_15': 'model_over_15.pkl',
    'over_25': 'model_over_25.pkl',
    'team_over_05': 'model_team_over_05.pkl',
    'team_over_15': 'model_team_over_15.pkl',
    'team_over_25': 'model_team_over_25.pkl',
    'cards': 'model_cards.pkl',
    'team_cards': 'model_team_cards.pkl'
}
