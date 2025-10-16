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
    return `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <i class="bi bi-trophy-fill me-2"></i>
                    Match Result (1X2)
                </h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    ${generateProbabilityColumn('Home Win', matchResult.probabilities.home_win, matchResult.prediction === 'Home Win')}
                    ${generateProbabilityColumn('Draw', matchResult.probabilities.draw, matchResult.prediction === 'Draw')}
                    ${generateProbabilityColumn('Away Win', matchResult.probabilities.away_win, matchResult.prediction === 'Away Win')}
                </div>
                <div class="mt-3 text-center">
                    <span class="badge bg-success fs-6">
                        Prediction: ${matchResult.prediction}
                    </span>
                    <span class="badge bg-secondary fs-6 ms-2">
                        Confidence: ${(matchResult.confidence * 100).toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate Double Chance card HTML
 */
function generateDoubleChanceCard(doubleChance) {
    return `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="bi bi-diagram-3-fill me-2"></i>
                    Double Chance
                </h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    ${generateProbabilityColumn('1X (Home/Draw)', doubleChance.probabilities['1X'], doubleChance.prediction === '1X')}
                    ${generateProbabilityColumn('12 (Home/Away)', doubleChance.probabilities['12'], doubleChance.prediction === '12')}
                    ${generateProbabilityColumn('X2 (Draw/Away)', doubleChance.probabilities['X2'], doubleChance.prediction === 'X2')}
                </div>
                <div class="mt-3 text-center">
                    <span class="badge bg-info fs-6">
                        Prediction: ${doubleChance.prediction}
                    </span>
                    <span class="badge bg-secondary fs-6 ms-2">
                        Confidence: ${(doubleChance.confidence * 100).toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `;
}


/**
 * Generate Goals card HTML
 */
function generateGoalsCard(goals) {
    let html = `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0">
                    <i class="bi bi-bullseye me-2"></i>
                    Goals Predictions
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
    `;

    // Over/Under predictions with confidence
    ['over_0.5', 'over_1.5', 'over_2.5', 'over_3.5'].forEach(key => {
        if (goals[key]) {
            const threshold = key.replace('over_', '');
            const confidence = (goals[key].confidence * 100).toFixed(1);
            html += `
                <div class="col-md-6 mb-3">
                    <div class="border rounded p-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">Over/Under ${threshold}</h6>
                            <span class="badge bg-secondary">${confidence}%</span>
                        </div>
                        ${generateProbabilityBar('Over', goals[key].probability_over, goals[key].prediction === 'Over')}
                        <div class="mt-2">
                            <span class="badge ${goals[key].prediction === 'Over' ? 'bg-success' : 'bg-danger'}">
                                ${goals[key].prediction}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }
    });

    // BTTS with confidence
    if (goals.btts) {
        const confidence = (goals.btts.confidence * 100).toFixed(1);
        html += `
            <div class="col-md-6 mb-3">
                <div class="border rounded p-3 bg-light">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Both Teams To Score</h6>
                        <span class="badge bg-secondary">${confidence}%</span>
                    </div>
                    ${generateProbabilityBar('Yes', goals.btts.probability_yes, goals.btts.prediction === 'Yes')}
                    <div class="mt-2">
                        <span class="badge ${goals.btts.prediction === 'Yes' ? 'bg-success' : 'bg-danger'}">
                            ${goals.btts.prediction}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    html += `
                </div>
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
            const confidence = (data.confidence * 100).toFixed(1);
            html += `
                <div class="col-md-4 mb-3">
                    <div class="border rounded p-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">O/U ${threshold}</h6>
                            <span class="badge bg-secondary">${confidence}%</span>
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

    // Home team cards with bars
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
                const confidence = (data.confidence * 100).toFixed(1);
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">O/U ${threshold}</h6>
                                <span class="badge bg-secondary">${confidence}%</span>
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

    // Away team cards with bars
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
                const confidence = (data.confidence * 100).toFixed(1);
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">O/U ${threshold}</h6>
                                <span class="badge bg-secondary">${confidence}%</span>
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
