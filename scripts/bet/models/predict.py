"""
Prediction Module
Loads trained models and generates predictions for new matchups
"""

import pandas as pd
import numpy as np
import pickle
import os
import json
import sys
sys.path.append('/var/www/html/pyethone/scripts/bet')
from config.config import *
from models.feature_engineering import FeatureEngineer


class MatchPredictor:
    """
    Load models and predict outcomes for team matchups
    """
    
    def __init__(self):
        """Load all trained models"""
        self.models = {}
        self.metadata = None
        self._load_models()
        
        # Load historical data for feature calculation
        self.matches_df = pd.read_csv(MATCHES_FILE)
        self.engineer = FeatureEngineer(self.matches_df)
    
    def _load_models(self):
        """Load all saved models from disk"""
        print("Loading models...")
        
        # Load metadata
        meta_file = os.path.join(MODEL_DIR, 'model_metadata.pkl')
        with open(meta_file, 'rb') as f:
            self.metadata = pickle.load(f)
        
        # Load each model
        for model_name, filename in MODEL_FILES.items():
            filepath = os.path.join(MODEL_DIR, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.models[model_name] = pickle.load(f)
                print(f"Loaded: {model_name}")
        
        print(f"Models loaded: {len(self.models)}")
    
    def _build_features_for_matchup(self, home_team, away_team):
        """
        Generate feature vector for a specific matchup
        Uses most recent data from historical matches
        
        Returns:
            DataFrame with single row of features
        """
        # Use current date as reference
        current_date = pd.Timestamp.now()
        
        # Calculate features (same logic as training)
        home_form = self.engineer._calculate_team_form(home_team, current_date, 'home')
        away_form = self.engineer._calculate_team_form(away_team, current_date, 'away')
        home_overall = self.engineer._calculate_team_form(home_team, current_date, 'all')
        away_overall = self.engineer._calculate_team_form(away_team, current_date, 'all')
        h2h = self.engineer._calculate_h2h(home_team, away_team, current_date)
        
        # Use average referee stats (no specific referee for prediction)
        ref_stats = {
            'ref_avg_yellow': 3.0,
            'ref_avg_red': 0.2
        }
        
        # Get latest odds (use neutral 33/33/33 if not available)
        latest_match = self.matches_df.tail(1).iloc[0]
        odds_home = latest_match.get('AvgH', 3.0)
        odds_draw = latest_match.get('AvgD', 3.0)
        odds_away = latest_match.get('AvgA', 3.0)
        odds_over25 = latest_match.get('Avg>2.5', 2.0)
        
        # Build feature dictionary
        features = {
            'home_form_win_rate': home_form['win_rate'],
            'home_form_draw_rate': home_form['draw_rate'],
            'home_form_goals_scored': home_form['goals_per_match'],
            'home_form_goals_conceded': home_form['goals_conceded_per_match'],
            'away_form_win_rate': away_form['win_rate'],
            'away_form_draw_rate': away_form['draw_rate'],
            'away_form_goals_scored': away_form['goals_per_match'],
            'away_form_goals_conceded': away_form['goals_conceded_per_match'],
            'home_overall_win_rate': home_overall['win_rate'],
            'away_overall_win_rate': away_overall['win_rate'],
            'h2h_matches': h2h['h2h_matches'],
            'h2h_home_win_rate': h2h['h2h_home_wins'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.33,
            'h2h_draw_rate': h2h['h2h_draws'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.33,
            'h2h_avg_goals': h2h['h2h_avg_goals'],
            'ref_avg_yellow': ref_stats['ref_avg_yellow'],
            'ref_avg_red': ref_stats['ref_avg_red'],
            'odds_home': odds_home,
            'odds_draw': odds_draw,
            'odds_away': odds_away,
            'odds_over25': odds_over25
        }
        
        return pd.DataFrame([features])[self.metadata['feature_columns']]
    
    def predict_match(self, home_team, away_team):
        """
        Generate complete predictions for a matchup
        
        Args:
            home_team: Home team name
            away_team: Away team name
        
        Returns:
            Dict with all predictions and probabilities
        """
        print(f"\nPredicting: {home_team} vs {away_team}")
        
        # Build features
        X = self._build_features_for_matchup(home_team, away_team)
        
        predictions = {
            'home_team': home_team,
            'away_team': away_team
        }
        
        # 1X2 Prediction
        model_1x2 = self.models['1x2']['model']
        probs_1x2 = model_1x2.predict_proba(X)[0]
        reverse_map = self.models['1x2']['reverse_map']
        
        predictions['1x2'] = {
            'home_win_prob': float(probs_1x2[0]) * 100,
            'draw_prob': float(probs_1x2[1]) * 100,
            'away_win_prob': float(probs_1x2[2]) * 100,
            'predicted_outcome': reverse_map[np.argmax(probs_1x2)],
            'confidence': float(np.max(probs_1x2)) * 100,
            'home_win_odds': round(1 / probs_1x2[0], 2) if probs_1x2[0] > 0 else 999,
            'draw_odds': round(1 / probs_1x2[1], 2) if probs_1x2[1] > 0 else 999,
            'away_win_odds': round(1 / probs_1x2[2], 2) if probs_1x2[2] > 0 else 999
        }
        
        # Combined outcomes
        for outcome in ['1x', '12', 'x2']:
            model = self.models[outcome]['model']
            prob = model.predict_proba(X)[0][1]  # Probability of "yes"
            
            predictions[outcome] = {
                'probability': float(prob) * 100,
                'odds': round(1 / prob, 2) if prob > 0 else 999,
                'prediction': 'Yes' if prob > 0.5 else 'No'
            }
        
        # Over/Under goals (match totals)
        predictions['goals_match'] = {}
        
        for threshold in ['05', '15', '25']:
            model = self.models[f'over_{threshold}']['model']
            prob_over = model.predict_proba(X)[0][1]
            
            threshold_val = float(threshold) / 10
            
            predictions['goals_match'][f'over_{threshold}'] = {
                'threshold': threshold_val,
                'over_prob': float(prob_over) * 100,
                'under_prob': float(1 - prob_over) * 100,
                'prediction': 'Over' if prob_over > 0.5 else 'Under',
                'over_odds': round(1 / prob_over, 2) if prob_over > 0 else 999,
                'under_odds': round(1 / (1 - prob_over), 2) if prob_over < 1 else 999
            }
        
        # Team-specific goals
        predictions['goals_team'] = {}
        
        for threshold in ['05', '15', '25']:
            model = self.models[f'team_over_{threshold}']['model']
            prob_home_over = model.predict_proba(X)[0][1]
            
            threshold_val = float(threshold) / 10
            
            predictions['goals_team'][f'home_over_{threshold}'] = {
                'team': home_team,
                'threshold': threshold_val,
                'probability': float(prob_home_over) * 100,
                'odds': round(1 / prob_home_over, 2) if prob_home_over > 0 else 999
            }
            
            # Approximate away team (inverse correlation - simplified)
            prob_away_over = prob_home_over * 0.8  # Simplified
            
            predictions['goals_team'][f'away_over_{threshold}'] = {
                'team': away_team,
                'threshold': threshold_val,
                'probability': float(prob_away_over) * 100,
                'odds': round(1 / prob_away_over, 2) if prob_away_over > 0 else 999
            }
        
        # Cards predictions
        model_cards = self.models['cards']['model']
        predicted_total_cards = model_cards.predict(X)[0]
        
        model_team_cards = self.models['team_cards']['model']
        predicted_home_cards = model_team_cards.predict(X)[0]
        predicted_away_cards = predicted_total_cards - predicted_home_cards
        
        predictions['cards'] = {
            'total_cards': round(float(predicted_total_cards), 1),
            'home_cards': round(float(predicted_home_cards), 1),
            'away_cards': round(float(predicted_away_cards), 1)
        }
        
        return predictions
    
    def _convert_to_json_serializable(self, obj):
        """
        Recursively convert numpy types to native Python types
        
        Args:
            obj: Object to convert (dict, list, numpy type, etc.)
        
        Returns:
            JSON-serializable object
        """
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def predict_to_json(self, home_team, away_team, output_file=None):
        """
        Predict and save as JSON
        
        Args:
            home_team: Home team
            away_team: Away team
            output_file: Optional file path to save JSON
        
        Returns:
            JSON string
        """
        predictions = self.predict_match(home_team, away_team)
        
        # Convert numpy types to native Python types for JSON serialization
        predictions = self._convert_to_json_serializable(predictions)
        
        json_output = json.dumps(predictions, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            print(f"Predictions saved to: {output_file}")
        
        return json_output


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python predict.py <home_team> <away_team>")
        print("Example: python predict.py Liverpool 'Man City'")
        sys.exit(1)
    
    home_team = sys.argv[1]
    away_team = sys.argv[2]
    
    predictor = MatchPredictor()
    result = predictor.predict_to_json(home_team, away_team)
    
    print("\n" + "="*60)
    print("PREDICTIONS")
    print("="*60)
    print(result)
