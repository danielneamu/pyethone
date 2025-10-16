#!/bin/bash

# Backup Script for Football Prediction App - Session Handoff
# Creates backup copies with .txt extension for easy viewing

BACKUP_DIR="/var/www/html/pyethone/scripts/bet2/backup"
PROJECT_ROOT="/var/www/html/pyethone/scripts/bet2"

echo "=========================================="
echo "Football Prediction App - Backup for Next Session"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT" || exit 1

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to copy file and add .txt
copy_with_txt() {
    local src="$1"
    local dest="$BACKUP_DIR/$(basename "$src").txt"
    
    if [ -f "$src" ]; then
        cp "$src" "$dest"
        echo "✓ Copied: $src"
    else
        echo "✗ Missing: $src"
    fi
}

echo "Configuration & Data Files..."
copy_with_txt "data/competitions.csv"
copy_with_txt "data/notes.csv"
copy_with_txt "data/premier_league/2023-2024_all_teams.csv"
copy_with_txt "data/premier_league/2024-2025_all_teams.csv"
copy_with_txt "data/premier_league/2025-2026_all_teams.csv"

echo ""
echo "Python API - Core Scripts..."
copy_with_txt "python_api/__init__.py"
copy_with_txt "python_api/config.py"
copy_with_txt "python_api/requirements.txt"
copy_with_txt "python_api/predict.py"
copy_with_txt "python_api/train_ensemble.py"
copy_with_txt "python_api/train_cards.py"
copy_with_txt "python_api/get_teams.py"
copy_with_txt "python_api/get_competitions.py"

echo ""
echo "Python Services (Core Logic)..."
copy_with_txt "python_api/services/__init__.py"
copy_with_txt "python_api/services/predictor.py"
copy_with_txt "python_api/services/feature_engineering.py"
copy_with_txt "python_api/services/model_manager.py"
copy_with_txt "python_api/services/model_trainer.py"
copy_with_txt "python_api/services/data_loader.py"
copy_with_txt "python_api/services/confidence_calculator.py"
copy_with_txt "python_api/services/metrics_tracker.py"

echo ""
echo "Python Utils..."
copy_with_txt "python_api/utils/__init__.py"
copy_with_txt "python_api/utils/helpers.py"
copy_with_txt "python_api/utils/logging_config.py"
copy_with_txt "python_api/utils/validation.py"
copy_with_txt "python_api/utils/date_helpers.py"

echo ""
echo "PHP Backend..."
copy_with_txt "php_backend/config.php"
copy_with_txt "php_backend/api/predict_api.php"
copy_with_txt "php_backend/api/teams_api.php"
copy_with_txt "php_backend/api/competitions_api.php"
copy_with_txt "php_backend/utils/Logger.php"
copy_with_txt "php_backend/utils/Validator.php"

echo ""
echo "Frontend (GUI)..."
copy_with_txt "public/index.php"
copy_with_txt "public/css/custom.css"
copy_with_txt "public/js/app.js"

echo ""
echo "Automation Scripts..."
copy_with_txt "bash/update_data.sh"
copy_with_txt "bash/update_premier_league_data.py"

echo ""
echo "=========================================="
echo "Backup Complete!"
echo "=========================================="
echo "Files saved to: $BACKUP_DIR"
echo ""
echo "File count:"
ls -1 "$BACKUP_DIR" | wc -l
echo ""
echo "Total size:"
du -sh "$BACKUP_DIR"
echo ""
echo "Create archive? (y/n)"
read -r create_archive

if [[ "$create_archive" == "y" || "$create_archive" == "Y" ]]; then
    ARCHIVE_NAME="bet2_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "/var/www/html/pyethone/scripts/$ARCHIVE_NAME" -C "$BACKUP_DIR" .
    echo "✓ Archive created: /var/www/html/pyethone/scripts/$ARCHIVE_NAME"
fi

echo ""
echo "Next session: Upload files from $BACKUP_DIR to continue!"
