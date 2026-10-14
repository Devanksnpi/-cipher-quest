"""
common_algos.py — Deterministic cipher primitives for Cipher Quest.

All functions here are pure algorithmic implementations — NO LLM calls.
They produce consistent, reproducible results given the same inputs.
These are imported by the cipher agents and exposed as @tool functions.
"""

import base64
import string
from typing import Union


# ─────────────────────────────────────────────
# Caesar Cipher
# ─────────────────────────────────────────────

def caesar_encrypt(text: str, shift: int) -> str:
    """Encrypt plaintext with a Caesar cipher using the given shift (0-25)."""
    shift = shift % 26
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)


def caesar_decrypt(text: str, shift: int) -> str:
    """Decrypt a Caesar cipher by reversing the shift."""
    return caesar_encrypt(text, -shift)


def caesar_brute_force(ciphertext: str) -> list[dict]:
    """Try all 26 Caesar shifts. Returns list of {shift, plaintext}."""
    return [
        {"shift": shift, "plaintext": caesar_decrypt(ciphertext, shift)}
        for shift in range(26)
    ]


# ─────────────────────────────────────────────
# ROT13
# ─────────────────────────────────────────────

def rot13(text: str) -> str:
    """Apply ROT13 transformation (self-inverse — same function encrypts and decrypts)."""
    return caesar_encrypt(text, 13)


# ─────────────────────────────────────────────
# Vigenère Cipher
# ─────────────────────────────────────────────

def _clean_key(key: str) -> str:
    """Strip non-alpha chars from key and uppercase."""
    return ''.join(ch.upper() for ch in key if ch.isalpha())


def vigenere_encrypt(text: str, key: str) -> str:
    """Encrypt plaintext with a Vigenère cipher using the given key."""
    key = _clean_key(key)
    if not key:
        raise ValueError("Vigenère key must contain at least one letter.")
    result = []
    key_idx = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            key_idx += 1
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """Decrypt a Vigenère cipher using the given key."""
    key = _clean_key(key)
    if not key:
        raise ValueError("Vigenère key must contain at least one letter.")
    result = []
    key_idx = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base - shift) % 26 + base))
            key_idx += 1
        else:
            result.append(ch)
    return ''.join(result)


# ─────────────────────────────────────────────
# Atbash Cipher
# ─────────────────────────────────────────────

def atbash(text: str) -> str:
    """Apply Atbash substitution (A↔Z, B↔Y, …). Self-inverse."""
    result = []
    for ch in text:
        if ch.isupper():
            result.append(chr(ord('Z') - (ord(ch) - ord('A'))))
        elif ch.islower():
            result.append(chr(ord('z') - (ord(ch) - ord('a'))))
        else:
            result.append(ch)
    return ''.join(result)


# ─────────────────────────────────────────────
# Base64
# ─────────────────────────────────────────────

def base64_encode(text: str) -> str:
    """Encode a UTF-8 string to Base64."""
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def base64_decode(encoded: str) -> str:
    """Decode a Base64 string to UTF-8. Raises ValueError on bad input."""
    # Add padding if missing
    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += '=' * padding
    try:
        return base64.b64decode(encoded).decode('utf-8')
    except Exception as exc:
        raise ValueError(f"Invalid Base64 input: {exc}") from exc


# ─────────────────────────────────────────────
# XOR Cipher
# ─────────────────────────────────────────────

def xor_encrypt(text: str, key: str) -> str:
    """
    XOR-encrypt text with key, returning a hex-encoded ciphertext.
    Key is repeated to match text length.
    """
    if not key:
        raise ValueError("XOR key must be non-empty.")
    encrypted = bytes(
        ord(ch) ^ ord(key[i % len(key)])
        for i, ch in enumerate(text)
    )
    return encrypted.hex()


def xor_decrypt(hex_ciphertext: str, key: str) -> str:
    """
    XOR-decrypt a hex-encoded ciphertext with the given key.
    Key is repeated to match ciphertext length.
    """
    if not key:
        raise ValueError("XOR key must be non-empty.")
    try:
        cipher_bytes = bytes.fromhex(hex_ciphertext)
    except ValueError as exc:
        raise ValueError(f"Invalid hex ciphertext: {exc}") from exc
    decrypted = bytes(
        b ^ ord(key[i % len(key)])
        for i, b in enumerate(cipher_bytes)
    )
    return decrypted.decode('utf-8', errors='replace')


# ─────────────────────────────────────────────
# Rail Fence Cipher
# ─────────────────────────────────────────────

def rail_fence_encrypt(text: str, rails: int) -> str:
    """Encrypt text using the Rail Fence (zigzag) cipher with the given number of rails."""
    if rails < 2:
        return text
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for ch in text:
        fence[rail].append(ch)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return ''.join(''.join(r) for r in fence)


def rail_fence_decrypt(ciphertext: str, rails: int) -> str:
    """Decrypt a Rail Fence cipher with the given number of rails."""
    if rails < 2:
        return ciphertext
    n = len(ciphertext)
    # Determine which rail each position belongs to
    pattern = []
    rail = 0
    direction = 1
    for i in range(n):
        pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction

    # Count characters per rail and slice ciphertext accordingly
    indices = sorted(range(n), key=lambda i: pattern[i])
    result = [''] * n
    pos = 0
    for idx in indices:
        result[idx] = ciphertext[pos]
        pos += 1
    return ''.join(result)


