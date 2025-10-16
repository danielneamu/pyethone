#!/usr/bin/env python3
"""
Train Models - Standalone Script
Called from PHP via train_api.php
"""
import sys
import json
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '.')

from services.data_loader import DataLoader
from services.feature_engineering import FeatureEngineer
from services.model_trainer import ModelTrainer

def main():
    print(json.dumps({"status": "starting", "message": "Loading data..."}))
    
    # Load data
    loader = DataLoader('premier_league')
    train_df = loader.load_season('2023-2024')  # Training data
    val_df = loader.load_season('2024-2025')    # Validation data
    
    print(json.dumps({"status": "progress", "message": "Generating features..."}))
    
    # Generate features
    engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
    train_df_feat = engineer.generate_features(train_df)
    val_df_feat = engineer.generate_features(val_df)
    
    feature_columns = engineer.get_feature_names()
    
    print(json.dumps({"status": "progress", "message": f"Training models with {len(feature_columns)} features..."}))
    
    # Train models
    trainer = ModelTrainer('premier_league')
    results = trainer.train_all_models(train_df_feat, val_df_feat, feature_columns)
    
    # Format output
    output = {
        "status": "success",
        "message": "Training complete",
        "models_trained": 6,  # match_result + 4 over/under + btts
        "match_result_accuracy": results['match_result']['metrics']['accuracy'],
        "timestamp": results['timestamp']
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
