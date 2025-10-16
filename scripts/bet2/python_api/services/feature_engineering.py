"""
Feature Engineering Service - ENHANCED v3.0
Generates features with opponent context and xG intelligence

New Features:
- Opponent features (mirrored from opponent's perspective)
- Differential features (team - opponent)
- xG intelligence (trends, over/underperformance)
- Goal cross-features (BTTS, combined threat)
- Recency weighting (recent games weighted more)
"""
import pandas as pd
import numpy as np
import logging
import warnings
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Suppress pandas performance warnings
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generates comprehensive features for football match prediction
    
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
            df: DataFrame with match data
            
        Returns:
            DataFrame with all features added
        """
        logger.info(
            "Starting ENHANCED feature generation with opponent context...")
        logger.info(f"Input shape: {df.shape}")

        # Ensure chronological sorting
        if 'date' in df.columns:
            df = df.sort_values(['team_name', 'date']).reset_index(drop=True)

        # Make a copy
        df = df.copy()

        # Reset feature columns
        self.feature_columns = []

        # PHASE 1: Team-only features (existing)
        logger.info("Phase 1: Generating team features...")
        df = self._add_basic_features(df)
        df = self._add_rolling_window_features(df)
        df = self._add_contextual_features(df)
        df = self._add_streak_features(df)
        df = self._add_form_features(df)
        df = self._add_goal_specific_features(df)
        df = self._add_defensive_features(df)
        df = self._add_venue_specific_features(df)

        # PHASE 2: xG Intelligence features (NEW)
        logger.info("Phase 2: Generating xG intelligence features...")
        df = self._add_xg_intelligence_features(df)

        # PHASE 3: Opponent features (NEW)
        logger.info("Phase 3: Generating opponent features...")
        df = self._add_opponent_features(df)

        # PHASE 4: Differential features (NEW)
        logger.info("Phase 4: Generating differential features...")
        df = self._add_differential_features(df)

        # PHASE 5: Goal cross-features (NEW)
        logger.info("Phase 5: Generating goal cross-features...")
        df = self._add_goal_cross_features(df)

        # PHASE 6: Cards features (NEW)
        logger.info("Phase 6: Generating cards features...")
        df = self._add_cards_features(df)

        # Fill NaN values with 0
        feature_cols = [
            col for col in self.feature_columns if col in df.columns]
        df[feature_cols] = df[feature_cols].fillna(0)

        logger.info(
            f"Feature generation complete. Total features: {len(self.feature_columns)}")
        logger.info(f"Output shape: {df.shape}")

        return df

    def _add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic derived features (~25 features)"""
        logger.info("Adding basic features...")

        if 'result' in df.columns:
            df['points'] = df['result'].map({'W': 3, 'D': 1, 'L': 0})
            self.feature_columns.append('points')

        if 'goals_for' in df.columns and 'goals_against' in df.columns:
            df['goal_diff'] = df['goals_for'] - df['goals_against']
            self.feature_columns.append('goal_diff')

        if 'xg_for' in df.columns and 'xg_against' in df.columns:
            df['xg_diff'] = df['xg_for'] - df['xg_against']
            self.feature_columns.append('xg_diff')

        if 'shots_on_target' in df.columns and 'shots' in df.columns:
            df['shot_accuracy'] = df['shots_on_target'] / (df['shots'] + 0.01)
            self.feature_columns.append('shot_accuracy')

        if 'goals_for' in df.columns and 'shots' in df.columns:
            df['shots_conversion'] = df['goals_for'] / (df['shots'] + 0.01)
            self.feature_columns.append('shots_conversion')

        if 'result' in df.columns:
            df['win'] = (df['result'] == 'W').astype(int)
            df['draw'] = (df['result'] == 'D').astype(int)
            df['loss'] = (df['result'] == 'L').astype(int)
            self.feature_columns.extend(['win', 'draw', 'loss'])

        if 'goals_against' in df.columns:
            df['clean_sheet'] = (df['goals_against'] == 0).astype(int)
            self.feature_columns.append('clean_sheet')

        if 'goals_for' in df.columns:
            df['failed_to_score'] = (df['goals_for'] == 0).astype(int)
            self.feature_columns.append('failed_to_score')

        if 'goals_for' in df.columns and 'goals_against' in df.columns:
            df['both_scored'] = ((df['goals_for'] > 0) & (
                df['goals_against'] > 0)).astype(int)
            df['total_goals'] = df['goals_for'] + df['goals_against']
            self.feature_columns.extend(['both_scored', 'total_goals'])

        if 'total_goals' in df.columns:
            for threshold in [0.5, 1.5, 2.5, 3.5]:
                col_name = f'over_{str(threshold).replace(".", "_")}'
                df[col_name] = (df['total_goals'] > threshold).astype(int)
                self.feature_columns.append(col_name)

        if 'goals_for' in df.columns and 'xg_for' in df.columns:
            df['goals_vs_xg'] = df['goals_for'] - df['xg_for']
            self.feature_columns.append('goals_vs_xg')

        if 'shots_against' in df.columns and 'shots_on_target_against' in df.columns:
            df['defensive_pressure'] = df['shots_against'] - \
                df['shots_on_target_against']
            self.feature_columns.append('defensive_pressure')

        return df

    def _add_rolling_window_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling window features (~120 features)"""
        logger.info("Adding rolling window features...")

        core_stats = [
            'points', 'goals_for', 'goals_against', 'goal_diff',
            'xg_for', 'xg_against', 'xg_diff',
            'shots', 'shots_on_target', 'possession',
            'shot_accuracy', 'shots_conversion'
        ]

        advanced_stats = [
            'sca', 'gca', 'interceptions', 'tackles_won',
            'aerials_won', 'fouls', 'cards_yellow'
        ]

        all_stats = core_stats + advanced_stats
        available_stats = [col for col in all_stats if col in df.columns]

        for window in self.rolling_windows:
            for stat in available_stats:
                # Mean
                feature_name = f'{stat}_L{window}_mean'
                df[feature_name] = df.groupby('team_name')[stat].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

                # Std (only for larger windows)
                if window >= 5:
                    feature_name = f'{stat}_L{window}_std'
                    df[feature_name] = df.groupby('team_name')[stat].transform(
                        lambda x: x.shift(1).rolling(
                            window=window, min_periods=2).std()
                    )
                    self.feature_columns.append(feature_name)

        # Season averages
        for stat in available_stats[:10]:
            feature_name = f'{stat}_season_avg'
            df[feature_name] = df.groupby('team_name')[stat].transform(
                lambda x: x.shift(1).expanding(min_periods=1).mean()
            )
            self.feature_columns.append(feature_name)

        return df

    def _add_contextual_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add contextual features (~5 features)"""
        logger.info("Adding contextual features...")

        if 'venue' in df.columns:
            df['is_home'] = (df['venue'] == 'Home').astype(int)
            self.feature_columns.append('is_home')

        if 'dayofweek' in df.columns:
            df['is_weekend'] = df['dayofweek'].isin(['Sat', 'Sun']).astype(int)
            self.feature_columns.append('is_weekend')

        if 'date' in df.columns:
            df['date_parsed'] = pd.to_datetime(df['date'])
            df['rest_days'] = df.groupby('team_name')[
                'date_parsed'].diff().dt.days
            df['rest_days'] = df['rest_days'].clip(
                upper=30)  # Cap extreme values
            df.drop('date_parsed', axis=1, inplace=True)
            self.feature_columns.append('rest_days')

        df['match_number'] = df.groupby('team_name').cumcount() + 1
        self.feature_columns.append('match_number')

        return df

    def _add_streak_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add streak features (~8 features)"""
        logger.info("Adding streak features...")

        df['win_streak'] = df.groupby('team_name')['result'].transform(
            lambda x: self._calculate_streak_series(x.shift(1), 'W')
        )
        self.feature_columns.append('win_streak')

        df['loss_streak'] = df.groupby('team_name')['result'].transform(
            lambda x: self._calculate_streak_series(x.shift(1), 'L')
        )
        self.feature_columns.append('loss_streak')

        df['_unbeaten_temp'] = df['result'].isin(['W', 'D']).astype(int)
        df['unbeaten_streak'] = df.groupby('team_name')['_unbeaten_temp'].transform(
            lambda x: self._calculate_consecutive_series(x.shift(1))
        )
        df.drop('_unbeaten_temp', axis=1, inplace=True)
        self.feature_columns.append('unbeaten_streak')

        if 'goals_for' in df.columns:
            df['_scoring_temp'] = (df['goals_for'] > 0).astype(int)
            df['scoring_streak'] = df.groupby('team_name')['_scoring_temp'].transform(
                lambda x: self._calculate_consecutive_series(x.shift(1))
            )
            df.drop('_scoring_temp', axis=1, inplace=True)
            self.feature_columns.append('scoring_streak')

        if 'goals_against' in df.columns:
            df['_cs_temp'] = (df['goals_against'] == 0).astype(int)
            df['clean_sheet_streak'] = df.groupby('team_name')['_cs_temp'].transform(
                lambda x: self._calculate_consecutive_series(x.shift(1))
            )
            df.drop('_cs_temp', axis=1, inplace=True)
            self.feature_columns.append('clean_sheet_streak')

        df['games_since_win'] = df.groupby('team_name')['result'].transform(
            lambda x: self._calculate_games_since_series(x.shift(1), 'W')
        )
        self.feature_columns.append('games_since_win')

        return df

    def _add_form_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add form-based features (~15 features)"""
        logger.info("Adding form features...")

        for window in [3, 5]:
            feature_name = f'form_L{window}_ppg'
            df[feature_name] = df.groupby('team_name')['points'].transform(
                lambda x: x.shift(1).rolling(
                    window=window, min_periods=1).mean()
            )
            self.feature_columns.append(feature_name)

        for window in [5, 10]:
            feature_name = f'win_rate_L{window}'
            df[feature_name] = df.groupby('team_name')['win'].transform(
                lambda x: x.shift(1).rolling(
                    window=window, min_periods=1).mean()
            )
            self.feature_columns.append(feature_name)

        if 'goals_for' in df.columns:
            for window in [5]:
                feature_name = f'gf_momentum_L{window}'
                df[f'_gf_recent_{window}'] = df.groupby('team_name')['goals_for'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[f'_gf_longer_{window}'] = df.groupby('team_name')['goals_for'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window*2, min_periods=1).mean()
                )
                df[feature_name] = df[f'_gf_recent_{window}'] - \
                    df[f'_gf_longer_{window}']
                df.drop(
                    [f'_gf_recent_{window}', f'_gf_longer_{window}'], axis=1, inplace=True)
                self.feature_columns.append(feature_name)

        if 'goals_against' in df.columns:
            for window in [5]:
                feature_name = f'ga_momentum_L{window}'
                df[f'_ga_recent_{window}'] = df.groupby('team_name')['goals_against'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[f'_ga_longer_{window}'] = df.groupby('team_name')['goals_against'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window*2, min_periods=1).mean()
                )
                df[feature_name] = df[f'_ga_recent_{window}'] - \
                    df[f'_ga_longer_{window}']
                df.drop(
                    [f'_ga_recent_{window}', f'_ga_longer_{window}'], axis=1, inplace=True)
                self.feature_columns.append(feature_name)

        return df

    def _add_goal_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add goal-specific features (~40 features)"""
        logger.info("Adding goal-specific features...")

        for window in [5, 10]:
            for threshold in [0.5, 1.5, 2.5, 3.5]:
                col_name = f'over_{str(threshold).replace(".", "_")}'
                if col_name in df.columns:
                    feature_name = f'pct_over_{str(threshold).replace(".", "_")}_L{window}'
                    df[feature_name] = df.groupby('team_name')[col_name].transform(
                        lambda x: x.shift(1).rolling(
                            window=window, min_periods=1).mean()
                    )
                    self.feature_columns.append(feature_name)

        if 'both_scored' in df.columns:
            for window in [5, 10]:
                feature_name = f'pct_btts_L{window}'
                df[feature_name] = df.groupby('team_name')['both_scored'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

        if 'clean_sheet' in df.columns:
            for window in [5, 10]:
                feature_name = f'clean_sheet_rate_L{window}'
                df[feature_name] = df.groupby('team_name')['clean_sheet'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

        if 'failed_to_score' in df.columns:
            for window in [5, 10]:
                feature_name = f'failed_to_score_rate_L{window}'
                df[feature_name] = df.groupby('team_name')['failed_to_score'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

        return df

    def _add_defensive_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add defensive metrics (~20 features)"""
        logger.info("Adding defensive features...")

        defensive_stats = [
            'shots_against', 'shots_on_target_against', 'xg_against',
            'interceptions', 'tackles_won', 'aerials_won'
        ]

        available_defensive = [
            col for col in defensive_stats if col in df.columns]

        for window in [5, 10]:
            for stat in available_defensive:
                feature_name = f'{stat}_defensive_L{window}_mean'
                df[feature_name] = df.groupby('team_name')[stat].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

        return df

    def _add_venue_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add venue-specific rolling features (~40 features)"""
        logger.info("Adding venue-specific features...")

        venue_stats = ['points', 'goals_for', 'goals_against', 'win']

        for venue in ['Home', 'Away']:
            venue_df = df[df['venue'] == venue].copy()

            for window in [3, 5]:
                for stat in venue_stats:
                    if stat in df.columns:
                        feature_name = f'{stat}_{venue}_L{window}_mean'
                        venue_df[feature_name] = venue_df.groupby('team_name')[stat].transform(
                            lambda x: x.shift(1).rolling(
                                window=window, min_periods=1).mean()
                        )
                        if feature_name not in df.columns:
                            df[feature_name] = np.nan
                        df.loc[venue_df.index,
                               feature_name] = venue_df[feature_name]

                        if feature_name not in self.feature_columns:
                            self.feature_columns.append(feature_name)

        return df

    def _add_xg_intelligence_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add xG intelligence features (NEW - ~30 features)
        These capture finishing quality, chance creation trends, and form trajectory
        """
        logger.info("Adding xG intelligence features...")

        if 'goals_for' in df.columns and 'xg_for' in df.columns:
            # xG Overperformance (finishing above expected)
            for window in [3, 5, 10]:
                feature_name = f'xg_overperf_L{window}'
                df[f'_gf_L{window}'] = df.groupby('team_name')['goals_for'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[f'_xgf_L{window}'] = df.groupby('team_name')['xg_for'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[feature_name] = df[f'_gf_L{window}'] - df[f'_xgf_L{window}']
                df.drop([f'_gf_L{window}', f'_xgf_L{window}'],
                        axis=1, inplace=True)
                self.feature_columns.append(feature_name)

        if 'xg_for' in df.columns:
            # xG Attacking Trend (are chances increasing?)
            feature_name = 'xg_for_momentum'
            df['_xg_for_L3'] = df.groupby('team_name')['xg_for'].transform(
                lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
            )
            df['_xg_for_L10'] = df.groupby('team_name')['xg_for'].transform(
                lambda x: x.shift(1).rolling(window=10, min_periods=1).mean()
            )
            df[feature_name] = (df['_xg_for_L3'] -
                                df['_xg_for_L10']) / (df['_xg_for_L10'] + 0.01)
            df.drop(['_xg_for_L3', '_xg_for_L10'], axis=1, inplace=True)
            self.feature_columns.append(feature_name)

        if 'goals_against' in df.columns and 'xg_against' in df.columns:
            # Defensive xG Gap (keeper/defense performing vs expected)
            for window in [3, 5]:
                feature_name = f'xg_def_gap_L{window}'
                df[f'_ga_L{window}'] = df.groupby('team_name')['goals_against'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[f'_xga_L{window}'] = df.groupby('team_name')['xg_against'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                df[feature_name] = df[f'_ga_L{window}'] - df[f'_xga_L{window}']
                df.drop([f'_ga_L{window}', f'_xga_L{window}'],
                        axis=1, inplace=True)
                self.feature_columns.append(feature_name)

        if 'xg_against' in df.columns:
            # xG Defensive Trend (are chances conceded increasing?)
            feature_name = 'xg_against_momentum'
            df['_xg_against_L3'] = df.groupby('team_name')['xg_against'].transform(
                lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
            )
            df['_xg_against_L10'] = df.groupby('team_name')['xg_against'].transform(
                lambda x: x.shift(1).rolling(window=10, min_periods=1).mean()
            )
            df[feature_name] = (
                df['_xg_against_L3'] - df['_xg_against_L10']) / (df['_xg_against_L10'] + 0.01)
            df.drop(['_xg_against_L3', '_xg_against_L10'],
                    axis=1, inplace=True)
            self.feature_columns.append(feature_name)

        logger.info("Added xG intelligence features")
        return df

    def _add_opponent_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add opponent features (NEW - ~100 features)
        Mirror of key team features from opponent's perspective
        """
        logger.info("Adding opponent features...")

        # Key features to mirror for opponent
        key_features = [
            'goals_for_L3_mean', 'goals_for_L5_mean',
            'goals_against_L3_mean', 'goals_against_L5_mean',
            'xg_for_L3_mean', 'xg_for_L5_mean',
            'xg_against_L3_mean', 'xg_against_L5_mean',
            'points_L3_mean', 'points_L5_mean',
            'form_L3_ppg', 'form_L5_ppg',
            'win_rate_L5', 'win_rate_L10',
            'xg_overperf_L3', 'xg_overperf_L5',
            'xg_for_momentum', 'xg_against_momentum',
            'pct_btts_L5', 'pct_over_2_5_L5',
            'clean_sheet_rate_L5', 'failed_to_score_rate_L5'
        ]

        # Filter to only features that exist
        available_features = [f for f in key_features if f in df.columns]

        # For each match, get opponent's stats
        for feature in available_features:
            opp_feature_name = f'opp_{feature}'

            # Create mapping: for each (team, date), get opponent's feature value
            opponent_map = df.set_index(['opponent', 'date'])[feature]

            # Map opponent's feature to current row
            df[opp_feature_name] = df.apply(
                lambda row: opponent_map.get(
                    (row['team_name'], row['date']), 0),
                axis=1
            )

            self.feature_columns.append(opp_feature_name)

        logger.info(f"Added {len(available_features)} opponent features")
        return df

    def _add_differential_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add differential features (NEW - ~50 features)
        Team stats - Opponent stats = Relative strength
        """
        logger.info("Adding differential features...")

        # Features to create differentials for
        diff_features = [
            'goals_for_L5_mean', 'goals_against_L5_mean',
            'xg_for_L5_mean', 'xg_against_L5_mean',
            'points_L5_mean', 'form_L5_ppg',
            'win_rate_L5', 'xg_overperf_L5',
            'pct_btts_L5', 'clean_sheet_rate_L5'
        ]

        for feature in diff_features:
            if feature in df.columns and f'opp_{feature}' in df.columns:
                diff_name = f'diff_{feature}'
                df[diff_name] = df[feature] - df[f'opp_{feature}']
                self.feature_columns.append(diff_name)

        logger.info("Added differential features")
        return df

    def _add_goal_cross_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add goal cross-features (NEW - ~20 features)
        Features that combine team + opponent for goal predictions
        """
        logger.info("Adding goal cross-features...")

        # Combined goal threat (both teams' attacking)
        if 'goals_for_L5_mean' in df.columns and 'opp_goals_for_L5_mean' in df.columns:
            df['combined_goal_threat'] = (
                df['goals_for_L5_mean'] + df['opp_goals_for_L5_mean']) / 2
            self.feature_columns.append('combined_goal_threat')

        # Combined defensive weakness (both teams' defending)
        if 'goals_against_L5_mean' in df.columns and 'opp_goals_against_L5_mean' in df.columns:
            df['combined_def_weakness'] = (
                df['goals_against_L5_mean'] + df['opp_goals_against_L5_mean']) / 2
            self.feature_columns.append('combined_def_weakness')

        # BTTS likelihood index
        if all(col in df.columns for col in ['goals_for_L5_mean', 'opp_goals_for_L5_mean',
                                             'goals_against_L5_mean', 'opp_goals_against_L5_mean']):
            df['btts_likelihood'] = (
                (df['goals_for_L5_mean'] * df['opp_goals_against_L5_mean']) +
                (df['opp_goals_for_L5_mean'] * df['goals_against_L5_mean'])
            ) / 2
            self.feature_columns.append('btts_likelihood')

        # Total goals expected (team scoring + opponent scoring)
        if 'goals_for_L5_mean' in df.columns and 'opp_goals_for_L5_mean' in df.columns:
            df['total_goals_expected'] = df['goals_for_L5_mean'] + \
                df['opp_goals_for_L5_mean']
            self.feature_columns.append('total_goals_expected')

        # xG-based total expected
        if 'xg_for_L5_mean' in df.columns and 'opp_xg_for_L5_mean' in df.columns:
            df['xg_total_expected'] = df['xg_for_L5_mean'] + \
                df['opp_xg_for_L5_mean']
            self.feature_columns.append('xg_total_expected')

        logger.info("Added goal cross-features")
        return df

    def _add_cards_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add cards-specific features (~15 features)"""
        logger.info("Adding cards features...")

        # Total cards (yellow + red)
        if all(col in df.columns for col in ['cards_yellow', 'cards_red']):
            df['total_cards'] = df['cards_yellow'] + df['cards_red']
            df['total_cards_against'] = df['cards_yellow_against'] + \
                df['cards_red_against']

        # Cards rolling averages
        for window in [5, 10]:
            if 'total_cards' in df.columns:
                # Cards received by team
                feature_name = f'cards_L{window}_mean'
                df[feature_name] = df.groupby('team_name')['total_cards'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

                # Cards drawn (opponent receives)
                feature_name = f'cards_drawn_L{window}_mean'
                df[feature_name] = df.groupby('team_name')['total_cards_against'].transform(
                    lambda x: x.shift(1).rolling(
                        window=window, min_periods=1).mean()
                )
                self.feature_columns.append(feature_name)

        # Cards trend (increasing/decreasing discipline)
        if 'total_cards' in df.columns:
            df['cards_trend'] = df.groupby('team_name')['total_cards'].transform(
                lambda x: x.shift(1).rolling(window=3, min_periods=1).mean() -
                x.shift(1).rolling(window=10, min_periods=1).mean()
            )
            self.feature_columns.append('cards_trend')

        logger.info(f"Added cards features")
        return df


    @staticmethod
    def _calculate_streak_series(series, value):
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
    def _calculate_consecutive_series(series):
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

    @staticmethod
    def _calculate_games_since_series(series, value):
        """Calculate games since last occurrence of value"""
        games_since = []
        count = 0
        for val in series:
            if pd.isna(val):
                count += 1
            elif val == value:
                count = 0
            else:
                count += 1
            games_since.append(count)
        return pd.Series(games_since, index=series.index)

    def get_feature_names(self) -> List[str]:
        """Return list of all generated feature names"""
        return self.feature_columns.copy()

    def get_feature_count(self) -> int:
        """Return total number of features generated"""
        return len(self.feature_columns)

    def get_model_feature_names(self) -> List[str]:
        """
        Return only features safe for modeling (exclude data leakage features)
        
        Excludes:
        - Raw match outcomes (points, win, draw, loss, result indicators)
        - Single-match stats (goal_diff, goals_vs_xg from current match)
        """
        excluded_features = {
            'points', 'goal_diff', 'xg_diff', 'win', 'draw', 'loss',
            'clean_sheet', 'failed_to_score', 'both_scored', 'total_goals',
            'over_0_5', 'over_1_5', 'over_2_5', 'over_3_5',
            'goals_vs_xg', 'defensive_pressure', 'shot_accuracy', 'shots_conversion'
        }
        
        return [f for f in self.feature_columns if f not in excluded_features]
