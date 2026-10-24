import copy
import unittest
from unittest.mock import patch
from rouge import current_hanko as model


class CurrentHanko365Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = model.packet()
        assert cls.packet is not None, 'Install the candidate before execution.'
        cls.references = {sid: model.reference(sid) for sid in model.STAGES}
        assert all(cls.references.values())

    def test_six_exact_stages_five_levels_twelve_references(self):
        data = self.packet['data']
        self.assertEqual(tuple(data['bindings']), model.STAGES)
        self.assertEqual(len(data['originals']['levels']), 5)
        self.assertEqual(sum(len(r['rows']) for r in data['bindings'].values()), 12)
        for result in self.references.values():
            self.assertEqual(len(result['rows']), 2)
            self.assertEqual(sum(r['actor'] == 'smoke' for r in result['rows']), 1)
            self.assertIsNone(result['actual_skill_time']); self.assertFalse(result['numeric_model_added'])

    def test_all_seven_full_cards_and_four_original_corrected_descriptions_preserved(self):
        actors = self.packet['materials']['actors']
        self.assertEqual({k: len(r['cards']) for k, r in actors.items()}, {'hanko': 3, 'president': 3, 'smoke': 1})
        self.assertEqual(sum(len(r['descriptions_original_and_corrected']) for r in actors.values()), 4)
        for value in actors.values():
            for card in value['cards']:
                self.assertTrue(card['complete_DOM'].startswith('<div'))
                self.assertTrue(card['complete_DOM'].endswith('</div>'))
                self.assertTrue(card['body'])
        self.assertEqual((actors['hanko']['cards'][0]['initial_cooldown_documented'], actors['hanko']['cards'][0]['cooldown_documented']), (30, 30))
        self.assertEqual((actors['president']['cards'][0]['initial_cooldown_documented'], actors['president']['cards'][0]['cooldown_documented']), (2, 15))

    def test_full_game_original_and_community_correction_remain_distinct(self):
        result = self.references['ro6_b_1']; row = next(r for r in result['rows'] if r['actor'] == 'hanko')
        self.assertTrue(any('使其中所有单位' in r for r in row['enemy']['abilities']))
        text = model.player_text(result, row['key'], 'flare')
        self.assertIn('不会使其中所有单位', text)
        self.assertIn('原文与修正均保留', text)
        self.assertIn('烟雾弹', text)
        self.assertIn('天赋【烟雾】失效15秒', text)
        self.assertIsNone(result['actual_status_removed'])

    def test_overrides_do_not_promote_documented_fifteen_or_three_hundred_to_current_values(self):
        for sid in ('ro6_b_1_b', 'ro6_b_1_b_dlc1', 'ro6_t_4', 'ro6_e_t_4'):
            result = self.references[sid]
            boss = next(r for r in result['rows'] if r['actor'] != 'smoke')
            smoke = next(r for r in result['rows'] if r['actor'] == 'smoke')
            self.assertTrue(boss['has_stage_overwrite']); self.assertFalse(smoke['has_stage_overwrite'])
            text = model.player_text(result, boss['key'], 'flare')
            self.assertIn('通用文献的冷却、持续时间和数值不能直接视为本关实际值', text)
            self.assertIn('生成过程不会改变', model.player_text(result, smoke['key'], 'smoke'))
            self.assertIsNone(boss['actual_effective_parameters'])
        raw = next(r for r in self.references['ro6_b_1_b']['rows'] if r['actor'] == 'president')['raw_binding']
        self.assertEqual(raw['overwrittenData']['skills'][1]['blackboard'][0]['value'], 30.0)

    def test_false_defined_meeting_placeholders_do_not_rename_or_change_prefab(self):
        for sid in ('ro6_t_4', 'ro6_e_t_4'):
            row = next(r for r in self.references[sid]['rows'] if r['actor'] == 'president')
            self.assertEqual(row['raw_binding']['overwrittenData']['name']['m_value'], '玻利瓦尔军官改')
            self.assertIs(row['raw_binding']['overwrittenData']['name']['m_defined'], False)
            self.assertEqual(row['enemy']['name'], '“大总统”汉科')
            self.assertEqual(row['enemy']['prefab_key'], 'enemy_2139_shdbj2')

    def test_independent_smoke_has_only_its_own_topic_and_no_invented_spawn_count(self):
        result = self.references['ro6_b_1']; smoke = next(r for r in result['rows'] if r['actor'] == 'smoke')
        self.assertEqual(model.topics(result, smoke['key']), [('smoke', model.TOPICS['smoke'])])
        self.assertIsNone(model.selected_card(result, smoke['key'], 'blink'))
        text = model.player_text(result, smoke['key'], 'smoke')
        self.assertIn('角色类单位', text); self.assertIn('未被阻挡', text)
        self.assertIn('0.75秒', text); self.assertIn('300秒', text)
        self.assertIsNone(result['actual_smoke_cells'])
        self.assertEqual(len(model.related_entities(result, smoke['key'])), 1)

    def test_strict_identity_and_unsupported_stage_guards(self):
        for args in (('ro6_b_1', True), ('ro6_b_1', '999'), ('same_name', None), (False, None)):
            self.assertIsNone(model.reference(*args))
        self.assertIsNone(model.entity(self.references['ro6_b_1'], 0))
        self.assertEqual(model.topics(self.references['ro6_b_1'], '999'), [])

    def test_related_link_requires_current_whole_result_and_exact_reference(self):
        result = self.references['ro6_b_1']; source = result['rows'][0]['key']
        request = model.related_entities(result, source)[0]
        with patch.object(model, 'reference', return_value=copy.deepcopy(result)):
            target = model.resolve_related(result, source, request)
            self.assertEqual(target['enemy_key'], request['enemy_key']); self.assertFalse(target['run_updated'])
            self.assertIsNone(model.resolve_related(result, source, request | {'entity_id': 'enemy_2139_shdbj2'}))
            modified = copy.deepcopy(result); modified['stage_name'] = 'foreign'
            self.assertIsNone(model.resolve_related(modified, source, request))

    def test_current_whole_level_and_database_changes_invalidate_source(self):
        base = model.battle.packet(); changed = copy.deepcopy(base)
        key = self.packet['data']['bindings']['ro6_b_1']['level_key']
        changed['inputs']['levels'][key]['waves'][0]['preDelay'] += 1
        with patch.object(model.battle, 'packet', return_value=changed): self.assertIsNone(model.packet())
        changed = copy.deepcopy(base)
        changed['inputs']['enemy_definitions']['enemy_2156_shsmok'][0]['enemyData']['talentBlackboard'][1]['value'] = 200.0
        with patch.object(model.battle, 'packet', return_value=changed): self.assertIsNone(model.packet())

    def test_corrupt_manifest_fails_closed(self):
        read = model.battle.version._file
        class Damaged:
            def read_bytes(self): return b'{}'
        with patch.object(model.battle.version, '_file', side_effect=lambda name: Damaged() if name == model.MANIFEST else read(name)):
            self.assertIsNone(model.packet())


if __name__ == '__main__': unittest.main()
