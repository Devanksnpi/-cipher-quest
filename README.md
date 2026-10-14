# 🔐 Cipher Quest — Anti-Llama Crypto Squad

> *Elite intelligence agents master the art of cryptography to protect national (unicorn rental) security.*

An AWS Bedrock AgentCore multi-agent system that deploys specialized cipher-breaking AI agents to intercept and decrypt Evil Llama Syndicate transmissions.

## Architecture

```
cipher-quest/
├── agentcore/
│   └── agentcore.json          # AgentCore runtime config
├── agents/
│   ├── common_algos.py         # Deterministic cipher primitives (no LLM)
│   ├── classical_cipher_agent.py   # Classical cipher tools (Caesar, Vigenere, Atbash…)
│   ├── modern_cipher_agent.py      # Modern encoding tools (Base64, XOR, Rail Fence…)
│   └── analysis_agent.py           # Frequency/pattern analysis tools
├── cipher_command_agent.py     # Swarm orchestrator — wires all tool agents
├── lambda_handler.py           # AgentCore entrypoint (Lambda handler)
├── deploy_cipher_agents.sh     # Deployment script
├── requirements.txt
└── README.md
```

## Multi-Agent Design

```
User Request
     │
     ▼
cipher_command_agent  (Swarm orchestrator — claude-sonnet-4-5)
     │
     ├──► classical_cipher_agent tools  (Caesar, Vigenere, ROT13, Atbash, Playfair)
     ├──► modern_cipher_agent tools     (Base64, XOR, Rail Fence)
     └──► analysis_agent tools          (frequency analysis, index of coincidence, auto-detect)
```

The `cipher_command_agent` uses **Strands Agents Swarm** to route tasks to the right specialist. Each specialist exposes its capabilities as `@tool`-decorated functions that the orchestrator can call.

## Cipher Coverage

| Cipher | Encrypt | Decrypt | Agent |
|--------|---------|---------|-------|
| Caesar | ✅ | ✅ | classical |
| Vigenère | ✅ | ✅ | classical |
| ROT13 | ✅ | ✅ | classical |
| Atbash | ✅ | ✅ | classical |
| Playfair | ✅ | ✅ | classical |
| Base64 | ✅ | ✅ | modern |
| XOR | ✅ | ✅ | modern |
| Rail Fence | ✅ | ✅ | modern |
| Frequency Analysis | — | — | analysis |
| Auto-Detect | — | — | analysis |

## Setup

### Prerequisites
- Python 3.12+
- Node.js 20+ (for AgentCore CLI)
- AWS credentials configured (`aws configure`)

### Install AgentCore CLI
```bash
node --version                     # must be 20+
npm install -g @aws/agentcore@0.9.1
hash -r
agentcore --version
```

If `agentcore --version` reports `No such option: --version`, a legacy version of the CLI
is installed. Remove it first:
```bash
npm uninstall -g agentcore          # remove legacy
npm install -g @aws/agentcore@0.9.1 # install correct package
hash -r
agentcore --version
```

### Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Deploy
```bash
./deploy_cipher_agents.sh
```

The script will:
1. Validate `agentcore/agentcore.json`
2. Deploy the `cipher_quest_agent` runtime
3. Print the runtime ARN — submit that ARN in the quest UI

## Manual AgentCore Commands
```bash
agentcore validate
agentcore deploy
agentcore status --runtime cipher_quest_agent --json
```

## Usage Example

```python
from cipher_command_agent import agent

# Decrypt an intercepted llama transmission
result = agent("Decrypt this Caesar cipher with shift 13: 'Uryyb Jbeyq'")
print(result)
# → Hello World

# Auto-detect and crack an unknown cipher
result = agent("Analyze and decrypt: 'SGVsbG8gV29ybGQ='")
print(result)
# → Hello World (Base64 detected)
```

## Troubleshooting

- **AWS credentials**: `aws configure`
- **AgentCore logs**: CloudWatch log group containing `agentcore`
- **Validate config**: `agentcore validate`
- **Check status**: `agentcore status --runtime cipher_quest_agent --json`

---
*The fate of magical transportation depends on you, agent. 🦄⚔️🦙*
