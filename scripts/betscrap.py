import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://fbref.com/en/comps/9/Premier-League-Stats"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

# Parse the home/away table by id
home_away_table = soup.find('table', id='results2025-202691_home_away')

# Parse the squad stats table by id
squad_stats_table = soup.find('table', id='stats_squads_gca_for')

def parse_table(table, columns):
    data = []
    for row in table.tbody.find_all('tr')[:20]: # first 20 rows
        cells = row.find_all(['th', 'td'])
        row_data = []
        for col in columns:
            cell = row.find(attrs={"data-stat": col})
            if cell:
                text = cell.text.strip()
                row_data.append(text)
            else:
                row_data.append('')
        data.append(row_data)
    return data

home_away_cols = ['team', 'home_xg_for', 'home_xg_against', 'home_xg_diff', 'home_xg_diff_per90', 
                  'away_xg_for', 'away_xg_against', 'away_xg_diff', 'away_xg_diff_per90']

squad_cols = ['team', 'sca', 'sca_per90', 'gca', 'gca_per90']

opponent_cols = ['team', 'sca', 'sca_per90', 'gca', 'gca_per90']

home_away_data = parse_table(home_away_table, home_away_cols)
squad_data = parse_table(squad_stats_table, squad_cols)

# FBref uses separate tables for opponents; a similar method can be used if data is present on same page or another URL.

# Merge dataframes on team name
df_home_away = pd.DataFrame(home_away_data, columns=home_away_cols)
df_squad = pd.DataFrame(squad_data, columns=squad_cols)

df_merged = pd.merge(df_home_away, df_squad, on='team', suffixes=('', '_squad'))

print(df_merged.head(20))

# Save to csv if needed
df_merged.to_csv('premier_league_stats.csv', index=False)
