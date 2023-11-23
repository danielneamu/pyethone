<?php

$output = null;
$returnCode = null;

// Execute the Python script
exec('/var/www/html/pyethone/pye_venv/bin/python your_script.py', $output, $returnCode);

if ($returnCode === 0) {
    // Execution was successful
    echo json_encode(['success' => true, 'output' => $output]);
} else {
    // Execution failed
    echo json_encode(['success' => false, 'error' => 'Failed to run Python script']);
}
