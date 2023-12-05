<?php
// !Calling hello.py script using proc_open - getting back ONE variable
//*Advantages:
//      Provides more control over input and output streams
//      Allows capturing both standard output and errors.
//*Considerations:
//      Requires more code
//      Still poses security risks if not handled properly

$descriptorspec = array(
    0 => array("pipe", "r"),
    1 => array("pipe", "w"),
    2 => array("pipe", "w")
);

$command = 'python3 hello.py';
$process = proc_open($command, $descriptorspec, $pipes);

if (is_resource($process)) {
    fclose($pipes[0]);
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $errors = stream_get_contents($pipes[2]);  // Capture errors
    fclose($pipes[2]);
    proc_close($process);

    echo "Output: $output\n";

}
?>
