"""
Data Loader Service
Loads and validates CSV data files for football matches
"""
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import DATA_DIR

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handles loading and basic validation of match data from CSV files
    """

    def __init__(self, competition: str):
        """
        Initialize DataLoader for a specific competition

        Args:
            competition: Competition ID (e.g., 'premier_league')
        """
        self.competition = competition
        self.data_dir = DATA_DIR / competition

        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found for competition: {competition}")

    def load_season(self, season: str) -> pd.DataFrame:
        """
        Load data for a single season

        Args:
            season: Season identifier (e.g., '2023-2024')

        Returns:
            DataFrame with match data
        """
        file_path = self.data_dir / f"{season}_all_teams.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        logger.info(f"Loading data from {file_path}")

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from {season}")

            # Basic validation
            self._validate_dataframe(df, season)

            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Sort by date (critical for time-series features)
            df = df.sort_values('date').reset_index(drop=True)

            # Add season identifier
            df['season'] = season

            return df

        except Exception as e:
            logger.error(f"Error loading {season}: {str(e)}")
            raise

    def load_multiple_seasons(self, seasons: List[str]) -> pd.DataFrame:
        """
        Load and combine data from multiple seasons

        Args:
            seasons: List of season identifiers

        Returns:
            Combined DataFrame sorted by date
        """
        logger.info(f"Loading {len(seasons)} seasons: {seasons}")

        dfs = []
        for season in seasons:
            df = self.load_season(season)
            dfs.append(df)

        # Combine all seasons
        combined = pd.concat(dfs, ignore_index=True)

        # Sort by date across all seasons
        combined = combined.sort_values('date').reset_index(drop=True)

        logger.info(f"Combined dataset: {len(combined)} rows across {len(seasons)} seasons")

        return combined

    def get_available_seasons(self) -> List[str]:
        """
        Get list of available seasons for this competition

        Returns:
            List of season identifiers sorted by year
        """
        seasons = []

        for file in self.data_dir.glob('*_all_teams.csv'):
            season = file.stem.replace('_all_teams', '')
            seasons.append(season)

        # Sort seasons (most recent first)
        seasons.sort(reverse=True)

        return seasons

    def get_team_list(self, season: str) -> List[str]:
        """
        Get list of teams in a season

        Args:
            season: Season identifier

        Returns:
            Sorted list of team names
        """
        df = self.load_season(season)
        teams = sorted(df['team_name'].unique())
        return teams

    def get_team_data(self, season: str, team_name: str) -> pd.DataFrame:
        """
        Get all matches for a specific team in a season

        Args:
            season: Season identifier
            team_name: Name of the team

        Returns:
            DataFrame with team's matches
        """
        df = self.load_season(season)
        team_df = df[df['team_name'] == team_name].copy()

        logger.info(f"Found {len(team_df)} matches for {team_name} in {season}")

        return team_df

    def _validate_dataframe(self, df: pd.DataFrame, season: str):
        """
        Validate that DataFrame has required columns and data quality

        Args:
            df: DataFrame to validate
            season: Season identifier (for error messages)
        """
        required_columns = [
            'team_name', 'date', 'venue', 'opponent', 'result',
            'goals_for', 'goals_against', 'xg_for', 'xg_against'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(
                f"Missing required columns in {season}: {missing_columns}"
            )

        # Check for data quality issues
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values found in {season}:")
            for col, count in null_counts[null_counts > 0].items():
                logger.warning(f"  {col}: {count} nulls")

        # Validate venue values
        valid_venues = ['Home', 'Away']
        invalid_venues = df[~df['venue'].isin(valid_venues)]['venue'].unique()
        if len(invalid_venues) > 0:
            raise ValueError(f"Invalid venue values in {season}: {invalid_venues}")

        # Validate result values
        valid_results = ['W', 'D', 'L']
        invalid_results = df[~df['result'].isin(valid_results)]['result'].unique()
        if len(invalid_results) > 0:
            raise ValueError(f"Invalid result values in {season}: {invalid_results}")

        logger.info(f"Validation passed for {season}")

    def get_data_summary(self, season: str) -> Dict:
        """
        Get summary statistics for a season's data

        Args:
            season: Season identifier

        Returns:
            Dictionary with summary statistics
        """
        df = self.load_season(season)

        summary = {
            'season': season,
            'total_rows': len(df),
            'total_matches': len(df) // 2,  # Each match appears twice
            'num_teams': df['team_name'].nunique(),
            'teams': sorted(df['team_name'].unique()),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict()
        }

        return summary


def load_data_for_training(
    competition: str,
    train_seasons: List[str],
    val_seasons: List[str],
    test_seasons: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Load data for model training with train/val/test split

    Args:
        competition: Competition ID
        train_seasons: List of seasons for training
        val_seasons: List of seasons for validation
        test_seasons: Optional list of seasons for testing

    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    loader = DataLoader(competition)

    logger.info("Loading training data...")
    train_df = loader.load_multiple_seasons(train_seasons)

    logger.info("Loading validation data...")
    val_df = loader.load_multiple_seasons(val_seasons)

    test_df = None
    if test_seasons:
        logger.info("Loading test data...")
        test_df = loader.load_multiple_seasons(test_seasons)

    logger.info(f"Data loaded - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df) if test_df is not None else 0}")

    return train_df, val_df, test_df