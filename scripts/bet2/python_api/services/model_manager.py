"""
Model Manager Service - Multi-Model Support
Loads and manages XGBoost, Random Forest, or Ensemble models
"""
import joblib
import logging
from pathlib import Path
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages loading and caching of prediction models
    
    Supports:
    - xgboost: XGBoost only
    - randomforest: Random Forest only  
    - ensemble: Weighted average of both
    """

    def __init__(self, competition: str, model_type: str = 'ensemble'):
        """
        Initialize ModelManager
        
        Args:
            competition: Competition name (e.g., 'premier_league')
            model_type: 'xgboost', 'randomforest', or 'ensemble'
        """
        self.competition = competition
        self.model_type = model_type
        self.models_dir = Path(__file__).parent.parent / 'models' / competition
        self.cache = {}

        logger.info(
            f"ModelManager initialized for {competition} with model_type={model_type}")

    def load_model(self, model_name: str, model_dir: Optional[Path] = None):
        """
        Load a single model (XGBoost or RF)
        
        Args:
            model_name: Name of model (e.g., 'match_result')
            model_dir: Optional custom directory
            
        Returns:
            Loaded model object
        """
        cache_key = f"{model_name}_{self.model_type}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if model_dir is None:
            model_dir = self.models_dir / model_name

        model_dir = Path(model_dir)

        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        # Load based on model_type
        if self.model_type == 'xgboost':
            model_path = model_dir / 'xgboost_model.pkl'
            if not model_path.exists():
                raise FileNotFoundError(
                    f"XGBoost model not found: {model_path}")
            model = joblib.load(model_path)
            logger.info(f"Loaded XGBoost model: {model_name}")

        elif self.model_type == 'randomforest':
            model_path = model_dir / 'randomforest_model.pkl'
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Random Forest model not found: {model_path}")
            model = joblib.load(model_path)
            logger.info(f"Loaded Random Forest model: {model_name}")

        elif self.model_type == 'ensemble':
            # Load both models
            xgb_path = model_dir / 'xgboost_model.pkl'
            rf_path = model_dir / 'randomforest_model.pkl'

            if not xgb_path.exists() or not rf_path.exists():
                raise FileNotFoundError(
                    f"Ensemble requires both models in {model_dir}")

            xgb_model = joblib.load(xgb_path)
            rf_model = joblib.load(rf_path)

            # Return dict with both models
            model = {
                'xgboost': xgb_model,
                'randomforest': rf_model,
                'type': 'ensemble'
            }
            logger.info(f"Loaded Ensemble models: {model_name}")

        else:
            raise ValueError(
                f"Invalid model_type: {self.model_type}. Must be 'xgboost', 'randomforest', or 'ensemble'")

        self.cache[cache_key] = model
        return model

    def get_all_models(self) -> Dict:
        """Load all models for prediction (match result, goals, cards)"""
        models = {}

        # =========================================
        # MATCH RESULT MODEL (1X2)
        # =========================================
        try:
            models['match_result'] = self.load_model('match_result')
        except FileNotFoundError as e:
            logger.warning(f"Match result model not found: {e}")

        # =========================================
        # GOALS MODELS (O/U + BTTS)
        # =========================================
        models['goals'] = {}
        goal_types = ['over_0_5', 'over_1_5', 'over_2_5', 'over_3_5', 'btts']

        for goal_type in goal_types:
            try:
                goals_dir = self.models_dir / 'goals'

                if self.model_type == 'xgboost':
                    model_path = goals_dir / f'{goal_type}_xgboost.pkl'
                    if not model_path.exists():
                        # Fallback to old naming
                        model_path = goals_dir / f'{goal_type}_model.pkl'
                    if model_path.exists():
                        models['goals'][goal_type] = joblib.load(model_path)
                        logger.info(f"Loaded XGBoost goal model: {goal_type}")

                elif self.model_type == 'randomforest':
                    model_path = goals_dir / f'{goal_type}_randomforest.pkl'
                    if model_path.exists():
                        models['goals'][goal_type] = joblib.load(model_path)
                        logger.info(f"Loaded RF goal model: {goal_type}")

                elif self.model_type == 'ensemble':
                    xgb_path = goals_dir / f'{goal_type}_xgboost.pkl'
                    rf_path = goals_dir / f'{goal_type}_randomforest.pkl'

                    # Fallback for XGB
                    if not xgb_path.exists():
                        xgb_path = goals_dir / f'{goal_type}_model.pkl'

                    if xgb_path.exists() and rf_path.exists():
                        models['goals'][goal_type] = {
                            'xgboost': joblib.load(xgb_path),
                            'randomforest': joblib.load(rf_path),
                            'type': 'ensemble'
                        }
                        logger.info(f"Loaded ensemble goal model: {goal_type}")
                    elif xgb_path.exists():
                        # Fallback to XGBoost only
                        models['goals'][goal_type] = joblib.load(xgb_path)
                        logger.warning(
                            f"Only XGBoost available for {goal_type}")

            except Exception as e:
                logger.warning(f"Could not load goal model {goal_type}: {e}")

        # =========================================
        # CARDS MODELS (Total and Team O/U)
        # =========================================
        models['cards'] = {}
        cards_types = [
            'total_cards_over_2_5',
            'total_cards_over_3_5',
            'total_cards_over_4_5',
            'team_cards_over_1_5',
            'team_cards_over_2_5'
        ]

        for cards_type in cards_types:
            try:
                cards_dir = self.models_dir / 'cards'

                if self.model_type == 'xgboost':
                    model_path = cards_dir / f'{cards_type}_xgboost.pkl'
                    if model_path.exists():
                        models['cards'][cards_type] = joblib.load(model_path)
                        logger.info(
                            f"Loaded XGBoost cards model: {cards_type}")

                elif self.model_type == 'randomforest':
                    model_path = cards_dir / f'{cards_type}_randomforest.pkl'
                    if model_path.exists():
                        models['cards'][cards_type] = joblib.load(model_path)
                        logger.info(f"Loaded RF cards model: {cards_type}")

                elif self.model_type == 'ensemble':
                    xgb_path = cards_dir / f'{cards_type}_xgboost.pkl'
                    rf_path = cards_dir / f'{cards_type}_randomforest.pkl'

                    if xgb_path.exists() and rf_path.exists():
                        models['cards'][cards_type] = {
                            'xgboost': joblib.load(xgb_path),
                            'randomforest': joblib.load(rf_path),
                            'type': 'ensemble'
                        }
                        logger.info(
                            f"Loaded ensemble cards model: {cards_type}")
                    elif xgb_path.exists():
                        # Fallback to XGBoost only
                        models['cards'][cards_type] = joblib.load(xgb_path)
                        logger.warning(
                            f"Only XGBoost available for {cards_type}")

            except Exception as e:
                logger.warning(f"Could not load cards model {cards_type}: {e}")

        return models


    def set_model_type(self, model_type: str):
        """Change model type and clear cache"""
        if model_type not in ['xgboost', 'randomforest', 'ensemble']:
            raise ValueError(f"Invalid model_type: {model_type}")

        self.model_type = model_type
        self.cache = {}
        logger.info(f"Model type changed to: {model_type}")

    def get_model_metadata(self, model_name: str) -> Dict:
        """Load model metadata (accuracy, training date, etc.)"""
        metadata_path = self.models_dir / model_name / 'metadata.json'

        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)

        return {}
