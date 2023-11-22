<?php

function runPythonScript($symbol)
{
    // Specify python script to run
    $pythonScriptPath = "/var/www/html/pyethone/scripts/ta/ta.py";
    // Specify the directory for Matplotlib configuration
    $matplotlibConfigDir = "/home/danielneamu/.config/matplotlib/matplotlib_config";

    // Create the directory if it doesn't exist
    if (!file_exists($matplotlibConfigDir)) {
        mkdir($matplotlibConfigDir, 0777, true);
    }

    // Set the MPLCONFIGDIR environment variable
    putenv("MPLCONFIGDIR=$matplotlibConfigDir");

    // Execute the Python script and capture output and errors
    exec("/var/www/html/pyethone/pye_venv/bin/python $pythonScriptPath $symbol 2>&1", $output, $returnCode);

    // Check for errors
    if ($returnCode !== 0) {
        // Print the output and error details
        echo "Error executing Python script. Return code: $returnCode\n";
        echo "Output: " . implode("\n", $output) . "\n";
        return null; // or handle the error in a different way
    } else {
        // Join the output array into a single string
        $jsonOutput = implode("\n", $output);

        $jsonStart = strpos($jsonOutput, '{');

        if ($jsonStart !== false) {
            // Extract the JSON string from the output
            $jsonString = substr($jsonOutput, $jsonStart);

            // Replace "NaN" with null in the JSON string
            $jsonString = str_replace('NaN', 'null', $jsonString);

            // Decode the JSON string into a PHP associative array
            $variablesArray = json_decode($jsonString, true);

            return $variablesArray;
        } else {
            echo "Error: JSON data not found in Python script output.\n";
            return null; // or handle the error in a different way
        }
    }
}
