<?php

// Path to the Python script
$pythonScriptPath = "ta1.py";

// Path to the virtual environment's Python interpreter
$pythonInterpreter = "/var/www/html/pyethone/pye_venv/bin/python";

// Construct the command to run the Python script within the virtual environment
$command = "$pythonInterpreter $pythonScriptPath 2>&1";

exec("/var/www/html/pyethone/pye_venv/bin/python -V", $output, $returnCode);
echo "Python version: " . implode("\n", $output) . "\n";

// Execute the command
exec($command, $output, $returnCode);

// Output the results
echo "Python script output: " . implode("\n", $output) . "\n";
echo "Python script return code: " . $returnCode . "\n";
