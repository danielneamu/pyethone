<?php
// !Calling hello.py script using proc_open - getting back MULTIPLE variables
//*Advantages:
//      Provides more control over input and output streams
//      Allows capturing both standard output and errors.
//*Considerations:
//      Requires more code
//      Still poses security risks if not handled properly


putenv("PYTHONIOENCODING=utf-8");

$descriptorspec = array(
    0 => array("pipe", "r"),
    1 => array("pipe", "w"),
    2 => array("pipe", "w")
);

$pythonInterpreter = '/var/www/html/pyethone/pye_venv/bin/python3';
$command = "$pythonInterpreter hello.py";
$process = proc_open($command, $descriptorspec, $pipes);

if (is_resource($process)) {
    fclose($pipes[0]);
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $errors = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    proc_close($process);

    // Parse the output to extract variables
    $outputLines = explode("\n", trim($output));
    $variables = array();

    foreach ($outputLines as $line) {
        list($key, $value) = explode(": ", $line, 2);
        $variables[$key] = $value;
    }

    // Access the variables
    $variable1 = $variables['VAR1'];
    $variable2 = $variables['VAR2'];

    echo "Variable 1: $variable1\n";
    echo "Variable 2: $variable2\n";
}
