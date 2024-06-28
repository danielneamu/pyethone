<?php
// Define paths and commands
$pythonEnvPath = '/var/www/html/pyethone/pye_venv';
$pythonInterpreter = "$pythonEnvPath/bin/python3.11";
$activateScript = "$pythonEnvPath/bin/activate";
$sourceCommand = "source $activateScript && ";

// Set PYTHONPATH to include the correct site-packages directory
putenv("PYTHONPATH=$pythonEnvPath/lib/python3.11/site-packages");

// Variables to pass to the Python script
$var1 = 'value1';
$var2 = 'value2';

// Replace with the path to your Python script
$pythonScript = '/var/www/html/pyethone/scripts/phpcall2/check_yfinance.py';

// Command to run Python script with arguments
$command = "$sourceCommand $pythonInterpreter $pythonScript '$var1' '$var2' 2>&1";
echo($command);

// Execute the command
$result = shell_exec($command);

echo($var1);
// Display the result
echo "Python script output: \n" . $result . "\n";
?>