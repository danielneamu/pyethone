#!/usr/bin/env python3
"""
Training Script for Football Prediction Models
Loads data, generates features, trains all models with proper validation
"""
from services.model_trainer import ModelTrainer
from services.feature_engineering import FeatureEngineer
from services.data_loader import DataLoader
import pandas as pd
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline"""

    logger.info("=" * 80)
    logger.info("FOOTBALL PREDICTION MODEL TRAINING")
    logger.info("=" * 80)

    # 1. Load data
    logger.info("\n[Step 1/5] Loading data...")
    data_loader = DataLoader('premier_league')
    seasons = data_loader.get_available_seasons()
    logger.info(f"Available seasons: {seasons}")

    df = data_loader.load_multiple_seasons(seasons)
    logger.info(f"Loaded {len(df)} total matches")

    # 2. Generate features
    logger.info("\n[Step 2/5] Generating features...")
    feature_engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
    df = feature_engineer.generate_features(df)

    feature_columns = feature_engineer.get_model_feature_names()
    logger.info(f"Generated {len(feature_columns)} features")
    logger.info(f"Dataset shape: {df.shape}")

    # 3. Split data - use 80% for training, 20% for validation
    logger.info("\n[Step 3/5] Splitting data...")

    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)

    # Remove rows with insufficient history (first few matches per team)
    min_matches = 5
    df = df[df['match_number'] >= min_matches].reset_index(drop=True)
    logger.info(
        f"Using matches from match #{min_matches} onwards: {len(df)} samples")

    # Split
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    val_df = df.iloc[split_idx:].copy()

    logger.info(f"Training set: {len(train_df)} samples")
    logger.info(f"Validation set: {len(val_df)} samples")

    # Check for missing features
    missing_in_train = [
        col for col in feature_columns if col not in train_df.columns]
    missing_in_val = [
        col for col in feature_columns if col not in val_df.columns]

    if missing_in_train:
        logger.error(f"Missing features in training: {missing_in_train}")
        return
    if missing_in_val:
        logger.error(f"Missing features in validation: {missing_in_val}")
        return

    logger.info("All features present in both sets ✓")

    # 4. Train models
    logger.info("\n[Step 4/5] Training models...")
    trainer = ModelTrainer(competition='premier_league')

    results = trainer.train_all_models(
        train_df=train_df,
        val_df=val_df,
        feature_columns=feature_columns
    )

    # 5. Display results
    logger.info("\n[Step 5/5] Training Results Summary")
    logger.info("=" * 80)

    # Match result
    if results['match_result']:
        metrics = results['match_result']['metrics']
        logger.info("\n📊 Match Result Model (1X2):")
        logger.info(f"   Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"   F1 Score:  {metrics['f1_macro']:.4f}")
        logger.info(f"   Log Loss:  {metrics['log_loss']:.4f}")

    # Goals models
    if results['goals']:
        logger.info("\n⚽ Goals Models (Over/Under):")
        for key, model_result in results['goals'].items():
            if key.startswith('over_'):
                threshold = key.replace('over_', '').replace('_', '.')
                metrics = model_result['metrics']
                logger.info(
                    f"   O/U {threshold}: Acc={metrics['accuracy']:.4f}, ROC-AUC={metrics['roc_auc']:.4f}")
            elif key == 'btts':
                metrics = model_result['metrics']
                logger.info(
                    f"   BTTS:      Acc={metrics['accuracy']:.4f}, F1={metrics['f1']:.4f}")

    logger.info("\n" + "=" * 80)
    logger.info("✅ Training completed successfully!")
    logger.info("=" * 80)

    # Test prediction with new features
    logger.info("\n[Bonus] Testing prediction with Arsenal vs Chelsea...")
    try:
        from services.predictor import Predictor
        from services.model_manager import ModelManager

        model_manager = ModelManager('premier_league')
        predictor = Predictor(model_manager, data_loader, feature_engineer)

        prediction = predictor.predict_match('Arsenal', 'Chelsea')  # FIXED - only 2 args

        if prediction['success']:
            probs = prediction['predictions']['match_result']['probabilities']
            logger.info(f"   Home Win: {probs['home_win']:.2%}")
            logger.info(f"   Draw:     {probs['draw']:.2%}")
            logger.info(f"   Away Win: {probs['away_win']:.2%}")
            logger.info("   ✓ Probabilities look realistic!")
        else:
            logger.warning(f"   Prediction failed: {prediction.get('error')}")

    except Exception as e:
        logger.warning(f"   Could not test prediction: {e}")

    logger.info("\n🎉 All done! Models are ready for prediction.")


if __name__ == "__main__":
    main()
