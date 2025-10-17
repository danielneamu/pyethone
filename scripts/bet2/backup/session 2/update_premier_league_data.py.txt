#!/usr/bin/env python3
"""
Incremental Data Updater for Premier League
Scrapes only NEW matches from FBRef and appends to existing CSV
Run this every 2 days to keep predictions up-to-date
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys
from pathlib import Path
from datetime import datetime
import sys
sys.stdout.reconfigure(line_buffering=True)

# Set up paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'premier_league'
OUTPUT_FILE = DATA_DIR / '2025-2026_all_teams.csv'

# Current season configuration
CURRENT_SEASON = "2025-2026"
SEASON_URL = "2025-2026"  # Format for FBRef URLs

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

# Rate limiting configuration
REQUEST_DELAY = 8
TEAM_DELAY = 15
MAX_RETRIES = 3

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
    }


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


def get_existing_matchweeks(existing_df, team_code):
    """Get set of matchweeks already scraped for a team"""
    if existing_df.empty:
        return set()
    team_data = existing_df[existing_df['team_code'] == team_code]
    if team_data.empty:
        return set()
    return set(team_data['round'].dropna().unique())


def make_request_with_retry(url, max_retries=MAX_RETRIES):
    """Make HTTP request with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 60
                print(f"    ⚠️  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Request error: {e}. Retrying...")
            time.sleep(10)
    raise Exception(f"Failed after {max_retries} retries")


def scrape_schedule(team_code, existing_matchweeks):
    """Scrape team schedule and return only new matches"""
    url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/schedule/"
    response = make_request_with_retry(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', id='matchlogs_for')
    if not table or not table.tbody:
        print(f"      ⚠️  No schedule table found")
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))
        return pd.DataFrame(), []

    columns = [
        'round', 'dayofweek', 'date', 'comp', 'venue',
        'result', 'opponent', 'goals_for', 'goals_against',
        'xg_for', 'xg_against', 'possession', 'attendance',
        'captain', 'formation', 'referee'
    ]

    data = []
    new_row_indices = []
    row_index = 0

    for row in table.tbody.find_all('tr'):
        match_report_cell = row.find('td', {'data-stat': 'match_report'})

        if match_report_cell and 'Match Report' in match_report_cell.text:
            row_data = {}
            for col in columns:
                if col == 'comp':
                    row_data[col] = 'EPL'
                else:
                    cell = row.find(['td', 'th'], {'data-stat': col})
                    row_data[col] = cell.text.strip() if cell else ''

            matchweek = row_data.get('round', '')
            if matchweek not in existing_matchweeks:
                data.append(row_data)
                new_row_indices.append(row_index)

            row_index += 1

    time.sleep(REQUEST_DELAY + random.uniform(1, 3))
    return pd.DataFrame(data, columns=columns), new_row_indices


# [Keep all your existing scrape functions: scrape_table_for_rows, scrape_table_against_rows, scrape_team_data]
# I'm including the scrape_team_data function with minor modifications:
def scrape_table_for_rows(team_code, page_type, row_indices, table_id='matchlogs_for'):
    """Scrape specific rows from a 'for' table (team stats)"""
    if not row_indices:
        return pd.DataFrame()

    url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/{page_type}/"
    response = make_request_with_retry(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', id=table_id)

    if not table:
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))
        return pd.DataFrame()

    headers_row = table.find('thead').find_all('tr')[-1]
    all_columns = []

    for th in headers_row.find_all('th'):
        data_stat = th.get('data-stat')
        if data_stat:
            all_columns.append(data_stat)

    # Skip first 9 columns AND skip match_report
    selected_columns = [
        col for col in all_columns[9:] if col != 'match_report']

    # Rename columns based on page type
    column_mapping = {}
    if page_type == 'shooting':
        column_mapping = {
            'goals': None,  # Skip - duplicate of goals_for
            'xg': 'expected_goals',
            'npxg': 'expected_goals_non_penalty',
            'npxg_per_shot': 'expected_goals_non_penalty_per_shot',
            'xg_net': 'expected_goals_net',
            'npxg_net': 'expected_goals_non_penalty_net'
        }

    data = []
    all_rows = table.tbody.find_all('tr')

    for idx in row_indices:
        if idx < len(all_rows):
            row = all_rows[idx]
            row_data = {}
            for col in selected_columns:
                # Skip columns marked as None
                if col in column_mapping and column_mapping[col] is None:
                    continue

                cell = row.find(['td', 'th'], {'data-stat': col})
                # Apply column rename if exists
                new_col_name = column_mapping.get(col, col)
                if cell:
                    row_data[new_col_name] = cell.text.strip()
                else:
                    row_data[new_col_name] = ''
            data.append(row_data)

    time.sleep(REQUEST_DELAY + random.uniform(1, 3))
    return pd.DataFrame(data)


