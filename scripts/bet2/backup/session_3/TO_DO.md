Here’s a breakdown addressing both your conceptual and implementation points so everything is clear moving forward.

1. Tracking, comparing, and the impact on models
When we talk about “tracking” and “comparing models,” it means evaluation and monitoring, not live retraining.
Here’s how each step fits logically:

a. Tracking predictions and comparing to actual results
Every saved prediction gets matched later (once actual results are known).

We compute accuracy metrics like accuracy_pct, f1_score, roc_auc, etc.

This data helps monitor trends — e.g. “Ensemble is 12% more accurate than Random Forest in 1X2 over last 5 weeks.”

b. Model comparison and analytics
We'll visualize results by market: 1X2, goals, BTTS, cards.

The goal is to compare performance between models — XGBoost vs Random Forest vs Ensemble.

It does not automatically retrain models.
These comparisons guide manual retraining decisions and feature tuning.

c. Does this affect model training?
Not automatically yet, but it can once you want adaptive learning:

We can later enable “periodic retraining” using match results to re-fit models weekly or monthly.

This would use consistency scores in the database to decide if performance drift warrants retraining.

So currently — analytics are diagnostic, not self-corrective. Retraining remains manual or scheduled intentionally.


3. Analytics showing saved games
That view will be simple and highly useful:

Table view (or dashboard card) listing all saved matches.

Columns:
home_team, away_team, prediction_1x2, certainty_1x2, match_date, prediction_date

Filters: by date range, teams, or certainty level.

Optional metrics view combining overall accuracies and ROI summaries.

We’ll later extend this analytics view to include:

“Results missing” (games with no actual outcome yet)

“Model performance summary per market”

“ROI and prediction consistency over time.”

4. Next concrete steps
We can proceed like this:

Adjust predict_api.php and GUI for manual save toggle.

Create a basic analytics page listing saved predictions.

Step 3: Add Actual Match Results
Track what actually happened in matches to compare against predictions.
What to build:
Add columns to database for actual results (actual_result, actual_goals, actual_btts, actual_cards)
Create a form/interface to input actual match results when games finish
Mark predictions as "matched" once results are entered

Step 4: Calculate Prediction Accuracy
Compare predictions vs actual results to measure model performance.
What to build:
Python script to calculate accuracy metrics:
Overall accuracy % per market (1X2, Goals, BTTS, Cards)
Accuracy by certainty level (high/medium/low)
Accuracy by model type (Ensemble vs XGBoost vs Random Forest)
Display accuracy stats in analytics page

Step 5: Model Performance Comparison
See which models perform best on different markets.
What to build:
Comparison charts showing:
Ensemble vs XGBoost vs Random Forest accuracy
Which model is best for 1X2 predictions
Which model is best for Goals predictions
ROI tracking (if you add odds data)

Step 6: Adaptive Learning (Optional Advanced)
Use accuracy data to improve model selection or trigger retraining.
What to build:
Auto-retraining trigger when accuracy drops below threshold
Model confidence weighting based on recent performance
Feature importance analysis