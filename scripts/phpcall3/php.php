<?php
$command = '/var/www/html/pyethone/pye_venv/bin/python /var/www/html/pyethone/scripts/phpcall3/python.py 2>&1';
$output = shell_exec($command);

if ($output === null) {
    echo "Error executing the command. Last PHP error: " . error_get_last()['message'] . "\n";
} else {
    echo "Raw output:\n$output\n";

    $venv_info = json_decode($output, true);
    if ($venv_info === null) {
        echo "Error decoding JSON.\n";
    } else {
        echo "Virtual Environment Path: " . ($venv_info['venv_path'] ?? 'Not available') . "\n";
        echo "Virtual Environment Name: " . ($venv_info['venv_name'] ?? 'Not available') . "\n";
        echo "Python Version: " . ($venv_info['python_version'] ?? 'Not available') . "\n";
        echo "YFinance Installed: " . ($venv_info['yfinance_installed'] ? 'Yes' : 'No') . "\n";
        echo "YFinance Version: " . ($venv_info['yfinance_version'] ?? 'Not available') . "\n";
    }
}
