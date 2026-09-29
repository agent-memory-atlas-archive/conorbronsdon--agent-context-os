from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "adapters/cursor/ide_conformance.py"
SPEC = importlib.util.spec_from_file_location("contextos_cursor_ide", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ide = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ide
SPEC.loader.exec_module(ide)


class CursorIdeHarnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.binary = self.root / "Cursor.exe"
        self.binary.write_bytes(b"synthetic cursor binary")
        self.source_sha = "a" * 40
        self.workspace = self.root / "workspace"
        self.profile = self.root / "profile"
        self.manifest = self.root / "manifest.json"
        self.evidence = self.root / "evidence.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def prepare(self) -> dict[str, object]:
        args = argparse.Namespace(
            binary=self.binary,
            binary_sha256=ide.sha256_file(self.binary),
            expected_version="3.18.25",
            source_sha=self.source_sha,
            workspace=self.workspace,
            profile=self.profile,
            manifest=self.manifest,
            allow_model_traffic=True,
            acknowledge_disposable_workspace=True,
        )
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            ide.prepare(args)
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def test_prepare_builds_distinct_ide_controls(self) -> None:
        manifest = self.prepare()
        self.assertEqual("ide", manifest["surface"])
        self.assertNotEqual(manifest["workspace"], manifest["profile"])
        self.assertFalse((self.workspace / ".cursor/mcp.json").exists())
        self.assertFalse((self.workspace / ".cursor/hooks.json").exists())
        rule = (self.workspace / ".cursor/rules/conformance.mdc").read_text()
        self.assertIn("alwaysApply: true", rule)
        explicit = (
            self.workspace / ".agents/skills/contextos-live-explicit/SKILL.md"
        ).read_text()
        short_update = (
            self.workspace / ".agents/skills/update/SKILL.md"
        ).read_text()
        self.assertIn("disable-model-invocation: true", explicit)
        self.assertIn("disable-model-invocation: true", short_update)
        self.assertIn("/update", manifest["prompts"]["short_update"])
        self.assertIn("do not submit or execute", manifest["prompts"]["short_update"])
        self.assertEqual(
            "IDE control cannot exclude a direct read of the skill file",
            manifest["unverified_controls"]["explicit_skill_must_fire"],
        )

    def test_prepare_requires_exact_binary_hash_and_opt_ins(self) -> None:
        args = argparse.Namespace(
            binary=self.binary,
            binary_sha256="0" * 64,
            expected_version="3.18.25",
            source_sha=self.source_sha,
            workspace=self.workspace,
            profile=self.profile,
            manifest=self.manifest,
            allow_model_traffic=True,
            acknowledge_disposable_workspace=True,
        )
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            with self.assertRaisesRegex(ide.HarnessError, "SHA-256"):
                ide.prepare(args)
        args.allow_model_traffic = False
        with self.assertRaisesRegex(ide.HarnessError, "opt-in"):
            ide.prepare(args)

    def valid_observations(self, canaries: dict[str, str]) -> dict[str, object]:
        return {
            "root_response": canaries["root"],
            "nested_response": canaries["nested"],
            "rule_response": canaries["rule"],
            "conflict_response": canaries["conflict_rule"],
            "implicit_response": "NO_SKILL_BODY",
            "explicit_response": canaries["skill"],
            "short_update_resolution": "ambiguous",
            "ask_write_denied": True,
            "agent_write_denied": True,
            "agent_write_approved": True,
            "short_update_not_executed": True,
            "implicit_skill_body_not_loaded": True,
        }

    def test_record_verifies_canaries_and_exact_file_outcome(self) -> None:
        manifest = self.prepare()
        (self.profile / "profile-marker").write_text("used\n", encoding="utf-8")
        (self.workspace / ide.APPROVED_FILE).write_text(
            ide.APPROVED_CONTENT + "\n", encoding="utf-8"
        )
        observations = self.root / "observations.json"
        observations.write_text(
            json.dumps(self.valid_observations(manifest["canaries"])) + "\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            manifest=self.manifest,
            observations=observations,
            evidence=self.evidence,
            acknowledge_operator_attestation=True,
        )
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            ide.record(args)
        evidence = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual("project_rule", evidence["instruction_rule_conflict_winner"])
        self.assertEqual("ambiguous", evidence["short_update_resolution"])
        self.assertEqual("operator-attested-with-local-verification", evidence["evidence_kind"])
        self.assertTrue(evidence["attested_controls"]["interactive_approval_is_scoped"])
        self.assertTrue(evidence["verified_controls"]["fixture_mutation_is_scoped"])
        self.assertEqual(64, len(evidence["native_profile_snapshot_sha256"]))
        self.assertNotIn("canaries", evidence)
        self.assertNotIn("explicit_skill_must_fire", evidence["attested_controls"])
        self.assertEqual(
            "IDE control cannot exclude a direct read of the skill file",
            evidence["unverified_controls"]["explicit_skill_must_fire"],
        )

    def test_record_rejects_denied_or_unexpected_writes(self) -> None:
        manifest = self.prepare()
        (self.profile / "profile-marker").write_text("used\n", encoding="utf-8")
        (self.workspace / "ask-write.txt").write_text("unexpected\n")
        (self.workspace / ide.APPROVED_FILE).write_text(ide.APPROVED_CONTENT + "\n")
        observations = self.root / "observations.json"
        observations.write_text(
            json.dumps(self.valid_observations(manifest["canaries"])), encoding="utf-8"
        )
        args = argparse.Namespace(
            manifest=self.manifest,
            observations=observations,
            evidence=self.evidence,
            acknowledge_operator_attestation=True,
        )
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            with self.assertRaisesRegex(ide.HarnessError, "denied control wrote"):
                ide.record(args)

    def diagnostic_fixture(self):
        manifest = self.prepare()
        (self.profile / "profile-marker").write_text("used\n", encoding="utf-8")
        (self.workspace / ide.APPROVED_FILE).write_text(ide.APPROVED_CONTENT, encoding="utf-8")
        (self.workspace / "denied-write.txt").write_text(ide.DENIED_CONTENT, encoding="utf-8")
        observations = self.valid_observations(manifest["canaries"])
        observations.pop("agent_write_denied")
        observations.pop("agent_write_approved")
        observations.update(agent_write_behavior="immediate", file_write_control_observed=True)
        path = self.root / "observations.json"
        path.write_text(json.dumps(observations), encoding="utf-8")
        args = argparse.Namespace(
            manifest=self.manifest, observations=path, evidence=self.evidence,
            acknowledge_operator_attestation=True, characterize_file_writes=True,
        )
        return args, observations

    def test_immediate_write_diagnostic_cannot_claim_approval_or_promotion(self) -> None:
        args, _ = self.diagnostic_fixture()
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            ide.record(args)
        evidence = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual("operator-attested-write-characterization", evidence["evidence_kind"])
        self.assertIs(False, evidence["promotion_eligible"])
        self.assertEqual("immediate", evidence["agent_write_behavior"])
        self.assertNotIn("interactive_denial_preserves_files", evidence["attested_controls"])
        self.assertNotIn("interactive_approval_is_scoped", evidence["attested_controls"])
        self.assertIn("explicit_skill_must_fire", evidence["unverified_controls"])

    def test_strict_record_does_not_accept_diagnostic_immediate_write(self) -> None:
        args, observations = self.diagnostic_fixture()
        args.characterize_file_writes = False
        observations.update(agent_write_denied=True, agent_write_approved=True)
        args.observations.write_text(json.dumps(observations), encoding="utf-8")
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            with self.assertRaisesRegex(ide.HarnessError, "denied control wrote"):
                ide.record(args)
        self.assertFalse(self.evidence.exists())

    def test_diagnostic_still_rejects_unrelated_or_ask_writes(self) -> None:
        args, _ = self.diagnostic_fixture()
        for name in ("ask-write.txt", "unrelated.txt"):
            with self.subTest(name=name):
                path = self.workspace / name
                path.write_text("unexpected", encoding="utf-8")
                with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
                    with self.assertRaises(ide.HarnessError):
                        ide.record(args)
                path.unlink()
                self.assertFalse(self.evidence.exists())

    def test_diagnostic_requires_observation_and_exact_immediate_write(self) -> None:
        args, observations = self.diagnostic_fixture()
        for missing in ("agent_write_behavior", "file_write_control_observed"):
            with self.subTest(missing=missing):
                reduced = {key: value for key, value in observations.items() if key != missing}
                args.observations.write_text(json.dumps(reduced), encoding="utf-8")
                with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
                    with self.assertRaises(ide.HarnessError):
                        ide.record(args)
        args.observations.write_text(json.dumps(observations), encoding="utf-8")
        path = self.workspace / "denied-write.txt"
        path.write_text("wrong content", encoding="utf-8")
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            with self.assertRaises(ide.HarnessError):
                ide.record(args)
        path.unlink()
        with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
            with self.assertRaises(ide.HarnessError):
                ide.record(args)
        self.assertFalse(self.evidence.exists())

    def test_final_reply_cannot_hide_implicit_skill_body_loading(self) -> None:
        args, observations = self.diagnostic_fixture()
        for characterize in (False, True):
            for value in (False, None):
                with self.subTest(characterize=characterize, attestation=value):
                    args.characterize_file_writes = characterize
                    candidate = dict(observations, agent_write_denied=True, agent_write_approved=True)
                    if value is None:
                        candidate.pop("implicit_skill_body_not_loaded")
                    else:
                        candidate["implicit_skill_body_not_loaded"] = value
                    args.observations.write_text(json.dumps(candidate), encoding="utf-8")
                    with mock.patch.object(ide, "repository_source_sha", return_value=self.source_sha):
                        with self.assertRaisesRegex(ide.HarnessError, "implicit_skill_body_not_loaded"):
                            ide.record(args)
                    self.assertFalse(self.evidence.exists())

    def test_record_is_create_only_and_requires_attestation(self) -> None:
        self.evidence.write_text("existing\n", encoding="utf-8")
        with self.assertRaisesRegex(ide.HarnessError, "refusing to overwrite"):
            ide.write_create_only(self.evidence, {"value": True})
        args = argparse.Namespace(acknowledge_operator_attestation=False)
        with self.assertRaisesRegex(ide.HarnessError, "operator-attestation"):
            ide.record(args)

    def test_source_never_launches_cursor_or_invokes_update(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("Start-Process", source)
        self.assertNotIn("subprocess.Popen", source)
        self.assertNotIn('"/update"', source)
        self.assertIn("short_update_must_not_execute", source)


if __name__ == "__main__":
    unittest.main()
