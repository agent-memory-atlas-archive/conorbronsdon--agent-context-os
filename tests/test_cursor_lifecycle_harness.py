from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import os
import subprocess
import sys
import time
import unittest
from unittest import mock

from adapters.cursor import lifecycle_conformance as live
from adapters.cursor.live_conformance import default_runner
from contextos.primitives import canonical_json


class CursorLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_proposal_binds_workflow_and_digest(self):
        folder = self.root / '.context-os/proposals'
        folder.mkdir(parents=True)
        document = {'workflow': 'update', 'changes': [
            {'path': 'state/current.md', 'diff': '+new', 'after_text': 'new'}]}
        document['proposal_digest'] = hashlib.sha256(canonical_json(document).encode()).hexdigest()
        path = folder / 'proposal.json'
        path.write_text(json.dumps(document))
        self.assertEqual(document, live.proposal(self.root, set(), 'update')[1])
        with self.assertRaisesRegex(live.HarnessError, 'wrong workflow'):
            live.proposal(self.root, set(), 'end')
        document['changes'][0]['after_text'] = 'substituted'
        path.write_text(json.dumps(document))
        with self.assertRaisesRegex(Exception, 'digest does not match'):
            live.proposal(self.root, set(), 'update')

    def test_pending_exclusion_does_not_hide_receipts_or_state(self):
        for rel in ('.context-os/inputs/x.json', '.context-os/proposals/x.json',
                    '.context-os/receipts/x.json', 'state/current.md'):
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('original')
        baseline = live.state(self.root, include_pending=False)
        (self.root / '.context-os/inputs/x.json').write_text('payload')
        self.assertEqual(baseline, live.state(self.root, include_pending=False))
        (self.root / 'state/current.md').write_text('premature apply')
        self.assertNotEqual(baseline, live.state(self.root, include_pending=False))

    def test_apply_checks_content_and_unrelated_files(self):
        (self.root / 'sentinel').write_text('untouched')
        baseline = live.state(self.root)
        document = {'changes': [{'path': 'target', 'after_text': 'approved'}]}
        (self.root / 'target').write_text('approved')
        live.check_applied(self.root, document, baseline)
        (self.root / 'sentinel').write_text('modified')
        with self.assertRaisesRegex(live.HarnessError, 'unexpected files'):
            live.check_applied(self.root, document, baseline)

    def test_approval_is_not_inferred_from_file_presence(self):
        (self.root / 'setup.approve').write_text('wrong')
        with self.assertRaisesRegex(live.HarnessError, 'before review'):
            live.approve(self.root, 'setup', {'proposal_digest': 'a' * 64}, timeout=0)

    def test_requested_fact_must_be_saved_not_only_displayed(self):
        document = {'changes': [{'after_text': 'actual saved fact', 'diff': '+expected fact'}]}
        live.require_fact(document, 'actual saved fact')
        with self.assertRaisesRegex(live.HarnessError, 'omitted'):
            live.require_fact(document, 'expected fact')

    def test_timeout_stops_descendants_holding_output_pipes(self):
        started = time.monotonic()
        script = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); time.sleep(60)"
        with self.assertRaises(subprocess.TimeoutExpired):
            default_runner([sys.executable, '-c', script], self.root, os.environ, 0.5)
        self.assertLess(time.monotonic() - started, 15)

    def test_runner_preserves_success_output(self):
        result = default_runner([sys.executable, '-c', "print('control')"], self.root, os.environ, 10)
        self.assertEqual(0, result.returncode)
        self.assertEqual('control\n', result.stdout)

    def test_interrupt_cleans_up_process_and_preserves_exception(self):
        process = mock.Mock(pid=123)
        process.communicate.side_effect = [KeyboardInterrupt, ('', '')]
        with mock.patch('adapters.cursor.live_conformance.subprocess.Popen', return_value=process), \
             mock.patch('adapters.cursor.live_conformance.subprocess.run'), \
             mock.patch('adapters.cursor.live_conformance.os.killpg', create=True), \
             self.assertRaises(KeyboardInterrupt):
            default_runner(['fixture'], self.root, {}, 10)
        process.kill.assert_called_once()
        self.assertEqual(2, process.communicate.call_count)

    def test_git_state_detects_refs_config_and_staged_changes(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'seed').write_text('seed')
        subprocess.run(['git', 'add', 'seed'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                        'commit', '-qm', 'seed'], cwd=self.root, check=True)
        before = live.git_state(self.root)
        subprocess.run(['git', 'tag', 'unexpected'], cwd=self.root, check=True)
        self.assertNotEqual(before, live.git_state(self.root))
        (self.root / 'seed').write_text('staged')
        subprocess.run(['git', 'add', 'seed'], cwd=self.root, check=True)
        with self.assertRaisesRegex(live.HarnessError, 'index changed'):
            live.git_state(self.root)

    def test_proposal_rejects_unicode_display_spoofing(self):
        folder = self.root / '.context-os/proposals'
        folder.mkdir(parents=True)
        for control in ('\x7f', '\x85', '\u202e', '\u2066'):
            document = {'workflow': 'update', 'changes': [
                {'path': 'state/current.md', 'diff': '+' + control, 'after_text': control}]}
            document['proposal_digest'] = hashlib.sha256(canonical_json(document).encode()).hexdigest()
            (folder / 'proposal.json').write_text(json.dumps(document))
            with self.subTest(control=repr(control)), self.assertRaisesRegex(live.HarnessError, 'unsafe proposal display'):
                live.proposal(self.root, set(), 'update')


if __name__ == '__main__':
    unittest.main()
