# Cursor adapter

Context OS supports Cursor Agent CLI as a first-class surface. The desktop IDE
remains experimental. Both discover the repository-root `AGENTS.md` and project
skills under `.agents/skills/`, but they have different binaries, permissions,
configuration, and conformance gates. A green CLI check is not IDE evidence.

CLI promotion is scoped to `2026.09.28-64d2043` on Windows, with host controls,
the shipped setup/start/update/end workflows, exact-digest operator apply,
and fresh-session handoff recorded in the [promotion evidence](../../docs/evidence/runtime-promotion-2026-09-29/README.md).
It does not promote the IDE or establish parity on untested platforms.

## Setup

Select Cursor alongside any other agents during repository setup:

```bash
bash scripts/setup.sh --agents cursor
# or
bash scripts/setup.sh --agents claude,codex,cursor
```

For the IDE, open this repository as the workspace. For the CLI, install the
Cursor Agent CLI separately, start `agent` from the repository root, and verify
the exact executable with `agent --version`. The executable name `agent` is too
generic for safe automatic detection. Doctor probes the unambiguous
`cursor-agent` alias; if your installation provides only `agent`, verify its
exact path manually. Setup registers the adapter but
does not launch either surface, authenticate Cursor, trust the workspace, or
change account, user, project, MCP, hook, sandbox, or permission settings.

Invoke `/context-setup`, `/context-start`, `/context-update`, and `/context-end`
explicitly. Cursor CLI owns the built-in `/update` command for updating Cursor
itself, so the documented Cursor lifecycle deliberately avoids the short
aliases. The namespaced skills route mutations through the deterministic
proposal/apply kernel. Even in an IDE run mode or `agent -p --force`, an agent
instruction is not approval of a Context OS proposal: inspect the exact diff
and approve its digest separately.

## Rules and skills

Cursor also supports project rules in `.cursor/rules/**/*.mdc`; plain Markdown
files in that directory are ignored. Cursor documents Team, Project, then User
rule priority, but does not document which source wins when root `AGENTS.md`
conflicts with a project `.mdc` rule. Context OS therefore ships no Cursor rule
file and makes no conflict-precedence claim. Keep the shared lifecycle contract
in `AGENTS.md`; make Cursor rules narrow and non-overlapping.

Cursor discovers skills in both `.agents/skills/` and `.cursor/skills/`, but its
documentation does not define a same-name collision winner. Context OS ships
only `.agents/skills/`. That shared directory includes the four short aliases
as well as the four `context-*` cores, so Cursor discovers both sets even though
this adapter documents only the namespaced commands. Cursor does not document
whether its built-in `/update` or the discovered `update` skill wins. Do not use
the short aliases in Cursor, and do not duplicate these names in another Cursor
skill root. Every shipped lifecycle core and short alias sets
`disable-model-invocation: true`, so Cursor includes it only after explicit
slash invocation. The same files also carry Devin's `triggers: ["user"]`; each
host ignores the other host's extension while the shared procedure remains
provider-neutral.

Cursor CLI also reads a root `CLAUDE.md`, when present, alongside `AGENTS.md`
and `.cursor/rules`. This template ships `CLAUDE.md` as a removable seed, so the
runtime descriptor cannot declare it as a required repository source. Its
Claude command table includes the short lifecycle names; Cursor users should
still use only the namespaced `context-*` skills. Cursor also scans compatible
`.claude/skills/` and `.codex/skills/` roots. No lifecycle skill is shipped in
those roots today, but same-name additions create another unresolved collision.

## Authorization boundaries

The IDE and CLI authorization controls are not interchangeable:

- IDE Run Modes and project/user `permissions.json` govern IDE shell, MCP, and
  fetch behavior. Cursor says Auto-review is not a security boundary.
- CLI permissions live in user `~/.cursor/cli-config.json` and project
  `.cursor/cli.json`. An explicit deny wins an allow for the matched tool, but
  a `Write(...)` deny does not prevent the same filesystem change through
  `Shell(...)`; deny every applicable tool path when enforcing an outcome.
  Treat relative path-scoped `Write(...)` denies as insufficient until an exact
  installed-version fixture proves otherwise; test broad `Write(*)` and
  `Shell(*)` denies against every intended write path, including `--force`.
- Treat `agent -p` as write-capable unless the exact installed-version fixture
  proves the selected mode remains read-only. Use `--mode ask` or `--mode plan`
  when the invocation must remain read-only. `--force` additionally force-allows
  commands unless an explicit permission deny matches. These are
  installed-version conformance gates because unattended behavior can change
  across releases.
