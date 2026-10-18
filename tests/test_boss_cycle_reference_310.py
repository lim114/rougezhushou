"""Two-entry documentary condition flow; no Qt/game/chat or actual combat state."""
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

from rouge import boss_cycle_reference as model, battle_preview, enemy_skills

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (('ro6_b_5', 'enemy_2147_shophm', 0), ('ro6_b_5', 'enemy_2148_shorbb', 0))


class BossCycle310Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.battle = json.loads((ROOT / 'rouge/data/battle-previews.json').read_bytes())
        cls.skills = json.loads((ROOT / 'rouge/data/enemy-skill-references.json').read_bytes())
        cls.selected = json.loads((ROOT / model.SELECTED).read_bytes())

    def setUp(self):
        self.addCleanup(battle_preview.battle_data.cache_clear)
        self.addCleanup(enemy_skills.skill_data.cache_clear)

    def result(self, index=0):
        return model.cycle_reference(*TARGETS[index])

    def assertUnknown(self, result):
        for key in model.ACTUAL_FIELDS:
            self.assertIsNone(result[key], key)
        for key in ('current_server_verified', 'numerical_phase_model_added', 'run_state_updated',
                    'inventory_updated', 'modifiers_changed', 'maps_changed'):
            self.assertIs(result[key], False, key)

    def clone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        for name in [model.MANIFEST, *manifest['runtime_files']]:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return root, manifest

    def test01_exact_two_entries_keep_distinct_actor_identity(self):
        self.assertEqual(model.TARGETS, TARGETS)
        for index, (_, enemy, _) in enumerate(TARGETS):
            result = self.result(index)
            self.assertEqual(result['status'], 'documented_reference')
            self.assertIs(result['source_valid'], True)
            self.assertEqual(result['reference']['enemy_id'], enemy)
            self.assertEqual(result['reference']['entry_name'], ['洛伦茨，扰动之谬', '源阶方'][index])
            self.assertUnknown(result)

    def test02_related_enemy_and_device_never_become_new_entry_or_read_sources(self):
        with patch.object(model, '_packet', side_effect=AssertionError('no new source I/O')):
            for sid, enemy, level in [(None, None, None), ([], {}, 0),
                    ('ro6_b_5', 'enemy_2147_shophm', False), ('ro6_b_5', 'enemy_2148_shorbb', 0.0),
                    ('ro6_b_5', 'enemy_2147_shophm', 1), ('ro6_b_6', 'enemy_2147_shophm', 0),
                    ('ro6_b_5', 'enemy_2149_shorsm', 0), ('ro6_b_5', 'trap_324_shmbmb', 0)]:
                self.assertIsNone(model.cycle_reference(sid, enemy, level))

    def test03_both_entries_share_four_topics_not_an_inferred_phase_count(self):
        one, two = self.result(), self.result(1)
        for result in (one, two):
            self.assertEqual([row['id'] for row in result['reference']['topics']], ['flow', 'lorentz', 'cube', 'module'])
            self.assertIsNone(result['phase_stats'])
            self.assertUnknown(result)
        self.assertEqual(one['reference']['topics'], two['reference']['topics'])
        self.assertEqual(one['source_identity'], two['source_identity'])

    def test04_seven_flow_records_are_grouped_by_independent_conditions(self):
        ref = self.result()['reference']
        self.assertIs(ref['not_a_linear_timeline'], True)
        self.assertEqual(len(ref['documentary_flow']), 7)
        self.assertEqual([group['id'] for group in ref['flow_groups']],
                         ['alternating_conditions', 'first_half_hp_change', 'endpoint_and_exit', 'module_outcomes'])
        self.assertEqual(ref['flow_groups'][0]['step_ids'],
                         ['lorentz_knockdown', 'cube_activate', 'module_clear_gate', 'cube_deactivate'])
        text = model.reference_text(self.result(), 'flow')
        for phrase in ('不表示这些事情会依次发生', '主交替条件链', '首次半血的独立变化',
                       '终点、被摧毁与退场分支', '模块存活完成与致命伤害分支'):
            self.assertIn(phrase, text)

    def test05_lorentz_rebirth_start_end_and_cube_skill_end_stay_separate(self):
        text = model.reference_text(self.result(), 'flow')
        for phrase in ('重生开始时', '重生结束时', '不等于源阶方的“激活”技能已经结束',
                       '自己的“激活中止”技能结束时', '不要将这一步与洛伦茨返回合并成同时发生'):
            self.assertIn(phrase, text)

    def test06_no_module_gate_belongs_to_lorentz_not_the_cube(self):
        ref = self.result()['reference']
        gate = next(row for row in ref['documentary_flow'] if row['step_id'] == 'module_clear_gate')
        self.assertEqual(gate['condition_actor'], '洛伦茨，扰动之谬')
        text = model.reference_text(self.result(), 'flow')
        for phrase in ('检查“场上是否还有模块”的是预退场模式的洛伦茨', '5秒后', '每0.2秒'):
            self.assertIn(phrase, text)
        self.assertIsNone(self.result()['actual_modules'])

    def test07_first_half_hp_is_historical_condition_not_current_hp_reconstruction(self):
        result = self.result()
        text = model.reference_text(result, 'flow')
        for phrase in ('首次低于半血', '文献8秒改为4秒', '不能只看当前血量重新判断', '另一批关卡预设路径'):
            self.assertIn(phrase, text)
        self.assertIsNone(result['actual_half_hp_gate'])
        self.assertIsNone(result['actual_elapsed_time'])

    def test08_endpoint_loss_does_not_claim_every_run_fails(self):
        text = model.reference_text(self.result(), 'flow')
        for phrase in ('扣除30点目标生命', '扣30点不代表所有对局必败', '实际剩余目标生命', '持续时间无限'):
            self.assertIn(phrase, text)

    def test09_generic_cube_exit_not_limited_to_destroyed_skill_branch(self):
        text = model.reference_text(self.result(), 'flow')
        for phrase in ('另一个通用条款', '源阶方退场时', '跳过重生', '不能将后一个条款限定为只有“被摧毁”会触发'):
            self.assertIn(phrase, text)

    def test10_seven_boss_skills_two_ability_cards_and_device_skill_table_are_distinct(self):
        ref = self.result()['reference']
        cards = ref['reviewed_complete_documentation']['cards']
        self.assertEqual(sum(row['kind'] == 'skill' for row in cards), 7)
        self.assertEqual(sum(row['kind'] == 'ability' for row in cards), 2)
        self.assertEqual(len(ref['skills']), 7)
        self.assertEqual(len(ref['reviewed_complete_documentation']['module']['skill_tables']), 1)
        self.assertNotIn('trap_324_shmbmb', [row['id'] for row in self.selected['complete_original_level']['enemyDbRefs']])
        self.assertIn('trap_324_shmbmb', json.dumps(self.selected['complete_original_level']['predefines']))

    def test11_unlabelled_modes_are_not_forced_into_initial_or_action_mode(self):
        ref = self.result()['reference']
        for name in ('象限封锁', '被摧毁'):
            skill = next(row for row in ref['skills'] if row['name'] == name)
            self.assertEqual(skill['documented_modes'], [])
            self.assertEqual(skill['mode_label'], '文献未限定模式')
        self.assertIn('不能擅自绑定初始模式', model.reference_text(self.result(), 'lorentz'))

    def test12_selected_actor_page_expands_complete_skill_effects_directly(self):
        text = model.reference_text(self.result(), 'cube')
        for phrase in ('【召唤敌人】', '【激活】', '【失链裂变】', '【召唤源阶粒素】', '【激活中止】',
                       '【被摧毁】', '仅自身未持有裂变冷却时可触发', '触发技能不需要目标', '技能持续5秒'):
            self.assertIn(phrase, text)
        text = model.reference_text(self.result(), 'lorentz')
        self.assertIn('【象限封锁】', text)
        self.assertIn('随机选择攻击范围内的3个', text)
        raw_effect = next(skill['text'] for skill in self.result()['reference']['skills'] if skill['name'] == '象限封锁')
        self.assertEqual(text.count(raw_effect), 1)
        self.assertIn('见下方各招式', model.reference_text(self.result(), 'cube'))
        result = self.result()
        for topic in (None, 'flow', 'lorentz', 'cube', 'module'):
            player = model.reference_text(result, topic)
            for phrase in ('关卡结束脚本', '基准字段', '预计算'):
                self.assertNotIn(phrase, player)
        technical = json.dumps(result['reference'], ensure_ascii=False)
        for phrase in ('关卡结束脚本', '基准字段', '预计算'):
            self.assertIn(phrase, technical)

    def test13_zero_document_baselines_do_not_become_current_zero_damage_or_guessed_multiplier(self):
        result = self.result()
        text = model.reference_text(result, 'cube')
        original_cube = next(topic for topic in result['reference']['topics'] if topic['id'] == 'cube')
        self.assertIn('以基准字段0记载', '\n'.join(original_cube['paragraphs']))
        self.assertIn('固定文献将源阶方行动模式的攻击增益与污染伤害默认值记为0', text)
        self.assertIn('不能据此得到本局加成或污染数值', text)
        self.assertIn('不能自行补难度倍率', text)
        self.assertNotIn('每秒受到0', text)
        self.assertIsNone(result['actual_damage'])

    def test14_module_is_read_as_device_not_enemy_or_base_stat_prediction(self):
        text = model.reference_text(self.result(), 'module')
        for phrase in ('关卡装置', '不是敌人列表中的敌人', '可以被我方治疗', '不把表中基础面板当成本局面板'):
            self.assertIn(phrase, text)
        for value in ('7500', '1650'):
            self.assertNotIn(value, text)
        technical = self.result()['reference']['reviewed_complete_documentation']['module']['complete_visible_table']
        self.assertIn('7500', technical)
        self.assertIn('1650', technical)

    def test15_module_success_and_lethal_damage_branches_are_not_added_together(self):
        result = self.result()
        text = model.reference_text(result, 'module')
        for phrase in ('全域信息失真', '最大生命值8%', '攻击力的20%', '延迟0.8秒',
                       '攻击力的100%', '不要把成功完成技能后的强制击杀直接等同受到致命伤害',
                       '不能把技力消耗当固定秒数'):
            self.assertIn(phrase, text)
        self.assertUnknown(result)

    def test16_module_instant_sp_adjustment_is_not_all_sp_recovery(self):
        text = model.reference_text(self.result(), 'module')
        for phrase in ('即时技力增加或减少会被取消', '自然回复速度', '仍可生效', '任何技力增益均无效'):
            self.assertIn(phrase, text)

    def test17_returned_whole_nested_records_are_defensive(self):
        first = self.result()
        first['reference']['topics'][0]['paragraphs'].clear()
        first['reference']['skills'][0]['text'] = '污染'
        first['source_identity'].clear()
        second = self.result()
        self.assertTrue(second['reference']['topics'][0]['paragraphs'])
        self.assertNotEqual(second['reference']['skills'][0]['text'], '污染')
        self.assertEqual(second['source_identity']['data_sha256'], model.DATA_SHA256)

    def test18_each_runtime_member_tamper_delete_and_recovery_is_fresh(self):
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
                        for index in range(2):
                            result = self.result(index)
                            self.assertFalse(result['source_valid'], (name, mode, index))
                            self.assertIsNone(result['reference'])
                            self.assertIsNone(result['source_identity'])
                            self.assertUnknown(result)
                    finally:
                        path.write_bytes(old)
                    self.assertTrue(self.result()['source_valid'], (name, mode))

    def test19_manifest_cannot_be_replaced_to_authorize_changed_data(self):
        root, manifest = self.clone()
        with patch.object(model, 'ROOT', root):
            self.assertTrue(self.result()['source_valid'])
            data = root / model.DATA
            data.write_bytes(data.read_bytes() + b' ')
            manifest['data_sha256'] = sha256(data.read_bytes()).hexdigest()
            manifest['runtime_files'][model.DATA] = {'sha256': manifest['data_sha256'], 'bytes': data.stat().st_size}
            (root / model.MANIFEST).write_text(json.dumps(manifest), encoding='utf8')
            self.assertFalse(self.result()['source_valid'])

    def test20_entire_target_stage_and_related_enemy_objects_must_match(self):
        for mode in ('map', 'related_enemy'):
            battle = deepcopy(self.battle)
            if mode == 'map':
                battle['stages']['ro6_b_5']['map'][0][0] = '污染'
            else:
                enemy = next(row for row in battle['stages']['ro6_b_5']['enemies'] if row['id'] == 'enemy_2149_shorsm')
                enemy['level'] = False
            with patch.object(battle_preview, 'battle_data', return_value=battle):
                self.assertFalse(self.result()['source_valid'])

    def test21_all_three_complete_skill_definitions_and_bindings_are_guarded(self):
        for enemy in ('enemy_2147_shophm', 'enemy_2148_shorbb', 'enemy_2149_shorsm'):
            for mode in ('definition', 'binding'):
                skills = deepcopy(self.skills)
                if mode == 'definition':
                    skills['definitions'][enemy]['0']['unexpected'] = True
                else:
                    skills['bindings']['ro6_b_5'][enemy + '@0']['stage_overrides'] = ['污染']
                with patch.object(enemy_skills, 'skill_data', return_value=skills):
                    self.assertFalse(self.result()['source_valid'], (enemy, mode))

    def test22_source_identity_drift_rejects_but_unrelated_stage_drift_does_not(self):
        battle = deepcopy(self.battle)
        battle['source']['unexpected'] = True
        with patch.object(battle_preview, 'battle_data', return_value=battle):
            self.assertFalse(self.result()['source_valid'])
        battle = deepcopy(self.battle)
        battle['stages']['ro6_t_1']['name'] = '无关关卡'
        with patch.object(battle_preview, 'battle_data', return_value=battle):
            self.assertTrue(self.result()['source_valid'])

    def test23_unknown_topic_and_invalid_source_never_retain_old_actor_reading(self):
        result = self.result()
        for value in (False, 0, [], 'first', ''):
            text = model.reference_text(result, value)
            self.assertIn('所选资料条目暂时无法核对', text)
            self.assertNotIn('象限封锁', text)
        with patch.object(model, '_packet', return_value=None):
            result = self.result()
        self.assertIn('旧说明与条目选择已清除', model.reference_text(result, 'cube'))
        self.assertIsNone(result['reference'])
        self.assertEqual(model.reference_text(None), '')

    def test24_reference_does_not_predict_or_mutate_legacy_combat_state(self):
        before = deepcopy(battle_preview.battle_data())
        with patch.object(battle_preview, 'enemy_preview', side_effect=AssertionError('not a prediction query')):
            for index in range(2):
                result = self.result(index)
                text = model.reference_text(result)
                for raw in ('enemy_2147', 'trap_324', 'complete_DOM', 'm_defined'):
                    self.assertNotIn(raw, text)
                self.assertUnknown(result)
        self.assertEqual(battle_preview.battle_data(), before)

    def test25_public_source_boundaries_and_exact_builder_reconstruction(self):
        for name in ('../private.json', 'C:/private.json', '/private.json', 'research\\file.json', 0):
            with self.assertRaises(ValueError):
                model._file(name)
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        self.assertIs(manifest['runtime_full_database_hashing'], False)
        self.assertEqual(set(manifest['runtime_files']), model.RUNTIME_FILES)
        self.assertFalse(any('enemy_database.json' in name or 'battle-previews.json' in name for name in manifest['runtime_files']))
        inputs = [ROOT / source['file'] for source in self.selected['source_files']]
        if not all(path.is_file() for path in inputs):
            self.skipTest('完整固定构建原件未提供，重建未执行，不能计为通过。')
        path = ROOT / 'scripts/build_boss_cycle_reference_310.py'
        spec = spec_from_file_location('cycle310_fixed_source_builder', path)
        builder = module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            receipt = builder.build(ROOT, output)
            self.assertEqual(receipt['boss_skill_cards'], 7)
            self.assertEqual(receipt['ability_cards'], 2)
            self.assertEqual(receipt['separate_module_skill_tables'], 1)
            for name in receipt['outputs']:
                self.assertEqual((output / name).read_bytes(), (ROOT / name).read_bytes(), name)


if __name__ == '__main__':
    unittest.main()
