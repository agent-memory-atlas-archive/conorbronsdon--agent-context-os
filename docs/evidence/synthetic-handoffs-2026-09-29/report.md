# Synthetic handoff observations

On September 29, the maintainer requested synthetic testers in place of the
volunteer observations proposed in #205 and #228. Three producer simulations
exercised the actual kernel at source commit
`947769c957423919ffcd37d4c83573aea1539bae`. Three separate receiving agents then
read the resulting workspaces without inheriting producer conversation history.
Only fictional Lantern context was used. No personal imports, integrations,
native host launches or publication took place.

These observations cover deterministic lifecycle operations and source-backed
agent recovery. They do not measure human onboarding, native host discovery,
host approval UI, or comparative model performance. Runtime names in receipts
are self-reported simulation labels. The actual clock measured automated
execution, not a person completing the guide.

## Newcomer

The producer applied four reviewed proposals: agent selection, project setup,
end handoff and a current-state correction. Independent verification matched
all four receipt digests to their proposals and five current target hashes to
the files. A wrong digest was refused without changing decisions. The fresh
receiver cited the saved CSV choice, spreadsheet-analysis rationale, rejected
PDF sorting limitation, unresolved launch date and column-outline next step.

The first setup payload omitted current state. A setup receipt existed but
start correctly reported `initialized: false`; a reviewed correction produced
`initialized: true`. This was a simulated producer omission, rather than an
observed native Claude failure. The guide now asks reviewers to inspect current
state and check initialization after apply.

Windows text-mode piped stdin also reproduced a setup defect: a blank CRLF name
answer replaced the name placeholder with a carriage return. The setup script
now strips the trailing CR from prompted answers. Regression controls exercise
both blank and populated CRLF names. Interactive terminal behavior was not
observed. The original changed fixture was preserved.

The original setup/end sequence took roughly three minutes from clone activity;
the inspected current-state correction brought the exercise to roughly six
minutes. These timestamps include agent and environment work, and provide no
human timing guarantee. A separate full workspace validation attempt lost its
top-level process before capturing a terminal result; it is unverified.

## Returning session

The producer saved a comma delimiter choice, then appended a semicolon decision
explicitly superseding it and updated current state through reviewed end
proposals. The fresh receiver selected semicolon, recognized comma as historical,
retained the original export rationale and unresolved launch date, and cited
the actual source rows. Column names remained unspecified.

An optional `current_markdown` payload without its date line was rejected.
Preserving exactly one existing `**Last Updated:**` line fixed the payload.
The end skill now explains this requirement; the kernel advances the date.
The rejected payload did not alter durable state. Independent re-verification
also confirmed source hashes, two matching decision-history receipts, and
wrong-digest refusal without mutation.

Observed kernel command time was 37.87 seconds; the original simulation through
verification took 254.33 seconds. This includes a payload correction and excludes
any human or native host onboarding measurement. Python executed the actual
kernel after Git Bash failed to start in the sandbox.

## Reject and revise

The producer deliberately proposed an invented October 15 launch date. The
synthetic reviewer withheld apply. Before/after hashes of durable files and the
receipt list were identical. The inaccurate proposal remained stored. A revised
proposal kept the date unresolved, and only its exact digest was applied.

The fresh receiver distinguished the unapplied artifact from the durable
decision, verified the corrected receipt against source hashes, and answered
from the project, decision and session files. It did not adopt the invented
date. Start still reported general state uninitialized in this deliberately
partial fixture; this scenario proves rejection and continuity, not onboarding
readiness. The guide now explains declining an inaccurate diff and reviewing a
new proposal and digest.

The successful automated producer run took 22.969 seconds, excluding drafting,
review, reporting and a failed attempt that incorrectly used `generic` for
content apply. The kernel correctly reserves `generic` for agent configuration
and materialization. The corrected simulation used the documented self-reported
content-runtime label.

## Evidence limits and disposition

Producer artifacts include inputs, proposal diffs/digests, receipts, start/history
outputs, source hashes, negative controls and receiving answers. Full local
artifacts remain in the maintainer's retained task scratch. This report publishes
the redacted observations and their tested source identity; it excludes machine
paths, ancestor-repository Git identifiers and process/account metadata.

The returning and rejection fixtures were archive copies nested inside another
Git repository, so their receipt Git evidence identified the enclosing repository.
The product commit above was bound separately by the source export. A future
release qualification fixture should use an independent repository boundary.

All three fresh receivers recovered the scenario facts with source citations.
Remaining placeholders in weekly priorities, blockers and tasks were identified
as unknown context, not proof that there were no blockers. Read-only inventory
alone does not prove an agent read a source; the separate receiving answers and
file inspection provide the bounded recovery evidence here.

Composer 2.5 reviewed a public contract packet. Cursor Grok 4.7 High timed out
after 180 seconds; Cursor Grok 4.6 completed a smaller handoff packet. Its warning
against inferring human or native-host behavior is reflected in these limits.
These assistance calls supplement the work and are not the required independent
exact-commit release reviews.
