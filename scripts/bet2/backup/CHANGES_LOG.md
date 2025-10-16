# Session Changes Log

## Session 1 - October 16, 2025

### Fixes Applied
1. ✅ Standardized model hyperparameters
   - Added MODEL_PARAMS to config.py
   - Updated train_ensemble.py and train_cards.py
   - All RF/XGB models use consistent params

2. ✅ Changed confidence to certainty
   - Added `_calculate_certainty()` method to predictor.py
   - Margin-based calculation (1st place - 2nd place)
   - Updated all prediction responses
   - Updated GUI (app.js) to show "Certainty" instead

3. ✅ Reviewed potential bugs
   - Data leakage: Validated opponent features are correct
   - Path config: Noted for future improvement
   - Duplicate code: Not present in current version

4. ✅ Admin controls
   - Added update data button (triggers scraper)
   - Added retrain models button (runs training scripts)
   - PHP APIs: update_data_api.php, retrain_api.php

### Files Modified
- `python_api/config.py` - Added MODEL_PARAMS
- `python_api/services/predictor.py` - Certainty calculation
- `python_api/train_ensemble.py` - Use MODEL_PARAMS
- `python_api/train_cards.py` - Use MODEL_PARAMS
- `public/js/app.js` - Changed confidence to certainty
- `php_backend/api/update_data_api.php` - NEW
- `php_backend/api/retrain_api.php` - NEW

### Current Model Performance
- Match Result (Ensemble): 50.6%
- Goals O/U 2.5: 51.6%
- Total Cards O/U 3.5: 58.7%