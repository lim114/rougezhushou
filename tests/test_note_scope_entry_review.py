"""Scope identity parsing, using synthetic catalogue entries only."""
import json
import unittest
from copy import deepcopy
from unittest.mock import patch

from rouge import player_note_scopes as scopes
from tests.test_inline_notebook_review import rows


class NoteScopeEntryTests(unittest.TestCase):
    def test_invalid_input_and_stale_identity_are_rejected(self):
        catalogue = rows()
        valid = scopes.scope(catalogue, 'floor1', '普通作战')
        malformed = [
            None, 7, 'not-json', '[]',
            json.dumps(['pinned-public-version', [], None]),
            json.dumps(['pinned-public-version', 'floor1', []]),
            json.dumps(['pinned-public-version', 'floor1', '不存在的节点']),
            json.dumps(['old-version', 'floor1', '普通作战']),
        ]
        for identity in malformed:
            with self.subTest(identity=identity):
                self.assertIsNone(scopes.scope_parts({**valid, 'variant_id': identity}, catalogue))
        missing = dict(valid)
        del missing['variant_id']
        self.assertIsNone(scopes.scope_parts(missing, catalogue))
        self.assertIsNone(scopes.scope_parts({**valid, 'title': '错误标题'}, catalogue))
        self.assertIsNone(scopes.scope_parts(valid, []))

    def test_valid_scope_roundtrip_reads_source_identity_once(self):
        catalogue = rows()
        for floor, node in [(None, None), ('floor1', None), ('floor1', '普通作战')]:
            with self.subTest(floor=floor, node=node):
                content = scopes.scope(catalogue, floor, node)
                with patch.object(scopes.json, 'loads', wraps=json.loads) as decode:
                    self.assertEqual(scopes.scope_parts(content, catalogue), (floor, node))
                self.assertEqual(decode.call_count, 2)  # Incoming identity and catalogue source.

    def test_internal_catalogue_errors_are_not_relabelled_as_bad_input(self):
        catalogue = rows()
        content = scopes.scope(catalogue, 'floor1', '普通作战')
        broken = deepcopy(catalogue)
        del broken[0]['context']
        with self.assertRaises(KeyError):
            scopes.scope_parts(content, broken)
        for error in (ValueError('internal scope error'), TypeError('internal scope error')):
            with self.subTest(error=type(error).__name__):
                with patch.object(scopes, 'scope', side_effect=error):
                    with self.assertRaises(type(error)):
                        scopes.scope_parts(content, catalogue)


if __name__ == '__main__':
    unittest.main()
