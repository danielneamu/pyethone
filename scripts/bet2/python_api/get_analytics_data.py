#!/usr/bin/env python3
"""
Get Analytics Data for Dashboard
Returns JSON with markets, calibration, and model performance
"""

from services.database_service import DatabaseService
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main():
    try:
        db = DatabaseService()

        # Get market performance
        markets = db.get_market_performance()

        # Calculate summary stats
        total_predictions = sum(m.get('total_preds', 0) for m in markets)

        best_market = None
        best_roi = -999
        for m in markets:
            if m.get('avg_roi', 0) > best_roi:
                best_roi = m.get('avg_roi', 0)
                best_market = m.get('market')

        # Placeholder calibration data (will be calculated in collect_results.py)
        calibration = [
            {'confidence_level': 60, 'actual_accuracy': 58},
            {'confidence_level': 70, 'actual_accuracy': 68},
            {'confidence_level': 80, 'actual_accuracy': 81},
            {'confidence_level': 90, 'actual_accuracy': 85},
        ]

        # Placeholder model comparison
        models = [
            {'model_type': 'ensemble', 'accuracy_pct': 55.2,
                'brier_score': 0.232, 'f1_score': 0.489},
            {'model_type': 'xgboost', 'accuracy_pct': 54.1,
                'brier_score': 0.245, 'f1_score': 0.476},
            {'model_type': 'random_forest', 'accuracy_pct': 53.8,
                'brier_score': 0.251, 'f1_score': 0.471},
        ]

        result = {
            'success': True,
            'total_predictions': total_predictions,
            'total_correct': int(total_predictions * 0.55),  # Placeholder
            'overall_roi': 5.3,  # Placeholder
            'best_market': best_market,
            'best_market_roi': best_roi,
            'avg_brier_score': 0.232,
            'markets': markets,
            'calibration': calibration,
            'models': models
        }

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
