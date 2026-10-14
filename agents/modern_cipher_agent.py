"""
modern_cipher_agent.py — Modern encoding cipher tools for Cipher Quest.

Exposes Base64, XOR, and Rail Fence as @tool-decorated functions that the
Swarm orchestrator (cipher_command_agent) can call.

All implementations delegate to common_algos.py — deterministic, no LLM.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from strands import Agent, tool
from agents.common_algos import (
    base64_encode,
    base64_decode,
    xor_encrypt,
    xor_decrypt,
    rail_fence_encrypt,
    rail_fence_decrypt,
)


# ─────────────────────────────────────────────
# Base64 tools
# ─────────────────────────────────────────────

@tool
def tool_base64_encode(text: str) -> str:
    """
    Encode a string to Base64.

    Args:
        text: The UTF-8 string to encode.

    Returns:
        Base64-encoded string.
    """
    return base64_encode(text)


@tool
def tool_base64_decode(encoded: str) -> str:
    """
    Decode a Base64-encoded string back to plaintext.

    Args:
        encoded: The Base64-encoded string (padding optional).

    Returns:
        The decoded UTF-8 string.
    """
    return base64_decode(encoded)


# ─────────────────────────────────────────────
# XOR tools
# ─────────────────────────────────────────────

@tool
def tool_xor_encrypt(text: str, key: str) -> str:
    """
    Encrypt text using XOR with the given key.

    The output is hex-encoded. The key is repeated to match text length.

    Args:
        text: The plaintext to encrypt.
        key: The XOR key string (non-empty).

    Returns:
        Hex-encoded ciphertext.
    """
    return xor_encrypt(text, key)


@tool
def tool_xor_decrypt(hex_ciphertext: str, key: str) -> str:
    """
    Decrypt a hex-encoded XOR ciphertext using the given key.

    Args:
        hex_ciphertext: The hex-encoded ciphertext produced by XOR encryption.
        key: The XOR key string used during encryption.

    Returns:
        The decrypted plaintext.
    """
    return xor_decrypt(hex_ciphertext, key)


# ─────────────────────────────────────────────
# Rail Fence tools
# ─────────────────────────────────────────────

@tool
def tool_rail_fence_encrypt(text: str, rails: int) -> str:
    """
    Encrypt text using the Rail Fence (zigzag) transposition cipher.

    Args:
        text: The plaintext to encrypt.
        rails: Number of rails (must be ≥ 2).

    Returns:
        The Rail Fence-encrypted ciphertext.
    """
    return rail_fence_encrypt(text, rails)


@tool
def tool_rail_fence_decrypt(ciphertext: str, rails: int) -> str:
    """
    Decrypt a Rail Fence cipher.

    Args:
        ciphertext: The ciphertext to decrypt.
        rails: Number of rails used during encryption (must be ≥ 2).

    Returns:
        The decrypted plaintext.
    """
    return rail_fence_decrypt(ciphertext, rails)


@tool
def tool_rail_fence_brute_force(ciphertext: str, max_rails: int = 10) -> str:
    """
    Try Rail Fence decryption with 2 through max_rails rails.

    Args:
        ciphertext: The ciphertext to brute-force.
        max_rails: Maximum number of rails to try (default 10).

    Returns:
        A formatted string listing each rail count and its decryption.
    """
    lines = []
    for r in range(2, max_rails + 1):
        plaintext = rail_fence_decrypt(ciphertext, r)
        lines.append(f"Rails {r:2d}: {plaintext}")
    return '\n'.join(lines)


# ─────────────────────────────────────────────
# Modern Cipher Agent (standalone use)
# ─────────────────────────────────────────────

MODERN_TOOLS = [
    tool_base64_encode,
    tool_base64_decode,
    tool_xor_encrypt,
    tool_xor_decrypt,
    tool_rail_fence_encrypt,
    tool_rail_fence_decrypt,
    tool_rail_fence_brute_force,
]

modern_cipher_agent = Agent(
    system_prompt=(
        "You are the Modern Encoding Specialist — an expert in contemporary cipher "
        "and encoding techniques. You handle Base64 encoding/decoding, XOR encryption, "
        "and Rail Fence transposition ciphers. Always use the provided tools; never "
        "attempt to perform encoding math yourself. For XOR, remember the output is "
        "hex-encoded and the same key is needed for decryption."
    ),
    tools=MODERN_TOOLS,
)
