"""
Player Style Classifier
=======================
Classifies poker opponents into behavioral archetypes based on statistical
fingerprints (VPIP, PFR, 3BET) collected from hand history.

Classic Archetypes:
    Nit           – VPIP <15, PFR <12      (extremely tight)
    TAG           – VPIP 15-25, PFR 12-20  (tight-aggressive regular)
    LAG           – VPIP 25-40, PFR 18-35  (loose-aggressive)
    Loose Passive – VPIP >35, PFR <15      (calling station)
    Maniac        – VPIP >40, 3BET >15     (hyper-aggressive)

Usage:
    from player_classifier import classify_player, get_strategy_suggestions

    style = classify_player(vpip=31, pfr=24, threebet=9)
    print(style)  # "LAG"

    advice = get_strategy_suggestions(style)
    for line in advice:
        print(line)
"""

from typing import List


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_player(vpip: float, pfr: float, threebet: float) -> str:
    """Return the player-style archetype that best matches the given stats.

    Args:
        vpip:     Voluntarily-put-money-in-pot percentage (0-100).
        pfr:      Pre-flop raise percentage (0-100).
        threebet: Pre-flop 3-bet percentage (0-100).

    Returns:
        One of: "Nit", "TAG", "LAG", "Loose Passive", "Maniac", or "Unknown".

    Classification priority:
        Maniac is tested before Loose Passive so that hyper-aggressive players
        are not mislabelled as calling stations.
    """
    if vpip < 15 and pfr < 12:
        return "Nit"

    if 15 <= vpip <= 25 and 12 <= pfr <= 20:
        return "TAG"

    if vpip > 40 and threebet > 15:
        return "Maniac"

    if vpip > 35 and pfr < 15:
        return "Loose Passive"

    if vpip > 25 and pfr > 18:
        return "LAG"

    return "Unknown"


# ---------------------------------------------------------------------------
# Strategy suggestions
# ---------------------------------------------------------------------------

_STRATEGY_MAP: dict = {
    "Nit": [
        "Steal blinds aggressively — Nits fold to pressure",
        "3-bet more frequently against their opens",
        "Fold to their aggression; they rarely bluff",
        "Don't pay off their big hands",
    ],
    "TAG": [
        "Respect their aggression — avoid marginal spots out of position",
        "3-bet/4-bet bluff selectively to exploit their fold-to-3bet tendency",
        "C-bet smaller on boards that hit their range",
        "Battle for positional advantage pre-flop",
    ],
    "LAG": [
        "Tighten your calling range; they inflate pots with wide hands",
        "Trap with strong hands instead of re-raising",
        "Float or check-raise on favourable boards to counter c-bets",
        "Value bet thinner on the river against their wide ranges",
    ],
    "Loose Passive": [
        "Value bet thinner — they call too wide",
        "Bluff less frequently; they rarely fold",
        "Increase isolation raises to play heads-up in position",
        "Bet for value relentlessly on all streets",
    ],
    "Maniac": [
        "Widen your calling range; they over-bluff",
        "Trap with strong hands rather than building the pot yourself",
        "Avoid marginal bluffs — they call down light",
        "Let them dictate the betting and punish with strong holdings",
    ],
    "Unknown": [
        "Collect more hands before drawing strategic conclusions",
        "Watch for bet-sizing tells and showdown tendencies",
    ],
}


def get_strategy_suggestions(player_style: str) -> List[str]:
    """Return a list of strategic adjustments for the given player style.

    Args:
        player_style: One of the archetype names returned by :func:`classify_player`.

    Returns:
        A list of plain-text strategy tips.  Falls back to generic advice for
        unrecognised style strings.
    """
    return _STRATEGY_MAP.get(player_style, _STRATEGY_MAP["Unknown"])


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    """Run built-in classifier tests."""
    print("Running player classifier tests...")

    # --- classify_player tests ---

    # Nit
    assert classify_player(12, 9, 2) == "Nit", "Nit classification failed"
    assert classify_player(14, 11, 1) == "Nit", "Nit boundary failed"
    print("  ✓ Nit classification")

    # TAG
    assert classify_player(20, 15, 6) == "TAG", "TAG classification failed"
    assert classify_player(15, 12, 4) == "TAG", "TAG lower boundary failed"
    assert classify_player(25, 20, 7) == "TAG", "TAG upper boundary failed"
    print("  ✓ TAG classification")

    # LAG
    assert classify_player(31, 24, 9) == "LAG", "LAG classification failed"
    assert classify_player(35, 25, 8) == "LAG", "LAG classification failed (high end)"
    print("  ✓ LAG classification")

    # Loose Passive
    assert classify_player(40, 10, 3) == "Loose Passive", "Loose Passive failed"
    assert classify_player(50, 8, 2) == "Loose Passive", "Loose Passive (high VPIP) failed"
    print("  ✓ Loose Passive classification")

    # Maniac
    assert classify_player(45, 35, 18) == "Maniac", "Maniac classification failed"
    assert classify_player(55, 40, 20) == "Maniac", "Maniac (extreme) failed"
    print("  ✓ Maniac classification")

    # Unknown
    assert classify_player(22, 5, 1) == "Unknown", "Unknown fallback failed"
    print("  ✓ Unknown fallback")

    # --- get_strategy_suggestions tests ---

    for style in ("Nit", "TAG", "LAG", "Loose Passive", "Maniac"):
        suggestions = get_strategy_suggestions(style)
        assert isinstance(suggestions, list) and len(suggestions) > 0, \
            f"Empty suggestions for {style}"
    unknown_suggestions = get_strategy_suggestions("Unknown")
    assert len(unknown_suggestions) > 0, "Empty suggestions for Unknown"
    fallback_suggestions = get_strategy_suggestions("NonExistentStyle")
    assert fallback_suggestions == get_strategy_suggestions("Unknown"), \
        "Fallback for unrecognised style failed"
    print("  ✓ Strategy suggestions")

    print("\n✅ All classifier tests passed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        _run_tests()
        sys.exit(0)

    if len(sys.argv) >= 4:
        try:
            v = float(sys.argv[1])
            p = float(sys.argv[2])
            t = float(sys.argv[3])
        except ValueError:
            print("Usage: python player_classifier.py <vpip> <pfr> <threebet>")
            sys.exit(1)

        style = classify_player(v, p, t)
        print(f"Player style: {style}")
        print("\nStrategy adjustments:")
        for tip in get_strategy_suggestions(style):
            print(f"  • {tip}")
    else:
        print("Usage:")
        print("  python player_classifier.py <vpip> <pfr> <threebet>")
        print("  python player_classifier.py test")
