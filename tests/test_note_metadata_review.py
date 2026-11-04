"""Metadata entry contracts, using only synthetic local note files."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from rouge.player_note_library import NoteLibrary


class NoteMetadataReviewTests(unittest.TestCase):
    def test_internal_type_error_is_not_reported_as_bad_metadata(self):
        with TemporaryDirectory() as folder:
            library = NoteLibrary(folder)
            library.record({'title': '公开场景', 'kind': 'battle'})
            with patch('rouge.player_notes.content_key', side_effect=TypeError('internal defect')):
                with self.assertRaisesRegex(TypeError, 'internal defect'):
                    library.records()

    def test_corrupt_metadata_does_not_hide_valid_record_or_change_files(self):
        with TemporaryDirectory() as folder:
            library = NoteLibrary(folder)
            content = {'title': '公开场景', 'kind': 'battle'}
            library.record(content)
            broken = Path(folder) / 'broken.meta.json'
            broken.write_bytes(b'{invalid')
            wrong = Path(folder) / 'wrong.meta.json'
            wrong.write_text(json.dumps({'schema': 'player-note-context-v1', 'content': []}), encoding='utf8')
            before = {p.name: p.read_bytes() for p in Path(folder).iterdir()}
            self.assertEqual(library.records(), {'["battle","公开场景"]': {'content': content}})
            self.assertEqual(set(library.issues), {broken.name, wrong.name})
            self.assertEqual(before, {p.name: p.read_bytes() for p in Path(folder).iterdir()})

    def test_identity_fields_survive_metadata_projection(self):
        cases = [
            ({'title': '场景甲', 'extra': 'not persisted'}, '["content","场景甲"]'),
            ({'kind': 'event', 'title': '场景乙', 'event_id': 'event-b'}, '["event","event-b"]'),
            ({'kind': 'battle', 'title': '场景丙', 'variant_id': 'elite-c', 'event_id': 'event-c'}, '["battle","elite-c"]'),
        ]
        with TemporaryDirectory() as folder:
            library = NoteLibrary(folder)
            for content, key in cases:
                with self.subTest(key=key):
                    library.record(content)
                    path = Path(folder) / (sha256(key.encode()).hexdigest() + '.meta.json')
                    saved = json.loads(path.read_text('utf8'))['content']
                    self.assertNotIn('extra', saved)
                    self.assertEqual(library.records()[key]['content'], saved)
                    self.assertEqual(saved['title'], content['title'])