- `--trust`, `--force`, and broad shell, write, MCP, or absolute-path grants are
  opt-in permission expansions. Setup never supplies them.

Use a disposable fixture to test unattended modes. Never run a `--force`
conformance check against a real context repository.

## Hooks, memory, and MCP

Cursor project hooks use `.cursor/hooks.json`. Command hooks block on exit code
2 and otherwise fail open by default; cloud-agent hook coverage is a smaller
documented subset. Context OS intentionally ships no Cursor hook adapter until
an exact installed IDE and CLI fixture proves the selected events, output, and
failure behavior. Project hooks and blocking pre-tool hooks are therefore
unsupported by this adapter, not silently inherited from Claude or Codex.

Cursor loads project MCP configuration from `.cursor/mcp.json`; MCP remains a
separate trust and authorization boundary. Setup does not install, authenticate,
approve, or enable a server.

Cursor rules, account settings, chat/session history, Cloud Agents, Automations,
and any host-native memories are outside Context OS state. No Cursor-native
memory is synchronized into `state/` or `sessions/`; portable continuity changes
only through a reviewed Context OS proposal.

## Diagnostics and promotion gates

Run `bash scripts/contextos.sh doctor --runtime cursor` for descriptor,
registration, materialization, and local binary checks. It probes the `cursor`
IDE launcher and `cursor-agent` CLI alias separately. Aggregate availability is
`available` when both resolve and `mixed` when only one resolves; resolution
does not establish working authentication or conformance. The generic `agent`
CLI name has no resolution-only probe. Cursor has no
documented all-up native doctor. For the CLI, record `agent --version`, `agent
about`, `agent status`, and `agent mcp list` separately from IDE diagnostics.

The lightweight opt-in CLI control is an exact-version and required-flag smoke test,
not installed lifecycle conformance. It runs from a disposable directory and
does not authenticate, trust a workspace, call a model, or exercise writes.

The stronger live CLI harness is `adapters/cursor/live_conformance.py`. Run it
only from a clean exact commit, with an exact separately installed or extracted
binary and an evidence path outside the repository:

```bash
python adapters/cursor/live_conformance.py \
  --binary /exact/path/to/cursor-agent \
  --expected-version <exact-version> \
  --source-sha <exact-clean-commit> \
  --evidence /outside/repository/cursor-cli-evidence.json \
  --allow-model-traffic
```

The opt-in flag authorizes Cursor model traffic and writes only in a synthetic
temporary workspace marked disposable. The root, nested, and rule controls
check exact canary responses in ask mode. Their prompts mention repository
instructions or a project rule, and reads are allowed, so they do not isolate
automatic discovery from a prompted file read. The harness also checks
explicit-skill must-fire and implicit-skill must-not-fire behavior, read-only
ask mode, the exact unattended write behavior
without `--force`, a stream-observed denied write attempt under `--force`, and
an exact allowed write. It does not treat a model merely choosing not to write
as evidence that project denial precedence works.
For the explicit-skill control it denies direct `.agents/**` reads, so a passing
run must use Cursor's skill mechanism rather than merely reading the skill file;
it also denies all shell commands for that turn so `cat` cannot bypass the
file-read control.
It refuses a dirty source worktree,
version drift, missing authentication, evidence overwrite, unexpected fixture
mutation, and the real repository as a target. It never invokes Cursor's
built-in `/update` command. A passing CLI artifact is not IDE evidence.

User-level write or shell allowances and conflicting deny rules invalidate
permission conformance; use a dedicated clean CLI configuration rather than
changing the operator's normal permissions. Preflight inspects the effective
`CURSOR_CONFIG_DIR` override (or `XDG_CONFIG_HOME/cursor`), matching the
installed `2026.09.23-86fc751` build on all platforms. Blank overrides are
ignored; relative override paths are rejected. An injected config path must be named
`cli-config.json`. The inspected directory is always pinned for the child via
`CURSOR_CONFIG_DIR`. The config hash records preflight contents; it does not
attest that user configuration stayed unchanged throughout the run.
Evidence identifies the supplied
Cursor launcher by basename and SHA-256, including when Windows invokes it
through `cmd.exe`. The hash covers that file, not every bundled dependency.
The launcher is checked before each command and before evidence is written.
If Windows retains a temporary-file handle after the controls finish, evidence
records `workspace_cleanup: retained-cleanup-error` instead of discarding the
result. Its local stderr diagnostic identifies the retained path; inspect and
clean that fixture after the client exits. The path is omitted from shareable
evidence.

