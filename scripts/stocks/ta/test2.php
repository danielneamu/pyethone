<?php
// Set the path to the Python executable
$python_path = '/var/www/html/pyethone/pye_venv/bin/python';

// Set the path to the Python script
$python_script = '/var/www/html/pyethone/scripts/stock_price.py';

// Set the number to pass to the Python script
$number = 100;

// Run the Python script and capture the output
$output = exec($python_path . ' ' . $python_script . ' ' . $number, $output_array, $return_value);

// Check for errors
if ($return_value != 0) {
    error_log("Error running Python script: " . $output);
    echo "Error adding 1 to the number. Please check the logs.";
} else {
    // Print the result
    echo "The number plus 1 is: " . $output;
}
