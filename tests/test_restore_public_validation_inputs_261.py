"""Integrity and consumer-contract checks; fixtures are synthetic test data."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
from scripts import restore_public_validation_inputs_261 as restore


class PublicSourceIndex261Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.documents = {}
        tables = {}
        for name in sorted(restore.TABLE_NAMES):
            raw = json.dumps({'fixture': name}).encode()
            self.put('.cache/game-data/' + name + '.json', raw)
            tables[name] = {'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'
                           + restore.GAME_COMMIT + '/zh_CN/gamedata/excel/' + name + '.json',
                           'sha256': restore.sha(raw), 'bytes': len(raw)}
        self.documents['rouge/data/catalog.json'] = {'source': {
            'repository': 'Kengxxiao/ArknightsGameData', 'commit': restore.GAME_COMMIT, 'files': tables}}
        image_data = io.BytesIO()
        Image.new('RGB', (2, 3), (23, 41, 59)).save(image_data, format='PNG')
        raw = image_data.getvalue()
        self.put('rouge/data/battle-maps/synthetic.png', raw)
        image = {'file': 'battle-maps/synthetic.png', 'url':
                 'https://raw.githubusercontent.com/fexli/ArknightsResource/' + restore.RESOURCE_COMMIT
                 + '/mapreview/synthetic.png', 'sha256': restore.sha(raw), 'bytes': len(raw),
                 'source_blob_sha1': self.blob(raw), 'width': 2, 'height': 3}
        self.documents['rouge/data/battle-previews.json'] = {'source': {
            'game_commit': restore.GAME_COMMIT, 'resource_commit': restore.RESOURCE_COMMIT},
            'stages': {f'synthetic_{i}': {'image': copy.deepcopy(image)} for i in range(105)}}
        operators = {}
        for i in range(32):
            profile = 'char_synthetic_' + str(i)
            records = []
            for orientation in ('Front', 'Back'):
                raw = ('synthetic skeleton ' + profile + orientation).encode()
                self.put('.cache/research/timing-048/' + profile + '-' + orientation + '.skel', raw)
                records.append({'orientation': orientation, 'source': {
                    'url': 'https://raw.githubusercontent.com/fexli/ArknightsResource/'
                    + restore.RESOURCE_COMMIT + '/spine/' + profile + '/' + profile
                    + '/' + orientation + '/' + profile + '.skel',
                    'sha256': restore.sha(raw), 'git_blob': self.blob(raw), 'bytes': len(raw)}})
            operators[profile] = {'id': profile, 'records': records}
        self.documents['rouge/data/original-animation-references.json'] = {
            'source_commit': restore.RESOURCE_COMMIT, 'counts': {'source_skeletons': 64},
            'operators': operators}
        self.freeze_descriptors()

    @staticmethod
    def blob(raw):
        return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

    def put(self, relative, raw):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)

    def freeze_descriptors(self):
        self.pins = {}
        for relative, data in self.documents.items():
            raw = restore.encoded(data)
            self.put(relative, raw)
            self.pins[relative] = restore.sha(raw)

    def build(self):
        return restore.build_indexes(self.root, '2026-10-13T00:00:00+00:00', self.pins)

    def assert_no_indexes(self):
        self.assertTrue(all(not (self.root / p).exists() for p in restore.TARGETS))

    def test_complete_consumer_schemas_have_fresh_provenance_without_mutating_originals(self):
        indexes, audit = self.build()
        before = {r['path']: (self.root / r['path']).read_bytes() for r in audit['verified_public_originals']}
        self.assertEqual(audit['counts'], {'tables': 5, 'battle_stage_ids': 105,
                         'battle_image_files': 1, 'unique_battle_image_sha256': 1,
                         'original_skeletons': 64, 'verified_original_files': 70})
        self.assert_no_indexes()
        restore.create_indexes(self.root, indexes)
        table, images, skeletons = [json.loads((self.root / p).read_bytes()) for p in restore.TARGETS]
        self.assertEqual(table['commit'], restore.GAME_COMMIT)
        self.assertEqual(table['files'], self.documents['rouge/data/catalog.json']['source']['files'])
        self.assertEqual(images['images'], {sid: stage['image'] for sid, stage in
                                           self.documents['rouge/data/battle-previews.json']['stages'].items()})
        self.assertEqual(len(skeletons), 64)
        self.assertEqual(len({i['url'] for i in skeletons}), 64)
        for metadata in (table, images, *skeletons):
            self.assertEqual(metadata['index_type'], 'fresh_public_source_index')
            self.assertFalse(metadata['historical_download_recreated'])
            self.assertEqual(metadata['checked_at_utc'], '2026-10-13T00:00:00+00:00')
        self.assertEqual(before, {p: (self.root / p).read_bytes() for p in before})

    def test_tampered_table_and_skeleton_are_rejected_before_any_write(self):
        for relative in ('.cache/game-data/character_table.json',
                         '.cache/research/timing-048/char_synthetic_0-Back.skel'):
            with self.subTest(relative=relative):
                p = self.root / relative
                original = p.read_bytes()
                p.write_bytes(original + b'altered')
                with self.assertRaisesRegex(ValueError, 'SHA/size'):
                    self.build()
                self.assert_no_indexes()
                p.write_bytes(original)

    def test_rehashed_wrong_git_blob_and_image_dimensions_cannot_pass(self):
        image = self.documents['rouge/data/battle-previews.json']['stages']['synthetic_0']['image']
        for key, value, message in (('source_blob_sha1', '0' * 40, 'Git blob'),
                                    ('width', 99, 'dimensions')):
            original = image[key]
            image[key] = value
            self.freeze_descriptors()
            with self.assertRaisesRegex(ValueError, message):
                self.build()
            self.assert_no_indexes()
            image[key] = original

    def test_descriptor_hash_and_exact_source_url_and_complete_scope_are_required(self):
        p = self.root / 'rouge/data/catalog.json'
        p.write_bytes(p.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'descriptor changed'):
            self.build()
        source = self.documents['rouge/data/catalog.json']['source']
        source['files']['skill_table']['url'] = source['files']['skill_table']['url'].replace(restore.GAME_COMMIT, 'main')
        self.freeze_descriptors()
        with self.assertRaisesRegex(ValueError, 'Table URL'):
            self.build()
        self.assert_no_indexes()

    def test_duplicate_skeleton_descriptor_cannot_disagree_or_hide_a_missing_face(self):
        animation = self.documents['rouge/data/original-animation-references.json']
        profile = next(iter(animation['operators'].values()))
        record = copy.deepcopy(profile['records'][0])
        record['source']['sha256'] = '0' * 64
        profile['records'].append(record)
        self.freeze_descriptors()
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            self.build()
        profile['records'].pop()
        profile['records'].pop()
        self.freeze_descriptors()
        with self.assertRaisesRegex(ValueError, 'All exact 64'):
            self.build()

    def test_missing_raw_source_and_incomplete_stage_scope_are_rejected(self):
        p = self.root / '.cache/game-data/skill_table.json'
        original = p.read_bytes()
        p.unlink()
        with self.assertRaises(FileNotFoundError):
            self.build()
        self.assert_no_indexes()
        p.write_bytes(original)
        self.documents['rouge/data/battle-previews.json']['stages'].pop('synthetic_104')
        self.freeze_descriptors()
        with self.assertRaisesRegex(ValueError, 'scope/commits'):
            self.build()
        self.assert_no_indexes()

    def test_unsafe_paths_symlinks_and_existing_receipts_are_preserved(self):
        with self.assertRaisesRegex(ValueError, 'escapes'):
            restore.safe_path(self.root, '../private.json')
        p = self.root / '.cache/game-data/skill_table.json'
        raw = p.read_bytes()
        p.unlink()
        outside = self.root / 'synthetic-other-table.json'
        outside.write_bytes(raw)
        p.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.build()
        p.unlink(); p.write_bytes(raw)
        indexes, _ = self.build()
        old = self.root / restore.TARGETS[1]
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_bytes(b'historical receipt must stay unchanged')
        with self.assertRaises(FileExistsError):
            restore.create_indexes(self.root, indexes)
        self.assertEqual(old.read_bytes(), b'historical receipt must stay unchanged')
        self.assertFalse((self.root / restore.TARGETS[0]).exists())
        self.assertFalse((self.root / restore.TARGETS[2]).exists())


if __name__ == '__main__':
    unittest.main()
