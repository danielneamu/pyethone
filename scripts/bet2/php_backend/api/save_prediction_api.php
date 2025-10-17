<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid JSON']);
    exit;
}

// Call Python save script directly
try {
    $pythonSaveScript = __DIR__ . '/../../python_api/save_prediction_to_db.py';

    if (!file_exists($pythonSaveScript)) {
        throw new Exception('Save script not found');
    }

    $jsonData = escapeshellarg(json_encode($data));
    $venvPython = '/var/www/html/pyethone/pye_venv/bin/python3';
    $logFile = __DIR__ . '/../../python_api/logs/save_errors.log';

    // Run synchronously to get immediate feedback
    $command = "$venvPython $pythonSaveScript $jsonData 2>&1";
    $output = shell_exec($command);
    $result = json_decode($output, true);

    if ($result && isset($result['success']) && $result['success']) {
        echo json_encode(['success' => true, 'message' => 'Prediction saved']);
    } else {
        echo json_encode(['success' => false, 'error' => 'Save failed', 'details' => $output]);
    }
} catch (Exception $e) {
    error_log("Save error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
