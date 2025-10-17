/**
 * Football Predictions App - Main JavaScript
 */

// Configuration
const API_BASE = '../php_backend/api';
const COMPETITION = 'premier_league';

// State
let teams = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    loadTeams();
    setupFormHandler();
});

/**
 * Load teams from API
 */
async function loadTeams() {
    try {
        const response = await fetch(`${API_BASE}/teams_api.php?competition=${COMPETITION}`);
        const data = await response.json();

        if (data.success) {
            teams = data.teams;
            populateTeamSelects();
        } else {
            showError('Failed to load teams');
        }
    } catch (error) {
        console.error('Error loading teams:', error);
        showError('Failed to load teams');
    }
}

/**
 * Populate team dropdowns
 */
function populateTeamSelects() {
    const homeSelect = document.getElementById('homeTeam');
    const awaySelect = document.getElementById('awayTeam');

    teams.forEach(team => {
        // Try team.name, fallback to team (string)
        const teamName = team.name ? team.name : team;
        const optionHome = new Option(teamName, teamName);
        const optionAway = new Option(teamName, teamName);
        homeSelect.add(optionHome);
        awaySelect.add(optionAway);
    });

}

/**
 * Setup form submission handler
 */
function setupFormHandler() {
    const form = document.getElementById('predictionForm');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const homeTeam = document.getElementById('homeTeam').value;
        const awayTeam = document.getElementById('awayTeam').value;
        const modelType = document.getElementById('modelType').value;

        // Validation
        if (!homeTeam || !awayTeam) {
            showError('Please select both teams');
            return;
        }

        if (homeTeam === awayTeam) {
            showError('Home and away teams must be different');
            return;
        }

        // Get prediction
        await getPrediction(homeTeam, awayTeam, modelType);
    });
}

/**
 * Get prediction from API
 */
async function getPrediction(homeTeam, awayTeam, modelType) {
    // Show loading
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'block';

    const predictBtn = document.getElementById('predictBtn');
    predictBtn.disabled = true;

    // Start timer
    let seconds = 0;
    const timerElement = document.getElementById('loadingTimer');
    const timerInterval = setInterval(() => {
        seconds++;
        timerElement.textContent = `${seconds}s`;
    }, 1000);

    try {
        const response = await fetch(`${API_BASE}/predict_api.php`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                home_team: homeTeam,
                away_team: awayTeam,
                competition: COMPETITION,
                model_type: modelType
            })
        });

        const data = await response.json();

        // Stop timer
        clearInterval(timerInterval);

        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Prediction failed');
        }
    } catch (error) {
        clearInterval(timerInterval);
        console.error('Error getting prediction:', error);
        showError('Failed to get prediction');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
        predictBtn.disabled = false;
    }
}


/**
 * Display prediction results
 */
function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const predictions = data.predictions;
    const match = data.match;

    let html = `
        <!-- Match Header -->
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col text-center">
                        <h3 class="mb-0">${match.home_team}</h3>
                        <small class="text-muted">Home</small>
                    </div>
                    <div class="col-auto">
                        <h4 class="mb-0 text-muted">VS</h4>
                    </div>
                    <div class="col text-center">
                        <h3 class="mb-0">${match.away_team}</h3>
                        <small class="text-muted">Away</small>
                    </div>
                </div>
                <hr>
                <div class="text-center">
                    <span class="badge bg-info">Model: ${data.model_type.toUpperCase()}</span>
                    <span class="badge bg-secondary ms-2">${new Date(match.date).toLocaleString()}</span>
                </div>
            </div>
        </div>
    `;

    // Match Result Card
    html += generateMatchResultCard(predictions.match_result);

    // Double Chance Card
    html += generateDoubleChanceCard(predictions.double_chance);

    // Goals Card
    html += generateGoalsCard(predictions.goals);

    // Cards Card
    html += generateCardsCard(predictions.cards);

    // Raw JSON Data (Collapsible)
    html += generateRawJsonCard(data);

    container.innerHTML = html;
    container.style.display = 'block';
}


/**
 * Generate Match Result card HTML
 */
