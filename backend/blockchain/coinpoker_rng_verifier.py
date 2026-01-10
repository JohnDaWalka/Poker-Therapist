"""CoinPoker provably-fair RNG verifier.

CoinPoker hand exports often include a section like:

  *** RNG ***
  phrase: 111
  ...
  Shuffled hashed deck:
    41. <card_hash> <- H(<salt+card hex>) | ... - ok

This verifier re-computes SHA-256 over the bytes represented by the hex inside
H(...), and confirms it matches the listed card hash.

If all verifiable lines match, the hand is considered RNG-verified.

Note: This does NOT prove gameplay correctness, only that the exported proof
is internally consistent.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional


_PHRASE_RE = re.compile(r"^\s*phrase:\s*(?P<phrase>.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_COMBINED_SEED_RE = re.compile(r"^\s*(?P<hex>[a-f0-9]{64})\s*\(combined\)\s*$", re.IGNORECASE | re.MULTILINE)

# Example line:
# 41. 2f65... <- H(be3b...004163) | ASCII: ... - ok
_VERIFY_LINE_RE = re.compile(
    r"^\s*\d+\.\s*(?P<expected>[a-fA-F0-9]{64})\s*(?:<-\s*H\((?P<input>[a-fA-F0-9]+)\))?\s*(?P<tail>.*)$",
    re.MULTILINE,
)


def _sha256_hex_from_input_hex(input_hex: str) -> str:
    b = bytes.fromhex(input_hex)
    return hashlib.sha256(b).hexdigest()


def extract_rng_phrase(text: str) -> Optional[str]:
    m = _PHRASE_RE.search(text)
    return m.group("phrase").strip() if m else None


def extract_combined_seed_hash(text: str) -> Optional[str]:
    m = _COMBINED_SEED_RE.search(text)
    return m.group("hex").lower() if m else None


def verify_rng(text: str) -> Dict[str, Any]:
    phrase = extract_rng_phrase(text)
    combined_seed_hash = extract_combined_seed_hash(text)

    total = 0
    verified = 0
    mismatches: List[Dict[str, str]] = []
    missing_inputs = 0

    for m in _VERIFY_LINE_RE.finditer(text):
        expected = m.group("expected").lower()
        input_hex = m.group("input")
        tail = (m.group("tail") or "").lower()

        # Only treat as a verifiable line when it actually includes H(...)
        if not input_hex:
            # If the export doesn't include H(...) there is nothing to verify here.
            continue

        total += 1
        try:
            computed = _sha256_hex_from_input_hex(input_hex).lower()
        except Exception:
            missing_inputs += 1
            mismatches.append({"expected": expected, "computed": "<error>", "input_hex": input_hex})
            continue

        if computed == expected:
            verified += 1
        else:
            mismatches.append({"expected": expected, "computed": computed, "input_hex": input_hex})

        # If the line explicitly says "- ok" but our computed differs, that’s important.
        # We leave that to mismatches.

    ok = (total > 0) and (verified == total)

    return {
        "ok": ok,
        "phrase": phrase,
        "combined_seed_hash": combined_seed_hash,
        "verifiable_lines": total,
        "verified_lines": verified,
        "missing_inputs": missing_inputs,
        "mismatches": mismatches,
    }
