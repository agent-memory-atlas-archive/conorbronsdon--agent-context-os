# Published-bundle upgrade preflight

Status: passed bounded Windows preflight; final 1.0 qualification remains open.

Both published release asset sets were downloaded and verified with the shipped
`scripts/release-artifacts.py verify` before extraction. Verification checked
the five-asset set, checksums, provenance, offline instructions, archive members
and locked directory files. The trusted release identities used were:

| Release | Source commit | Bundle digest | Locked files |
|---|---|---|---|
| 0.14.0 | `4e5db061b45e3ba43f42452c8ef5b6c7627235b9` | `b014d9fcaff98acc3cc20a67147b4babba1b1eb58b8daab44f301d9543cbf62a` | 195 |
| 0.15.0 | `947769c957423919ffcd37d4c83573aea1539bae` | `7d64abcbb3b80cb722157c34ebe80c8ce42631a6e2fcaf6296e724e8d46b95eb` | 197 |

Windows directory verification explicitly reported executable-mode verification
as unavailable. This is not Linux executable-bit qualification.

`gh release verify` verified both GitHub release attestations and resolved their
tags to the commits above. All ten downloaded asset hashes were independently
compared with those attested digests and matched, including each detached lock,
offline instruction file, provenance document, tar and checksum file.

## Trial candidate

The candidate was a directory snapshot of development work based on 0.15.0,
with the proposed compatibility contract, guide corrections and CRLF setup fix.
Its test bundle version was set to 1.0.0 solely to exercise a version transition;
the kernel source still declared 0.15.0. This was not a built or published 1.0
release and had no final reviewed commit binding.

The candidate bundle digest was
`2f1ee208f64c21251bb842793545b5804202ffb402fd1e4933b46d2cbe914bc8`.
Its source files and hashes, detached lock, original release bundles, preserved
managed edits, proposals and receipts remain in retained local task scratch.
Subsequent edits invalidate any inference that this preflight qualifies the
final release bytes.

## Observed transitions

For each old release, the harness used the real workspace init/update/reconcile
CLI and the shared apply transaction engine. It initialized a full-template
workspace selecting Claude and Codex, customized the seed current state and
added a file under an extensible project root.

| Control | 0.14.0 → trial candidate | 0.15.0 → trial candidate |
|---|---|---|
| Modified managed README rejected with durable files unchanged | Pass | Pass |
| Missing installed state rejected update with reconcile guidance | Pass | Pass |
| Reconcile against original pinned bundle restored installed identity | Pass | Pass |
| Exception after first durable publication rolled back exact file hashes | Pass | Pass |
| Process exited after first durable publication; journal and lock retained | Exit 79 | Exit 79 |
| Reapply after the exact child exited recovered the journal and completed | Pass | Pass |
| Custom seed and extensible project file preserved byte-for-byte | Pass | Pass |
| Tracked and installed bundle identity matched candidate after recovery | Pass | Pass |
| Receipt digest matched reviewed update proposal | Pass | Pass |

The process-exit control ran an isolated child with an injected `os._exit(79)`
after the first target publication. The parent waited for that exact child to
exit, preserved its stale lock bytes, and removed only that lock. It retained
the journal and reapplied the same proposal through normal recovery. It did not
delete recovery evidence or use a second upgrade implementation.

Update proposal/receipt digests were
`50cd12acbec83a58674fbca6bee7f41724297abc4b4e4a461b0e04710ec1cb12`
for 0.14.0 and
`af8039d3acbc7ae3542e8be5cc2cf56b17b9cdd6308827dc1fe550db016a94db`
for 0.15.0. The initial harness attempt stopped because its assertion expected
the word "modified" or "conflict" while the kernel correctly reported "managed
path is dirty". That failed fixture was preserved; both complete transitions
ran in fresh directories after correcting the assertion.

## Remaining qualification

Repeat these controls using the final exact-reviewed candidate and reproducible
release artifacts on Linux and Windows. Include selected-profile transitions,
personalized managed instructions and skills, legacy/schema-v1 workspaces,
source or target drift between proposal and apply, post-receipt doctor failures,
and recovery after multiple publications. The current preflight establishes
neither all upgrade combinations nor full 1.0 release readiness.
