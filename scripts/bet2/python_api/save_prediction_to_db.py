#!/usr/bin/env python3
"""
Save Prediction to Database
Called from PHP after generating prediction
"""

from services.database_service import DatabaseService
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'No data provided'}))
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])

        db = DatabaseService()
        success = db.save_prediction(data)

        if success:
            print(json.dumps({'success': True, 'message': 'Prediction saved'}))
        else:
            print(json.dumps(
                {'success': False, 'error': 'Database save failed'}))

    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
