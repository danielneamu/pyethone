<?php

// Set MPLCONFIGDIR to a writable directory
$mplConfigDir = '/var/www/html/pyethone/matplotlib_cache';
putenv("MPLCONFIGDIR=$mplConfigDir");

// Ensure the MPLCONFIGDIR directory exists
if (!file_exists($mplConfigDir)) {
    mkdir($mplConfigDir, 0777, true);
}


// Get ticker, start_date, and end_date from URL parameters or use default values
$ticker = isset($_GET['ticker']) ? $_GET['ticker'] : 'RNG';
$start_date = isset($_GET['start_date']) ? $_GET['start_date'] : '2024-01-01';
$end_date = isset($_GET['end_date']) ? $_GET['end_date'] : '2024-06-28';

$command = "/var/www/html/pyethone/pye_venv/bin/python /var/www/html/pyethone/scripts/stocks/ta2/stock_analyzer.py $ticker $start_date $end_date 2>&1";


// Execute the command
$result = shell_exec($command);

// Display the result for debugging
echo "<pre>$result</pre>";

// Display the generated image
$imagePath = 'stock_analysis.png';
if (file_exists($imagePath)) {
    echo "<img src='$imagePath' alt='Stock Analysis'>";
} else {
    echo "Image not found.";
}
