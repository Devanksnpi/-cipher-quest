"""
lambda_handler.py — AWS Lambda / AgentCore entrypoint for Cipher Quest.

This is the runtime entrypoint referenced by agentcore/agentcore.json.
It wraps the cipher_command_agent in a Lambda-compatible handler that
AgentCore uses to serve requests.

Expected event format:
    {
        "prompt": "Decrypt this Caesar cipher with shift 13: Uryyb Jbeyq"
    }

    or the AgentCore standard input:
    {
        "inputText": "...",
        "sessionId": "...",       # optional
        "sessionAttributes": {}   # optional
    }
"""

import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context) -> dict:
    """
    Lambda handler — AgentCore entrypoint for Cipher Quest.

    Accepts both simple {"prompt": "..."} and AgentCore-standard
    {"inputText": "..."} event shapes.

    Returns:
        {
            "statusCode": 200,
            "body": "<agent response string>",
            "sessionId": "..."
        }
    """
    logger.info("Cipher Quest invoked. Event keys: %s", list(event.keys()))

    # Extract the user's message from the event
    prompt = (
        event.get("prompt")
        or event.get("inputText")
        or event.get("input")
        or event.get("query")
        or ""
    )

    if not prompt:
        logger.warning("No prompt found in event: %s", json.dumps(event))
        return {
            "statusCode": 400,
            "body": "Missing prompt. Provide 'prompt' or 'inputText' in the event.",
        }

    # Lazy import to avoid cold-start cost if the module isn't needed
    try:
        from cipher_command_agent import agent  # noqa: PLC0415

        logger.info("Routing to cipher_command_agent: %s", prompt[:120])
        result = agent(prompt)

        # Strands Agent returns a complex object; get the string representation
        response_text = str(result)

        logger.info("Agent response length: %d chars", len(response_text))

        return {
            "statusCode": 200,
            "body": response_text,
            "sessionId": event.get("sessionId", ""),
        }

    except Exception as exc:
        logger.exception("Cipher Quest agent error")
        return {
            "statusCode": 500,
            "body": f"Agent error: {str(exc)}",
        }
