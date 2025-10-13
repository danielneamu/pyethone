#!/bin/bash

echo "=== Checking Apache User ==="
ps aux | grep apache2 | head -1

echo -e "\n=== Current File Ownership ==="
ls -la /var/www/html/pyethone/scripts/bet/api/predict_api.php
ls -la /var/www/html/pyethone/scripts/bet/data/teams.csv

echo -e "\n=== Fixing Permissions ==="
sudo chown -R www-data:www-data /var/www/html/pyethone/scripts/bet/
sudo chmod -R 755 /var/www/html/pyethone/scripts/bet/
sudo chmod -R 775 /var/www/html/pyethone/scripts/bet/logs/
sudo chmod -R 775 /var/www/html/pyethone/scripts/bet/models/saved_models/
sudo chmod -R 775 /var/www/html/pyethone/scripts/bet/data/processed/

echo -e "\n=== New File Ownership ==="
ls -la /var/www/html/pyethone/scripts/bet/api/predict_api.php
ls -la /var/www/html/pyethone/scripts/bet/data/teams.csv

echo -e "\n=== Testing API via CLI ==="
REQUEST_METHOD=GET QUERY_STRING="action=teams" php /var/www/html/pyethone/scripts/bet/api/predict_api.php

echo -e "\n=== Testing API via Web ==="
curl -k "https://piedone.go.ro/pyethone/scripts/bet/api/predict_api.php?action=teams"

echo -e "\n=== Checking Apache Error Log ==="
sudo tail -10 /var/log/apache2/error.log
