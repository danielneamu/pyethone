<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'list_predictions':
        listSavedPredictions();
        break;
    case 'stats':
        getPredictionStats();
        break;
    case 'delete_prediction':
        deletePrediction();
        break;
    case 'update_match_date':
        updateMatchDate();
        break;
    case 'accuracy_stats':
        getAccuracyStats();
        break;
    default:
        echo json_encode(['error' => 'Invalid action']);
}

function listSavedPredictions()
{
    $dbPath = __DIR__ . '/../../python_api/database/predictions.db';

    if (!file_exists($dbPath)) {
        echo json_encode(['error' => 'Database not found']);
        return;
    }

    try {
        $db = new SQLite3($dbPath);
        $limit = $_GET['limit'] ?? 50;
        $offset = $_GET['offset'] ?? 0;

        $query = "SELECT  * FROM predictions 
                  ORDER BY prediction_date DESC 
                  LIMIT :limit OFFSET :offset";

        $stmt = $db->prepare($query);
        $stmt->bindValue(':limit', (int)$limit, SQLITE3_INTEGER);
        $stmt->bindValue(':offset', (int)$offset, SQLITE3_INTEGER);

        $result = $stmt->execute();
        $predictions = [];

        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $predictions[] = $row;
        }

        // Get total count
        $countResult = $db->query("SELECT COUNT(*) as total FROM predictions");
        $total = $countResult->fetchArray(SQLITE3_ASSOC)['total'];

        echo json_encode([
            'success' => true,
            'predictions' => $predictions,
            'total' => $total,
            'limit' => $limit,
            'offset' => $offset
        ]);

        $db->close();
    } catch (Exception $e) {
        echo json_encode(['error' => $e->getMessage()]);
    }
}

function getPredictionStats()
{
    $dbPath = __DIR__ . '/../../python_api/database/predictions.db';

    try {
        $db = new SQLite3($dbPath);

        $stats = [
            'total_predictions' => 0,
            'by_model' => [],
            'by_competition' => [],
            'matched_count' => 0,
            'by_certainty' => [
                'high' => 0,
                'medium' => 0,
                'low' => 0
            ]
        ];

        // Total predictions
        $result = $db->query("SELECT COUNT(*) as total FROM predictions");
        $stats['total_predictions'] = $result->fetchArray(SQLITE3_ASSOC)['total'];

        // By model type
        $result = $db->query("SELECT model_type, COUNT(*) as count FROM predictions GROUP BY model_type");
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $stats['by_model'][$row['model_type']] = $row['count'];
        }

        // By competition
        $result = $db->query("SELECT competition, COUNT(*) as count FROM predictions GROUP BY competition");
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $stats['by_competition'][$row['competition']] = $row['count'];
        }

        // Matched predictions
        $result = $db->query("SELECT COUNT(*) as matched FROM predictions WHERE is_matched = 1");
        $stats['matched_count'] = $result->fetchArray(SQLITE3_ASSOC)['matched'];

        // By certainty level
        $result = $db->query("
            SELECT 
                CASE 
                    WHEN certainty_1x2 >= 0.7 THEN 'high'
                    WHEN certainty_1x2 >= 0.4 THEN 'medium'
                    ELSE 'low'
                END as certainty_level,
                COUNT(*) as count
            FROM predictions 
            GROUP BY certainty_level
        ");
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $stats['by_certainty'][$row['certainty_level']] = $row['count'];
        }

        echo json_encode(['success' => true, 'stats' => $stats]);

        $db->close();
    } catch (Exception $e) {
        echo json_encode(['error' => $e->getMessage()]);
    }
}

function deletePrediction()
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        echo json_encode(['error' => 'Method not allowed']);
        return;
    }

    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $id = $data['id'] ?? null;

    if (!$id) {
        echo json_encode(['error' => 'Missing prediction ID']);
        return;
    }

    $dbPath = __DIR__ . '/../../python_api/database/predictions.db';

    try {
        $db = new SQLite3($dbPath);
        $stmt = $db->prepare("DELETE FROM predictions WHERE id = :id");
        $stmt->bindValue(':id', $id, SQLITE3_INTEGER);
        $stmt->execute();

        echo json_encode(['success' => true, 'message' => 'Prediction deleted']);
        $db->close();
    } catch (Exception $e) {
        echo json_encode(['error' => $e->getMessage()]);
    }
}

