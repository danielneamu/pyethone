"""
Model Training Service
Trains XGBoost and Random Forest models for football match prediction
"""
import pandas as pd
import numpy as np
import logging
import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    log_loss, roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains machine learning models for football match prediction

    Usage:
        trainer = ModelTrainer(competition='premier_league')
        results = trainer.train_all_models(train_df, val_df)
    """

    def __init__(self, competition: str, models_dir: Path = None):
        """
        Initialize ModelTrainer

        Args:
            competition: Competition ID (e.g., 'premier_league')
            models_dir: Directory to save models (default: config.MODELS_DIR)
        """
        self.competition = competition

        if models_dir is None:
            from config import MODELS_DIR
            self.models_dir = MODELS_DIR / competition
        else:
            self.models_dir = models_dir

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        (self.models_dir / 'match_result').mkdir(exist_ok=True)
        (self.models_dir / 'goals').mkdir(exist_ok=True)

        self.training_history = []

    def train_all_models(
        self, 
        train_df: pd.DataFrame, 
        val_df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict:
        """
        Train all prediction models

        Args:
            train_df: Training data with features
            val_df: Validation data with features
            feature_columns: List of feature column names

        Returns:
            Dictionary with training results
        """
        logger.info("Starting model training for all prediction types...")

        results = {
            'match_result': None,
            'goals': {},
            'timestamp': datetime.now().isoformat()
        }

        # Train match result model (1X2)
        logger.info("Training match result model...")
        results['match_result'] = self.train_match_result_model(
            train_df, val_df, feature_columns
        )

        # Train goals models (Over/Under)
        logger.info("Training goals models...")
        for threshold in [0.5, 1.5, 2.5, 3.5]:
            logger.info(f"Training Over/Under {threshold} model...")
            results['goals'][f'over_{threshold}'] = self.train_goals_model(
                train_df, val_df, feature_columns, threshold
            )

        # Train BTTS model
        logger.info("Training BTTS model...")
        results['goals']['btts'] = self.train_btts_model(
            train_df, val_df, feature_columns
        )

        # Save training history
        self._save_training_history(results)

        logger.info("All models trained successfully!")
        return results

    def train_match_result_model(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict:
        """
        Train model for match result prediction (Home Win, Draw, Away Win)

        Returns:
            Dictionary with model, metrics, and metadata
        """
        logger.info("Training match result (1X2) model...")

        # Prepare data
        X_train, y_train = self._prepare_match_result_data(train_df, feature_columns)
        X_val, y_val = self._prepare_match_result_data(val_df, feature_columns)

        logger.info(f"Training samples: {len(X_train)}, Validation samples: {len(X_val)}")
        logger.info(f"Features: {len(feature_columns)}")
        logger.info(f"Class distribution: {dict(pd.Series(y_train).value_counts())}")

        # Train XGBoost model
        model = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='mlogloss'
        )

        # Train
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)

        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision_macro': precision_score(y_val, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(y_val, y_pred, average='macro', zero_division=0),
            'f1_macro': f1_score(y_val, y_pred, average='macro', zero_division=0),
            'log_loss': log_loss(y_val, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_val, y_pred).tolist()
        }

        logger.info(f"Match result model - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_macro']:.4f}")

        # Save model
        model_path = self.models_dir / 'match_result' / 'xgboost_model.pkl'
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")

        # Save metadata
        metadata = {
            'model_type': 'xgboost_classifier',
            'task': 'match_result',
            'classes': ['Home Win', 'Draw', 'Away Win'],
            'n_features': len(feature_columns),
            'feature_names': feature_columns,
            'metrics': metrics,
            'trained_at': datetime.now().isoformat(),
            'train_samples': len(X_train),
            'val_samples': len(X_val)
        }

        metadata_path = self.models_dir / 'match_result' / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return {
            'model_path': str(model_path),
            'metrics': metrics,
            'metadata': metadata
        }

    def _prepare_match_result_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for match result model"""

        # Map results to classes: 0=Home Win, 1=Draw, 2=Away Win
        # Remember: data is from team's perspective, we need match perspective
        # For home matches: W=0, D=1, L=2
        # For away matches: W=2, D=1, L=0

        df = df.copy()

        # Create target based on venue
        def map_result(row):
            if row['venue'] == 'Home':
                return {'W': 0, 'D': 1, 'L': 2}[row['result']]
            else:  # Away
                return {'W': 2, 'D': 1, 'L': 0}[row['result']]

        y = df.apply(map_result, axis=1)

        # Get features
        X = df[feature_columns].fillna(0)

        return X.values, y.values

    def train_goals_model(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        feature_columns: List[str],
        threshold: float
    ) -> Dict:
        """
        Train model for goals Over/Under prediction

        Args:
            threshold: Goals threshold (0.5, 1.5, 2.5, 3.5)

        Returns:
            Dictionary with model, metrics, and metadata
        """
        logger.info(f"Training Over/Under {threshold} model...")

        # Prepare data
        X_train, y_train = self._prepare_goals_data(train_df, feature_columns, threshold)
        X_val, y_val = self._prepare_goals_data(val_df, feature_columns, threshold)

        logger.info(f"Over {threshold} - Positive: {y_train.sum()}, Negative: {len(y_train) - y_train.sum()}")

        # Train XGBoost binary classifier
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )

        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_val, y_pred_proba) if len(set(y_val)) > 1 else 0.5
        }

        logger.info(f"Over {threshold} - Accuracy: {metrics['accuracy']:.4f}, ROC AUC: {metrics['roc_auc']:.4f}")

        # Save model
        model_name = f'over_{str(threshold).replace(".", "_")}_model.pkl'
        model_path = self.models_dir / 'goals' / model_name
        joblib.dump(model, model_path)

        # Save metadata
        metadata = {
            'model_type': 'xgboost_classifier',
            'task': f'goals_over_{threshold}',
            'threshold': threshold,
            'n_features': len(feature_columns),
            'metrics': metrics,
            'trained_at': datetime.now().isoformat()
        }

        return {
            'model_path': str(model_path),
            'metrics': metrics,
            'metadata': metadata
        }

    def train_btts_model(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict:
        """Train Both Teams To Score (BTTS) model"""
        logger.info("Training BTTS model...")

        # Prepare data
        X_train, y_train = self._prepare_btts_data(train_df, feature_columns)
        X_val, y_val = self._prepare_btts_data(val_df, feature_columns)

        # Train model
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )

        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_val, y_pred_proba) if len(set(y_val)) > 1 else 0.5
        }

        logger.info(f"BTTS - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")

        # Save
        model_path = self.models_dir / 'goals' / 'btts_model.pkl'
        joblib.dump(model, model_path)

        metadata = {
            'model_type': 'xgboost_classifier',
            'task': 'btts',
            'metrics': metrics,
            'trained_at': datetime.now().isoformat()
        }

        return {
            'model_path': str(model_path),
            'metrics': metrics,
            'metadata': metadata
        }

    def _prepare_goals_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        threshold: float
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for goals Over/Under model"""

        # Total goals in match
        df = df.copy()
        total_goals = df['goals_for'] + df['goals_against']
        y = (total_goals > threshold).astype(int)

        X = df[feature_columns].fillna(0)

        return X.values, y.values

    def _prepare_btts_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for BTTS model"""

        df = df.copy()
        y = ((df['goals_for'] > 0) & (df['goals_against'] > 0)).astype(int)

        X = df[feature_columns].fillna(0)

        return X.values, y.values

    def _save_training_history(self, results: Dict):
        """Save training history to JSON file"""

        history_file = self.models_dir / 'training_history.json'

        # Load existing history
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []

        # Add new entry
        history.append({
            'timestamp': results['timestamp'],
            'match_result_accuracy': results['match_result']['metrics']['accuracy'],
            'models_trained': {
                'match_result': True,
                'goals_over_05': 'over_0.5' in results['goals'],
                'goals_over_15': 'over_1.5' in results['goals'],
                'goals_over_25': 'over_2.5' in results['goals'],
                'goals_over_35': 'over_3.5' in results['goals'],
                'btts': 'btts' in results['goals']
            }
        })

        # Keep only last 20 training sessions
        history = history[-20:]

        # Save
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

        logger.info(f"Training history saved to {history_file}")

    def get_model_info(self, model_type: str) -> Dict:
        """Get information about a trained model"""

        metadata_paths = {
            'match_result': self.models_dir / 'match_result' / 'metadata.json',
            'goals': self.models_dir / 'goals' / 'metadata.json'
        }

        path = metadata_paths.get(model_type)
        if path and path.exists():
            with open(path, 'r') as f:
                return json.load(f)

        return None

    def list_available_models(self) -> List[str]:
        """List all available trained models"""

        models = []

        # Match result model
        if (self.models_dir / 'match_result' / 'xgboost_model.pkl').exists():
            models.append('match_result')

        # Goals models
        goals_dir = self.models_dir / 'goals'
        if goals_dir.exists():
            for model_file in goals_dir.glob('*.pkl'):
                models.append(f"goals_{model_file.stem}")

        return models
