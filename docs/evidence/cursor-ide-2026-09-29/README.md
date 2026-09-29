# Cursor IDE 3.22.7 operator diagnostic

This run is **not a conformance pass or IDE promotion**. Codex operated a real
local IDE window with the maintainer's permission; the maintainer signed in to
an isolated profile. The source was `bc4aa5e18857f4fcfa247fbbae23eca649dbf7c6`.
The IDE binary hash stayed unchanged through exit. Model selection was `Auto`;
this does not pin the underlying model. See [verified file outcomes](host-diagnostic.json)
and [copied replies and observations](observations.json).

The answer-key directory was unreadable to the Windows operator account while
Cursor ran. Updates and extensions were disabled in the isolated profile.
No project MCP or hook was configured. The session used the local IDE after
switching out of the post-login Agents window. No Cloud agent was launched.
This is profile isolation, not an OS sandbox.

## Findings

- Root, rule, nested, and explicit response values matched their random canaries.
  Root, rule, and conflict replies showed no tool call. The root instruction won
  the rule conflict. The rule turn used Agent mode; other discovery turns used Ask.
- The nested file was attached through the native context picker. The model read
  it and searched the workspace for its canary; automatic nested discovery is
  not established.
- The implicit turn showed **Used contextos-live-explicit**, and the visible
  activity summary listed two `SKILL.md` reads. Its final reply nevertheless
  returned the root canary. This fails the skill-body must-not-load control.
  Final-answer comparison alone would have incorrectly treated it as a pass.
  Native metadata confirms ordinary `read_file_v2` calls, not a distinct native
  skill-invocation tool. The turn also searched its own fixture's native chat
  transcripts. The sanitized tool metadata is embedded in the host diagnostic.
- The explicit skill was typed, selected from the real slash menu, and submitted.
  It returned its canary with no visible tool call. Pasting a slash string alone
  had not opened the picker. The skill file had been opened while inspecting
  the preceding trace, so this does not exclude editor-context contamination.
- Ask refused the requested file write, and that file stayed absent.
- Agent wrote both synthetic files immediately. Keep and Review appeared only
  after the files were on disk. No pre-write approval was granted. The denial
  prompt explicitly asked the model to leave any immediate write in place for
  inspection; it did not undo the outcome.
- The `/update` slash menu listed the workspace collision skill above
  `/update-cursor-settings`. The input was cleared without submission.
- Only `approved-write.txt` and `denied-write.txt` changed in the host fixture.

The IDE recorder now requires `implicit_skill_body_not_loaded: true` based on
inspection of the tool trace, in addition to the final reply check. Both strict
and write-characterization modes reject a missing or false attestation. This
fix improves evidence quality; it does not fix Cursor's observed skill access.
The IDE remains experimental. These host failures are not waived by the
separate lifecycle results below.

## Shipped lifecycle results

[Lifecycle evidence](lifecycle.json) records real desktop IDE invocation of
`/context-setup`, `/context-start`, `/context-update`, and `/context-end`, followed
by a fresh `/context-start` chat on source
`02f2bd17f75936b37e103b20ff94b73aeb0e1361`. The binary stayed unchanged through
exit. Native user-message metadata records `grok-4.7`; that is an observed model
selection, not an independently verified backend identity.

Setup, update, and end each created exactly one proposal and stopped before
apply. The operator inspected the displayed diff, checked wrong-digest rejection,
and applied the exact digest. Receipts matched their proposal digests and runtime.
Exact changed-file contents, unrelated files, and Git control metadata passed
verification. Reapplying update and end failed as stale without further changes.
Start and handoff preserved every fixture file and Git control metadata.

The handoff prompt omitted the random verification value. Its separate chat read
the saved session and returned the exact value; inspected tool paths and shell
commands stayed within the repository. The same isolated profile retained prior
selected skill keys, so this does not establish fresh-profile isolation. Setup
only added one synthetic identity file: the kernel correctly continued to report
`initialized: false` for the remaining template state. This is a bounded
proposal/apply and continuity test, not complete onboarding validation.

Initial setup/start shell attempts missed PowerShell's call operator and were
retried successfully. Later prompts explicitly supplied that Windows requirement.
Tool status `completed` does not imply command success. The evidence preserves
selected tool metadata and final replies, without reasoning or account data.

## Validation and review

Full validation on the recorded `bc4aa5e` source passed 976 tests, with 47
skipped, in 917.658 seconds, plus all repository checks. The recorder follow-up
passed its focused regression suite. A tool-free, zero-priced
`cohere/north-mini-code:free` review of the `bc4aa5e` diagnostic delta timed out
with no model response; it is `setup_failed`, not sign-off. Packet SHA-256:
`0714298a51b02a916940fd981e333c9cc186d2a161dddb864118ac2d16fe9a75`.
The broader [independent review blockers](../runtime-promotion-2026-09-29/reviews.md)
remain in effect. No merge or publication is established by this record.

Full validation on `02f2bd1` passed 977 tests, with 47 skipped, in 893.790
seconds, plus all repository checks. A later recorder hardening rejects malformed
write-behavior values and strict-mode contradictions, and emits the exact
`implicit_skill_body_not_loaded` attestation. Its focused suite passed 12 tests.

