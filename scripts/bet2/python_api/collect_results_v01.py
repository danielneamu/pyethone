#!/usr/bin/env python3
"""
Results Collection Script - ULTIMATE FINAL VERSION
Fetches actual match results and calculates accuracy metrics
Handles missing columns gracefully
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
        self.data_loader = DataLoader('premier_league')

    def collect_results(self, days_back: int = 30):
        """Collect actual results for recent predictions"""
        logger.info("=" * 80)
        logger.info("RESULTS COLLECTION STARTED")
        logger.info("=" * 80)

        predictions = self.db.get_unmatched_predictions(days_back=days_back)
        logger.info(f"📊 Found {len(predictions)} unmatched predictions")

        if not predictions:
            logger.info("✅ No predictions to match. Exiting.")
            return

        seasons = self.data_loader.get_available_seasons()
        df = self.data_loader.load_multiple_seasons(seasons)

        cutoff_date = (datetime.now() - timedelta(days=days_back)
                       ).strftime('%Y-%m-%d')
        df = df[df['date'] >= cutoff_date].copy()

        matched_count = 0

        for pred in predictions:
            match = self._find_matching_result(pred, df)

            if match is not None:
                result_data = self._extract_result_data(pred, match)
                success = self.db.save_actual_result(result_data)

                if success:
                    matched_count += 1
                    logger.info(
                        f"✅ Matched: {pred['home_team']} vs {pred['away_team']} on {pred['match_date']}")

        logger.info(
            f"✅ Matched {matched_count}/{len(predictions)} predictions with results")

        self.calculate_metrics()

    def _find_matching_result(self, prediction: dict, df: pd.DataFrame) -> pd.Series:
        """Find matching result in dataframe"""
        home_team = prediction['home_team']
        away_team = prediction['away_team']
        match_date = str(prediction['match_date'])

        df['date'] = df['date'].astype(str)

        logger.info(
            f"🔍 Looking for: date={match_date}, home={home_team}, away={away_team}")

        match = df[
            (df['date'] == match_date) &
            (df['team_name'] == home_team) &
            (df['opponent'] == away_team) &
            (df['venue'] == 'Home')
        ]

        if not match.empty:
            logger.info(f"✅ Found exact match!")
            return match.iloc[0]

        date_matches = df[df['date'] == match_date]
        logger.info(f"🔍 Rows with matching date: {len(date_matches)}")

        team_matches = df[df['team_name'] == home_team]
        logger.info(f"🔍 Rows with matching home team: {len(team_matches)}")

        opponent_matches = df[df['opponent'] == away_team]
        logger.info(f"🔍 Rows with matching opponent: {len(opponent_matches)}")

        match = df[
            (df['date'] == match_date) &
            (df['team_name'].str.contains(home_team.split()[0], case=False, na=False)) &
            (df['opponent'].str.contains(away_team.split()[0], case=False, na=False)) &
            (df['venue'] == 'Home')
        ]

        if not match.empty:
            logger.info(f"⚠️  Fuzzy matched!")
            return match.iloc[0]

        logger.warning(f"❌ No match found")
        return None

    def _extract_result_data(self, prediction: dict, match: pd.Series) -> dict:
        """Extract result data from match row"""
        goals_home = int(match['goals_for'])
        goals_away = int(match['goals_against'])
        total_goals = goals_home + goals_away

        result = match['result']
        if result == 'W':
            actual_result = 'Home Win'
        elif result == 'D':
            actual_result = 'Draw'
        else:
            actual_result = 'Away Win'

        btts_actual = 'Yes' if (goals_home > 0 and goals_away > 0) else 'No'

        cards_home = 0
        cards_away = 0

        if 'cards_yellow' in match.index and 'cards_red' in match.index:
            cards_home = int(match.get('cards_yellow', 0)) + \
                int(match.get('cards_red', 0))

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
            'match_date': match['date']
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
        logger.info(f"📊 Available columns: {list(df.columns)}")

        if 'actual_result' not in df.columns:
            logger.warning("⚠️ No actual_result column in dataframe")
            return

        matched_df = df[df['actual_result'].notna()].copy()

        if matched_df.empty:
            logger.warning("⚠️ No predictions with actual results.")
            return

        has_goals = 'goals_home' in matched_df.columns and 'goals_away' in matched_df.columns
        has_btts = 'btts_actual' in matched_df.columns
        has_cards = 'cards_home' in matched_df.columns and 'cards_away' in matched_df.columns

        logger.info(f"📊 Found {len(matched_df)} predictions with results")
        logger.info(
            f"📊 Has goals data: {has_goals}, Has BTTS: {has_btts}, Has cards: {has_cards}")

        self._calculate_match_result_metrics(matched_df)
        if has_btts:
            self._calculate_btts_metrics_safe(matched_df)
        if has_goals:
            self._calculate_goals_metrics_safe(matched_df)
        if has_cards:
            self._calculate_cards_metrics_safe(matched_df)
        self._calculate_market_performance(matched_df)

        logger.info("\n✅ Metrics calculation complete!")

    def _calculate_match_result_metrics(self, df: pd.DataFrame):
        """Calculate metrics for match result predictions"""
        valid = df[
            (df['prediction_1x2'].notna()) &
            (df['actual_result'].notna()) &
            (df['actual_result'] != '') &
            (df['actual_result'] != 'None')
        ].copy()

        if valid.empty:
            logger.warning("⚠️ No valid match results to calculate metrics")
            return

        correct = (valid['prediction_1x2'] == valid['actual_result']).sum()
        accuracy = (correct / len(valid)) * 100

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

        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        le.fit(['Home Win', 'Draw', 'Away Win'])

        y_true = le.transform(valid['actual_result'])
        y_pred = le.transform(valid['prediction_1x2'])
        f1 = f1_score(y_true, y_pred, average='macro')

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

    def _calculate_goals_metrics_safe(self, df: pd.DataFrame):
        """Calculate goals metrics safely"""
        for threshold in [0.5, 1.5, 2.5, 3.5]:
            threshold_str = str(threshold).replace('.', '')
            col_prediction = f'prediction_goals_{threshold_str}'
            col_prob = f'prob_over_{threshold_str}'

            if col_prediction not in df.columns or col_prob not in df.columns:
                continue

            valid = df[df[col_prediction].notna()].copy()

            if valid.empty:
                continue

            valid['total_goals'] = (valid['goals_home'].fillna(
                0) + valid['goals_away'].fillna(0)).astype(int)
            valid['actual_over'] = (
                valid['total_goals'] > threshold).astype(int)
            valid['predicted_over'] = (
                valid[col_prediction] == f'Over {threshold}').astype(int)

            correct = (valid['predicted_over'] == valid['actual_over']).sum()
            accuracy = (correct / len(valid)) * 100

            brier = brier_score_loss(
                valid['actual_over'], valid[col_prob].fillna(0.5))

            try:
                roc_auc = roc_auc_score(
                    valid['actual_over'], valid[col_prob].fillna(0.5))
            except:
                roc_auc = None

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

            auc_str = f"{roc_auc:.3f}" if roc_auc is not None else "N/A"
            logger.info(
                f"⚽ Goals O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={auc_str}")

    def _calculate_btts_metrics_safe(self, df: pd.DataFrame):
        """Calculate metrics for BTTS market - safely"""
        if 'prediction_btts' not in df.columns or 'prob_btts_yes' not in df.columns:
            logger.warning("⚠️ Missing BTTS prediction columns")
            return

        valid = df[df['prediction_btts'].notna()].copy()

        if valid.empty:
            logger.warning("⚠️ No BTTS predictions available")
            return

        valid['actual_btts_binary'] = (
            valid['btts_actual'] == 'Yes').astype(int)
        valid['predicted_btts_binary'] = (
            valid['prediction_btts'] == 'Yes').astype(int)

        correct = (valid['predicted_btts_binary'] ==
                   valid['actual_btts_binary']).sum()
        accuracy = (correct / len(valid)) * 100

        brier = brier_score_loss(
            valid['actual_btts_binary'], valid['prob_btts_yes'].fillna(0.5))

        try:
            roc_auc = roc_auc_score(
                valid['actual_btts_binary'], valid['prob_btts_yes'].fillna(0.5))
        except:
            roc_auc = None

        precision = precision_score(
            valid['actual_btts_binary'], valid['predicted_btts_binary'], zero_division=0)
        recall = recall_score(
            valid['actual_btts_binary'], valid['predicted_btts_binary'], zero_division=0)

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

        auc_str = f"{roc_auc:.3f}" if roc_auc is not None else "N/A"
        logger.info(
            f"⚽ BTTS: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={auc_str}")

    def _calculate_cards_metrics_safe(self, df: pd.DataFrame):
        """Calculate cards metrics safely"""
        for threshold in [3.5, 4.5]:
            threshold_str = str(threshold).replace('.', '')
            col_prediction = f'prediction_cards_{threshold_str}'
            col_prob = f'prob_cards_over_{threshold_str}'

            if col_prediction not in df.columns or col_prob not in df.columns:
                continue

            valid = df[df[col_prediction].notna()].copy()

            if valid.empty:
                continue

            valid['total_cards'] = (valid['cards_home'].fillna(
                0) + valid['cards_away'].fillna(0)).astype(int)
            valid['actual_over'] = (
                valid['total_cards'] > threshold).astype(int)
            valid['predicted_over'] = (
                valid[col_prediction] == f'Over {threshold}').astype(int)

            correct = (valid['predicted_over'] == valid['actual_over']).sum()
            accuracy = (correct / len(valid)) * 100

            brier = brier_score_loss(
                valid['actual_over'], valid[col_prob].fillna(0.5))

            try:
                roc_auc = roc_auc_score(
                    valid['actual_over'], valid[col_prob].fillna(0.5))
            except:
                roc_auc = None

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

            auc_str = f"{roc_auc:.3f}" if roc_auc is not None else "N/A"
            logger.info(
                f"🟨 Cards O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier:.3f}, AUC={auc_str}")

    def _calculate_market_performance(self, df: pd.DataFrame):
        """Calculate performance ranking for markets"""
        markets = [
            ('O/U 0.5', 'prediction_goals_05', 'total_goals', 0.5),
            ('O/U 1.5', 'prediction_goals_15', 'total_goals', 1.5),
            ('O/U 2.5', 'prediction_goals_25', 'total_goals', 2.5),
            ('O/U 3.5', 'prediction_goals_35', 'total_goals', 3.5),
            ('BTTS', 'prediction_btts', 'btts_actual', None),
            ('Cards O/U 3.5', 'prediction_cards_35', 'total_cards', 3.5),
            ('Cards O/U 4.5', 'prediction_cards_45', 'total_cards', 4.5),
        ]

        for market_name, pred_col, actual_col, threshold in markets:
            if pred_col not in df.columns:
                continue

            valid = df[df[pred_col].notna()].copy()

            if valid.empty:
                continue

            if actual_col == 'total_goals' and ('total_goals' not in valid.columns or valid['total_goals'].isna().any()):
                valid['total_goals'] = valid['goals_home'].fillna(
                    0) + valid['goals_away'].fillna(0)
            elif actual_col == 'total_cards' and ('total_cards' not in valid.columns or valid['total_cards'].isna().any()):
                valid['total_cards'] = valid['cards_home'].fillna(
                    0) + valid['cards_away'].fillna(0)

            if threshold is not None and actual_col == 'total_goals':
                correct = ((valid[actual_col] > threshold) == (
                    valid[pred_col].str.contains('Over'))).sum()
            elif threshold is not None and actual_col == 'total_cards':
                correct = ((valid[actual_col] > threshold) == (
                    valid[pred_col].str.contains('Over'))).sum()
            else:
                correct = (valid[pred_col] == valid[actual_col]).sum()

            accuracy = (correct / len(valid)) * 100
            roi = ((correct * 2.0) - len(valid)) / len(valid) * 100

            logger.info(f"💰 {market_name}: {len(valid)} bets, ROI={roi:.1f}%")


def main():
    """Main execution"""
    collector = ResultsCollector()
    collector.collect_results(days_back=30)


if __name__ == "__main__":
    main()
