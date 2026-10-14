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
from strands.models import BedrockModel

# ── Import all specialist tool lists ──────────────────────────────────────────
from agents.classical_cipher_agent import CLASSICAL_TOOLS
from agents.modern_cipher_agent import MODERN_TOOLS
from agents.analysis_agent import ANALYSIS_TOOLS

# ── Aggregate all tools into a single flat list ───────────────────────────────
ALL_CIPHER_TOOLS = CLASSICAL_TOOLS + MODERN_TOOLS + ANALYSIS_TOOLS

# ── Model selection ───────────────────────────────────────────────────────────
# Default: Claude 3 Haiku — fast, cheap, sufficient for tool routing.
# Override with BEDROCK_MODEL_ID env var.
# Use BEDROCK_FALLBACK_MODEL_ID for complex unknown ciphers (e.g., claude-sonnet).
_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# ── System prompt ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are the Cipher Quest Command Agent — an elite cryptanalysis orchestrator
protecting unicorn rental operations from the Evil Llama Syndicate.

YOUR ONLY JOB: Identify the cipher used in a message and immediately call the correct tool.
NEVER attempt to decrypt, encode, or analyze text manually. Always use a tool.

FAST-PATH DECISION TREE (check in this order):
1. Text ends with '=' or '==' OR contains only A-Z/a-z/0-9/+/  → tool_base64_decode
2. Text is pure hex (0-9, a-f only, even length, no key given)   → tool_hex_decode
3. Cipher is explicitly named ROT13                              → tool_rot13
4. Cipher is explicitly named Caesar WITH a known shift          → tool_caesar_decrypt
5. Cipher is explicitly named Caesar but shift is UNKNOWN        → tool_caesar_brute_force
6. Cipher is Vigenère with a known key                          → tool_vigenere_decrypt
7. Cipher is Atbash                                              → tool_atbash
8. Cipher is Playfair with a known key                          → tool_playfair_decrypt
9. Cipher is Rail Fence with known rails                        → tool_rail_fence_decrypt
10. Cipher is Rail Fence but rails UNKNOWN                       → tool_rail_fence_brute_force
11. Cipher is XOR with a known key (hex input)                   → tool_xor_decrypt
12. Cipher type is UNKNOWN                                       → tool_auto_crack first,
    then follow up with specific tools based on its suggestion

RESPONSE FORMAT:
- State: cipher type detected
- State: key/shift used (if applicable)
- State: plaintext result
- Check if the result could itself be encrypted (multi-layer) and re-process if needed

The fate of unicorn rentals everywhere depends on your speed and accuracy. 🦄"""

# ── Cipher Command Agent ──────────────────────────────────────────────────────
_bedrock_model = BedrockModel(
    model_id=_MODEL_ID,
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
)

agent = Agent(
    model=_bedrock_model,
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
