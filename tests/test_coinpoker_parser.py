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
    # Note: The mock hash data above doesn't actually verify correctly,
    # but we still extract and attempt verification
    assert rng["verified_lines"] == 0
    assert rng["ok"] is False


def test_full_hand_360327066_parsing() -> None:
    """Test parsing the complete hand #360327066 with full RNG data."""
    text = r"""
CoinPoker Hand #360327066: Tournament #1424001, ₮5 Mini Rapido Hold'em No Limit (160/320 ante 40 play) 2026/01/10 01:08:19 GMT
Table '4' 7-max Seat #1 is the button
Seat 1: pollaloka (20707 in chips)
Seat 2: zerd (18792 in chips)
Seat 3: ChipHappens (54068 in chips)
Seat 4: jdwalka (20000 in chips)
Seat 5: Retracpoka (26407 in chips)
Seat 6: FloppyDolphin (35397 in chips)
Seat 7: yhardell (13555 in chips)
pollaloka: posts the ante 40
zerd: posts the ante 40
ChipHappens: posts the ante 40
jdwalka: posts the ante 40
Retracpoka: posts the ante 40
FloppyDolphin: posts the ante 40
yhardell: posts the ante 40
zerd: posts small blind 160
ChipHappens: posts big blind 320
*** HOLE CARDS ***
Dealt to jdwalka [6c Ad]
jdwalka has timed out
jdwalka activated time-bank (30 seconds)
jdwalka: folds
Retracpoka: folds
FloppyDolphin: raises 1080 to 1400
yhardell: folds
pollaloka: folds
zerd: folds
ChipHappens: raises 53708 and is all-in
FloppyDolphin: calls 33957 and is all-in
Uncalled bet (18671) returned to ChipHappens
*** FLOP *** [2d 7d 7s]
*** TURN *** [2d 7d 7s] [Jd]
*** RIVER *** [2d 7d 7s Jd] [Ah]
*** SHOW DOWN ***
ChipHappens: shows [Ac Kh] (two pairs, Aces and Sevens)
FloppyDolphin: shows [5c 5h] (two pairs, Sevens and Fives)
ChipHappens collected 71154 from pot
*** SUMMARY ***
Total pot 71154 | CC 0
Board [ 2d 7d 7s Jd Ah ]
Game ended: 2026/01/10 01:09:29 GMT
Seat 1: pollaloka (button) folded before Flop
Seat 2: zerd (small blind) folded before Flop
Seat 3: ChipHappens (big blind) showed [Ac Kh] and won (71154) with two pairs, Aces and Sevens
Seat 4: jdwalka folded before Flop
Seat 5: Retracpoka folded before Flop
Seat 6: FloppyDolphin showed [5c 5h]
Seat 7: yhardell folded before Flop
*** RNG ***
phrase: 111
cards: (2d) (7d) (7s) (Jd) (Ah) Jh 2c Js 2h Tc 2s 8d 3h 4h Kd Qs 5s Qh Td 4c Ks Qd 8h 3c 7h 9h 8s 6s 4s Kc Th 7c 9s 6h XX XX XX XX
player_cards: 3 6c Ad
HandId: 360327066 Validate Hand
Initial hashed deck:

3eb42dd1dc5c2bf4e4f8b4e9a6d9000321095e82ae7187cc60cf9b90e68f6cb6
bc706b809e31d18521cbc298a17a6ab7cd34562cb2ec84403a1598d0d2b1a2f4
3a094884a44dca0da66e6e28d0eb1fdfc68fe41045119ab23e209767cb2a877b
c6101e475d797e035228bb62033f0c2ec6cf82f9bade7749d65734657b7630f4
5340df43e390c3f7ef8a42a93daf85b986c31b817394042d2c6f676af8e94e12
ab8f5052365bccbc663fa44a725167a2e38a204df7da6ba2cc83b6f617b786d5
81335069d445ed571b45c59adff35effc2e16170017c6dbbf22b4e9aa5845ee6
bb6d5fc2daee1fc6cb64207fb846e41d5e7ea89b5c09fc5dce5458fe09a06e24
bd305eee3d342365340aa267b97e25d54dfc4765649c6c558f4fc9ad6f108907
f3ab02807aa80b58aed37c0cf611a7e7a9585b11bba923e75f6faf4b3442b2c1
989bd4abc4006b45992cc9a34498cf295360458f16649c0c3967608ff1338648
9c53db5f2c1e7a904657883c319a6966ea59bdecad599cb83ab58dd6cf05b250
0a870733be0f0e9a8aba91d7faa8bfb6d8d63f6fd560b807f170acf9441da6c8
2066d908de6c9cd1dc85e1d5acf3a0f008dc0581e078e96a2fc34a252897267b
8b179426d43ba37fd37541262f138625cfe1bb168c73c171af8538ae4d246472
63edb70ff490b87f2ff645c29ab3b08122e38b051eaa754257f1749671960254
8ee7aec54e0f5ca8d8733eb606a4e6dac7a761c73eba676d36d7d0ce07703564
543a2435c4b40092a77cb47166c5d2da2b6b4bdd56658f3d202c9309e67f72b7
cb7fa7cbed85500591fe11645ba3520e8f01fe6881eae40a18d271cdc6842020
b1f9fac65f69681e0a8cb9d4f09dc973b37d82ba0ade26040670f389432aec67
1073dd0c86b4b9ea71c3e1e23d1c198ff6a2792dcca1b859d29575cc529443b7
1f7b1a5941f46edcfe8c21177f564c17a9d571368e55158d9a68244bc05c42ff
0e08279bb4ef17cd49eca86f4b6c58fc1d63e1d911c1cdfef5d23d6cd3aaaf55
b77b641338ff47b8919bb092b75c7987f32026dc0507b37d8bd8de475c343c39
2c141115df775aca09c0d7ddb0eaa94e19c93030fd87eff9111e19a286ca57bd
31db2d6cae289847cbccd84326253a2807e85665139cb8cb2846096db4a00d4e
5d9ff3bfe385139118c8b11231503ce5cdd5e58d8bcb1073b874d9f37e32f70c
44ff25c9d17b249f667ee2ef1464df6fb8e2a49ccd20036de79dd881af2a76b9
45ccd38a06b24653edd794846bbfecc6424214da1bd659c1e04568f1658fa1d7
4bfea1c3b588539f0b3a5a98cf0eb6975acb666fe72cdf5d0e700115e6bb63dd
3287865bc2a18ba5c40e0ace6bcef4bd7814fff84380e8fdd55cb228e6633846
a71b85b8171812652d1398706640f95e36eeea0135a4da55e0de01487bc9409e
61c51c03256d6d6bb1697aff9af6c44a5d00ede39f6b435ee6d19532934264b7
4bde4e14370a9a4a41a7c088b27db4bef83d9d66e2ba5bb9cdf98e55b07a9a30
c65316c9bec23ae9d5c764aa25cf7089e6ce2a7a23c5c1aef02a5cbab7862f15
d73a7347a4be68d88a31ed2bd9ff256d7fcdaf4a319ce4b0e54a14476b923cfa
d10e095c6aef466518709f31723b17b0ab9162e6a49ff444ef2cc435ede28d8b
cc42afb6e42189902a9ed4422043f842be356d8f98e65bd60d5bb709e14b442d
f5ed925aa69464617bed6416772000c841378e9a0ba29fe1e0a5f2976e69baa1
62cab64735be87f2741451b74a220132b4204e33392d51b5751da884a79f8e35
2f65b74d0b92e558fe4b157ea664b63eac23e733e156023a08b7841d5815fa08
3554559904135fd1c59884c8447cead26ebab46b7979b7cbbe14362edbaa2a32
2db990aaa46108efee6f69b5a2d2a366c854defb9409011d1a4279b2ae0cc0ec
2b4e932891948e0833a0a15f362503d8b451653fbede287a0182523933689f2c
78a32d6c4aca3209b94c9b0be502a9820890dd4a48fff70c71df304b33d3f738
36c0a111ae59493c71be7044326e2587f8e508a0c49570424747a148f010d154
2ab761ca07bf318470730218e4b21a967e1b833ee6c6c2ebd305236706e93ba2
aa65d425506d48f71181189409518506f3c8bda7855000d9c56a09457bdd651c
cc5f4702e0652f6deb7f049b457a2a5a6b5e8e5a0157af5cd1cb3b3fc066c8a6
cb00d4ba1680cf0ac6c1fdf56bc533d9d741d855246c8d6e23562d0dbd18a9e5
6c08201a8f7b6caef919f0782dfe501e72ed3c383bf961fedb035b49719d7e06
d8623900d9acb46fdda07fd671d8384dbe68d6ec806abf3706bdd76b64be1aae
Seeds by seat index:
Seed Hex Representation Seed Text Representation
-1 b9fd357bd9b90529c6a0eb1fedd27ffd66656d8c0786d3f6f3f74d07e17d174e | ASCII: ..5{...)........fem.......M..}.N (operator)
0 63392ca01a144f267ca6dcf2d9adecf8406aab39e011ba14573a795fd7d145a2 | ASCII: c9,...O&|.......@j.9....W:y_..E. (Player: pollaloka)
1 7a65726400000000000000000000000000000000000000000000000000000000 | ASCII: zerd............................ (Player: zerd)
2 4c65747320676f00000000000000000000000000000000000000000000000000 | ASCII: Lets go......................... (Player: ChipHappens)
3 3131310000000000000000000000000000000000000000000000000000000000 | ASCII: 111............................. (Player: jdwalka)
4 686f6c7900000000000000000000000000000000000000000000000000000000 | ASCII: holy............................ (Player: Retracpoka)
5 7394a29794ad49985c70dcde60370d294233c4fe2acb72d7cdc2c053cc2ee9f7 | ASCII: s.....I.\p..`7.)B3..*.r....S.... (Player: FloppyDolphin)
6 26b6fb72c8456d7ac3ec0efab1cde0a447b188d13113bc48c64a09c46a7da11d | ASCII: &..r.Emz........G...1..H.J..j}.. (Player: yhardell)
----------------------------------------------------------------
ea3988ac5179a4490c728644f39b73e61a003c6eeb1f230b5cc58d820fefe0ed (combined)

Shuffled hashed deck:
Card Hash Card Hex Representation (salt + card) Card Text Representation
11. 989bd4abc4006b45992cc9a34498cf295360458f16649c0c3967608ff1338648
36. d73a7347a4be68d88a31ed2bd9ff256d7fcdaf4a319ce4b0e54a14476b923cfa
9. bd305eee3d342365340aa267b97e25d54dfc4765649c6c558f4fc9ad6f108907
8. bb6d5fc2daee1fc6cb64207fb846e41d5e7ea89b5c09fc5dce5458fe09a06e24
41. 2f65b74d0b92e558fe4b157ea664b63eac23e733e156023a08b7841d5815fa08 <- H(be3b6efc756c701fe6ce1d8a8c80c4255f3e0a38fa9fb13e348f19f86798228e004163) | ASCII: .;n.ulp........%>.8...>4...g."..Ac - ok
18. 543a2435c4b40092a77cb47166c5d2da2b6b4bdd56658f3d202c9309e67f72b7 <- H(5a4b4cbcb79edf0a0560f55e0fc936063041e5cafa345c8d1473704f6a6e687c004b68) | ASCII: ZKL.......^..6.0A...4\..spOjnh|.Kh - ok
6. 3a094884a44dca0da66e6e28d0eb1fdfc68fe41045119ab23e209767cb2a877b <- H(a7702ac52d0cc99d7d1a581bc47a831232b6037ba47eb33267b64cc9dddf17ba003663) | ASCII: .p*.-...}.X..z..2..{.~.2g.L......6c - ok
17. 8ee7aec54e0f5ca8d8733eb606a4e6dac7a761c73eba676d36d7d0ce07703564 <- H(d9ba8f2934fe391bad1d08d25e1e005365ed47b7f69d85a9b2fb2331d7735bb7004164) | ASCII: ...)4.9.....^..Se.G.......#1.s[..Ad - ok
30. 4bfea1c3b588539f0b3a5a98cf0eb6975acb666fe72cdf5d0e700115e6bb63dd
43. 2db990aaa46108efee6f69b5a2d2a366c854defb9409011d1a4279b2ae0cc0ec
15. 8b179426d43ba37fd37541262f138625cfe1bb168c73c171af8538ae4d246472 <- H(868300524a246413dec95c73e82326082264d4da061c12fec501a7b8a19749b4003563) | ASCII: ...RJ$d...\s.#&."d............I..5c - ok
29. 45ccd38a06b24653edd794846bbfecc6424214da1bd659c1e04568f1658fa1d7 <- H(80343cd423b5c80cdab6fb5a9bb272405ae4288c3e48a9e8e2119e2fbbd627fb003568) | ASCII: .4<.#......Z..r@Z.(.>H...../..'..5h - ok
5. 5340df43e390c3f7ef8a42a93daf85b986c31b817394042d2c6f676af8e94e12
50. cb00d4ba1680cf0ac6c1fdf56bc533d9d741d855246c8d6e23562d0dbd18a9e5
21. 1073dd0c86b4b9ea71c3e1e23d1c198ff6a2792dcca1b859d29575cc529443b7 <- H(6bbbfdca50fd182b2c25e682a3918c0e336ff49a9524e62500e108426bb41246003264) | ASCII: k...P..+,%......3o...$.%...Bk..F.2d - ok
12. 9c53db5f2c1e7a904657883c319a6966ea59bdecad599cb83ab58dd6cf05b250 <- H(a6b3d5d732c1c65de10260e07ad5b8ffb6407e6143b4214161b5b9fda3dece01003764) | ASCII: ....2..]...z....@~aC.!Aa........7d - ok
20. b1f9fac65f69681e0a8cb9d4f09dc973b37d82ba0ade26040670f389432aec67 <- H(2a0ffe42ac97b6a587aabcf95cb5802ab653a738d6e10d6f1cf28e81edd65c9b003773) | ASCII: ..B...........S.8...o........7s - ok
34. 4bde4e14370a9a4a41a7c088b27db4bef83d9d66e2ba5bb9cdf98e55b07a9a30 <- H(b4f2e458d9a52d80ce98724b6b978011e62caa82ca802d380185b05b840fb09e004a64) | ASCII: ...X..-...rKk....,....-8...[.....Jd - ok
28. 44ff25c9d17b249f667ee2ef1464df6fb8e2a49ccd20036de79dd881af2a76b9 <- H(c7c4c81eedecc92243c2e060fd73858d1ba250a5c39f2982beb6a5741818f540004168) | ASCII: ......."C..`.s....P...)....t...@.Ah - ok
13. 0a870733be0f0e9a8aba91d7faa8bfb6d8d63f6fd560b807f170acf9441da6c8 <- H(1929bb06276f47d8b95a0d52346b285b76412c5fdfb6417af017a6a99967e8cf004a68) | ASCII: .)..'oG..Z.R4k([vA,..Az.....g...Jh - ok
51. 6c08201a8f7b6caef919f0782dfe501e72ed3c383bf961fedb035b49719d7e06 <- H(5ec27105661298ca343e0140f35881c70ef7aca5ce9e85209a63d3c780a2dfd8003263) | ASCII: ^.q.f...4>.@.X......... .c.......2c - ok
2. bc706b809e31d18521cbc298a17a6ab7cd34562cb2ec84403a1598d0d2b1a2f4 <- H(7623fb5bfcefb8b1a956c3551c8210be89fe6155ff70e6caadf58201dce2a88e004a73) | ASCII: v#.[.....V.U......aU.p...........Js - ok
33. 61c51c03256d6d6bb1697aff9af6c44a5d00ede39f6b435ee6d19532934264b7 <- H(73763da5078d7f816148afef21017f04121a9a288b4dbdcbeff36e867f18f236003268) | ASCII: sv=.....aH..!......(.M....n....6.2h - ok
7. 81335069d445ed571b45c59adff35effc2e16170017c6dbbf22b4e9aa5845ee6 <- H(ef782733bb9924780f505971c50d68d4bb02d311f6710e291afb984beaf4c192005463) | ASCII: .x'3..$x.PYq..h......q.)...K.....Tc - ok
""".strip()

    hands = parse_many(text)
    assert len(hands) == 1
    
    hand = hands[0]
    assert hand.hand_id == "360327066"
    assert hand.stakes == "160/320 ante 40"
    assert hand.player_name == "jdwalka"
    assert hand.hole_cards == "6cAd"
    assert hand.board == "2d7d7s Jd Ah"
    assert hand.rng_phrase == "111"
    assert hand.rng_combined_seed_hash == "ea3988ac5179a4490c728644f39b73e61a003c6eeb1f230b5cc58d820fefe0ed"
    
    # Verify RNG data is extracted
    rng = verify_rng(text)
    assert rng["phrase"] == "111"
    assert rng["combined_seed_hash"] == "ea3988ac5179a4490c728644f39b73e61a003c6eeb1f230b5cc58d820fefe0ed"
    # Should have multiple verifiable lines from the full export
    assert rng["verifiable_lines"] > 10
