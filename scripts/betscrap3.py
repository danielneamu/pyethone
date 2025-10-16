from collections import Counter
import requests
from bs4 import BeautifulSoup
import time

# Test with one team
team_code = "822bd0ba"  # Liverpool
season = "2025-2026"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_table_columns(url, table_id):
    """Get all column names from a specific table"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', id=table_id)
        if not table:
            return None

        # Get header row
        headers_row = table.find('thead').find_all('tr')[-1]
        columns = []

        for th in headers_row.find_all('th'):
            data_stat = th.get('data-stat')
            if data_stat:
                columns.append(data_stat)

        return columns
    except Exception as e:
        print(f"Error: {e}")
        return None


# URLs to check
pages = {
    'schedule': f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/schedule/",
    'shooting': f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/shooting/",
    'gca': f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/gca/",
    'misc': f"https://fbref.com/en/squads/{team_code}/{season}/matchlogs/c9/misc/"
}

print("="*80)
print(f"COLUMN ANALYSIS FOR {team_code} - {season}")
print("="*80)

all_columns = {}

for page_name, url in pages.items():
    print(f"\n{'='*80}")
    print(f"PAGE: {page_name.upper()}")
    print(f"{'='*80}")

    # matchlogs_for
    print(f"\nTable: matchlogs_for")
    cols = get_table_columns(url, 'matchlogs_for')
    if cols:
        print(f"  Total columns: {len(cols)}")
        print(f"  First 9 (skipped): {cols[:9]}")
        print(f"  From 10th onward (used): {cols[9:]}")
        all_columns[f"{page_name}_for"] = cols
    else:
        print("  ✗ Table not found")

    time.sleep(2)

    # matchlogs_against
    print(f"\nTable: matchlogs_against")
    cols = get_table_columns(url, 'matchlogs_against')
    if cols:
        print(f"  Total columns: {len(cols)}")
        print(f"  First 9 (skipped): {cols[:9]}")
        print(f"  From 10th onward (used with '_against'): {cols[9:]}")
        all_columns[f"{page_name}_against"] = cols
    else:
        print("  ✗ Table not found")

    time.sleep(2)

# Now check for duplicates across all extracted columns
print("\n" + "="*80)
print("DUPLICATE ANALYSIS")
print("="*80)

# Simulate what the script does
final_columns = []

# Schedule gets all columns
if 'schedule_for' in all_columns:
    schedule_cols = ['round', 'dayofweek', 'date', 'time', 'comp', 'venue',
                     'result', 'opponent', 'goals_for', 'goals_against',
                     'xg_for', 'xg_against', 'possession', 'attendance',
                     'captain', 'formation', 'referee']
    final_columns.extend([(col, 'schedule') for col in schedule_cols])

# Other tables: skip first 9, use rest
for key, cols in all_columns.items():
    if key == 'schedule_for':
        continue

    if '_for' in key and key != 'schedule_for':
        page_name = key.replace('_for', '')
        extracted_cols = cols[9:]
        final_columns.extend([(col, key) for col in extracted_cols])

    elif '_against' in key:
        page_name = key.replace('_against', '')
        extracted_cols = cols[9:]
        # Add _against suffix
        final_columns.extend([(col + '_against', key)
                             for col in extracted_cols])

# Find duplicates
col_names = [col for col, _ in final_columns]
col_counts = Counter(col_names)
duplicates = {col: count for col, count in col_counts.items() if count > 1}

if duplicates:
    print("\n⚠️  DUPLICATE COLUMNS FOUND:")
    for col, count in sorted(duplicates.items()):
        sources = [source for c, source in final_columns if c == col]
        print(f"  '{col}' appears {count} times")
        print(f"    Sources: {sources}")
else:
    print("\n✓ No duplicate columns found")

print(f"\nTotal final columns: {len(col_names)}")
print(f"Unique columns: {len(set(col_names))}")

# Show all final columns
print("\n" + "="*80)
print("ALL FINAL COLUMNS (in order)")
print("="*80)
seen = set()
for col, source in final_columns:
    if col not in seen:
        print(f"  {col:40s} from {source}")
        seen.add(col)
    else:
        print(f"  {col:40s} from {source} *** DUPLICATE ***")
