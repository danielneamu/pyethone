# Football Prediction App - Current Project Status

## Overview
Machine learning-based football match prediction system using XGBoost and Random Forest models. Predicts match results (1X2), goals (Over/Under), BTTS, and cards with confidence scoring and ensemble learning.

## What We're Building
A full-stack prediction platform that:
- Scrapes match data from FBRef automatically
- Trains ML models on 3 seasons of Premier League data (212 features)
- Provides predictions via PHP-Python API integration
- Shows results in responsive Bootstrap 5 web interface
- Tracks prediction accuracy over time (planned)

## Current Status: **PRODUCTION-READY v1.0** ✅

### Completed Features
✅ **ML Pipeline (100%)**
- 212-feature engineering with opponent intelligence
- Cards features (yellow/red card predictions)
- Ensemble models (60% RF + 40% XGBoost)
- No data leakage (temporal filtering with .shift(1))

✅ **Prediction Accuracy**
- Match Result: 51% (ensemble)
- Goals O/U 0.5: 94.2%
- Goals O/U 2.5: 51.6%
- Total Cards O/U 3.5: 58.7%

✅ **API & Backend (100%)**
- Python prediction service with model caching
- PHP REST API endpoints
- Team/competition data APIs
- JSON response formatting

✅ **Frontend (100%)**
- Match result predictions with probability bars
- Double chance betting options
- Goals predictions (O/U 0.5-3.5 + BTTS)
- Cards predictions (total match + individual teams)
- Certainty scoring (margin-based, not just max probability)
- Responsive design with Bootstrap 5

✅ **Automation (100%)**
- Data update script (FBRef scraper)
- Cron-ready automation
- Logging and error tracking

✅ **Recent Fixes (Today's Session)**
- Standardized hyperparameters via config.py MODEL_PARAMS
- Changed "confidence" to "certainty" (margin-based calculation)
- Reviewed and validated no data leakage bugs
- Admin panel buttons for data update/model retraining (implemented)

### Architecture
bet2/
├── python_api/ # ML core
│ ├── services/ # Predictor, feature engineering, model manager
│ ├── models/ # Trained .pkl files (NOT in backup - too large)
│ └── utils/ # Helpers, logging, validation
├── php_backend/ # REST API
│ ├── api/ # Endpoints (predict, teams, competitions)
│ └── utils/ # Logger, Validator
├── public/ # Web GUI
│ ├── index.php # Main interface
│ ├── js/app.js # Frontend logic
│ └── css/custom.css # Styling
├── data/ # CSV datasets (3 seasons)
└── bash/ # Automation scripts

### Tech Stack
- **ML:** Python 3.13, XGBoost, scikit-learn, pandas, numpy
- **Backend:** PHP 8.x, shell scripts
- **Frontend:** HTML5, Bootstrap 5, Vanilla JS
- **Data:** FBRef scraper, CSV storage
- **Server:** Ubuntu, Apache/Nginx

### Known Limitations
⚠️ Single competition (Premier League only)
⚠️ No database (predictions not tracked yet)
⚠️ No user authentication
⚠️ Models not versioned
⚠️ Hardcoded paths (not deployment-ready)

## What's Working Right Now
1. Navigate to `http://localhost/pyethone/scripts/bet2/public/index.php`
2. Select two teams (e.g., Arsenal vs Chelsea)
3. Choose model type (XGBoost / Random Forest / Ensemble)
4. Click "Generate Prediction"
5. See full predictions with certainty scores

## File Locations
**Project root:** `/var/www/html/pyethone/scripts/bet2/`
**Python API:** `python_api/`
**PHP Backend:** `php_backend/api/`
**GUI:** `public/index.php`
**Models:** `python_api/models/premier_league/` (⚠️ Not in backup - retrain with scripts)

## Key Commands
Test prediction
cd /var/www/html/pyethone/scripts/bet2/python_api
python predict.py "Arsenal" "Chelsea" "premier_league" "ensemble"

Retrain models
python train_ensemble.py # Match result + goals
python train_cards.py # Cards predictions

Update data
cd ../bash
./update_data.sh

Access GUI
http://localhost/pyethone/scripts/bet2/public/index.php

