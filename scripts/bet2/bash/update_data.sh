#!/bin/bash
# Premier League Data Update Script
# Run this every 2 days via cron to keep data fresh

# Set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/update_premier_league_data.py"
VENV_PATH="/var/www/html/pyethone/pye_venv"
LOG_FILE="$PROJECT_ROOT/logs/data_update_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory if doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the Python script with logging
echo "========================================" | tee -a "$LOG_FILE"
echo "Data Update Started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

python3  -u "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Data Update Finished: $(date)" | tee -a "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
