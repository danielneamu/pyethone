#!/usr/bin/env python3
"""
Database Initialization Script
Creates SQLite schema for prediction tracking
"""

import sqlite3
from pathlib import Path
import sys

# Set up paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = SCRIPT_DIR / "predictions.db"


def init_database():
    """Initialize SQLite database with schema"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. PREDICTIONS TABLE - Store all predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            competition TEXT DEFAULT 'premierleague',
            model_type TEXT DEFAULT 'ensemble',
            
            -- Match Result (1X2)
            prediction_1x2 TEXT,
            prob_home REAL,
            prob_draw REAL,
            prob_away REAL,
            certainty_1x2 REAL,
            
            -- Double Chance
            prob_home_draw REAL,
            prob_home_away REAL,
            prob_draw_away REAL,
            
            -- Goals Over/Under
            prediction_goals_05 TEXT,
            prob_over_05 REAL,
            certainty_goals_05 REAL,
            
            prediction_goals_15 TEXT,
            prob_over_15 REAL,
            certainty_goals_15 REAL,
            
            prediction_goals_25 TEXT,
            prob_over_25 REAL,
            certainty_goals_25 REAL,
            
            prediction_goals_35 TEXT,
            prob_over_35 REAL,
            certainty_goals_35 REAL,
            
            -- BTTS
            prediction_btts TEXT,
            prob_btts_yes REAL,
            certainty_btts REAL,
            
            -- Cards
            prediction_cards_35 TEXT,
            prob_cards_over_35 REAL,
            certainty_cards_35 REAL,
            
            prediction_cards_45 TEXT,
            prob_cards_over_45 REAL,
            certainty_cards_45 REAL,
            
            -- Metadata
            prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            match_date DATE,
            is_matched BOOLEAN DEFAULT 0,
            
            UNIQUE(home_team, away_team, match_date)
        )
    """)

    # 2. ACTUAL RESULTS TABLE - Store match outcomes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actual_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            
            -- Match Result
            actual_result TEXT,
            goals_home INTEGER,
            goals_away INTEGER,
            total_goals INTEGER,
            
            -- BTTS
            btts_actual TEXT,
            
            -- Cards
            cards_home INTEGER,
            cards_away INTEGER,
            total_cards INTEGER,
            
            -- Metadata
            match_date DATE,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (match_id) REFERENCES predictions(match_id)
        )
    """)

    # 3. ACCURACY METRICS TABLE - Aggregated performance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accuracy_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_type TEXT NOT NULL,
            market TEXT NOT NULL,
            model_type TEXT,
            
            -- Accuracy Stats
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            accuracy_pct REAL,
            
            -- Brier Score (PRIMARY METRIC)
            brier_score REAL,
            
            -- Secondary Metrics
            f1_score REAL,
            roc_auc REAL,
            precision_score REAL,
            recall_score REAL,
            
            -- ROI Tracking
            total_roi_pct REAL,
            
            -- Filters
            certainty_level TEXT,
            team_name TEXT,
            
            -- Metadata
            calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            calculation_period TEXT,
            
            UNIQUE(metric_type, market, model_type, certainty_level, team_name, calculation_period)
        )
    """)

    # 4. BETTING RECOMMENDATIONS TABLE - Market performance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_name TEXT UNIQUE NOT NULL,
            
            -- Performance
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            accuracy_pct REAL,
            brier_score REAL,
            roi_pct REAL,
            
            -- Recommendation
            is_recommended BOOLEAN DEFAULT 0,
            confidence_threshold REAL,
            
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for faster queries
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_predictions_teams ON predictions(home_team, away_team)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_results_date ON actual_results(match_date)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_metrics_market ON accuracy_metrics(market, model_type)")

    conn.commit()
    conn.close()

    print(f"✅ Database initialized: {DB_PATH}")
    print(f"📊 Tables created: predictions, actual_results, accuracy_metrics, market_performance")


if __name__ == "__main__":
    init_database()
