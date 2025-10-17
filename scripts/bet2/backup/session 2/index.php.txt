<?php

/**
 * Football Prediction App - Main Page
 * Professional betting predictions using ML
 */
require_once __DIR__ . '/../php_backend/config.php';
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Predictions - ML Betting Analysis</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/custom.css">
</head>

<body>
    <!-- Navigation -->
    <nav class="navbar navbar-dark bg-dark shadow-sm">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="bi bi-activity me-2"></i>
                Football Predictions ML
            </a>
            <span class="navbar-text text-light">
                <i class="bi bi-cpu me-1"></i>
                Powered by XGBoost & Random Forest
            </span>
        </div>
    </nav>

    <div class="container my-4">
        <!-- Header Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card bg-primary text-white">
                    <div class="card-body py-4">
                        <h1 class="card-title mb-2">
                            <i class="bi bi-graph-up-arrow me-2"></i>
                            Match Prediction System
                        </h1>
                        <p class="card-text mb-0">
                            Advanced machine learning predictions for Premier League matches
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Prediction Form -->
        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card shadow-sm h-100">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">
                            <i class="bi bi-sliders me-2"></i>
                            Prediction Settings
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="predictionForm">
                            <!-- Competition Selection -->
                            <div class="mb-3">
                                <label for="competition" class="form-label">
                                    <i class="bi bi-trophy me-1"></i>
                                    Competition
                                </label>
                                <select class="form-select" id="competition" required>
                                    <option value="premier_league" selected>Premier League</option>
                                </select>
                            </div>

                            <!-- Home Team -->
                            <div class="mb-3">
                                <label for="homeTeam" class="form-label">
                                    <i class="bi bi-house-fill me-1"></i>
                                    Home Team
                                </label>
                                <select class="form-select" id="homeTeam" required>
                                    <option value="">Select home team...</option>
                                </select>
                            </div>

                            <!-- Away Team -->
                            <div class="mb-3">
                                <label for="awayTeam" class="form-label">
                                    <i class="bi bi-airplane-fill me-1"></i>
                                    Away Team
                                </label>
                                <select class="form-select" id="awayTeam" required>
                                    <option value="">Select away team...</option>
                                </select>
                            </div>

                            <!-- Model Type -->
                            <div class="mb-3">
                                <label for="modelType" class="form-label">
                                    <i class="bi bi-cpu-fill me-1"></i>
                                    Model Type
                                </label>
                                <select class="form-select" id="modelType">
                                    <option value="ensemble" selected>Ensemble (Best)</option>
                                    <option value="randomforest">Random Forest</option>
                                    <option value="xgboost">XGBoost</option>
                                </select>
                                <div class="form-text">
                                    Ensemble combines both models for best accuracy
                                </div>
                            </div>

                            <!-- Submit Button -->
                            <button type="submit" class="btn btn-primary w-100" id="predictBtn">
                                <i class="bi bi-lightning-charge-fill me-2"></i>
                                Generate Prediction
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div class="col-lg-8 mb-4">
                <!-- Loading Spinner -->
                <div id="loadingSpinner" class="text-center py-5" style="display: none;">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-muted">Analyzing match data...</p>
                    <p class="text-primary fw-bold fs-4" id="loadingTimer">0s</p>
                </div>

                <!-- Welcome Message -->
                <div id="welcomeMessage" class="card shadow-sm">
                    <div class="card-body text-center py-5">
                        <i class="bi bi-box-seam display-1 text-muted mb-3"></i>
                        <h4>Ready to Predict</h4>
                        <p class="text-muted">Select teams and generate your first prediction</p>
                    </div>
                </div>

                <!-- Results Container -->
                <div id="resultsContainer" style="display: none;">
                    <!-- Results will be inserted here by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <!-- Admin Controls Section -->
    <div class="container my-4">
        <div class="row">
            <div class="col-12">
                <div class="card shadow-sm border-warning">
                    <div class="card-header bg-warning">
                        <h5 class="mb-0">
                            <i class="bi bi-gear-fill me-2"></i>
                            Admin Controls
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <!-- Update Data Button -->
                            <div class="col-md-6 mb-3">
                                <div class="d-grid">
                                    <button id="updateDataBtn" class="btn btn-primary btn-lg">
                                        <i class="bi bi-arrow-clockwise me-2"></i>
                                        Update Match Data
                                    </button>
                                </div>
                                <small class="text-muted mt-2 d-block">
                                    Scrape latest matches from FBRef (takes ~2-3 minutes)
                                </small>
                                <div id="updateDataStatus" class="mt-2"></div>
                            </div>

                            <!-- Retrain Models Button -->
                            <div class="col-md-6 mb-3">
                                <div class="d-grid">
                                    <button id="retrainBtn" class="btn btn-success btn-lg">
                                        <i class="bi bi-cpu-fill me-2"></i>
                                        Retrain Models
                                    </button>
                                </div>
                                <small class="text-muted mt-2 d-block">
                                    Retrain all prediction models (takes ~3-5 minutes)
                                </small>
                                <div id="retrainStatus" class="mt-2"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <!-- Footer -->
    <footer class="bg-light py-3 mt-5">
        <div class="container text-center text-muted">
            <small>
                Football Predictions ML &copy; 2025 |
                Data updated: <span id="lastUpdate">Loading...</span>
            </small>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>

</html>