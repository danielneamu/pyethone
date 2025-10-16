<?php
/**
 * Predict API - Direct PHP to Python
 * Generates match predictions
 * 
 * Usage: predict_api.php?home_team=Arsenal&away_team=Chelsea&competition=premier_league
 */

header('Content-Type: application/json');

// Configuration
define('PYTHON_BIN', '/var/www/html/pyethone/pye_venv/bin/python');
define('PYTHON_SCRIPT', '/var/www/html/pyethone/scripts/bet2/python_api/predict.py');

try {
    // Get parameters
    $home_team = $_GET['home_team'] ?? '';
    $away_team = $_GET['away_team'] ?? '';
    $competition = $_GET['competition'] ?? 'premier_league';

    // Validate
    if (empty($home_team) || empty($away_team)) {
        throw new Exception('Both home_team and away_team are required');
    }

    // Build command
    $command = escapeshellcmd(PYTHON_BIN . ' ' . PYTHON_SCRIPT) . ' ' . 
               escapeshellarg($home_team) . ' ' . 
               escapeshellarg($away_team) . ' ' . 
               escapeshellarg($competition);

    // Execute with timeout (predictions can take 3-5 seconds)
    $command .= ' 2>&1';
    $output = shell_exec($command);

    if ($output === null) {
        throw new Exception('Failed to execute prediction script');
    }

    // Decode JSON
    $result = json_decode($output, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('Invalid JSON from Python: ' . $output);
    }

    // Return result
    echo json_encode($result);

} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
