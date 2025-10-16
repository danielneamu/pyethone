#!/usr/bin/env python3
"""
Predict Match - Standalone Script
Generates predictions for a football match
Called from PHP via predict_api.php

Usage: python predict.py <home_team> <away_team> [competition]
"""
import sys
import json
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '.')

from services.data_loader import DataLoader
from services.feature_engineering import FeatureEngineer
from services.model_manager import ModelManager
from services.predictor import Predictor


def main():
    # Parse arguments
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: predict.py <home_team> <away_team> [competition]"
        }))
        sys.exit(1)

    home_team = sys.argv[1]
    away_team = sys.argv[2]
    competition = sys.argv[3] if len(sys.argv) > 3 else 'premier_league'

    try:
        # Initialize services
        loader = DataLoader(competition)
        engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
        manager = ModelManager(competition)
        predictor = Predictor(manager, loader, engineer)

        # Generate prediction
        result = predictor.predict_match(home_team, away_team, 'Home')

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
