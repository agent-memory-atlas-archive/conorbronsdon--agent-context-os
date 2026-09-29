"""Opt-in Cursor CLI lifecycle test; exact proposals require operator approval."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
from pathlib import Path
import secrets
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from adapters.cursor.live_conformance import (
    CursorHarness, HarnessError, REPOSITORY_ROOT, require_json_result,
    repository_source_sha, require_outside_source, require_success, output_summary,
)
from contextos.kernel import validate_proposal
from contextos.primitives import is_link_like, read_regular_file_snapshot
from contextos.workspace_schema import strict_json_loads

PHASES = ("setup", "start", "update", "end")


def require_fact(document: dict, fact: str) -> None:
    if not any(fact in change["after_text"] for change in document["changes"]):
        raise HarnessError("proposal omitted the requested synthetic fact")


def state(root: Path, *, include_pending: bool = True) -> dict[str, str]:
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in [*dirs, *files]:
            if is_link_like(parent / name):
                raise HarnessError("fixture contains a link")
        if parent == root:
            dirs[:] = [name for name in dirs if name != ".git"]
        for name in files:
            path = parent / name
            rel = path.relative_to(root).as_posix()
            if not include_pending and rel.startswith((".context-os/inputs/", ".context-os/proposals/")):
                continue
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def proposal(root: Path, previous: set[Path], phase: str) -> tuple[Path, dict]:
    added = set((root / ".context-os/proposals").glob("*.json")) - previous
    if len(added) != 1:
        raise HarnessError("phase must create exactly one proposal")
    path = added.pop()
    raw, _ = read_regular_file_snapshot(path, subject="Cursor lifecycle proposal")
    if len(raw) > 2_000_000:
        raise HarnessError("proposal too large")
    document = strict_json_loads(raw.decode("utf-8"), source=str(path))
    validate_proposal(document)
    if document.get("workflow") != phase or not document.get("changes"):
        raise HarnessError("proposal has wrong workflow or no changes")
    for change in document["changes"]:
        if not isinstance(change, dict) or not all(isinstance(change.get(k), str) for k in ("path", "diff", "after_text")):
            raise HarnessError("proposal lacks reviewable text")
        if any(ord(c) < 32 and c not in "\n\t" for c in change["path"] + change["diff"]):
            raise HarnessError("unsafe proposal display")
    return path, document


def approve(directory: Path, phase: str, document: dict, timeout: float = 900) -> None:
    review, approval = directory / f"{phase}.review.txt", directory / f"{phase}.approve"
    if approval.exists():
        raise HarnessError("approval existed before review")
    with review.open("x", encoding="utf-8") as stream:
        stream.write("Digest: " + document["proposal_digest"] + "\n")
        for change in document["changes"]:
            stream.write(change["path"] + "\n" + change["diff"] + "\n")
    print(f"Review {review}; write the exact digest to {approval}", flush=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if approval.exists():
            if approval.read_text(encoding="utf-8") != document["proposal_digest"]:
                raise HarnessError("operator did not approve the exact digest")
            return
        time.sleep(1)
    raise HarnessError("operator approval timed out")


def check_applied(root: Path, document: dict, before: dict[str, str]) -> None:
    after = state(root, include_pending=False)
    expected = dict(before)
    for change in document["changes"]:
        rel = change["path"]
        expected[rel] = hashlib.sha256(change["after_text"].encode("utf-8")).hexdigest()
    # Receipts are separately checked against the exact digest and runtime.
    without_receipts = lambda value: {k: v for k, v in value.items() if not k.startswith(".context-os/receipts/")}
    if without_receipts(after) != without_receipts(expected):
        raise HarnessError("apply changed unexpected files or produced incorrect content")


def execute(harness: CursorHarness, approvals: Path, evidence: Path) -> dict:
    harness.env["PYTHONDONTWRITEBYTECODE"] = "1"
    source_sha = repository_source_sha()
    if source_sha != harness.evidence.source_sha:
        raise HarnessError("source revision mismatch")
    controls = {}
    handoff_fact = "The synthetic fixture must verify continuity using " + secrets.token_hex(16) + "."
    facts = {
        "setup": "The fixture tests portable continuity.",
        "update": "The synthetic fixture completed its Cursor setup test.",
        "end": handoff_fact,
    }
    result = {"runtime": "cursor", "surface": "cli", "source_sha": source_sha,
              "controls": controls, "operator": "external-exact-digest",
              "os": platform.platform(), "model_selection": "Cursor configured default",
              "started_at": datetime.now(timezone.utc).isoformat(),
              "prompts": {}, "phases": {}, "kernel_commands": [],
              "limits": ["No IDE, hook, MCP execution, or native-memory claim.",
                         "Scoped to the recorded client, model selection, and operating system."]}
    current = "preflight"
    try:
        with harness.disposable_workspace() as temporary:
            root = temporary / "workspace"
            cloned = subprocess.run(["git", "clone", "--local", "--no-hardlinks", "--quiet",
                                     str(REPOSITORY_ROOT), str(root)], capture_output=True, check=False)
            if cloned.returncode:
                raise HarnessError("cannot clone clean source fixture")
            harness.preflight(root)
            (root / "unrelated-sentinel.txt").write_text(secrets.token_hex(24), encoding="utf-8")
            controls[current] = "passed"
            for phase in PHASES:
                current = phase
                print(f"Cursor lifecycle: {phase}", flush=True)
                before = state(root, include_pending=phase == "start")
                pending = set((root / ".context-os/proposals").glob("*.json"))
                detail = {
                    "setup": "Audience confirmed: synthetic public fixture only. Use identity/lifecycle-fixture.md containing '# Synthetic lifecycle identity\\n\\nThe fixture tests portable continuity.\\n'.",
                    "start": "Read the continuity inventory and summarize it. Make no changes.",
                    "update": "Record this fact: The synthetic fixture completed its Cursor setup test.",
                    "end": "Record this outcome: The synthetic fixture completed its Cursor lifecycle test. Record this exact next action: " + handoff_fact,
                }[phase]
                prompt = (f"/context-{phase} This is an explicitly authorized synthetic lifecycle fixture. "
                          f"Use the colocated repository. {detail} "
                          "For mutations, create exactly one kernel proposal, display its diff and digest, "
                          "then stop. Do not apply, commit, push, or modify other files. "
                          "Use .context-os/inputs for payloads. Do not use host-native memory as input.")
                result["prompts"][phase] = prompt
                response = harness.agent(root, prompt, *( ["--mode", "ask"] if phase == "start" else []))
                require_json_result(response, f"{phase} lifecycle")
                if state(root, include_pending=phase == "start") != before:
                    raise HarnessError("lifecycle changed files before operator apply")
                head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
                if head != source_sha:
                    raise HarnessError("model changed fixture HEAD")
                if phase == "start":
                    controls["start_read_only"] = "passed"
                    continue
                path, document = proposal(root, pending, phase)
                require_fact(document, facts[phase])
                raw = path.read_bytes()
                approve(approvals, phase, document)
                if path.read_bytes() != raw:
                    raise HarnessError("proposal changed after operator review")
                digest = document["proposal_digest"]
                def kernel(confirm: str):
                    output = harness.runner([sys.executable, "-m", "contextos", "apply",
                                           path.relative_to(root).as_posix(), "--confirm", confirm,
                                           "--runtime", "cursor"], root, harness.env, harness.timeout)
                    result["kernel_commands"].append(output_summary(output))
                    return output
                rejected_before = state(root)
                wrong = kernel("0" * 64 if digest != "0" * 64 else "1" * 64)
                if not wrong.returncode or "--confirm must exactly match" not in wrong.stderr + wrong.stdout:
                    raise HarnessError("wrong digest was not rejected")
                if state(root) != rejected_before:
                    raise HarnessError("wrong-digest rejection mutated fixture")
                controls[f"{phase}_wrong_digest_rejected"] = "passed"
                receipts_before = set((root / ".context-os/receipts").glob("*.json"))
                require_success(kernel(digest), "approved apply")
                added = set((root / ".context-os/receipts").glob("*.json")) - receipts_before
                if len(added) != 1:
                    raise HarnessError("apply must emit exactly one receipt")
                receipt_path = added.pop()
                receipt_raw = receipt_path.read_bytes()
                receipt = json.loads(receipt_raw.decode("utf-8"))
                if receipt.get("proposal_digest") != digest or receipt.get("runtime") != "cursor":
                    raise HarnessError("receipt does not bind the Cursor proposal")
                check_applied(root, document, before)
                result["phases"][phase] = {
                    "proposal_digest": digest,
                    "proposal_sha256": hashlib.sha256(raw).hexdigest(),
                    "receipt": receipt_path.relative_to(root).as_posix(),
                    "receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
                    "receipt_proposal_digest": receipt["proposal_digest"],
                    "receipt_runtime": receipt["runtime"],
                    "applied_files": {change["path"]: hashlib.sha256(
                        (root / change["path"]).read_bytes()).hexdigest() for change in document["changes"]},
                }
                controls[f"{phase}_proposal_apply"] = "passed"
                if phase != "setup":
                    stale_before = state(root)
                    stale = kernel(digest)
                    if not stale.returncode or "refusing stale proposal; file changed" not in stale.stdout + stale.stderr:
                        raise HarnessError("stale proposal was not rejected")
                    if state(root) != stale_before:
                        raise HarnessError("stale rejection mutated fixture")
                    controls[f"{phase}_stale_rejected"] = "passed"
            current = "handoff"
            before = state(root)
            result["prompts"]["handoff"] = "/context-start Read the saved session and report the exact next action for the synthetic fixture, including its verification value."
            answer = require_json_result(harness.agent(root,
                result["prompts"]["handoff"],
                "--mode", "ask"), "new-session handoff")
            if handoff_fact not in answer or state(root) != before:
                raise HarnessError("new session did not recover the saved next action read-only")
            controls[current] = "passed"
            harness.verify_binary()
            if repository_source_sha() != source_sha:
                raise HarnessError("source changed during live run")
            controls["run"] = "passed"
    except Exception as exc:
        controls[current] = "failed"
        controls["run"] = "failed"
        # Local diagnostics only; shareable evidence excludes raw model output and paths.
        print(f"Cursor lifecycle failed: {exc}", file=sys.stderr)
        result["failure_type"] = type(exc).__name__
    result["host"] = vars(harness.evidence)
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    evidence = require_outside_source(evidence)
    with evidence.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "expected-version", "source-sha", "evidence", "approval-dir"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--allow-model-traffic", action="store_true")
    args = parser.parse_args()
    if not args.allow_model_traffic:
        parser.error("requires --allow-model-traffic for disposable synthetic model calls")
    approvals = require_outside_source(Path(args.approval_dir))
    evidence = require_outside_source(Path(args.evidence))
    if not approvals.is_dir() or any(approvals.iterdir()) or evidence.exists():
        parser.error("use an empty external approval directory and a new evidence path")
    harness = CursorHarness(Path(args.binary), args.expected_version, args.source_sha)
    return 0 if execute(harness, approvals, evidence)["controls"]["run"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
