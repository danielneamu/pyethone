"""
Get Teams - Standalone Script
Returns teams for a competition/season as JSON
Called from PHP via exec()
Usage: python get_teams.py <competition> <season>
"""
from services.data_loader import DataLoader
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def get_teams(competition, season):
    """Get teams for a competition and season"""
    try:
        loader = DataLoader(competition)
        teams = loader.get_team_list(season)

        # Format response
        teams_list = [
            {
                "id": team.lower().replace(' ', '_'),
                "name": team
            }
            for team in teams
        ]

        return {
            "success": True,
            "competition": competition,
            "season": season,
            "teams": teams_list
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps(
            {"success": False, "error": "Usage: get_teams.py <competition> <season>"}))
        sys.exit(1)

    competition = sys.argv[1]
    season = sys.argv[2] if len(sys.argv) > 2 else "2025-2026"

    result = get_teams(competition, season)
    print(json.dumps(result))
