<?php

/**
 * Update Data API - Triggers data scraping
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Path to update script
$updateScript = __DIR__ . '/../../bash/update_data.sh';

// Check if script exists
if (!file_exists($updateScript)) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Update script not found'
    ]);
    exit;
}

// Execute update script in background
$command = sprintf('bash %s > /dev/null 2>&1 &', escapeshellarg($updateScript));
exec($command, $output, $returnCode);

// Log file to check progress
$logDir = __DIR__ . '/../../logs';
$latestLog = null;
if (is_dir($logDir)) {
    $logFiles = glob($logDir . '/data_update_*.log');
    if (!empty($logFiles)) {
        usort($logFiles, function ($a, $b) {
            return filemtime($b) - filemtime($a);
        });
        $latestLog = basename($logFiles[0]);
    }
}

echo json_encode([
    'success' => true,
    'message' => 'Data update started',
    'log_file' => $latestLog,
    'started_at' => date('Y-m-d H:i:s')
]);
