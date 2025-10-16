# Key File Locations
## Project Structure

/var/www/html/pyethone/scripts/bet2/

├── python_api/
│ ├── init.py
│ ├── config.py # ⭐ Config (paths, MODEL_PARAMS)
│ ├── requirements.txt
│ ├── predict.py # ⭐ Main prediction script
│ ├── train_ensemble.py # ⭐ Train match/goals models
│ ├── train_cards.py # ⭐ Train cards models
│ ├── get_teams.py
│ ├── get_competitions.py
│ │
│ ├── services/
│ │ ├── predictor.py # ⭐ Core prediction logic
│ │ ├── feature_engineering.py # ⭐ 212 features
│ │ ├── model_manager.py
│ │ ├── model_trainer.py
│ │ └── data_loader.py
│ │
│ ├── utils/
│ │ ├── helpers.py
│ │ ├── logging_config.py
│ │ └── validation.py
│ │
│ └── models/premier_league/ # ⚠️ NOT in backup (20+ MB)
│ ├── match_result/
│ ├── goals/
│ └── cards/
│
├── php_backend/
│ ├── config.php
│ ├── api/
│ │ ├── predict_api.php # ⭐ Main API endpoint
│ │ ├── teams_api.php
│ │ └── competitions_api.php
│ └── utils/
│ ├── Logger.php
│ └── Validator.php
│
├── public/
│ ├── index.php # ⭐ Main GUI
│ ├── js/app.js # ⭐ Frontend logic
│ └── css/custom.css
│
├── data/
│ ├── competitions.csv
│ ├── notes.csv
│ └── premier_league/
│ ├── 2023-2024_all_teams.csv
│ ├── 2024-2025_all_teams.csv
│ └── 2025-2026_all_teams.csv
│
├── bash/
│ ├── update_data.sh # ⭐ Data scraper wrapper
│ └── update_premier_league_data.py
│
└── logs/
├── predictions.log
├── training.log
└── data_update_*.log



## Files to Edit Most Often
1. `python_api/services/predictor.py` - Prediction logic
2. `python_api/services/feature_engineering.py` - Add features
3. `python_api/config.py` - Hyperparameters, paths
4. `public/js/app.js` - GUI updates
5. `php_backend/api/predict_api.php` - API changes

## Files NOT in Backup
- `python_api/models/**/*.pkl` (too large - retrain with scripts)
- `logs/*` (regenerated)
- `__pycache__/` (Python cache)