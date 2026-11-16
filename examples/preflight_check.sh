#!/usr/bin/env bash
# Free pre-execution check of one contract over REST (no API key, no wallet).
#   ./preflight_check.sh <ethereum|base> <0x contract address>
# Prints the JSON verdict: who can change the contract (proxy admin, timelock, Safe), pinned to a block hash.
set -euo pipefail

API="${PACTA_API_URL:-https://pacta-x402.pacta.workers.dev}"
CHAIN="${1:-base}"
ADDRESS="${2:-0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913}"   # default: USDC on Base

case "$CHAIN" in
  ethereum|base) ;;
  *) echo "chain must be ethereum or base" >&2; exit 2 ;;
esac
if [[ ! "$ADDRESS" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
  echo "address must be a 0x-prefixed 20-byte hex address" >&2
  exit 2
fi

# caller_agent / requester_role / caller_purpose are optional over REST and describe the workflow, never a person.
# Always send a User-Agent: Cloudflare's edge refuses some default library agents (error 1010) before the API answers.
curl -fsS --max-time 30 -A "${PACTA_USER_AGENT:-my-agent/1.0}" \
  "${API}/v1/check/preflight?chain=${CHAIN}&address=${ADDRESS}&caller_agent=shell-example&requester_role=defi_developer&caller_purpose=integration_testing"
echo