def scrape_table_against_rows(team_code, page_type, row_indices, table_id='matchlogs_against'):
    """Scrape specific rows from an 'against' table (opponent stats)"""
    if not row_indices:
        return pd.DataFrame()

    url = f"https://fbref.com/en/squads/{team_code}/{SEASON_URL}/matchlogs/c9/{page_type}/"
    response = make_request_with_retry(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', id=table_id)

    if not table:
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))
        return pd.DataFrame()

    headers_row = table.find('thead').find_all('tr')[-1]
    all_columns = []

    for th in headers_row.find_all('th'):
        data_stat = th.get('data-stat')
        if data_stat:
            all_columns.append(data_stat)

    # Skip first 9 columns AND skip match_report
    selected_columns = [
        col for col in all_columns[9:] if col != 'match_report']

    # Rename columns based on page type
    column_mapping = {}
    if page_type == 'shooting':
        column_mapping = {
            'goals': None,  # Skip - duplicate of goals_against
            'xg': 'expected_goals',
            'npxg': 'expected_goals_non_penalty',
            'npxg_per_shot': 'expected_goals_non_penalty_per_shot',
            'xg_net': 'expected_goals_net',
            'npxg_net': 'expected_goals_non_penalty_net'
        }

    data = []
    all_rows = table.tbody.find_all('tr')

    for idx in row_indices:
        if idx < len(all_rows):
            row = all_rows[idx]
            row_data = {}
            for col in selected_columns:
                # Skip columns marked as None
                if col in column_mapping and column_mapping[col] is None:
                    continue

                cell = row.find(['td', 'th'], {'data-stat': col})
                # Apply column rename if exists, then add _against suffix
                base_name = column_mapping.get(col, col)
                new_col_name = base_name + '_against'
                if cell:
                    row_data[new_col_name] = cell.text.strip()
                else:
                    row_data[new_col_name] = ''
            data.append(row_data)

    time.sleep(REQUEST_DELAY + random.uniform(1, 3))
    return pd.DataFrame(data)


def scrape_team_data(team_name, team_code, existing_matchweeks):
    """Scrape all data for a team (only new matches)"""
    print(f"\n[Scraping {team_name}]")

    if existing_matchweeks:
        print(f"  Existing matchweeks: {sorted(existing_matchweeks)}")

    try:
        print(f"  → Checking schedule for new matches...")
        df_schedule, new_row_indices = scrape_schedule(
            team_code, existing_matchweeks)

        if df_schedule.empty:
            print(f"  ✓ No new matches")
            return pd.DataFrame()

        print(f"  → Found {len(new_row_indices)} new matches")

        print(f"  → Shooting (for & against)...")
        df_shooting_for = scrape_table_for_rows(
            team_code, 'shooting', new_row_indices)
        df_shooting_against = scrape_table_against_rows(
            team_code, 'shooting', new_row_indices)

        print(f"  → GCA (for & against)...")
        df_gca_for = scrape_table_for_rows(team_code, 'gca', new_row_indices)
        df_gca_against = scrape_table_against_rows(
            team_code, 'gca', new_row_indices)

        print(f"  → Misc (for & against)...")
        df_misc_for = scrape_table_for_rows(team_code, 'misc', new_row_indices)
        df_misc_against = scrape_table_against_rows(
            team_code, 'misc', new_row_indices)

        # Merge all dataframes horizontally
        df_merged = pd.concat([
            df_schedule,
            df_shooting_for,
            df_shooting_against,
            df_gca_for,
            df_gca_against,
            df_misc_for,
            df_misc_against
        ], axis=1)

        # Add team name and code as first columns
        df_merged.insert(0, 'team_code', team_code)
        df_merged.insert(0, 'team_name', team_name)

        print(f"  ✓ Scraped {len(df_merged)} matches")

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

    print(f"\nStarting incremental scrape...")
    print(f"  Request delay: ~{REQUEST_DELAY}s")
    print(f"  Team delay: ~{TEAM_DELAY}s\n")

    # Scrape each team
    for idx, (team_name, team_code) in enumerate(TEAMS_2025_2026.items(), 1):
        print(f"[{idx}/{len(TEAMS_2025_2026)}]", end=" ")
        existing_matchweeks = get_existing_matchweeks(existing_df, team_code)
        team_df = scrape_team_data(team_name, team_code, existing_matchweeks)

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
