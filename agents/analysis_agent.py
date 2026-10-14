"""
analysis_agent.py — Cryptanalysis tools for Cipher Quest.

Exposes frequency analysis, Index of Coincidence, cipher suggestion,
and auto-crack utilities as @tool-decorated functions for the Swarm
orchestrator (cipher_command_agent).

All analysis logic in common_algos.py is deterministic — no LLM calls.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from strands import Agent, tool
from agents.common_algos import (
    letter_frequency,
    index_of_coincidence,
    suggest_cipher,
    caesar_brute_force,
    rail_fence_decrypt,
    base64_decode,
    xor_decrypt,
    ENGLISH_FREQ,
)


# ─────────────────────────────────────────────
# Frequency analysis tools
# ─────────────────────────────────────────────

@tool
def tool_letter_frequency(text: str) -> str:
    """
    Compute letter frequency percentages for the given text.

    Useful for identifying monoalphabetic substitution ciphers — compare
    against known English frequencies (E≈12.7%, T≈9.1%, A≈8.2%, …).

    Args:
        text: The text to analyze.

    Returns:
        JSON string mapping each letter to its frequency percentage.
    """
    freq = letter_frequency(text)
    return json.dumps(freq, indent=2)


@tool
def tool_index_of_coincidence(text: str) -> str:
    """
    Compute the Index of Coincidence (IC) for text.

    Interpretation:
    - IC ≈ 0.065 → English plaintext (monoalphabetic cipher likely)
    - IC ≈ 0.050 → Vigenère or Playfair
    - IC ≈ 0.038 → Random / strong polyalphabetic or transposition

    Args:
        text: The text to analyze.

    Returns:
        A human-readable string with the IC value and its interpretation.
    """
    ic = index_of_coincidence(text)
    if ic > 0.060:
        interpretation = "close to English (monoalphabetic substitution likely)"
    elif ic > 0.045:
        interpretation = "intermediate (Vigenère, Playfair, or short key poly)"
    else:
        interpretation = "low/random (transposition or strong polyalphabetic)"
    return f"IC = {ic:.6f} — {interpretation}"


@tool
def tool_suggest_cipher(text: str) -> str:
    """
    Heuristically suggest which cipher might have been applied to the text.

    Checks for Base64 encoding, XOR hex output, and uses IC analysis to
    distinguish monoalphabetic from polyalphabetic/transposition ciphers.

    Args:
        text: The ciphertext to analyze.

    Returns:
        A string naming the most likely cipher type.
    """
    return suggest_cipher(text)


@tool
def tool_english_frequency_reference() -> str:
    """
    Return the standard English letter frequency table for comparison.

    Returns:
        JSON string mapping each letter to its expected English frequency %.
    """
    return json.dumps(ENGLISH_FREQ, indent=2)


# ─────────────────────────────────────────────
# Auto-crack tool
# ─────────────────────────────────────────────

@tool
def tool_auto_crack(ciphertext: str) -> str:
    """
    Attempt to automatically identify and decrypt ciphertext.

    Strategy:
    1. Suggest the cipher type using heuristics.
    2. For Base64 → decode immediately.
    3. For monoalphabetic (high IC) → brute-force Caesar and score results.
    4. For Rail Fence → try rails 2-8.
    5. Otherwise → return frequency analysis + IC for manual investigation.

    Args:
        ciphertext: The ciphertext to crack.

    Returns:
        A formatted string with the best decryption attempt(s) and confidence.
    """
    lines = ["=== Auto-Crack Report ==="]

    # Step 1: Suggest cipher type
    suggestion = suggest_cipher(ciphertext)
    lines.append(f"Cipher suggestion: {suggestion}")

    # Step 2: Base64 fast path
    if suggestion == "Base64":
        try:
            decoded = base64_decode(ciphertext)
            lines.append(f"\n✅ Base64 decoded: {decoded}")
            return '\n'.join(lines)
        except ValueError as e:
            lines.append(f"Base64 decode failed: {e}")

    # Step 3: Monoalphabetic — brute-force Caesar, score by English freq fit
    ic = index_of_coincidence(ciphertext)
    lines.append(f"Index of Coincidence: {ic:.6f}")

    if ic > 0.055:
        lines.append("\nBrute-forcing Caesar cipher (all 26 shifts):")
        candidates = caesar_brute_force(ciphertext)
        # Score each candidate by chi-squared against English frequencies
        scored = []
        for c in candidates:
            freq = letter_frequency(c["plaintext"])
            chi2 = sum(
                ((freq.get(letter, 0) - expected) ** 2) / expected
                for letter, expected in ENGLISH_FREQ.items()
                if expected > 0
            )
            scored.append((chi2, c["shift"], c["plaintext"]))
        scored.sort()
        # Top 3 candidates
        for chi2, shift, plaintext in scored[:3]:
            lines.append(f"  Shift {shift:2d} (score {chi2:.1f}): {plaintext}")
        lines.append(f"\n🏆 Best Caesar candidate: shift={scored[0][1]} → {scored[0][2]}")

    # Step 4: Rail Fence attempts
    elif suggestion.startswith("Rail"):
        lines.append("\nTrying Rail Fence decryption (rails 2-8):")
        for r in range(2, 9):
            attempt = rail_fence_decrypt(ciphertext, r)
            lines.append(f"  Rails {r}: {attempt}")

    # Step 5: Manual investigation fallback
    else:
        freq = letter_frequency(ciphertext)
        top_letters = sorted(freq.items(), key=lambda x: -x[1])[:5]
        lines.append(f"\nTop letters in ciphertext: {top_letters}")
        lines.append("Recommendation: Provide the key or cipher type for targeted decryption.")

    return '\n'.join(lines)


@tool
def tool_chi_squared_score(text: str) -> str:
    """
    Score text against expected English letter frequencies using chi-squared.

    Lower score = closer to English. Useful for evaluating Caesar brute-force
    candidates.

    Args:
        text: The candidate plaintext to score.

    Returns:
        The chi-squared score as a string (lower is better).
    """
    freq = letter_frequency(text)
    chi2 = sum(
        ((freq.get(letter, 0) - expected) ** 2) / expected
        for letter, expected in ENGLISH_FREQ.items()
        if expected > 0
    )
    return f"Chi-squared score: {chi2:.4f} (lower = more English-like)"


# ─────────────────────────────────────────────
# Analysis Agent (standalone use)
# ─────────────────────────────────────────────

ANALYSIS_TOOLS = [
    tool_letter_frequency,
    tool_index_of_coincidence,
    tool_suggest_cipher,
    tool_english_frequency_reference,
    tool_auto_crack,
    tool_chi_squared_score,
]

analysis_agent = Agent(
    system_prompt=(
        "You are the Cryptanalysis Intelligence Officer — an expert at breaking unknown "
        "ciphers through statistical analysis. You use frequency analysis, Index of "
        "Coincidence, and chi-squared scoring to identify and defeat encryption. "
        "Always use the provided tools for analysis. When asked to auto-crack a cipher, "
        "use tool_auto_crack first, then interpret and explain the results clearly. "
        "Never guess — let the math guide your conclusions."
    ),
    tools=ANALYSIS_TOOLS,
)