function generateMatchResultCard(matchResult) {
    const homeProb = (matchResult.probabilities.home_win * 100).toFixed(1);
    const drawProb = (matchResult.probabilities.draw * 100).toFixed(1);
    const awayProb = (matchResult.probabilities.away_win * 100).toFixed(1);

    // Changed from confidence to certainty
    const certainty = (matchResult.certainty * 100).toFixed(1);
    const certaintyLevel = matchResult.certainty_level;

    let html = `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-trophy-fill me-2"></i>
                    Match Result Prediction
                    <span class="badge bg-light text-dark fs-6 ms-2">
                        ${matchResult.prediction}
                    </span>
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <h6>Prediction: <strong>${matchResult.prediction}</strong></h6>
                    <span class="badge bg-secondary">Certainty: ${certainty}%</span>
                    <span class="badge bg-info ms-2">${certaintyLevel}</span>
                </div>
                
                <h6 class="mb-3">Probabilities:</h6>
                
                <!-- Home Win -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span><i class="bi bi-house-fill text-success me-1"></i> Home Win</span>
                        <strong>${homeProb}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-success" style="width: ${homeProb}%">
                            ${homeProb}%
                        </div>
                    </div>
                </div>
                
                <!-- Draw -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span><i class="bi bi-dash-circle text-warning me-1"></i> Draw</span>
                        <strong>${drawProb}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-warning" style="width: ${drawProb}%">
                            ${drawProb}%
                        </div>
                    </div>
                </div>
                
                <!-- Away Win -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span><i class="bi bi-airplane-fill text-danger me-1"></i> Away Win</span>
                        <strong>${awayProb}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-danger" style="width: ${awayProb}%">
                            ${awayProb}%
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    return html;
}


/**
 * Generate Double Chance card HTML
 */
/**
 * Generate Double Chance card
 */
function generateDoubleChanceCard(doubleChance) {
    const prob1X = (doubleChance.probabilities['1X'] * 100).toFixed(1);
    const prob12 = (doubleChance.probabilities['12'] * 100).toFixed(1);
    const probX2 = (doubleChance.probabilities['X2'] * 100).toFixed(1);

    const certainty = (doubleChance.certainty * 100).toFixed(1);
    const certaintyLevel = doubleChance.certainty_level;

    let html = `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="bi bi-shield-check me-2"></i>
                    Double Chance
                    <span class="badge bg-light text-dark fs-6 ms-2">
                        ${doubleChance.prediction}
                    </span>
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <h6>Best Option: <strong>${doubleChance.prediction}</strong></h6>
                    <span class="badge bg-secondary">Certainty: ${certainty}%</span>
                    <span class="badge bg-info ms-2">${certaintyLevel}</span>
                </div>
                
                <h6 class="mb-3">Double Chance Options:</h6>
                
                <!-- 1X (Home or Draw) -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span>
                            <i class="bi bi-1-circle me-1"></i>
                            1X (Home Win or Draw)
                        </span>
                        <strong>${prob1X}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar ${doubleChance.prediction === '1X' ? 'bg-success' : 'bg-secondary'}" 
                             style="width: ${prob1X}%">
                            ${prob1X}%
                        </div>
                    </div>
                </div>
                
                <!-- 12 (Home or Away) -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span>
                            <i class="bi bi-intersect me-1"></i>
                            12 (Home Win or Away Win)
                        </span>
                        <strong>${prob12}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar ${doubleChance.prediction === '12' ? 'bg-success' : 'bg-secondary'}" 
                             style="width: ${prob12}%">
                            ${prob12}%
                        </div>
                    </div>
                </div>
                
                <!-- X2 (Draw or Away) -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span>
                            <i class="bi bi-2-circle me-1"></i>
                            X2 (Draw or Away Win)
                        </span>
                        <strong>${probX2}%</strong>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar ${doubleChance.prediction === 'X2' ? 'bg-success' : 'bg-secondary'}" 
                             style="width: ${probX2}%">
                            ${probX2}%
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-light mt-3 mb-0">
                    <small>
                        <i class="bi bi-info-circle me-1"></i>
                        Double Chance betting covers two of the three possible outcomes, providing safer odds.
                    </small>
                </div>
            </div>
        </div>
    `;

    return html;
}




/**
 * Generate Goals card HTML
 */
function generateGoalsCard(goals) {
    let html = `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <i class="bi bi-bullseye me-2"></i>
                    Goals Predictions
                </h5>
            </div>
            <div class="card-body">
    `;

    // Over/Under predictions
    ['over_0.5', 'over_1.5', 'over_2.5', 'over_3.5'].forEach(key => {
        if (goals[key]) {
            const data = goals[key];
            const threshold = key.replace('over_', '');
            const certainty = (data.certainty * 100).toFixed(1);  // Changed from confidence

            html += `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Over/Under ${threshold} Goals</h6>
                        <div>
                            <span class="badge ${data.prediction === 'Over' ? 'bg-success' : 'bg-danger'}">
                                ${data.prediction}
                            </span>
                            <span class="badge bg-secondary ms-2">${certainty}%</span>
                            <span class="badge bg-info ms-1">${data.certainty_level}</span>
                        </div>
                    </div>
                    ${generateProbabilityBar('Over', data.probability_over, data.prediction === 'Over')}
                </div>
            `;
        }
    });

    // BTTS
    if (goals.btts) {
        const btts = goals.btts;
        const certainty = (btts.certainty * 100).toFixed(1);  // Changed from confidence

        html += `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">Both Teams To Score (BTTS)</h6>
                    <div>
                        <span class="badge ${btts.prediction === 'Yes' ? 'bg-success' : 'bg-danger'}">
                            ${btts.prediction}
                        </span>
                        <span class="badge bg-secondary ms-2">${certainty}%</span>
                        <span class="badge bg-info ms-1">${btts.certainty_level}</span>
                    </div>
                </div>
                ${generateProbabilityBar('Yes', btts.probability_yes, btts.prediction === 'Yes')}
            </div>
        `;
    }

    html += `
            </div>
        </div>
    `;

    return html;
}



/**
 * Generate Cards prediction HTML
 */
function generateCardsCard(cards) {
    let html = `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="bi bi-file-earmark-text-fill me-2"></i>
                    Cards Predictions
                </h5>
            </div>
            <div class="card-body">
    `;

    // Total match cards with bars
    if (cards.total_match) {
        html += '<h6 class="mb-3">Total Match Cards (Both Teams)</h6><div class="row mb-4">';
        Object.keys(cards.total_match).forEach(key => {
            const threshold = key.replace('over_', '');
            const data = cards.total_match[key];
            const certainty = (data.certainty * 100).toFixed(1);  // Changed from confidence

            html += `
                <div class="col-md-4 mb-3">
                    <div class="border rounded p-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">O/U ${threshold}</h6>
                            <span class="badge bg-secondary">${certainty}%</span>
                        </div>
                        <div class="mb-2">
                            <span class="badge bg-info">${data.certainty_level}</span>
                        </div>
                        ${generateProbabilityBar('Over', data.probability_over, data.prediction === 'Over')}
                        <div class="mt-2">
                            <span class="badge ${data.prediction === 'Over' ? 'bg-success' : 'bg-danger'}">
                                ${data.prediction}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }

    // Home team cards
    if (cards.home_team) {
        html += `
            <h6 class="mb-2">
                <i class="bi bi-house-fill me-1"></i>
                ${cards.home_team.team_name} Cards
            </h6>
            <div class="row mb-4">
        `;
        ['over_1.5', 'over_2.5'].forEach(key => {
            if (cards.home_team[key]) {
                const data = cards.home_team[key];
                const threshold = key.replace('over_', '');
                const certainty = (data.certainty * 100).toFixed(1);  // Changed from confidence

                html += `
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">O/U ${threshold}</h6>
                                <span class="badge bg-secondary">${certainty}%</span>
                            </div>
                            <div class="mb-2">
                                <span class="badge bg-info">${data.certainty_level}</span>
                            </div>
                            ${generateProbabilityBar('Over', data.probability_over, data.prediction === 'Over')}
                            <div class="mt-2">
                                <span class="badge ${data.prediction === 'Over' ? 'bg-success' : 'bg-danger'}">
                                    ${data.prediction}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        html += '</div>';
    }

    // Away team cards (same pattern)
    if (cards.away_team) {
        html += `
            <h6 class="mb-2">
                <i class="bi bi-airplane-fill me-1"></i>
                ${cards.away_team.team_name} Cards
            </h6>
            <div class="row">
        `;
        ['over_1.5', 'over_2.5'].forEach(key => {
            if (cards.away_team[key]) {
                const data = cards.away_team[key];
                const threshold = key.replace('over_', '');
                const certainty = (data.certainty * 100).toFixed(1);  // Changed from confidence

                html += `
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">O/U ${threshold}</h6>
                                <span class="badge bg-secondary">${certainty}%</span>
                            </div>
                            <div class="mb-2">
                                <span class="badge bg-info">${data.certainty_level}</span>
                            </div>
                            ${generateProbabilityBar('Over', data.probability_over, data.prediction === 'Over')}
                            <div class="mt-2">
                                <span class="badge ${data.prediction === 'Over' ? 'bg-success' : 'bg-danger'}">
                                    ${data.prediction}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        html += '</div>';
    }

    html += `
            </div>
        </div>
    `;

    return html;
}



/**
 * Helper: Generate probability column
 */
function generateProbabilityColumn(label, probability, isWinner) {
    const percent = (probability * 100).toFixed(1);
    const badgeClass = isWinner ? 'bg-success' : 'bg-secondary';

    return `
        <div class="col">
            <h6>${label}</h6>
            <div class="progress" style="height: 25px;">
                <div class="progress-bar ${badgeClass}" 
                     style="width: ${percent}%"
                     role="progressbar">
                    ${percent}%
                </div>
            </div>
        </div>
    `;
}

/**
 * Helper: Generate probability bar
 */
function generateProbabilityBar(label, probability, isPredicted) {
    const percent = (probability * 100).toFixed(1);
    const badgeClass = isPredicted ? 'bg-success' : 'bg-secondary';

    return `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span>${label}</span>
            <strong>${percent}%</strong>
        </div>
        <div class="progress" style="height: 8px;">
            <div class="progress-bar ${badgeClass}" style="width: ${percent}%"></div>
        </div>
    `;
}

/**
 * Helper: Generate small prediction card
 */
function generateSmallPredictionCard(label, data) {
    const isOver = data.prediction === 'Over';
    const prob = isOver ? data.probability_over : data.probability_under;
    const percent = (prob * 100).toFixed(1);

    return `
        <div class="border rounded p-2 text-center">
            <small class="text-muted">${label}</small>
            <div class="fw-bold ${isOver ? 'text-success' : 'text-danger'}">
                ${data.prediction} (${percent}%)
            </div>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(message) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
        </div>
    `;
    container.style.display = 'block';
    document.getElementById('welcomeMessage').style.display = 'none';
}

/**
 * Generate collapsible raw JSON card
 */
function generateRawJsonCard(data) {
    // Pretty print JSON
    const jsonString = JSON.stringify(data, null, 2);

    return `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0">
                    <button class="btn btn-link text-white text-decoration-none p-0 w-100 text-start" 
                            type="button" 
                            data-bs-toggle="collapse" 
                            data-bs-target="#rawJsonCollapse">
                        <i class="bi bi-code-square me-2"></i>
                        Raw API Response
                        <i class="bi bi-chevron-down float-end"></i>
                    </button>
                </h5>
            </div>
            <div class="collapse" id="rawJsonCollapse">
                <div class="card-body bg-dark text-light">
                    <div class="mb-2">
                        <button class="btn btn-sm btn-outline-light" onclick="copyJsonToClipboard()">
                            <i class="bi bi-clipboard me-1"></i>
                            Copy JSON
                        </button>
                    </div>
                    <pre class="mb-0" style="font-size: 0.85em; max-height: 500px; overflow-y: auto;"><code id="rawJsonContent">${escapeHtml(jsonString)}</code></pre>
                </div>
            </div>
        </div>
    `;
}

/**
 * Escape HTML for JSON display
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Copy JSON to clipboard
 */
function copyJsonToClipboard() {
    const jsonContent = document.getElementById('rawJsonContent').textContent;
    navigator.clipboard.writeText(jsonContent).then(() => {
        // Show success message
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check me-1"></i> Copied!';
        btn.classList.remove('btn-outline-light');
        btn.classList.add('btn-success');

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-light');
        }, 2000);
    });
}


