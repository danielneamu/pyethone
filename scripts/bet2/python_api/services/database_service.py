"""
Database Service - SQLite Operations
Handles all database interactions for prediction tracking
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages database operations for predictions and results"""

    def __init__(self, db_path: Path = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent.parent / \
                "database" / "predictions.db"

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database file exists"""
        if not self.db_path.exists():
            logger.warning(
                f"Database not found at {self.db_path}. Run init_db.py first!")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_prediction(self, prediction_data: Dict) -> bool:
        """Save prediction to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            match_id = f"{prediction_data['home_team']}_{prediction_data['away_team']}_{prediction_data.get('match_date', datetime.now().strftime('%Y-%m-%d'))}"
            preds = prediction_data.get('predictions', {})

            cursor.execute("""
                INSERT OR REPLACE INTO predictions (
                    match_id, home_team, away_team, competition, model_type,
                    prediction_1x2, prob_home, prob_draw, prob_away, certainty_1x2,
                    prob_home_draw, prob_home_away, prob_draw_away,
                    prediction_goals_05, prob_over_05, certainty_goals_05,
                    prediction_goals_15, prob_over_15, certainty_goals_15,
                    prediction_goals_25, prob_over_25, certainty_goals_25,
                    prediction_goals_35, prob_over_35, certainty_goals_35,
                    prediction_btts, prob_btts_yes, certainty_btts,
                    prediction_cards_35, prob_cards_over_35, certainty_cards_35,
                    prediction_cards_45, prob_cards_over_45, certainty_cards_45,
                    match_date,
                    prediction_cards_25, prob_cards_over_25, certainty_cards_25
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                prediction_data['home_team'],
                prediction_data['away_team'],
                prediction_data.get('competition', 'premier_league'),
                prediction_data.get('model_type', 'ensemble'),

                # Match result
                preds.get('match_result', {}).get('prediction'),
                preds.get('match_result', {}).get(
                    'probabilities', {}).get('home_win'),
                preds.get('match_result', {}).get(
                    'probabilities', {}).get('draw'),
                preds.get('match_result', {}).get(
                    'probabilities', {}).get('away_win'),
                preds.get('match_result', {}).get('certainty'),

                # Double chance
                preds.get('double_chance', {}).get(
                    'probabilities', {}).get('1X'),
                preds.get('double_chance', {}).get(
                    'probabilities', {}).get('12'),
                preds.get('double_chance', {}).get(
                    'probabilities', {}).get('X2'),

                # Goals O/U 0.5
                preds.get('goals', {}).get('over_0.5', {}).get('prediction'),
                preds.get('goals', {}).get(
                    'over_0.5', {}).get('probability_over'),
                preds.get('goals', {}).get('over_0.5', {}).get('certainty'),

                # Goals O/U 1.5
                preds.get('goals', {}).get('over_1.5', {}).get('prediction'),
                preds.get('goals', {}).get(
                    'over_1.5', {}).get('probability_over'),
                preds.get('goals', {}).get('over_1.5', {}).get('certainty'),

                # Goals O/U 2.5
                preds.get('goals', {}).get('over_2.5', {}).get('prediction'),
                preds.get('goals', {}).get(
                    'over_2.5', {}).get('probability_over'),
                preds.get('goals', {}).get('over_2.5', {}).get('certainty'),

                # Goals O/U 3.5
                preds.get('goals', {}).get('over_3.5', {}).get('prediction'),
                preds.get('goals', {}).get(
                    'over_3.5', {}).get('probability_over'),
                preds.get('goals', {}).get('over_3.5', {}).get('certainty'),

                # BTTS
                preds.get('goals', {}).get('btts', {}).get('prediction'),
                preds.get('goals', {}).get('btts', {}).get('probability_yes'),
                preds.get('goals', {}).get('btts', {}).get('certainty'),

                # Cards O/U 3.5
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_3.5', {}).get('prediction'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_3.5', {}).get('probability_over'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_3.5', {}).get('certainty'),

                # Cards O/U 4.5
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_4.5', {}).get('prediction'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_4.5', {}).get('probability_over'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_4.5', {}).get('certainty'),

                # Match date
                prediction_data.get('match_date'),

                # Cards O/U 2.5 (at the end!)
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_2.5', {}).get('prediction'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_2.5', {}).get('probability_over'),
                preds.get('cards', {}).get('total_match', {}).get(
                    'over_2.5', {}).get('certainty')
            ))

            conn.commit()
            conn.close()
            logger.info(f"✅ Saved prediction: {match_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving prediction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False





    def get_unmatched_predictions(self, days_back: int = 7) -> List[Dict]:
        """Get predictions without matched results"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_back)
                       ).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT * FROM predictions 
            WHERE is_matched = 0 
            AND prediction_date >= ?
            ORDER BY prediction_date DESC
        """, (cutoff_date,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def save_actual_result(self, result_data: Dict) -> bool:
        """Save actual match result"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            match_id = result_data['match_id']

            cursor.execute("""
                INSERT OR REPLACE INTO actual_results (
                    match_id, home_team, away_team,
                    actual_result, goals_home, goals_away, total_goals,
                    btts_actual, cards_home, cards_away, total_cards,
                    match_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                result_data['home_team'],
                result_data['away_team'],
                result_data['actual_result'],
                result_data['goals_home'],
                result_data['goals_away'],
                result_data['total_goals'],
                result_data['btts_actual'],
                result_data.get('cards_home', 0),
                result_data.get('cards_away', 0),
                result_data.get('total_cards', 0),
                result_data['match_date']
            ))

            # Mark prediction as matched
            cursor.execute("""
                UPDATE predictions 
                SET is_matched = 1 
                WHERE match_id = ?
            """, (match_id,))

            conn.commit()
            conn.close()

            logger.info(f"✅ Saved result: {match_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving result: {e}")
            return False

    def get_predictions_with_results(self, limit: int = 100) -> List[Dict]:
        """Get predictions matched with actual results"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                p.*,
                r.actual_result, r.goals_home, r.goals_away, r.total_goals,
                r.btts_actual, r.total_cards
            FROM predictions p
            INNER JOIN actual_results r ON p.match_id = r.match_id
            ORDER BY p.prediction_date DESC
            LIMIT ?
        """, (limit,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def save_accuracy_metric(self, metric_data: Dict) -> bool:
        """Save calculated accuracy metric"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO accuracy_metrics (
                    metric_type, market, model_type,
                    total_predictions, correct_predictions, accuracy_pct,
                    brier_score, f1_score, roc_auc,
                    precision_score, recall_score, total_roi_pct,
                    certainty_level, team_name, calculation_period
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric_data['metric_type'],
                metric_data['market'],
                metric_data.get('model_type'),
                metric_data['total_predictions'],
                metric_data['correct_predictions'],
                metric_data['accuracy_pct'],
                metric_data.get('brier_score'),
                metric_data.get('f1_score'),
                metric_data.get('roc_auc'),
                metric_data.get('precision_score'),
                metric_data.get('recall_score'),
                metric_data.get('total_roi_pct'),
                metric_data.get('certainty_level'),
                metric_data.get('team_name'),
                metric_data.get('calculation_period', 'all_time')
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"❌ Error saving metric: {e}")
            return False

    def get_market_performance(self) -> List[Dict]:
        """Get performance for all markets"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                market,
                AVG(accuracy_pct) as avg_accuracy,
                AVG(brier_score) as avg_brier,
                AVG(total_roi_pct) as avg_roi,
                SUM(total_predictions) as total_preds
            FROM accuracy_metrics
            WHERE calculation_period = 'all_time'
            GROUP BY market
            ORDER BY avg_roi DESC
        """)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results
