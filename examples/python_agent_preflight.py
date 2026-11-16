"""Call Pacta's free remote MCP server from a Python agent before it touches a contract (stdlib only).

  python3 python_agent_preflight.py                      # USDC on Base
  python3 python_agent_preflight.py ethereum 0x...       # any contract on Ethereum or Base
  PACTA_MCP_URL=http://127.0.0.1:8787/mcp python3 ...    # another endpoint (e.g. a local test server)

Sends one JSON-RPC 2.0 `tools/call` for `pacta_check_preflight` to the Streamable HTTP endpoint (stateless: no session,
no API key, no wallet) and prints the verdict. Exit code 0 = the call succeeded (whatever the verdict), 1 = error.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

MCP_URL = "https://pacta-x402.pacta.workers.dev/mcp"

# Three required, non-personal fields on every free tools/call (closed enums; see the server's tool schema):
CALLER = {
    "caller_agent": "python-agent-example",        # lowercase slug naming your agent / framework, never a person
    "requester_role": "autonomous_agent",          # autonomous_agent | defi_developer | risk_curator_analyst | ...
    "caller_purpose": "pre_trade_safety",          # pre_trade_safety | collateral_due_diligence | security_audit | ...
}


def call_tool(url, name, arguments, request_id=1, timeout=30):
    """One MCP tools/call over HTTP -> the tool result object (structuredContent when present, else the parsed text content)."""
    body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": "tools/call",
                       "params": {"name": name, "arguments": arguments}}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                                          "User-Agent": "defi-control-plane-mcp-example/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        msg = json.load(resp)
    if "error" in msg:
        raise RuntimeError(f"JSON-RPC error {msg['error'].get('code')}: {msg['error'].get('message')}")
    result = msg.get("result") or {}
    if result.get("isError"):
        raise RuntimeError("tool error: " + " ".join(c.get("text", "") for c in result.get("content", [])))
    if isinstance(result.get("structuredContent"), dict):
        return result["structuredContent"]
    text = "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
    return json.loads(text) if text else {}


def main(argv):
    chain = argv[1] if len(argv) > 1 else "base"
    address = argv[2] if len(argv) > 2 else "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"     # USDC on Base
    if chain not in ("ethereum", "base") or not re.fullmatch(r"0x[0-9a-fA-F]{40}", address):
        print("usage: python_agent_preflight.py [ethereum|base] [0x contract address]", file=sys.stderr)
        return 1
    url = os.environ.get("PACTA_MCP_URL", MCP_URL)
    try:
        out = call_tool(url, "pacta_check_preflight", {"chain": chain, "address": address, **CALLER})
    except (urllib.error.URLError, RuntimeError, ValueError) as e:
        print(f"preflight failed: {e}", file=sys.stderr)
        return 1
    print(f"verdict: {out.get('verdict')}  (chain {out.get('chain')}, address {out.get('address')})")
    for k in ("riskScore", "pinnedBlock"):
        if k in out:
            print(f"{k}: {out[k]}")
    print(json.dumps(out, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
