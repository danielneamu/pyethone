<?php
// !Calling hello.py script using shell_exec - getting back ONE variable
//*Advantages:
//      Simple and easy to implement.
//      Suitable for basic use cases.
//*Considerations:
//      Potential security risks, especially if user inputs are involved.
//      Limited control over the execution environment.

// Define the path to the python interpreter (in this case inside venv: pye_venv)
$pythonInterpreter = '/var/www/html/pyethone/pye_venv/bin/python3';

// Define the stock symboll
$symbol = 'AMZN';

// Replace with the actual absolute path to your Python script
$pythonScriptPath = 'hello.py';

// Build the command
//$command = "$pythonInterpreter $pythonScriptPath $symbol 2>&1";
$command = "$pythonInterpreter $pythonScriptPath";
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
