<?php

/**
 * Analytics Dashboard - 3-Tab Design
 * Tab 1: 🎯 Markets (PRIMARY - 60% emphasis)
 * Tab 2: 📈 Calibration (SECONDARY - 30% emphasis)
 * Tab 3: 🔧 Models (TERTIARY - 10% emphasis)
 */

require_once __DIR__ . '/../php_backend/config.php';

// Fetch analytics data from Python
$pythonScript = __DIR__ . '/../python_api/get_analytics_data.py';
$cmd = "python3 $pythonScript 2>&1";
exec($cmd, $output, $returnCode);

$analyticsData = json_decode(implode("\n", $output), true);

if (!$analyticsData || !$analyticsData['success']) {
    $analyticsData = [
        'success' => false,
        'markets' => [],
        'calibration' => [],
        'models' => []
    ];
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Dashboard - Football Predictions</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <style>
        .metric-card {
            transition: transform 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        .roi-positive {
            color: #28a745;
            font-weight: bold;
        }

        .roi-negative {
            color: #dc3545;
            font-weight: bold;
        }

        .top-market {
            border-left: 4px solid #28a745;
        }

        .avoid-market {
            border-left: 4px solid #dc3545;
        }

        .nav-pills .nav-link.active {
            background-color: #0d6efd;
        }

        .badge-roi {
            font-size: 1.1rem;
            padding: 0.5rem 1rem;
        }
    </style>
</head>

<body>

    <!-- Navigation -->
    <nav class="navbar navbar-dark bg-dark shadow-sm">
        <div class="container-fluid">
            <a class="navbar-brand" href="index.php">
                <i class="bi bi-arrow-left me-2"></i> Back to Predictions
            </a>
            <span class="navbar-text text-light">
                <i class="bi bi-graph-up me-1"></i> Analytics Dashboard
            </span>
        </div>
    </nav>

    <div class="container my-4" style="max-width: 75%;">

        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="display-5">
                    <i class="bi bi-bar-chart-fill text-primary"></i> Performance Analytics
                </h1>
                <p class="text-muted">Track prediction accuracy, market performance, and model reliability</p>
            </div>
        </div>

        <!-- 3-Tab Navigation -->
        <ul class="nav nav-pills mb-4" id="analyticsTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="markets-tab" data-bs-toggle="tab" data-bs-target="#markets" type="button">
                    🎯 Markets <span class="badge bg-success ms-2">PRIMARY</span>
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="calibration-tab" data-bs-toggle="tab" data-bs-target="#calibration" type="button">
                    📈 Calibration
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="models-tab" data-bs-toggle="tab" data-bs-target="#models" type="button">
                    🔧 Models
                </button>
            </li>
            <!-- Prediction tab -->
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="predictions-tab" data-bs-toggle="tab" data-bs-target="#predictions" type="button">
                    <i class="bi bi-database me-1"></i> Saved Predictions
                </button>
            </li>
            <!-- Accuracy tab -->
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="accuracy-tab" data-bs-toggle="tab" data-bs-target="#accuracy" type="button">
                    <i class="bi bi-bar-chart-fill me-1"></i> Accuracy
                </button>
            </li>

        </ul>


        <!-- Tab Content -->
        <div class="tab-content" id="analyticsTabsContent">

            <!-- TAB 1: MARKETS -->
            <div class="tab-pane fade show active" id="markets" role="tabpanel">

                <div class="row">
                    <!-- Summary Stats -->
                    <div class="col-md-4 mb-4">
                        <div class="card text-white bg-primary">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="bi bi-trophy-fill"></i> Total Predictions
                                </h5>
                                <h2><?= $analyticsData['total_predictions'] ?? 0 ?></h2>
                                <p class="mb-0">
                                    <small>
                                        <i class="bi bi-check-circle"></i>
                                        <?= $analyticsData['total_correct'] ?? 0 ?> Correct
                                    </small>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4 mb-4">
                        <div class="card text-white bg-success">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="bi bi-graph-up-arrow"></i> Overall ROI
                                </h5>
                                <h2>+<?= number_format($analyticsData['overall_roi'] ?? 0, 1) ?>%</h2>
                                <p class="mb-0">
                                    <small>Based on 2.0 avg odds</small>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4 mb-4">
                        <div class="card text-white bg-info">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="bi bi-award"></i> Best Market
                                </h5>
                                <h2><?= $analyticsData['best_market'] ?? 'N/A' ?></h2>
                                <p class="mb-0">
                                    <small><?= $analyticsData['best_market_roi'] ?? 0 ?>% ROI</small>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Top Performing Markets -->
                <div class="card mb-4 top-market">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="bi bi-star-fill"></i> 🏆 TOP PERFORMING MARKETS
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <?php if (!empty($analyticsData['markets'])): ?>
                                <?php
                                $topMarkets = array_filter($analyticsData['markets'], function ($m) {
                                    return ($m['roi_pct'] ?? 0) > 0;
                                });
                                usort($topMarkets, function ($a, $b) {
                                    return ($b['roi_pct'] ?? 0) <=> ($a['roi_pct'] ?? 0);
                                });
                                $topMarkets = array_slice($topMarkets, 0, 3);
                                ?>

                                <?php foreach ($topMarkets as $index => $market): ?>
                                    <div class="col-md-4 mb-3">
                                        <div class="card metric-card">
                                            <div class="card-body text-center">
                                                <h3 class="text-muted">#<?= $index + 1 ?></h3>
                                                <h5><?= htmlspecialchars($market['market']) ?></h5>
                                                <span class="badge badge-roi bg-success">
                                                    +<?= number_format($market['roi_pct'], 1) ?>% ROI
                                                </span>
                                                <p class="mt-2 mb-0 text-muted">
                                                    <small>
                                                        <?= $market['total_predictions'] ?> predictions |
                                                        <?= number_format($market['accuracy_pct'], 1) ?>% accuracy
                                                    </small>
                                                </p>
                                                <p class="mb-0">
                                                    <small class="text-info">
                                                        Brier: <?= number_format($market['brier_score'], 3) ?>
                                                    </small>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>

                            <?php else: ?>
                                <div class="col-12">
                                    <p class="text-muted">
                                        <i class="bi bi-info-circle"></i>
                                        No market data yet. Make predictions to see performance!
                                    </p>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>

                <!-- Markets to Avoid -->
                <div class="card mb-4 avoid-market">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0">
                            <i class="bi bi-exclamation-triangle-fill"></i> ⚠️ AVOID THESE MARKETS
                        </h5>
                    </div>
                    <div class="card-body">
                        <?php
                        $worstMarkets = array_filter($analyticsData['markets'] ?? [], function ($m) {
                            return ($m['roi_pct'] ?? 0) < 0;
                        });
                        usort($worstMarkets, function ($a, $b) {
                            return ($a['roi_pct'] ?? 0) <=> ($b['roi_pct'] ?? 0);
                        });
                        $worstMarkets = array_slice($worstMarkets, 0, 3);
                        ?>

                        <?php if (!empty($worstMarkets)): ?>
                            <ul class="list-group">
                                <?php foreach ($worstMarkets as $market): ?>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <span>
                                            <i class="bi bi-x-circle text-danger"></i>
                                            <?= htmlspecialchars($market['market']) ?>
                                        </span>
                                        <span class="roi-negative">
                                            <?= number_format($market['roi_pct'], 1) ?>% ROI
                                        </span>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        <?php else: ?>
                            <p class="text-success mb-0">
                                <i class="bi bi-check-circle-fill"></i>
                                All markets showing positive ROI!
                            </p>
                        <?php endif; ?>
                    </div>
                </div>

                <!-- All Markets Table -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-table"></i> Complete Market Performance
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Market</th>
                                        <th>Predictions</th>
                                        <th>Accuracy</th>
                                        <th>Brier Score</th>
                                        <th>ROI</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (!empty($analyticsData['markets'])): ?>
                                        <?php foreach ($analyticsData['markets'] as $market): ?>
                                            <tr>
                                                <td><strong><?= htmlspecialchars($market['market']) ?></strong></td>
                                                <td><?= $market['total_predictions'] ?></td>
                                                <td><?= number_format($market['accuracy_pct'], 1) ?>%</td>
                                                <td><?= number_format($market['brier_score'], 3) ?></td>
                                                <td class="<?= ($market['roi_pct'] > 0) ? 'roi-positive' : 'roi-negative' ?>">
                                                    <?= ($market['roi_pct'] > 0 ? '+' : '') . number_format($market['roi_pct'], 1) ?>%
                                                </td>
                                                <td>
                                                    <?php if ($market['roi_pct'] > 5): ?>
                                                        <span class="badge bg-success">✓ Bet</span>
                                                    <?php elseif ($market['roi_pct'] < -2): ?>
                                                        <span class="badge bg-danger">✗ Avoid</span>
                                                    <?php else: ?>
                                                        <span class="badge bg-warning">⚠ Caution</span>
                                                    <?php endif; ?>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="6" class="text-center text-muted">
                                                No market data available yet
                                            </td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>

            <!-- TAB 2: CALIBRATION -->
            <div class="tab-pane fade" id="calibration" role="tabpanel">

                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="bi bi-bullseye"></i> Confidence Reliability
                        </h5>
                    </div>
                    <div class="card-body">
                        <p class="lead">How reliable are my probability estimates?</p>

                        <div class="row">
                            <?php if (!empty($analyticsData['calibration'])): ?>
                                <?php foreach ($analyticsData['calibration'] as $cal): ?>
                                    <div class="col-md-4 mb-3">
                                        <div class="card">
                                            <div class="card-body text-center">
                                                <h6 class="text-muted">When I say <?= $cal['confidence_level'] ?>%</h6>
                                                <h3><?= number_format($cal['actual_accuracy'], 1) ?>%</h3>
                                                <p class="mb-0">
                                                    <?php if (abs($cal['actual_accuracy'] - $cal['confidence_level']) < 5): ?>
                                                        <span class="text-success">✓ Well calibrated</span>
                                                    <?php else: ?>
                                                        <span class="text-warning">⚠ Needs adjustment</span>
                                                    <?php endif; ?>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            <?php else: ?>
                                <div class="col-12">
                                    <p class="text-muted">Calibration data will appear after collecting results</p>
                                </div>
                            <?php endif; ?>
                        </div>

                        <!-- Calibration Chart -->
                        <div class="mt-4">
                            <canvas id="calibrationChart" height="80"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Brier Score Summary -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-graph-down"></i> Brier Score Performance
                        </h5>
                    </div>
                    <div class="card-body">
                        <p>
                            <strong>Current Brier Score:</strong>
                            <span class="badge bg-info fs-5">
                                <?= number_format($analyticsData['avg_brier_score'] ?? 0, 3) ?>
                            </span>
                        </p>
                        <p class="text-muted mb-0">
                            <small>
                                Lower is better. Scores below 0.25 are excellent.
                                Brier score measures probability calibration quality.
                            </small>
                        </p>
                    </div>
                </div>

            </div>

            <!-- TAB 3: MODELS -->
            <div class="tab-pane fade" id="models" role="tabpanel">

                <div class="alert alert-info">
                    <i class="bi bi-info-circle-fill"></i>
                    <strong>Auto-Selection Active:</strong> System automatically uses the best-performing model.
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-cpu-fill"></i> Model Comparison (Advanced)
                        </h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Currently Using:</strong> <span class="badge bg-primary">Ensemble</span></p>

                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Model</th>
                                        <th>Accuracy</th>
                                        <th>Brier Score</th>
                                        <th>F1 Score</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (!empty($analyticsData['models'])): ?>
                                        <?php foreach ($analyticsData['models'] as $model): ?>
                                            <tr>
                                                <td><?= htmlspecialchars($model['model_type']) ?></td>
                                                <td><?= number_format($model['accuracy_pct'], 1) ?>%</td>
                                                <td><?= number_format($model['brier_score'], 3) ?></td>
                                                <td><?= number_format($model['f1_score'] ?? 0, 3) ?></td>
                                                <td>
                                                    <?php if ($model['model_type'] === 'ensemble'): ?>
                                                        <span class="badge bg-success">✓ Active</span>
                                                    <?php else: ?>
                                                        <span class="badge bg-secondary">Standby</span>
                                                    <?php endif; ?>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="5" class="text-center text-muted">
                                                No model comparison data yet
                                            </td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>

                        <p class="text-muted mb-0">
                            <small>
                                <i class="bi bi-lightbulb"></i>
                                The ensemble model combines XGBoost (40%) and Random Forest (60%)
                                for optimal performance across all markets.
                            </small>
                        </p>
                    </div>
                </div>

            </div>

            <!-- TAB4 - SAVED PREDICTIONS TAB -->
            <div class="tab-pane fade" id="predictions" role="tabpanel">
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0">
                                    <i class="bi bi-table me-2"></i>
                                    Saved Predictions Database
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <p class="text-muted mb-0">
                                        Total Saved: <strong id="savedPredictionsCount">0</strong>
                                    </p>
                                    <button class="btn btn-sm btn-outline-primary" onclick="loadSavedPredictions()">
                                        <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                                    </button>
                                </div>

                                <div class="table-responsive">
                                    <table class="table table-striped table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th>#</th>
                                                <th>Predicted On</th>
                                                <th>Match Date</th>
                                                <th>Match</th>
                                                <th>Model</th>
                                                <th>1X2 Prediction</th>
                                                <th>Probabilities</th>
                                                <th>Certainty</th>
                                                <th>BTTS</th>
                                                <th>Goals 2.5</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody id="savedPredictionsTable">
                                            <tr>
                                                <td colspan="10" class="text-center text-muted">
                                                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                                                    Loading predictions...
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 5 - Accuracy Tab -->
            <div class="tab-pane fade" id="accuracy" role="tabpanel">

                <!-- 4A: Overall Accuracy Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card text-white bg-primary">
                            <div class="card-body text-center">
                                <h3 class="mb-0" id="acc1x2">-%</h3>
                                <p class="mb-0">1X2 Accuracy</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success">
                            <div class="card-body text-center">
                                <h3 class="mb-0" id="accGoals">-%</h3>
                                <p class="mb-0">Goals O/U 2.5</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-info">
                            <div class="card-body text-center">
                                <h3 class="mb-0" id="accBTTS">-%</h3>
                                <p class="mb-0">BTTS Accuracy</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-danger">
                            <div class="card-body text-center">
                                <h3 class="mb-0" id="accCards">-%</h3>
                                <p class="mb-0">Cards Accuracy</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4B: Accuracy by Certainty Level -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h5 class="mb-0"><i class="bi bi-speedometer2 me-2"></i>Accuracy by Certainty Level</h5>
                            </div>
                            <div class="card-body">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Certainty Level</th>
                                            <th>1X2 Accuracy</th>
                                            <th>Goals Accuracy</th>
                                            <th>Total Predictions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="certaintyTable">
                                        <tr>
                                            <td colspan="4" class="text-center text-muted">Loading...</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4C: Model Comparison -->
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-dark text-white">
                                <h5 class="mb-0"><i class="bi bi-graph-up me-2"></i>Model Performance Comparison</h5>
                            </div>
                            <div class="card-body">
                                <div id="modelComparisonTable"></div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>


        </div>

    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // Calibration Chart
        const calibrationData = <?= json_encode($analyticsData['calibration'] ?? []) ?>;

        if (calibrationData.length > 0) {
            const ctx = document.getElementById('calibrationChart');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: calibrationData.map(d => d.confidence_level + '%'),
                    datasets: [{
                            label: 'Actual Accuracy',
                            data: calibrationData.map(d => d.actual_accuracy),
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            tension: 0.1
                        },
                        {
                            label: 'Perfect Calibration',
                            data: calibrationData.map(d => d.confidence_level),
                            borderColor: 'rgb(255, 99, 132)',
                            borderDash: [5, 5],
                            backgroundColor: 'transparent'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Calibration Curve'
                        },
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Actual Accuracy (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Predicted Confidence (%)'
                            }
                        }
                    }
                }
            });
        }

        // Load Saved Predictions for the new tab
        async function loadSavedPredictions() {
            const API_BASE = '../php_backend/api';
            const tbody = document.getElementById('savedPredictionsTable');

            // Show loading
            tbody.innerHTML = '<tr><td colspan="10" class="text-center"><div class="spinner-border spinner-border-sm me-2"></div>Loading...</td></tr>';

            try {
                const response = await fetch(`${API_BASE}/analytics_api.php?action=list_predictions&limit=50`);
                const data = await response.json();

                if (data.success && data.predictions.length > 0) {
                    tbody.innerHTML = '';
                    document.getElementById('savedPredictionsCount').textContent = data.predictions.length;

                    data.predictions.forEach((pred, index) => {
                        const certaintyClass = pred.certainty_1x2 >= 0.7 ? 'text-success fw-bold' :
                            pred.certainty_1x2 >= 0.4 ? 'text-warning fw-bold' : 'text-danger fw-bold';

                        const predDate = new Date(pred.prediction_date).toLocaleDateString();

                        tbody.innerHTML += `
        <tr style="cursor: pointer;" onclick="showPredictionDetails(${pred.id})" class="table-row-hover">
            <td>${index + 1}</td>
            
            <!-- Prediction Date (Read-only) -->
            <td>
                <small class="text-muted">${predDate}</small>
            </td>
            
            <!-- Match Date (Editable) -->
            <td>
                <input type="date" 
                       class="form-control form-control-sm match-date-input" 
                       data-prediction-id="${pred.id}"
                       value="${pred.match_date || ''}"
                       onclick="event.stopPropagation()"
                       onchange="updateMatchDate(${pred.id}, this.value)"
                       style="max-width: 150px;"
                       title="Click to set match date">
            </td>
            
            <!-- Rest of columns -->
            <td><strong>${pred.home_team}</strong> vs ${pred.away_team}</td>
            <td><span class="badge bg-info">${pred.model_type}</span></td>
            <td><span class="badge bg-primary">${pred.prediction_1x2}</span></td>
            <td>
                <small>
                    H: ${(pred.prob_home * 100).toFixed(0)}% | 
                    D: ${(pred.prob_draw * 100).toFixed(0)}% | 
                    A: ${(pred.prob_away * 100).toFixed(0)}%
                </small>
            </td>
            <td><span class="${certaintyClass}">${(pred.certainty_1x2 * 100).toFixed(0)}%</span></td>
            <td>${pred.prediction_btts || '-'}</td>
            <td>${pred.prediction_goals_25 || '-'}</td>
            <td>
                ${pred.is_matched ? '<span class="badge bg-success">✓ Matched</span>' : '<span class="badge bg-secondary">Pending</span>'}
                <button class="btn btn-sm btn-outline-primary ms-2" onclick="event.stopPropagation(); showPredictionDetails(${pred.id})">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        </tr>
    `;
                    });

                } else {
                    tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No predictions saved yet</td></tr>';
                    document.getElementById('savedPredictionsCount').textContent = '0';
                }
            } catch (error) {
                console.error('Error loading predictions:', error);
                tbody.innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error loading predictions</td></tr>';
            }
        }

        // Load predictions when the tab is shown
        document.getElementById('predictions-tab').addEventListener('shown.bs.tab', function() {
            loadSavedPredictions();
        });

        // Also load on page load if this tab is active
        document.addEventListener('DOMContentLoaded', function() {
            // Your existing DOMContentLoaded code here

            // If predictions tab is active, load predictions
            if (document.getElementById('predictions-tab').classList.contains('active')) {
                loadSavedPredictions();
            }
        });

        // Show prediction details in modal
        // Show prediction details in modal
        async function showPredictionDetails(predictionId) {
            const API_BASE = '../php_backend/api';

            try {
                const response = await fetch(`${API_BASE}/analytics_api.php?action=list_predictions&limit=1000`);
                const data = await response.json();

                if (data.success) {
                    const pred = data.predictions.find(p => p.id == predictionId);

                    if (!pred) {
                        alert('Prediction not found');
                        return;
                    }

                    // Populate modal
                    document.getElementById('modalMatchTitle').textContent = `${pred.home_team} vs ${pred.away_team}`;
                    document.getElementById('modalHomeTeam').textContent = pred.home_team;
                    document.getElementById('modalAwayTeam').textContent = pred.away_team;
                    document.getElementById('modalModel').textContent = pred.model_type.toUpperCase();
                    document.getElementById('modalDate').textContent = new Date(pred.prediction_date).toLocaleDateString();

                    // Match Result (1X2)
                    document.getElementById('modal1x2Prediction').textContent = pred.prediction_1x2 || 'N/A';
                    const probHome = (pred.prob_home * 100).toFixed(1);
                    const probDraw = (pred.prob_draw * 100).toFixed(1);
                    const probAway = (pred.prob_away * 100).toFixed(1);

                    document.getElementById('modalProbHome').textContent = probHome + '%';
                    document.getElementById('modalProbDraw').textContent = probDraw + '%';
                    document.getElementById('modalProbAway').textContent = probAway + '%';
                    document.getElementById('modalProbHomeBar').style.width = probHome + '%';
                    document.getElementById('modalProbDrawBar').style.width = probDraw + '%';
                    document.getElementById('modalProbAwayBar').style.width = probAway + '%';

                    const certaintyClass = pred.certainty_1x2 >= 0.7 ? 'text-success' : pred.certainty_1x2 >= 0.4 ? 'text-warning' : 'text-danger';
                    const certaintyElem = document.getElementById('modalCertainty1x2');
                    certaintyElem.textContent = (pred.certainty_1x2 * 100).toFixed(1) + '%';
                    certaintyElem.className = certaintyClass;

                    // Goals Predictions
                    document.getElementById('modalGoals05').textContent = pred.prediction_goals_05 || 'N/A';
                    document.getElementById('modalProb05').textContent = pred.prob_over_05 ? `${(pred.prob_over_05 * 100).toFixed(1)}% (Certainty: ${(pred.certainty_goals_05 * 100).toFixed(1)}%)` : '';

                    document.getElementById('modalGoals15').textContent = pred.prediction_goals_15 || 'N/A';
                    document.getElementById('modalProb15').textContent = pred.prob_over_15 ? `${(pred.prob_over_15 * 100).toFixed(1)}% (Certainty: ${(pred.certainty_goals_15 * 100).toFixed(1)}%)` : '';

                    document.getElementById('modalGoals25').textContent = pred.prediction_goals_25 || 'N/A';
                    document.getElementById('modalProb25').textContent = pred.prob_over_25 ? `${(pred.prob_over_25 * 100).toFixed(1)}% (Certainty: ${(pred.certainty_goals_25 * 100).toFixed(1)}%)` : '';

                    document.getElementById('modalGoals35').textContent = pred.prediction_goals_35 || 'N/A';
                    document.getElementById('modalProb35').textContent = pred.prob_over_35 ? `${(pred.prob_over_35 * 100).toFixed(1)}% (Certainty: ${(pred.certainty_goals_35 * 100).toFixed(1)}%)` : '';

                    // BTTS
                    document.getElementById('modalBTTS').textContent = pred.prediction_btts || 'N/A';
                    document.getElementById('modalProbBTTS').textContent = pred.prob_btts_yes ? `${(pred.prob_btts_yes * 100).toFixed(1)}% (Certainty: ${(pred.certainty_btts * 100).toFixed(1)}%)` : '';

                    // Double Chance (calculated from 1X2 probabilities)
                    const prob1X = pred.prob_home_draw || (pred.prob_home + pred.prob_draw);
                    const prob12 = pred.prob_home_away || (pred.prob_home + pred.prob_away);
                    const probX2 = pred.prob_draw_away || (pred.prob_draw + pred.prob_away);

                    document.getElementById('modalDC1X').textContent = prob1X ? `${(prob1X * 100).toFixed(1)}%` : 'N/A';
                    document.getElementById('modalDC12').textContent = prob12 ? `${(prob12 * 100).toFixed(1)}%` : 'N/A';
                    document.getElementById('modalDCX2').textContent = probX2 ? `${(probX2 * 100).toFixed(1)}%` : 'N/A';

                    // Cards Predictions
                    let cardsHTML = '';

                    if (pred.prediction_cards_25 || pred.prediction_cards_35 || pred.prediction_cards_45) {
                        cardsHTML += '<div class="row">';

                        // Cards 2.5
                        if (pred.prediction_cards_25) {
                            cardsHTML += `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Total Cards O/U 2.5</h6>
                                    <h5><span class="badge bg-danger">${pred.prediction_cards_25}</span></h5>
                                    <small>Probability: ${(pred.prob_cards_over_25 * 100).toFixed(1)}%</small><br>
                                    <small>Certainty: ${(pred.certainty_cards_25 * 100).toFixed(1)}%</small>
                                </div>
                            </div>
                        </div>
                    `;
                        }

                        // Cards 3.5
                        if (pred.prediction_cards_35) {
                            cardsHTML += `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Total Cards O/U 3.5</h6>
                                    <h5><span class="badge bg-danger">${pred.prediction_cards_35}</span></h5>
                                    <small>Probability: ${(pred.prob_cards_over_35 * 100).toFixed(1)}%</small><br>
                                    <small>Certainty: ${(pred.certainty_cards_35 * 100).toFixed(1)}%</small>
                                </div>
                            </div>
                        </div>
                    `;
                        }

                        // Cards 4.5
                        if (pred.prediction_cards_45) {
                            cardsHTML += `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Total Cards O/U 4.5</h6>
                                    <h5><span class="badge bg-danger">${pred.prediction_cards_45}</span></h5>
                                    <small>Probability: ${(pred.prob_cards_over_45 * 100).toFixed(1)}%</small><br>
                                    <small>Certainty: ${(pred.certainty_cards_45 * 100).toFixed(1)}%</small>
                                </div>
                            </div>
                        </div>
                    `;
                        }

                        cardsHTML += '</div>';
                    } else {
                        cardsHTML = '<div class="col-12 text-muted text-center">No cards predictions available</div>';
                    }

                    document.getElementById('modalCardsContent').innerHTML = cardsHTML;

                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('predictionDetailsModal'));
                    modal.show();
                }
            } catch (error) {
                console.error('Error loading prediction details:', error);
                alert('Error loading prediction details');
            }
        }


        // Update match date for a prediction
        async function updateMatchDate(predictionId, newDate) {
            const API_BASE = '../php_backend/api';

            if (!newDate) {
                return; // Allow clearing the date
            }

            try {
                const response = await fetch(`${API_BASE}/analytics_api.php?action=update_match_date`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id: predictionId,
                        match_date: newDate
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // Visual feedback - green border flash
                    const input = document.querySelector(`input[data-prediction-id="${predictionId}"]`);
                    input.classList.add('border-success', 'border-3');
                    setTimeout(() => {
                        input.classList.remove('border-success', 'border-3');
                    }, 1500);

                    console.log('✅ Match date updated:', newDate);
                } else {
                    alert('Failed to update match date: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error updating match date:', error);
                alert('Error updating match date');
            }
        }

        // Load Accuracy Stats
        async function loadAccuracyStats() {
            const API_BASE = '../php_backend/api';

            try {
                const response = await fetch(`${API_BASE}/analytics_api.php?action=accuracy_stats`);
                const data = await response.json();

                if (data.success && data.stats) {
                    const stats = data.stats;

                    // 4A: Overall Accuracy Cards
                    if (stats.overall && stats.overall.total_matched > 0) {
                        document.getElementById('acc1x2').textContent = stats.overall.accuracy_1x2 + '%';
                        document.getElementById('accGoals').textContent = stats.overall.accuracy_goals + '%';
                        document.getElementById('accBTTS').textContent = stats.overall.accuracy_btts + '%';
                        document.getElementById('accCards').textContent = stats.overall.accuracy_cards + '%';
                    } else {
                        document.getElementById('acc1x2').textContent = 'N/A';
                        document.getElementById('accGoals').textContent = 'N/A';
                        document.getElementById('accBTTS').textContent = 'N/A';
                        document.getElementById('accCards').textContent = 'N/A';
                    }

                    // 4B: Accuracy by Certainty Level
                    const certaintyTable = document.getElementById('certaintyTable');
                    if (stats.by_certainty && Object.keys(stats.by_certainty).length > 0) {
                        certaintyTable.innerHTML = '';

                        // Order: High, Medium, Low
                        const order = ['High', 'Medium', 'Low'];
                        order.forEach(level => {
                            if (stats.by_certainty[level]) {
                                const cert = stats.by_certainty[level];
                                const rowClass = level === 'High' ? 'table-success' :
                                    level === 'Medium' ? 'table-warning' : 'table-danger';

                                certaintyTable.innerHTML += `
                            <tr class="${rowClass}">
                                <td><strong>${level} (${level === 'High' ? '70%+' : level === 'Medium' ? '40-70%' : '<40%'})</strong></td>
                                <td>${cert.accuracy_1x2}%</td>
                                <td>${cert.accuracy_goals}%</td>
                                <td>${cert.total}</td>
                            </tr>
                        `;
                            }
                        });
                    } else {
                        certaintyTable.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No matched predictions yet</td></tr>';
                    }

                    // 4C: Model Comparison
                    const modelTable = document.getElementById('modelComparisonTable');
                    if (stats.by_model && Object.keys(stats.by_model).length > 0) {
                        let html = `
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Model</th>
                                <th>1X2 Accuracy</th>
                                <th>Goals Accuracy</th>
                                <th>BTTS Accuracy</th>
                                <th>Total Predictions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                        // Sort by 1X2 accuracy (best first)
                        const sortedModels = Object.entries(stats.by_model).sort((a, b) =>
                            b[1].accuracy_1x2 - a[1].accuracy_1x2
                        );

                        sortedModels.forEach(([modelName, modelStats]) => {
                            const badgeClass = modelName === 'ensemble' ? 'bg-success' :
                                modelName === 'xgboost' ? 'bg-primary' : 'bg-info';

                            html += `
                        <tr>
                            <td><span class="badge ${badgeClass}">${modelName.toUpperCase()}</span></td>
                            <td>
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-success" style="width: ${modelStats.accuracy_1x2}%">
                                        ${modelStats.accuracy_1x2}%
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-info" style="width: ${modelStats.accuracy_goals}%">
                                        ${modelStats.accuracy_goals}%
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-warning" style="width: ${modelStats.accuracy_btts}%">
                                        ${modelStats.accuracy_btts}%
                                    </div>
                                </div>
                            </td>
                            <td><strong>${modelStats.total}</strong></td>
                        </tr>
                    `;
                        });

                        html += '</tbody></table>';
                        modelTable.innerHTML = html;
                    } else {
                        modelTable.innerHTML = '<p class="text-center text-muted">No matched predictions yet. Start making predictions!</p>';
                    }

                } else {
                    console.error('Failed to load accuracy stats:', data.error);
                }
            } catch (error) {
                console.error('Error loading accuracy stats:', error);
            }
        }

        // Load accuracy stats when the Accuracy tab is clicked
        document.getElementById('accuracy-tab').addEventListener('shown.bs.tab', function() {
            loadAccuracyStats();
        });

        // Optional: Load on page load if Accuracy tab is active
        document.addEventListener('DOMContentLoaded', function() {
            // Your existing DOMContentLoaded code...

            // Check if Accuracy tab is active on page load
            if (document.getElementById('accuracy-tab').classList.contains('active')) {
                loadAccuracyStats();
            }
        });
    </script>



    <!-- * Modal  -   Prediction Details Modal -->
    <div class="modal fade" id="predictionDetailsModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="bi bi-info-circle me-2"></i>
                        <span id="modalMatchTitle">Prediction Details</span>
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <!-- Match Info -->
                        <div class="col-md-12 mb-3">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <div class="row text-center">
                                        <div class="col">
                                            <h4 id="modalHomeTeam">-</h4>
                                            <small class="text-muted">Home</small>
                                        </div>
                                        <div class="col-auto">
                                            <h4 class="text-muted">VS</h4>
                                        </div>
                                        <div class="col">
                                            <h4 id="modalAwayTeam">-</h4>
                                            <small class="text-muted">Away</small>
                                        </div>
                                    </div>
                                    <hr>
                                    <div class="text-center">
                                        <span class="badge bg-info me-2" id="modalModel">Model</span>
                                        <span class="badge bg-secondary" id="modalDate">Date</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Match Result Prediction -->
                        <div class="col-md-6 mb-3">
                            <div class="card h-100">
                                <div class="card-header bg-primary text-white">
                                    <strong>Match Result (1X2)</strong>
                                </div>
                                <div class="card-body">
                                    <h5 class="text-center mb-3">
                                        <span class="badge bg-success" id="modal1x2Prediction">-</span>
                                    </h5>
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>Home Win</span>
                                            <strong id="modalProbHome">-%</strong>
                                        </div>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" id="modalProbHomeBar"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>Draw</span>
                                            <strong id="modalProbDraw">-%</strong>
                                        </div>
                                        <div class="progress">
                                            <div class="progress-bar bg-warning" id="modalProbDrawBar"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span>Away Win</span>
                                            <strong id="modalProbAway">-%</strong>
                                        </div>
                                        <div class="progress">
                                            <div class="progress-bar bg-danger" id="modalProbAwayBar"></div>
                                        </div>
                                    </div>
                                    <hr>
                                    <div class="text-center">
                                        <span class="text-muted">Certainty:</span>
                                        <strong id="modalCertainty1x2" class="text-success">-%</strong>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Goals & BTTS -->
                        <!-- Goals, BTTS & Double Chance -->
                        <div class="col-md-6 mb-3">
                            <div class="card h-100">
                                <div class="card-header bg-success text-white">
                                    <strong>Goals & Special Markets</strong>
                                </div>
                                <div class="card-body">
                                    <!-- Goals -->
                                    <h6 class="border-bottom pb-2 mb-3">Goals Predictions</h6>
                                    <div class="mb-2">
                                        <strong>O/U 0.5:</strong>
                                        <span class="badge bg-primary" id="modalGoals05">-</span>
                                        <small class="text-muted ms-2" id="modalProb05">-</small>
                                    </div>
                                    <div class="mb-2">
                                        <strong>O/U 1.5:</strong>
                                        <span class="badge bg-primary" id="modalGoals15">-</span>
                                        <small class="text-muted ms-2" id="modalProb15">-</small>
                                    </div>
                                    <div class="mb-2">
                                        <strong>O/U 2.5:</strong>
                                        <span class="badge bg-primary" id="modalGoals25">-</span>
                                        <small class="text-muted ms-2" id="modalProb25">-</small>
                                    </div>
                                    <div class="mb-3">
                                        <strong>O/U 3.5:</strong>
                                        <span class="badge bg-primary" id="modalGoals35">-</span>
                                        <small class="text-muted ms-2" id="modalProb35">-</small>
                                    </div>

                                    <!-- BTTS -->
                                    <h6 class="border-bottom pb-2 mb-3">Both Teams To Score</h6>
                                    <div class="mb-3">
                                        <span class="badge bg-primary" id="modalBTTS">-</span>
                                        <small class="text-muted ms-2" id="modalProbBTTS">-</small>
                                    </div>

                                    <!-- Double Chance -->
                                    <h6 class="border-bottom pb-2 mb-3">Double Chance</h6>
                                    <div class="mb-2">
                                        <strong>1X (Home or Draw):</strong>
                                        <small class="text-muted ms-2" id="modalDC1X">-</small>
                                    </div>
                                    <div class="mb-2">
                                        <strong>12 (Home or Away):</strong>
                                        <small class="text-muted ms-2" id="modalDC12">-</small>
                                    </div>
                                    <div class="mb-2">
                                        <strong>X2 (Draw or Away):</strong>
                                        <small class="text-muted ms-2" id="modalDCX2">-</small>
                                    </div>
                                </div>
                            </div>
                        </div>


                        <!-- Cards Predictions -->
                        <div class="col-md-12">
                            <div class="card">
                                <div class="card-header bg-danger text-white">
                                    <strong>Cards Predictions</strong>
                                </div>
                                <div class="card-body">
                                    <div class="row" id="modalCardsContent">
                                        <div class="col-12 text-muted text-center">
                                            No cards data available
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>

</body>

</html>