The IDE has a separate operator-assisted harness at
`adapters/cursor/ide_conformance.py`. Its `prepare` command requires an exact
clean source commit, installed binary hash, disposable workspace, isolated
native profile, and explicit model-traffic opt-ins. Open only the generated
workspace with the generated profile. Follow the prompts stored in the
create-only manifest, record the exact synthetic observations in a JSON file,
then use `record` with `--acknowledge-operator-attestation`. The recorder checks
root and nested instructions, an always-applied project rule, installed-build
instruction/rule conflict behavior, the explicit skill's exact canary response,
implicit-skill must-not-fire behavior, Ask-mode preservation, interactive denial and scoped
approval, native-profile isolation, and absence of project MCP and hook config.
Inspect the expanded tool trace for the implicit turn and affirm
`implicit_skill_body_not_loaded: true` only when neither a skill invocation nor
a direct skill-body read occurred. A final reply containing another canary does
not establish this control. The recorder rejects a missing or false attestation.
The prepared IDE workspace and profile do not deny direct reads of the skill
file. A matching explicit response therefore cannot establish that the slash
command resolved; the manifest and evidence record `explicit_skill_must_fire`
as `unverified`.
It accepts only one exact approved fixture write and emits create-only evidence
outside the repository. Its artifact labels host observations as
`operator-attested-with-local-verification`, separating them from the fixture
and file-state controls it verifies itself. For the short `/update` collision, observe the slash
menu and record `builtin`, `skill`, `ambiguous`, or `unavailable`; never submit
or execute it.

For builds that apply Agent file edits immediately, use
`record --characterize-file-writes` to retain a diagnostic without weakening the
strict approval test. Record `agent_write_behavior` as `immediate` or
`approval-required`, and attest `file_write_control_observed: true`. In the
immediate case, leave `denied-write.txt` with exactly `DENIED_WRITE_CONTROL`;
do not undo the edit or claim a denial occurred. Ask-mode and unrelated-file
preservation still apply. The diagnostic is explicitly `promotion_eligible:
false`; it does not establish shell approvals, native slash invocation, or the
Context OS proposal/apply lifecycle. The default recorder continues to reject
an immediate denial-control write.

Project-owned `.cursor/` configuration is permitted by workspace validation.
Strict maintainer validation still requires every template-owned path to have
an explicit component owner.

Each surface's first-class promotion requires its own exact-version conformance,
including root and nested instruction discovery, `.cursor/rules` conflict
controls, short-alias versus built-in resolution, the shipped explicit-only
skill frontmatter, interactive must-fire and must-not-fire approval controls,
headless ask, no-`--force`, and `--force` behavior, deny precedence, MCP scope,
native-state isolation, and either a tested Cursor-specific hook adapter or a
continuing explicit no-hook claim. The runtime's overall tier reflects its
strongest surface; a passing CLI does not satisfy the IDE's interactive controls.

### September 26, 2026 IDE operator run (diagnostic)

An agent operator ran the prepared IDE fixture on IDE `3.21.18`
([record](../../docs/evidence/cursor-ide-2026-09-26/README.md)), with the
answer key made unreadable to the operator account. The root, nested, rule,
and explicit canaries matched, and the implicit control did not return the
skill canary. The Agent-mode denial control failed: the IDE wrote the file
before any approval prompt, and Review, Keep, and Undo came only afterwards.
Cursor then updated itself to `3.22.7` on exit, so `record` refused the run.
The IDE surface remains unverified.

### September 29, 2026 IDE operator run (failed control)

A fresh IDE `3.22.7` run matched the canaries, resolved an explicitly selected
slash skill, and preserved Ask-mode files. The implicit turn nevertheless read
the explicit-only skill body while returning a different final canary. Agent
file writes were immediate. The [record](../../docs/evidence/cursor-ide-2026-09-29/README.md)
explains these limits and the recorder fix; the IDE remains experimental.

### CLI lifecycle conformance

