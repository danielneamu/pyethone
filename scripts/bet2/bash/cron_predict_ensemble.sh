#!/bin/bash
# Cron script for Ensemble predictions (DEFAULT - best accuracy)
cd /var/www/html/pyethone/scripts/bet2/python_api
source ../../pye_venv/bin/activate
python predict.py "$1" "$2" "premier_league" "ensemble"