The follow-up implementation is `69f391f76b3970d9d17bbc23e7df3477f815bda9`.
Its full suite reported `OK (skipped=47)` after 978 tests, followed by
`All validation passed`; the log's wall time was 20,172.767 seconds across a
long execution pause. The outer PowerShell redirection wrapper returned 1
despite that success footer. Final manifest and documentation checks were
therefore repeated with explicit native exit-code forwarding. These closeout
notes do not change the reviewed implementation files.
The operational free review, `inclusionai/ling-3.0-flash-sante:free`, completed
on that exact SHA with no introduced defects at the requested confidence.
It reported an optional coverage gap for diagnostic approval-required success;
strict approval success and immediate diagnostic success are already tested.
The compatibility fallback for direct callers is intentional. Packet SHA-256:
`ad4064a566799392872c8abb95c6374a4841d8e5b5b6fe807bce53905d0be82f`.
The tool-free stream contained only system, text, and result events (5,007 input
and 8,975 output tokens). Both prices were verified zero in the live catalog.

The adversarial lane exhausted its three candidates: Cohere timed out,
`google/gemma-4-31b-it:free` on `02f2bd1` returned 429 with zero output, and
`poolside/laguna-xs-2.1:free` on `69f391f` returned 429 with zero output.
The final packet SHA-256 was
`f1859b83f8770ad0d0997a92be00309583a5e31dffa2a839e60fe599a7f8a303`.
These are setup failures. The required primary review remains quota-blocked
on authenticated Claude and the eligible paid Go fallback. No sign-off is implied.

The isolated IDE process exited, its answer-key ACL was restored, and its
temporary signed-in profile was deleted after exporting the synthetic evidence.

## ACP integration follow-up

T3 Code connects Cursor through the CLI's ACP transport, not desktop UI control.
Its [spawn adapter](https://github.com/pingdotgg/t3code/blob/d2c9281b8112dc3b2991642c4bdb985e4b08b9bb/apps/server/src/provider/acp/CursorAcpSupport.ts)
launches `cursor-agent acp`; its
[shared contract](https://github.com/pingdotgg/t3code/blob/d2c9281b8112dc3b2991642c4bdb985e4b08b9bb/apps/server/src/provider/Services/ProviderAdapter.ts)
normalizes sessions, turns, approvals, events, and declared capability limits.
This is a candidate for programmatic Context OS integration, not evidence that
the desktop IDE meets its current promotion gates.

A separate initialization-only probe of Cursor CLI `2026.09.28-64d2043` succeeded
with JSON-RPC protocol version 1 in an empty isolated workspace and config.
The agent advertised `loadSession`, session listing, image prompts, HTTP/SSE MCP,
and `cursor_login`. The entrypoint SHA-256 was
`9e3d6101a208743cb0c35236ece75acdcd268f329e912ade9901c9eabd52468c`.
No authentication, session creation, model prompt, or tool permission was requested.
Advertised capabilities still require behavioral tests before integration claims.
[Cursor's ACP documentation](https://cursor.com/docs/cli/acp) describes the transport;
[Hermes also documents an ACP server](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/acp.md).
Neither protocol support nor skill metadata replaces exact-digest kernel approval.
The isolated Hermes 0.21.5 test installation's `acp --check` reported the optional
`acp` dependency missing; no dependency or global configuration was changed.

The design lesson is to distinguish reliable lifecycle support from host feature
parity. An ordinary skill-file read is not proof of native automatic invocation,
and a missing file-edit approval prompt is not a failed shell-approval test.
A future promotion-contract revision should state these capabilities separately
and verify the promises it makes. This record preserves the current failed
controls and does not itself revise the gate or promote the IDE.

## Offline ACP foundation, September 29

Implementation commit: `eec46e123b1e79d1785dd3553f5ab9f1aea739b8`.
The [shared ACP foundation](../../../adapters/acp/README.md) adds message
correlation, streamed notification forwarding, cancellation, and default refusal
of permission requests and blocking Cursor extensions. It launches no processes
and is not a complete ACP client. Eight synthetic protocol tests passed; the
Cursor descriptor suite passed nine tests with one installed-client check skipped.
The live ACP/T3 smoke test is deferred at the operator's request. No app window, live ACP/IDE session, dependency installation, or global
configuration change was used. The separate tool-free review below used Hermes
for inference only.

The Cursor support contract now separates required lifecycle controls from
individual host capability claims. The earlier failed controls remain failed;
neither IDE nor ACP support is promoted by this change.

Operational review through `inclusionai/ling-3.0-flash-sante:free` completed on
that exact commit using the inspected public packet, Hermes with tools disabled,
and zero prompt/completion prices verified in the live catalog. Packet SHA-256:
`fb4d2dc278c71bce2212985270f126749559803270fd789f085f53a7adcc57aa`.
The stream contained system, text, and result events only, with 6,117 input and
10,962 output tokens. Its four findings were checked against actual files:

- Result payload validation is deliberately delegated to the future session
  layer; the README explicitly requires capability/initialization validation.
  No current downstream consumer or live-conformance claim was affected.
- `close()` returns interrupted IDs and methods. The caller retains the request
  returned by `request()`; this module does not promise session recovery.
- The claim that cancellation needs `requestId` contradicts the official
  [ACP cancellation contract](https://agentclientprotocol.com/protocol/v1/prompt-turn#cancellation),
  which specifies `sessionId` and a notification, matching the code.
- Outbound requests use integer IDs. Inbound request IDs belong to the peer's
  separate request direction and are echoed unchanged. A response to our response
  is not a valid outstanding request and should be rejected.

None established an introduced defect in the bounded implementation. This does
not replace primary review. The earlier primary quota failures and exhausted
adversarial candidate budget remain recorded above; no additional attempt is
claimed for those lanes on this commit. Required reviews remain pending, and
nothing is pushed, merged, or published.

Full repository validation on the implementation commit passed 986 tests in
1,032.496 seconds, with 47 skipped, followed by every repository check and
`All validation passed`. The native wrapper exited 0. The log is retained in the
operator-owned task scratch directory as `validation-acp-foundation.log`.
This closeout changes evidence documentation only; the reviewed code is unchanged.
