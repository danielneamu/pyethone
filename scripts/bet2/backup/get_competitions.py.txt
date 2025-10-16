"""
Get Competitions - Standalone Script
Returns available competitions as JSON
Called from PHP via exec()
"""
from config import DATA_DIR
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def get_competitions():
    """Get list of available competitions"""
    try:
        import pandas as pd

        # Read competitions.csv
        comp_file = DATA_DIR / "competitions.csv"

        if not comp_file.exists():
            return {"error": "Competitions file not found"}

        df = pd.read_csv(comp_file)

        # Get available seasons for each competition
        competitions = []
        for _, row in df.iterrows():
            comp_id = row['competition_id']
            comp_dir = DATA_DIR / comp_id

            # Find available seasons
            seasons = []
            if comp_dir.exists():
                for file in comp_dir.glob('*_all_teams.csv'):
                    season = file.stem.replace('_all_teams', '')
                    seasons.append(season)

            seasons.sort(reverse=True)

            competitions.append({
                "id": comp_id,
                "name": row['competition_name'],
                "country": row['country'],
                "seasons": seasons,
                "active": bool(row['active'])
            })

        return {"success": True, "competitions": competitions}

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = get_competitions()
    print(json.dumps(result))
