# ACP connection foundation

Status: offline protocol tests only. No installed Cursor or Hermes ACP lifecycle
has passed conformance, and no T3 application smoke test has run. The interactive
test is deferred at the operator's request. Existing CLI support tiers do not
extend to an ACP connection automatically.

T3 connects Cursor through
[`cursor-agent acp`](https://github.com/pingdotgg/t3code/blob/d2c9281b8112dc3b2991642c4bdb985e4b08b9bb/apps/server/src/provider/acp/CursorAcpSupport.ts).
Its [provider interface](https://github.com/pingdotgg/t3code/blob/d2c9281b8112dc3b2991642c4bdb985e4b08b9bb/apps/server/src/provider/Services/ProviderAdapter.ts)
separates sessions, turns, events, and permissions from the app UI. Context OS can
use the same connection pattern while keeping lifecycle state in its kernel.
This connects the Cursor CLI; it does not automate the desktop IDE.

## Shared protocol code

[`protocol.py`](protocol.py) provides message correlation for an eventual
conformance client. It preserves streamed notifications and provider payloads,
reports remote errors, refuses unknown responses, and returns unfinished requests
on close. Cancellation sends a notification; it does not manufacture completion.

The default peer cancels every permission request, question, and Cursor plan
approval. Unknown requests receive a method-not-supported error. It never chooses
an allow option. A future interactive client must display the requested action
and preserve the provider's option IDs when returning a real operator decision.

This module does not launch processes, frame JSON lines, validate the full ACP
schema, authenticate, create sessions automatically, enforce workflow ordering,
or implement transport deadlines. The transport owner must bound messages,
enforce timeouts, drain stderr separately, and stop its own child on EOF or
protocol failure. It must validate initialization and capability responses before
using optional methods. No filesystem or terminal client capabilities are
advertised. That does not constrain tools implemented inside the agent process.

Run the offline tests from the repository root:

```sh
python -m unittest discover -s tests -p test_acp_protocol.py
```

The tests cover interleaved notifications, response correlation, denied approval
paths, unsupported tools, errors, malformed messages, and interrupted requests.
They use synthetic messages, launch no agents, and make no model requests.

## Provider-specific work still required

| Provider | Documented entry point | Remaining verification |
| --- | --- | --- |
| Cursor | `cursor-agent acp` / `agent acp` | Authentication, session creation, explicit skill resolution, streamed lifecycle turns, permissions, cancellation, and fresh-session handoff |
| Hermes | `hermes acp` | Optional ACP dependency, isolated configuration and MCP startup, skill discovery, permissions, lifecycle turns, and persisted-session behavior |

Use [Cursor's ACP reference](https://cursor.com/docs/cli/acp) and the
[ACP permission contract](https://agentclientprotocol.com/protocol/v1/tool-calls)
for wire behavior. Hermes documents its
[ACP entry point](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/acp.md)
and [implementation boundaries](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/acp-internals.md).
The earlier [initialization probe](../../docs/evidence/cursor-ide-2026-09-29/README.md#acp-integration-follow-up)
established only Cursor's handshake; the isolated Hermes test installation lacked
the optional ACP dependency. Neither result establishes a working app integration.

Before a live test, use an exact source commit, disposable synthetic repository,
fresh provider configuration, recorded binary version, and explicit model-traffic
authorization. Review configured MCP startup independently of the initialize
handshake. Do not inherit permissive flags or global tool configuration silently.
Verify setup, start, update, end, wrong/stale digest rejection, receipts,
unrelated-file preservation, and repository-backed handoff. Record app, provider,
model, and connection mode separately. Keep native memory outside repository state.

An ACP permission response is a client decision, not proof of human approval.
The conformance client must stop at each proposal and obtain the operator's exact
digest before apply. The kernel checks integrity; it cannot establish who chose
the digest. Unsupported rollback, hooks, or memory bridges remain explicit limits.
