// Advanced Poker Tools JavaScript

let selectedRange = new Set();
let currentScenario = null;

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Range Visualizer
async function initRangeMatrix() {
    const response = await fetch('/api/range/matrix');
    const data = await response.json();
    
    const matrix = data.matrix;
    const matrixDiv = document.getElementById('range-matrix');
    matrixDiv.innerHTML = '';
    
    matrix.forEach(row => {
        row.forEach(hand => {
            const cell = document.createElement('div');
            cell.className = 'range-cell';
            cell.textContent = hand;
            cell.onclick = () => toggleHand(hand, cell);
            
            // Add class for visual distinction
            if (hand.length === 2) {
                cell.classList.add('pair');
            } else if (hand.endsWith('s')) {
                cell.classList.add('suited');
            }
            
            matrixDiv.appendChild(cell);
        });
    });
}

function toggleHand(hand, cell) {
    if (selectedRange.has(hand)) {
        selectedRange.delete(hand);
        cell.classList.remove('selected');
    } else {
        selectedRange.add(hand);
        cell.classList.add('selected');
    }
    updateRangeSummary();
}

function updateRangeSummary() {
    const listDiv = document.getElementById('range-list');
    const countSpan = document.getElementById('range-count');
    
    listDiv.innerHTML = '';
    selectedRange.forEach(hand => {
        const tag = document.createElement('span');
        tag.className = 'range-tag';
        tag.textContent = hand;
        listDiv.appendChild(tag);
    });
    
    countSpan.textContent = selectedRange.size;
}

async function addPresetRange(rangeType) {
    const response = await fetch('/api/range/preset', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({range_type: rangeType})
    });
    
    const data = await response.json();
    data.hands.forEach(hand => {
        selectedRange.add(hand);
        
        // Update cell visual
        const cells = document.querySelectorAll('.range-cell');
        cells.forEach(cell => {
            if (cell.textContent === hand) {
                cell.classList.add('selected');
            }
        });
    });
    
    updateRangeSummary();
}

function clearRange() {
    selectedRange.clear();
    document.querySelectorAll('.range-cell').forEach(cell => {
        cell.classList.remove('selected');
    });
    updateRangeSummary();
}

// Equity Calculator
async function calculateEquity() {
    const range1 = document.getElementById('range1').value.trim();
    const range2 = document.getElementById('range2').value.trim();
    const board = document.getElementById('equity-board').value.trim();
    const simulations = parseInt(document.getElementById('simulations').value);
    
    const resultDiv = document.getElementById('equity-result');
    resultDiv.innerHTML = '<p>Calculating... (this may take a few seconds)</p>';
    
    try {
        const response = await fetch('/api/equity/range-vs-range', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                range1: range1,
                range2: range2,
                board: board ? board.split(/\s+/) : [],
                trials: simulations
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            return;
        }
        
        displayEquityResult(data);
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

function displayEquityResult(data) {
    const resultDiv = document.getElementById('equity-result');
    
    resultDiv.innerHTML = `
        <h3>Equity Results</h3>
        <div class="equity-chart">
            <div class="equity-bar player1" style="width: ${data.hand1_equity}%">
                ${data.hand1_equity}%
            </div>
            <div class="equity-bar player2" style="width: ${data.hand2_equity}%">
                ${data.hand2_equity}%
            </div>
        </div>
        
        <div class="equity-details">
            <div class="equity-stat">
                <div class="equity-stat-value">${data.range1}</div>
                <div class="equity-stat-label">Range 1</div>
            </div>
            <div class="equity-stat">
                <div class="equity-stat-value">${data.range2}</div>
                <div class="equity-stat-label">Range 2</div>
            </div>
            <div class="equity-stat">
                <div class="equity-stat-value">${data.hand1_wins}</div>
                <div class="equity-stat-label">Range 1 Wins</div>
            </div>
            <div class="equity-stat">
                <div class="equity-stat-value">${data.hand2_wins}</div>
                <div class="equity-stat-label">Range 2 Wins</div>
            </div>
            <div class="equity-stat">
                <div class="equity-stat-value">${data.ties}</div>
                <div class="equity-stat-label">Ties</div>
            </div>
            <div class="equity-stat">
                <div class="equity-stat-value">${data.total_trials}</div>
                <div class="equity-stat-label">Simulations</div>
            </div>
        </div>
    `;
}

// GTO Trainer
async function loadGTOScenario() {
    const scenario = document.getElementById('gto-scenario').value;
    if (!scenario) return;
    
    currentScenario = scenario;
    
    const response = await fetch(`/api/gto/scenario/${scenario}`);
    const data = await response.json();
    
    const infoDiv = document.getElementById('gto-info');
    infoDiv.className = 'show';
    infoDiv.innerHTML = `
        <h3>${scenario.replace(/_/g, ' ')}</h3>
        <p><strong>Open Size:</strong> ${data.open_size}</p>
        <p><strong>Open Frequency:</strong> ${data.open_frequency}</p>
        <p><strong>Number of Hands in Range:</strong> ${data.num_hands}</p>
        <details>
            <summary><strong>Opening Range:</strong></summary>
            <div style="margin-top: 10px;">
                ${data.range.map(h => `<span class="range-tag">${h}</span>`).join(' ')}
            </div>
        </details>
    `;
}

async function checkGTOHand() {
    const hand = document.getElementById('gto-hand').value.trim();
    const scenario = currentScenario;
    
    if (!scenario) {
        alert('Please select a scenario first');
        return;
    }
    
    const response = await fetch('/api/gto/check-hand', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({hand: hand, scenario: scenario})
    });
    
    const data = await response.json();
    const resultDiv = document.getElementById('gto-result');
    
    if (data.should_open) {
        resultDiv.className = 'correct';
        resultDiv.innerHTML = `
            <strong>✓ Correct!</strong> ${hand} should ${data.action} to ${data.open_size}bb in this spot.
        `;
    } else {
        resultDiv.className = 'incorrect';
        resultDiv.innerHTML = `
            <strong>✗ Incorrect.</strong> ${hand} should ${data.action} in this spot.
        `;
    }
}

// Hand History Parser
async function parseHandHistory() {
    const handText = document.getElementById('hand-history').value.trim();
    
    if (!handText) {
        alert('Please paste a hand history');
        return;
    }
    
    const response = await fetch('/api/handhistory/parse', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({hand_text: handText, parser: 'pokerstars'})
    });
    
    const data = await response.json();
    const resultDiv = document.getElementById('history-result');
    
    if (data.error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
    }
    
    resultDiv.innerHTML = `
        <h3>Parsed Hand Information</h3>
        <p><strong>Stakes:</strong> ${data.stakes || 'Unknown'}</p>
        <p><strong>Players:</strong> ${data.players.length}</p>
        <p><strong>Board:</strong> ${data.board.join(' ') || 'No board found'}</p>
        <details>
            <summary><strong>Actions (${data.actions.length}):</strong></summary>
            <div style="margin-top: 10px; font-family: monospace; font-size: 12px;">
                ${data.actions.map(a => `<div>${a}</div>`).join('')}
            </div>
        </details>
    `;
    
    // Show simplified stats
    const statsDiv = document.getElementById('stats-summary');
    statsDiv.style.display = 'block';
    
    // Simple demo stats (in production, would calculate from multiple hands)
    document.getElementById('stat-vpip').textContent = '23%';
    document.getElementById('stat-pfr').textContent = '18%';
    document.getElementById('stat-3bet').textContent = '7%';
    document.getElementById('stat-hands').textContent = '1';
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initRangeMatrix();
});
