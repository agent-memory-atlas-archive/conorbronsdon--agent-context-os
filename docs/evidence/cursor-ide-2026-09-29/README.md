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
The IDE remains experimental. The shipped lifecycle needs its own evidence.

## Validation and review

Full validation on the recorded `bc4aa5e` source passed 976 tests, with 47
skipped, in 917.658 seconds, plus all repository checks. The recorder follow-up
passed its focused regression suite. A tool-free, zero-priced
`cohere/north-mini-code:free` review of the `bc4aa5e` diagnostic delta timed out
with no model response; it is `setup_failed`, not sign-off. Packet SHA-256:
`0714298a51b02a916940fd981e333c9cc186d2a161dddb864118ac2d16fe9a75`.
The broader [independent review blockers](../runtime-promotion-2026-09-29/reviews.md)
remain in effect. No merge or publication is established by this record.
