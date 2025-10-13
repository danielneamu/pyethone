<?php

/**
 * Model Retraining API
 * Triggers model retraining process
 * Should be called after new match data is added
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Configuration
define('PYTHON_VENV', '/var/www/html/pyethone/pye_venv/bin/python');
define('FEATURE_SCRIPT', '/var/www/html/pyethone/scripts/bet/models/feature_engineering.py');
define('TRAIN_SCRIPT', '/var/www/html/pyethone/scripts/bet/models/train_models.py');
define('LOG_FILE', '/var/www/html/pyethone/scripts/bet/logs/retraining.log');

/**
 * Log retraining activity
 * 
 * @param string $message Log message
 */
function logMessage($message)
{
    $timestamp = date('Y-m-d H:i:s');
    $logEntry = "[{$timestamp}] {$message}\n";
    file_put_contents(LOG_FILE, $logEntry, FILE_APPEND);
}

/**
 * Execute retraining process
 * 
 * @return array Result with success status and messages
 */
function retrainModels()
{
    $output = [];
    $errors = [];

    logMessage("Retraining initiated");

    // Step 1: Generate features
    logMessage("Step 1: Generating features");
    $featureCommand = PYTHON_VENV . " " . FEATURE_SCRIPT . " 2>&1";
    exec($featureCommand, $featureOutput, $featureReturn);

    if ($featureReturn !== 0) {
        $error = "Feature generation failed: " . implode("\n", $featureOutput);
        logMessage("ERROR: " . $error);
        return [
            'success' => false,
            'error' => $error,
            'stage' => 'feature_generation'
        ];
    }

    $output['feature_generation'] = implode("\n", $featureOutput);
    logMessage("Features generated successfully");

    // Step 2: Train models
    logMessage("Step 2: Training models");
    $trainCommand = PYTHON_VENV . " " . TRAIN_SCRIPT . " 2>&1";
    exec($trainCommand, $trainOutput, $trainReturn);

    if ($trainReturn !== 0) {
        $error = "Model training failed: " . implode("\n", $trainOutput);
        logMessage("ERROR: " . $error);
        return [
            'success' => false,
            'error' => $error,
            'stage' => 'model_training'
        ];
    }

    $output['model_training'] = implode("\n", $trainOutput);
    logMessage("Models trained successfully");

    logMessage("Retraining completed successfully");

    return [
        'success' => true,
        'message' => 'Models retrained successfully',
        'timestamp' => date('Y-m-d H:i:s'),
        'output' => $output
    ];
}

/**
 * Get last retraining info
 * 
 * @return array Info about last retraining
 */
function getRetrainingInfo()
{
    if (!file_exists(LOG_FILE)) {
        return [
            'last_retrain' => 'Never',
            'status' => 'No training history'
        ];
    }

    $lines = file(LOG_FILE);
    $lastLine = end($lines);

    return [
        'last_retrain' => date('Y-m-d H:i:s', filemtime(LOG_FILE)),
        'last_log_entry' => trim($lastLine)
    ];
}

// Route handling
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    // Trigger retraining
    $input = json_decode(file_get_contents('php://input'), true);
    $action = $input['action'] ?? 'retrain';

    if ($action === 'retrain') {
        // Execute retraining (this may take several minutes)
        set_time_limit(600); // 10 minutes max

        $result = retrainModels();
        echo json_encode($result);
    } else {
        echo json_encode([
            'success' => false,
            'error' => 'Invalid action'
        ]);
    }
} elseif ($method === 'GET') {
    // Get retraining info
    echo json_encode([
        'success' => true,
        'info' => getRetrainingInfo()
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Method not allowed'
    ]);
}
