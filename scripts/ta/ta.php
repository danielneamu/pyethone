<?php
// Replace with the actual symbol you want to pass
$symbol = "ARM";  

// Specify pyton script to run
$pythonScriptPath = "/var/www/html/pyethone/scripts/ta/ta.py";
// Specify the directory for Matplotlib configuration
$matplotlibConfigDir = "/home/danielneamu/.config/matplotlib/";


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
    echo "Error executing Python script DIN NOU. Return code: $returnCode\n";
    echo "Output: " . implode("\n", $output) . "\n";
} else {
    // Join the output array into a single string
    $jsonOutput = implode("\n", $output);

    $jsonStart =  strpos($jsonOutput, '{');

    if ($jsonStart !== false) {
        // Extract the JSON string from the output
        $jsonString = substr($jsonOutput, $jsonStart);

        // Replace "NaN" with null in the JSON string
        $jsonString = str_replace('NaN', 'null', $jsonString);

        // Decode the JSON string into a PHP associative array
        $variablesArray = json_decode($jsonString, true);

        // Access the variables as needed
        $symbol = $variablesArray['symbol'];
        $adjClose = $variablesArray['Adj_Close'];
        $macd = $variablesArray['MACD_12_26_9'];
        $macdHistogram = $variablesArray['MACD_histogram_12_26_9'];
        $rsi_14 = $variablesArray['RSI_14'];
        $bbl_5_20 = $variablesArray['BBL_5_2.0'];
        $bbm_5_20 = $variablesArray['BBM_5_2.0'];
        $bbu_5_20 = $variablesArray['BBU_5_2.0'];
        $sma_20 = $variablesArray['SMA_20'];
        $ema_20 = $variablesArray['EMA_20'];
        $obv_in_million = $variablesArray['OBV_in_million'];
        $stochk_14_3_3 = $variablesArray['STOCHk_14_3_3'];
        $stochd_14_3_3 = $variablesArray['STOCHd_14_3_3'];
        $adx_14 = $variablesArray['ADX_14'];
        $willr_14 = $variablesArray['WILLR_14'];
        $cmf_20 = $variablesArray['CMF_20'];
        $psari_002_02 = $variablesArray['PSARl_0.02_0.2'];
        $psars_002_02 = $variablesArray['PSARs_0.02_0.2'];
        // Add more variables as needed
        $plotPaths = $variablesArray['plot_paths'];  // Retrieve the plot paths


        // Use the variables as needed
        echo "Symbol: $symbol<br>";
        echo "Prediction: $prediction<br>";
        echo "Adj Close: $adjClose<br>";
        echo "MACD: $macd<br>";
        echo "MACD Histogram: $macdHistogram<br>";
        echo "RSI_14: $rsi_14<br>";
        echo "BBL_5_20: $bbl_5_20<br>";
        // Add more variable outputs as needed

        $imagePath = $plotPaths[0];
        $webRelativePath = str_replace('/var/www/html', '', $imagePath);

        echo "<img src='$webRelativePath' alt='Plot'><br>";

        echo ($variablesArray['new_prompt']);

    } else {
        echo "Error: JSON data not found in Python script output.\n";
    }

}
