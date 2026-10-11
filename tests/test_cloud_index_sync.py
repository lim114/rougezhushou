"""Cloud continuation preserves current requirements and truthful validation."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.update_cloud_index import update


class CloudIndexSyncTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        checkpoint = {'completed_sections': 185, 'next_section': 186,
                      'batch_status': 'IN_PROGRESS', 'next_full_validation_after': 200,
                      'sections': [], 'policy': {'current_user_batch_target_section': 285}}
        (self.root/'DEVELOPMENT_CHECKPOINT.json').write_text(json.dumps(checkpoint), encoding='utf-8')
        for file in ('PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'PROJECT_COMPLETED.md', 'AGENTS.md'):
            (self.root/file).write_text('Public current document: '+file, encoding='utf-8')
        (self.root/'CLOUD_HANDOFF.md').write_text('Historical migration context', encoding='utf-8')
        (self.root/'PROJECT_REQUIREMENTS.md').write_text('当前要求：本局只读，未知保留。', encoding='utf-8')
        receipt = self.root/'verification/full-185/native.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({'available_checks_passed': False}), encoding='utf-8')

    def test_requirements_are_versioned_with_current_checkpoint_and_failed_validation(self):
        update(self.root)
        index = json.loads((self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'))
        expected = hashlib.sha256((self.root/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()
        self.assertEqual(index['requirements']['sha256'], expected)
        self.assertEqual(index['public_pointers']['PROJECT_REQUIREMENTS.md'], expected)
        self.assertEqual(index['current_batch_target_section'], 285)
        self.assertFalse(index['latest_full_available_checks_passed'])
        (self.root/'PROJECT_REQUIREMENTS.md').write_text('更新要求：不发送聊天。', encoding='utf-8')
        update(self.root)
        changed = json.loads((self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'))
        self.assertNotEqual(changed['requirements']['sha256'], expected)

    def test_repeated_update_preserves_historical_context_and_excludes_private_state(self):
        private = self.root/'.local'
        private.mkdir()
        (private/'run-state.json').write_text('PRIVATE_RUN_SENTINEL', encoding='utf-8')
        update(self.root)
        first = (self.root/'CLOUD_HANDOFF.md').read_text(encoding='utf-8')
        update(self.root)
        final = (self.root/'CLOUD_HANDOFF.md').read_text(encoding='utf-8')
        self.assertEqual(first, final)
        self.assertEqual(final.count('<!-- live-cloud-index:start -->'), 1)
        self.assertIn('Historical migration context', final)
        self.assertIn('PROJECT_REQUIREMENTS.md', final)
        self.assertNotIn('PRIVATE_RUN_SENTINEL', final)
        self.assertNotIn('PRIVATE_RUN_SENTINEL', (self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'))

    def test_missing_requirements_fail_before_overwriting_existing_index(self):
        (self.root/'CLOUD_INDEX.json').write_text('Existing publication', encoding='utf-8')
        (self.root/'PROJECT_REQUIREMENTS.md').unlink()
        with self.assertRaisesRegex(FileNotFoundError, 'PROJECT_REQUIREMENTS'):
            update(self.root)
        self.assertEqual((self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'), 'Existing publication')
