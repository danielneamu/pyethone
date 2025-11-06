#!/usr/bin/env python3
"""
Fix Database Schema - Add missing columns to predictions table
"""

import sqlite3
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent / "database" / "predictions.db"


def fix_schema():
    """Add missing columns to predictions table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("total_goals", "INTEGER"),
        ("btts_actual", "INTEGER"),
        ("total_cards", "INTEGER"),
        ("actual_result", "TEXT")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(
                f"ALTER TABLE predictions ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"ℹ️  Column already exists: {col_name}")
            else:
                print(f"❌ Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("\n✅ Schema fix complete!")


if __name__ == "__main__":
    fix_schema()
