"""
Data processor for FBRef HTML
Handles all BeautifulSoup parsing and DataFrame construction
"""

from bs4 import BeautifulSoup
import pandas as pd


def parse_schedule(html, existing_matchweeks):
    """
    Parse schedule table from HTML
    Returns: (DataFrame, list of new row indices)
    """
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='matchlogs_for')

    if not table or not table.tbody:
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
        # Only process rows with match reports (completed matches)
        match_report_cell = row.find('td', {'data-stat': 'match_report'})

        if match_report_cell and 'Match Report' in match_report_cell.text:
            row_data = {}

            for col in columns:
                if col == 'comp':
                    row_data[col] = 'EPL'
                else:
                    cell = row.find(['td', 'th'], {'data-stat': col})
                    row_data[col] = cell.text.strip() if cell else ''

            # Check if this matchweek is new
            matchweek = row_data.get('round', '')
            if matchweek not in existing_matchweeks:
                data.append(row_data)
                new_row_indices.append(row_index)

            row_index += 1

    return pd.DataFrame(data, columns=columns), new_row_indices


def parse_stats_table(html, table_id, row_indices, is_against=False, page_type=None):
    """
    Parse stats table (for or against) from HTML for specific row indices
    
    Args:
        html: HTML content
        table_id: 'matchlogs_for' or 'matchlogs_against'
        row_indices: List of row indices to extract
        is_against: If True, append '_against' to column names
        page_type: 'shooting', 'gca', 'misc' - for special column handling
    
    Returns: DataFrame with extracted stats
    """
    if not row_indices:
        return pd.DataFrame()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id=table_id)

    if not table:
        return pd.DataFrame()

    # Get column names from header
    headers_row = table.find('thead').find_all('tr')[-1]
    all_columns = [th.get('data-stat')
                   for th in headers_row.find_all('th') if th.get('data-stat')]

    # Skip first 9 columns (match info) and skip 'match_report'
    selected_columns = [
        col for col in all_columns[9:] if col != 'match_report']

    # Define column mappings/exclusions by page type
    column_mapping = {}
    if page_type == 'shooting':
        column_mapping = {
            'goals': None,  # Skip - duplicate
            'xg': 'expected_goals',
            'npxg': 'expected_goals_non_penalty',
            'npxg_per_shot': 'expected_goals_non_penalty_per_shot',
            'xg_net': 'expected_goals_net',
            'npxg_net': 'expected_goals_non_penalty_net'
        }

    # Extract data for specified rows
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

                # Add '_against' suffix for opponent stats
                if is_against:
                    new_col_name = new_col_name + '_against'

                row_data[new_col_name] = cell.text.strip() if cell else ''

            data.append(row_data)

    return pd.DataFrame(data)


def merge_team_data(df_schedule, df_shooting_for, df_shooting_against,
                    df_gca_for, df_gca_against, df_misc_for, df_misc_against,
                    team_name, team_code):
    """
    Merge all dataframes horizontally and add team identifiers
    Returns: Merged DataFrame
    """
    df_merged = pd.concat([
        df_schedule,
        df_shooting_for,
        df_shooting_against,
        df_gca_for,
        df_gca_against,
        df_misc_for,
        df_misc_against
    ], axis=1)

    # Add team info as first columns
    df_merged.insert(0, 'team_code', team_code)
    df_merged.insert(0, 'team_name', team_name)

    return df_merged


def get_existing_matchweeks(existing_df, team_code):
    """
    Extract set of matchweeks already in dataset for a specific team
    Returns: Set of matchweek strings
    """
    if existing_df.empty:
        return set()

    team_data = existing_df[existing_df['team_code'] == team_code]
    if team_data.empty:
        return set()

    return set(team_data['round'].dropna().unique())
