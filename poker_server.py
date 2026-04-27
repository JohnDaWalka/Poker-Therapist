"""
Poker Training Server - Flask application for interactive poker training.
Provides API endpoints for hand evaluation and board comparison.
"""

import logging

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from poker_engine import (
    Card, PokerGame, Deck, Rank, Suit
)
from advanced_tools import (
    HandRange, EquityCalculator, GTOTrainer, HandHistoryParser
)
from equity_sim import range_vs_range, parse_range, multi_way_equity
from statistics_tracker import stats_tracker, multiplayer_manager
from training_scenarios import ScenarioGenerator, ScenarioType
import random

app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')
CORS(app)

logger = logging.getLogger(__name__)

# Store training sessions
training_sessions = {}


@app.route('/')
def index():
    """Serve the main training interface"""
    return render_template('index.html')


@app.route('/advanced')
def advanced():
    """Serve the advanced tools interface"""
    return render_template('advanced.html')


@app.route('/hud')
def hud():
    """Serve the HUD overlay"""
    return render_template('hud.html')


@app.route('/api/deck', methods=['GET'])
def get_deck():
    """Get all cards in a deck"""
    deck = Deck()
    return jsonify({
        'cards': [str(card) for card in deck.cards]
    })


@app.route('/api/random-cards', methods=['GET'])
def random_cards():
    """Get random cards for training"""
    count = int(request.args.get('count', 2))
    game_type = request.args.get('type', 'holdem')
    
    deck = Deck()
    cards = random.sample(deck.cards, min(count, 52))
    
    return jsonify({
        'cards': [str(card) for card in cards]
    })


