#!/usr/bin/env bash
# deploy_cipher_agents.sh — Deploy the Cipher Quest anti-llama crypto squad
# to AWS Bedrock AgentCore.
#
# Usage:
#   ./deploy_cipher_agents.sh
#
# Prerequisites:
#   - AWS credentials configured (aws configure)
#   - AgentCore CLI installed: npm install -g @aws/agentcore@0.9.1
#   - Python venv active with requirements installed

set -euo pipefail

# ── Colours ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Colour

banner() { echo -e "\n${CYAN}${BOLD}═══ $* ═══${NC}"; }
ok()     { echo -e "${GREEN}✅  $*${NC}"; }
warn()   { echo -e "${YELLOW}⚠️   $*${NC}"; }
fail()   { echo -e "${RED}❌  $*${NC}"; exit 1; }

# ── Phase 0: Verify we're in the right directory ───────────────────────────
banner "Phase 0 — Pre-flight checks"

[[ -f "agentcore/agentcore.json" ]] || fail "agentcore/agentcore.json not found. Run from the cipher-quest root."
[[ -f "lambda_handler.py" ]]        || fail "lambda_handler.py not found."
[[ -f "cipher_command_agent.py" ]]  || fail "cipher_command_agent.py not found."
[[ -f "requirements.txt" ]]         || fail "requirements.txt not found."
ok "Project structure verified"

# ── Phase 0.5: Check agentcore CLI ────────────────────────────────────────
banner "Phase 0.5 — AgentCore CLI check"

if ! command -v agentcore &> /dev/null; then
  warn "agentcore CLI not found. Installing @aws/agentcore@0.9.1 ..."
  npm install -g @aws/agentcore@0.9.1
  hash -r
fi

AGENTCORE_VERSION=$(agentcore --version 2>/dev/null || echo "unknown")
ok "AgentCore CLI: ${AGENTCORE_VERSION}"

# ── Phase 1: AWS credentials check ────────────────────────────────────────
banner "Phase 1 — AWS credentials"

if ! aws sts get-caller-identity &> /dev/null; then
  fail "AWS credentials not configured. Run: aws configure"
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_DEFAULT_REGION:-${AWS_REGION:-us-east-1}}
ok "AWS Account: ${ACCOUNT_ID} | Region: ${AWS_REGION}"

# ── Phase 2: Validate agentcore.json ──────────────────────────────────────
banner "Phase 2 — Validate agentcore configuration"

agentcore validate && ok "agentcore.json is valid" || fail "agentcore validate failed. Check agentcore/agentcore.json."

# ── Phase 3: Deploy ────────────────────────────────────────────────────────
banner "Phase 3 — Deploying cipher_quest_agent runtime"

echo -e "${YELLOW}Deploying... this may take 2-5 minutes.${NC}"
agentcore deploy

ok "Deployment complete"

# ── Phase 4: Check status and extract ARN ─────────────────────────────────
banner "Phase 4 — Runtime status"

echo -e "${YELLOW}Fetching runtime status...${NC}"

STATUS_JSON=$(agentcore status --runtime cipher_quest_agent --json 2>/dev/null || echo '{}')
echo "${STATUS_JSON}" | python3 -m json.tool 2>/dev/null || echo "${STATUS_JSON}"

# Try to extract the ARN
RUNTIME_ARN=$(echo "${STATUS_JSON}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
# Try common ARN fields
for key in ('arn', 'runtimeArn', 'agentRuntimeArn', 'resourceArn'):
    if key in data:
        print(data[key])
        break
" 2>/dev/null || echo "")

if [[ -n "${RUNTIME_ARN}" ]]; then
  echo ""
  echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}${BOLD}║   🦄  CIPHER QUEST DEPLOYMENT SUCCESSFUL!  🦄            ║${NC}"
  echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "${CYAN}${BOLD}Runtime ARN (submit this in the quest UI):${NC}"
  echo -e "${BOLD}${RUNTIME_ARN}${NC}"
  echo ""
else
  warn "Could not auto-extract ARN from status output."
  echo "Run manually to get the ARN:"
  echo "  agentcore status --runtime cipher_quest_agent --json"
fi

echo ""
echo -e "${CYAN}Useful commands:${NC}"
echo "  agentcore validate"
echo "  agentcore deploy"
echo "  agentcore status --runtime cipher_quest_agent --json"
echo ""
echo -e "${YELLOW}If things go sideways:${NC}"
echo "  • Check AWS creds:  aws configure"
echo "  • CloudWatch logs:  Look for log group with 'agentcore' in the name"
echo "  • Validate config:  agentcore validate"
echo ""
echo -e "${GREEN}The fate of unicorn rentals is in safe hands. 🦄⚔️🦙${NC}"
