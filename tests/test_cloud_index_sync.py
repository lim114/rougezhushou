"""Cloud continuation preserves current requirements and truthful validation."""
import copy
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
        checkpoint = {'branch': 'codex/p2-development',
                      'completed_sections': 185, 'next_section': 186,
                      'batch_status': 'IN_PROGRESS', 'next_full_validation_after': 200,
                      'sections': [{'number': 185, 'verification': 'verification/sections/185.json'}],
                      'policy': {'current_user_batch_target_section': 285,
                                 'next_full_validation_after': 200},
                      'current_batch_commit_policy': {'next_full_validation_after': 200},
                      'current_section_save': {'section': 185,
                          'verification': 'verification/sections/185.json',
                          'scope': 'current_functional_section', 'binding': 'enclosing_commit'}}
        section = self.root/'verification/sections/185.json'
        section.parent.mkdir(parents=True)
        section.write_text(json.dumps({'section': 185}), encoding='utf-8')
        # Isolated declared publication fixtures exercise consistency only.
        # Real project commit/remote authenticity belongs to root publication audit.
        self.previous_commit = 'a' * 40
        self.current_commit = 'b' * 40
        state_path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        proof = self.root/'verification/publication/185.json'
        proof.parent.mkdir(parents=True)
        proof.write_text(json.dumps({'section': 185, 'passed': True,
            'branch': 'codex/p2-development', 'commit': self.current_commit,
            'local_HEAD': self.current_commit, 'remote_HEAD': self.current_commit,
            'remote_branch': 'origin/codex/p2-development', 'push_primary_exit': 0}), encoding='utf-8')
        checkpoint['last_verified_cloud_save'] = {'section': 185, 'commit': self.current_commit,
            'scope': 'current_functional_section', 'binding': 'verified_remote_commit',
            'proof': 'verification/publication/185.json',
            'proof_sha256': hashlib.sha256(proof.read_bytes()).hexdigest()}
        state_path.write_text(json.dumps(checkpoint), encoding='utf-8')
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

    def test_declared_repair_receipt_is_preferred_over_first_native_receipt(self):
        path=self.root/'DEVELOPMENT_CHECKPOINT.json'
        checkpoint=json.loads(path.read_text(encoding='utf-8'))
        checkpoint['last_full_validation']={'after_section':185,'receipt':'verification/full-185/native-after-repair.json'}
        path.write_text(json.dumps(checkpoint),encoding='utf-8')
        (self.root/'verification/full-185/native-after-repair.json').write_text(json.dumps({'available_checks_passed':True}),encoding='utf-8')
        update(self.root)
        index=json.loads((self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual(index['latest_full_receipt'],'verification/full-185/native-after-repair.json')
        self.assertTrue(index['latest_full_available_checks_passed'])
        self.assertIn('native-after-repair.json',(self.root/'CLOUD_HANDOFF.md').read_text(encoding='utf-8'))

    def test_missing_or_private_declared_receipt_cannot_overwrite_public_index(self):
        path=self.root/'DEVELOPMENT_CHECKPOINT.json'
        checkpoint=json.loads(path.read_text(encoding='utf-8'))
        for reference in ('verification/full-185/missing.json','.local/run-state.json','verification/full-184/native.json'):
            with self.subTest(reference=reference):
                (self.root/'CLOUD_INDEX.json').write_text('Existing publication',encoding='utf-8')
                checkpoint['last_full_validation']={'after_section':185,'receipt':reference}
                path.write_text(json.dumps(checkpoint),encoding='utf-8')
                with self.assertRaises((ValueError,FileNotFoundError)):update(self.root)
                self.assertEqual((self.root/'CLOUD_INDEX.json').read_text(encoding='utf-8'),'Existing publication')

    def test_missing_or_stale_current_save_is_rejected_before_any_output_write(self):
        path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        original = json.loads(path.read_text())
        cases = [
            ('missing current save', lambda cp: cp.pop('current_section_save')),
            ('section mismatch', lambda cp: cp['current_section_save'].update(section=149)),
            ('receipt mismatch', lambda cp: cp['current_section_save'].update(verification='verification/sections/149.json')),
            ('missing current binding', lambda cp: cp['current_section_save'].pop('binding')),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                cp = copy.deepcopy(original)
                mutate(cp)
                path.write_text(json.dumps(cp))
                self.assert_rejected_without_output_change()

    def assert_rejected_without_output_change(self):
        index = self.root/'CLOUD_INDEX.json'
        handoff = self.root/'CLOUD_HANDOFF.md'
        index.write_text('Original index sentinel')
        handoff.write_text('Original handoff sentinel')
        with self.assertRaises((ValueError, FileNotFoundError)):
            update(self.root)
        self.assertEqual(index.read_text(), 'Original index sentinel')
        self.assertEqual(handoff.read_text(), 'Original handoff sentinel')

    def test_stale_unbound_or_forged_publication_is_rejected(self):
        path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        original = json.loads(path.read_text())
        cases = [
            ('old section', lambda cp: cp['last_verified_cloud_save'].update(section=149)),
            ('missing scope', lambda cp: cp['last_verified_cloud_save'].pop('scope')),
            ('missing binding', lambda cp: cp['last_verified_cloud_save'].pop('binding')),
            ('abbreviated commit', lambda cp: cp['last_verified_cloud_save'].update(commit=self.current_commit[:8])),
            ('missing proof', lambda cp: cp['last_verified_cloud_save'].update(proof='verification/publication/missing.json')),
            ('wrong proof hash', lambda cp: cp['last_verified_cloud_save'].update(proof_sha256='0' * 64)),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                cp = copy.deepcopy(original)
                mutate(cp)
                path.write_text(json.dumps(cp))
                self.assert_rejected_without_output_change()
        # Matching commit strings and a recomputed hash do not excuse failed publication.
        cp = copy.deepcopy(original)
        proof = self.root/'verification/publication/185.json'
        data = json.loads(proof.read_text())
        data['passed'] = False
        proof.write_text(json.dumps(data))
        cp['last_verified_cloud_save']['proof_sha256'] = hashlib.sha256(proof.read_bytes()).hexdigest()
        path.write_text(json.dumps(cp))
        self.assert_rejected_without_output_change()

    def test_next_section_cadence_and_other_current_pointers_must_agree(self):
        path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        original = json.loads(path.read_text())
        cases = [
            ('next section', lambda cp: cp.update(next_section=260)),
            ('policy cadence', lambda cp: cp['policy'].update(next_full_validation_after=185)),
            ('active cadence', lambda cp: cp['current_batch_commit_policy'].update(next_full_validation_after=185)),
            ('stale current full', lambda cp: cp.update(current_available_full_validation={'section':140,'receipt':'verification/full-140/summary.json'}, last_full_validation={'after_section':185,'receipt':'verification/full-185/native.json'})),
            ('stale current batch', lambda cp: cp.update(current_batch={'start':143,'end':150},batch_start_section=151,batch_target_section=285)),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                cp = copy.deepcopy(original)
                mutate(cp)
                path.write_text(json.dumps(cp))
                self.assert_rejected_without_output_change()

    def test_previous_verified_section_is_allowed_for_new_function_but_not_paused_maintenance(self):
        path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        cp = json.loads(path.read_text())
        cp['last_verified_cloud_save'].update(section=184, commit=self.previous_commit,
                                             scope='previous_functional_section')
        proof = self.root/'verification/publication/185.json'
        proof.write_text(json.dumps({'section':184,'passed':True,
            'branch':'codex/p2-development','commit':self.previous_commit,
            'local_HEAD':self.previous_commit,
            'remote_HEAD':self.previous_commit,'remote_branch':'origin/codex/p2-development',
            'push_primary_exit':0}))
        cp['last_verified_cloud_save']['proof_sha256'] = hashlib.sha256(proof.read_bytes()).hexdigest()
        path.write_text(json.dumps(cp))
        update(self.root)
        self.assertEqual(json.loads((self.root/'CLOUD_INDEX.json').read_text())['completed_sections'],185)
        cp['policy']['new_functional_sections_paused'] = True
        path.write_text(json.dumps(cp))
        self.assert_rejected_without_output_change()

    def test_current_verified_publication_allows_maintenance_without_new_section(self):
        path = self.root/'DEVELOPMENT_CHECKPOINT.json'
        cp = json.loads(path.read_text())
        cp['policy']['new_functional_sections_paused'] = True
        cp['batch_status'] = 'FUNCTIONAL_TARGET_COMPLETED_FULL_VALIDATION_REPAIR_IN_PROGRESS'
        cp['current_available_full_validation'] = {'section':185,'receipt':'verification/full-185/native.json'}
        cp['last_full_validation'] = {'after_section':185,'receipt':'verification/full-185/native.json'}
        cp.update(batch_start_section=151,batch_target_section=285)
        cp['current_batch'] = {'start':151,'end':285,'status':cp['batch_status'],
                               'next_section':186,'next_full_validation_after':200}
        path.write_text(json.dumps(cp))
        update(self.root)
        result = json.loads((self.root/'CLOUD_INDEX.json').read_text())
        self.assertEqual(result['completed_sections'],185)
        self.assertEqual(result['next_section'],186)
        self.assertEqual(len(result['sections']),1)
        self.assertFalse(result['latest_full_available_checks_passed'])
