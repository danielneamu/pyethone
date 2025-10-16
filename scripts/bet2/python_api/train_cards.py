#!/usr/bin/env python3
"""
Train Cards Prediction Models
Markets: Total Cards O/U (2.5, 3.5, 4.5) + Team Cards O/U (1.5, 2.5)
"""
from services.feature_engineering import FeatureEngineer
from services.data_loader import DataLoader
import joblib
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
import sys
import logging
from pathlib import Path
from config import MODEL_PARAMS


sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("CARDS PREDICTION MODELS TRAINING")
    logger.info("=" * 80)

    # Load data
    logger.info("\n[1/4] Loading data...")
    data_loader = DataLoader('premier_league')
    seasons = data_loader.get_available_seasons()
    df = data_loader.load_multiple_seasons(seasons)
    logger.info(f"Loaded {len(df)} matches")

    # Generate features
    logger.info("\n[2/4] Generating features...")
    feature_engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
    df = feature_engineer.generate_features(df)
    feature_columns = feature_engineer.get_model_feature_names()
    logger.info(f"Generated {len(feature_columns)} features")

    # Prepare data
    logger.info("\n[3/4] Preparing training data...")
    df = df.sort_values('date').reset_index(drop=True)
    df = df[df['match_number'] >= 5].reset_index(drop=True)

    # Calculate total cards per match (both teams combined)
    df['match_total_cards'] = (
        df['cards_yellow'] + df['cards_red'] + df.get('cards_yellow_red', 0) +
        df['cards_yellow_against'] + df['cards_red_against'] +
        df.get('cards_yellow_red_against', 0)
    )

    # Calculate team cards (just this team)
    df['team_total_cards'] = df['cards_yellow'] + \
        df['cards_red'] + df.get('cards_yellow_red', 0)

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    val_df = df.iloc[split_idx:].copy()

    X_train = train_df[feature_columns].values
    X_val = val_df[feature_columns].values

    logger.info(f"Training: {len(X_train)} samples")
    logger.info(f"Validation: {len(X_val)} samples")

    # Create cards directory
    cards_dir = Path('models/premier_league/cards')
    cards_dir.mkdir(parents=True, exist_ok=True)

    # Train models
    logger.info("\n[4/4] Training Cards Models...")
    logger.info("-" * 80)

    cards_results = {}

    # ========================================
    # TOTAL MATCH CARDS (both teams) O/U
    # ========================================
    for threshold in [2.5, 3.5, 4.5]:
        logger.info(f"\nTraining Total Cards Over/Under {threshold}...")

        y_train = (train_df['match_total_cards']
                   > threshold).astype(int).values
        y_val = (val_df['match_total_cards'] > threshold).astype(int).values

        # XGBoost
        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42
        )
        xgb_model.fit(X_train, y_train)
        xgb_acc = accuracy_score(y_val, xgb_model.predict(X_val))

        # Random Forest
        #rf_model = RandomForestClassifier(
        #    n_estimators=100,
        #    max_depth=10,
        #    random_state=42,
        #    n_jobs=-1
        #)

        rf_model = RandomForestClassifier(**MODEL_PARAMS['randomforest']['binary'])
        rf_model.fit(X_train, y_train)
        rf_acc = accuracy_score(y_val, rf_model.predict(X_val))

        logger.info(f"  XGBoost: {xgb_acc:.4f}, RF: {rf_acc:.4f}")

        # Save
        prefix = f'total_cards_over_{str(threshold).replace(".", "_")}'
        joblib.dump(xgb_model, cards_dir / f'{prefix}_xgboost.pkl')
        joblib.dump(rf_model, cards_dir / f'{prefix}_randomforest.pkl')

        cards_results[f'Total O/U {threshold}'] = {
            'xgb': xgb_acc, 'rf': rf_acc}

    # ========================================
    # TEAM CARDS (single team) O/U
    # ========================================
    for threshold in [1.5, 2.5]:
        logger.info(f"\nTraining Team Cards Over/Under {threshold}...")

        y_train = (train_df['team_total_cards'] > threshold).astype(int).values
        y_val = (val_df['team_total_cards'] > threshold).astype(int).values

        # XGBoost
        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42
        )
        xgb_model.fit(X_train, y_train)
        xgb_acc = accuracy_score(y_val, xgb_model.predict(X_val))

        # Random Forest
        #rf_model = RandomForestClassifier(
        #    n_estimators=100,
        #    max_depth=10,
        #    random_state=42,
        #    n_jobs=-1
        #)

        rf_model = RandomForestClassifier(**MODEL_PARAMS['randomforest']['binary'])
        rf_model.fit(X_train, y_train)
        rf_acc = accuracy_score(y_val, rf_model.predict(X_val))

        logger.info(f"  XGBoost: {xgb_acc:.4f}, RF: {rf_acc:.4f}")

        # Save
        prefix = f'team_cards_over_{str(threshold).replace(".", "_")}'
        joblib.dump(xgb_model, cards_dir / f'{prefix}_xgboost.pkl')
        joblib.dump(rf_model, cards_dir / f'{prefix}_randomforest.pkl')

        cards_results[f'Team O/U {threshold}'] = {'xgb': xgb_acc, 'rf': rf_acc}

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("CARDS MODELS SUMMARY:")
    logger.info("=" * 80)
    for model_name, results in cards_results.items():
        best = "RF" if results['rf'] > results['xgb'] else "XGB"
        logger.info(
            f"  {model_name:<25} XGB={results['xgb']:.4f}, RF={results['rf']:.4f} (Best: {best})")

    logger.info("\n✅ All cards models trained successfully!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
