"""
Predictor Service
Generates predictions for football matches
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Predictor:
    """
    Generates predictions for football matches

    Usage:
        from services.model_manager import ModelManager
        from services.data_loader import DataLoader
        from services.feature_engineering import FeatureEngineer

        manager = ModelManager('premier_league')
        loader = DataLoader('premier_league')
        engineer = FeatureEngineer()

        predictor = Predictor(manager, loader, engineer)
        prediction = predictor.predict_match('Arsenal', 'Chelsea', 'Home')
    """

    def __init__(self, model_manager, data_loader, feature_engineer):
        """
        Initialize Predictor

        Args:
            model_manager: ModelManager instance
            data_loader: DataLoader instance
            feature_engineer: FeatureEngineer instance
        """
        self.model_manager = model_manager
        self.data_loader = data_loader
        self.feature_engineer = feature_engineer

        # Load all models
        self.models = self.model_manager.get_all_models()

    def predict_match(
        self, 
        home_team: str, 
        away_team: str, 
        venue: str = 'Home'
    ) -> Dict:
        """
        Generate prediction for a match

        Args:
            home_team: Home team name
            away_team: Away team name
            venue: 'Home' or 'Away' (perspective for features)

        Returns:
            Dictionary with predictions and probabilities
        """
        logger.info(f"Generating prediction: {home_team} vs {away_team}")

        try:
            # Prepare match data for prediction
            match_data = self._prepare_match_data(home_team, away_team, venue)

            # Generate features
            match_features = self._generate_features(match_data)

            # Get predictions
            match_result = self._predict_match_result(match_features)
            goals = self._predict_goals(match_features)

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
                    'goals': goals
                },
                'timestamp': datetime.now().isoformat()
            }

            return prediction

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _prepare_match_data(self, home_team: str, away_team: str, venue: str) -> pd.DataFrame:
        """Prepare match data for feature generation"""

        # Load historical data to calculate features
        historical_data = self.data_loader.load_multiple_seasons(['2023-2024', '2024-2025'])

        # Create a row for the match to predict
        # We need team and opponent names to generate features
        match_row = {
            'team_name': home_team if venue == 'Home' else away_team,
            'opponent': away_team if venue == 'Home' else home_team,
            'venue': venue,
            'date': pd.Timestamp.now(),
            # Placeholder values (will not be used in features due to shift(1))
            'result': 'D',
            'goals_for': 0,
            'goals_against': 0
        }

        # Append to historical data
        match_df = pd.DataFrame([match_row])
        combined_df = pd.concat([historical_data, match_df], ignore_index=True)

        return combined_df

    def _generate_features(self, match_data: pd.DataFrame) -> np.ndarray:
        """Generate features for the match"""
        
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            with_features = self.feature_engineer.generate_features(match_data)
        
        # Get last row
        match_features = with_features.iloc[-1]
        
        # Get expected features from model
        metadata = self.model_manager.get_model_metadata('match_result')
        if metadata and 'feature_names' in metadata:
            expected_features = metadata['feature_names']
            
            # Build feature array matching trained model EXACTLY
            X_list = []
            for feat in expected_features:
                val = match_features.get(feat, 0)
                X_list.append(0 if pd.isna(val) else float(val))
            
            X = np.array(X_list).reshape(1, -1)
        else:
            # Fallback
            feature_names = self.feature_engineer.get_feature_names()
            X = match_features[feature_names].values.reshape(1, -1)
            X = np.nan_to_num(X, 0)
        
        return X

    def _predict_match_result(self, features: np.ndarray) -> Dict:
        """Predict match result (1X2)"""

        model = self.models['match_result']

        # Get probabilities
        probabilities = model.predict_proba(features)[0]

        # Get prediction
        prediction = model.predict(features)[0]

        # Map to result
        result_map = {0: 'Home Win', 1: 'Draw', 2: 'Away Win'}
        predicted_result = result_map[prediction]

        # Calculate confidence
        confidence = float(max(probabilities))

        return {
            'prediction': predicted_result,
            'probabilities': {
                'home_win': float(probabilities[0]),
                'draw': float(probabilities[1]),
                'away_win': float(probabilities[2])
            },
            'confidence': confidence,
            'confidence_level': self._get_confidence_level(confidence)
        }

    def _predict_goals(self, features: np.ndarray) -> Dict:
        """Predict goals (Over/Under and BTTS)"""

        goals_predictions = {}

        # Over/Under predictions
        for threshold in ['0.5', '1.5', '2.5', '3.5']:
            goal_type = f'over_{threshold}'

            try:
                model = self.models['goals'][goal_type]

                # Get probability
                probability = model.predict_proba(features)[0][1]  # Probability of Over
                prediction = model.predict(features)[0]

                goals_predictions[goal_type] = {
                    'prediction': 'Over' if prediction == 1 else 'Under',
                    'probability_over': float(probability),
                    'probability_under': float(1 - probability),
                    'confidence': float(max(probability, 1 - probability))
                }
            except (KeyError, FileNotFoundError):
                logger.warning(f"Model for {goal_type} not available")

        # BTTS prediction
        try:
            btts_model = self.models['goals']['btts']

            probability = btts_model.predict_proba(features)[0][1]
            prediction = btts_model.predict(features)[0]

            goals_predictions['btts'] = {
                'prediction': 'Yes' if prediction == 1 else 'No',
                'probability_yes': float(probability),
                'probability_no': float(1 - probability),
                'confidence': float(max(probability, 1 - probability))
            }
        except (KeyError, FileNotFoundError):
            logger.warning("BTTS model not available")

        return goals_predictions

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
