"""
Tests for new poker features: multi-way equity, variants, scenarios, and statistics
"""

import sys
import os
import json
import tempfile
from poker_engine import Card, PokerGame, LowballEvaluator, Rank, Suit
from equity_sim import multi_way_equity, parse_range
from training_scenarios import ScenarioGenerator, ScenarioType
from statistics_tracker import StatisticsTracker, MultiplayerSessionManager


def test_multi_way_equity():
    """Test multi-way equity calculator for 3+ players"""
    print("Testing multi-way equity calculator...")
    
    # Test 3-way equity
    result = multi_way_equity(['AA', 'KK', 'QQ'], trials=1000)
    assert 'equities' in result, "Result should have equities"
    assert len(result['equities']) == 3, "Should have 3 players"
    assert result['players'] == 3, "Should report 3 players"
    
    # AA should have highest equity
    aa_equity = result['equities'][0]['equity']
    kk_equity = result['equities'][1]['equity']
    qq_equity = result['equities'][2]['equity']
    
    assert aa_equity > kk_equity, "AA should have higher equity than KK"
    assert kk_equity > qq_equity, "KK should have higher equity than QQ"
    
    print(f"✓ Multi-way equity test passed: AA={aa_equity}%, KK={kk_equity}%, QQ={qq_equity}%")
    
    # Test with board
    result = multi_way_equity(['AKs', 'QQ', 'JJ'], ['As', 'Kh', '7d'], trials=500)
    assert result['equities'][0]['equity'] > 70, "AKs should have high equity on AsKh7d"
    
    print("✓ Multi-way equity with board test passed")


def test_stud_evaluation():
    """Test 7-Card Stud hand evaluation"""
    print("\nTesting 7-Card Stud evaluation...")
    
    # Create a straight
    cards_str = ['As', 'Kh', 'Qd', 'Jc', 'Ts', '9h', '8d']
    cards = [Card.from_string(c) for c in cards_str]
    result = PokerGame.evaluate_stud_hand(cards)
    
    assert result['game_type'] == '7-Card Stud', "Should be Stud"
    assert result['hand_rank'] == 'Straight', "Should find straight"
    assert len(result['best_hand']) == 5, "Best hand should have 5 cards"
    
    print(f"✓ Stud evaluation test passed: {result['hand_rank']}")
    
    # Test that it raises error for wrong number of cards
    try:
        cards_str = ['As', 'Kh', 'Qd', 'Jc', 'Ts']
        cards = [Card.from_string(c) for c in cards_str]
        PokerGame.evaluate_stud_hand(cards)
        assert False, "Should raise error for 5 cards"
    except ValueError:
        print("✓ Stud error handling test passed")


def test_razz_evaluation():
    """Test Razz (lowball) hand evaluation"""
    print("\nTesting Razz evaluation...")
    
    # Create a low hand
    cards_str = ['As', '2h', '3d', '4c', '5s', 'Kh', 'Qd']
    cards = [Card.from_string(c) for c in cards_str]
    result = PokerGame.evaluate_razz_hand(cards)
    
    assert result['game_type'] == 'Razz', "Should be Razz"
    assert 'low' in result['hand_rank'].lower(), "Should be a low hand"
    assert len(result['best_hand']) == 5, "Best hand should have 5 cards"
    
    print(f"✓ Razz evaluation test passed: {result['hand_rank']}")
    
    # Test lowball comparison
    hand1 = [1, 2, 3, 4, 5]  # Wheel - best low hand
    hand2 = [1, 2, 3, 4, 6]
    comparison = LowballEvaluator.compare_lowball_hands(hand1, hand2)
    assert comparison == 1, "Wheel should beat 6-low"
    
    print("✓ Lowball comparison test passed")


