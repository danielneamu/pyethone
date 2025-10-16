import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# Competition codes mapping
COMPETITION_CODES = {
    'c9': 'EPL',      # Premier League
    'c12': 'La Liga',
    'c11': 'Serie A',
    'c20': 'Bundesliga',
    'c13': 'Ligue 1',
    '8;': 'Champions League',
    '19;': 'Europa League',
    '882;': 'Europa Conference League',
    '514': 'FA Cup',
    '690': 'EFL Cup',
    '10': 'EFL Championship',
    # Add more as needed
}
# Premier League teams for 2025-2026 season
teams2526 = {
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

teams2425= {
    'Arsenal': '18bb7c10',
    'Aston Villa': '8602292d',
    'Bournemouth': '4ba7cbea',
    'Brentford': 'cd051869',
    'Brighton': 'd07537b9',
    'Chelsea': 'cff3d9bb',
    'Crystal Palace': '47c64c55',
    'Everton': 'd3fd31cc',
    'Fulham': 'fd962109',
    'Ipswich Town': 'b74092de', 
    'Leicester City': 'a2d435b3',
    'Liverpool': '822bd0ba',
    'Manchester City': 'b8fd03ef',
    'Manchester Utd': '19538871',
    'Newcastle Utd': 'b2b47a98',
    'Nott\'ham Forest': 'e4a775cb',
    'Southampton': '33c895d4',
    'Tottenham': '361ca564',
    'West Ham': '7c21e445',
    'Wolves': '8cec06e1'
}

teams = {
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
    'Liverpool': '822bd0ba',
    'Luton Town': 'e297cd13',
    'Manchester City': 'b8fd03ef',
    'Manchester Utd': '19538871',
    'Newcastle Utd': 'b2b47a98',
    'Nott\'ham Forest': 'e4a775cb',
    'Sheffield Utd': '1df6b87e',
    'Tottenham': '361ca564',
    'West Ham': '7c21e445',
    'Wolves': '8cec06e1'
}


season = "2023-2024"
output_filename = f'premier_league_{season}_all_teams.csv'

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

REQUEST_DELAY = 8
TEAM_DELAY = 15
MAX_RETRIES = 3


def get_random_headers():
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def load_existing_data():
    if os.path.exists(output_filename):
        print(f"Found existing file: {output_filename}")
        df = pd.read_csv(output_filename)
        print(
            f"  Existing data: {len(df)} matches, {df['team_name'].nunique()} teams")
        return df
    else:
        print("No existing file found. Will create new dataset.")
        return pd.DataFrame()


def get_existing_matchweeks(existing_df, team_code):
    if existing_df.empty:
        return set()
    team_data = existing_df[existing_df['team_code'] == team_code]
    if team_data.empty:
        return set()
    matchweeks = set(team_data['round'].dropna().unique())
    return matchweeks


def make_request_with_retry(url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 60
                print(
                    f"    ⚠️  Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Request error: {e}. Retrying in 10s...")
            time.sleep(10)
    raise Exception(f"Failed after {max_retries} retries")


def scrape_schedule(team_code, existing_matchweeks):
    url = f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/schedule/"
    response = make_request_with_retry(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', id='matchlogs_for')

    # Add better error handling
    if not table:
        print(f"      ⚠️  No matchlogs_for table found at {url}")
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))
        return pd.DataFrame(), []

    if not table.tbody:
        print(f"      ⚠️  Table found but no tbody at {url}")
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))
        return pd.DataFrame(), []

    # Rest of the function stays the same...
    columns = [
        'round', 'dayofweek', 'date', 'comp', 'venue',
        'result', 'opponent', 'goals_for', 'goals_against',
        'xg_for', 'xg_against', 'possession', 'attendance',
        'captain', 'formation', 'referee'
    ]

    data = []
    new_rows_indices = []
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
                    if cell:
                        row_data[col] = cell.text.strip()
                    else:
                        row_data[col] = ''

            matchweek = row_data.get('round', '')
            if matchweek not in existing_matchweeks:
                data.append(row_data)
                new_rows_indices.append(row_index)

            row_index += 1

    time.sleep(REQUEST_DELAY + random.uniform(1, 3))
    return pd.DataFrame(data, columns=columns), new_rows_indices





def scrape_table_for_rows(team_code, page_type, row_indices, table_id='matchlogs_for'):
    if not row_indices:
        return pd.DataFrame()

    url = f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/{page_type}/"
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
    if not row_indices:
        return pd.DataFrame()

    url = f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/{page_type}/"
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
    print(f"\nScraping {team_name} ({team_code})...")

    if existing_matchweeks:
        print(f"  Existing matchweeks: {sorted(existing_matchweeks)}")

    try:
        print(f"  → Checking schedule for new matches...")
        df_schedule, new_row_indices = scrape_schedule(
            team_code, existing_matchweeks)

        if df_schedule.empty:
            print(f"  ✓ {team_name}: No new matches to scrape")
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

        # Merge all dataframes
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

        print(f"  ✓ {team_name}: {len(df_merged)} new matches scraped")

        wait_time = TEAM_DELAY + random.uniform(3, 7)
        print(f"  ⏳ Waiting {wait_time:.1f} seconds before next team...")
        time.sleep(wait_time)

        return df_merged

    except Exception as e:
        print(f"  ✗ Error scraping {team_name}: {str(e)}")
        time.sleep(TEAM_DELAY * 3)
        return pd.DataFrame()


# Main execution
print(f"{'='*60}")
print(f"Premier League {season} - Incremental Scraper (Fixed)")
print(f"{'='*60}\n")

existing_df = load_existing_data()
new_teams_data = []

print(
    f"\nStarting scrape with ~{REQUEST_DELAY}s delay between requests and ~{TEAM_DELAY}s between teams...")
print(f"Using {len(user_agents)} different user agents for rotation\n")

for idx, (team_name, team_code) in enumerate(teams.items(), 1):
    print(f"[{idx}/20]", end=" ")
    existing_matchweeks = get_existing_matchweeks(existing_df, team_code)
    team_df = scrape_team_data(team_name, team_code, existing_matchweeks)

    if not team_df.empty:
        new_teams_data.append(team_df)

if new_teams_data:
    df_new_data = pd.concat(new_teams_data, ignore_index=True)

    if not existing_df.empty:
        df_all_teams = pd.concat([existing_df, df_new_data], ignore_index=True)
        print(
            f"\n✓ Added {len(df_new_data)} new matches to existing {len(existing_df)} matches")
    else:
        df_all_teams = df_new_data
        print(f"\n✓ Created new dataset with {len(df_new_data)} matches")

    df_all_teams.to_csv(output_filename, index=False)

    print(f"\n{'='*60}")
    print(f"✓ Data saved to {output_filename}")
    print(f"Total matches: {len(df_all_teams)}")
    print(f"Total columns: {len(df_all_teams.columns)}")
    print(f"Teams included: {df_all_teams['team_name'].nunique()}")
    print(f"{'='*60}")
else:
    print("\n✓ No new data to add. All teams are up to date!")
