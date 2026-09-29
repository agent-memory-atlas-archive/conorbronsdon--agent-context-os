# Cursor CLI and Hermes promotion evidence

These are synthetic Windows 11 fixtures, not personal-context sessions. The
source revision, client version, timestamps, controls, and limits are recorded
in each artifact. Account configuration hashes are omitted from the shareable
copies; credentials and home directories are not included.

## Cursor CLI

Cursor Agent CLI `2026.09.28-64d2043` passed the 14 host controls against the
unmodified v0.14.0 source `4e5db061b45e3ba43f42452c8ef5b6c7627235b9`:
[host evidence](cursor-host-release-baseline.json). The configured model was
Composer 2.5; the CLI selected its configured default rather than a pinned model
revision. The artifact records the executable and command-output hashes.

The full setup/start/update/end workflow and fresh-session handoff then passed
on `feba424cbb10f495a3b0b8a9e1ff382f1156d1a7`:
[lifecycle run 3](cursor-lifecycle-3.json). Each mutation produced one reviewed
proposal. The operator inspected each actual diff and supplied its exact digest
through an external approval file. The kernel rejected wrong digests and
already-applied update/end proposals, emitted matching Cursor receipts, and
produced the exact approved files. Start was read-only. A fresh session recovered
a random value saved by end without changing fixture files.

The hardened fixture also passed every lifecycle and handoff control on
`5da7b9bfbf3f3f25475a4ea371cfdae848edf78e`: [lifecycle run 4](cursor-lifecycle-4.json).
Its source remote was removed and Git metadata was checked between phases.
The [host controls rerun](cursor-host-5da7b9b.json) also passed all 14 controls
on that exact hardened revision.

This supports the CLI surface independently of the IDE. The existing IDE
diagnostics remain failed/unverified. No hook adapter, native-memory bridge,
MCP execution, undocumented rule-conflict precedence, or other-platform parity
is established. The host discovery prompts refer to instructions and do not
isolate automatic discovery from prompted reads. First-class describes the
tested lifecycle integration, not an OS sandbox or every Cursor capability.

Earlier failures remain visible:

- [Lifecycle run 1](cursor-lifecycle-1.json) timed out without the mutation-mode
  flag. Its Windows launcher left descendants holding output pipes; the runner
  now kills the child tree on timeout or interruption.
- [Lifecycle run 2](cursor-lifecycle-2.json) passed all lifecycle mutations but
  failed a combined handoff check requiring the entire sentence verbatim. That
  artifact does not distinguish wording from file mutation, so it is not counted
  as passing. Run 3 checks the unpredictable recovery value and read-only state
  separately and passed both.

## Hermes

Tests use the official `v2026.9.24` source tag,
`f97608f178d1ffeca59860195ab7da295f7c8e5f`, reporting
`Hermes Agent v0.21.5 (2026.9.24)`, installed in an isolated environment.
Each fixture has a fresh HERMES_HOME, explicit project-skill trust, synthetic
native-memory canaries, and `auth.adopt_external_logins: false`. No host OAuth
tokens or existing native memories were copied. Provider keys were supplied
only through the driver's filtered environment.

Tool-free discovery is a separate turn with both instruction canaries, zero
tool events, unchanged fixture files, and unchanged native memory. The normal
lifecycle turn may subsequently read instructions. `--discovery-mode combined`
retains the old strict self-read controls for comparison.

Run 7 passed every required control on
`5da7b9bfbf3f3f25475a4ea371cfdae848edf78e` with
`google/gemini-3.8-flash` through OpenRouter, a 300-second per-call budget,
and 40 turns: [passing lifecycle](hermes-live-7.json). Setup, update, and end
were individually reviewed and applied by exact digest. Wrong-digest and
stale-target rejection, matching receipts, read-only start, native-memory
separation, and the unrelated sentinel all passed. This establishes the
first-class CLI lifecycle; it does not establish interactive slash routing.

