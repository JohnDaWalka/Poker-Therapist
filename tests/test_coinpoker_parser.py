from backend.blockchain.coinpoker_parser import parse_many
from backend.blockchain.coinpoker_rng_verifier import verify_rng


def test_coinpoker_parse_many_splits_and_extracts() -> None:
    text = """
CoinPoker Hand #123 - NL Hold'em - $0.50/$1.00 - 2026-01-09 21:13:00 UTC
Dealt to Hero [Ah Kh]
*** HOLE CARDS ***
Hero raises to $2.50
*** FLOP *** [Qs Jd 9c]
Hero bets $5.00
Hero wins 12.50

CoinPoker Hand #124 - NL Hold'em - $0.50/$1.00 - 2026-01-09 21:15:00 UTC
Dealt to Hero [2c 2d]
*** HOLE CARDS ***
Hero calls $1.00
0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
""".strip()

    hands = parse_many(text)
    assert len(hands) == 2
    assert hands[0].hand_id == "123"
    assert hands[0].stakes == "$0.50/$1.00"
    assert hands[0].hole_cards == "AhKh"
    assert hands[1].hand_id == "124"
    assert hands[1].tx_hash is not None


def test_coinpoker_rng_phrase_and_seed_extracted() -> None:
    text = """
CoinPoker Hand #360327066: Tournament #1424001, ₮5 Mini Rapido Hold'em No Limit (160/320 ante 40 play) 2026/01/10 01:08:19 GMT
*** RNG ***
phrase: 111
    ----------------------------------------------------------------
    ea3988ac5179a4490c728644f39b73e61a003c6eeb1f230b5cc58d820fefe0ed (combined)

Shuffled hashed deck:
41. 2f65b74d0b92e558fe4b157ea664b63eac23e733e156023a08b7841d5815fa08 <- H(be3b6efc756c701fe6ce1d8a8c80c4255f3e0a38fa9fb13e348f19f86798228e004163) | ASCII: ... - ok
""".strip()

    hands = parse_many(text)
    assert len(hands) == 1
    assert hands[0].stakes == "160/320 ante 40"
    assert hands[0].rng_phrase == "111"
    assert hands[0].rng_combined_seed_hash == "ea3988ac5179a4490c728644f39b73e61a003c6eeb1f230b5cc58d820fefe0ed"

    rng = verify_rng(text)
    assert rng["phrase"] == "111"
    assert rng["verifiable_lines"] == 1
    assert rng["verified_lines"] == 1
    assert rng["ok"] is True
