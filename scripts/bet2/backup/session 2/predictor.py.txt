"""
Predictor Service - ENHANCED v3.0
Generates predictions using opponent-aware features
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Predictor:
    """
    Generates predictions for football matches with opponent context

    Usage:
        predictor = Predictor(model_manager, data_loader, feature_engineer)
        prediction = predictor.predict_match('Arsenal', 'Chelsea')
    """

    def __init__(self, model_manager, data_loader, feature_engineer):
        """Initialize Predictor with pre-generated features"""
        self.model_manager = model_manager
        self.data_loader = data_loader
        self.feature_engineer = feature_engineer

        # Load all models
        self.models = self.model_manager.get_all_models()

        # Pre-generate features from historical data
        logger.info(
            "Pre-loading and generating features from historical data...")
        self.historical_features = self._preload_features()
        logger.info(
            f"Features ready for {len(self.historical_features['team_name'].unique())} teams")

    def _preload_features(self) -> pd.DataFrame:
        """Pre-generate features from all historical data"""
        seasons = self.data_loader.get_available_seasons()
        df = self.data_loader.load_multiple_seasons(seasons)
        df_with_features = self.feature_engineer.generate_features(df)
        return df_with_features

    def _calculate_certainty(self, probabilities: dict, prediction_type: str = 'multi') -> tuple:
        """
        Calculate prediction certainty based on probability distribution
        
        Args:
            probabilities: Dict of outcome probabilities
            prediction_type: 'multi' (3+ outcomes) or 'binary' (2 outcomes)
        
        Returns:
            (certainty_score, certainty_level)
        """
        probs_sorted = sorted(probabilities.values(), reverse=True)
        max_prob = probs_sorted[0]

        if prediction_type == 'multi' and len(probs_sorted) >= 2:
            # Multi-class: certainty = margin between 1st and 2nd place
            second_prob = probs_sorted[1]
            margin = max_prob - second_prob

            # Normalize margin (can range from 0 to ~0.9)
            # Scale it to make it more interpretable
            certainty = min(margin * 1.5, 1.0)

        elif prediction_type == 'binary' and len(probs_sorted) >= 2:
            # Binary: certainty = how far from 50/50
            margin = abs(max_prob - 0.5)
            certainty = margin * 2  # Scale to 0-1 range

        else:
            # Fallback: use max probability
            certainty = max_prob

        # Certainty levels
        if certainty >= 0.7:
            level = "Very High"
        elif certainty >= 0.5:
            level = "High"
        elif certainty >= 0.3:
            level = "Medium"
        elif certainty >= 0.15:
            level = "Low"
        else:
            level = "Very Low"

        return round(certainty, 4), level


    def predict_match(self, home_team: str, away_team: str) -> Dict:
        """
        Generate prediction for a match

        Args:
            home_team: Home team name
            away_team: Away team name

        Returns:
            Dictionary with predictions and probabilities
        """
        logger.info(f"Generating prediction: {home_team} vs {away_team}")

        try:
            # Build feature vector for this matchup
            features = self._build_match_features(home_team, away_team)

            # Get predictions
            match_result = self._predict_match_result(features)
            double_chance = self._calculate_double_chance(match_result)
            goals = self._predict_goals(features)
            # CHANGED - added team names
            cards = self._predict_cards(features, home_team, away_team)

            # Build response
            prediction = {
                'success': True,
                'match': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': datetime.now().isoformat()
                },
                'predictions': {
                    'match_result': match_result,
                    'double_chance': double_chance,
                    'goals': goals,
                    'cards': cards  # NEW
                },
                'timestamp': datetime.now().isoformat()
            }

            return prediction

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _build_match_features(self, home_team: str, away_team: str) -> np.ndarray:
        """
        Build feature vector for a specific matchup
        
        This combines:
        - Home team's recent features
        - Away team's recent features (as opponent features)
        - Differential features (home - away)
        - Cross features (combined metrics)
        """
        # Get feature names
        feature_names = self.feature_engineer.get_model_feature_names()

        # Get home team's most recent match features
        home_data = self.historical_features[
            self.historical_features['team_name'] == home_team
        ].sort_values('date')

        if len(home_data) == 0:
            raise ValueError(f"No historical data found for {home_team}")

        home_latest = home_data.iloc[-1]

        # Get away team's most recent match features
        away_data = self.historical_features[
            self.historical_features['team_name'] == away_team
        ].sort_values('date')

        if len(away_data) == 0:
            raise ValueError(f"No historical data found for {away_team}")

        away_latest = away_data.iloc[-1]

        # Build feature vector
        features = {}

        for feat in feature_names:
            if feat.startswith('opp_'):
                # Opponent feature - use away team's base feature
                base_feat = feat.replace('opp_', '')
                features[feat] = away_latest.get(base_feat, 0)

            elif feat.startswith('diff_'):
                # Differential feature - home minus away
                base_feat = feat.replace('diff_', '')
                home_val = home_latest.get(base_feat, 0)
                away_val = away_latest.get(base_feat, 0)
                features[feat] = home_val - away_val

            elif feat in ['combined_goal_threat', 'combined_def_weakness',
                          'btts_likelihood', 'total_goals_expected', 'xg_total_expected']:
                # Cross features - recalculate from both teams
                if feat == 'combined_goal_threat':
                    features[feat] = (
                        home_latest.get('goals_for_L5_mean', 0) +
                        away_latest.get('goals_for_L5_mean', 0)
                    ) / 2
                elif feat == 'combined_def_weakness':
                    features[feat] = (
                        home_latest.get('goals_against_L5_mean', 0) +
                        away_latest.get('goals_against_L5_mean', 0)
                    ) / 2
                elif feat == 'btts_likelihood':
                    features[feat] = (
                        (home_latest.get('goals_for_L5_mean', 0) *
                         away_latest.get('goals_against_L5_mean', 0)) +
                        (away_latest.get('goals_for_L5_mean', 0) *
                         home_latest.get('goals_against_L5_mean', 0))
                    ) / 2
                elif feat == 'total_goals_expected':
                    features[feat] = (
                        home_latest.get('goals_for_L5_mean', 0) +
                        away_latest.get('goals_for_L5_mean', 0)
                    )
                elif feat == 'xg_total_expected':
                    features[feat] = (
                        home_latest.get('xg_for_L5_mean', 0) +
                        away_latest.get('xg_for_L5_mean', 0)
                    )

            else:
                # Regular team feature - use home team's value
                features[feat] = home_latest.get(feat, 0)

        # Override venue to Home
        if 'is_home' in features:
            features['is_home'] = 1.0

        # Convert to array in correct order
        feature_array = np.array([features.get(f, 0) for f in feature_names])

        # Handle NaNs
        feature_array = np.nan_to_num(feature_array, nan=0.0)

        return feature_array.reshape(1, -1)

    def _predict_match_result(self, features: np.ndarray) -> Dict:
        """Predict match result (1X2) - supports ensemble"""
        model = self.models['match_result']

        # Check if ensemble
        if isinstance(model, dict) and model.get('type') == 'ensemble':
            # Ensemble prediction
            xgb_proba = model['xgboost'].predict_proba(features)[0]
            rf_proba = model['randomforest'].predict_proba(features)[0]

            # Weighted average (60% RF, 40% XGB based on performance)
            probabilities = 0.6 * rf_proba + 0.4 * xgb_proba
            prediction = int(np.argmax(probabilities))

            logger.debug("Used ensemble prediction (60% RF, 40% XGB)")
        else:
            # Single model prediction
            probabilities = model.predict_proba(features)[0]
            prediction = model.predict(features)[0]

        result_map = {0: 'Home Win', 1: 'Draw', 2: 'Away Win'}
        predicted_result = result_map[prediction]

        # Calculate certainty (margin-based)
        prob_dict = {
            'home_win': float(probabilities[0]),
            'draw': float(probabilities[1]),
            'away_win': float(probabilities[2])
        }
        certainty, certainty_level = self._calculate_certainty(
            prob_dict, 'multi')

        return {
            'prediction': predicted_result,
            'probabilities': prob_dict,
            'certainty': certainty,
            'certainty_level': certainty_level
        }

    def _predict_goals(self, features: np.ndarray) -> Dict:
        """Predict goals (Over/Under and BTTS) - supports ensemble"""
        goals_predictions = {}

        # Over/Under predictions - map display names to file names
        thresholds = {
            'over_0.5': 'over_0_5',
            'over_1.5': 'over_1_5',
            'over_2.5': 'over_2_5',
            'over_3.5': 'over_3_5'
        }

        for display_name, file_name in thresholds.items():
            try:
                model = self.models['goals'][file_name]

                # Check if ensemble
                if isinstance(model, dict) and model.get('type') == 'ensemble':
                    xgb_proba = model['xgboost'].predict_proba(features)[0][1]
                    rf_proba = model['randomforest'].predict_proba(features)[
                        0][1]
                    probability = 0.6 * rf_proba + 0.4 * xgb_proba
                    prediction = 1 if probability > 0.5 else 0
                else:
                    probability = model.predict_proba(features)[0][1]
                    prediction = model.predict(features)[0]

                # Calculate certainty
                prob_dict = {'over': float(
                    probability), 'under': float(1 - probability)}
                certainty, certainty_level = self._calculate_certainty(
                    prob_dict, 'binary')

                goals_predictions[display_name] = {
                    'prediction': 'Over' if prediction == 1 else 'Under',
                    'probability_over': float(probability),
                    'probability_under': float(1 - probability),
                    'certainty': certainty,
                    'certainty_level': certainty_level
                }

            except (KeyError, FileNotFoundError, Exception) as e:
                logger.warning(f"Model for {display_name} not available: {e}")

        # BTTS prediction
        try:
            btts_model = self.models['goals']['btts']

            if isinstance(btts_model, dict) and btts_model.get('type') == 'ensemble':
                xgb_proba = btts_model['xgboost'].predict_proba(features)[0][1]
                rf_proba = btts_model['randomforest'].predict_proba(features)[
                    0][1]
                probability = 0.6 * rf_proba + 0.4 * xgb_proba
                prediction = 1 if probability > 0.5 else 0
            else:
                probability = btts_model.predict_proba(features)[0][1]
                prediction = btts_model.predict(features)[0]

            # Calculate certainty
            prob_dict = {'yes': float(probability),
                         'no': float(1 - probability)}
            certainty, certainty_level = self._calculate_certainty(
                prob_dict, 'binary')

            goals_predictions['btts'] = {
                'prediction': 'Yes' if prediction == 1 else 'No',
                'probability_yes': float(probability),
                'probability_no': float(1 - probability),
                'certainty': certainty,
                'certainty_level': certainty_level
            }

        except (KeyError, FileNotFoundError, Exception) as e:
            logger.warning(f"BTTS model not available: {e}")

        return goals_predictions

    def _predict_cards(self, features: np.ndarray, home_team: str, away_team: str) -> Dict:
        """
        Predict cards for both teams separately
        
        Args:
            features: Feature vector (from home team perspective)
            home_team: Home team name
            away_team: Away team name
        """
        cards_predictions = {
            'total_match': {},
            'home_team': {'team_name': home_team},
            'away_team': {'team_name': away_team}
        }

        # ==========================================
        # TOTAL MATCH CARDS (both teams combined)
        # ==========================================
        total_thresholds = {
            'over_2.5': 'total_cards_over_2_5',
            'over_3.5': 'total_cards_over_3_5',
            'over_4.5': 'total_cards_over_4_5'
        }

        for display_name, file_name in total_thresholds.items():
            try:
                model = self.models['cards'][file_name]

                if isinstance(model, dict) and model.get('type') == 'ensemble':
                    xgb_proba = model['xgboost'].predict_proba(features)[0][1]
                    rf_proba = model['randomforest'].predict_proba(features)[
                        0][1]
                    probability = 0.6 * rf_proba + 0.4 * xgb_proba
                    prediction = 1 if probability > 0.5 else 0
                else:
                    probability = model.predict_proba(features)[0][1]
                    prediction = model.predict(features)[0]

                prob_dict = {'over': float(probability), 'under': float(1 - probability)}
                certainty, certainty_level = self._calculate_certainty(prob_dict, 'binary')
                
                cards_predictions['total_match'][display_name] = {
                    'prediction': 'Over' if prediction == 1 else 'Under',
                    'probability_over': float(probability),
                    'probability_under': float(1 - probability),
                    'certainty': certainty,
                    'certainty_level': certainty_level
                }


            except (KeyError, FileNotFoundError, Exception) as e:
                logger.warning(
                    f"Model for total {display_name} not available: {e}")

        # ==========================================
        # HOME TEAM CARDS
        # ==========================================
        team_thresholds = {
            'over_1.5': 'team_cards_over_1_5',
            'over_2.5': 'team_cards_over_2_5'
        }

        for display_name, file_name in team_thresholds.items():
            try:
                model = self.models['cards'][file_name]

                if isinstance(model, dict) and model.get('type') == 'ensemble':
                    xgb_proba = model['xgboost'].predict_proba(features)[0][1]
                    rf_proba = model['randomforest'].predict_proba(features)[
                        0][1]
                    probability = 0.6 * rf_proba + 0.4 * xgb_proba
                    prediction = 1 if probability > 0.5 else 0
                else:
                    probability = model.predict_proba(features)[0][1]
                    prediction = model.predict(features)[0]

                # Calculate certainty
                prob_dict = {'over': float(probability), 'under': float(1 - probability)}
                certainty, certainty_level = self._calculate_certainty(prob_dict, 'binary')
                
                cards_predictions['home_team'][display_name] = {
                    'prediction': 'Over' if prediction == 1 else 'Under',
                    'probability_over': float(probability),
                    'probability_under': float(1 - probability),
                    'certainty': certainty,
                    'certainty_level': certainty_level
                }


            except (KeyError, FileNotFoundError, Exception) as e:
                logger.warning(
                    f"Home team cards {display_name} not available: {e}")

        # ==========================================
        # AWAY TEAM CARDS (using opponent features)
        # ==========================================
        # Build away team feature vector (swap home/away perspective)
        try:
            away_features = self._build_match_features(away_team, home_team)

            for display_name, file_name in team_thresholds.items():
                try:
                    model = self.models['cards'][file_name]

                    if isinstance(model, dict) and model.get('type') == 'ensemble':
                        xgb_proba = model['xgboost'].predict_proba(away_features)[
                            0][1]
                        rf_proba = model['randomforest'].predict_proba(away_features)[
                            0][1]
                        probability = 0.6 * rf_proba + 0.4 * xgb_proba
                        prediction = 1 if probability > 0.5 else 0
                    else:
                        probability = model.predict_proba(away_features)[0][1]
                        prediction = model.predict(features)[0]

                    # Calculate certainty
                    prob_dict = {'over': float(
                        probability), 'under': float(1 - probability)}
                    certainty, certainty_level = self._calculate_certainty(
                        prob_dict, 'binary')

                    cards_predictions['away_team'][display_name] = {
                        'prediction': 'Over' if prediction == 1 else 'Under',
                        'probability_over': float(probability),
                        'probability_under': float(1 - probability),
                        'certainty': certainty,
                        'certainty_level': certainty_level
                    }

                except (KeyError, FileNotFoundError, Exception) as e:
                    logger.warning(
                        f"Away team cards {display_name} not available: {e}")

        except Exception as e:
            logger.warning(
                f"Could not generate away team cards prediction: {e}")

        return cards_predictions



    def _calculate_double_chance(self, match_result: Dict) -> Dict:
        """
        Calculate double chance probabilities from match result
        
        Double chance betting options:
        - 1X: Home win OR Draw
        - X2: Draw OR Away win
        - 12: Home win OR Away win (no draw)
        """
        probs = match_result['probabilities']

        prob_1x = probs['home_win'] + probs['draw']
        prob_x2 = probs['draw'] + probs['away_win']
        prob_12 = probs['home_win'] + probs['away_win']

        # Find best option
        best_option = max(
            ('1X', prob_1x),
            ('X2', prob_x2),
            ('12', prob_12),
            key=lambda x: x[1]
        )

        prob_dict = {
            '1X': float(prob_1x),
            'X2': float(prob_x2),
            '12': float(prob_12)
        }
        certainty, certainty_level = self._calculate_certainty(
            prob_dict, 'multi')

        return {
            'prediction': best_option[0],
            'probabilities': prob_dict,
            'certainty': certainty,
            'certainty_level': certainty_level
        }


    @staticmethod
    def _get_confidence_level(confidence: float) -> str:
        """Convert confidence to human-readable level"""
        if confidence >= 0.75:
            return 'Very High'
        elif confidence >= 0.65:
            return 'High'
        elif confidence >= 0.55:
            return 'Medium'
        else:
            return 'Low'