The separate `adapters/cursor/lifecycle_conformance.py` exercises the shipped
four lifecycle skills in a disposable clone. It checks read-only start,
proposal-only mutation turns, operator-approved exact-digest apply and receipts,
wrong and stale digest rejection, exact applied content, unrelated-file
preservation, Git control metadata, and a fresh session reading the saved handoff.
The clone has no source remote. This is a disposable test fixture, not an OS
sandbox. Run it from a clean
commit with `--binary`, `--expected-version`, `--source-sha`, `--evidence`, an
empty external `--approval-dir`, and `--allow-model-traffic`. Review each
`<phase>.review.txt`, then write only its exact approved digest, with no newline,
to `<phase>.approve`. On Windows, use
`[IO.File]::WriteAllText('<phase>.approve', '<digest>')`; shell redirection may
add a newline or incompatible encoding. It never supplies approval itself. Host permission controls
remain the responsibility of `live_conformance.py`; both artifacts are needed.

### September 26, 2026 CLI conformance

CLI `2026.09.26-dd393fe` passed all 14 live controls from source commit
`281c859` ([evidence](../../docs/evidence/cursor-cli-2026-09-26/README.md)).
That commit fixed the deny-precedence parser. The client reports a denied file
write as `editToolCall` with a `writePermissionDenied` result, and the harness
had been looking for a different event shape. This is CLI evidence only. The
IDE surface still needs an uncontaminated operator run. Overall support was
experimental at the time of this earlier evidence.

### September 24, 2026 live diagnostics

These observations used clean source commit
`4ea28a6901d168b884f6c8621d90a1f897b4e99f`; they are failed or incomplete
diagnostics, not passing conformance artifacts. Support was experimental at that time.

- CLI `2026.09.23-86fc751`: the first run failed the exact nested canary.
  A second run passed that control, then stopped because the denial stream did
  not establish a rejected write attempt. A model declining to write does not
  prove enforcement. The baseline also accepted a user `Shell(ls)` allowance,
  so permission conclusions from these runs are confounded. The changes above
  reject that setup before model traffic.
- IDE `3.18.25`, executable SHA-256
  `7acc54201db5ba24bb4fab2e1cd41fabd6a25fd43c7923b96efb235c370c009e`:
  root, nested-file-context, and project-rule prompts returned their canaries
  in an isolated profile and synthetic workspace. During the implicit-skill
  control, the IDE read the external test manifest and prior observation file.
  That run is contaminated and cannot establish discovery or skill isolation.
  Workspace and profile separation alone do not prevent reads outside them.
  Repeat with the expected answers inaccessible to model tools before using
  results for promotion. Interactive write and slash-menu controls were not
  completed.

### Grok Bot research (#170)

Grok Bot is a separate application with a persistent cloud computer. Calling a
Grok model through Cursor CLI does not establish Bot runtime support. The
official setup flow requires installing the desktop app and signing in with a
Cursor account; see [onboarding](https://cursor.com/docs/grok-bot/get-started)
and [working with Bots](https://cursor.com/docs/grok-bot/work).

The initial September 24 setup attempt reached the download dialog, but Chrome blocked
the official installer with `ERR_BLOCKED_BY_CLIENT`. No Bot task or lifecycle
control was run at that point. A supported individual Bot conversation API was not established
by the documentation reviewed. No Bot adapter or runtime declaration is shipped.

Later that day, the operator downloaded the installer. Desktop version `0.58.0`
was installed after its Anysphere signature was verified. Native desktop UI
automation successfully submitted a bounded task and retrieved the response.
The Bot reported host build `8b0b203`, the source commit above, a clean disposable
checkout, and exit status zero from `bash scripts/contextos.sh start`. Its returned
inventory had `initialized: false`. It reported explicitly reading the repository
instructions and skills rather than receiving them automatically. A follow-up
returned the requested command outputs, but the cloud filesystem and tool trace
were not independently inspected. These are Bot-reported smoke-test observations;
native discovery, proposal/apply approval, and persistence remain unverified.

For a new disposable checkout, use this bounded first task:

> In a disposable cloud checkout of the public agent-context-os repository,
> record the exact commit and your Bot build. Follow the repository instructions
> and report which instruction files and skills you actually discover, including
> how they were loaded. Run the read-only lifecycle start inventory. Using only
> synthetic session data, prepare an update proposal and show its diff and digest.
> Stop before apply, commit, push, or connecting any private account. Report the
> exact commands, tool results, changed files, and approval prompts.

Then test an explicitly rejected proposal and an approved exact-digest proposal
in that same disposable checkout, preserving before/after state and the receipt.
Test explicit lifecycle invocation separately from ordinary prompts; an ordinary
prompt must not invoke a user-only lifecycle skill. Keep expected canaries and
operator evidence outside the Bot's accessible storage. Record persistence across
conversations and the boundary between Bot memory and repository state. Those
observations determine whether a Bot adapter is needed; they must not be inferred
from the IDE or CLI results.
