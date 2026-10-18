"""Source-bound documentary boss forms; no game, Qt, private state or prediction."""
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

from rouge import boss_phase_reference as model, battle_preview, enemy_skills

ROOT = Path(__file__).resolve().parents[1]
PHASE_IDS = ['first', 'calamity_1', 'second', 'calamity_2', 'third', 'flying']
PHASE_NAMES = ['第一形态', '灾厄形态(一)', '第二形态', '灾厄形态(二)', '第三形态', '飞行形态']
MODE_LABELS = [['灾厄形态(一)', '灾厄形态(二)'], ['第二形态', '第三形态'],
               ['第三形态'], ['第三形态'], ['飞行形态'], ['飞行形态']]


class BossPhase309Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.battle = json.loads((ROOT / 'rouge/data/battle-previews.json').read_bytes())
        cls.skills = json.loads((ROOT / 'rouge/data/enemy-skill-references.json').read_bytes())
        cls.original_player = json.loads((ROOT / model.PLAYER).read_bytes())
        cls.selected = json.loads((ROOT / model.SELECTED).read_bytes())

    def setUp(self):
        self.addCleanup(battle_preview.battle_data.cache_clear)
        self.addCleanup(enemy_skills.skill_data.cache_clear)

    def result(self):
        return model.phase_reference('ro6_b_6', 'enemy_2150_shchmr', 0)

    def assertUnknown(self, result):
        for key in model.ACTUAL_FIELDS:
            self.assertIsNone(result[key], key)
        for key in ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated',
                    'inventory_updated', 'modifiers_changed', 'maps_changed'):
            self.assertIs(result[key], False, key)

    def clone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name)
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        for name in [model.MANIFEST, *manifest['runtime_files']]:
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return target, manifest

    def test01_exact_identity_and_actual_fields_are_unknown(self):
        result = self.result()
        self.assertEqual(model.TARGET, ('ro6_b_6', 'enemy_2150_shchmr', 0))
        self.assertIs(result['source_valid'], True)
        self.assertEqual(result['status'], 'documented_reference')
        self.assertEqual(result['reference']['boss_name'], '玻利瓦尔，症结之核')
        self.assertEqual({key: result['reference'][key] for key in ('stage_id', 'enemy_id', 'level')},
                         {'stage_id': 'ro6_b_6', 'enemy_id': 'enemy_2150_shchmr', 'level': 0})
        self.assertUnknown(result)

    def test02_non_targets_and_bool_float_levels_do_not_read_sources(self):
        with patch.object(model, '_packet', side_effect=AssertionError('no new source I/O')):
            for sid, eid, level in [(None, None, None), ([], {}, 0), ('ro6_b_6', 'enemy_2150_shchmr', False),
                    ('ro6_b_6', 'enemy_2150_shchmr', 0.0), ('ro6_b_6', 'enemy_2150_shchmr', 1),
                    ('ro6_b_5', 'enemy_2150_shchmr', 0), ('ro6_b_6', 'enemy_2150_shchmr_b', 0)]:
                self.assertIsNone(model.phase_reference(sid, eid, level))

    def test03_complete_selected_original_records_and_source_objects_are_retained(self):
        data = model._packet()
        self.assertEqual(data['selected_originals'], self.selected)
        self.assertEqual(self.selected['canonical_stage_complete'], self.battle['stages']['ro6_b_6'])
        self.assertEqual(self.selected['current_skill_definition_complete'], self.skills['definitions']['enemy_2150_shchmr'])
        self.assertEqual(self.selected['current_skill_binding_complete'], self.skills['bindings']['ro6_b_6']['enemy_2150_shchmr@0'])

    def test04_six_documentary_entries_do_not_become_six_blood_bars(self):
        result = self.result()
        phases = result['reference']['phases']
        self.assertEqual([row['id'] for row in phases], PHASE_IDS)
        self.assertEqual([row['phase_id'] for row in phases], PHASE_IDS)
        self.assertEqual([row['name'] for row in phases], PHASE_NAMES)
        self.assertEqual(phases[-1]['kind'], 'third_form_flight_subform')
        self.assertIn('血条数', result['reference']['scope_notice'])
        self.assertIsNone(result['phase_stats'])

    def test05_complete_headers_correct_old_empty_mode_extraction(self):
        skills = self.result()['reference']['skills']
        self.assertEqual([row['documented_modes'] for row in skills], MODE_LABELS)
        for old, current in zip(self.original_player['skills'], skills):
            self.assertEqual(current['original_documented_modes'], old['documented_modes'])
            self.assertEqual(current['complete_DOM'], old['complete_DOM'])
            self.assertEqual(current['effect_text'], old['effect_text'])

    def test06_first_form_empty_labelled_cards_does_not_mean_no_skills(self):
        result = self.result()
        self.assertEqual(result['reference']['phases'][0]['skill_ids'], [])
        text = model.reference_text(result, 'first')
        self.assertIn('未在这个条目下另列专属招式', text)
        self.assertIn('普通攻击', text)
        self.assertNotIn('第一形态没有技能', text)

    def test07_all_seven_transitions_and_return_edges_preserved(self):
        transitions = self.result()['reference']['transitions']
        self.assertEqual([(row['from_phase_id'], row['to_phase_id']) for row in transitions],
            [('first', 'calamity_1'), ('calamity_1', 'second'), ('second', 'calamity_2'),
             ('calamity_2', 'third'), ('third', 'calamity_2'), ('third', 'flying'), ('flying', 'third')])
        for row in transitions:
            self.assertIsNone(row['actual_transition'])
        self.assertIn('不经过重生', transitions[4]['text'])
        self.assertIn('不是再次被击倒', transitions[4]['text'])

    def test08_main_target_retreat_is_interruption_not_automatic_next_form(self):
        result = self.result()
        mouth = next(row for row in result['reference']['skills'] if row['skill_id'] == 'calamity_mouth')
        self.assertIn('若主目标已退场，打断此技能', mouth['effect_text'])
        self.assertIn('若技能未被打断', mouth['effect_text'])
        text = model.reference_text(result, 'calamity_1')
        self.assertIn('不能把每次中断当成进入下一形态', text)
        self.assertUnknown(result)

    def test09_selected_form_only_lists_its_own_skill_cards(self):
        result = self.result()
        text = model.reference_text(result, 'flying')
        self.assertIn('未熄之地(飞行)', text)
        self.assertIn('降落（飞行形态）', text)
        self.assertNotIn('再次释放（第三形态）', text)
        for phrase in ('对应的【未熄之地】效果（文献交叉说明）', '燃烧区域', '持续25秒',
                       '每秒检测一次', '地面阻挡', '不叠加', '存疑'):
            self.assertIn(phrase, text)
        text = model.reference_text(result, 'second')
        self.assertIn('未熄之地（第二形态、第三形态）', text)
        self.assertNotIn('起飞（第三形态）', text)

    def test10_cycle_retention_is_labelled_document_explanatory_note(self):
        ref = self.result()['reference']
        notes = ref['common_documented_context']['reading_notes']
        self.assertTrue(any(row.startswith('文献说明注：') and '未用完的延长灾厄' in row for row in notes))
        review = json.loads((ROOT / model.REVIEW).read_bytes())
        self.assertIn('均不会经过重生', review['additional_document_tooltip_notes'][0]['text'])

    def test11_source_differences_not_rewritten_as_numeric_conflicts(self):
        result = self.result()
        differences = result['reference']['source_differences']
        self.assertEqual(differences, self.original_player['source_differences'])
        self.assertEqual(differences[0]['fixed_fields']['reborn_2.max_hp'], 1.0)
        self.assertEqual(differences[1]['fixed_fields'], {'Fire.duration_extend': 10.0, 'Fire.cooldown': 1.0})
        self.assertIn('不能认定两份来源互斥', differences[0]['reading_notice'])
        self.assertIn('不能擅自以10+1解释', differences[1]['reading_notice'])
        self.assertUnknown(result)

    def test12_plain_player_reading_keeps_conditions_without_engine_ids(self):
        text = model.reference_text(self.result())
        for word in ('进入、离开和返回', '共同能力', '不能直接对算', '仍未确认', '存疑', '优先选择', '其次为自身'):
            self.assertIn(word, text)
        for word in ('enemy_2150', 'ro6_b_6', 'reborn_2', 'Fireball', 'Fire.', 'complete_DOM', '我方干员 > 自身', 'dot'):
            self.assertNotIn(word, text)

    def test13_technical_objects_keep_full_documents_and_fixed_identifiers(self):
        ref = self.result()['reference']
        self.assertEqual(ref['source_docs'], self.original_player['source_docs'])
        self.assertEqual(ref['common_documented_context']['complete_DOM'], self.original_player['common_documented_context']['complete_DOM'])
        self.assertEqual(ref['identity'], {'stage_id': 'ro6_b_6', 'enemy_id': 'enemy_2150_shchmr', 'level': 0})
        self.assertEqual([row['revision'] for row in ref['source_docs']], ['435612', '420841'])

    def test14_nested_return_values_are_defensive_and_not_a_mutable_source_cache(self):
        first = self.result()
        first['reference']['phases'][0]['name'] = '污染'
        first['reference']['skills'][0]['complete_DOM']['children'].clear()
        first['source_identity'].clear()
        second = self.result()
        self.assertEqual(second['reference']['phases'][0]['name'], '第一形态')
        self.assertTrue(second['reference']['skills'][0]['complete_DOM']['children'])
        self.assertEqual(second['source_identity']['data_sha256'], model.DATA_SHA256)

    def test15_each_runtime_member_byte_change_delete_and_recovery_is_fresh(self):
        root, manifest = self.clone()
        with patch.object(model, 'ROOT', root):
            self.assertTrue(self.result()['source_valid'])
            for name in manifest['runtime_files']:
                path = root / name
                old = path.read_bytes()
                for mode in ('tamper', 'delete'):
                    try:
                        if mode == 'tamper':
                            path.write_bytes(old + b' ')
                        else:
                            path.unlink()
                        result = self.result()
                        self.assertFalse(result['source_valid'], (name, mode))
                        self.assertIsNone(result['reference'])
                        self.assertIsNone(result['source_identity'])
                        self.assertUnknown(result)
                    finally:
                        path.write_bytes(old)
                    self.assertTrue(self.result()['source_valid'], (name, mode))

    def test16_manifest_is_fresh_and_cannot_authorize_changed_data(self):
        root, _ = self.clone()
        with patch.object(model, 'ROOT', root):
            self.assertTrue(self.result()['source_valid'])
            data = root / model.DATA
            raw = data.read_bytes()
            data.write_bytes(raw + b' ')
            manifest = json.loads((root / model.MANIFEST).read_bytes())
            manifest['data_sha256'] = sha256(data.read_bytes()).hexdigest()
            manifest['runtime_files'][model.DATA] = {'sha256': manifest['data_sha256'], 'bytes': data.stat().st_size}
            (root / model.MANIFEST).write_text(json.dumps(manifest), encoding='utf8')
            result = self.result()
            self.assertFalse(result['source_valid'])
            self.assertIsNone(result['reference'])

    def test17_entire_current_stage_cache_is_compared_not_only_enemy_fields(self):
        battle = deepcopy(self.battle)
        battle['stages']['ro6_b_6']['map'][0][0] = '污染'
        with patch.object(battle_preview, 'battle_data', return_value=battle):
            self.assertFalse(self.result()['source_valid'])

    def test18_current_enemy_level_boolean_and_complete_enemy_pollution_are_rejected(self):
        for field, value in (('level', False), ('description', '污染')):
            battle = deepcopy(self.battle)
            enemy = next(row for row in battle['stages']['ro6_b_6']['enemies'] if row['id'] == 'enemy_2150_shchmr')
            enemy[field] = value
            with patch.object(battle_preview, 'battle_data', return_value=battle):
                self.assertFalse(self.result()['source_valid'])

    def test19_complete_skill_definition_and_binding_cache_pollution_is_rejected(self):
        for field in ('definition', 'binding'):
            table = deepcopy(self.skills)
            if field == 'definition':
                table['definitions']['enemy_2150_shchmr']['0']['extra_unbound'] = True
            else:
                table['bindings']['ro6_b_6']['enemy_2150_shchmr@0']['stage_overrides'] = ['污染']
            with patch.object(enemy_skills, 'skill_data', return_value=table):
                self.assertFalse(self.result()['source_valid'])

    def test20_source_identity_pollution_is_rejected_but_unrelated_stage_is_not_target(self):
        battle = deepcopy(self.battle)
        battle['source']['unexpected'] = True
        with patch.object(battle_preview, 'battle_data', return_value=battle):
            self.assertFalse(self.result()['source_valid'])
        battle = deepcopy(self.battle)
        battle['stages']['ro6_t_1']['name'] = '与本目标无关'
        with patch.object(battle_preview, 'battle_data', return_value=battle):
            self.assertTrue(self.result()['source_valid'])

    def test21_no_combat_prediction_or_state_mutation_called(self):
        before = deepcopy(battle_preview.battle_data())
        with patch.object(battle_preview, 'enemy_preview', side_effect=AssertionError('not a numerical query')):
            result = self.result()
            self.assertTrue(result['source_valid'])
            self.assertUnknown(result)
        self.assertEqual(battle_preview.battle_data(), before)

    def test22_unknown_phase_does_not_silently_select_or_show_another_phase(self):
        result = self.result()
        for value in (False, 0, [], 'unknown', ''):
            text = model.reference_text(result, value)
            self.assertIn('所选形态资料暂时无法核对', text)
            self.assertNotIn('灾厄之口', text)

    def test23_source_unavailable_text_does_not_keep_old_result(self):
        with patch.object(model, '_packet', return_value=None):
            result = self.result()
        self.assertIsNone(result['reference'])
        text = model.reference_text(result, 'third')
        self.assertIn('旧说明与形态选择已清除', text)
        self.assertNotIn('灾厄之口', text)
        self.assertEqual(model.reference_text(None), '')

    def test24_public_path_and_runtime_vs_build_source_boundaries(self):
        for name in ('../private.json', 'C:/private.json', '/private.json', 'research\\file.json', 1):
            with self.assertRaises(ValueError):
                model._file(name)
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        self.assertIs(manifest['runtime_full_database_hashing'], False)
        self.assertEqual(set(manifest['runtime_files']), model.RUNTIME_FILES)
        self.assertFalse(any('enemy_database.json' in name or 'battle-previews.json' in name for name in manifest['runtime_files']))
        self.assertTrue(any('enemy_database.json' in name for name in manifest['build_authority_files']))

    def test25_builder_reproduces_all_generated_bytes_from_complete_fixed_sources(self):
        database = ROOT / '.cache/game-data/levels/enemydata/enemy_database.json'
        if not database.is_file():
            self.skipTest('完整固定原敌人数据库未提供；不可将未执行的重建核验计为通过。')
        source = ROOT / 'scripts/build_boss_phase_reference_309.py'
        spec = spec_from_file_location('boss309_documentary_builder', source)
        builder = module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            receipt = builder.build(ROOT, temporary)
            self.assertEqual(receipt['kind'], 'SECTION309_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE')
            for name in receipt['outputs']:
                self.assertEqual((temporary / name).read_bytes(), (ROOT / name).read_bytes(), name)


if __name__ == '__main__':
    unittest.main()
