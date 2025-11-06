#!/usr/bin/env python3
"""
Incremental Data Updater for Premier League
Scrapes only NEW matches from FBRef and appends to existing CSV
Run this every 2 days to keep predictions up-to-date
"""

from data_processor import (
    parse_schedule,
    parse_stats_table,
    merge_team_data,
    get_existing_matchweeks
)
from scraper import create_scraper
from datetime import datetime
import random
import time
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


# Import our modules

# Set up paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'premier_league'
OUTPUT_FILE = DATA_DIR / '2025-2026_all_teams.csv'

# Current season configuration
CURRENT_SEASON = "2025-2026"
SEASON_URL = "2025-2026"

# Premier League teams for 2025-2026 season
TEAMS_2025_2026 = {
    'Arsenal': '18bb7c10',
    'Aston Villa': '8602292d',
    'Bournemouth': '4ba7cbea',
    'Brentford': 'cd051869',
    'Brighton': 'd07537b9',
    'Burnley': '943e8050',
    'Chelsea': 'cff3d9bb',
    'Crystal Palace': '47c64c55',
    'Everton': 'd3fd31cc',
    'Fulham': 'fd962109',
    'Leeds United': '5bfb9659',
    'Liverpool': '822bd0ba',
    'Manchester City': 'b8fd03ef',
    'Manchester Utd': '19538871',
    'Newcastle Utd': 'b2b47a98',
    'Nott\'ham Forest': 'e4a775cb',
    'Sunderland': '8ef52968',
    'Tottenham': '361ca564',
    'West Ham': '7c21e445',
    'Wolves': '8cec06e1'
}

# Rate limiting
TEAM_DELAY = 15


def load_existing_data():
    """Load existing CSV data if it exists"""
    if OUTPUT_FILE.exists():
        print(f"✓ Found existing file: {OUTPUT_FILE}")
        df = pd.read_csv(OUTPUT_FILE)
        print(
            f"  Existing data: {len(df)} matches, {df['team_name'].nunique()} teams")
        return df
    else:
        print("ℹ️  No existing file found. Will create new dataset.")
        return pd.DataFrame()


def scrape_team_data(scraper, team_name, team_code, existing_matchweeks):
    """
    Scrape all data for a team (only new matches)
    Uses Playwright scraper for fetching, data_processor for parsing
    """
    print(f"\n[Scraping {team_name}]")

    if existing_matchweeks:
        print(f"  Existing matchweeks: {sorted(existing_matchweeks)}")

    try:
        # 1. Get schedule and identify new matches
        print(f"  → Checking schedule for new matches...")
        schedule_url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/schedule/"
        schedule_html = scraper.fetch_page(schedule_url)
        df_schedule, new_row_indices = parse_schedule(
            schedule_html, existing_matchweeks)

        if df_schedule.empty:
            print(f"  ✓ No new matches")
            return pd.DataFrame()

        print(f"  → Found {len(new_row_indices)} new matches")

        # 2. Scrape shooting stats (for & against)
        print(f"  → Shooting (for & against)...")
        shooting_url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/shooting/"
        shooting_html = scraper.fetch_page(shooting_url)
        df_shooting_for = parse_stats_table(shooting_html, 'matchlogs_for', new_row_indices,
                                            is_against=False, page_type='shooting')
        df_shooting_against = parse_stats_table(shooting_html, 'matchlogs_against', new_row_indices,
                                                is_against=True, page_type='shooting')

        # 3. Scrape GCA stats (for & against)
        print(f"  → GCA (for & against)...")
        gca_url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/gca/"
        gca_html = scraper.fetch_page(gca_url)
        df_gca_for = parse_stats_table(
            gca_html, 'matchlogs_for', new_row_indices, is_against=False)
        df_gca_against = parse_stats_table(
            gca_html, 'matchlogs_against', new_row_indices, is_against=True)

        # 4. Scrape misc stats (for & against)
        print(f"  → Misc (for & against)...")
        misc_url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/misc/"
        misc_html = scraper.fetch_page(misc_url)
        df_misc_for = parse_stats_table(
            misc_html, 'matchlogs_for', new_row_indices, is_against=False)
        df_misc_against = parse_stats_table(
            misc_html, 'matchlogs_against', new_row_indices, is_against=True)

        # 5. Merge all data
        df_merged = merge_team_data(
            df_schedule, df_shooting_for, df_shooting_against,
            df_gca_for, df_gca_against, df_misc_for, df_misc_against,
            team_name, team_code
        )

        print(f"  ✓ Scraped {len(df_merged)} matches")

        # Wait between teams
        wait_time = TEAM_DELAY + random.uniform(3, 7)
        print(f"  ⏳ Waiting {wait_time:.1f}s...")
        time.sleep(wait_time)

        return df_merged

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        time.sleep(TEAM_DELAY * 3)
        return pd.DataFrame()


def main():
    print("=" * 70)
    print(f"Premier League {CURRENT_SEASON} - Data Update Script")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing data
    existing_df = load_existing_data()
    new_teams_data = []

    print(f"\nStarting incremental scrape with Playwright...")

    # Create Playwright scraper (context manager handles browser lifecycle)
    with create_scraper() as scraper:
        # Scrape each team
        for idx, (team_name, team_code) in enumerate(TEAMS_2025_2026.items(), 1):
            print(f"[{idx}/{len(TEAMS_2025_2026)}]", end=" ")
            existing_matchweeks = get_existing_matchweeks(
                existing_df, team_code)
            team_df = scrape_team_data(
                scraper, team_name, team_code, existing_matchweeks)

            if not team_df.empty:
                new_teams_data.append(team_df)

    # Save results
    if new_teams_data:
        df_new_data = pd.concat(new_teams_data, ignore_index=True)

        if not existing_df.empty:
            df_all = pd.concat([existing_df, df_new_data], ignore_index=True)
            print(f"\n✓ Added {len(df_new_data)} new matches")
        else:
            df_all = df_new_data
            print(f"\n✓ Created new dataset with {len(df_new_data)} matches")

        df_all.to_csv(OUTPUT_FILE, index=False)

        print(f"\n{'='*70}")
        print(f"✓ Data saved to: {OUTPUT_FILE}")
        print(f"  Total matches: {len(df_all)}")
        print(f"  Total teams: {df_all['team_name'].nunique()}")
        print(f"{'='*70}")
    else:
        print("\n✓ No new data. All teams up to date!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
