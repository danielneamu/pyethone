#!/usr/bin/env python3
"""
Results Collection Script - FIXED
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
        self.data_loader = DataLoader('premier_league')

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
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        df = df[df['date'] >= cutoff_date].copy()
        
        logger.info(f"📊 Loaded {len(df)} recent matches from CSV (after {cutoff_date})")
        
        # DEBUG: Show sample CSV data
        if not df.empty:
            logger.info(f"\n📋 Sample CSV matches (Home perspective only):")
            home_matches = df[df['venue'] == 'Home'].head(3)
            for _, row in home_matches.iterrows():
                logger.info(f"  - {row['team_name']} vs {row['opponent']} on {str(row['date'])[:10]}")

        matched_count = 0

        # DEBUG: Show what we're looking for
        logger.info(f"\n📋 Predictions to match:")
        for i, pred in enumerate(predictions[:3], 1):  # Show first 3
            logger.info(f"  {i}. {pred['home_team']} vs {pred['away_team']} on {pred.get('match_date', 'NO DATE')}")

        for pred in predictions:
            # Try to find matching result
            match = self._find_matching_result(pred, df)

            if match is not None:
                result_data = self._extract_result_data(pred, match)
                
                # DEBUG: Log what we're trying to save
                logger.debug(f"  Saving result: {result_data}")
                
                success = self.db.save_actual_result(result_data)

                if success:
                    matched_count += 1
                    logger.info(f"✅ Matched: {pred['home_team']} vs {pred['away_team']}")
                else:
                    logger.error(f"❌ Failed to save: {pred['home_team']} vs {pred['away_team']}")
            else:
                logger.warning(f"⚠️  No match found for {pred['home_team']} vs {pred['away_team']} on {pred.get('match_date', 'unknown date')}")

        logger.info(f"✅ Matched {matched_count}/{len(predictions)} predictions with results")

        # Calculate metrics
        self.calculate_metrics()

    def _find_matching_result(self, prediction: dict, df: pd.DataFrame) -> pd.Series:
        """
        Find matching result in dataframe
        
        FIXED: Properly handles home/away perspective matching
        Uses prediction['match_date'] for matching, not the date from match_id
        """
        home_team = prediction['home_team']
        away_team = prediction['away_team']
        # Use match_date from prediction, not from match_id
        match_date = prediction.get('match_date')

        if not match_date:
            logger.warning(f"  No match_date in prediction for {home_team} vs {away_team}")
            return None
        
        # Ensure match_date is just YYYY-MM-DD format
        if len(str(match_date)) > 10:
            match_date = str(match_date)[:10]

        logger.debug(f"  Searching for: {home_team} vs {away_team} on {match_date}")

        # Method 1: Find home team's perspective (team_name=home, opponent=away, venue=Home)
        match = df[
            (df['team_name'] == home_team) &
            (df['opponent'] == away_team) &
            (df['venue'] == 'Home') &
            (df['date'] == match_date)
        ]

        if not match.empty:
            logger.debug(f"  ✓ Found match (home perspective): {home_team} vs {away_team}")
            return match.iloc[0]

        # Method 2: Try fuzzy match (handle name variations like "Nott'ham Forest" vs "Nottingham Forest")
        # Split on first word for team identification
        home_key = home_team.split()[0]
        away_key = away_team.split()[0]
        
        match = df[
            (df['team_name'].str.contains(home_key, case=False, na=False)) &
            (df['opponent'].str.contains(away_key, case=False, na=False)) &
            (df['venue'] == 'Home') &
            (df['date'] == match_date)
        ]

        if not match.empty:
            logger.debug(f"  ✓ Found match (fuzzy): {home_team} vs {away_team}")
            return match.iloc[0]

        # Method 3: Try within ±2 days (in case date is slightly off)
        try:
            match_date_dt = pd.to_datetime(match_date)
            
            match = df[
                (df['team_name'] == home_team) &
                (df['opponent'] == away_team) &
                (df['venue'] == 'Home') &
                (abs((pd.to_datetime(df['date']) - match_date_dt).dt.days) <= 2)
            ]
            
            if not match.empty:
                logger.debug(f"  ✓ Found match (±2 days): {home_team} vs {away_team}")
                return match.iloc[0]
        except Exception as e:
            logger.debug(f"  Date parsing failed: {e}")

        return None

    def _extract_result_data(self, prediction: dict, match: pd.Series) -> dict:
        """
        Extract result data from match row
        
        FIXED: Uses correct column names from CSV and handles missing values
        """
        try:
            # From home team's perspective in CSV:
            # goals_for = home team's goals, goals_against = away team's goals
            goals_home = int(match['goals_for']) if pd.notna(match['goals_for']) else 0
            goals_away = int(match['goals_against']) if pd.notna(match['goals_against']) else 0
            total_goals = goals_home + goals_away

            # Determine result (from match perspective, not team perspective)
            result = match['result']  # W/D/L from home team's view
            if result == 'W':
                actual_result = 'Home Win'
            elif result == 'D':
                actual_result = 'Draw'
            else:  # L
                actual_result = 'Away Win'

            # BTTS
            btts_actual = 1 if (goals_home > 0 and goals_away > 0) else 0

            # Cards (if available) - handle missing values
            cards_yellow_home = int(match.get('cards_yellow', 0)) if pd.notna(match.get('cards_yellow')) else 0
            cards_red_home = int(match.get('cards_red', 0)) if pd.notna(match.get('cards_red')) else 0
            cards_yellow_away = int(match.get('cards_yellow_against', 0)) if pd.notna(match.get('cards_yellow_against')) else 0
            cards_red_away = int(match.get('cards_red_against', 0)) if pd.notna(match.get('cards_red_against')) else 0
            
            cards_home = cards_yellow_home + cards_red_home
            cards_away = cards_yellow_away + cards_red_away
            total_cards = cards_home + cards_away

            # Convert match date to string for storage
            actual_match_date_str = str(match['date'])[:10] if pd.notna(match['date']) else None
            
            # Generate match_id based on MATCH DATE, not prediction date
            # Format: Home_Away_MatchDate (this is the game identifier)
            match_id = f"{prediction['home_team']}_{prediction['away_team']}_{actual_match_date_str}"

            # Return data matching the database schema EXACTLY
            result_data = {
                'match_id': match_id,  # Use original match_id from prediction
                'home_team': prediction['home_team'],
                'away_team': prediction['away_team'],
                'actual_result': actual_result,
                'total_goals': total_goals,
                'btts_actual': btts_actual,
                'total_cards': total_cards,
                'goals_home': goals_home,
                'goals_away': goals_away,
                'cards_home': cards_home,
                'cards_away': cards_away,
                'match_date': actual_match_date_str  # Actual match date from CSV
            }
            
            logger.debug(f"  Extracted result data: {result_data}")
            return result_data
            
        except KeyError as e:
            logger.error(f"❌ Missing column in CSV: {e}")
            logger.error(f"   Available columns: {match.index.tolist()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error extracting result data: {e}")
            logger.error(f"   Match data: {match.to_dict()}")
            raise

    def calculate_metrics(self):
        """Calculate accuracy metrics from predictions + results"""
        logger.info("\n" + "=" * 80)
        logger.info("CALCULATING ACCURACY METRICS")
        logger.info("=" * 80)

        # Get matched predictions with results
        data = self.db.get_predictions_with_results(limit=1000)

        if not data:
            logger.warning("⚠️ No matched predictions found. Cannot calculate metrics.")
            return

        df = pd.DataFrame(data)
        logger.info(f"📊 Analyzing {len(df)} matched predictions")

        # Check data quality - use correct column names from database
        has_goals = 'total_goals' in df.columns and df['total_goals'].notna().any()
        has_btts = 'btts_actual' in df.columns and df['btts_actual'].notna().any()
        has_cards = 'total_cards' in df.columns and df['total_cards'].notna().any()
        
        logger.info(f"📊 Data available - Goals: {has_goals}, BTTS: {has_btts}, Cards: {has_cards}")

        # 1. Match result metrics
        if 'actual_result' in df.columns:
            self._calculate_match_result_metrics(df)

        # 2. Goals metrics
        if has_goals:
            for threshold in [0.5, 1.5, 2.5, 3.5]:
                self._calculate_goals_metrics(df, threshold)

        # 3. BTTS metrics
        if has_btts:
            self._calculate_btts_metrics(df)

        # 4. Cards metrics
        if has_cards:
            for threshold in [2.5, 3.5, 4.5]:
                self._calculate_cards_metrics(df, threshold)

        logger.info("\n✅ Metrics calculation complete!")

    def _calculate_match_result_metrics(self, df: pd.DataFrame):
        """Calculate metrics for match result predictions"""
        valid = df[df['prediction_1x2'].notna() & df['actual_result'].notna()].copy()

        if valid.empty:
            logger.warning("⚠️ No valid match result predictions")
            return

        logger.info(f"📊 Found {len(valid)} predictions with results")

        # Calculate correctness
        valid['correct_1x2_calc'] = (valid['prediction_1x2'] == valid['actual_result']).astype(int)
        correct = valid['correct_1x2_calc'].sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY METRIC)
        try:
            y_true_home = (valid['actual_result'] == 'Home Win').astype(int)
            y_true_draw = (valid['actual_result'] == 'Draw').astype(int)
            y_true_away = (valid['actual_result'] == 'Away Win').astype(int)

            brier_home = brier_score_loss(y_true_home, valid['prob_home'].fillna(0.33))
            brier_draw = brier_score_loss(y_true_draw, valid['prob_draw'].fillna(0.33))
            brier_away = brier_score_loss(y_true_away, valid['prob_away'].fillna(0.33))
            brier_avg = (brier_home + brier_draw + brier_away) / 3
        except Exception as e:
            logger.warning(f"⚠️ Could not calculate Brier score: {e}")
            brier_avg = None

        # F1 Score (SECONDARY)
        try:
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y_true = le.fit_transform(valid['actual_result'])
            y_pred = le.transform(valid['prediction_1x2'])
            f1 = f1_score(y_true, y_pred, average='macro')
        except Exception as e:
            logger.warning(f"⚠️ Could not calculate F1 score: {e}")
            f1 = None

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

        brier_str = f"{brier_avg:.3f}" if brier_avg else 'N/A'
        f1_str = f"{f1:.3f}" if f1 else 'N/A'
        logger.info(f"⚽ Match Result (1X2): Accuracy={accuracy:.1f}%, Brier={brier_str}, F1={f1_str}")
       

    def _calculate_goals_metrics(self, df: pd.DataFrame, threshold: float):
        """Calculate metrics for goals O/U markets"""
        threshold_str = str(threshold).replace('.', '')
        col_prediction = f'prediction_goals_{threshold_str}'
        col_prob = f'prob_over_{threshold_str}'

        if col_prediction not in df.columns or 'total_goals' not in df.columns:
            return

        valid = df[df[col_prediction].notna() & df['total_goals'].notna()].copy()

        if valid.empty:
            return

        # Actual outcome - use total_goals from database
        valid['actual_over'] = (valid['total_goals'] > threshold).astype(int)
        valid['predicted_over'] = (valid[col_prediction].str.contains('Over', na=False)).astype(int)

        # Accuracy
        correct = (valid['predicted_over'] == valid['actual_over']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        try:
            brier = brier_score_loss(valid['actual_over'], valid[col_prob].fillna(0.5))
        except:
            brier = None

        # ROC-AUC (SECONDARY)
        try:
            if len(valid['actual_over'].unique()) > 1:
                roc_auc = roc_auc_score(valid['actual_over'], valid[col_prob].fillna(0.5))
            else:
                roc_auc = None
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

        brier_str = f"{brier:.3f}" if brier else 'N/A'
        auc_str = f"{roc_auc:.3f}" if roc_auc else 'N/A'
        logger.info(f"⚽ Goals O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier_str}, AUC={auc_str}")

    def _calculate_btts_metrics(self, df: pd.DataFrame):
        """Calculate metrics for BTTS market"""
        valid = df[df['prediction_btts'].notna() & df['btts_actual'].notna()].copy()

        if valid.empty:
            return

        # Actual outcome - use btts_actual from database
        valid['predicted_btts_binary'] = (valid['prediction_btts'] == 'Yes').astype(int)

        # Accuracy
        correct = (valid['predicted_btts_binary'] == valid['btts_actual']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        try:
            brier = brier_score_loss(valid['btts_actual'], valid['prob_btts_yes'].fillna(0.5))
        except:
            brier = None

        # ROC-AUC (SECONDARY)
        try:
            if len(valid['btts_actual'].unique()) > 1:
                roc_auc = roc_auc_score(valid['btts_actual'], valid['prob_btts_yes'].fillna(0.5))
            else:
                roc_auc = None
        except:
            roc_auc = None

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
            'calculation_period': 'all_time'
        }

        self.db.save_accuracy_metric(metric_data)

        brier_str = f"{brier:.3f}" if brier else 'N/A'
        auc_str = f"{roc_auc:.3f}" if roc_auc else 'N/A'
        logger.info(f"⚽ BTTS: Accuracy={accuracy:.1f}%, Brier={brier_str}, AUC={auc_str}")

    def _calculate_cards_metrics(self, df: pd.DataFrame, threshold: float):
        """Calculate metrics for cards O/U markets"""
        threshold_str = str(threshold).replace('.', '')
        col_prediction = f'prediction_cards_{threshold_str}'
        col_prob = f'prob_cards_over_{threshold_str}'

        if col_prediction not in df.columns or 'total_cards' not in df.columns:
            return

        valid = df[df[col_prediction].notna() & df['total_cards'].notna()].copy()

        if valid.empty:
            return

        # Actual outcome - use total_cards from database
        valid['actual_over'] = (valid['total_cards'] > threshold).astype(int)
        valid['predicted_over'] = (valid[col_prediction].str.contains('Over', na=False)).astype(int)

        # Accuracy
        correct = (valid['predicted_over'] == valid['actual_over']).sum()
        accuracy = (correct / len(valid)) * 100

        # Brier Score (PRIMARY)
        try:
            brier = brier_score_loss(valid['actual_over'], valid[col_prob].fillna(0.5))
        except:
            brier = None

        # ROC-AUC (SECONDARY)
        try:
            if len(valid['actual_over'].unique()) > 1:
                roc_auc = roc_auc_score(valid['actual_over'], valid[col_prob].fillna(0.5))
            else:
                roc_auc = None
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

        brier_str = f"{brier:.3f}" if brier else 'N/A'
        auc_str = f"{roc_auc:.3f}" if roc_auc else 'N/A'
        logger.info(f"🟨 Cards O/U {threshold}: Accuracy={accuracy:.1f}%, Brier={brier_str}, AUC={auc_str}")


def main():
    """Main execution"""
    collector = ResultsCollector()

    # Collect results from last 7 days
    collector.collect_results(days_back=7)


if __name__ == "__main__":
    main()