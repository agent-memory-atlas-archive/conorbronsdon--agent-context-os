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
