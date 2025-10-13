# Football Prediction System - API Documentation

## Base URL

http://localhost/pyethone/scripts/bet/api/

text

## Endpoints

### 1. Get Available Teams

**Endpoint**: `predict_api.php?action=teams`  
**Method**: GET  
**Description**: Retrieve list of all available teams

**Request**:
curl "http://localhost/pyethone/scripts/bet/api/predict_api.php?action=teams"

text

**Response**:
{
"success": true,
"teams": [
{
"name": "Arsenal",
"short_name": "ARS"
},
{
"name": "Liverpool",
"short_name": "LIV"
}
]
}

text

---

### 2. Get Match Predictions

**Endpoint**: `predict_api.php`  
**Method**: POST  
**Description**: Generate predictions for specified matchup

**Request**:
curl -X POST http://localhost/pyethone/scripts/bet/api/predict_api.php
-H "Content-Type: application/json"
-d '{
"home_team": "Liverpool",
"away_team": "Arsenal"
}'

text

**Response**:
{
"success": true,
"data": {
"home_team": "Liverpool",
"away_team": "Arsenal",
"1x2": {
"home_win_prob": 52.3,
"draw_prob": 25.1,
"away_win_prob": 22.6,
"predicted_outcome": "H",
"confidence": 52.3,
"home_win_odds": 1.91,
"draw_odds": 3.98,
"away_win_odds": 4.42
},
"1x": {
"probability": 77.4,
"odds": 1.29,
"prediction": "Yes"
},
"12": {
"probability": 74.9,
"odds": 1.33,
"prediction": "Yes"
},
"x2": {
"probability": 47.7,
"odds": 2.10,
"prediction": "No"
},
"goals_match": {
"over_05": {
"threshold": 0.5,
"over_prob": 95.2,
"under_prob": 4.8,
"prediction": "Over",
"over_odds": 1.05,
"under_odds": 20.83
},
"over_15": {
"threshold": 1.5,
"over_prob": 78.6,
"under_prob": 21.4,
"prediction": "Over",
"over_odds": 1.27,
"under_odds": 4.67
},
"over_25": {
"threshold": 2.5,
"over_prob": 54.2,
"under_prob": 45.8,
"prediction": "Over",
"over_odds": 1.84,
"under_odds": 2.18
}
},
"goals_team": {
"home_over_05": {
"team": "Liverpool",
"threshold": 0.5,
"probability": 88.5,
"odds": 1.13
},
"home_over_15": {
"team": "Liverpool",
"threshold": 1.5,
"probability": 62.3,
"odds": 1.61
},
"home_over_25": {
"team": "Liverpool",
"threshold": 2.5,
"probability": 32.1,
"odds": 3.11
},
"away_over_05": {
"team": "Arsenal",
"threshold": 0.5,
"probability": 70.8,
"odds": 1.41
},
"away_over_15": {
"team": "Arsenal",
"threshold": 1.5,
"probability": 49.8,
"odds": 2.01
},
"away_over_25": {
"team": "Arsenal",
"threshold": 2.5,
"probability": 25.7,
"odds": 3.89
}
},
"cards": {
"total_cards": 4.2,
"home_cards": 2.1,
"away_cards": 2.1
}
}
}

text

**Error Response**:
{
"success": false,
"error": "Invalid home team: InvalidTeam"
}

text

---

### 3. Retrain Models

**Endpoint**: `retrain_api.php`  
**Method**: POST  
**Description**: Trigger model retraining process

**Request**:
curl -X POST http://localhost/pyethone/scripts/bet/api/retrain_api.php
-H "Content-Type: application/json"
-d '{"action": "retrain"}'

text

**Response (Success)**:
{
"success": true,
"message": "Models retrained successfully",
"timestamp": "2025-10-12 19:45:23",
"output": {
"feature_generation": "Features saved...",
"model_training": "Training complete..."
}
}

text

**Response (Error)**:
{
"success": false,
"error": "Model training failed: ...",
"stage": "feature_generation"
}

text

---

### 4. Get Retraining Info

**Endpoint**: `retrain_api.php`  
**Method**: GET  
**Description**: Get last retraining timestamp

**Request**:
curl "http://localhost/pyethone/scripts/bet/api/retrain_api.php"

text

**Response**:
{
"success": true,
"info": {
"last_retrain": "2025-10-12 14:30:15",
"last_log_entry": "[2025-10-12 14:30:15] Retraining completed successfully"
}
}

text

---

## Error Codes

| HTTP Status | Error Type | Description |
|-------------|-----------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Missing or invalid parameters |
| 500 | Server Error | Python execution failed or model error |

## Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- 10 predictions per minute per IP
- 1 retraining per hour

## Data Models

### Team Object
{
"name": "Full team name",
"short_name": "3-letter code"
}

text

### Prediction Outcome Values
- `H` = Home win
- `D` = Draw
- `A` = Away win

### Odds Format
All odds in decimal format (European style):
- 2.00 = Even money (50% probability)
- 1.50 = Favorites
- 3.00+ = Underdogs

## Integration Examples

### JavaScript (Fetch API)
async function getPrediction(homeTeam, awayTeam) {
const response = await fetch('/pyethone/scripts/bet/api/predict_api.php', {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({
home_team: homeTeam,
away_team: awayTeam
})
});

const data = await response.json();
return data;
}

text

### PHP
$ch = curl_init('http://localhost/pyethone/scripts/bet/api/predict_api.php');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
'home_team' => 'Liverpool',
'away_team' => 'Arsenal'
]));

$response = curl_exec($ch);
$data = json_decode($response, true);
curl_close($ch);

text

### Python
import requests

response = requests.post(
'http://localhost/pyethone/scripts/bet/api/predict_api.php',
json={
'home_team': 'Liverpool',
'away_team': 'Arsenal'
}
)

data = response.json()
print(data['data']['1x2'])

text

## Notes

- All timestamps in `YYYY-MM-DD HH:MM:SS` format
- Retraining process can take 5-10 minutes
- Predictions cached for performance (reload after retraining)