def test_training_scenarios():
    """Test training scenario generation"""
    print("\nTesting training scenario generation...")
    
    # Test squeeze play scenario
    scenario = ScenarioGenerator.generate_squeeze_play()
    assert scenario.scenario_type == ScenarioType.SQUEEZE_PLAY
    assert 'hole_cards' in scenario.setup
    assert len(scenario.questions) > 0
    
    print(f"✓ Squeeze play scenario generated: {len(scenario.questions)} questions")
    
    # Test flush draw scenario
    scenario = ScenarioGenerator.generate_flush_draw()
    assert scenario.scenario_type == ScenarioType.FLUSH_DRAW
    assert 'board' in scenario.setup
    
    print(f"✓ Flush draw scenario generated")
    
    # Test random scenario generation
    scenario = ScenarioGenerator.generate_scenario()
    assert scenario is not None
    assert scenario.scenario_type in ScenarioType
    
    print(f"✓ Random scenario generated: {scenario.scenario_type.value}")
    
    # Test listing scenario types
    types = ScenarioGenerator.list_scenario_types()
    assert len(types) > 0
    assert 'squeeze_play' in types
    
    print(f"✓ Found {len(types)} scenario types")


def test_statistics_tracker():
    """Test statistics tracking functionality"""
    print("\nTesting statistics tracker...")
    
    # Create temporary tracker with cross-platform temp file
    fd, test_file = tempfile.mkstemp(suffix='.json')
    os.close(fd)  # Close the file descriptor
    
    try:
        tracker = StatisticsTracker(test_file)
        
        # Record training session
        tracker.record_training_session('test_user', {
            'game_type': 'holdem',
            'correct': True,
            'hand_type': 'flush',
            'duration': 30
        })
        
        # Record equity calculation
        tracker.record_equity_calculation('test_user', 'holdem', 2)
        
        # Record GTO decision
        tracker.record_gto_decision('test_user', 'BTN_vs_BB_15bb', True)
        
        # Get user report
        report = tracker.get_user_report('test_user')
        
        assert report['user_id'] == 'test_user'
        assert report['summary']['total_training_sessions'] == 1
        assert report['summary']['overall_accuracy'] == 100.0
        assert report['summary']['equity_calculations'] == 1
        assert report['gto_training']['correct_decisions'] == 1
        
        print(f"✓ Statistics tracking test passed: {report['summary']}")
        
        # Get global stats
        global_stats = tracker.get_global_stats()
        assert global_stats['total_users'] == 1
        
        print(f"✓ Global statistics test passed")
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


def test_multiplayer_sessions():
    """Test multiplayer session management"""
    print("\nTesting multiplayer session management...")
    
    manager = MultiplayerSessionManager()
    
    # Create session
    session_id = manager.create_session('player1', 'equity', max_players=3)
    assert session_id is not None
    assert session_id.startswith('mp_')
    
    print(f"✓ Created session: {session_id}")
    
    # Join session
    result = manager.join_session(session_id, 'player2')
    assert result['success'] is True
    
    print(f"✓ Player 2 joined session")
    
    # Get session
    session = manager.get_session(session_id)
    assert len(session['players']) == 2
    assert session['status'] == 'waiting'
    
    print(f"✓ Session has {len(session['players'])} players")
    
    # Start session
    result = manager.start_session(session_id)
    assert result['success'] is True
    
    # Verify session is active
    session = manager.get_session(session_id)
    assert session['status'] == 'active'
    
    print(f"✓ Session started successfully")
    
    # List sessions
    sessions = manager.list_available_sessions()
    # Should be empty since our session is now active
    assert len(sessions) == 0
    
    print(f"✓ Session listing test passed")


def test_parse_range():
    """Test range parsing functionality"""
    print("\nTesting range parsing...")
    
    # Test suited hands
    combos = parse_range('AKs')
    assert len(combos) == 4, "AKs should have 4 combinations"
    
    # Test offsuit hands
    combos = parse_range('AKo')
    assert len(combos) == 12, "AKo should have 12 combinations"
    
    # Test pairs
    combos = parse_range('AA')
    assert len(combos) == 6, "AA should have 6 combinations"
    
    print(f"✓ Range parsing test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Poker Suite Feature Tests")
    print("=" * 60)
    
    try:
        test_parse_range()
        test_multi_way_equity()
        test_stud_evaluation()
        test_razz_evaluation()
        test_training_scenarios()
        test_statistics_tracker()
        test_multiplayer_sessions()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
