#!/usr/bin/env python3
"""
Results Collection Script
Fetches actual match results and calculates accuracy metrics
"""

from sklearn.metrics import brier_score_loss, f1_score, roc_auc_score, precision_score, recall_score
from services.data_loader import DataLoader
from services.database_service import DatabaseService
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResultsCollector:
    """Collects actual results and calculates metrics"""

    def __init__(self):
        self.db = DatabaseService()
        self.data_loader = DataLoader('premierleague')

    def collect_results(self, days_back: int = 7):
        """
        Collect actual results for recent predictions
        
        Args:
            days_back: How many days back to check
        """
        logger.info("=" * 80)
        logger.info("RESULTS COLLECTION STARTED")
        logger.info("=" * 80)

        # Get unmatched predictions
        predictions = self.db.get_unmatched_predictions(days_back=days_back)
        logger.info(f"📊 Found {len(predictions)} unmatched predictions")

        if not predictions:
            logger.info("✅ No predictions to match. Exiting.")
            return

        # Load recent match data
        seasons = self.data_loader.get_available_seasons()
        df = self.data_loader.load_multiple_seasons(seasons)

        # Filter to recent matches only
        cutoff_date = (datetime.now() - timedelta(days=days_back)
                       ).strftime('%Y-%m-%d')
        df = df[df['Date'] >= cutoff_date].copy()

        matched_count = 0

        for pred in predictions:
            # Try to find matching result
            match = self._find_matching_result(pred, df)

            if match is not None:
                result_data = self._extract_result_data(pred, match)
                success = self.db.save_actual_result(result_data)

                if success:
                    matched_count += 1

        logger.info(
            f"✅ Matched {matched_count}/{len(predictions)} predictions with results")

        # Calculate metrics
        self.calculate_metrics()

    def _find_matching_result(self, prediction: dict, df: pd.DataFrame) -> pd.Series:
        """Find matching result in dataframe"""
        home_team = prediction['home_team']
        away_team = prediction['away_team']

        # Try exact match
        match = df[
            (df['Team'] == home_team) &
            (df['Opponent'] == away_team) &
            (df['Venue'] == 'Home')
        ]

        if not match.empty:
            return match.iloc[0]

        # Try fuzzy match (handle name variations)
        match = df[
            (df['Team'].str.contains(home_team.split()[0], case=False)) &
            (df['Opponent'].str.contains(away_team.split()[0], case=False)) &
            (df['Venue'] == 'Home')
        ]

        if not match.empty:
            return match.iloc[0]

        return None

    def _extract_result_data(self, prediction: dict, match: pd.Series) -> dict:
        """Extract result data from match row"""
        goals_home = int(match['GF'])
        goals_away = int(match['GA'])
        total_goals = goals_home + goals_away

        # Determine result
        if goals_home > goals_away:
            actual_result = 'Home Win'
        elif goals_away > goals_home:
            actual_result = 'Away Win'
        else:
            actual_result = 'Draw'

        # BTTS
        btts_actual = 'Yes' if (goals_home > 0 and goals_away > 0) else 'No'

        # Cards (if available)
        cards_home = int(match.get('CrdY', 0)) + int(match.get('CrdR', 0))
        cards_away = int(match.get('Opp_CrdY', 0)) + \
            int(match.get('Opp_CrdR', 0))
        total_cards = cards_home + cards_away

        return {
            'match_id': prediction['match_id'],
            'home_team': prediction['home_team'],
            'away_team': prediction['away_team'],
            'actual_result': actual_result,
            'goals_home': goals_home,
            'goals_away': goals_away,
            'total_goals': total_goals,
            'btts_actual': btts_actual,
            'cards_home': cards_home,
            'cards_away': cards_away,
            'total_cards': total_cards,
            'match_date': match['Date']
        }

    def calculate_metrics(self):
        """Calculate accuracy metrics from predictions + results"""
        logger.info("\n" + "=" * 80)
        logger.info("CALCULATING ACCURACY METRICS")
        logger.info("=" * 80)

        data = self.db.get_predictions_with_results(limit=1000)

        if not data:
            logger.warning(
                "⚠️ No matched predictions found. Cannot calculate metrics.")
            return

        df = pd.DataFrame(data)
        logger.info(f"📊 Analyzing {len(df)} matched predictions")

        # 1. MATCH RESULT (1X2) - Brier Score + F1
        self._calculate_match_result_metrics(df)

        # 2. GOALS MARKETS - Brier Score + ROC-AUC
        for threshold in [0.5, 1.5, 2.5, 3.5]:
            self._calculate_goals_metrics(df, threshold)

        # 3. BTTS - Brier Score + ROC-AUC
        self._calculate_btts_metrics(df)

        # 4. CARDS - Brier Score + ROC-AUC
        for threshold in [3.5, 4.5]:
            self._calculate_cards_metrics(df, threshold)

        # 5. MARKET PERFORMANCE (for dashboard Tab 1)
        self._calculate_market_performance(df)

        logger.info("\n✅ Metrics calculation complete!")

    def _calculate_match_result_metrics(self, df: pd.DataFrame):
        """Calculate metrics for match result predictions"""
        # Filter valid predictions
        valid = df[df['prediction_1x2'].notna()].copy()

        if valid.empty:
            return

        # Accuracy
        correct = (valid['prediction_1x2'] == valid['actual_result']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        y_true_home = (valid['actual_result'] == 'Home Win').astype(int)
        y_true_draw = (valid['actual_result'] == 'Draw').astype(int)
        y_true_away = (valid['actual_result'] == 'Away Win').astype(int)

        brier_home = brier_score_loss(
            y_true_home, valid['prob_home'].fillna(0))
        brier_draw = brier_score_loss(
            y_true_draw, valid['prob_draw'].fillna(0))
        brier_away = brier_score_loss(
            y_true_away, valid['prob_away'].fillna(0))
        brier_avg = (brier_home + brier_draw + brier_away) / 3

        # F1 Score (SECONDARY)
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y_true = le.fit_transform(valid['actual_result'])
        y_pred = le.transform(valid['prediction_1x2'])
        f1 = f1_score(y_true, y_pred, average='macro')

        # Save to database
        metric_data = {
            'metric_type': 'match_result',
            'market': '1X2',
            'model_type': 'ensemble',
            'total_predictions': len(valid),
            'correct_predictions': correct,
            'accuracy_pct': accuracy,
            'brier_score': brier_avg,
            'f1_score': f1,
            'calculation_period': 'all_time'
        }

        self.db.save_accuracy_metric(metric_data)

        logger.info(
            f"⚽ Match Result (1X2): Accuracy={accuracy:.1f}%, Brier={brier_avg:.3f}, F1={f1:.3f}")

    def _calculate_goals_metrics(self, df: pd.DataFrame, threshold: float):
        """Calculate metrics for goals O/U markets"""
        threshold_str = str(threshold).replace('.', '')
        col_prediction = f'prediction_goals_{threshold_str}'
        col_prob = f'prob_over_{threshold_str}'

        if col_prediction not in df.columns:
            return

        valid = df[df[col_prediction].notna()].copy()

        if valid.empty:
            return

        # Actual outcome
        valid['actual_over'] = (valid['total_goals'] > threshold).astype(int)
        valid['predicted_over'] = (
            valid[col_prediction] == f'Over {threshold}').astype(int)

        # Accuracy
        correct = (valid['predicted_over'] == valid['actual_over']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        brier = brier_score_loss(
            valid['actual_over'], valid[col_prob].fillna(0.5))

        # ROC-AUC (SECONDARY)
        try:
            roc_auc = roc_auc_score(
                valid['actual_over'], valid[col_prob].fillna(0.5))
        except:
            roc_auc = None

        # Save to database
        metric_data = {
            'metric_type': 'goals_over_under',
            'market': f'O/U {threshold}',
            'model_type': 'ensemble',
            'total_predictions': len(valid),
            'correct_predictions': correct,
            'accuracy_pct': accuracy,
            'brier_score': brier,
            'roc_auc': roc_auc,
            'calculation_period': 'all_time'
        }

        self.db.save_accuracy_metric(metric_data)

        logger.info(
            f"⚽ Goals O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={roc_auc:.3f if roc_auc else 'N/A'}")

    def _calculate_btts_metrics(self, df: pd.DataFrame):
        """Calculate metrics for BTTS market"""
        valid = df[df['prediction_btts'].notna()].copy()

        if valid.empty:
            return

        # Actual outcome
        valid['actual_btts_binary'] = (
            valid['btts_actual'] == 'Yes').astype(int)
        valid['predicted_btts_binary'] = (
            valid['prediction_btts'] == 'Yes').astype(int)

        # Accuracy
        correct = (valid['predicted_btts_binary'] ==
                   valid['actual_btts_binary']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        brier = brier_score_loss(
            valid['actual_btts_binary'], valid['prob_btts_yes'].fillna(0.5))

        # ROC-AUC (SECONDARY)
        try:
            roc_auc = roc_auc_score(
                valid['actual_btts_binary'], valid['prob_btts_yes'].fillna(0.5))
        except:
            roc_auc = None

        # Precision/Recall for "Yes" class
        precision = precision_score(
            valid['actual_btts_binary'], valid['predicted_btts_binary'], zero_division=0)
        recall = recall_score(
            valid['actual_btts_binary'], valid['predicted_btts_binary'], zero_division=0)

        # Save to database
        metric_data = {
            'metric_type': 'btts',
            'market': 'BTTS',
            'model_type': 'ensemble',
            'total_predictions': len(valid),
            'correct_predictions': correct,
            'accuracy_pct': accuracy,
            'brier_score': brier,
            'roc_auc': roc_auc,
            'precision_score': precision,
            'recall_score': recall,
            'calculation_period': 'all_time'
        }

        self.db.save_accuracy_metric(metric_data)

        logger.info(
            f"⚽ BTTS: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={roc_auc:.3f if roc_auc else 'N/A'}")

    def _calculate_cards_metrics(self, df: pd.DataFrame, threshold: float):
        """Calculate metrics for cards O/U markets"""
        threshold_str = str(threshold).replace('.', '')
        col_prediction = f'prediction_cards_{threshold_str}'
        col_prob = f'prob_cards_over_{threshold_str}'

        if col_prediction not in df.columns:
            return

        valid = df[df[col_prediction].notna()].copy()

        if valid.empty:
            return

        # Actual outcome
        valid['actual_over'] = (valid['total_cards'] > threshold).astype(int)
        valid['predicted_over'] = (
            valid[col_prediction] == f'Over {threshold}').astype(int)

        # Accuracy
        correct = (valid['predicted_over'] == valid['actual_over']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        brier = brier_score_loss(
            valid['actual_over'], valid[col_prob].fillna(0.5))

        # ROC-AUC (SECONDARY)
        try:
            roc_auc = roc_auc_score(
                valid['actual_over'], valid[col_prob].fillna(0.5))
        except:
            roc_auc = None

        # Save to database
        metric_data = {
            'metric_type': 'cards_over_under',
            'market': f'Cards O/U {threshold}',
            'model_type': 'ensemble',
            'total_predictions': len(valid),
            'correct_predictions': correct,
            'accuracy_pct': accuracy,
            'brier_score': brier,
            'roc_auc': roc_auc,
            'calculation_period': 'all_time'
        }

        self.db.save_accuracy_metric(metric_data)

        logger.info(
            f"🟨 Cards O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={roc_auc:.3f if roc_auc else 'N/A'}")

    def _calculate_market_performance(self, df: pd.DataFrame):
        """Calculate performance ranking for markets (for Tab 1)"""
        markets = [
            ('O/U 0.5', 'prediction_goals_05', 'total_goals', 0.5),
            ('O/U 1.5', 'prediction_goals_15', 'total_goals', 1.5),
            ('O/U 2.5', 'prediction_goals_25', 'total_goals', 2.5),
            ('O/U 3.5', 'prediction_goals_35', 'total_goals', 3.5),
            ('BTTS', 'prediction_btts', 'btts_actual', None),
            ('Cards O/U 3.5', 'prediction_cards_35', 'total_cards', 3.5),
            ('Cards O/U 4.5', 'prediction_cards_45', 'total_cards', 4.5),
        ]

        # Calculate ROI (simplified - assumes 1.0 unit per bet, 2.0 odds)
        for market_name, pred_col, actual_col, threshold in markets:
            if pred_col not in df.columns:
                continue

            valid = df[df[pred_col].notna()].copy()

            if valid.empty:
                continue

            # Simplified ROI calculation (placeholder)
            # In production, you'd integrate actual odds
            if threshold is not None and actual_col == 'total_goals':
                correct = ((valid[actual_col] > threshold) == (
                    valid[pred_col].str.contains('Over'))).sum()
            elif threshold is not None and actual_col == 'total_cards':
                correct = ((valid[actual_col] > threshold) == (
                    valid[pred_col].str.contains('Over'))).sum()
            else:
                correct = (valid[pred_col] == valid[actual_col]).sum()

            accuracy = (correct / len(valid)) * 100
            roi = ((correct * 2.0) - len(valid)) / \
                len(valid) * 100  # Simplified

            logger.info(f"💰 {market_name}: {len(valid)} bets, ROI={roi:.1f}%")


def main():
    """Main execution"""
    collector = ResultsCollector()

    # Collect results from last 7 days
    collector.collect_results(days_back=7)


if __name__ == "__main__":
    main()
