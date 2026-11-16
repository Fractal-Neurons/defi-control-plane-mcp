<img src="https://pacta.wtf/logo.svg" alt="Pacta" width="56" height="56" align="left">

# defi-control-plane-mcp
<br clear="left">

Starter kit for the free **Pacta by Fractal Neurons** remote MCP server: before an AI agent deposits into, approves or
calls a DeFi contract, it asks who can change that contract's rules (proxy admin, timelock delay, Safe threshold,
pause / blacklist / upgrade roles) and gets a verdict pinned to a block hash. Zero install, no API key, no wallet.

## 1-line install

```bash
claude mcp add --transport http pacta https://pacta-x402.pacta.workers.dev/mcp
```

Any MCP client that speaks Streamable HTTP can use the same URL. The server is stateless JSON-RPC 2.0: `tools/call`
works without a session.

## Examples

| file | what it does |
| :--- | :--- |
| [`examples/cursor_mcp.json`](examples/cursor_mcp.json) | Cursor `mcp.json` entry (remote URL) |
| [`examples/claude_desktop_config.json`](examples/claude_desktop_config.json) | Claude Desktop entry through the `mcp-remote` stdio bridge (`npx -y mcp-remote <url>`) |
| [`examples/preflight_check.sh`](examples/preflight_check.sh) | `curl` the REST twin: `./examples/preflight_check.sh base 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| [`examples/python_agent_preflight.py`](examples/python_agent_preflight.py) | stdlib-only Python: one JSON-RPC `tools/call` of `pacta_check_preflight`, prints the verdict |

```bash
python3 examples/python_agent_preflight.py ethereum 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```

## Caller fields

Every free MCP `tools/call` accepts three optional, non-personal attribution fields that describe the workflow, never a person (omitted fields never block a call):

- `caller_agent`: a lowercase slug for your agent, IDE or framework (`^[a-z0-9][a-z0-9._/-]{1,47}$`, e.g. `claude-code`, `cursor`);
- `requester_role`: `autonomous_agent` | `defi_developer` | `risk_curator_analyst` | `security_researcher` | `protocol_team` | `institutional_allocator` | `individual_user`;
- `caller_purpose`: `pre_trade_safety` | `collateral_due_diligence` | `yield_allocation` | `security_audit` | `governance_monitoring` | `integration_testing` | `general_research`.

A non-blank invalid value gets JSON-RPC `-32602` listing what is allowed. Over REST they are optional query parameters.

HTTP clients should send a User-Agent (`curl -A "my-agent/1.0"`, or `headers={"User-Agent": "my-agent/1.0"}` with `urllib`): Cloudflare's edge refuses some default library agents with error 1010 before the API answers.

## Verdicts

`pacta_check_preflight` returns one of `IMMUTABLE_NO_ADMIN`, `TIMELOCK_PROTECTED`, `ZERO_DELAY_TIMELOCK_RISK`,
`MULTISIG_NO_TIMELOCK`, `INSTANT_EOA_ADMIN_RISK`, `UNDEPLOYED_OR_EOA` or `UNCLASSIFIED_CONTRACT_CONTROLLER`, with a 0–100
`riskScore`, the proxy / admin / timelock breakdown and `pinnedBlock` / `pinnedBlockHash`. Other tools:
`pacta_lookup_protocol` (find an indexed protocol by name, symbol or address), `pacta_scan_control_plane` (full control
plane of any contract on Ethereum or Base) and the timelock / proposal scanners listed by `tools/list`.

## Links

- Canonical repository: https://github.com/Fractal-Neurons/pacta
- Live index (74 indexed protocols: 62 Base-EAS-attested + 12 RPC-pinned; every record block-pinned): https://pacta.wtf/
- USDC bounties for verified control-plane mismatches: https://pacta.wtf/bounties/
- Hunter leaderboard: https://pacta.wtf/leaderboard/
- Community & Builder Q&A (GitHub Discussions): https://github.com/Fractal-Neurons/pacta/discussions
  (questions about targets, fixtures or the MCP tools: the Builder & Bounty Q&A thread, https://github.com/Fractal-Neurons/pacta/discussions/44)

Read-only on-chain analysis, not investment advice. Report security vulnerabilities to the affected protocol's bug
bounty programme, not in issues here.

## License

Apache-2.0, see [LICENSE](LICENSE).
