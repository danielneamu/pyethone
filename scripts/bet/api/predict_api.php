<?php
/**
 * Prediction API Endpoint
 * Handles prediction requests from the frontend
 * Calls Python prediction script and returns JSON
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Configuration
define('PYTHON_VENV', '/var/www/html/pyethone/pye_venv/bin/python');
define('PREDICT_SCRIPT', '/var/www/html/pyethone/scripts/bet/models/predict.py');
define('TEAMS_FILE', '/var/www/html/pyethone/scripts/bet/data/teams.csv');

/**
 * Load available teams from CSV
 * 
 * @return array List of teams
 */
function getTeamsList() {
    $teams = [];
    
    if (($handle = fopen(TEAMS_FILE, "r")) !== FALSE) {
        $header = fgetcsv($handle); // Skip header
        
        while (($data = fgetcsv($handle)) !== FALSE) {
            $teams[] = [
                'name' => $data[0],
                'short_name' => $data[1]
            ];
        }
        fclose($handle);
    }
    
    return $teams;
}

/**
 * Execute Python prediction script
 * 
 * @param string $homeTeam Home team name
 * @param string $awayTeam Away team name
 * @return array Prediction results
 */
function getPrediction($homeTeam, $awayTeam) {
    // Escape shell arguments for security
    $homeTeamEscaped = escapeshellarg($homeTeam);
    $awayTeamEscaped = escapeshellarg($awayTeam);
    
    // Build command
    $command = PYTHON_VENV . " " . PREDICT_SCRIPT . " " . $homeTeamEscaped . " " . $awayTeamEscaped . " 2>&1";
    
    // Execute Python script
    exec($command, $output, $returnCode);
    
    if ($returnCode !== 0) {
        return [
            'error' => true,
            'message' => 'Prediction failed: ' . implode("\n", $output)
        ];
    }
    
    // Extract JSON from output (skip print statements)
    $jsonOutput = '';
    $jsonStarted = false;
    
    foreach ($output as $line) {
        if (trim($line) === '{') {
            $jsonStarted = true;
        }
        
        if ($jsonStarted) {
            $jsonOutput .= $line;
        }
    }
    
    $predictions = json_decode($jsonOutput, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        return [
            'error' => true,
            'message' => 'Failed to parse predictions: ' . json_last_error_msg(),
            'raw_output' => implode("\n", $output)
        ];
    }
    
    return [
        'error' => false,
        'predictions' => $predictions
    ];
}

/**
 * Validate team names
 * 
 * @param string $team Team name to validate
 * @param array $validTeams List of valid teams
 * @return bool
 */
function isValidTeam($team, $validTeams) {
    foreach ($validTeams as $validTeam) {
        if ($validTeam['name'] === $team) {
            return true;
        }
    }
    return false;
}

// Route handling
$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {
    case 'GET':
        // GET request - return available teams
        $action = $_GET['action'] ?? 'teams';
        
        if ($action === 'teams') {
            echo json_encode([
                'success' => true,
                'teams' => getTeamsList()
            ]);
        } else {
            echo json_encode([
                'success' => false,
                'error' => 'Invalid action'
            ]);
        }
        break;
    
    case 'POST':
        // POST request - get predictions
        $input = json_decode(file_get_contents('php://input'), true);
        
        if (!isset($input['home_team']) || !isset($input['away_team'])) {
            echo json_encode([
                'success' => false,
                'error' => 'Missing required parameters: home_team and away_team'
            ]);
            exit;
        }
        
        $homeTeam = $input['home_team'];
        $awayTeam = $input['away_team'];
        
        // Validate teams
        $teams = getTeamsList();
        
        if (!isValidTeam($homeTeam, $teams)) {
            echo json_encode([
                'success' => false,
                'error' => 'Invalid home team: ' . $homeTeam
            ]);
            exit;
        }
        
        if (!isValidTeam($awayTeam, $teams)) {
            echo json_encode([
                'success' => false,
                'error' => 'Invalid away team: ' . $awayTeam
            ]);
            exit;
        }
        
        if ($homeTeam === $awayTeam) {
            echo json_encode([
                'success' => false,
                'error' => 'Home and away teams must be different'
            ]);
            exit;
        }
        
        // Get predictions
        $result = getPrediction($homeTeam, $awayTeam);
        
        if ($result['error']) {
            echo json_encode([
                'success' => false,
                'error' => $result['message'],
                'details' => $result['raw_output'] ?? ''
            ]);
        } else {
            echo json_encode([
                'success' => true,
                'data' => $result['predictions']
            ]);
        }
        break;
    
    default:
        echo json_encode([
            'success' => false,
            'error' => 'Method not allowed'
        ]);
        break;
}
?>