# ─────────────────────────────────────────────
# Playfair Cipher
# ─────────────────────────────────────────────

def _build_playfair_square(key: str) -> list[list[str]]:
    """Build the 5×5 Playfair key square (I/J merged)."""
    key = key.upper().replace('J', 'I')
    seen: set[str] = set()
    sequence = []
    for ch in key + string.ascii_uppercase:
        if ch == 'J':
            continue
        if ch not in seen:
            seen.add(ch)
            sequence.append(ch)
    square = [sequence[i * 5:(i + 1) * 5] for i in range(5)]
    return square


def _playfair_position(square: list[list[str]], ch: str) -> tuple[int, int]:
    for r, row in enumerate(square):
        if ch in row:
            return r, row.index(ch)
    raise ValueError(f"Character '{ch}' not found in Playfair square.")


def _playfair_prepare(text: str) -> list[str]:
    """Prepare plaintext: uppercase, replace J→I, split into digraphs with X fillers."""
    text = text.upper().replace('J', 'I')
    letters = [ch for ch in text if ch.isalpha()]
    pairs = []
    i = 0
    while i < len(letters):
        a = letters[i]
        if i + 1 >= len(letters):
            pairs.extend([a, 'X'])
            i += 1
        elif letters[i + 1] == a:
            pairs.extend([a, 'X'])
            i += 1
        else:
            pairs.extend([a, letters[i + 1]])
            i += 2
    return pairs


def playfair_encrypt(text: str, key: str) -> str:
    """Encrypt text using the Playfair cipher with the given key."""
    square = _build_playfair_square(key)
    pairs = _playfair_prepare(text)
    result = []
    for i in range(0, len(pairs), 2):
        r1, c1 = _playfair_position(square, pairs[i])
        r2, c2 = _playfair_position(square, pairs[i + 1])
        if r1 == r2:
            result.extend([square[r1][(c1 + 1) % 5], square[r2][(c2 + 1) % 5]])
        elif c1 == c2:
            result.extend([square[(r1 + 1) % 5][c1], square[(r2 + 1) % 5][c2]])
        else:
            result.extend([square[r1][c2], square[r2][c1]])
    return ''.join(result)


def playfair_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt a Playfair cipher with the given key."""
    square = _build_playfair_square(key)
    ciphertext = ciphertext.upper().replace('J', 'I')
    letters = [ch for ch in ciphertext if ch.isalpha()]
    result = []
    for i in range(0, len(letters), 2):
        r1, c1 = _playfair_position(square, letters[i])
        r2, c2 = _playfair_position(square, letters[i + 1])
        if r1 == r2:
            result.extend([square[r1][(c1 - 1) % 5], square[r2][(c2 - 1) % 5]])
        elif c1 == c2:
            result.extend([square[(r1 - 1) % 5][c1], square[(r2 - 1) % 5][c2]])
        else:
            result.extend([square[r1][c2], square[r2][c1]])
    return ''.join(result)


# ─────────────────────────────────────────────
# Frequency Analysis
# ─────────────────────────────────────────────

# English letter frequencies (approximate %)
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.49,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07,
}


def letter_frequency(text: str) -> dict[str, float]:
    """Return letter frequency percentages for the given text (case-insensitive)."""
    letters = [ch.upper() for ch in text if ch.isalpha()]
    total = len(letters)
    if total == 0:
        return {}
    counts: dict[str, int] = {}
    for ch in letters:
        counts[ch] = counts.get(ch, 0) + 1
    return {ch: round(count / total * 100, 2) for ch, count in sorted(counts.items())}


def index_of_coincidence(text: str) -> float:
    """
    Compute the Index of Coincidence (IC) for text.
    English plaintext ≈ 0.065; random text ≈ 0.038.
    """
    letters = [ch.upper() for ch in text if ch.isalpha()]
    n = len(letters)
    if n < 2:
        return 0.0
    counts: dict[str, int] = {}
    for ch in letters:
        counts[ch] = counts.get(ch, 0) + 1
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return round(numerator / denominator, 6)


def suggest_cipher(text: str) -> str:
    """
    Heuristic guess at what cipher might have been used, based on IC and character set.
    Returns a string hint.
    """
    # Check Base64
    import re
    stripped = text.strip().rstrip('=')
    if re.fullmatch(r'[A-Za-z0-9+/]+', stripped) and len(text) % 4 in (0, 2, 3):
        try:
            decoded = base64.b64decode(text + '==').decode('utf-8')
            if decoded.isprintable():
                return "Base64"
        except Exception:
            pass

    # Check hex (XOR output)
    if re.fullmatch(r'[0-9a-fA-F]+', text) and len(text) % 2 == 0:
        return "XOR (hex-encoded)"

    # IC-based
    ic = index_of_coincidence(text)
    letters_only = ''.join(ch for ch in text if ch.isalpha())
    if len(letters_only) == 0:
        return "Unknown"

    if ic > 0.060:
        return "Caesar or Atbash (monoalphabetic substitution)"
    elif ic > 0.045:
        return "Vigenère or Playfair (polyalphabetic / digraphic)"
    else:
        return "Rail Fence or other transposition cipher"
