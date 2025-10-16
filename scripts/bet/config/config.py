"""
Configuration settings for football prediction system
"""

import os

# Base paths
BASE_DIR = '/var/www/html/pyethone/scripts/bet'
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models', 'saved_models')

# Data files
MATCHES_FILE = os.path.join(DATA_DIR, 'E0_1926_consolidated.csv')
TEAMS_FILE = os.path.join(DATA_DIR, 'teams.csv')
PROCESSED_DATA = os.path.join(DATA_DIR, 'processed', 'features.csv')

# Analysis windows
FORM_WINDOW = 10  # Last 10 matches for form calculation
H2H_WINDOW = 5    # Last 5 head-to-head meetings

# Model parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
TEMPORAL_DECAY = 0.95  # Weight decay for older matches

# League averages (calculated from data)
LEAGUE_AVG_HOME_GOALS = 1.5
LEAGUE_AVG_AWAY_GOALS = 1.2
LEAGUE_AVG_GOALS_TOTAL = 2.7
LEAGUE_AVG_HOME_WIN_RATE = 0.46

# Minimum matches for reliable statistics
MIN_MATCHES_FORM = 5
MIN_MATCHES_H2H = 3

# Model files
MODEL_FILES = {
    # Result predictions
    '1x2': 'model_1x2.pkl',
    '1x': 'model_1x.pkl',
    '12': 'model_12.pkl',
    'x2': 'model_x2.pkl',

    # Goal predictions (match totals)
    'over_05': 'model_over_05.pkl',
    'over_15': 'model_over_15.pkl',
    'over_25': 'model_over_25.pkl',

    # Goal predictions (team-specific)
    'team_over_05': 'model_team_over_05.pkl',
    'team_over_15': 'model_team_over_15.pkl',
    'team_over_25': 'model_team_over_25.pkl',

    # Card predictions
    'cards': 'model_cards.pkl',
    'team_cards': 'model_team_cards.pkl'
}

# Model hyperparameters for XGBoost
N_ESTIMATORS = 200      # Number of boosting rounds
LEARNING_RATE = 0.1     # Step size shrinkage
MAX_DEPTH = 6           # Maximum tree depth

LOG_DIR = os.path.join(BASE_DIR, 'logs')

