<?php

/**
 * Competitions API - Direct PHP to Python
 * Returns available competitions
 */

header('Content-Type: application/json');

// Configuration
define('PYTHON_BIN', '/var/www/html/pyethone/pye_venv/bin/python');
define('PYTHON_SCRIPT', '/var/www/html/pyethone/scripts/bet2/python_api/get_competitions.py');

try {
    // Build command
    $command = escapeshellcmd(PYTHON_BIN . ' ' . PYTHON_SCRIPT);

    // Execute Python script
    $output = shell_exec($command . ' 2>&1');

    if ($output === null) {
        throw new Exception('Failed to execute Python script');
    }

    // Decode JSON from Python
    $result = json_decode($output, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('Invalid JSON from Python: ' . json_last_error_msg());
    }

    // Return result
    echo json_encode($result);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
