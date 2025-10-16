"""
Model Manager Service
Loads and caches trained models for predictions
"""
import joblib
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages loading and caching of trained models

    Usage:
        manager = ModelManager('premier_league')
        match_model = manager.get_match_result_model()
        over_25_model = manager.get_goals_model('over_2.5')
    """

    def __init__(self, competition: str, models_dir: Path = None):
        """
        Initialize ModelManager

        Args:
            competition: Competition ID (e.g., 'premier_league')
            models_dir: Directory where models are stored
        """
        self.competition = competition

        if models_dir is None:
            from config import MODELS_DIR
            self.models_dir = MODELS_DIR / competition
        else:
            self.models_dir = models_dir

        # Cache for loaded models
        self._model_cache = {}
        self._metadata_cache = {}

    def get_match_result_model(self):
        """Load match result (1X2) model"""
        cache_key = 'match_result'

        if cache_key not in self._model_cache:
            model_path = self.models_dir / 'match_result' / 'xgboost_model.pkl'

            if not model_path.exists():
                raise FileNotFoundError(f"Match result model not found: {model_path}")

            logger.info(f"Loading match result model from {model_path}")
            self._model_cache[cache_key] = joblib.load(model_path)

            # Load metadata
            metadata_path = self.models_dir / 'match_result' / 'metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self._metadata_cache[cache_key] = json.load(f)

        return self._model_cache[cache_key]

    def get_goals_model(self, goal_type: str):
        """
        Load goals model

        Args:
            goal_type: 'over_0.5', 'over_1.5', 'over_2.5', 'over_3.5', or 'btts'
        """
        cache_key = f'goals_{goal_type}'

        if cache_key not in self._model_cache:
            # Map goal type to filename
            if goal_type == 'btts':
                model_name = 'btts_model.pkl'
            else:
                model_name = f"{goal_type.replace('.', '_')}_model.pkl"

            model_path = self.models_dir / 'goals' / model_name

            if not model_path.exists():
                raise FileNotFoundError(f"Goals model not found: {model_path}")

            logger.info(f"Loading {goal_type} model from {model_path}")
            self._model_cache[cache_key] = joblib.load(model_path)

        return self._model_cache[cache_key]

    def get_all_models(self) -> Dict:
        """Load all available models"""
        models = {
            'match_result': self.get_match_result_model(),
            'goals': {}
        }

        # Load all goals models
        for goal_type in ['over_0.5', 'over_1.5', 'over_2.5', 'over_3.5', 'btts']:
            try:
                models['goals'][goal_type] = self.get_goals_model(goal_type)
            except FileNotFoundError:
                logger.warning(f"Model {goal_type} not found, skipping")

        return models

    def get_model_metadata(self, model_type: str) -> Optional[Dict]:
        """Get metadata for a model"""
        cache_key = model_type

        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]

        metadata_path = self.models_dir / model_type / 'metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self._metadata_cache[cache_key] = json.load(f)
                return self._metadata_cache[cache_key]

        return None

    def clear_cache(self):
        """Clear model cache (useful for reloading updated models)"""
        self._model_cache.clear()
        self._metadata_cache.clear()
        logger.info("Model cache cleared")