The subsequent preparation-only change removes the clone source remote, as
already done for Cursor. A regression test verifies this; lifecycle prompts,
recording, and controls are unchanged from the passing run.

The [v0.15.0 preparation rerun](hermes-live-v015.json) passed every required
control on `cd7dac2f91814b73950fdcc95ce5375d0e5ac70f`, including the source-remote
removal. It used the same Hermes version, model route, 300-second per-call
budget, and 40-turn limit. Setup, update, and end proposals were individually
inspected and approved by exact digest. Optional hooks remained unsupported
by the live test. A subsequent README index-link correction and evidence
closeout are documentation changes; final reviewed-revision acceptance remains
a pre-merge gate.

Retained attempts:

| Artifact | Outcome |
|---|---|
| [Run 1](hermes-live-1.json) | Exact client startup warning broke JSON parsing; narrowly recognized and recorded thereafter. |
| [Run 2](hermes-live-2.json) | Discovery produced canaries but Windows wrote cache paths under literal `%SystemDrive%`; environment preservation fixed rather than ignoring the mutation. |
| [Run 3](hermes-live-3.json) | Discovery passed; Nemotron Ultra free setup timed out amid provider overload and instruction reads. |
| [Run 4](hermes-live-4.json) | OpenCode Go GLM 5.3 Flash unavailable: monthly usage limit exhausted. |
| [Run 5](hermes-live-5.json) | Poolside Laguna free discovery passed; lifecycle failed during upstream rate limiting. |
| [Run 6](hermes-live-6.json) | Gemini 3.8 Flash produced the expected setup proposal on turn 20, but hit the turn limit before completing; not a passing phase. |

Optional Hermes hooks remain advisory and untested by this live harness.
Single-query mode uses `-s context-<phase>` to preload skills; this does not
verify interactive slash-menu behavior or short aliases that collide with
Hermes built-ins.

## Validation and review

### Hermes interactive command routing

The [interactive routing probe](hermes-interactive-routing.json) ran Hermes
v0.21.5 in a Windows ConPTY against source `8366f6c`, using a fresh profile and
the same synthetic fixture preparation. It launched `hermes chat` with Gemini
3.8 Flash through OpenRouter, `-t none --safe-mode --ignore-user-config`, a
120-second per-call budget, and one turn per response. Neither `-q` nor `-s`
was supplied.

Each of `/context-setup`, `/context-start`, `/context-update`, and `/context-end`
loaded its complete skill into the user message and returned that skill's
distinct random canary, with zero tool calls. An invented
`/context-no-such-fixture-skill` command was rejected without a model message.
Tracked files, the unrelated sentinel, and synthetic native-memory files were
unchanged. The eight source skill hashes remain bound to the fixture manifest.

To reproduce, prepare a fresh fixture and home with the documented live
conformance command, disable external login adoption, trust the fixture, and
start an interactive chat with those options. Enter each `/context-*` command
with: `Report only the fixture canary stated in the <skill-name> skill loaded
for this command. Do not use tools or begin the workflow.` Compare the answer
with that phase's manifest canary outside the fixture, then enter the invented
command. Inspect the session records for the expanded skill body, exact
assistant answers, and absence of tool calls; compare fixture and memory bytes.

This proves routing, not interactive lifecycle execution. The first prompt
requested both root and skill canaries, but returned only the skill canary;
root-instruction discovery is established by the separate lifecycle evidence,
not by this probe. Short-alias invocation remains untested.

Final `bash scripts/validate-all.sh` passed on implementation commit
`e84e094e4131a15d51e88d92399ed2c3816a3bef`: 972 tests in 876.839 seconds,
47 skipped, plus hook and portability checks, links, manifests, schemas, and
generated runtime artifacts. The earlier 968-test run and focused regressions
also passed. The subsequent closeout commit changes evidence documentation only.

See [independent review status](reviews.md). A live pass is not independent
review approval, and no merge or release is authorized by these artifacts.
