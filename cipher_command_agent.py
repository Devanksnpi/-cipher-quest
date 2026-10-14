"""
cipher_command_agent.py — Swarm orchestrator for Cipher Quest.

This is the top-level command agent. It uses Strands Agents' Swarm pattern
to route cryptography requests to the appropriate specialist tools:

  - Classical ciphers  → Caesar, ROT13, Vigenère, Atbash, Playfair tools
  - Modern encoding    → Base64, XOR, Rail Fence tools
  - Cryptanalysis      → frequency analysis, IC, chi-squared, auto-crack tools

The Swarm aggregates ALL tool functions from all specialist agents and gives
the orchestrating LLM a single flat tool namespace to pick from.

Usage:
    from cipher_command_agent import agent
    result = agent("Decrypt this Base64: SGVsbG8gV29ybGQ=")
    print(result)
"""

import os

from strands import Agent

# ── Import all specialist tool lists ──────────────────────────────────────────
from agents.classical_cipher_agent import CLASSICAL_TOOLS
from agents.modern_cipher_agent import MODERN_TOOLS
from agents.analysis_agent import ANALYSIS_TOOLS

# ── Aggregate all tools into a single flat list ───────────────────────────────
ALL_CIPHER_TOOLS = CLASSICAL_TOOLS + MODERN_TOOLS + ANALYSIS_TOOLS

# ── Model selection ───────────────────────────────────────────────────────────
_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5")

# ── System prompt ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are the Cipher Quest Command Agent — the field commander of an elite
anti-llama cryptography squad. Your mission: intercept and decrypt Evil Llama Syndicate
transmissions to protect unicorn rental operations worldwide.

You have access to a full suite of cipher tools spanning classical and modern techniques:

CLASSICAL CIPHER TOOLS:
- tool_caesar_encrypt / tool_caesar_decrypt / tool_caesar_brute_force
- tool_rot13
- tool_vigenere_encrypt / tool_vigenere_decrypt
- tool_atbash
- tool_playfair_encrypt / tool_playfair_decrypt

MODERN ENCODING TOOLS:
- tool_base64_encode / tool_base64_decode
- tool_xor_encrypt / tool_xor_decrypt
- tool_rail_fence_encrypt / tool_rail_fence_decrypt / tool_rail_fence_brute_force

CRYPTANALYSIS TOOLS:
- tool_letter_frequency
- tool_index_of_coincidence
- tool_suggest_cipher
- tool_english_frequency_reference
- tool_auto_crack
- tool_chi_squared_score

RULES OF ENGAGEMENT:
1. ALWAYS use the tools — never compute ciphers manually or guess outputs.
2. When the cipher type is unknown, start with tool_suggest_cipher or tool_auto_crack.
3. For brute-force attacks, use tool_caesar_brute_force + tool_chi_squared_score to rank candidates.
4. Report your findings clearly: cipher type detected, key/shift found, and the plaintext.
5. If a transmission could be multi-layered, check the decoded output for further encryption.

The fate of unicorn rentals everywhere depends on your technical accuracy. Be precise. 🦄"""

# ── Cipher Command Agent ──────────────────────────────────────────────────────
agent = Agent(
    system_prompt=_SYSTEM_PROMPT,
    tools=ALL_CIPHER_TOOLS,
)


# ── CLI usage ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        print("Cipher Quest Command Agent — Interactive Mode")
        print("Type your cryptographic request (or 'quit' to exit).")
        print("-" * 60)
        while True:
            try:
                query = input("\n🔐 Agent> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nMission complete. 🦄")
                sys.exit(0)
            if query.lower() in ('quit', 'exit', 'q'):
                print("Mission complete. 🦄")
                sys.exit(0)
            if not query:
                continue
            result = agent(query)
            print(f"\n{result}")
        sys.exit(0)

    result = agent(query)
    print(result)
