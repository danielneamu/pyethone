#!/usr/bin/env python3
"""
Predict Match - Standalone Script with Model Type Selection
Usage: python predict.py <home_team> <away_team> [competition] [model_type]
"""
from services.predictor import Predictor
from services.model_manager import ModelManager
from services.feature_engineering import FeatureEngineer
from services.data_loader import DataLoader
import sys
import json
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '.')


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: predict.py <home_team> <away_team> [competition] [model_type]"
        }))
        sys.exit(1)

    home_team = sys.argv[1]
    away_team = sys.argv[2]
    competition = sys.argv[3] if len(sys.argv) > 3 else 'premier_league'
    model_type = sys.argv[4] if len(sys.argv) > 4 else 'ensemble'  # NEW

    try:
        # Initialize services with model_type
        loader = DataLoader(competition)
        engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
        manager = ModelManager(competition, model_type=model_type)  # CHANGED
        predictor = Predictor(manager, loader, engineer)

        # Generate prediction
        result = predictor.predict_match(home_team, away_team)

        # Add model type to response
        result['model_type'] = model_type

        # Output JSON
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
