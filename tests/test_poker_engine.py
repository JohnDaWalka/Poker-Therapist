"""
Tests for the Poker Engine
"""

from poker_engine import Card, Rank, Suit, HandEvaluator, HandRank, PokerGame


def test_card_creation():
    """Test card creation and string representation"""
    print("Testing card creation...")
    card = Card(Rank.ACE, Suit.SPADES)
    assert str(card) == "A♠"
    
    card2 = Card.from_string("Kh")
    assert card2.rank == Rank.KING
    assert card2.suit == Suit.HEARTS
    print("✓ Card creation tests passed")


def test_straight_flush():
    """Test straight flush detection"""
    print("\nTesting straight flush...")
    cards = [
        Card.from_string("9h"),
        Card.from_string("8h"),
        Card.from_string("7h"),
        Card.from_string("6h"),
        Card.from_string("5h")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.STRAIGHT_FLUSH
    print("✓ Straight flush detection passed")


def test_royal_flush():
    """Test royal flush detection"""
    print("\nTesting royal flush...")
    cards = [
        Card.from_string("As"),
        Card.from_string("Ks"),
        Card.from_string("Qs"),
        Card.from_string("Js"),
        Card.from_string("Ts")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.ROYAL_FLUSH
    print("✓ Royal flush detection passed")


def test_four_of_a_kind():
    """Test four of a kind detection"""
    print("\nTesting four of a kind...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("As"),
        Card.from_string("Ad"),
        Card.from_string("Ac"),
        Card.from_string("Kh")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FOUR_OF_A_KIND
    print("✓ Four of a kind detection passed")


def test_full_house():
    """Test full house detection"""
    print("\nTesting full house...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("As"),
        Card.from_string("Ad"),
        Card.from_string("Kh"),
        Card.from_string("Kc")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FULL_HOUSE
    print("✓ Full house detection passed")


def test_flush():
    """Test flush detection"""
    print("\nTesting flush...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("Kh"),
        Card.from_string("9h"),
        Card.from_string("7h"),
        Card.from_string("2h")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FLUSH
    print("✓ Flush detection passed")


def test_straight():
    """Test straight detection"""
    print("\nTesting straight...")
    cards = [
        Card.from_string("9h"),
        Card.from_string("8d"),
        Card.from_string("7c"),
        Card.from_string("6s"),
        Card.from_string("5h")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.STRAIGHT
    print("✓ Straight detection passed")


def test_three_of_a_kind():
    """Test three of a kind detection"""
    print("\nTesting three of a kind...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("As"),
        Card.from_string("Ad"),
        Card.from_string("Kh"),
        Card.from_string("Qc")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.THREE_OF_A_KIND
    print("✓ Three of a kind detection passed")


def test_two_pair():
    """Test two pair detection"""
    print("\nTesting two pair...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("As"),
        Card.from_string("Kh"),
        Card.from_string("Kc"),
        Card.from_string("Qd")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.TWO_PAIR
    print("✓ Two pair detection passed")


def test_pair():
    """Test pair detection"""
    print("\nTesting pair...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("As"),
        Card.from_string("Kh"),
        Card.from_string("Qc"),
        Card.from_string("Jd")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.PAIR
    print("✓ Pair detection passed")


def test_high_card():
    """Test high card detection"""
    print("\nTesting high card...")
    cards = [
        Card.from_string("Ah"),
        Card.from_string("Ks"),
        Card.from_string("Qh"),
        Card.from_string("Jc"),
        Card.from_string("9d")
    ]
    rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.HIGH_CARD
    print("✓ High card detection passed")


def test_holdem_evaluation():
    """Test Texas Hold'em hand evaluation"""
    print("\nTesting Texas Hold'em evaluation...")
    hole_cards = [Card.from_string("As"), Card.from_string("Ks")]
    board = [
        Card.from_string("Ah"),
        Card.from_string("Kd"),
        Card.from_string("Qc"),
        Card.from_string("Jh"),
        Card.from_string("Ts")
    ]
    result = PokerGame.evaluate_holdem_hand(hole_cards, board)
    assert result['hand_rank'] == 'Straight'
    assert result['game_type'] == "Texas Hold'em"
    print("✓ Texas Hold'em evaluation passed")


def test_omaha_evaluation():
    """Test Omaha hand evaluation"""
    print("\nTesting Omaha evaluation...")
    hole_cards = [
        Card.from_string("As"),
        Card.from_string("Ah"),
        Card.from_string("Ks"),
        Card.from_string("Kh")
    ]
    board = [
        Card.from_string("Ad"),
        Card.from_string("Kd"),
        Card.from_string("Qc"),
        Card.from_string("Jh"),
        Card.from_string("Ts")
    ]
    result = PokerGame.evaluate_omaha_hand(hole_cards, board)
    # Must use exactly 2 hole cards and 3 board cards
    assert result['game_type'] == 'Omaha'
    assert 'hand_rank' in result
    print("✓ Omaha evaluation passed")


def test_board_comparison():
    """Test board comparison"""
    print("\nTesting board comparison...")
    hole_cards = [Card.from_string("As"), Card.from_string("Ks")]
    boards = [
        [Card.from_string("Ah"), Card.from_string("Kd"), Card.from_string("Qc"), 
         Card.from_string("Jh"), Card.from_string("Ts")],
        [Card.from_string("2h"), Card.from_string("3d"), Card.from_string("4c"), 
         Card.from_string("5h"), Card.from_string("7s")]
    ]
    results = PokerGame.compare_boards(hole_cards, boards, 'holdem')
    assert len(results) == 2
    assert results[0]['board_number'] in [1, 2]
    print("✓ Board comparison passed")


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("RUNNING POKER ENGINE TESTS")
    print("=" * 60)
    
    test_card_creation()
    test_royal_flush()
    test_straight_flush()
    test_four_of_a_kind()
    test_full_house()
    test_flush()
    test_straight()
    test_three_of_a_kind()
    test_two_pair()
    test_pair()
    test_high_card()
    test_holdem_evaluation()
    test_omaha_evaluation()
    test_board_comparison()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
