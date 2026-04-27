"""
Simple Web UI for Poker Equity Calculation
A minimal, focused interface for range vs range equity calculations
"""

import logging
import os

from flask import Flask, request, jsonify, render_template_string
from equity_sim import range_vs_range

app = Flask(__name__)

logger = logging.getLogger(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <title>Poker Equity Calculator</title>
  <style>
    body { 
      font-family: 'Segoe UI', sans-serif; 
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
      color: #eee; 
      text-align: center; 
      padding: 50px;
      min-height: 100vh;
    }
    
    h1 {
      font-size: 3em;
      margin-bottom: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .subtitle {
      font-size: 1.2em;
      opacity: 0.8;
      margin-bottom: 40px;
    }
    
    input, button { 
      padding: 15px 20px; 
      font-size: 18px; 
      margin: 10px;
      border-radius: 8px;
      border: none;
    }
    
    input {
      background: #fff;
      color: #333;
      width: 300px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    input::placeholder {
      color: #999;
    }
    
    button {
      background: #4CAF50;
      color: white;
      cursor: pointer;
      font-weight: bold;
      transition: all 0.3s;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    button:hover {
      background: #45a049;
      transform: translateY(-2px);
      box-shadow: 0 6px 8px rgba(0,0,0,0.4);
    }
    
    .hand { 
      font-family: monospace; 
      background: rgba(255,255,255,0.1);
      backdrop-filter: blur(10px);
      padding: 30px; 
      border-radius: 15px; 
      display: inline-block;
      box-shadow: 0 8px 16px rgba(0,0,0,0.3);
      border: 2px solid rgba(255,255,255,0.2);
    }
    
    .board-input {
      margin-top: 15px;
      opacity: 0.9;
    }
    
    .result { 
      margin-top: 30px; 
      font-size: 20px;
      background: rgba(255,255,255,0.95);
      color: #333;
      padding: 30px;
      border-radius: 15px;
      display: none;
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
      box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    
    .result.show {
      display: block;
    }
    
    .equity-bar-container {
      display: flex;
      height: 50px;
      border-radius: 10px;
      overflow: hidden;
      margin: 20px 0;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .equity-bar {
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 18px;
      transition: all 0.5s ease;
    }
    
    .equity-bar.hero {
      background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
    }
    
    .equity-bar.villain {
      background: linear-gradient(90deg, #f44336 0%, #ef5350 100%);
    }
    
    .stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
      margin-top: 20px;
    }
    
    .stat-box {
      background: #f5f5f5;
      padding: 15px;
      border-radius: 10px;
    }
    
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #4CAF50;
    }
    
    .stat-label {
      font-size: 14px;
      color: #666;
      margin-top: 5px;
    }
    
    .help-text {
      margin-top: 20px;
      font-size: 14px;
      opacity: 0.7;
    }
    
    .examples {
      margin-top: 30px;
      background: rgba(255,255,255,0.1);
      padding: 20px;
      border-radius: 10px;
      display: inline-block;
    }
    
    .examples h3 {
      margin-bottom: 10px;
    }
    
    .example-item {
      font-family: monospace;
      margin: 5px 0;
      font-size: 14px;
    }
    
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #4CAF50;
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .advanced-link {
      margin-top: 30px;
    }
    
    .advanced-link a {
      color: #4CAF50;
      text-decoration: none;
      font-size: 16px;
      padding: 10px 20px;
      border: 2px solid #4CAF50;
      border-radius: 8px;
      display: inline-block;
      transition: all 0.3s;
    }
    
    .advanced-link a:hover {
      background: #4CAF50;
      color: white;
    }
  </style>
</head>
<body>
  <h1>🃏 Poker Equity Calculator</h1>
  <p class="subtitle">Calculate your equity vs any range in real-time</p>
  
  <div class="hand">
    <div>
      <input type="text" id="myhand" placeholder="Your hand: AhKh or AKs" />
    </div>
    <div>
      <input type="text" id="range" placeholder="Villain range: QQ, AKo, JTs" />
    </div>
    <div class="board-input">
      <input type="text" id="board" placeholder="Board (optional): As Kh 7d" />
    </div>
    <div>
      <button onclick="run()">Calculate Equity</button>
    </div>
    <p class="help-text">
      Examples: AA, KK+, AKs, AKo, JTs, 77-99<br>
      Board format: As Kh Qd Jc Ts
    </p>
  </div>
  
  <div class="result" id="out"></div>
  
  <div class="examples">
    <h3>Quick Examples:</h3>
    <div class="example-item">AA vs KK → ~82% equity</div>
    <div class="example-item">AKs vs QQ → ~45% equity</div>
    <div class="example-item">JJ vs AKo → ~55% equity</div>
  </div>
  
  <div class="advanced-link">
    <a href="/advanced">Open Advanced Tools →</a>
  </div>

  <script>
    async function run() {
      const my = document.getElementById("myhand").value.trim();
      const rng = document.getElementById("range").value.trim();
      const board = document.getElementById("board").value.trim();
      const outDiv = document.getElementById("out");
      
      if (!my || !rng) {
        alert("Please enter both your hand and villain's range");
        return;
      }
      
      // Show loading state
      outDiv.className = "result show";
      outDiv.innerHTML = '<div class="loading"></div><p>Calculating equity...</p>';
      
      try {
        const r = await fetch("/equity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            hand: my, 
            range: rng,
            board: board ? board.split(/\\s+/) : []
          })
        });
        
        const json = await r.json();
        
        if (json.error) {
          outDiv.innerHTML = `<p style="color: #f44336;"><b>Error:</b> ${json.error}</p>`;
          return;
        }
        
        const heroEq = (json.hand1_equity || 0).toFixed(1);
        const villainEq = (json.hand2_equity || 0).toFixed(1);
        
        outDiv.innerHTML = `
          <h2>Equity Results</h2>
          <div class="equity-bar-container">
            <div class="equity-bar hero" style="width: ${heroEq}%">
              ${heroEq}%
            </div>
            <div class="equity-bar villain" style="width: ${villainEq}%">
              ${villainEq}%
            </div>
          </div>
          
          <div class="stats">
            <div class="stat-box">
              <div class="stat-value">${json.hand1_wins || 0}</div>
              <div class="stat-label">Your Wins</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">${json.hand2_wins || 0}</div>
              <div class="stat-label">Villain Wins</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">${json.ties || 0}</div>
              <div class="stat-label">Ties</div>
            </div>
          </div>
          
          <p style="margin-top: 20px; color: #666;">
            <small>${json.total_trials || json.trials || 10000} Monte Carlo simulations</small>
          </p>
        `;
      } catch (error) {
        outDiv.innerHTML = `<p style="color: #f44336;"><b>Error:</b> ${error.message}</p>`;
      }
    }
    
    // Allow Enter key to calculate
    document.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        run();
      }
    });
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    """Serve the simple equity calculator UI"""
    return render_template_string(HTML)


@app.route("/equity", methods=["POST"])
def calc():
    """Calculate equity endpoint"""
    try:
        data = request.json
        hand = data.get("hand", "")
        villain_range = data.get("range", "")
        board = data.get("board", [])
        
        # Calculate equity using our range_vs_range function
        result = range_vs_range(
            hand, 
            villain_range, 
            board if board else None, 
            trials=10000
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error in equity calculation")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route("/advanced")
def advanced():
    """Redirect to advanced tools"""
    from flask import redirect
    return redirect("/templates/advanced.html")


if __name__ == "__main__":
    print("Starting Simple Poker Equity Calculator...")
    print("Visit http://localhost:5001 for the equity calculator")
    print("Visit http://localhost:5001/advanced for advanced tools")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=5001)
