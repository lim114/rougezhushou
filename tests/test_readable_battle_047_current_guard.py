"""Current presentation source guard; historical pre047 check stays unavailable.

The reference bodies are exact public Git originals.  No current calculation
output or current source body is stored as a historical expected result.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT
ARCHIVE = ROOT / 'research/presentation-source-guard'
GUARDS = {
    'rouge/battle_preview.py': {'battle_data', 'display_cell', 'route_reference',
        'hidden_group_reference', 'spawn_rows', 'enemy_preview', 'value_text'},
    'rouge/enemy_skills.py': {'skill_data', 'enemy_skill_reference', 'raw_text',
        'blackboard_text', 'definition_text'},
    'rouge/spawn_reference.py': {'finite_nonnegative', 'local_sequence',
        'ordinal_offset', 'movement_reference'},
}
CHANGED = {
    ('rouge/battle_preview.py', 'enemy_preview'),
    ('rouge/enemy_skills.py', 'enemy_skill_reference'),
    ('rouge/spawn_reference.py', 'movement_reference'),
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def nodes(path):
    return {node.name: ast.dump(node, include_attributes=False)
        for node in ast.parse(path.read_text(encoding='utf-8')).body
        if isinstance(node, ast.FunctionDef)}


class CurrentPresentationSourceGuard047Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ARCHIVE / 'source-manifest.json').read_text(encoding='utf-8'))

    def test_exact_guard_membership_and_historical_scope_are_preserved(self):
        rows = self.manifest['functions']
        expected = {(source, name) for source, names in GUARDS.items() for name in names}
        actual = {(row['source_path'], row['function']) for row in rows}
        self.assertEqual(actual, expected)
        self.assertEqual(len(rows), 16)
        self.assertEqual({(row['source_path'], row['function']) for row in rows
            if row['scope'] == 'APPROVED_SOURCE_CHANGE'}, CHANGED)
        self.assertFalse(self.manifest['historical_047_validation_closed'])
        self.assertFalse(self.manifest['current_output_golden_generated'])

    def test_six_archived_originals_keep_verified_public_bytes(self):
        sources = self.manifest['source_files']
        self.assertEqual(len(sources), 6)
        sealed047 = json.loads((PROJECT_ROOT / 'FINAL_0.47_VERIFICATION.json').read_text(encoding='utf-8'))
        for source in sources:
            with self.subTest(source=source['archive_path']):
                raw = (ARCHIVE / source['archive_path']).read_bytes()
                self.assertEqual(digest(raw), source['sha256'])
                self.assertEqual(len(raw), source['bytes'])
                self.assertTrue(source['never_pre047_backup'])
                if source['historical_phase'] == 'POST_0.47_EXACT_PUBLIC_BYTES':
                    self.assertEqual(source['sha256'], sealed047['source_sha256'][source['source_path']])
                    self.assertEqual(source['git_commit'], '30f631f10fdc103820a25109f4d259b74ddf6ece')
                else:
                    receipt = (PROJECT_ROOT / source['section_receipt']).read_bytes()
                    self.assertEqual(digest(receipt), source['section_receipt_sha256'])

    def test_thirteen_unchanged_functions_keep_real_post047_ast(self):
        rows = [r for r in self.manifest['functions'] if r['scope'] == 'UNCHANGED_POST047_AST']
        self.assertEqual(len(rows), 13)
        for row in rows:
            with self.subTest(source=row['source_path'], function=row['function']):
                before = nodes(ARCHIVE / row['archive_path'])[row['function']]
                after = nodes(PROJECT_ROOT / row['source_path'])[row['function']]
                self.assertEqual(digest(before.encode()), row['target_ast_sha256'])
                self.assertEqual(before, after)
                self.assertEqual(row['approved_change_history'], [])

    def test_three_documented_extensions_keep_approved_section_ast(self):
        rows = [r for r in self.manifest['functions'] if r['scope'] == 'APPROVED_SOURCE_CHANGE']
        self.assertEqual(len(rows), 3)
        archived = {r['archive_path']: r for r in self.manifest['source_files']}
        for row in rows:
            with self.subTest(source=row['source_path'], function=row['function']):
                self.assertTrue(row['approved_change_history'])
                self.assertEqual(row['approved_change_history'][-1]['commit'],
                    archived[row['archive_path']]['git_commit'])
                for change in row['approved_change_history']:
                    raw = (PROJECT_ROOT / change['section_receipt']).read_bytes()
                    self.assertEqual(digest(raw), change['section_receipt_sha256'])
                approved = nodes(ARCHIVE / row['archive_path'])[row['function']]
                current = nodes(PROJECT_ROOT / row['source_path'])[row['function']]
                self.assertEqual(digest(approved.encode()), row['target_ast_sha256'])
                self.assertEqual(approved, current)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, default=ROOT)
    options, remaining = parser.parse_known_args()
    PROJECT_ROOT = options.project_root.resolve()
    unittest.main(argv=[__file__, *remaining])
