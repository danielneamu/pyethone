"""
Test script for DataLoader
Run this to verify data loading works correctly
"""
import sys
from pathlib import Path

# Add python_api to path
sys.path.insert(0, str(Path(__file__).parent))

from services.data_loader import DataLoader, load_data_for_training
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_data_loader():
    """Test the DataLoader functionality"""

    print("=" * 80)
    print("Testing DataLoader")
    print("=" * 80)

    # Initialize loader for Premier League
    loader = DataLoader('premier_league')

    # Test 1: Get available seasons
    print("\nTest 1: Available Seasons")
    print("-" * 40)
    seasons = loader.get_available_seasons()
    print(f"Found {len(seasons)} seasons: {seasons}")

    # Test 2: Load single season
    print("\nTest 2: Load Single Season (2025-2026)")
    print("-" * 40)
    df = loader.load_season('2025-2026')
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {len(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Teams: {df['team_name'].nunique()}")
    print(f"\nFirst few rows:")
    print(df[['date', 'team_name', 'opponent', 'venue', 'result', 'goals_for', 'goals_against']].head())

    # Test 3: Get team list
    print("\nTest 3: Get Team List")
    print("-" * 40)
    teams = loader.get_team_list('2025-2026')
    print(f"Teams in 2025-2026: {teams}")

    # Test 4: Get specific team data
    print("\nTest 4: Get Team Data (Arsenal)")
    print("-" * 40)
    arsenal_df = loader.get_team_data('2025-2026', 'Arsenal')
    print(f"Arsenal matches: {len(arsenal_df)}")
    print(arsenal_df[['date', 'opponent', 'venue', 'result', 'goals_for', 'goals_against']].head())

    # Test 5: Load multiple seasons
    print("\nTest 5: Load Multiple Seasons")
    print("-" * 40)
    multi_df = loader.load_multiple_seasons(['2023-2024', '2024-2025'])
    print(f"Combined data: {len(multi_df)} rows")
    print(f"Seasons: {multi_df['season'].unique()}")
    print(f"Date range: {multi_df['date'].min()} to {multi_df['date'].max()}")

    # Test 6: Data summary
    print("\nTest 6: Data Summary")
    print("-" * 40)
    summary = loader.get_data_summary('2024-2025')
    print(f"Season: {summary['season']}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Total matches: {summary['total_matches']}")
    print(f"Number of teams: {summary['num_teams']}")
    print(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")

    # Test 7: Training data split
    print("\nTest 7: Training Data Split")
    print("-" * 40)
    train_df, val_df, test_df = load_data_for_training(
        'premier_league',
        train_seasons=['2023-2024'],
        val_seasons=['2024-2025'],
        test_seasons=['2025-2026']
    )
    print(f"Train: {len(train_df)} rows")
    print(f"Val: {len(val_df)} rows")
    print(f"Test: {len(test_df)} rows")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    test_data_loader()