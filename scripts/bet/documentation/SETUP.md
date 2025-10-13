# Football Prediction System - Setup Guide

## Prerequisites

- Python 3.8+ with virtual environment at `/var/www/html/pyethone/pye_venv`
- Apache/Nginx web server with PHP 7.4+
- MySQL (optional, for future enhancements)
- Terminal access for setup

## Installation Steps

### 1. Verify Directory Structure

cd /var/www/html/pyethone/scripts/bet/

text

Ensure the following structure exists:

bet/
├── data/
├── models/
├── api/
├── gui/
├── config/
├── logs/
└── documentation/

text

### 2. Install Python Dependencies

Activate virtual environment and install required packages:

source /var/www/html/pyethone/pye_venv/bin/activate
pip install pandas numpy scikit-learn xgboost


### 3. Set File Permissions

Make scripts executable
chmod +x models/*.py

Set write permissions for logs and processed data
chmod 777 logs/
chmod 777 data/processed/
chmod 777 models/saved_models/


### 4. Initial Data Preparation

Run feature engineering:

source /var/www/html/pyethone/pye_venv/bin/activate
python models/feature_engineering.py

Expected output: `Features saved to: /var/www/html/pyethone/scripts/bet/data/processed/features.csv`

### 5. Train Initial Models

python models/train_models.py

This will take 5-10 minutes. Expected output shows training progress for all 12 models.

### 6. Configure Web Server

#### Apache Configuration

Add to your Apache config or `.htaccess`:

<Directory "/var/www/html/pyethone/scripts/bet/gui">
Options Indexes FollowSymLinks
AllowOverride All
Require all granted
</Directory>

<Directory "/var/www/html/pyethone/scripts/bet/api">
Options None
AllowOverride None
Require all granted
</Directory>

Restart Apache:

sudo systemctl restart apache2


### 7. Test Installation

#### Test Python Prediction:

source /var/www/html/pyethone/pye_venv/bin/activate
python models/predict.py Liverpool Arsenal

Should output JSON predictions.

#### Test PHP API:

curl "http://localhost/pyethone/scripts/bet/api/predict_api.php?action=teams"

Should return JSON with team list.

### 8. Access GUI

Open browser and navigate to:

http://localhost/pyethone/scripts/bet/gui/index.html


## Troubleshooting

### Python Module Not Found

source /var/www/html/pyethone/pye_venv/bin/activate
pip list # Verify installed packages


### PHP Cannot Execute Python

Check `predict_api.php` line 12:
define('PYTHON_VENV', '/var/www/html/pyethone/pye_venv/bin/python');


Verify path exists:
ls -la /var/www/html/pyethone/pye_venv/bin/python


### Permission Denied Errors

chmod -R 755 /var/www/html/pyethone/scripts/bet/
chmod 777 /var/www/html/pyethone/scripts/bet/logs/
chmod 777 /var/www/html/pyethone/scripts/bet/data/processed/
chmod 777 /var/www/html/pyethone/scripts/bet/models/saved_models/


### Models Not Loading

Check if model files exist:
ls -la /var/www/html/pyethone/scripts/bet/models/saved_models/


Should show 13 `.pkl` files.

## Post-Installation

1. **Add New Match Data**: Update `E0_1926_consolidated.csv` with new match results
2. **Retrain Models**: Use GUI "Retrain Models" button or run:
python models/feature_engineering.py && python models/train_models.py

3. **Monitor Logs**: Check `logs/training_logs.txt` for training history

## Security Recommendations

1. **Restrict API Access**: Add authentication to `retrain_api.php`
2. **Input Validation**: Already implemented in PHP
3. **Rate Limiting**: Add request throttling for production
4. **HTTPS**: Use SSL certificate for production deployment

## Next Steps

- Read `USAGE.md` for user guide
- Read `API.md` for API documentation
- Test with different team matchups