/**
 * Admin Controls - Update Data
 */
document.getElementById('updateDataBtn').addEventListener('click', async function () {
    const btn = this;
    const statusDiv = document.getElementById('updateDataStatus');

    // Disable button
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Updating...';

    try {
        const response = await fetch(`${API_BASE}/update_data_api.php`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    Data update started! Check logs for progress.
                    <br><small>Started at: ${data.started_at}</small>
                </div>
            `;

            // Re-enable after 3 minutes
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Update Match Data';
            }, 180000);
        } else {
            throw new Error(data.error || 'Update failed');
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Error: ${error.message}
            </div>
        `;
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Update Match Data';
    }
});

/**
 * Admin Controls - Retrain Models
 */
document.getElementById('retrainBtn').addEventListener('click', async function () {
    const btn = this;
    const statusDiv = document.getElementById('retrainStatus');

    // Confirm action
    if (!confirm('Retrain all models? This will take 3-5 minutes.')) {
        return;
    }

    // Disable button
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Training...';

    try {
        const response = await fetch(`${API_BASE}/retrain_api.php`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    Model retraining started!
                    <br><small>Started at: ${data.started_at}</small>
                    <br><small>Training: ${data.scripts.join(', ')}</small>
                </div>
            `;

            // Re-enable after 5 minutes
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Retrain Models';
                statusDiv.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle-fill me-2"></i>
                        Training complete! Models updated.
                    </div>
                `;
            }, 300000);
        } else {
            throw new Error(data.error || 'Training failed');
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Error: ${error.message}
            </div>
        `;
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Retrain Models';
    }
});
