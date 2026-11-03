"""Public source/identity contract; candidate requires explicit --module-file."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse
import importlib.util
import inspect
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_FILE = ROOT / 'rouge/spawn_candidates.py'

def load(path, suffix='test'):
    name = 'rouge._spawn_candidates_299_' + suffix
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SpawnCandidatesTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None: cls.subject = load(MODULE_FILE)

    def stage(self, sid='ro6_n_2_1'):
        result = self.subject.stage_reference(sid)
        self.assertIsNotNone(result)
        self.assertTrue(result['source_valid'])
        self.assertEqual(result['status'], 'documented_reference')
        return result

    def action(self, sid='ro6_n_2_1', aid='w1.f4.a1'):
        result = self.subject.action_reference(sid, aid)
        self.assertIsNotNone(result)
        self.assertTrue(result['source_valid'])
        return result

    def test_01_all_69_stage_original_group_package_memberships(self):
        total_groups = total_packages = 0
        original_paths = set()
        for sid in self.subject.STAGE_IDS:
            result = self.stage(sid)
            original = json.loads((self.subject.ROOT / result['source_file']).read_bytes())
            original_paths.add(result['source_file'])
            for field, key in (('groups', 'randomSpawnGroupKey'), ('packages', 'randomSpawnGroupPackKey')):
                expected = {}
                for wi, wave in enumerate(original['waves'], 1):
                    for fi, fragment in enumerate(wave['fragments'], 1):
                        for ai, action in enumerate(fragment['actions'], 1):
                            if action.get(key): expected.setdefault((f'w{wi}.f{fi}', action[key]), []).append((f'w{wi}.f{fi}.a{ai}', action))
                actual = {(r['queue_id'], r['group_key'] if field == 'groups' else r['package_key']):
                          [(m['action_id'], m['raw_action']) for m in r['members']] for r in result[field]}
                self.assertEqual(actual, expected, (sid, field))
            total_groups += len(result['groups']); total_packages += len(result['packages'])
        self.assertEqual((len(self.subject.STAGE_IDS), len(original_paths), total_groups, total_packages), (69, 38, 285, 215))

    def test_02_same_g1_key_different_fragments_not_joined(self):
        first = self.action()
        later = self.action(aid='w1.f6.a7')
        self.assertEqual([m['display_name'] for m in first['groups'][0]['members']], ['黑水源石虫', '辐能源石虫'])
        self.assertEqual([m['display_name'] for m in later['groups'][0]['members']], ['黑水源石虫·α', '冰爆源石虫', '高能源石虫'])
        self.assertNotEqual(first['groups'][0]['reference_id'], later['groups'][0]['reference_id'])

    def test_03_same_enemy_different_count_route_delay_preserved(self):
        result = self.action('ro6_n_1_4', 'w1.f3.a2')
        members = result['groups'][0]['members']
        self.assertEqual([m['display_name'] for m in members], ['颂水贤者', '颂水贤者'])
        self.assertEqual([m['declared_count'] for m in members], [3, 4])
        self.assertEqual([m['raw_action']['routeIndex'] for m in members], [17, 18])
        self.assertEqual([m['raw_action']['preDelay'] for m in members], [9.5, 7.0])
        self.assertEqual(len({m['reference_id'] for m in members}), 2)

    def test_04_package_keeps_group_null_companion(self):
        result = self.action('ro6_n_1_4', 'w1.f3.a4')
        self.assertEqual(len(result['packages']), 1)
        members = result['packages'][0]['members']
        self.assertEqual([m['action_id'] for m in members], ['w1.f3.a4', 'w1.f3.a5'])
        self.assertEqual([m['raw_action']['randomSpawnGroupKey'] for m in members], ['big', None])
        self.assertIsNone(result['packages'][0]['actual_selection'])

    def test_05_empty_action_and_empty_activation_are_distinct(self):
        empty = self.action('ro6_n_2_5', 'w1.f2.a5')['groups'][0]['members'][1]
        activation = self.action('ro6_n_1_1', 'w1.f1.a1')['groups'][0]['members'][0]
        self.assertEqual((empty['action_type'], empty['display_name']), ('EMPTY', '空动作（不生成敌人）'))
        self.assertEqual((activation['action_type'], activation['display_name']), ('ACTIVATE_PREDEFINED', '未指定激活目标'))
        self.assertIsNone(empty['predefined_reference'])
        self.assertEqual(activation['predefined_reference']['status'], 'empty_key')
        self.assertIsNone(empty['spawn_reference']); self.assertIsNone(activation['spawn_reference'])

    def test_06_predefined_exact_alias_name_and_position_never_route_index(self):
        result = self.action('ro6_n_1_1', 'w1.f1.a2')
        member = next(m for m in result['groups'][0]['members'] if m['action_id'] == 'w1.f1.a2')
        ref = member['predefined_reference']
        self.assertEqual(member['display_name'], '恶笼草')
        self.assertEqual(ref['status'], 'exact_alias')
        self.assertEqual(ref['alias'], 'trap_321_shnbox#1')
        self.assertEqual(ref['objects'][0]['entity_id'], 'trap_321_shnbox')
        self.assertIsNone(member['spawn_reference'])
        self.assertFalse(ref['position_is_actual'])
        original = json.loads((self.subject.ROOT / result['source_file']).read_bytes())
        obj = next(v for v in original['predefines']['tokenInsts'] if v.get('alias') == ref['alias'])
        self.assertEqual(ref['objects'][0]['raw'], obj)
        self.assertEqual(ref['objects'][0]['display_cell'], {'row': len(original['mapData']['map'])-1-obj['position']['row'], 'col': obj['position']['col']})

    def test_07_member_token_resolves_same_exact_identity(self):
        result = self.action(); relation = result['groups'][0]; member = relation['members'][1]
        token = self.subject.member_token(result['stage_id'], result['origin_action_id'], member['action_id'], relation['reference_id'])
        self.assertEqual(token, member['token'])
        resolved = self.subject.resolve_reference(token)
        self.assertEqual(resolved['member'], member)
        self.assertEqual(resolved['relation']['reference_id'], relation['reference_id'])
        self.assertEqual(resolved['source_identity'], result['source_identity'])
        self.assertEqual(resolved['origin_action_id'], 'w1.f4.a1')

    def test_08_origin_must_belong_to_exact_relation(self):
        result = self.action(); relation = result['groups'][0]
        self.assertIsNone(self.subject.member_token('ro6_n_2_1', 'w1.f4.a2', 'w1.f4.a1', relation['reference_id']))
        token = deepcopy(relation['members'][0]['token']); token['origin_action_id'] = 'w1.f4.a2'
        self.assertIsNone(self.subject.resolve_reference(token))

    def test_09_stage_browse_token_uses_no_origin_and_never_auto_selects(self):
        result = self.stage(); relation = result['groups'][0]; member = relation['members'][0]
        self.assertIsNone(result['origin_action_id']); self.assertIsNone(result['selected_action'])
        self.assertIsNone(member['token']['origin_action_id'])
        self.assertEqual(self.subject.resolve_reference(member['token'])['member'], member)

    def test_10_normal_emergency_and_wrong_queue_token_rejected(self):
        token = self.action()['groups'][0]['members'][0]['token']
        for field, value in [('stage_id', 'ro6_e_2_1'), ('queue_id', 'w1.f6'), ('relation_kind', 'package'), ('scope_key', 'same-name'), ('relation_key', 'g2'), ('member_reference_id', 'wrong')]:
            bad = deepcopy(token); bad[field] = value
            self.assertIsNone(self.subject.resolve_reference(bad), field)
        self.assertNotEqual(self.action()['scope_key'], self.action('ro6_e_2_1', 'w1.f4.a1')['scope_key'])

    def test_11_token_rejects_extra_fields_wrong_types_and_missing_fields(self):
        token = self.action()['groups'][0]['members'][0]['token']
        bad = deepcopy(token); bad['actual_selected'] = True
        self.assertIsNone(self.subject.resolve_reference(bad))
        for field in token:
            bad = deepcopy(token); del bad[field]
            self.assertIsNone(self.subject.resolve_reference(bad), field)
        for bad in (None, [], True, 1, 'token'):
            self.assertIsNone(self.subject.resolve_reference(bad))

    def test_12_branch_and_nonexistent_actions_do_not_borrow_main_groups(self):
        for action in ('branch:g1.p1.a1', 'w99.f1.a1', 'g1', True, None):
            self.assertIsNone(self.subject.action_reference('ro6_n_2_1', action))
        for stage in ('missing', True, None, ''):
            self.assertIsNone(self.subject.stage_reference(stage))

    def test_13_return_values_are_defensive_copies(self):
        result = self.action(); original = deepcopy(result)
        result['groups'][0]['members'][0]['raw_action']['count'] = 999
        result['groups'][0]['members'][0]['token']['source_identity'].clear()
        result['packages'].clear()
        self.assertEqual(self.action(), original)

    def test_14_spawn_reference_is_fixed_unique_level_and_main_action(self):
        member = self.action()['groups'][0]['members'][1]
        self.assertEqual(member['enemy_references'], [{'id': 'enemy_1352_eslime', 'level': 0, 'name': '辐能源石虫', 'level_type': 'NORMAL', 'source_role': 'fixed_stage_enemy_reference'}])
        self.assertEqual(member['spawn_reference'], {'stage_id': 'ro6_n_2_1', 'action_id': 'w1.f4.a8', 'enemy_id': 'enemy_1352_eslime', 'level': 0, 'route_index_reference': 19, 'level_source_sha256': 'd067c73d052167dbe57f78693dc46d8a5e337c7f63f0f68ca1e5b1fd727c7d1b'})

    def test_15_no_actual_probability_or_clock_from_source_membership(self):
        result = self.action()
        self.assertIsNone(result['actual_selection']); self.assertIsNone(result['probabilities'])
        for relation in result['groups'] + result['packages']:
            self.assertIsNone(relation['actual_selection'])
            for member in relation['members']:
                self.assertIsNone(member['actual_selected'])
                self.assertNotIn('absolute_time', member)
                self.assertNotIn('probability', member)
        self.assertIn('不证明', result['notice'])

    def test_16_mutated_warm_legacy_stage_and_source_fail_closed(self):
        actual = deepcopy(self.subject.battle_preview.battle_data())
        bad = deepcopy(actual); bad['stages']['ro6_n_2_1']['enemies'][0]['name'] = '伪造名称'
        with patch.object(self.subject.battle_preview, 'battle_data', return_value=bad):
            result = self.subject.stage_reference('ro6_n_2_1')
            self.assertFalse(result['source_valid']); self.assertEqual(result['groups'], [])
        bad = deepcopy(actual); bad['source']['game_commit'] = 'unbound'
        with patch.object(self.subject.battle_preview, 'battle_data', return_value=bad):
            self.assertFalse(self.subject.stage_reference('ro6_n_2_1')['source_valid'])
        self.assertTrue(self.stage()['source_valid'])

    def test_17_strict_stage_object_types_reject_bool_for_numeric(self):
        actual = deepcopy(self.subject.battle_preview.battle_data())
        actual['stages']['ro6_n_2_1']['waves'][0]['index'] = True
        with patch.object(self.subject.battle_preview, 'battle_data', return_value=actual):
            self.assertFalse(self.subject.stage_reference('ro6_n_2_1')['source_valid'])

    def test_18_full_valid_clone_then_each_used_source_tamper_and_missing(self):
        base = self.subject.ROOT
        manifest = json.loads((base / self.subject.MANIFEST).read_bytes())
        with tempfile.TemporaryDirectory(prefix='rouge299-public-source-') as temporary:
            cloned_root = Path(temporary)
            for name in [self.subject.MANIFEST, *manifest['files']]:
                target = cloned_root / name; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(base / name, target)
            with patch.object(self.subject, 'ROOT', cloned_root):
                original = self.stage(); token = original['groups'][0]['members'][0]['token']
                used = [self.subject.MANIFEST, *manifest['global_files'], manifest['stage_files']['ro6_n_2_1']]
                for name in used:
                    path = cloned_root / name; raw = path.read_bytes()
                    for mode in ('one_byte', 'missing'):
                        if mode == 'one_byte': path.write_bytes(raw + b' ')
                        else: path.unlink()
                        broken = self.subject.stage_reference('ro6_n_2_1')
                        self.assertFalse(broken['source_valid'], (name, mode))
                        self.assertEqual(broken['status'], 'source_unavailable')
                        self.assertEqual((broken['groups'], broken['packages']), ([], []))
                        for key in ('selected_action', 'scope_key', 'source_identity', 'source', 'source_file'):
                            self.assertIsNone(broken[key])
                        self.assertIsNone(self.subject.resolve_reference(token))
                        path.write_bytes(raw)
                        self.assertTrue(self.stage()['source_valid'], (name, mode, 'restore'))

    def test_19_public_api_has_no_source_or_value_injection(self):
        self.assertEqual(tuple(inspect.signature(self.subject.stage_reference).parameters), ('stage_id',))
        self.assertEqual(tuple(inspect.signature(self.subject.action_reference).parameters), ('stage_id', 'action_id'))
        self.assertEqual(tuple(inspect.signature(self.subject.resolve_reference).parameters), ('token',))
        with self.assertRaises(TypeError): self.subject.stage_reference('ro6_n_2_1', data={})
        with self.assertRaises(TypeError): self.subject.resolve_reference({}, source={})

    def test_20_bound_source_packet_and_literal_data_pins_are_real(self):
        raw = (self.subject.ROOT / self.subject.MANIFEST).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), self.subject.MANIFEST_SHA256)
        manifest = json.loads(raw)
        self.assertEqual(sha256((self.subject.ROOT / self.subject.DATA).read_bytes()).hexdigest(), self.subject.DATA_SHA256)
        self.assertEqual(len(set(manifest['stage_files'].values())), 38)
        self.assertFalse(manifest['runtime_reads_primary_character_table'])

    def test_21_default_builder_is_read_only_and_reproduces_complete_scope(self):
        builder = self.subject.ROOT / 'scripts/build_spawn_candidates_299.py'
        if not builder.is_file(): self.fail('Fixed public builder missing')
        manifest = json.loads((self.subject.ROOT / self.subject.MANIFEST).read_bytes())
        files = [self.subject.ROOT / name for name in [self.subject.MANIFEST, *manifest['files']]] + [builder, Path(self.subject.__file__)]
        before = {str(p): sha256(p.read_bytes()).hexdigest() for p in files}
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(builder)], cwd=self.subject.ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf8', errors='replace'))
        receipt = json.loads(result.stdout)
        self.assertFalse(receipt['write']); self.assertTrue(receipt['existing_outputs_match'])
        self.assertEqual(receipt['counts'], {'stages': 69, 'original_levels': 38, 'groups': 285, 'packages': 215})
        self.assertEqual(before, {str(p): sha256(p.read_bytes()).hexdigest() for p in files})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--module-file', type=Path)
    args, other = parser.parse_known_args()
    if args.module_file is not None: SpawnCandidatesTests.subject = load(args.module_file.resolve(), 'explicit')
    unittest.main(argv=[sys.argv[0], *other])
