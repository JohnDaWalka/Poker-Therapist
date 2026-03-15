"""
HUD Display
===========
Formats per-player statistics into a compact Heads-Up Display (HUD) string
suitable for overlaying on a poker client or printing to a terminal.

Example output:
    Villain_87
    VPIP 31 / PFR 24 / 3B 9
    Style: LAG
    Hands: 842

    Strategy adjustments:
      • Tighten your calling range; they inflate pots with wide hands
      • Trap with strong hands instead of re-raising
      …

Usage:
    from hud import format_hud_display, format_hud_compact

    stats = {
        "player_id": "Villain_87",
        "vpip": 31, "pfr": 24, "threebet": 9,
        "af": 2.5, "wtsd": 28, "hands": 842,
        "player_style": "LAG",
    }
    print(format_hud_display(stats))
    print(format_hud_compact(stats))
"""

from typing import Dict, Any, List

from player_classifier import get_strategy_suggestions

_BULLET = "\u2022"  # •


# ---------------------------------------------------------------------------
# Public formatters
# ---------------------------------------------------------------------------

def format_hud_display(stats: Dict[str, Any], *, show_strategy: bool = True) -> str:
    """Return a multi-line HUD string for *stats*.

    Args:
        stats: Dict containing at least the keys ``player_id``, ``vpip``,
               ``pfr``, ``threebet``, ``hands``, and ``player_style``.
               Optional keys: ``af``, ``wtsd``.
        show_strategy: When ``True`` (default), append strategy suggestions
                       below the stat block.

    Returns:
        A formatted, human-readable HUD block.
    """
    player_id    = stats.get("player_id", "Unknown")
    vpip         = stats.get("vpip", 0)
    pfr          = stats.get("pfr", 0)
    threebet     = stats.get("threebet", 0)
    af           = stats.get("af")
    wtsd         = stats.get("wtsd")
    hands        = stats.get("hands", 0)
    player_style = stats.get("player_style", "Unknown")

    lines: List[str] = [
        player_id,
        f"VPIP {_fmt(vpip)} / PFR {_fmt(pfr)} / 3B {_fmt(threebet)}",
    ]

    if af is not None and wtsd is not None:
        lines.append(f"AF {_fmt(af)} / WTSD {_fmt(wtsd)}")

    lines.append(f"Style: {player_style}")
    lines.append(f"Hands: {hands}")

    if show_strategy:
        suggestions = get_strategy_suggestions(player_style)
        lines.append("")
        lines.append("Strategy adjustments:")
        for tip in suggestions:
            lines.append(f"  {_BULLET} {tip}")

    return "\n".join(lines)


def format_hud_compact(stats: Dict[str, Any]) -> str:
    """Return a single-line compact HUD string for *stats*.

    Useful for space-constrained overlays.

    Example:
        ``Villain_87 | VPIP 31 / PFR 24 / 3B 9 | LAG | 842h``

    Args:
        stats: Same shape as accepted by :func:`format_hud_display`.

    Returns:
        A single-line HUD string.
    """
    player_id    = stats.get("player_id", "Unknown")
    vpip         = stats.get("vpip", 0)
    pfr          = stats.get("pfr", 0)
    threebet     = stats.get("threebet", 0)
    hands        = stats.get("hands", 0)
    player_style = stats.get("player_style", "Unknown")

    return (
        f"{player_id} | "
        f"VPIP {_fmt(vpip)} / PFR {_fmt(pfr)} / 3B {_fmt(threebet)} | "
        f"{player_style} | "
        f"{hands}h"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(value: Any) -> str:
    """Format a stat value: integers as-is, floats rounded to 1 dp."""
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.1f}"
    return str(int(value)) if value is not None else "–"


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

def _run_tests() -> None:
    """Run built-in HUD display tests."""
    print("Running HUD display tests...")

    sample_stats = {
        "player_id": "Villain_87",
        "vpip": 31,
        "pfr": 24,
        "threebet": 9,
        "af": 2.5,
        "wtsd": 28,
        "hands": 842,
        "player_style": "LAG",
    }

    # --- format_hud_display ---
    full = format_hud_display(sample_stats)
    assert "Villain_87" in full, "Player name missing from HUD"
    assert "VPIP 31" in full, "VPIP missing from HUD"
    assert "PFR 24" in full, "PFR missing from HUD"
    assert "3B 9" in full, "3BET missing from HUD"
    assert "Style: LAG" in full, "Style missing from HUD"
    assert "Hands: 842" in full, "Hands missing from HUD"
    assert "Strategy adjustments:" in full, "Strategy section missing from HUD"
    assert "AF 2.5" in full, "AF missing from HUD"
    assert "WTSD 28" in full, "WTSD missing from HUD"
    print("  ✓ format_hud_display – full block")

    # Without strategy
    no_strat = format_hud_display(sample_stats, show_strategy=False)
    assert "Strategy adjustments:" not in no_strat, "Strategy should be hidden"
    print("  ✓ format_hud_display – no strategy flag")

    # --- format_hud_compact ---
    compact = format_hud_compact(sample_stats)
    assert "Villain_87" in compact, "Player name missing from compact HUD"
    assert "LAG" in compact, "Style missing from compact HUD"
    assert "842h" in compact, "Hands missing from compact HUD"
    assert "\n" not in compact, "Compact HUD must be single line"
    print("  ✓ format_hud_compact – single line")

    # Missing optional fields
    minimal = {"player_id": "Bob", "vpip": 20, "pfr": 15, "threebet": 5,
               "hands": 100, "player_style": "TAG"}
    minimal_full = format_hud_display(minimal)
    assert "AF" not in minimal_full, "AF should not appear when not provided"
    assert "WTSD" not in minimal_full, "WTSD should not appear when not provided"
    print("  ✓ format_hud_display – missing optional fields handled gracefully")

    print("\n✅ All HUD display tests passed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        _run_tests()
        sys.exit(0)

    # Demo output
    demo = {
        "player_id": "Villain_87",
        "vpip": 31, "pfr": 24, "threebet": 9,
        "af": 2.5, "wtsd": 28, "hands": 842,
        "player_style": "LAG",
    }
    print(format_hud_display(demo))
    print()
    print(format_hud_compact(demo))