function updateMatchDate()
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        echo json_encode(['success' => false, 'error' => 'Method not allowed']);
        return;
    }

    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    $id = $data['id'] ?? null;
    $matchDate = $data['match_date'] ?? null;

    if (!$id) {
        echo json_encode(['success' => false, 'error' => 'Missing prediction ID']);
        return;
    }

    $dbPath = __DIR__ . '/../../python_api/database/predictions.db';

    try {
        $db = new SQLite3($dbPath);
        $stmt = $db->prepare("UPDATE predictions SET match_date = :match_date WHERE id = :id");
        $stmt->bindValue(':match_date', $matchDate, SQLITE3_TEXT);
        $stmt->bindValue(':id', $id, SQLITE3_INTEGER);
        $stmt->execute();

        echo json_encode([
            'success' => true,
            'message' => 'Match date updated',
            'id' => $id,
            'match_date' => $matchDate
        ]);

        $db->close();
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
}

function getAccuracyStats()
{
    $dbPath = __DIR__ . '/../../python_api/database/predictions.db';

    try {
        $db = new SQLite3($dbPath);

        $stats = [
            'overall' => [],
            'by_model' => [],
            'by_certainty' => [],
            'by_market' => []
        ];

        // Overall accuracy (matched predictions only)
        $result = $db->query("
            SELECT 
                COUNT(*) as total,
                SUM(correct_1x2) as correct_1x2,
                SUM(correct_goals_25) as correct_goals,
                SUM(correct_btts) as correct_btts,
                SUM(correct_cards_35) as correct_cards
            FROM predictions 
            WHERE is_matched = 1
        ");
        $row = $result->fetchArray(SQLITE3_ASSOC);

        $total = $row['total'];
        if ($total > 0) {
            $stats['overall'] = [
                'total_matched' => $total,
                'accuracy_1x2' => round(($row['correct_1x2'] / $total) * 100, 1),
                'accuracy_goals' => round(($row['correct_goals'] / $total) * 100, 1),
                'accuracy_btts' => round(($row['correct_btts'] / $total) * 100, 1),
                'accuracy_cards' => round(($row['correct_cards'] / $total) * 100, 1)
            ];
        }

        // Accuracy by model
        $result = $db->query("
            SELECT 
                model_type,
                COUNT(*) as total,
                SUM(correct_1x2) as correct_1x2,
                SUM(correct_goals_25) as correct_goals,
                SUM(correct_btts) as correct_btts
            FROM predictions 
            WHERE is_matched = 1
            GROUP BY model_type
        ");

        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $total = $row['total'];
            $stats['by_model'][$row['model_type']] = [
                'total' => $total,
                'accuracy_1x2' => round(($row['correct_1x2'] / $total) * 100, 1),
                'accuracy_goals' => round(($row['correct_goals'] / $total) * 100, 1),
                'accuracy_btts' => round(($row['correct_btts'] / $total) * 100, 1)
            ];
        }

        // Accuracy by certainty level
        $result = $db->query("
            SELECT 
                CASE 
                    WHEN certainty_1x2 >= 0.7 THEN 'High'
                    WHEN certainty_1x2 >= 0.4 THEN 'Medium'
                    ELSE 'Low'
                END as certainty_level,
                COUNT(*) as total,
                SUM(correct_1x2) as correct_1x2,
                SUM(correct_goals_25) as correct_goals
            FROM predictions 
            WHERE is_matched = 1
            GROUP BY certainty_level
        ");

        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $total = $row['total'];
            $stats['by_certainty'][$row['certainty_level']] = [
                'total' => $total,
                'accuracy_1x2' => round(($row['correct_1x2'] / $total) * 100, 1),
                'accuracy_goals' => round(($row['correct_goals'] / $total) * 100, 1)
            ];
        }

        echo json_encode(['success' => true, 'stats' => $stats]);
        $db->close();
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
}
