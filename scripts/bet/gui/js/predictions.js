/**
 * Football Prediction System - Frontend JavaScript
 * Handles API calls, UI updates, and user interactions
 */

// API Configuration
const API_BASE = '/pyethone/scripts/bet/api';
const PREDICT_API = `${API_BASE}/predict_api.php`;
const RETRAIN_API = `${API_BASE}/retrain_api.php`;

// State management
let availableTeams = [];
let currentPredictions = null;

/**
 * Initialize application on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    loadTeams();
    setupEventListeners();
    loadRetrainingInfo();
});

/**
 * Load available teams from API
 */
async function loadTeams() {
    try {
        const response = await fetch(`${PREDICT_API}?action=teams`);
        const data = await response.json();
        
        if (data.success) {
            availableTeams = data.teams;
            populateTeamDropdowns();
        } else {
            showError('Failed to load teams: ' + data.error);
        }
    } catch (error) {
        showError('Network error loading teams: ' + error.message);
    }
}

/**
 * Populate team dropdown menus
 */
function populateTeamDropdowns() {
    const homeSelect = document.getElementById('homeTeam');
    const awaySelect = document.getElementById('awayTeam');
    
    // Clear existing options (keep placeholder)
    homeSelect.innerHTML = '<option value="">-- Select Home Team --</option>';
    awaySelect.innerHTML = '<option value="">-- Select Away Team --</option>';
    
    // Add team options
    availableTeams.forEach(team => {
        const homeOption = document.createElement('option');
        homeOption.value = team.name;
        homeOption.textContent = `${team.name} (${team.short_name})`;
        homeSelect.appendChild(homeOption);
        
        const awayOption = document.createElement('option');
        awayOption.value = team.name;
        awayOption.textContent = `${team.name} (${team.short_name})`;
        awaySelect.appendChild(awayOption);
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Team selection change
    document.getElementById('homeTeam').addEventListener('change', validateSelection);
    document.getElementById('awayTeam').addEventListener('change', validateSelection);
    
    // Predict button
    document.getElementById('predictBtn').addEventListener('click', getPredictions);
    
    // Retrain button
    document.getElementById('retrainBtn').addEventListener('click', retrainModels);
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
}

/**
 * Validate team selection
 */
function validateSelection() {
    const homeTeam = document.getElementById('homeTeam').value;
    const awayTeam = document.getElementById('awayTeam').value;
    const predictBtn = document.getElementById('predictBtn');
    
    // Enable button only if both teams selected and different
    if (homeTeam && awayTeam && homeTeam !== awayTeam) {
        predictBtn.disabled = false;
    } else {
        predictBtn.disabled = true;
    }
    
    // Show error if same team selected
    if (homeTeam && awayTeam && homeTeam === awayTeam) {
        showError('Please select different teams');
    } else {
        hideError();
    }
}

/**
 * Get predictions from API
 */
async function getPredictions() {
    const homeTeam = document.getElementById('homeTeam').value;
    const awayTeam = document.getElementById('awayTeam').value;
    
    // Show loading
    showLoading();
    hideResults();
    hideError();
    
    try {
        const response = await fetch(PREDICT_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                home_team: homeTeam,
                away_team: awayTeam
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPredictions = data.data;
            displayPredictions();
        } else {
            showError('Prediction failed: ' + data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Display predictions in UI
 */
function displayPredictions() {
    const predictions = currentPredictions;
    
    // Update match header
    document.getElementById('homeTeamName').textContent = predictions.home_team;
    document.getElementById('awayTeamName').textContent = predictions.away_team;
    
    // 1X2 Tab
    display1X2Predictions(predictions['1x2']);
    
    // Combined outcomes
    displayCombinedOutcomes(predictions);
    
    // Goals predictions
    displayGoalsPredictions(predictions);
    
    // Cards predictions
    displayCardsPredictions(predictions);
    
    // Show results section
    showResults();
}

/**
 * Display 1X2 predictions
 */
function display1X2Predictions(data) {
    // Probabilities
    document.getElementById('homeWinProb').textContent = data.home_win_prob.toFixed(1) + '%';
    document.getElementById('drawProb').textContent = data.draw_prob.toFixed(1) + '%';
    document.getElementById('awayWinProb').textContent = data.away_win_prob.toFixed(1) + '%';
    
    // Odds
    document.getElementById('homeWinOdds').textContent = data.home_win_odds;
    document.getElementById('drawOdds').textContent = data.draw_odds;
    document.getElementById('awayWinOdds').textContent = data.away_win_odds;
    
    // Progress bars
    document.getElementById('homeWinProgress').style.width = data.home_win_prob + '%';
    document.getElementById('drawProgress').style.width = data.draw_prob + '%';
    document.getElementById('awayWinProgress').style.width = data.away_win_prob + '%';
    
    // Predicted outcome
    const outcomeMap = {
        'H': 'Home Win',
        'D': 'Draw',
        'A': 'Away Win'
    };
    document.getElementById('predictedOutcome').textContent = outcomeMap[data.predicted_outcome];
    
    // Confidence badge
    const confidence = data.confidence;
    const confidenceBadge = document.getElementById('confidenceBadge');
    
    if (confidence >= 65) {
        confidenceBadge.textContent = 'High confidence';
        confidenceBadge.style.background = 'rgba(40, 167, 69, 0.5)';
    } else if (confidence >= 50) {
        confidenceBadge.textContent = 'Medium confidence';
        confidenceBadge.style.background = 'rgba(255, 193, 7, 0.5)';
    } else {
        confidenceBadge.textContent = 'Low confidence';
        confidenceBadge.style.background = 'rgba(220, 53, 69, 0.5)';
    }
}

/**
 * Display combined outcomes
 */
function displayCombinedOutcomes(predictions) {
    // 1X
    document.getElementById('prob1X').textContent = predictions['1x'].probability.toFixed(1) + '%';
    document.getElementById('odds1X').textContent = predictions['1x'].odds;
    document.getElementById('verdict1X').textContent = predictions['1x'].prediction;
    
    // 12
    document.getElementById('prob12').textContent = predictions['12'].probability.toFixed(1) + '%';
    document.getElementById('odds12').textContent = predictions['12'].odds;
    document.getElementById('verdict12').textContent = predictions['12'].prediction;
    
    // X2
    document.getElementById('probX2').textContent = predictions['x2'].probability.toFixed(1) + '%';
    document.getElementById('oddsX2').textContent = predictions['x2'].odds;
    document.getElementById('verdictX2').textContent = predictions['x2'].prediction;
}

/**
 * Display goals predictions
 */
function displayGoalsPredictions(predictions) {
    const goalsMatch = predictions.goals_match;
    const goalsTeam = predictions.goals_team;
    
    // Match totals
    ['05', '15', '25'].forEach(threshold => {
        const data = goalsMatch[`over_${threshold}`];
        
        document.getElementById(`over${threshold}Prob`).textContent = data.over_prob.toFixed(1) + '%';
        document.getElementById(`under${threshold}Prob`).textContent = data.under_prob.toFixed(1) + '%';
        document.getElementById(`over${threshold}Odds`).textContent = data.over_odds;
        document.getElementById(`under${threshold}Odds`).textContent = data.under_odds;
        document.getElementById(`pred${threshold}`).textContent = '✓ ' + data.prediction;
    });
    
    // Team-specific goals
    document.getElementById('homeTeamGoals').textContent = predictions.home_team + ' Goals';
    document.getElementById('awayTeamGoals').textContent = predictions.away_team + ' Goals';
    
    ['05', '15', '25'].forEach(threshold => {
        const homeData = goalsTeam[`home_over_${threshold}`];
        const awayData = goalsTeam[`away_over_${threshold}`];
        
        document.getElementById(`homeOver${threshold}`).textContent = 
            `${homeData.probability.toFixed(1)}% (odds: ${homeData.odds})`;
        
        document.getElementById(`awayOver${threshold}`).textContent = 
            `${awayData.probability.toFixed(1)}% (odds: ${awayData.odds})`;
    });
}

/**
 * Display cards predictions
 */
function displayCardsPredictions(predictions) {
    const cards = predictions.cards;
    
    document.getElementById('totalCards').textContent = cards.total_cards;
    document.getElementById('homeCards').textContent = cards.home_cards;
    document.getElementById('awayCards').textContent = cards.away_cards;
    
    // Update team labels
    document.getElementById('homeTeamCards').textContent = predictions.home_team + ' Cards';
    document.getElementById('awayTeamCards').textContent = predictions.away_team + ' Cards';
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Remove active class from all tabs and panels
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    
    // Add active class to selected tab and panel
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

/**
 * Retrain models
 */
async function retrainModels() {
    const retrainBtn = document.getElementById('retrainBtn');
    const retrainStatus = document.getElementById('retrainStatus');
    
    // Confirm action
    if (!confirm('Retraining will take several minutes. Continue?')) {
        return;
    }
    
    // Disable button
    retrainBtn.disabled = true;
    retrainStatus.textContent = 'Retraining in progress...';
    retrainStatus.style.color = '#ffc107';
    
    try {
        const response = await fetch(RETRAIN_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'retrain'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            retrainStatus.textContent = 'Retraining completed successfully!';
            retrainStatus.style.color = '#28a745';
            
            setTimeout(() => {
                location.reload(); // Reload to use new models
            }, 2000);
        } else {
            retrainStatus.textContent = 'Retraining failed: ' + data.error;
            retrainStatus.style.color = '#dc3545';
            retrainBtn.disabled = false;
        }
    } catch (error) {
        retrainStatus.textContent = 'Network error: ' + error.message;
        retrainStatus.style.color = '#dc3545';
        retrainBtn.disabled = false;
    }
}

/**
 * Load retraining info
 */
async function loadRetrainingInfo() {
    try {
        const response = await fetch(RETRAIN_API);
        const data = await response.json();
        
        if (data.success && data.info.last_retrain) {
            document.getElementById('dataDate').textContent = data.info.last_retrain;
        }
    } catch (error) {
        console.error('Failed to load retraining info:', error);
    }
}

/**
 * UI Helper Functions
 */
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showResults() {
    document.getElementById('resultsSection').style.display = 'block';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

function showError(message) {
    const errorDisplay = document.getElementById('errorDisplay');
    errorDisplay.textContent = '⚠️ ' + message;
    errorDisplay.style.display = 'block';
}

function hideError() {
    document.getElementById('errorDisplay').style.display = 'none';
}
