<?php
// Define the path to the python interpreter (in this case inside venv: pye_venv)
$pythonInterpreter = '/var/www/html/pyethone/pye_venv/bin/python3';

// Define the stock symboll
$symbol = 'AMZN';

// Replace with the actual absolute path to your Python script
$pythonScriptPath = 'hello.py';
$var = "lumeeee";

// Build the command
//$command = "$pythonInterpreter $pythonScriptPath $symbol 2>&1";
$command = "$pythonInterpreter $pythonScriptPath $var";
// Execute the command
$result = shell_exec($command);

// Check for errors
if ($result === null) {
    // Handle execution error
    echo "Error executing the command.";
} else {
    // Display the result
    echo $result;
}
