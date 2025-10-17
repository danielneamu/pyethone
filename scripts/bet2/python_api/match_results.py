#!/usr/bin/env python3
"""
Auto-match predictions with actual results from CSV data
Run this after data scraping to update prediction accuracy
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import json

def match_results():
    """Match predictions with actual results from CSV data"""
    
    script_dir = Path(__file__).parent
    db_path = script_dir / 'database' / 'predictions.db'
    data_dir = script_dir.parent / 'data' / 'premier_league'
    
    print("=" * 70)
    print("🔍 AUTO-MATCHING PREDICTIONS WITH ACTUAL RESULTS")
    print("=" * 70)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get unmatched predictions with match_date set
    cursor.execute("""
        SELECT id, home_team, away_team, match_date, competition,
               prediction_1x2, prediction_goals_05, prediction_goals_15, 
               prediction_goals_25, prediction_goals_35,
               prediction_btts, prediction_cards_25, prediction_cards_35, prediction_cards_45
        FROM predictions 
        WHERE is_matched = 0 AND match_date IS NOT NULL
    """)
    
    predictions = cursor.fetchall()
    print(f"\n📊 Found {len(predictions)} unmatched predictions with match dates set")
    
    if len(predictions) == 0:
        print("✅ No predictions to match. All done!")
        conn.close()
        return {'success': True, 'matched': 0, 'message': 'No predictions to match'}
    
    matched_count = 0
    errors = []
    
    for pred in predictions:
        (pred_id, home, away, match_date, comp, 
         pred_1x2, pred_g05, pred_g15, pred_g25, pred_g35,
         pred_btts, pred_c25, pred_c35, pred_c45) = pred
        
        # Determine season from match_date
        match_year = int(match_date.split('-')[0])
        if match_year >= 2025:
            season = '2025-2026'
        elif match_year >= 2024:
            season = '2024-2025'
        else:
            season = '2023-2024'
        
        csv_file = data_dir / f'{season}_all_teams.csv'
        
        if not csv_file.exists():
            errors.append(f"CSV file not found for {season}")
            continue
        
        # Load CSV data
        df = pd.read_csv(csv_file)
        
        # Match by date and teams (home team perspective)
        match_rows = df[
            (df['team_name'] == home) &
            (df['opponent'] == away) &
            (df['date'] == match_date)
        ]
        
        if match_rows.empty:
            print(f"⚠️  No match found for {home} vs {away} on {match_date}")
            continue
        
        # Extract actual results
        match_data = match_rows.iloc[0]
        
        # Determine actual result (from home team perspective)
        result = match_data['result']  # 'W', 'D', 'L'
        if result == 'W':
            actual_result = 'Home Win'
        elif result == 'D':
            actual_result = 'Draw'
        else:  # 'L'
            actual_result = 'Away Win'
        
        # Calculate actual stats
        goals_for = int(match_data['goals_for'])
        goals_against = int(match_data['goals_against'])
        actual_goals = goals_for + goals_against
        actual_btts = 1 if (goals_for > 0 and goals_against > 0) else 0
        
        # Cards (yellow + red cards)
        cards_for = int(match_data.get('cards_yellow', 0)) + int(match_data.get('cards_red', 0))
        cards_against_row = df[
            (df['team_name'] == away) &
            (df['opponent'] == home) &
            (df['date'] == match_date)
        ]
        if not cards_against_row.empty:
            cards_against = int(cards_against_row.iloc[0].get('cards_yellow', 0)) + int(cards_against_row.iloc[0].get('cards_red', 0))
        else:
            cards_against = 0
        
        actual_cards = cards_for + cards_against
        
        # Calculate correctness for each prediction
        correct_1x2 = 1 if pred_1x2 == actual_result else 0
        correct_g05 = 1 if (pred_g05 == 'Over' and actual_goals > 0.5) or (pred_g05 == 'Under' and actual_goals <= 0.5) else 0
        correct_g15 = 1 if (pred_g15 == 'Over' and actual_goals > 1.5) or (pred_g15 == 'Under' and actual_goals <= 1.5) else 0
        correct_g25 = 1 if (pred_g25 == 'Over' and actual_goals > 2.5) or (pred_g25 == 'Under' and actual_goals <= 2.5) else 0
        correct_g35 = 1 if (pred_g35 == 'Over' and actual_goals > 3.5) or (pred_g35 == 'Under' and actual_goals <= 3.5) else 0
        correct_btts = 1 if (pred_btts == 'Yes' and actual_btts == 1) or (pred_btts == 'No' and actual_btts == 0) else 0
        correct_c25 = 1 if (pred_c25 == 'Over' and actual_cards > 2.5) or (pred_c25 == 'Under' and actual_cards <= 2.5) else 0
        correct_c35 = 1 if (pred_c35 == 'Over' and actual_cards > 3.5) or (pred_c35 == 'Under' and actual_cards <= 3.5) else 0
        correct_c45 = 1 if (pred_c45 == 'Over' and actual_cards > 4.5) or (pred_c45 == 'Under' and actual_cards <= 4.5) else 0
        
        # Update database
        cursor.execute("""
            UPDATE predictions SET
                actual_result = ?,
                actual_goals = ?,
                actual_btts = ?,
                actual_cards = ?,
                correct_1x2 = ?,
                correct_goals_05 = ?,
                correct_goals_15 = ?,
                correct_goals_25 = ?,
                correct_goals_35 = ?,
                correct_btts = ?,
                correct_cards_25 = ?,
                correct_cards_35 = ?,
                correct_cards_45 = ?,
                is_matched = 1,
                matched_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (actual_result, actual_goals, actual_btts, actual_cards,
              correct_1x2, correct_g05, correct_g15, correct_g25, correct_g35,
              correct_btts, correct_c25, correct_c35, correct_c45, pred_id))
        
        matched_count += 1
        status = "✅" if correct_1x2 else "❌"
        print(f"{status} {home} vs {away} ({match_date}) - Predicted: {pred_1x2}, Actual: {actual_result}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✅ MATCHED {matched_count} PREDICTIONS")
    print("=" * 70)
    
    return {
        'success': True, 
        'matched': matched_count,
        'errors': errors if errors else None
    }

if __name__ == '__main__':
    result = match_results()
    print(json.dumps(result, indent=2))
