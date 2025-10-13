# Football Prediction System - User Guide

## Overview

The Football Prediction System uses machine learning (XGBoost) to predict match outcomes based on historical data, team form, head-to-head records, and referee tendencies.

## Accessing the System

Open your web browser and navigate to:
http://localhost/pyethone/scripts/bet/gui/index.html

text

## Making Predictions

### Step 1: Select Teams

1. Click the **Home Team** dropdown
2. Choose the home team from the list
3. Click the **Away Team** dropdown
4. Choose the away team (must be different from home team)

### Step 2: Generate Predictions

Click the **"Get Predictions"** button. The system will:
- Calculate team statistics
- Load trained models
- Generate predictions (takes 2-5 seconds)

### Step 3: View Results

Predictions are organized in 4 tabs:

#### **1X2 Results Tab**

Shows probabilities for match outcome:
- **Home Win (1)**: Probability and odds for home victory
- **Draw (X)**: Probability and odds for draw
- **Away Win (2)**: Probability and odds for away victory

**How to read:**
- **Percentage**: Model's confidence (e.g., 45% = 45% chance)
- **Odds**: Decimal odds format (e.g., 2.22 = bet £1 to win £2.22)
- **Progress bars**: Visual representation of probabilities
- **Predicted Outcome**: Most likely result
- **Confidence badge**: 
  - High (≥65%): Strong prediction
  - Medium (50-65%): Moderate certainty
  - Low (<50%): Uncertain outcome

#### **Combined Bets Tab**

Shows combined outcome predictions:
- **1X**: Home win OR draw
- **12**: Either team wins (no draw)
- **X2**: Draw OR away win

Each shows probability, odds, and Yes/No prediction.

#### **Goals Tab**

**Match Totals** - Over/Under predictions:
- **Over/Under 0.5**: At least 1 goal vs 0 goals
- **Over/Under 1.5**: 2+ goals vs 0-1 goals
- **Over/Under 2.5**: 3+ goals vs 0-2 goals (most popular)

Each shows:
- Over probability and odds
- Under probability and odds
- Predicted outcome

**Team-Specific Goals**:
- Probabilities for each team to score Over 0.5, 1.5, 2.5 goals
- Useful for "Both Teams To Score" (BTTS) bets

#### **Cards Tab**

Predicts number of yellow + red cards:
- **Total Match Cards**: Expected cards for entire match
- **Home Team Cards**: Expected cards for home team
- **Away Team Cards**: Expected cards for away team

**Note**: Based on team discipline and referee tendencies.

## Understanding Predictions

### Probability vs Odds

- **Probability (%)**: Model's confidence
  - 50% = coin flip
  - 75% = strong likelihood
  - 90%+ = very confident
  
- **Decimal Odds**: Potential return
  - 2.00 = 50% probability (2x return)
  - 1.50 = 66.7% probability
  - 3.00 = 33.3% probability

### Confidence Levels

The system considers predictions "reliable" when:
- Confidence ≥ 65% for main outcome
- Combined outcomes show consistent patterns
- Goal predictions align with team statistics

### When to Trust Predictions

**High reliability scenarios:**
- Teams with extensive match history
- Clear form differences (one team in great form, other struggling)
- Strong head-to-head patterns
- Recent matches with similar statistics

**Lower reliability scenarios:**
- New team matchups (limited head-to-head)
- Mid-season when form is fluctuating
- Teams with inconsistent recent performance

## Model Retraining

### When to Retrain

Retrain models after:
- Adding new match results (weekly during season)
- Significant team changes (transfers, manager changes)
- Every 10-15 new matches

### How to Retrain

1. **Add new data**: Update `data/E0_1926_consolidated.csv` with new matches
2. **Click "Retrain Models"** button in GUI
3. **Confirm**: Process takes 5-10 minutes
4. **Wait**: Page will reload automatically when complete

**Alternative (Command Line)**:
cd /var/www/html/pyethone/scripts/bet
source /var/www/html/pyethone/pye_venv/bin/activate
python models/feature_engineering.py
python models/train_models.py

text

## Tips for Best Results

1. **Check recent form**: Models weight recent matches more heavily
2. **Consider context**: Injuries, suspensions not in historical data
3. **Compare multiple matchups**: Look for value in odds
4. **Track accuracy**: Keep records to validate model performance
5. **Use conservatively**: Models predict probabilities, not certainties

## Common Questions

**Q: Why do probabilities sometimes seem off?**  
A: Models use historical patterns. Unexpected events (red cards, injuries mid-game) aren't predictable.

**Q: Can I add more teams?**  
A: Yes! Add them to `teams.csv` and ensure match data exists for them.

**Q: What's the model accuracy?**  
A: Check `logs/training_logs.txt` for model-specific accuracy. Typically:
- 1X2: 55-65% accuracy
- Over/Under: 60-70% accuracy
- Cards: ±0.8 cards MAE

**Q: Why do some predictions show 999 odds?**  
A: Probability is very close to 0% (extremely unlikely outcome).

## Responsible Use

- This system is for **educational/analytical purposes**
- Predictions are **statistical estimates**, not guarantees
- Past performance doesn't guarantee future results
- Always verify with current team news and conditions

## Support

For issues or questions:
1. Check logs: `logs/training_logs.txt` and `logs/retraining.log`
2. Verify data files are up to date
3. Ensure models are trained (check `models/saved_models/`)