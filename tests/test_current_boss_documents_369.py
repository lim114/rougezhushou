"""Necessary exact-current qualification checks. Prepared, not executed by subagent."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch
from rouge import current_boss_documents as model


class CurrentBossDocuments369Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = model.packet()
        if cls.packet is None: raise AssertionError('Prepared public sources must be installed before running')
        cls.references = {sid: model.reference(sid) for sid in model.STAGES}

    def test_exact_nine_targets_and_no_invented_database_aliases(self):
        self.assertEqual(len(model.TARGETS), 9)
        self.assertEqual(len(self.packet['data']['database_comparison']), 12)
        rows = self.packet['data']['database_comparison']
        self.assertEqual(sum(r['database_record_present'] for r in rows), 10)
        independent = [r['enemy_id'] for r in rows if r['independent_level_entity']]
        self.assertEqual(independent, ['enemy_2146_cadesd_2', 'enemy_2146_cadesd_3'])

    def test_all_nine_current_references_keep_authentic_legacy_identity(self):
        for sid, key, eid, level, family in model.TARGETS:
            with self.subTest(stage=sid, key=key):
                result = model.reference(sid, key); self.assertIsNotNone(result)
                row = model.entity(result, key); self.assertIsNotNone(row)
                self.assertEqual((row['enemy']['id'], row['enemy']['level']), (eid, level))
                doc = row['legacy_document']
                self.assertEqual((doc['stage_id'], doc['enemy_id'], doc['level']), (sid, eid, level))
                self.assertEqual(row['family'], family)
                self.assertIsNone(result['expected_stats']); self.assertIsNone(result['actual_phase'])
                self.assertIsNone(result['actual_skill_time']); self.assertFalse(result['numeric_model_added'])
                self.assertFalse(result['actual_server_verified']); self.assertFalse(result['run_updated'])

    def test_all_current_stage_configurations_only_offer_original_nine_tuples(self):
        current = self.packet['current']; stages = current['version']['current']['details']['stages']
        offered = []
        for sid, stage in stages.items():
            level = current['inputs']['levels'].get('levels/' + stage['levelId'].lower() + '.json')
            if level is None: continue
            for i, enemy in enumerate(level['enemyDbRefs']):
                if any(sid == t[0] and str(i) == t[1] for t in model.TARGETS): offered.append((sid, str(i)))
        self.assertEqual(len(stages), 184)
        self.assertEqual(set(offered), {(t[0], t[1]) for t in model.TARGETS})

    def test_same_name_other_stage_and_dlc1_do_not_inherit_document(self):
        for sid, key in [('ro6_b_4_b', '0'), ('ro6_b_5_b', '0'), ('ro6_b_2_dlc1', '1'),
                         ('ro6_b_2_b_dlc1', '0'), ('ro6_n_1_1', '9')]:
            self.assertIsNone(model.reference(sid, key))
        for bad in (0, True, '00', '-1', 'enemy_2150_shchmr', '1'):
            self.assertIsNone(model.reference('ro6_b_6', bad))

    def test_six_whole_level_qualifications_preserve_gold_difference(self):
        rows = [r for f in self.packet['data']['families'].values() for r in f['level_qualification']]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(r['whole_level_equal'] for r in rows), 5)
        change = next(r for r in rows if r['stage_id'] == 'ro6_b_2_b')
        self.assertEqual(change['changed_top_fields'], ['runes'])
        self.assertIsNone(change['differences'][0]['current'])
        self.assertEqual(len(change['differences'][0]['previous']), 2)
        text = model.player_text(self.references['ro6_b_2_b'], '0')
        self.assertIn('版本差异', text); self.assertIn('不沿用旧关卡', text)
        self.assertNotIn('1.3', text); self.assertNotIn('1.4', text)

    def test_complete_existing_topics_still_readable(self):
        for sid, key, _, _, family in model.TARGETS:
            result = self.references[sid]
            topics = model.topics(result, key)
            self.assertEqual(len(topics), 6 if family == 'phase' else 4)
            for item in topics:
                with self.subTest(stage=sid, key=key, topic=item['id']):
                    text = model.player_text(result, key, item['id'])
                    self.assertIn(item['name'], text)
                    self.assertIn('未知', text)
                    self.assertNotEqual(text, model.UNAVAILABLE)

    def test_unknown_topic_does_not_display_old_branch(self):
        result = self.references['ro6_b_4']
        self.assertIn('无法核对', model.player_text(result, '0', 'invented'))
        self.assertEqual(model.player_text(result, '0', True), model.UNAVAILABLE)

    def test_current_database_complete_record_mutation_blocks_all_documents(self):
        broken = deepcopy(self.packet['current'])
        broken['inputs']['enemy_definitions']['enemy_2150_shchmr'][0]['enemyData']['name']['m_value'] = 'changed'
        with patch.object(model.battle, 'packet', return_value=broken):
            self.assertIsNone(model.packet())

    def test_level_and_stage_mutations_block_including_new_runes(self):
        mutators = [
            lambda p: p['inputs']['levels']['levels/obt/roguelike/ro6/level_rogue6_b-2-b.json'].__setitem__('runes', []),
            lambda p: p['inputs']['levels']['levels/obt/roguelike/ro6/level_rogue6_b-5.json']['enemyDbRefs'][0].__setitem__('level', True),
            lambda p: p['version']['current']['details']['stages']['ro6_b_6'].__setitem__('name', 'changed'),
            lambda p: p['inputs']['handbook']['enemy_2150_shchmr'].__setitem__('name', 'changed'),
        ]
        for mutate in mutators:
            broken = deepcopy(self.packet['current']); mutate(broken)
            with patch.object(model.battle, 'packet', return_value=broken): self.assertIsNone(model.packet())

    def test_legacy_source_failure_never_authorizes_current_reader(self):
        with patch.object(model, '_legacy', return_value=(lambda *a: None, lambda *a: 'old text')):
            self.assertIsNone(model.reference('ro6_b_6', '0'))

    def test_stale_or_forged_document_result_clears_player_text(self):
        result = deepcopy(self.references['ro6_b_6'])
        result['rows'][0]['legacy_document']['reference']['boss_name'] = 'forged'
        self.assertEqual(model.player_text(result, '0'), model.UNAVAILABLE)
        result = deepcopy(self.references['ro6_b_6']); result['expected_stats'] = {'atk': 999}
        self.assertEqual(model.player_text(result, '0'), model.UNAVAILABLE)

    def test_bad_manifest_cannot_keep_prior_source(self):
        with TemporaryDirectory() as temp:
            bad = Path(temp) / 'bad.json'; bad.write_text('{}', encoding='utf-8')
            original = model.battle.version._file
            with patch.object(model.battle.version, '_file', side_effect=lambda n: bad if n == model.MANIFEST else original(n)):
                self.assertIsNone(model.packet())
                self.assertEqual(model.player_text(self.references['ro6_b_6'], '0'), model.UNAVAILABLE)

    def test_related_entity_is_exact_same_stage_and_rejects_forged_request(self):
        result = self.references['ro6_b_5']; rows = model.related_entities(result, '0')
        self.assertEqual({r['entity_id'] for r in rows}, {'enemy_2148_shorbb', 'enemy_2149_shorsm'})
        for row in rows:
            request = model.resolve_entity(result, '0', row)
            self.assertEqual((request['stage_id'], request['enemy_key']), ('ro6_b_5', row['key']))
        bad = deepcopy(rows[0]); bad['key'] = '999'
        self.assertIsNone(model.resolve_entity(result, '0', bad))

    def test_original_map_reference_rejects_geometry_mismatch(self):
        from rouge import current_map_position as maps
        result = self.references['ro6_b_6']
        broken = {'stage_id': result['stage_id'], 'current_level_key': result['level_key'],
                  'source_identity': 'wrong', 'complete_current_geometry': {'mapData': {}}}
        with patch.object(maps, 'stage_reference', return_value=broken): self.assertIsNone(model.map_reference(result))

    def test_current_stage_exact_enemy_binding_cannot_be_swapped(self):
        good = model.battle.stage_reference('ro6_b_6'); broken = deepcopy(good)
        broken['enemies'][0]['raw_binding']['level'] = 1
        with patch.object(model.battle, 'stage_reference', return_value=broken):
            self.assertIsNone(model.reference('ro6_b_6', '0'))

    def test_true_false_types_and_empty_overview_are_distinct(self):
        self.assertFalse(model._same(True, 1)); self.assertFalse(model._same(False, 0))
        self.assertIn('请选择', model.player_text(self.references['ro6_b_6']))
        self.assertEqual(model.topics(None, '0'), [])
        self.assertEqual(model.related_entities(None, '0'), [])


if __name__ == '__main__':
    unittest.main()
