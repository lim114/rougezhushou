"""Public, read-only provenance checks using temporary copies of real evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts import verify_original_animation_provenance as provenance

ROOT = Path(__file__).resolve().parents[1]
ENTRY_LEDGER = {'CLI_invocations': 0, 'direct_verifier_entries': 0,
                'CLI_reported_verifier_entries': 0}


class OriginalAnimationProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for key in ENTRY_LEDGER:
            ENTRY_LEDGER[key] = 0
        cls.source_paths = [ROOT / provenance.DATA_RELATIVE,
                            ROOT / provenance.EVIDENCE_RELATIVE / 'public-artifacts-manifest087.json']
        cls.source_paths.extend(ROOT / provenance.EVIDENCE_RELATIVE / name
                                for name in provenance.REQUIRED_LEAVES)
        cls.original_hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in cls.source_paths}

    @classmethod
    def tearDownClass(cls):
        actual = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in cls.source_paths}
        if actual != cls.original_hashes:
            raise AssertionError('Verification mutated repository source inputs')

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='动画 source relocation ')
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.checkout = self.workspace / '移植 checkout with spaces'
        for path in self.source_paths:
            target = self.checkout / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        self.script = self.checkout / 'scripts/verify_original_animation_provenance.py'
        self.script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(provenance.__file__), self.script)
        self.packet = self.checkout / provenance.EVIDENCE_RELATIVE
        self.data_path = self.checkout / provenance.DATA_RELATIVE
        self.foreign_cwd = self.workspace / 'unrelated 工作目录'
        self.foreign_cwd.mkdir()

    def restore_inputs(self):
        for path in self.source_paths:
            target = self.checkout / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)

    def hashes(self):
        return {path.relative_to(self.workspace).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.workspace.rglob('*') if path.is_file()}

    def invoke_cli(self, *arguments):
        before = self.hashes()
        ENTRY_LEDGER['CLI_invocations'] += 1
        result = subprocess.run([sys.executable, '-I', str(self.script), *map(str, arguments)],
                                cwd=self.foreign_cwd, capture_output=True, text=True,
                                encoding='utf-8', timeout=20)
        self.assertEqual(self.hashes(), before)
        self.assertEqual(result.stderr, '')
        report = json.loads(result.stdout)
        self.assertEqual(report['verifier_function_entries'], 1)
        ENTRY_LEDGER['CLI_reported_verifier_entries'] += report['verifier_function_entries']
        for key in ('source_skeleton_parser_calls', 'network_calls', 'application_API_calls',
                    'project_helper_calls'):
            self.assertEqual(report[key], 0)
        return result.returncode, report

    def assert_direct_error(self, code):
        before = self.hashes()
        ENTRY_LEDGER['direct_verifier_entries'] += 1
        with self.assertRaises(provenance.ProvenanceError) as caught:
            provenance.verify(repository_root=self.checkout)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(self.hashes(), before)

    def mutate_data(self, change):
        data = json.loads(self.data_path.read_bytes())
        change(data)
        self.data_path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n')
                                   .replace('\n', '\r\n').encode())

    def test_relocation_default_root_and_explicit_paths_from_foreign_cwd(self):
        code, default = self.invoke_cli()
        self.assertEqual(code, 0)
        self.assertTrue(default['passed'])
        self.assertEqual(default['verified_leaf_count'], 6)
        self.assertEqual(default['added_back_records'], 5)
        self.assertTrue(default['full_historical_inverse_byte_exact'])
        self.assertFalse(default['generic_skill_has_skill_number'])
        self.assertFalse(default['runtime_binding_verified'])
        separate = self.workspace / '独立 evidence folder'
        shutil.move(self.packet, separate)
        relocated_data = self.workspace / '独立 references.json'
        shutil.move(self.data_path, relocated_data)
        code, explicit = self.invoke_cli('--repository-root', self.checkout,
                                         '--references', relocated_data, '--evidence-dir', separate)
        self.assertEqual(code, 0)
        self.assertEqual(explicit, default)

    def test_each_saved_public_leaf_corruption_is_detected_without_a_reader(self):
        for name in provenance.REQUIRED_LEAVES:
            with self.subTest(leaf=name):
                self.restore_inputs()
                path = self.packet / name
                raw = bytearray(path.read_bytes())
                raw[-1] ^= 1
                path.write_bytes(raw)
                self.assert_direct_error('source_hash_mismatch')

    def test_derived_records_detect_float_frame_preview_and_absent_motion_changes(self):
        def attack(data):
            return next(r for r in data['operators'][provenance.OPERATOR]['records']
                        if r['id'] == provenance.OPERATOR + ':Back:Attack')

        def wrong_duration(data):
            attack(data)['duration']['seconds'] += .1

        def wrong_frame(data):
            attack(data)['events'][0]['raw_frames_30hz'] += 1

        def wrong_preview_type(data):
            attack(data)['preview']['windup_frames'] = True

        def absent_start(data):
            records = data['operators'][provenance.OPERATOR]['records']
            records[:] = [r for r in records if r['id'] != provenance.OPERATOR + ':Back:Start']

        def invented_die(data):
            # Deliberate corruption, not a claim that the real skeleton has Die.
            records = data['operators'][provenance.OPERATOR]['records']
            fake = copy.deepcopy(next(r for r in records if r['animation'] == 'Default'
                                     and r['orientation'] == 'Back'))
            fake['id'] = provenance.OPERATOR + ':Back:Die'
            fake['animation'] = 'Die'
            records.append(fake)

        for change in (wrong_duration, wrong_frame, wrong_preview_type, absent_start, invented_die):
            with self.subTest(change=change.__name__):
                self.restore_inputs()
                self.mutate_data(change)
                self.assert_direct_error('derived_records_mismatch')

    def test_binding_flags_and_generic_skill_number_cannot_be_certified(self):
        def runtime_true(data):
            next(r for r in data['operators'][provenance.OPERATOR]['records']
                 if r['id'] == provenance.OPERATOR + ':Back:Attack')['runtime_binding_verified'] = True

        def inferred_true(data):
            data['source_additions'][0]['runtime_binding_inferred'] = True

        def numbered_generic(data):
            next(r for r in data['operators'][provenance.OPERATOR]['records']
                 if r['id'] == provenance.OPERATOR + ':Back:Skill')['animation'] = 'Skill_1'

        def changed_default_binding(data):
            data['binding_status'] = 'native_binding_claim'

        for change, code in ((runtime_true, 'binding_scope_mismatch'),
                             (inferred_true, 'binding_scope_mismatch'),
                             (numbered_generic, 'generic_skill_binding_mismatch'),
                             (changed_default_binding, 'binding_scope_mismatch')):
            with self.subTest(change=change.__name__):
                self.restore_inputs()
                self.mutate_data(change)
                self.assert_direct_error(code)

    def test_old_dataset_inverse_and_future_snapshot_have_distinct_results(self):
        def changed_front(data):
            next(r for r in data['operators'][provenance.OPERATOR]['records']
                 if r['orientation'] == 'Front')['duration']['seconds'] += .1

        def changed_other_profile(data):
            key = next(key for key in data['operators'] if key != provenance.OPERATOR)
            data['operators'][key]['name'] += ' changed'

        for change in (changed_front, changed_other_profile):
            with self.subTest(change=change.__name__):
                self.restore_inputs()
                self.mutate_data(change)
                self.assert_direct_error('historical_inverse_mismatch')
        self.restore_inputs()

        def outside_snapshot(data):
            # Simulate an additional, separately declared source scope. The CLI
            # must decline certification, not claim it is valid or corrupt.
            data['source_additions'].append({'operator': 'later_scope', 'orientation': 'Front'})

        self.mutate_data(outside_snapshot)
        code, report = self.invoke_cli()
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'outside_supported_snapshot')
        self.assertFalse(report['passed'])

    def test_every_missing_leaf_and_corrupted_manifest_fail_explicitly(self):
        for name in provenance.REQUIRED_LEAVES:
            with self.subTest(missing=name):
                self.restore_inputs()
                (self.packet / name).unlink()
                code, report = self.invoke_cli()
                self.assertEqual(code, 1)
                self.assertEqual(report['code'], 'input_unavailable')
                self.assertIn(Path(name).name, report['message'])
                self.assertFalse(report['passed'])
        self.restore_inputs()
        manifest = self.packet / 'public-artifacts-manifest087.json'
        raw = bytearray(manifest.read_bytes())
        raw[-1] ^= 1
        manifest.write_bytes(raw)
        code, report = self.invoke_cli()
        self.assertEqual(code, 1)
        self.assertEqual(report['code'], 'manifest_hash_mismatch')
        self.assertFalse(report['passed'])


if __name__ == '__main__':
    unittest.main()
