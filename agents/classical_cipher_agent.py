"""
classical_cipher_agent.py — Classical cipher tools for Cipher Quest.

Exposes Caesar, ROT13, Vigenère, Atbash, and Playfair as @tool-decorated
functions that the Swarm orchestrator (cipher_command_agent) can call.

All implementations delegate to common_algos.py — deterministic, no LLM.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from strands import Agent, tool
from agents.common_algos import (
    caesar_encrypt,
    caesar_decrypt,
    caesar_brute_force,
    rot13,
    vigenere_encrypt,
    vigenere_decrypt,
    atbash,
    playfair_encrypt,
    playfair_decrypt,
)


# ─────────────────────────────────────────────
# Caesar tools
# ─────────────────────────────────────────────

@tool
def tool_caesar_encrypt(text: str, shift: int) -> str:
    """
    Encrypt text using the Caesar cipher.

    Args:
        text: The plaintext to encrypt.
        shift: Number of positions to shift (0-25).

    Returns:
        The Caesar-encrypted ciphertext.
    """
    return caesar_encrypt(text, shift)


@tool
def tool_caesar_decrypt(text: str, shift: int) -> str:
    """
    Decrypt text that was encrypted with the Caesar cipher.

    Args:
        text: The ciphertext to decrypt.
        shift: The shift used during encryption (0-25).

    Returns:
        The decrypted plaintext.
    """
    return caesar_decrypt(text, shift)


@tool
def tool_caesar_brute_force(ciphertext: str) -> str:
    """
    Try all 26 Caesar shifts on ciphertext and return all candidates.

    Args:
        ciphertext: The ciphertext to brute-force.

    Returns:
        A formatted string listing all 26 shift/plaintext pairs.
    """
    results = caesar_brute_force(ciphertext)
    lines = [f"Shift {r['shift']:2d}: {r['plaintext']}" for r in results]
    return '\n'.join(lines)


# ─────────────────────────────────────────────
# ROT13 tool
# ─────────────────────────────────────────────

@tool
def tool_rot13(text: str) -> str:
    """
    Apply ROT13 to text (self-inverse: encrypts and decrypts with the same call).

    Args:
        text: The text to transform.

    Returns:
        ROT13-transformed text.
    """
    return rot13(text)


# ─────────────────────────────────────────────
# Vigenère tools
# ─────────────────────────────────────────────

@tool
def tool_vigenere_encrypt(text: str, key: str) -> str:
    """
    Encrypt text using the Vigenère cipher.

    Args:
        text: The plaintext to encrypt.
        key: The keyword (letters only; case-insensitive).

    Returns:
        The Vigenère-encrypted ciphertext.
    """
    return vigenere_encrypt(text, key)


@tool
def tool_vigenere_decrypt(text: str, key: str) -> str:
    """
    Decrypt text that was encrypted with the Vigenère cipher.

    Args:
        text: The ciphertext to decrypt.
        key: The keyword used during encryption.

    Returns:
        The decrypted plaintext.
    """
    return vigenere_decrypt(text, key)


# ─────────────────────────────────────────────
# Atbash tool
# ─────────────────────────────────────────────

@tool
def tool_atbash(text: str) -> str:
    """
    Apply Atbash substitution (A↔Z, B↔Y, …). Self-inverse.

    Args:
        text: The text to transform.

    Returns:
        Atbash-transformed text.
    """
    return atbash(text)


# ─────────────────────────────────────────────
# Playfair tools
# ─────────────────────────────────────────────

@tool
def tool_playfair_encrypt(text: str, key: str) -> str:
    """
    Encrypt text using the Playfair cipher.

    Args:
        text: The plaintext to encrypt (letters only; J treated as I).
        key: The keyword for building the 5×5 key square.

    Returns:
        The Playfair-encrypted ciphertext (uppercase, no spaces).
    """
    return playfair_encrypt(text, key)


@tool
def tool_playfair_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt text that was encrypted with the Playfair cipher.

    Args:
        ciphertext: The ciphertext (letters only, even length).
        key: The keyword used during encryption.

    Returns:
        The decrypted plaintext (may contain filler X characters).
    """
    return playfair_decrypt(ciphertext, key)


# ─────────────────────────────────────────────
# Classical Cipher Agent (standalone use)
# ─────────────────────────────────────────────

CLASSICAL_TOOLS = [
    tool_caesar_encrypt,
    tool_caesar_decrypt,
    tool_caesar_brute_force,
    tool_rot13,
    tool_vigenere_encrypt,
    tool_vigenere_decrypt,
    tool_atbash,
    tool_playfair_encrypt,
    tool_playfair_decrypt,
]

classical_cipher_agent = Agent(
    system_prompt=(
        "You are the Classical Cipher Specialist — an expert in historical encryption "
        "techniques. You handle Caesar, ROT13, Vigenère, Atbash, and Playfair ciphers. "
        "Always use the provided tools for encryption and decryption; never attempt to "
        "perform cipher math yourself. When asked to brute-force, use the brute-force "
        "tool and identify the most likely plaintext from the results."
    ),
    tools=CLASSICAL_TOOLS,
)
