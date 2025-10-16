"""
Feature Engineering Service
Generates ~300 features for football match prediction

This service creates features from historical match data while preventing data leakage
by only using information available before each match.

Feature Categories:
1. Basic Features (20 features)
2. Rolling Window Features (150+ features)
3. Opponent Features (15 features)
4. Head-to-Head Features (10 features)
5. Differential Features (20 features)
6. Contextual Features (5 features)
7. Streak Features (6 features)
8. Goal-Specific Features (40 features)
9. Card-Specific Features (20 features)
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generates features for football match prediction

    Usage:
        engineer = FeatureEngineer(rolling_windows=[3, 5, 10])
        df_with_features = engineer.generate_features(df)
    """

    def __init__(self, rolling_windows: List[int] = [3, 5, 10]):
        """
        Initialize Feature Engineer

        Args:
            rolling_windows: List of window sizes for rolling calculations
        """
        self.rolling_windows = rolling_windows
        self.feature_columns = []

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all features for the dataset

        Args:
            df: DataFrame with match data (must have columns: team_name, date, opponent, venue, etc.)

        Returns:
            DataFrame with all features added
        """
        logger.info("Starting feature generation...")
        logger.info(f"Input shape: {df.shape}")

        # Ensure chronological sorting
        if 'date' in df.columns:
            df = df.sort_values(['team_name', 'date']).reset_index(drop=True)

        # Make a copy
        df = df.copy()

        # Generate features by category
        df = self._add_basic_features(df)
        df = self._add_rolling_window_features(df)
        df = self._add_opponent_features(df)
        df = self._add_head_to_head_features(df)
        df = self._add_differential_features(df)
        df = self._add_contextual_features(df)
        df = self._add_streak_features(df)
        df = self._add_goal_specific_features(df)
        df = self._add_card_specific_features(df)

        logger.info(f"Feature generation complete. Total features added: {len(self.feature_columns)}")
        logger.info(f"Output shape: {df.shape}")

        return df

    def _add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic derived features from raw data
        ~20 features
        """
        logger.info("Adding basic features...")

        # Points earned
        if 'result' in df.columns:
            df['points'] = df['result'].map({'W': 3, 'D': 1, 'L': 0})
            self.feature_columns.append('points')

        # Goal difference
        if 'goals_for' in df.columns and 'goals_against' in df.columns:
            df['goal_diff'] = df['goals_for'] - df['goals_against']
            self.feature_columns.append('goal_diff')

        # xG difference
        if 'xg_for' in df.columns and 'xg_against' in df.columns:
            df['xg_diff'] = df['xg_for'] - df['xg_against']
            self.feature_columns.append('xg_diff')

        # Shot accuracy
        if 'shots_on_target' in df.columns and 'shots' in df.columns:
            df['shot_accuracy'] = df['shots_on_target'] / (df['shots'] + 0.01)
            self.feature_columns.append('shot_accuracy')

        # Binary results
        if 'result' in df.columns:
            df['win'] = (df['result'] == 'W').astype(int)
            df['draw'] = (df['result'] == 'D').astype(int)
            df['loss'] = (df['result'] == 'L').astype(int)
            self.feature_columns.extend(['win', 'draw', 'loss'])

        # Clean sheet
        if 'goals_against' in df.columns:
            df['clean_sheet'] = (df['goals_against'] == 0).astype(int)
            self.feature_columns.append('clean_sheet')

        # Failed to score
        if 'goals_for' in df.columns:
            df['failed_to_score'] = (df['goals_for'] == 0).astype(int)
            self.feature_columns.append('failed_to_score')

        # Both teams scored
        if 'goals_for' in df.columns and 'goals_against' in df.columns:
            df['both_scored'] = ((df['goals_for'] > 0) & (df['goals_against'] > 0)).astype(int)
            self.feature_columns.append('both_scored')

        # Total goals
        if 'goals_for' in df.columns and 'goals_against' in df.columns:
            df['total_goals'] = df['goals_for'] + df['goals_against']
            self.feature_columns.append('total_goals')

        # Over/Under thresholds
        if 'total_goals' in df.columns:
            for threshold in [0.5, 1.5, 2.5, 3.5]:
                col_name = f'over_{str(threshold).replace(".", "_")}'
                df[col_name] = (df['total_goals'] > threshold).astype(int)
                self.feature_columns.append(col_name)

        # Expected goals performance vs actual
        if 'goals_for' in df.columns and 'xg_for' in df.columns:
            df['goals_vs_xg'] = df['goals_for'] - df['xg_for']
            self.feature_columns.append('goals_vs_xg')

        # Shots conversion rate
        if 'goals_for' in df.columns and 'shots' in df.columns:
            df['shots_conversion'] = df['goals_for'] / (df['shots'] + 0.01)
            self.feature_columns.append('shots_conversion')

        logger.info(f"Added {len([c for c in self.feature_columns if c in df.columns])} basic features")

        return df

    def _add_rolling_window_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add rolling window features
        ~150+ features
        """
        logger.info("Adding rolling window features...")

        # Core statistics to calculate rolling averages for
        core_stats = [
            'points', 'goals_for', 'goals_against', 'goal_diff',
            'xg_for', 'xg_against', 'xg_diff',
            'shots', 'shots_on_target', 'possession',
            'corners', 'fouls'
        ]

        # Advanced statistics
        advanced_stats = [
            'sca', 'gca', 'passes', 'passes_completed_pct',
            'progressive_passes', 'carries', 'tackles', 'interceptions',
            'aerials_won', 'clearances', 'blocked_shots'
        ]

        # Combine and filter to only columns that exist
        all_stats = core_stats + advanced_stats
        available_stats = [col for col in all_stats if col in df.columns]

        logger.info(f"Found {len(available_stats)} statistics for rolling calculations")

        # Calculate for each team
        for team in df['team_name'].unique():
            team_mask = df['team_name'] == team
            team_indices = df[team_mask].index

            # Overall rolling windows (all matches)
            for window in self.rolling_windows:
                for stat in available_stats:
                    # Mean
                    feature_name = f'{stat}_L{window}_mean'
                    values = df.loc[team_mask, stat].shift(1).rolling(
                        window=window, min_periods=1
                    ).mean()
                    df.loc[team_indices, feature_name] = values.values
                    if feature_name not in self.feature_columns:
                        self.feature_columns.append(feature_name)

                    # Std (only for larger windows to reduce features)
                    if window >= 5:
                        feature_name = f'{stat}_L{window}_std'
                        values = df.loc[team_mask, stat].shift(1).rolling(
                            window=window, min_periods=2
                        ).std()
                        df.loc[team_indices, feature_name] = values.values
                        if feature_name not in self.feature_columns:
                            self.feature_columns.append(feature_name)

            # Venue-specific rolling windows (Home/Away splits)
            for venue in ['Home', 'Away']:
                venue_team_mask = team_mask & (df['venue'] == venue)
                venue_indices = df[venue_team_mask].index

                # Only mean for venue-specific to control feature count
                for window in self.rolling_windows:
                    for stat in available_stats[:8]:  # Only core stats for venue
                        feature_name = f'{stat}_{venue}_L{window}_mean'
                        values = df.loc[venue_team_mask, stat].shift(1).rolling(
                            window=window, min_periods=1
                        ).mean()
                        df.loc[venue_indices, feature_name] = values.values
                        if feature_name not in self.feature_columns:
                            self.feature_columns.append(feature_name)

        # Season averages (expanding window)
        df = self._add_season_averages(df, available_stats[:12])  # Top 12 stats

        logger.info(f"Added rolling window features")

        return df

    def _add_season_averages(self, df: pd.DataFrame, stats: List[str]) -> pd.DataFrame:
        """Add season-to-date averages"""

        for team in df['team_name'].unique():
            team_mask = df['team_name'] == team
            team_indices = df[team_mask].index

            for stat in stats:
                if stat in df.columns:
                    feature_name = f'{stat}_season_avg'
                    values = df.loc[team_mask, stat].shift(1).expanding(min_periods=1).mean()
                    df.loc[team_indices, feature_name] = values.values
                    if feature_name not in self.feature_columns:
                        self.feature_columns.append(feature_name)

        return df

    def _add_opponent_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add opponent strength features
        ~15 features
        """
        logger.info("Adding opponent features...")

        # Create opponent lookup dictionary for efficiency
        opponent_stats = {}

        for idx, row in df.iterrows():
            team = row['team_name']
            opponent = row['opponent']
            match_date = row['date']

            # Get opponent's latest stats before this match
            opp_mask = (df['team_name'] == opponent) & (df['date'] < match_date)
            opp_data = df[opp_mask]

            if len(opp_data) > 0:
                latest_opp = opp_data.iloc[-1]

                # Opponent season averages
                for stat in ['points_season_avg', 'goals_for_season_avg', 'goals_against_season_avg',
                           'xg_for_season_avg', 'xg_against_season_avg']:
                    if stat in latest_opp:
                        feature_name = f'opp_{stat}'
                        df.at[idx, feature_name] = latest_opp[stat]
                        if feature_name not in self.feature_columns:
                            self.feature_columns.append(feature_name)

                # Opponent recent form (last 5 games)
                if len(opp_data) >= 5:
                    recent_opp = opp_data.tail(5)
                    df.at[idx, 'opp_form_L5_points'] = recent_opp['points'].mean()
                    df.at[idx, 'opp_form_L5_goals'] = recent_opp['goals_for'].mean()

                    if 'opp_form_L5_points' not in self.feature_columns:
                        self.feature_columns.extend(['opp_form_L5_points', 'opp_form_L5_goals'])

        logger.info(f"Added opponent features")
        return df

    def _add_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add head-to-head features
        ~10 features
        """
        logger.info("Adding head-to-head features...")

        for idx, row in df.iterrows():
            team = row['team_name']
            opponent = row['opponent']
            match_date = row['date']

            # Find historical H2H matches
            h2h_mask = (
                ((df['team_name'] == team) & (df['opponent'] == opponent)) |
                ((df['team_name'] == opponent) & (df['opponent'] == team))
            ) & (df['date'] < match_date)

            h2h_data = df[h2h_mask]

            if len(h2h_data) > 0:
                # From this team's perspective
                team_h2h = h2h_data[h2h_data['team_name'] == team]

                if len(team_h2h) > 0:
                    # Last 5 H2H
                    recent_h2h = team_h2h.tail(5)
                    df.at[idx, 'h2h_points_L5'] = recent_h2h['points'].mean()
                    df.at[idx, 'h2h_goals_for_L5'] = recent_h2h['goals_for'].mean()
                    df.at[idx, 'h2h_goals_against_L5'] = recent_h2h['goals_against'].mean()

                    # All-time H2H
                    df.at[idx, 'h2h_win_rate'] = (team_h2h['result'] == 'W').mean()
                    df.at[idx, 'h2h_matches'] = len(team_h2h)

                    for feat in ['h2h_points_L5', 'h2h_goals_for_L5', 'h2h_goals_against_L5',
                               'h2h_win_rate', 'h2h_matches']:
                        if feat not in self.feature_columns:
                            self.feature_columns.append(feat)

        logger.info(f"Added head-to-head features")
        return df

    def _add_differential_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add differential features (team - opponent)
        ~20 features
        """
        logger.info("Adding differential features...")

        diff_pairs = [
            ('points_season_avg', 'opp_points_season_avg'),
            ('goals_for_season_avg', 'opp_goals_for_season_avg'),
            ('goals_against_season_avg', 'opp_goals_against_season_avg'),
            ('xg_for_season_avg', 'opp_xg_for_season_avg'),
            ('xg_against_season_avg', 'opp_xg_against_season_avg'),
        ]

        for team_stat, opp_stat in diff_pairs:
            if team_stat in df.columns and opp_stat in df.columns:
                feature_name = f'diff_{team_stat.replace("_season_avg", "")}'
                df[feature_name] = df[team_stat] - df[opp_stat]
                self.feature_columns.append(feature_name)

        logger.info(f"Added differential features")
        return df

    def _add_contextual_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add contextual features
        ~5 features
        """
        logger.info("Adding contextual features...")

        # Venue encoding
        if 'venue' in df.columns:
            df['is_home'] = (df['venue'] == 'Home').astype(int)
            self.feature_columns.append('is_home')

        # Day of week
        if 'dayofweek' in df.columns:
            df['is_weekend'] = df['dayofweek'].isin(['Sat', 'Sun']).astype(int)
            self.feature_columns.append('is_weekend')

        # Rest days (if we have dates)
        if 'date' in df.columns:
            for team in df['team_name'].unique():
                team_mask = df['team_name'] == team
                team_dates = pd.to_datetime(df.loc[team_mask, 'date'])
                rest_days = team_dates.diff().dt.days
                df.loc[team_mask, 'rest_days'] = rest_days

            self.feature_columns.append('rest_days')

        logger.info(f"Added contextual features")
        return df

    def _add_streak_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add streak features
        ~6 features
        """
        logger.info("Adding streak features...")

        for team in df['team_name'].unique():
            team_mask = df['team_name'] == team
            team_indices = df[team_mask].index
            team_data = df[team_mask].copy()

            # Win streak
            win_streak = self._calculate_streak(team_data['result'].shift(1), 'W')
            df.loc[team_indices, 'win_streak'] = win_streak.values

            # Unbeaten streak (W or D)
            unbeaten = (team_data['result'].shift(1).isin(['W', 'D'])).astype(int)
            unbeaten_streak = self._calculate_consecutive(unbeaten)
            df.loc[team_indices, 'unbeaten_streak'] = unbeaten_streak.values

            # Scoring streak
            scoring = (team_data['goals_for'].shift(1) > 0).astype(int)
            scoring_streak = self._calculate_consecutive(scoring)
            df.loc[team_indices, 'scoring_streak'] = scoring_streak.values

            # Clean sheet streak
            clean_sheet = (team_data['goals_against'].shift(1) == 0).astype(int)
            clean_sheet_streak = self._calculate_consecutive(clean_sheet)
            df.loc[team_indices, 'clean_sheet_streak'] = clean_sheet_streak.values

        self.feature_columns.extend(['win_streak', 'unbeaten_streak', 'scoring_streak', 'clean_sheet_streak'])

        logger.info(f"Added streak features")
        return df

    @staticmethod
    def _calculate_streak(series, value):
        """Calculate current streak of a specific value"""
        streak = []
        current = 0
        for val in series:
            if pd.isna(val):
                current = 0
            elif val == value:
                current += 1
            else:
                current = 0
            streak.append(current)
        return pd.Series(streak, index=series.index)

    @staticmethod
    def _calculate_consecutive(series):
        """Calculate consecutive 1s in binary series"""
        streak = []
        current = 0
        for val in series:
            if pd.isna(val):
                current = 0
            elif val == 1:
                current += 1
            else:
                current = 0
            streak.append(current)
        return pd.Series(streak, index=series.index)

    def _add_goal_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add goal-specific features for O/U predictions
        ~40 features
        """
        logger.info("Adding goal-specific features...")

        for team in df['team_name'].unique():
            team_mask = df['team_name'] == team
            team_indices = df[team_mask].index
            team_data = df[team_mask].copy()

            # Over/Under percentages (last N games)
            for window in [5, 10]:
                for threshold in [0.5, 1.5, 2.5, 3.5]:
                    col_name = f'over_{str(threshold).replace(".", "_")}'
                    if col_name in team_data.columns:
                        feature_name = f'pct_over_{str(threshold).replace(".", "_")}_L{window}'
                        values = team_data[col_name].shift(1).rolling(
                            window=window, min_periods=1
                        ).mean()
                        df.loc[team_indices, feature_name] = values.values
                        self.feature_columns.append(feature_name)

            # BTTS percentage
            if 'both_scored' in team_data.columns:
                for window in [5, 10]:
                    feature_name = f'pct_btts_L{window}'
                    values = team_data['both_scored'].shift(1).rolling(
                        window=window, min_periods=1
                    ).mean()
                    df.loc[team_indices, feature_name] = values.values
                    self.feature_columns.append(feature_name)

            # Goals scored/conceded distribution
            for window in [10]:
                # Percentage of games with 0, 1, 2, 3+ goals scored
                for goals in [0, 1, 2]:
                    feature_name = f'pct_{goals}_goals_scored_L{window}'
                    goals_match = (team_data['goals_for'].shift(1) == goals).astype(int)
                    values = goals_match.rolling(window=window, min_periods=1).mean()
                    df.loc[team_indices, feature_name] = values.values
                    self.feature_columns.append(feature_name)

        logger.info(f"Added goal-specific features")
        return df

    def _add_card_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add card-specific features
        ~20 features
        """
        logger.info("Adding card-specific features...")

        # Check if card columns exist
        card_cols = ['cards_yellow', 'cards_red', 'cards_yellow_against', 'cards_red_against']
        available_card_cols = [col for col in card_cols if col in df.columns]

        if len(available_card_cols) == 0:
            logger.warning("No card columns found, skipping card features")
            return df

        for team in df['team_name'].unique():
            team_mask = df['team_name'] == team
            team_indices = df[team_mask].index
            team_data = df[team_mask].copy()

            # Card averages
            for window in [5, 10]:
                for card_col in available_card_cols:
                    feature_name = f'{card_col}_L{window}_mean'
                    values = team_data[card_col].shift(1).rolling(
                        window=window, min_periods=1
                    ).mean()
                    df.loc[team_indices, feature_name] = values.values
                    self.feature_columns.append(feature_name)

            # Total cards per match
            if 'yellow_cards' in df.columns and 'red_cards' in df.columns:
                team_data['total_cards_match'] = team_data['cards_yellow'] + team_data['cards_red']
                for window in [5, 10]:
                    feature_name = f'total_cards_L{window}_mean'
                    values = team_data['total_cards_match'].shift(1).rolling(
                        window=window, min_periods=1
                    ).mean()
                    df.loc[team_indices, feature_name] = values.values
                    self.feature_columns.append(feature_name)

        logger.info(f"Added card-specific features")
        return df

    def get_feature_names(self) -> List[str]:
        """Return list of all generated feature names"""
        return self.feature_columns.copy()

    def get_feature_count(self) -> int:
        """Return total number of features generated"""
        return len(self.feature_columns)
