#!/usr/bin/env python3
"""
Train Ensemble Models (XGBoost + Random Forest)
Trains BOTH algorithms for match result AND goals predictions
"""
from services.feature_engineering import FeatureEngineer
from services.data_loader import DataLoader
import joblib
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("ENSEMBLE MODEL TRAINING (XGBoost + Random Forest)")
    logger.info("=" * 80)

    # Load data
    logger.info("\n[1/6] Loading data...")
    data_loader = DataLoader('premier_league')
    seasons = data_loader.get_available_seasons()
    df = data_loader.load_multiple_seasons(seasons)
    logger.info(f"Loaded {len(df)} matches")

    # Generate features
    logger.info("\n[2/6] Generating features...")
    feature_engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
    df = feature_engineer.generate_features(df)
    feature_columns = feature_engineer.get_model_feature_names()
    logger.info(f"Generated {len(feature_columns)} features")

    # Prepare data
    logger.info("\n[3/6] Preparing training data...")
    df = df.sort_values('date').reset_index(drop=True)
    df = df[df['match_number'] >= 5].reset_index(drop=True)

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    val_df = df.iloc[split_idx:].copy()

    # Match result target
    result_map = {'W': 0, 'D': 1, 'L': 2}
    train_df['result_encoded'] = train_df['result'].map(result_map)
    val_df['result_encoded'] = val_df['result'].map(result_map)

    X_train = train_df[feature_columns].values
    y_train = train_df['result_encoded'].values
    X_val = val_df[feature_columns].values
    y_val = val_df['result_encoded'].values

    logger.info(f"Training: {len(X_train)} samples")
    logger.info(f"Validation: {len(X_val)} samples")

    # ============================================================
    # TRAIN MATCH RESULT MODELS
    # ============================================================
    logger.info("\n[4/6] Training Match Result Models...")
    logger.info("-" * 80)

    # XGBoost
    logger.info("Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)

    xgb_pred = xgb_model.predict(X_val)
    xgb_proba = xgb_model.predict_proba(X_val)
    xgb_acc = accuracy_score(y_val, xgb_pred)
    xgb_f1 = f1_score(y_val, xgb_pred, average='macro')

    logger.info(f"  XGBoost - Accuracy: {xgb_acc:.4f}, F1: {xgb_f1:.4f}")

    # Random Forest
    logger.info("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    rf_pred = rf_model.predict(X_val)
    rf_proba = rf_model.predict_proba(X_val)
    rf_acc = accuracy_score(y_val, rf_pred)
    rf_f1 = f1_score(y_val, rf_pred, average='macro')

    logger.info(f"  RandomForest - Accuracy: {rf_acc:.4f}, F1: {rf_f1:.4f}")

    # Ensemble
    ensemble_proba = 0.6 * rf_proba + 0.4 * xgb_proba
    ensemble_pred = np.argmax(ensemble_proba, axis=1)
    ensemble_acc = accuracy_score(y_val, ensemble_pred)
    ensemble_f1 = f1_score(y_val, ensemble_pred, average='macro')

    logger.info(
        f"  Ensemble - Accuracy: {ensemble_acc:.4f}, F1: {ensemble_f1:.4f}")

    # Save match result models
    logger.info("\nSaving match result models...")
    models_dir = Path('models/premier_league/match_result')
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(xgb_model, models_dir / 'xgboost_model.pkl')
    joblib.dump(rf_model, models_dir / 'randomforest_model.pkl')
    logger.info("✅ Match result models saved!")

    # ============================================================
    # TRAIN GOALS MODELS
    # ============================================================
    logger.info("\n[5/6] Training Goals Models...")
    logger.info("-" * 80)

    goals_dir = Path('models/premier_league/goals')
    goals_dir.mkdir(parents=True, exist_ok=True)

    goals_results = {}

    # Over/Under models
    for threshold in [0.5, 1.5, 2.5, 3.5]:
        logger.info(f"\nTraining Over/Under {threshold}...")

        y_col = f'over_{str(threshold).replace(".", "_")}'
        if y_col not in train_df.columns:
            logger.warning(f"  Column {y_col} not found, skipping")
            continue

        y_train_goals = train_df[y_col].values
        y_val_goals = val_df[y_col].values

        # XGBoost
        xgb_goals = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42
        )
        xgb_goals.fit(X_train, y_train_goals)
        xgb_acc_g = accuracy_score(y_val_goals, xgb_goals.predict(X_val))

        # Random Forest
        rf_goals = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        rf_goals.fit(X_train, y_train_goals)
        rf_acc_g = accuracy_score(y_val_goals, rf_goals.predict(X_val))

        logger.info(f"  XGBoost: {xgb_acc_g:.4f}, RF: {rf_acc_g:.4f}")

        # Save
        prefix = f'over_{str(threshold).replace(".", "_")}'
        joblib.dump(xgb_goals, goals_dir / f'{prefix}_xgboost.pkl')
        joblib.dump(rf_goals, goals_dir / f'{prefix}_randomforest.pkl')

        goals_results[f'over_{threshold}'] = {'xgb': xgb_acc_g, 'rf': rf_acc_g}

    # BTTS model
    if 'both_scored' in train_df.columns:
        logger.info(f"\nTraining BTTS...")

        y_train_btts = train_df['both_scored'].values
        y_val_btts = val_df['both_scored'].values

        # XGBoost
        xgb_btts = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42
        )
        xgb_btts.fit(X_train, y_train_btts)
        xgb_acc_btts = accuracy_score(y_val_btts, xgb_btts.predict(X_val))

        # Random Forest
        rf_btts = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        rf_btts.fit(X_train, y_train_btts)
        rf_acc_btts = accuracy_score(y_val_btts, rf_btts.predict(X_val))

        logger.info(f"  XGBoost: {xgb_acc_btts:.4f}, RF: {rf_acc_btts:.4f}")

        # Save
        joblib.dump(xgb_btts, goals_dir / 'btts_xgboost.pkl')
        joblib.dump(rf_btts, goals_dir / 'btts_randomforest.pkl')

        goals_results['btts'] = {'xgb': xgb_acc_btts, 'rf': rf_acc_btts}

    logger.info("\n✅ All goals models saved!")

    # ============================================================
    # SUMMARY
    # ============================================================
    logger.info("\n[6/6] Training Summary")
    logger.info("=" * 80)
    logger.info("\nMATCH RESULT MODELS:")
    logger.info(f"  XGBoost:      Accuracy = {xgb_acc:.4f}")
    logger.info(f"  RandomForest: Accuracy = {rf_acc:.4f}")
    logger.info(f"  Ensemble:     Accuracy = {ensemble_acc:.4f} ⭐ BEST")

    logger.info("\nGOALS MODELS:")
    for model_name, results in goals_results.items():
        best = "RF" if results['rf'] > results['xgb'] else "XGB"
        logger.info(
            f"  {model_name:<15} XGB={results['xgb']:.4f}, RF={results['rf']:.4f} (Best: {best})")

    logger.info("\n" + "=" * 80)
    logger.info("🎉 ALL MODELS TRAINED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info("\nNow test predictions with:")
    logger.info(
        '  python predict.py "Arsenal" "Chelsea" "premier_league" "ensemble"')


if __name__ == "__main__":
    main()
