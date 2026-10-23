"""Exact current queue scopes, original coverage, and fresh navigation guards."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge import current_spawn_candidates as model
from rouge import current_battle_reference as battle

ROOT = Path(__file__).resolve().parents[1]


def make_current(stage_id, level):
    """Use the public current projection's exact schema without loading any UI."""
    result = {'id': stage_id, 'level': deepcopy(level), 'actions': []}
    for queue in battle.queues(level):
        scope = {k: deepcopy(v) for k, v in queue.items() if k != 'actions'}
        for index, raw in enumerate(queue['actions']):
            result['actions'].append({'key': str(len(result['actions'])), 'queue': deepcopy(scope),
                'action_index': index + 1, 'source_selector': scope['source_selector'] + f'.actions[{index}]',
                'raw': deepcopy(raw), 'enemy_candidates': [], 'predefined_candidates': []})
    return result


def relation_action(key, *, group=None, package=None, typ='SPAWN'):
    return {'key': key, 'actionType': typ, 'randomSpawnGroupKey': group,
            'randomSpawnGroupPackKey': package, 'count': 1}


class CurrentSpawnCandidates355Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads((ROOT / 'research/p3-current-battle-314/source-inputs.json').read_text(encoding='utf8'))
        cls.topic = json.loads((ROOT / 'research/p3-expansion-313/current-topic.json').read_text(encoding='utf8'))
        cls.inventory = json.loads((ROOT / model.PACK / 'scope-inventory.json').read_text(encoding='utf8'))

    def test_entire_current_scope_184_configurations_113_unique_originals(self):
        stages = self.topic['details']['stages']
        self.assertEqual(len(stages), 184)
        self.assertEqual(len(self.inputs['levels']), 113)
        self.assertEqual(set(stages), set(self.inventory['stages']))
        counts = {'group': 0, 'package': 0, 'group_members': 0, 'package_members': 0,
                  'branch_relations': 0, 'stages_with_relations': 0}
        for sid, stage in stages.items():
            key = 'levels/' + stage['levelId'].lower() + '.json'
            original = self.inputs['levels'][key]
            actual, scopes = model._build(make_current(sid, original), {})
            expected = []
            for kind, field in (('group', 'randomSpawnGroupKey'), ('package', 'randomSpawnGroupPackKey')):
                # Independently enumerate raw wave/fragment and branch/phase scopes.
                queues = []
                for wi, wave in enumerate(original['waves']):
                    for fi, fragment in enumerate(wave['fragments']):
                        queues.append((f'$.waves[{wi}].fragments[{fi}]', fragment.get('actions') or []))
                for branch, value in (original.get('branches') or {}).items():
                    for pi, phase in enumerate(value.get('phases') or []):
                        queues.append(('$.branches[' + json.dumps(branch) + f'].phases[{pi}]', phase.get('actions') or []))
                for selector, actions in queues:
                    keys = list(dict.fromkeys(a[field] for a in actions if type(a.get(field)) is str and a[field]))
                    for group_key in keys:
                        members = [selector + f'.actions[{i}]' for i, a in enumerate(actions) if a.get(field) == group_key]
                        expected.append({'kind': kind, 'queue_selector': selector,
                                         'raw_relation_key': group_key, 'members': members})
            with self.subTest(stage_id=sid):
                projected = [{'kind': kind, 'queue_selector': r['scope_key'],
                              'raw_relation_key': r['raw_relation_key'],
                              'members': [m['source_selector'] for m in r['members']]}
                             for kind in ('group', 'package') for r in actual[kind]]
                self.assertEqual(projected, expected)
                self.assertEqual(projected, self.inventory['stages'][sid]['relations'])
                self.assertEqual(self.inventory['stages'][sid]['complete_stage'], stage)
                self.assertEqual(len(scopes), len(list(battle.queues(original))))
            counts['stages_with_relations'] += bool(actual['group'] or actual['package'])
            for kind in ('group', 'package'):
                counts[kind] += len(actual[kind])
                counts[kind + '_members'] += sum(len(r['members']) for r in actual[kind])
                counts['branch_relations'] += sum(r['queue']['kind'] == 'branch' for r in actual[kind])
        self.assertEqual(counts, {'group': 604, 'package': 393, 'group_members': 2635,
                                 'package_members': 1205, 'branch_relations': 0,
                                 'stages_with_relations': 140})

    def test_same_key_is_not_merged_between_fragments_waves_branches_or_phases(self):
        a = relation_action('enemy', group='shared', package='shared')
        level = {'waves': [{'fragments': [{'actions': [a]}, {'actions': [a]}]},
                           {'fragments': [{'actions': [a]}]}],
                 'branches': {'a': {'phases': [{'actions': [a]}, {'actions': [a]}]},
                              'b': {'phases': [{'actions': [a]}]}}}
        result, scopes = model._build(make_current('synthetic_scope_only', level), {})
        self.assertEqual(len(scopes), 6)
        for rows in result.values():
            self.assertEqual(len(rows), 6)
            self.assertEqual(len({r['key'] for r in rows}), 6)
            self.assertEqual(len({r['scope_key'] for r in rows}), 6)
            self.assertTrue(all(len(r['members']) == 1 for r in rows))
        self.assertTrue(set(r['key'] for r in result['group']).isdisjoint(r['key'] for r in result['package']))

    def test_multiple_members_and_both_relations_keep_empty_and_unnamed_distinct(self):
        level = {'waves': [{'fragments': [{'actions': [
            relation_action('', group='g', package='p', typ='EMPTY'),
            relation_action('', group='g', package='p', typ='ACTIVATE_PREDEFINED'),
            relation_action('enemy', group='g', package='p')]}]}], 'branches': {}}
        result, _ = model._build(make_current('synthetic_distinction_only', level), {})
        for rows in result.values():
            self.assertEqual(len(rows), 1)
            members = rows[0]['members']
            self.assertEqual([m['action_type'] for m in members], ['EMPTY', 'ACTIVATE_PREDEFINED', 'SPAWN'])
            self.assertEqual(members[0]['name'], '空白候选记录')
            self.assertEqual(members[1]['name'], '未指定启用目标')
            self.assertFalse(members[0]['can_request_position'])
            self.assertTrue(members[1]['can_request_position'])
            self.assertEqual([m['action_key'] for m in members], ['0', '1', '2'])

    def test_projection_drift_duplicate_or_extra_actions_rejected(self):
        level = {'waves': [{'fragments': [{'actions': [relation_action('e', group='g')]}]}], 'branches': {}}
        current = make_current('synthetic', level)
        changed = deepcopy(current); changed['actions'][0]['raw']['count'] = False
        with self.assertRaises(ValueError):
            model._build(changed, {})
        duplicate = deepcopy(current); duplicate['actions'].append(deepcopy(duplicate['actions'][0]))
        with self.assertRaises(ValueError):
            model._build(duplicate, {})
        extra = deepcopy(current); extra['actions'].append({**deepcopy(extra['actions'][0]), 'key': '1', 'source_selector': '$.unrelated'})
        with self.assertRaises(ValueError):
            model._build(extra, {})

    def test_nonstring_relation_keys_are_not_converted_or_guessed(self):
        for key in (0, False, [], {}):
            level = {'waves': [{'fragments': [{'actions': [relation_action('e', group=key)]}]}], 'branches': {}}
            with self.subTest(key=key), self.assertRaises(ValueError):
                model._build(make_current('synthetic', level), {})

    def test_current_public_query_and_exact_action_filter(self):
        result = model.stage_reference('ro6_n_1_1')
        self.assertIsNotNone(result)
        self.assertTrue(result['groups'])
        target = result['groups'][0]['members'][0]['action_key']
        restricted = model.stage_reference('ro6_n_1_1', target)
        self.assertTrue(restricted['groups'])
        self.assertTrue(all(any(m['action_key'] == target for m in r['members'])
                            for r in restricted['groups'] + restricted['packages']))
        self.assertIsNone(model.stage_reference('ro6_n_1_1', 'not-an-action'))
        self.assertIsNone(model.stage_reference(True))
        self.assertIsNone(model.stage_reference('ro6_n_1_1', False))
        self.assertIsNone(result['probabilities'])
        self.assertIsNone(result['actual_selection'])
        self.assertIsNone(result['absolute_time'])
        self.assertFalse(result['run_updated'])

    def test_primary_level_or_metadata_drift_fails_closed(self):
        current = battle.stage_reference('ro6_n_1_1')
        for field in ('level', 'stage', 'source'):
            changed = deepcopy(current)
            if field == 'level':
                changed['level']['waves'][0]['fragments'][0]['actions'][0]['count'] = False
            elif field == 'stage':
                changed['stage']['name'] = 'same name is not a source'
            else:
                changed['source']['sha256'] = '0' * 64
            with self.subTest(field=field), patch.object(battle, 'stage_reference', return_value=changed):
                self.assertIsNone(model.stage_reference('ro6_n_1_1'))

    def test_own_manifest_bad_source_fails_closed_without_writing_original_files(self):
        original_file = battle.version._file
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder) / 'manifest.json'; bad.write_bytes(b'{}')
            with patch.object(battle.version, '_file', side_effect=lambda name: bad if name == model.MANIFEST else original_file(name)):
                self.assertIsNone(model._packet())
                self.assertIsNone(model.stage_reference('ro6_n_1_1'))
        self.assertIsNotNone(model._packet())

    def test_resolve_rejects_foreign_relation_action_and_mutated_snapshot(self):
        result = model.stage_reference('ro6_n_1_1')
        relation = result['groups'][0]; member = relation['members'][0]
        with patch.object(model, 'stage_reference', return_value=deepcopy(result)):
            self.assertIsNotNone(model.resolve_member(result, relation['key'], member['action_key']))
            self.assertIsNone(model.resolve_member(result, 'foreign', member['action_key']))
            self.assertIsNone(model.resolve_member(result, relation['key'], 'foreign'))
            changed = deepcopy(result); changed['actual_count'] = 0
            self.assertIsNone(model.resolve_member(changed, relation['key'], member['action_key']))

    def test_position_reference_delegates_to_existing_reader_and_rejects_cross_binding(self):
        from rouge import current_action_positions
        result = model.stage_reference('ro6_n_1_1')
        relation = next(r for r in result['groups'] if any(m['can_request_position'] for m in r['members']))
        member = next(m for m in relation['members'] if m['can_request_position'])
        declared = {'stage_id': result['stage_id'], 'action_key': member['action_key'],
                    'battle_source_identity': result['battle_source_identity'],
                    'action': deepcopy(member['action']), 'entries': [],
                    'notes': ['Position remains unknown, no invented coordinates.']}
        with patch.object(model, 'stage_reference', return_value=deepcopy(result)):
            with patch.object(current_action_positions, 'reference', return_value=declared) as existing:
                self.assertIs(model.position_reference(result, relation['key'], member['action_key']), declared)
                existing.assert_called_once_with(result['stage_id'], member['action_key'])
            for key, value in [('stage_id', 'foreign'), ('action_key', 'foreign'),
                               ('battle_source_identity', 'foreign')]:
                wrong = deepcopy(declared); wrong[key] = value
                with patch.object(current_action_positions, 'reference', return_value=wrong):
                    self.assertIsNone(model.position_reference(result, relation['key'], member['action_key']))

    def test_player_text_keeps_records_not_actual_totals_and_raw_keys_technical(self):
        result = model.stage_reference('ro6_n_1_1')
        for row in result['groups'][:2]:
            for member in row['members']:
                text = model.player_text(result, row, member)
                self.assertIn('不能', text)
                self.assertIn('实际', text)
                self.assertNotIn('$.waves', text)
                self.assertNotIn('randomSpawnGroup', text)
                self.assertIsNone(member['actual_count'])
                self.assertIsNone(member['position_on_original'])


if __name__ == '__main__':
    unittest.main()
