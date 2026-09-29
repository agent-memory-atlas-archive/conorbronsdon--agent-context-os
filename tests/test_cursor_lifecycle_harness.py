from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from adapters.cursor import lifecycle_conformance as live
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


if __name__ == '__main__':
    unittest.main()
