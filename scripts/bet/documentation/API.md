# Football Prediction System - API Documentation (Updated)

## Base URL
https://your-domain/pyethone/scripts/bet/api/

## Endpoints

### 1. GET /predict_api.php?action=teams

Returns the list of valid teams.

Example: 

curl -k "https://your-domain/pyethone/scripts/bet/api/predict_api.php?action=teams"


Response:

{
"success": true,
"teams": [
{"name": "Arsenal", "short_name": "ARS"},
{"name": "Liverpool", "short_name": "LIV"},
...
]
}



### 2. POST /predict_api.php

Make predictions for a matchup.

Request body (JSON):

{
"home_team": "Liverpool",
"away_team": "Arsenal"
}



Response:

{
"success": true,
"data": {
"1x2": {...},
"1x": {...},
"12": {...},
"x2": {...},
"goals_match": {...},
"goals_team": {...},
"cards": {...}
}
}


### 3. POST /retrain_api.php

Trigger model retraining.

Request body:

{
"action": "retrain"
}



Response:

{
"success": true,
"message": "Models retrained successfully"
}



Or error messages if failed.



## Notes

- API expects HTTPS requests
- All JSON input and output
- Model retraining can take 5-10 minutes
- Remove `.htaccess` or enable `AllowOverride` in Apache config