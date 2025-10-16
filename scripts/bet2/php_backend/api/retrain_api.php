<?php

/**
 * Retrain API - Triggers model retraining
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Paths
$pythonApiDir = __DIR__ . '/../../python_api';
$venvPython = '/var/www/html/pyethone/pye_venv/bin/python3';

// Training scripts
$trainEnsemble = $pythonApiDir . '/train_ensemble.py';
$trainCards = $pythonApiDir . '/train_cards.py';

// Check if scripts exist
if (!file_exists($trainEnsemble) || !file_exists($trainCards)) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Training scripts not found'
    ]);
    exit;
}

// Execute training scripts in background (ensemble first, then cards)
$command = sprintf(
    '%s %s && %s %s > /dev/null 2>&1 &',
    escapeshellarg($venvPython),
    escapeshellarg($trainEnsemble),
    escapeshellarg($venvPython),
    escapeshellarg($trainCards)
);

exec($command, $output, $returnCode);

echo json_encode([
    'success' => true,
    'message' => 'Model retraining started',
    'scripts' => [
        'train_ensemble.py',
        'train_cards.py'
    ],
    'started_at' => date('Y-m-d H:i:s')
]);
