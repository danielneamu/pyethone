# Next Session - Priority Roadmap

## Immediate Next Steps (Session 2)

### **Option A: Prediction Tracking & Database** (Recommended)
**Goal:** Track predictions and measure accuracy over time

**Tasks:**
1. Create MySQL/SQLite database schema
   - `predictions` table (match, teams, predictions, certainty, timestamp)
   - `actual_results` table (match, actual_outcome, goals, cards)
   - `accuracy_metrics` table (aggregated performance)

2. Update `predict_api.php` to save predictions
   - Insert prediction to DB after generation
   - Store all markets (1X2, goals, cards)

3. Build results collection script
   - Fetch actual match results from FBRef/API
   - Match predictions with results
   - Calculate accuracy metrics

4. Create analytics dashboard (`public/analytics.php`)
   - Overall accuracy by market
   - Accuracy by certainty level
   - Model comparison (XGB vs RF vs Ensemble)
   - Time-series accuracy trends

**Expected Outcome:** Know which predictions are most reliable, improve model trust

---

### **Option B: Multi-Competition Support**
**Goal:** Add La Liga, Serie A, Bundesliga, Ligue 1

**Tasks:**
1. Add competition data (scrape 3 seasons each)
2. Train models for each league (same pipeline)
3. Update GUI with competition selector
4. Compare model performance across leagues

**Expected Outcome:** Predict matches from 5 major leagues

---

### **Option C: Batch Predictions**
**Goal:** Predict entire matchweek at once

**Tasks:**
1. Create batch prediction API endpoint
2. Build matchweek selection interface
3. Generate comparison table (all matches side-by-side)
4. CSV export functionality

**Expected Outcome:** Predict 10 matches in one click

---

## Future Sessions (3-6)

### **Session 3: Value Bet Finder**
- Scrape bookmaker odds (Oddsportal/BetExplorer)
- Compare model probability vs market odds
- Highlight value bets (e.g., model says 60% but odds imply 45%)
- Calculate expected value (EV)

### **Session 4: Prediction Explanations**
- Integrate SHAP values
- Show: "Why did model predict home win?"
- Display top 5 influential features
- Feature importance visualization

### **Session 5: Enhanced UX**
- Team badges/logos
- Head-to-head history
- Team form indicators (last 5 games)
- League table integration
- Dark mode

### **Session 6: Production Deployment**
- Environment variables (.env files)
- User authentication
- Rate limiting
- SSL/HTTPS setup
- Monitoring (Sentry, logs)
- Backups & recovery
- Docker containerization (optional)

---

## Quick Wins (Can Do Anytime)
- Add model retraining schedule (weekly cron)
- Email notifications for predictions
- Telegram bot integration
- Export predictions to PDF
- Add injury/suspension data
- Include weather conditions