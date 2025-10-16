"""
Model Training Module
Trains separate XGBoost models for different prediction tasks
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss, mean_absolute_error
import xgboost as xgb
import sys
sys.path.append('/var/www/html/pyethone/scripts/bet')
from config.config import *


class FootballPredictor:
    """
    Trains multiple specialized prediction models:
    - Match result (1X2)
    - Combined outcomes (1X, 12, X2)
    - Over/Under goals (match and team-specific)
    - Cards predictions
    """
    
    def __init__(self, features_df):
        """
        Initialize with engineered features
        
        Args:
            features_df: DataFrame from feature_engineering.py
        """
        self.df = features_df.copy()
        self.models = {}
        self.feature_columns = self._get_feature_columns()
        
    def _get_feature_columns(self):
        """Define which columns to use as model inputs"""
        # Automatically detect all feature columns by excluding metadata and targets
        exclude_cols = [
            'match_id', 'home_team', 'away_team', 'date', 'season', 'temporal_weight',
            'outcome', 'home_goals', 'away_goals', 'total_goals', 'total_cards',
            'home_cards', 'away_cards'
        ]

        feature_cols = [
            col for col in self.df.columns if col not in exclude_cols]

        print(f"\nUsing {len(feature_cols)} features:")
        for col in feature_cols:
            print(f"  - {col}")

        return feature_cols

    
    def _prepare_data(self, target_column, regression=False):
        """
        Prepare X, y, and sample weights for training
        
        Args:
            target_column: Name of target variable
            regression: True for regression, False for classification
        
        Returns:
            X_train, X_test, y_train, y_test, weights_train, weights_test
        """
        # Remove rows with missing targets
        df_clean = self.df.dropna(subset=[target_column] + self.feature_columns)
        
        X = df_clean[self.feature_columns]
        y = df_clean[target_column]
        weights = df_clean['temporal_weight']
        
        # Split with stratification for classification
        if regression:
            X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
                X, y, weights, test_size=TEST_SIZE, random_state=RANDOM_STATE
            )
        else:
            X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
                X, y, weights, test_size=TEST_SIZE, 
                random_state=RANDOM_STATE, stratify=y
            )
        
        return X_train, X_test, y_train, y_test, w_train, w_test
    
    def train_1x2_model(self):
        """Train main match result predictor (Home/Draw/Away)"""
        print("\n" + "="*60)
        print("Training 1X2 Model (Match Result)")
        print("="*60)
        
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data(
            'outcome')

        # Map H/D/A to numeric
        label_map = {'H': 0, 'D': 1, 'A': 2}
        y_train_numeric = y_train.map(label_map)
        y_test_numeric = y_test.map(label_map)
        
        model = xgb.XGBClassifier(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            objective='multi:softprob',
            random_state=RANDOM_STATE,
            eval_metric='mlogloss'
        )
        
        model.fit(X_train, y_train_numeric, sample_weight=w_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test_numeric, y_pred)
        
        print(f"Accuracy: {accuracy:.2%}")
        
        self.models['1x2'] = {
            'model': model,
            'label_map': label_map,
            'reverse_map': {v: k for k, v in label_map.items()},
            'accuracy': accuracy
        }
        
        return model
    
    def train_combined_models(self):
        """Train 1X, 12, X2 combined outcome models"""
        
        # 1X: Home win OR Draw
        print("\n" + "="*60)
        print("Training 1X Model (Home Win or Draw)")
        print("="*60)
        
        self.df['target_1x'] = self.df['outcome'].apply(lambda x: 1 if x in ['H', 'D'] else 0)
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data('target_1x')
        
        model_1x = xgb.XGBClassifier(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE
        )
        model_1x.fit(X_train, y_train, sample_weight=w_train)
        acc_1x = accuracy_score(y_test, model_1x.predict(X_test))
        print(f"1X Accuracy: {acc_1x:.2%}")
        
        self.models['1x'] = {'model': model_1x, 'accuracy': acc_1x}
        
        # 12: Home win OR Away win (no draw)
        print("\n" + "="*60)
        print("Training 12 Model (Either Team Wins)")
        print("="*60)
        
        self.df['target_12'] = self.df['outcome'].apply(lambda x: 1 if x in ['H', 'A'] else 0)
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data('target_12')
        
        model_12 = xgb.XGBClassifier(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE
        )
        model_12.fit(X_train, y_train, sample_weight=w_train)
        acc_12 = accuracy_score(y_test, model_12.predict(X_test))
        print(f"12 Accuracy: {acc_12:.2%}")
        
        self.models['12'] = {'model': model_12, 'accuracy': acc_12}
        
        # X2: Draw OR Away win
        print("\n" + "="*60)
        print("Training X2 Model (Draw or Away Win)")
        print("="*60)
        
        self.df['target_x2'] = self.df['outcome'].apply(lambda x: 1 if x in ['D', 'A'] else 0)
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data('target_x2')
        
        model_x2 = xgb.XGBClassifier(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE
        )
        model_x2.fit(X_train, y_train, sample_weight=w_train)
        acc_x2 = accuracy_score(y_test, model_x2.predict(X_test))
        print(f"X2 Accuracy: {acc_x2:.2%}")
        
        self.models['x2'] = {'model': model_x2, 'accuracy': acc_x2}
    
    def train_goals_models(self):
        """Train Over/Under goals models (match totals)"""
        
        for threshold in [0.5, 1.5, 2.5]:
            print("\n" + "="*60)
            print(f"Training Over {threshold} Goals Model")
            print("="*60)
            
            target_col = f'target_over_{threshold}'.replace('.', '')
            self.df[target_col] = (self.df['total_goals'] > threshold).astype(int)
            
            X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data(target_col)
            
            model = xgb.XGBClassifier(
                n_estimators=N_ESTIMATORS,
                learning_rate=LEARNING_RATE,
                max_depth=MAX_DEPTH,
                random_state=RANDOM_STATE
            )
            model.fit(X_train, y_train, sample_weight=w_train)
            
            accuracy = accuracy_score(y_test, model.predict(X_test))
            print(f"Over {threshold} Accuracy: {accuracy:.2%}")
            
            model_key = f'over_{str(threshold).replace(".", "")}'
            self.models[model_key] = {'model': model, 'accuracy': accuracy, 'threshold': threshold}
    
    def train_team_goals_models(self):
        """Train team-specific goal scoring models"""
        
        for threshold in [0.5, 1.5, 2.5]:
            print("\n" + "="*60)
            print(f"Training Team Over {threshold} Goals Models")
            print("="*60)
            
            # Home team scoring
            target_col_home = f'target_home_over_{threshold}'.replace('.', '')
            self.df[target_col_home] = (self.df['home_goals'] > threshold).astype(int)
            
            # Away team scoring
            target_col_away = f'target_away_over_{threshold}'.replace('.', '')
            self.df[target_col_away] = (self.df['away_goals'] > threshold).astype(int)
            
            # Train combined model (predicts home AND away separately)
            # For simplicity, we'll average the features and predict match context
            # In production, you'd train separate home/away models
            
            X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data(target_col_home)
            
            model = xgb.XGBClassifier(
                n_estimators=N_ESTIMATORS,
                learning_rate=LEARNING_RATE,
                max_depth=MAX_DEPTH,
                random_state=RANDOM_STATE
            )
            model.fit(X_train, y_train, sample_weight=w_train)
            
            accuracy = accuracy_score(y_test, model.predict(X_test))
            print(f"Team Over {threshold} Accuracy: {accuracy:.2%}")
            
            model_key = f'team_over_{str(threshold).replace(".", "")}'
            self.models[model_key] = {'model': model, 'accuracy': accuracy, 'threshold': threshold}
    
    def train_cards_models(self):
        """Train card prediction models"""
        
        print("\n" + "="*60)
        print("Training Cards Prediction Models")
        print("="*60)
        
        # Total match cards (regression)
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data(
            'total_cards', regression=True
        )
        
        model_total = xgb.XGBRegressor(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE
        )
        model_total.fit(X_train, y_train, sample_weight=w_train)
        
        mae = mean_absolute_error(y_test, model_total.predict(X_test))
        print(f"Total Cards MAE: {mae:.2f}")
        
        self.models['cards'] = {'model': model_total, 'mae': mae}
        
        # Team-specific cards
        X_train, X_test, y_train, y_test, w_train, w_test = self._prepare_data(
            'home_cards', regression=True
        )
        
        model_team = xgb.XGBRegressor(
            n_estimators=N_ESTIMATORS,
            learning_rate=LEARNING_RATE,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE
        )
        model_team.fit(X_train, y_train, sample_weight=w_train)
        
        mae_team = mean_absolute_error(y_test, model_team.predict(X_test))
        print(f"Team Cards MAE: {mae_team:.2f}")
        
        self.models['team_cards'] = {'model': model_team, 'mae': mae_team}
    
    def save_models(self):
        """Save all trained models to disk"""
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        print("\n" + "="*60)
        print("Saving Models")
        print("="*60)
        
        for model_name, model_data in self.models.items():
            filepath = os.path.join(MODEL_DIR, MODEL_FILES[model_name])
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"Saved: {model_name} -> {filepath}")
        
        # Save feature column names
        meta_file = os.path.join(MODEL_DIR, 'model_metadata.pkl')
        metadata = {
            'feature_columns': self.feature_columns,
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'n_samples': len(self.df),
            'models': {k: {key: val for key, val in v.items() if key != 'model'} 
                      for k, v in self.models.items()}
        }
        
        with open(meta_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"\nMetadata saved: {meta_file}")
        
        # Log training results
        log_file = os.path.join(LOG_DIR, 'training_logs.txt')
        os.makedirs(LOG_DIR, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Training completed: {metadata['training_date']}\n")
            f.write(f"Samples: {metadata['n_samples']}\n")
            f.write(f"Models trained: {len(self.models)}\n")
            for model_name, metrics in metadata['models'].items():
                f.write(f"  - {model_name}: {metrics}\n")
        
        print(f"Training log updated: {log_file}")
    
    def train_all(self):
        """Train all models in sequence"""
        print("\n" + "="*60)
        print("FOOTBALL PREDICTION MODEL TRAINING")
        print("="*60)
        print(f"Dataset: {len(self.df)} matches")
        print(f"Features: {len(self.feature_columns)}")
        print(f"Test split: {TEST_SIZE:.0%}")
        
        self.train_1x2_model()
        self.train_combined_models()
        self.train_goals_models()
        self.train_team_goals_models()
        self.train_cards_models()
        
        self.save_models()
        
        print("\n" + "="*60)
        print("TRAINING COMPLETE!")
        print("="*60)


# Main execution
if __name__ == "__main__":
    print("Loading processed features...")
    features = pd.read_csv(PROCESSED_DATA)
    
    predictor = FootballPredictor(features)
    predictor.train_all()
