# Independent review status

Lead: Codex. All packets contain only explicitly selected public repository
source and tests; no credentials, private context, or host configuration.
Reviewers have no tools and no edit assignment. There is no completed final
independent sign-off yet.

The implementation candidate is `e84e094e4131a15d51e88d92399ed2c3816a3bef`.
Its final strict validation passed 972 tests (47 skipped) and every repository
check. The source-remote removal was also applied to Hermes fixture preparation
after the reviewed `5da7b9b` revision, with a passing regression test. Final
primary review must cover that change and the promotion metadata/documentation;
the earlier code reviews do not cover the complete candidate.

## Primary review

Authenticated `claude-opus-5-5` reviewed
`feba424cbb10f495a3b0b8a9e1ff382f1156d1a7` through the Claude subscription,
with safe mode, no tools, no slash commands, and no session persistence.
Packet SHA-256: `479fd1f83c763d388982df99d6591e2a34f32686bb2cdf42ce7185d231cee8b3`.

Verified findings fixed in `5da7b9bfbf3f3f25475a4ea371cfdae848edf78e`:

- Remove the fixture's source remote and check Git refs, config, hooks, HEAD,
  and staged changes; ordinary read-only index refreshes remain permissible.
- Kill Cursor child processes on any interrupted execution, preserving the
  original exception when cleanup encounters an exited process.
- Reject Unicode control and bidi characters in proposal review displays.
- Handle a truncated Hermes startup notice without an indexing error.
- Add native-memory and premature-write negative controls for tool-free mode.

The approval-file formatting finding was not adopted: exact digest bytes are
intentional and the README documents a Windows write without BOM or newline.
A partial or malformed approval fails closed. The earlier claim that a forged
diff could be applied was rejected after reading the kernel: apply recomputes
the diff from after_text and rejects a mismatch before writing.

The re-review of `5da7b9b` failed before inference on both authenticated Opus
and Sonnet: weekly subscription limit. The eligible OpenCode Go fallback is
also unavailable because its monthly allowance is exhausted. These are setup
failures, not completed reviews. The earlier report cannot sign off the fixes.

## Free lanes

Live OpenRouter catalog entries confirmed zero prompt and completion prices.
Each attempted pass used Hermes `-t none --safe-mode --ignore-user-config -Q`
from an OS temporary directory outside checkouts, a fresh home, and bounded
turn/time limits. Failed or empty attempts do not count.

First required lane, capped at three candidates:

- `thinkingmachines/inkling:free`, packet at `ebcbe895a7aa572768423fa3c23cdb36ed5ff942`: timeout.
- `qwen/qwen3.8-27b:free`, packet at `feba424`: upstream 429 on all three requests, zero output tokens.
- `nvidia/nemotron-3.5-lightning:free`, packet at `5da7b9b`: timeout.

The `5da7b9b` packet SHA-256 is
`9d05a6cc80e7ad950d07a31173b71c10e46541aa031f89ee5c909ba59f543fcb`.
The free lane remains `setup_failed`; the Go fallback is quota-blocked.

Second required lane completed on `5da7b9b` with
`cohere/north-mini-code:free`: exit 0, 11,267 input / 4,784 output tokens,
no tool events. Its four findings were checked against actual code and rejected:
POSIX `start_new_session=True` makes the child PID its process-group ID; the
startup warning matcher is intentionally narrow; CR/control-character rejection
is an existing conservative display boundary; and Windows system variables
were demonstrably required to prevent cache pollution in run 2.

Final primary and the first additional-family review remain required before merge-ready
status. No push, merge, or publication has occurred.

## Draft PR and final-source validation follow-up

The later accumulated branch was pushed as draft
[PR #227](https://github.com/conorbronsdon/agent-context-os/pull/227), with head
`8d2f6bedd91f5a608accbe07ca9d27d1c29a8b75`. No merge or release is implied.
Cursor IDE, ACP, and subsequent review observations are recorded separately in
the [IDE evidence](../cursor-ide-2026-09-29/README.md).

An earlier full run had one README positioning assertion failure. Commit
`8d2f6be` restored the accurate product-description phrase without weakening the
test; all 24 positioning tests passed. A fresh canonical run on that unchanged
commit then passed all 986 tests in 1,028.074 seconds, with 47 skipped, and every
repository check; its wrapper exited 0. The operator-owned scratch log is
`acos-acp-resume-0929/validation-final-8d2f6be.log`.

[Hosted validation run 36607243722](https://github.com/conorbronsdon/agent-context-os/actions/runs/36607243722)
also passed on that head. Linux and Python 3.10 each passed 986 tests with 26
skips and all canonical checks. Windows passed 986 tests with 18 skips and its
materialization check. The macOS portability and separate SSOT jobs passed.
Different skip counts reflect the tested environments, not additional live-host
promotion evidence.

Independent review still blocks merge readiness. Authenticated Claude continued
to report its weekly limit. For the bounded Pi Dash catalog subset, three paid Go
fallbacks (`glm-5.3`, `kimi-k3`, `minimax-m3`) each returned HTTP 429; that fallback
candidate budget is exhausted. Free upstream-comparison review through
`inclusionai/ling-3.0-flash-sante:free` and adversarial review through
`poolside/laguna-s-2.1:free` completed on `fff0c33`, with no verified introduced
defect after checking the cited upstream files. Those subset reviews do not
replace the pending full runtime-promotion reviews above.

The later framing-only change received a tool-free Ling review on `fe3a4bd`.
Its filename, source-support, and link objections were rejected against actual
published assets and repository files; the separate positioning-test regression
was fixed as described above. Review packets and dispositions remain in the
operator-owned task scratch with a 2026-10-06 retention review date. This
follow-up adds changelog and evidence prose only; implementation is unchanged.
