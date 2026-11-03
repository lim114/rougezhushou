"""Exact identity, complete source, version and unknown-state contracts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import ast
import json
import shutil
import unittest

from rouge import gold_boss_reference as model, battle_preview, enemy_skills
from scripts import build_gold_boss_reference_312 as builder

ROOT = Path(__file__).resolve().parents[1]
KEYS = (('ro6_b_2', 'enemy_2140_shsgzd', 0), ('ro6_b_2', 'enemy_2142_shsggd', 0),
        ('ro6_b_2_b', 'enemy_2141_shsgz2', 0))


class GoldBossReference312Tests(unittest.TestCase):
    def result(self, i=0):
        return model.gold_reference(*KEYS[i])

    def clone(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        for name in (model.MANIFEST, *manifest['runtime_files']):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        return root, manifest

    def test_exact_three_stage_enemy_level_entries_and_every_actual_state_unknown(self):
        self.assertEqual(model.TARGETS, KEYS)
        for i, name in enumerate(('德莱昂', '赤金条', '“征服者”德莱昂')):
            result = self.result(i)
            self.assertIs(result['source_valid'], True)
            self.assertEqual(result['reference']['entry_name'], name)
            for field in model.ACTUAL_FIELDS:
                self.assertIsNone(result[field])
            for field in model.FALSE_FIELDS:
                self.assertIs(result[field], False)

    def test_wrong_versions_level_types_and_unrelated_entities_do_no_source_io(self):
        with patch.object(model, '_packet', side_effect=AssertionError('Unrelated source I/O')):
            for key in ((None, None, None), ([], {}, 0), (KEYS[0][0], KEYS[0][1], False),
                        (KEYS[0][0], KEYS[0][1], 0.0), (KEYS[0][0], KEYS[0][1], 1),
                        ('ro6_b_2_b', KEYS[0][1], 0), ('ro6_b_2', KEYS[2][1], 0),
                        ('ro6_b_2_b', KEYS[1][1], 0), ('ro6_b_4', KEYS[0][1], 0)):
                self.assertIsNone(model.gold_reference(*key), key)

    def test_complete_six_skill_three_ability_cards_dom_and_tooltips_preserved(self):
        docs = self.result()['complete_document_cards']
        cards = [card for doc in docs.values() for card in doc['cards']]
        self.assertEqual(sum(c['header'] is not None for c in cards), 6)
        self.assertEqual(sum(c['header'] is None for c in cards), 3)
        self.assertTrue(all(c['complete_DOM']['children'] and c['full'] for c in cards))
        self.assertIn('mc-tooltips', json.dumps(docs, ensure_ascii=False))
        self.assertEqual([len(self.result(i)['reference']['skills']) for i in range(3)], [3, 0, 3])
        for i in (0, 2):
            actor = self.result(i)['reference']['entry_name']
            for skill in self.result(i)['reference']['skills']:
                self.assertEqual(skill['source_actor'], actor)
                self.assertEqual(skill['text'], '\n'.join(docs[actor]['cards'][skill['card_index']]['paragraphs']))

    def test_version_movement_is_selected_not_silently_reused(self):
        normal = model.reference_text(self.result(0))
        stronger = model.reference_text(self.result(2))
        self.assertIn('移动速度+100%', normal)
        self.assertNotIn('移动速度+200%', normal)
        self.assertIn('移动速度+200%', stronger)
        self.assertNotIn('移动速度+100%', stronger)
        self.assertIn('光荣远征', normal)
        self.assertIn('赤金厄运', stronger)

    def test_four_topics_have_all_source_card_citations_and_manual_text(self):
        for i in range(3):
            result = self.result(i)
            self.assertEqual([t['id'] for t in result['reference']['topics']],
                             ['conditions', 'flight', 'gold', 'plunder_exit'])
            for topic in result['reference']['topics']:
                text = model.reference_text(result, topic['id'])
                self.assertIn('【' + topic['name'] + '】', text)
                self.assertTrue(topic['evidence'])
                for citation in topic['evidence']:
                    cards = result['complete_document_cards'][citation['actor']]['cards']
                    self.assertTrue(all(cards[i] for i in citation['card_indices']))
            self.assertIn('重新选择', model.reference_text(result, 'absent'))
            self.assertIn('重新选择', model.reference_text(result, False))

    def test_hit_attempt_skill_end_and_successful_gold_exit_are_distinct(self):
        flow = model.reference_text(self.result(), 'conditions')
        gold = model.reference_text(self.result(), 'gold')
        for word in ('才会尝试', '技能结束后', '第10秒', '无原因退场', '不能当作被击倒'):
            self.assertIn(word, flow)
        for word in ('只有成功触发后', '攻击尝试', '才立即死亡', '取消该次伤害', '已经死亡'):
            self.assertIn(word, gold)

    def test_gold_reward_is_conditional_not_a_drop_pool_or_claimed_quantity(self):
        text = model.reference_text(self.result(1), 'gold')
        for word in ('抵达自己的路径终点', '光彩松露', '不表示当前已获得', '数量或概率', '未列出它', '动态出现'):
            self.assertIn(word, text)
        selected = json.loads((ROOT / model.SELECTED).read_bytes())
        self.assertTrue(any(e['id'] == KEYS[1][1] for e in selected['complete_canonical_stages']['ro6_b_2']['enemies']))
        self.assertFalse(any(e['id'] == KEYS[1][1] for e in selected['complete_canonical_stages']['ro6_b_2_b']['enemies']))
        self.assertIsNone(self.result(1)['actual_reward'])

    def test_plunder_initial_check_is_not_current_absence_or_full_cycle(self):
        text = model.reference_text(self.result(), 'plunder_exit')
        for word in ('第0.1秒', '现在是否有赤金条', '25秒', '12.5秒', '不是完整', '攻击力+50%'):
            self.assertIn(word, text)
        self.assertIsNone(self.result()['actual_plunder_buff'])

    def test_uncertain_geometry_and_unmatched_boom_parameters_do_not_create_damage_model(self):
        text = model.reference_text(self.result(), 'flight')
        for word in ('存疑', '地面寻路', '飞行高度', '不根据名称相似或数组顺序'):
            self.assertIn(word, text)
        self.assertNotIn('Boom', text)
        selected = json.loads((ROOT / model.SELECTED).read_bytes())
        skills = selected['complete_skill_definitions'][KEYS[0][1]]['0']['skills']
        self.assertTrue(any(s['prefabKey'] == 'Boom' for s in skills))
        self.assertNotIn('Boom', [s['name'] for s in self.result()['reference']['skills']])

    def test_every_actual_runtime_member_is_required_even_after_a_warm_read(self):
        root, manifest = self.clone()
        with patch.object(model, 'ROOT', root):
            self.assertTrue(self.result()['source_valid'])
            for name in (model.MANIFEST, *manifest['runtime_files']):
                with self.subTest(member=name):
                    path = root / name
                    raw = path.read_bytes()
                    try:
                        path.write_bytes(raw + b' ')
                        result = self.result()
                        self.assertFalse(result['source_valid'])
                        self.assertIsNone(result['reference'])
                    finally:
                        path.write_bytes(raw)
                    self.assertTrue(self.result()['source_valid'])

    def test_stale_caller_packet_and_return_mutation_cannot_authorize_old_text(self):
        original = self.result()
        altered = deepcopy(original)
        altered['reference']['topics'][0]['paragraphs'].append('invented')
        self.assertEqual(model.reference_text(altered), model.UNAVAILABLE)
        altered['complete_document_cards'].clear()
        self.assertTrue(self.result()['complete_document_cards'])
        root, _ = self.clone()
        (root / model.SELECTED).write_bytes(b'{}')
        with patch.object(model, 'ROOT', root):
            self.assertEqual(model.reference_text(original), model.UNAVAILABLE)

    def test_whole_current_stage_source_definition_and_binding_drift_rejects(self):
        original_battle = deepcopy(battle_preview.battle_data())
        original_skills = deepcopy(enemy_skills.skill_data())
        for kind in ('stage', 'binding', 'definition', 'source'):
            battle, skills = deepcopy(original_battle), deepcopy(original_skills)
            if kind == 'stage':
                battle['stages']['ro6_b_2_b']['name'] += 'changed'
            elif kind == 'binding':
                skills['bindings']['ro6_b_2'][KEYS[0][1] + '@0']['use_db'] = False
            elif kind == 'definition':
                skills['definitions'][KEYS[2][1]]['0']['talentBlackboard'].clear()
            else:
                battle['source']['unexpected'] = True
            with patch.object(battle_preview, 'battle_data', return_value=battle), patch.object(enemy_skills, 'skill_data', return_value=skills):
                self.assertFalse(self.result()['source_valid'], kind)

    def test_runtime_never_opens_full_database_or_unrelated_files(self):
        original = model._file
        opened = []
        def track(name):
            opened.append(name)
            self.assertNotIn('.cache/', name)
            self.assertNotIn('.local/', name)
            return original(name)
        with patch.object(model, '_file', side_effect=track):
            self.assertTrue(self.result()['source_valid'])
        self.assertEqual(set(opened), {model.MANIFEST, *model.RUNTIME_FILES})

    def test_rebuild_is_byte_exact_or_missing_original_is_explicitly_unavailable(self):
        selected = json.loads((ROOT / model.PACK / 'selected-original-authority.json').read_bytes())
        missing = [name for name in selected['source_files'] if not (ROOT / name).is_file()]
        if missing:
            self.skipTest('完整固定原件不可用，不计为构建通过：' + ','.join(missing))
        files = builder.build(ROOT)
        for name, raw in files.items():
            self.assertEqual(raw, (ROOT / name).read_bytes(), name)
        self.assertEqual(sha256(files[model.DATA]).hexdigest(), model.DATA_SHA256)

    def test_path_traversal_and_symlink_parent_contract_is_fail_closed(self):
        for name in ('../private.json', '/absolute', 'C:/private', 'a\\b', 'a/../b'):
            with self.assertRaises(ValueError):
                model._file(name)


if __name__ == '__main__':
    unittest.main()