@app.route('/api/evaluate', methods=['POST'])
def evaluate_hand():
    """Evaluate a poker hand"""
    data = request.json
    game_type = data.get('game_type', 'holdem')
    
    try:
        # Parse hole cards
        hole_cards_str = data.get('hole_cards', [])
        hole_cards = [Card.from_string(c) for c in hole_cards_str]
        
        # Parse board cards
        board_str = data.get('board', [])
        board = [Card.from_string(c) for c in board_str]
        
        # Evaluate based on game type
        if game_type == 'holdem':
            result = PokerGame.evaluate_holdem_hand(hole_cards, board)
        elif game_type == 'omaha':
            result = PokerGame.evaluate_omaha_hand(hole_cards, board)
        else:
            return jsonify({'error': 'Invalid game type'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/compare-boards', methods=['POST'])
def compare_boards():
    """Compare the same hand across different boards"""
    data = request.json
    game_type = data.get('game_type', 'holdem')
    
    try:
        # Parse hole cards
        hole_cards_str = data.get('hole_cards', [])
        hole_cards = [Card.from_string(c) for c in hole_cards_str]
        
        # Parse multiple boards
        boards_str = data.get('boards', [])
        boards = []
        for board_str in boards_str:
            board = [Card.from_string(c) for c in board_str]
            boards.append(board)
        
        # Compare boards
        results = PokerGame.compare_boards(hole_cards, boards, game_type)
        
        return jsonify({
            'results': results,
            'game_type': game_type
        })
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/training/new', methods=['POST'])
def new_training_session():
    """Create a new training session"""
    data = request.json
    game_type = data.get('game_type', 'holdem')
    difficulty = data.get('difficulty', 'medium')
    
    session_id = str(random.randint(1000, 9999))
    
    # Generate random scenario
    deck = Deck()
    random.shuffle(deck.cards)
    
    if game_type == 'holdem':
        hole_cards = deck.cards[:2]
        board = deck.cards[2:7]
    else:  # omaha
        hole_cards = deck.cards[:4]
        board = deck.cards[4:9]
    
    training_sessions[session_id] = {
        'game_type': game_type,
        'hole_cards': [str(c) for c in hole_cards],
        'board': [str(c) for c in board],
        'difficulty': difficulty
    }
    
    return jsonify({
        'session_id': session_id,
        'hole_cards': training_sessions[session_id]['hole_cards'],
        'board': training_sessions[session_id]['board'],
        'game_type': game_type
    })


@app.route('/api/training/<session_id>/check', methods=['POST'])
def check_training_answer(session_id):
    """Check a training answer"""
    if session_id not in training_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.json
    user_answer = data.get('answer', '')
    
    session = training_sessions[session_id]
    hole_cards = [Card.from_string(c) for c in session['hole_cards']]
    board = [Card.from_string(c) for c in session['board']]
    
    if session['game_type'] == 'holdem':
        result = PokerGame.evaluate_holdem_hand(hole_cards, board)
    else:
        result = PokerGame.evaluate_omaha_hand(hole_cards, board)
    
    correct = result['hand_rank'].lower() == user_answer.lower()
    
    return jsonify({
        'correct': correct,
        'correct_answer': result['hand_rank'],
        'best_hand': result['best_hand'],
        'user_answer': user_answer
    })


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)


# Advanced features endpoints

@app.route('/api/range/matrix', methods=['GET'])
def get_range_matrix():
    """Get empty hand range matrix"""
    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    matrix = []
    
    for i, r1 in enumerate(ranks):
        row = []
        for j, r2 in enumerate(ranks):
            if i == j:  # Pair
                hand = f"{r1}{r2}"
            elif i < j:  # Suited (upper triangle)
                hand = f"{r1}{r2}s"
            else:  # Offsuit (lower triangle)
                hand = f"{r2}{r1}o"
            row.append(hand)
        matrix.append(row)
    
    return jsonify({'matrix': matrix, 'ranks': ranks})


@app.route('/api/range/preset', methods=['POST'])
def add_preset_range():
    """Add a preset range"""
    data = request.json
    range_type = data.get('range_type', 'all_pairs')
    
    hand_range = HandRange()
    hand_range.add_preset_range(range_type)
    
    return jsonify({
        'range_type': range_type,
        'hands': list(hand_range.hands),
        'count': len(hand_range.hands)
    })


@app.route('/api/equity/calculate', methods=['POST'])
def calculate_equity():
    """Calculate equity using Monte Carlo simulation"""
    data = request.json
    
    try:
        # Parse hero hand
        hero_cards_str = data.get('hero_hand', [])
        hero_hand = [Card.from_string(c) for c in hero_cards_str]
        
        # Parse board (optional)
        board_str = data.get('board', [])
        board = [Card.from_string(c) for c in board_str] if board_str else []
        
        # Parse villain range
        villain_hands = data.get('villain_range', [])
        villain_range = HandRange()
        for hand in villain_hands:
            villain_range.add_hand(hand)
        
        # Number of simulations
        num_sims = data.get('simulations', 10000)
        game_type = data.get('game_type', 'holdem')
        
        # Calculate equity
        result = EquityCalculator.calculate_equity(
            hero_hand, villain_range, board, num_sims, game_type
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/equity/range-vs-range', methods=['POST'])
def equity_range_vs_range():
    """Fast range vs range equity calculation"""
    data = request.json
    
    try:
        range1 = data.get('range1', 'AA')
        range2 = data.get('range2', 'KK')
        board = data.get('board', [])
        trials = data.get('trials', 10000)
        
        result = range_vs_range(range1, range2, board if board else None, trials)
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/gto/scenarios', methods=['GET'])
def list_gto_scenarios():
    """List available GTO scenarios"""
    scenarios = GTOTrainer.list_scenarios()
    return jsonify({'scenarios': scenarios})


@app.route('/api/gto/scenario/<scenario_name>', methods=['GET'])
def get_gto_scenario(scenario_name):
    """Get GTO recommendations for a scenario"""
    result = GTOTrainer.get_scenario(scenario_name)
    return jsonify(result)


@app.route('/api/gto/check-hand', methods=['POST'])
def check_gto_hand():
    """Check if a hand should be opened in a scenario"""
    data = request.json
    hand = data.get('hand', '')
    scenario = data.get('scenario', '')
    
    result = GTOTrainer.should_open(hand, scenario)
    return jsonify(result)


@app.route('/api/handhistory/parse', methods=['POST'])
def parse_hand_history():
    """Parse a hand history file"""
    data = request.json
    hand_text = data.get('hand_text', '')
    parser_type = data.get('parser', 'pokerstars')  # pokerstars or gg
    
    try:
        if parser_type == 'pokerstars':
            result = HandHistoryParser.parse_pokerstars(hand_text)
        else:
            result = {'error': 'Only PokerStars parser implemented currently'}
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/handhistory/stats', methods=['POST'])
def calculate_hand_stats():
    """Calculate stats from multiple hand histories"""
    data = request.json
    hand_histories = data.get('hand_histories', [])
    
    try:
        stats = HandHistoryParser.calculate_stats(hand_histories)
        return jsonify(stats)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


# Multi-way equity calculator endpoints
@app.route('/api/equity/multi-way', methods=['POST'])
def equity_multi_way():
    """Calculate equity for 3+ players"""
    data = request.json
    
    try:
        ranges = data.get('ranges', [])
        board = data.get('board', [])
        trials = data.get('trials', 10000)
        
        if len(ranges) < 2:
            return jsonify({'error': 'Need at least 2 ranges'}), 400
        
        result = multi_way_equity(ranges, board if board else None, trials)
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


# New poker variant endpoints
@app.route('/api/evaluate/stud', methods=['POST'])
def evaluate_stud():
    """Evaluate a 7-Card Stud hand"""
    data = request.json
    
    try:
        hole_cards_str = data.get('hole_cards', [])
        hole_cards = [Card.from_string(c) for c in hole_cards_str]
        
        if len(hole_cards) != 7:
            return jsonify({'error': '7-Card Stud requires exactly 7 cards'}), 400
        
        result = PokerGame.evaluate_stud_hand(hole_cards)
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/evaluate/razz', methods=['POST'])
def evaluate_razz():
    """Evaluate a Razz (lowball) hand"""
    data = request.json
    
    try:
        hole_cards_str = data.get('hole_cards', [])
        hole_cards = [Card.from_string(c) for c in hole_cards_str]
        
        if len(hole_cards) != 7:
            return jsonify({'error': 'Razz requires exactly 7 cards'}), 400
        
        result = PokerGame.evaluate_razz_hand(hole_cards)
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


# Training scenarios endpoints
@app.route('/api/scenarios/list', methods=['GET'])
def list_scenarios():
    """List available training scenario types"""
    scenarios = ScenarioGenerator.list_scenario_types()
    return jsonify({'scenarios': scenarios})


@app.route('/api/scenarios/generate', methods=['POST'])
def generate_scenario():
    """Generate a training scenario"""
    data = request.json
    scenario_type_str = data.get('scenario_type', None)
    
    try:
        scenario_type = None
        if scenario_type_str:
            scenario_type = ScenarioType(scenario_type_str)
        
        scenario = ScenarioGenerator.generate_scenario(scenario_type)
        return jsonify(scenario.to_dict())
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/scenarios/check-answer', methods=['POST'])
def check_scenario_answer():
    """Check answer to a scenario question"""
    data = request.json
    
    try:
        question_idx = data.get('question_index', 0)
        user_answer = data.get('answer', -1)
        correct_answer = data.get('correct_answer', -1)
        user_id = data.get('user_id', 'anonymous')
        
        is_correct = user_answer == correct_answer
        
        # Record the result
        stats_tracker.record_gto_decision(user_id, 'scenario_training', is_correct)
        
        return jsonify({
            'correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer
        })
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


# Statistics tracking endpoints
@app.route('/api/stats/user/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get statistics for a user"""
    try:
        report = stats_tracker.get_user_report(user_id)
        return jsonify(report)
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/stats/global', methods=['GET'])
def get_global_stats():
    """Get global statistics"""
    try:
        stats = stats_tracker.get_global_stats()
        return jsonify(stats)
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/stats/record-session', methods=['POST'])
def record_training_session():
    """Record a training session"""
    data = request.json
    
    try:
        user_id = data.get('user_id', 'anonymous')
        session_data = {
            'game_type': data.get('game_type', 'holdem'),
            'correct': data.get('correct', False),
            'hand_type': data.get('hand_type', 'unknown'),
            'duration': data.get('duration', 0)
        }
        
        stats_tracker.record_training_session(user_id, session_data)
        return jsonify({'success': True})
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/stats/record-equity', methods=['POST'])
def record_equity_calc():
    """Record an equity calculation"""
    data = request.json
    
    try:
        user_id = data.get('user_id', 'anonymous')
        game_type = data.get('game_type', 'holdem')
        players = data.get('players', 2)
        
        stats_tracker.record_equity_calculation(user_id, game_type, players)
        return jsonify({'success': True})
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


# Multiplayer session endpoints
@app.route('/api/multiplayer/create', methods=['POST'])
def create_multiplayer_session():
    """Create a multiplayer training session"""
    data = request.json
    
    try:
        creator_id = data.get('user_id', 'anonymous')
        session_type = data.get('session_type', 'equity')
        max_players = data.get('max_players', 4)
        
        session_id = multiplayer_manager.create_session(creator_id, session_type, max_players)
        return jsonify({'session_id': session_id, 'success': True})
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/join', methods=['POST'])
def join_multiplayer_session():
    """Join a multiplayer training session"""
    data = request.json
    
    try:
        session_id = data.get('session_id', '')
        player_id = data.get('user_id', 'anonymous')
        
        result = multiplayer_manager.join_session(session_id, player_id)
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/start/<session_id>', methods=['POST'])
def start_multiplayer_session(session_id):
    """Start a multiplayer session"""
    try:
        result = multiplayer_manager.start_session(session_id)
        return jsonify(result)
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/session/<session_id>', methods=['GET'])
def get_multiplayer_session(session_id):
    """Get multiplayer session details"""
    try:
        session = multiplayer_manager.get_session(session_id)
        return jsonify(session)
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/list', methods=['GET'])
def list_multiplayer_sessions():
    """List available multiplayer sessions"""
    try:
        sessions = multiplayer_manager.list_available_sessions()
        return jsonify({'sessions': sessions})
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/record-result', methods=['POST'])
def record_multiplayer_result():
    """Record a result in a multiplayer session"""
    data = request.json
    
    try:
        session_id = data.get('session_id', '')
        player_id = data.get('user_id', 'anonymous')
        result = data.get('result', {})
        
        response = multiplayer_manager.record_result(session_id, player_id, result)
        return jsonify(response)
    
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/api/multiplayer/end/<session_id>', methods=['POST'])
def end_multiplayer_session(session_id):
    """End a multiplayer session"""
    try:
        result = multiplayer_manager.end_session(session_id)
        return jsonify(result)
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({'error': 'An internal error occurred'}), 500


if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting Poker Training Server...")
    print("Visit http://localhost:5000 to start training!")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=5000)
