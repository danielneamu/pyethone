#!/bin/bash
# Results Collection - Cron Script
# Runs Saturday/Sunday/Monday nights + manual trigger

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$PROJECT_ROOT/python_api/collect_results.py"
VENV_PATH="/var/www/html/pyethone/pye_venv"  # ✅ FIXED
LOG_FILE="$PROJECT_ROOT/logs/results_collection_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

echo "========================================" | tee -a "$LOG_FILE"
echo "Results Collection Started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run collection script
python3 -u "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Results Collection Finished: $(date)" | tee -a "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
