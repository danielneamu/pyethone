<?php
// !Calling hello.py script using proc_open - getting back MULTIPLE variables
//*Advantages:
//      Provides more control over input and output streams
//      Allows capturing both standard output and errors.
//*Considerations:
//      Requires more code
//      Still poses security risks if not handled properly

// Set the Python input/output encoding to UTF-8
putenv("PYTHONIOENCODING=utf-8");

// Define the variable to be passed to Python
$phpVariable = "Hello from PHP!";

// Define descriptors for the pipes used in proc_open
$descriptorspec = array(
    0 => array("pipe", "r"),
    1 => array("pipe", "w"),
    2 => array("pipe", "w")
);

// Define the Python interpreter and the command to be executed
$pythonInterpreter = '/var/www/html/pyethone/pye_venv/bin/python3';
$pythonScript = 'hello2.py';
$command = "$pythonInterpreter $pythonScript \"$phpVariable\"";

// Open a process, execute the command, and create pipes for communication
$process = proc_open($command, $descriptorspec, $pipes);

// Check if the process is a resource
if (is_resource($process)) {
    // Close the stdin pipe
    fclose($pipes[0]);

    // Read the output from stdout
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);

    // Read any errors from stderr
    $errors = stream_get_contents($pipes[2]);
    fclose($pipes[2]);

    // Close the process
    proc_close($process);

    // Parse the output to extract variables
    $outputLines = explode("\n", trim($output));
    $variables = array();

    // Split each line into key-value pairs and store them in an array
    foreach ($outputLines as $line) {
        list($key, $value) = explode(": ", $line, 2);
        $variables[$key] = $value;
    }

    // Access the variables extracted from the Python script
    $variable1 = $variables['VAR1'];
    $variable2 = $variables['VAR2'];
    $variable3 = $variables['PHP_Variable'];

    echo "Variable 1: $variable1\n";
    echo "Variable 2: $variable2\n";
    echo "Variable 2: $variable3\n";
}
