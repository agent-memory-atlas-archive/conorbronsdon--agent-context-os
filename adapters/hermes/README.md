# Hermes adapter

Hermes CLI is first-class with installed-client evidence for Hermes Agent
`v0.21.5 (2026.9.24)` on Windows using `google/gemini-3.8-flash` through
OpenRouter. The [live lifecycle run](https://github.com/conorbronsdon/agent-context-os/blob/1d5f0dfa590cfd189128169d1aace00526442993/docs/evidence/runtime-promotion-2026-09-29/README.md)
passed explicit skill preloading, all four phases, reviewed exact-digest apply,
receipts, rejection controls, and native-memory separation. Optional hooks
remain advisory. A separate interactive probe verifies the four `/context-*`
commands; short-alias invocation remains unverified. Provider availability is
a separate prerequisite.

The [shared ACP connection foundation](https://github.com/conorbronsdon/agent-context-os/blob/1d5f0dfa590cfd189128169d1aace00526442993/adapters/acp/README.md) has offline tests and
bounded live Hermes ACP read/explicit-skill evidence. Full ACP lifecycle and app
integration remain unverified; the CLI tier does not promote them. No ACP
dependency or global configuration is installed by this foundation.

Run `bash scripts/contextos.sh install --runtime hermes` from the repository root.
The primary skill path is the repository-local `.agents/skills/` directory.
For an isolated fixture, set a fresh `HERMES_HOME` and run `hermes skills trust
<fixture>` yourself. Check `hermes skills list --source local` in a new session
for all four short aliases and all four `context-*` cores. Do not enable a
partial set. If you instead copy skills into a Hermes profile, record the source
commit and SHA-256 of each of the eight `SKILL.md` files; compare all eight after
every source revision and refresh changed copies. Run `bash scripts/contextos.sh
doctor --runtime hermes` to inspect local runtime and descriptor state. Binary
discovery by doctor is not installed-client conformance.

Invoke `/context-setup`, `/context-start`, `/context-update`, and
`/context-end`. On Hermes Agent v0.21.4, `hermes skills list --source local`
reports that `/start` and `/update` are unavailable because built-ins take
those names and suggests `/skill start` and `/skill update`. Keep the short
aliases installed; their invocation still needs a live control.

## Live conformance

Earlier failed attempts are retained in
[`docs/evidence/hermes-live-2026-09-23/`](https://github.com/conorbronsdon/agent-context-os/blob/1d5f0dfa590cfd189128169d1aace00526442993/docs/evidence/hermes-live-2026-09-23/README.md).

From a clean, reviewed source commit, choose new sibling paths outside any
Context OS checkout and run:

```sh
python adapters/hermes/live_conformance.py prepare --source . --expected-commit <full-sha> --fixture <new-fixture> --home <new-hermes-home>
```

Follow the printed manifest. The disposable clone has its source remote removed.
Set `HERMES_HOME` to the new home, supply provider
credentials through environment variables, and run from the source checkout.
Do not copy a profile, credentials, or native memory into the fixture:

```sh
python adapters/hermes/live_conformance.py record --fixture <fixture> --home <new-hermes-home> --manifest <manifest-path> --evidence <new-evidence.json> --binary <hermes-executable> --model <model-id> --provider <provider> --expected-version 'Hermes Agent v0.21.5' --run-budget 300 --max-turns 40
```

Before `record`, set `auth.adopt_external_logins: false` in the fresh home's
`config.yaml` so the fixture does not adopt another CLI's authenticated session.
The passing run used the local terminal backend and provider credentials from
the environment. The 40-turn budget allows normal instruction reads before
proposal creation; a turn-limit summary is not a passing lifecycle response.

`prepare` places two synthetic native-memory canaries under the fresh
`HERMES_HOME/memories/` path described by [Hermes memory documentation](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md).
`record` runs `hermes skills trust <fixture>` before the first phase, with the
same filtered environment and the fixture as its working directory. Hermes
only loads repository `.agents/skills/` when the repository root is trusted in
the active `HERMES_HOME` config. The trust command writes to the disposable
home's `config.yaml`; the harness checks that fixture files and Git status did
not change. A failed trust control stops the run before any model call.

Each phase uses `hermes chat -s context-<phase> -q <prompt>` to preload its
skill. Hermes Agent v0.21.4 single-query mode does not expand slash commands;
placing `/context-<phase>` in the prompt sends that text to the model. This
harness does not exercise interactive slash-command discovery. It records
version, commands, redacted events, discovery canaries,
skill views, read-only start, kernel proposals, no file changes before operator
apply, exact-digest apply receipts, wrong-digest and stale-target rejection,
memory separation,
and a byte-identical sentinel. The manifest stays outside the fixture, and
the canary edits are committed in the disposable fixture. Evidence names both
the source and fixture commits.

By default, each phase first runs a separate instruction-delivery turn with
`-t none` and the phase skill preloaded through `-s`. That turn must report both
instruction canaries, emit no tool event, and leave fixture and native memory
unchanged. It proves delivery without relying on the model choosing not to read
instruction files. The following lifecycle turn may read those files normally;
its reads are recorded but cannot establish discovery. Neither prompt names the
canary values. This tests explicit CLI preloading, not interactive slash routing.

Use `--discovery-mode combined` to retain the earlier strict self-read
semantics (both modes now use `-Q` for stream output). Evidence records the selected mode and effective command prompts. Both modes retain proposal review,
wrong-digest and stale-target rejection, read-only start, and memory separation.

Hermes Agent v0.21.4 emitted only valid JSON lines in a three-line live
`hermes chat -Q --format stream-json` probe, both with and without `-Q`.
The installed-client launch test keeps `-Q`.

On v0.21.5, `-t none` resolves to an empty tool selection but prints
`Warning: Unknown toolsets: none` before JSON output. The tool-free discovery
parser records that exact leading notice and rejects every other non-JSON line.
Its no-tool-event and mutation checks still apply. Windows runs preserve
`SYSTEMDRIVE` and `WINDIR` so native APIs do not create a literal `%SystemDrive%`
cache directory inside the fixture.

Tool-result self-read detection checks, before redacting tool results: literal
canaries, case changes, separators or `0x` prefixes in hex canaries, reversed
text, percent-encoding, `\u` escapes, and base64/base64url (including wrapped
output and gzip payloads). A result too large to decode within the harness limit
counts as a self-read. It does not prove discovery against arbitrary
transformations or unusual read commands; treat the recorded discovery control
as bounded evidence.
By default, pass-through is limited to
`PATH`, `SYSTEMROOT`, `SYSTEMDRIVE`, `WINDIR`, `HOME`, `USERPROFILE`, `TEMP`, `TMP`, `APPDATA`,
`LOCALAPPDATA`, `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` (including lowercase
forms), `SSL_CERT_FILE`, `SSL_CERT_DIR`, `REQUESTS_CA_BUNDLE`,
`CURL_CA_BUNDLE`, and `HERMES_*` variables other than `HERMES_ACCEPT_HOOKS`.
For `openrouter`, it also passes `OPENROUTER_API_KEY`. Other provider keys
require an explicit `--env-allow NAME`.
Before a model call, `record` checks for a populated provider key in that
filtered environment. `openrouter`, `openai`, and `anthropic` require
`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, and `ANTHROPIC_API_KEY`, respectively.
An unknown provider requires an allowed variable ending in `_API_KEY` or
`_TOKEN`, unless `--no-key-check` is set. Evidence records this setup control
separately from discovery, including when the check is bypassed.

The harness sets `HERMES_HOME` and `PYTHONDONTWRITEBYTECODE`. Evidence lists
passed variable names and API key names without values. Use `--env-allow NAME`
for an additional required variable. Inspect each printed proposal diff
and type its digest yourself. The evidence file is create-only and outside the
checkout. A failed control remains failed; prepare a new fixture for another
attempt. Model calls are opt-in and are not part of CI. The optional hook example
is recorded as unsupported unless separately exercised and reviewed.

In Hermes Agent v0.21.4, `tools/environments/local.py` uses
`_scrub_credentials` with the credential list in
`tools/environments/local_env_policy.py`; it includes `OPENROUTER_API_KEY`.
The key reaches Hermes's process environment, but terminal subprocesses have
it removed unless credential inheritance is enabled. A live terminal-tool
probe on 2026-09-26 returned `KEY_ABSENT` for `OPENROUTER_API_KEY`.

For an operator watching another process, pass `--approval-dir <existing-dir>`
to `record`. Keep that directory outside the fixture and `HERMES_HOME`.
For each proposal, inspect `<phase>.review.txt`, then write only
the exact digest, without a newline, to `<phase>.approve`. The harness waits up
to 15 minutes for each approval and rejects any other content. Without this
option, it prints the proposal and asks for the digest interactively.

The optional [`hooks.example.yaml`](hooks.example.yaml) maps Hermes lifecycle
and pre-write events to the same read-only policy checks used by the other
runtimes. Merge it into user configuration only after reviewing its commands.
Kernel proposal/apply enforcement does not depend on these hooks.

The YAML example is POSIX-oriented. On Windows, use an equivalent command such
as `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command
"$root = git rev-parse --show-toplevel; & (Join-Path $root
'scripts/context-os-hook.ps1') hermes pre-write"` for the pre-tool event (and replace `pre-write` with
`session-start` for the session event). Hermes hook policy remains advisory.

Hermes `MEMORY.md` and `USER.md` remain host-local. Never point the kernel at
them or mirror them into repository state automatically.
