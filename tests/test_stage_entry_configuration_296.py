"""Necessary public-source boundary tests; no Qt, game, chat or private data."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path('research/p3-stage-entry-configuration-296')
MODULE = Path('rouge/stage_entry_reference.py')


def load_module(root):
    spec = importlib.util.spec_from_file_location('stage_entry_reference_296_public_test', root / MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StageEntryConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rouge-296-public-')
        self.root = Path(self.temp.name)
        from rouge import stage_entry_reference as current_module
        manifest_file = Path(current_module.MANIFEST)
        manifest = json.loads((ROOT / manifest_file).read_bytes())
        files = [MODULE, Path('rouge/data/stage-entry-configuration-reference.json'), manifest_file]
        files.extend(Path(name) for name in manifest['files'])
        for relative in files:
            (self.root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, self.root / relative)
        self.module = load_module(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def reference(self):
        result = self.module.stage_entry_reference('ro6_t_12')
        self.assertEqual(result['status'], 'documented_reference')
        return result

    def test_only_exact_stage_reads_sources_no_emergency_or_same_name_alias(self):
        with patch.object(self.module, '_verified_packet', side_effect=AssertionError('No source scan permitted')):
            for value in (None, True, 12, [], {}, '无效验尸', 'ro6_e_t_12', 'ro6_t_12_b', 'RO6_T_12', ''):
                with self.subTest(value=value):
                    self.assertIsNone(self.module.stage_entry_reference(value))

    def test_fixed_stage_identity_and_full_original_are_retained(self):
        row = self.reference()
        self.assertEqual(row['stage_name'], '无效验尸')
        self.assertEqual(row['stage']['levelId'], 'Obt/Roguelike/RO6/level_rogue6_t-12')
        self.assertEqual(row['stage']['difficulty'], 'NORMAL')
        self.assertEqual(row['stage']['linkedStageId'], '')
        self.assertEqual(row['stage']['levelReplaceIds'], [])
        self.assertIn('boxProb', row['stage'])

    def test_three_floor_wordings_and_separate_fake_layer_are_not_a_global_pool(self):
        result = self.reference()
        self.assertEqual([r['main_floor_reference'] for r in result['rows']], [3, 4, 5, None])
        self.assertEqual([r['source_usage'] for r in result['rows']], [
            '给3层普通作战挂上狼兽主气泡', '给4层普通作战挂上狼兽主气泡',
            '给5层普通作战挂上狼兽主气泡', '给假层普通作战挂上狼兽主气泡'])
        self.assertEqual(result['rows'][3]['label'], '原资料称假层（不推定主层或秘境）')
        self.assertIsNone(result['complete_stage_floor_pool'])
        self.assertFalse(result['floor_eligibility_evaluated'])

    def test_four_distinct_feature_and_zone_objects_and_normal_node_type(self):
        rows = self.reference()['rows']
        self.assertEqual([r['feature_id'] for r in rows], [
            'rogue_6_end_3_relic_trigger_1', 'rogue_6_end_3_relic_trigger_2',
            'rogue_6_end_3_relic_trigger_3', 'rogue_6_end_3_relic_trigger_10'])
        self.assertEqual([r['zone']['id'] for r in rows], ['zone_3', 'zone_4', 'zone_5', 'zone_4_1'])
        for row in rows:
            self.assertEqual(row['feature_item']['type'], 'FEATURE')
            self.assertEqual(row['feature_relic']['id'], row['feature_id'])
            self.assertEqual(row['node_type'], 'BATTLE_NORMAL')
            self.assertIs(row['zone']['isHiddenZone'], False)
        self.assertEqual(rows[3]['zone']['name'], '受害者腐殖')

    def test_blackboard_types_and_all_six_pointers_are_preserved(self):
        for row in self.reference()['rows']:
            bb = row['feature_relic']['buffs'][0]['blackboard']
            self.assertEqual([b['key'] for b in bb], ['id', 'node', 'limit', 'zone_id', 'not_hold_relic_id', 'stage_id'])
            self.assertEqual([b['valueStr'] for b in bb], ['rogue_6_bubble_04', 'BATTLE_NORMAL', None,
                row['zone']['id'], 'rogue_6_relic_final_5', 'ro6_t_12'])
            self.assertEqual([b['value'] for b in bb], [0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
            self.assertTrue(all(type(b['value']) is float for b in bb))
            self.assertIs(type(row['configured_limit']), float)
            self.assertFalse(row['configured_limit_is_actual_count'])
            self.assertIsNone(row['actual_count'])

    def test_full_marker_and_distinct_item_text_do_not_prove_feature_acquisition(self):
        result = self.reference()
        self.assertEqual(result['marker']['item']['name'], '光明之末')
        self.assertEqual(result['marker']['item']['type'], 'NODE_BUOY')
        self.assertEqual(result['marker']['relic']['id'], 'rogue_6_bubble_04')
        self.assertIn('持有“怦然信标”，可以获得削弱强敌的方法。', result['marker']['item']['usage'])
        self.assertEqual(result['not_hold_item']['item']['name'], '湮没“光明”')
        self.assertEqual(result['beacon_item']['item']['name'], '怦然信标')
        self.assertEqual([b['key'] for b in result['beacon_item']['relic']['buffs']],
                         ['char_attribute_mul', 'global_buff_normal', 'push_message'])
        self.assertIs(result['upstream_reference']['activation_script_recovered'], False)
        self.assertIsNone(result['upstream_reference']['actual_feature_acquisition'])
        self.assertFalse(result['current_inventory_used'])

    def test_all_actuals_remain_unknown_with_no_status_matched_or_excluded(self):
        result = self.reference()
        for key in ('actual_eligibility', 'actual_node', 'actual_entry', 'actual_reward', 'actual_count', 'complete_stage_floor_pool'):
            self.assertIsNone(result[key])
        self.assertNotIn('checks', result)
        self.assertNotIn('conditions', result)
        for row in result['rows']:
            for key in ('actual_feature_attached', 'actual_node_marked', 'actual_stage_replacement', 'actual_count'):
                self.assertIsNone(row[key])
        self.assertIn('不保证每层出现一场', '\n'.join(result['unknowns']))

    def test_fixed_community_complete_paragraph_is_not_a_server_gate(self):
        result = self.reference()
        source = result['community_reference']
        self.assertEqual(source['community_revision'], 433770)
        self.assertEqual(source['role'], 'community_description_not_activation_script')
        self.assertFalse(source['beacon_acquisition_implies_feature_attachment_proven'])
        self.assertEqual(source['text'], '<光明之末>：未持有【湮没“光明”】时标记于普通【作战】：对战未名的荒原的无效验尸，完成后可以选择获得收藏品【湮没“光明”】。')
        self.assertEqual(result['source']['game_commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
        self.assertIn('not current-server', result['source']['scope'])

    def test_original_spans_bind_twenty_one_full_objects_and_not_reencoded_copies(self):
        entries = json.loads((self.root / PACKET / 'topic-selected-index.json').read_bytes())
        self.assertEqual(len(entries), 21)
        self.assertEqual(sum(entry['bytes'] for entry in entries), 14659)
        for entry in entries:
            raw = (self.root / entry['file']).read_bytes()
            self.assertEqual(len(raw), entry['end_byte_exclusive'] - entry['start_byte'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
            self.assertEqual(entry['complete_original_sha256'], 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86')
            self.assertIs(type(json.loads(raw)), dict)

    def test_mutating_public_results_or_source_data_never_changes_a_future_result(self):
        a = self.reference()
        a['rows'][0]['main_floor_reference'] = 1
        a['marker']['item']['name'] = 'wrong'
        a['source']['game_commit'] = 'wrong'
        packet = self.module.source_data()
        packet['stage']['id'] = 'wrong'
        packet['rows'].clear()
        b = self.reference()
        self.assertEqual(b['rows'][0]['main_floor_reference'], 3)
        self.assertEqual(b['marker']['item']['name'], '光明之末')
        self.assertEqual(len(self.module.source_data()['rows']), 4)

    def reject_tamper_and_restore(self, relative):
        original = (self.root / relative).read_bytes()
        self.reference()  # warm the parsed cache before changing any evidence.
        (self.root / relative).write_bytes(original + b'\n')
        failed = self.module.stage_entry_reference('ro6_t_12')
        self.assertEqual(failed['status'], 'source_unavailable')
        self.assertEqual(failed['rows'], [])
        self.assertIsNone(failed['marker'])
        self.assertIsNone(failed['source'])
        self.assertIsNone(self.module.source_data())
        (self.root / relative).write_bytes(original)
        self.assertEqual(len(self.reference()['rows']), 4)

    def test_warm_data_tamper_is_rejected_then_valid_restoration_recovers(self):
        self.reject_tamper_and_restore(Path(self.module.DATA))

    def test_warm_manifest_tamper_is_rejected_then_valid_restoration_recovers(self):
        self.reject_tamper_and_restore(Path(self.module.MANIFEST))

    def test_warm_original_feature_marker_and_community_tamper_each_fail_closed(self):
        for relative in (PACKET / 'original-values/relics--rogue_6_end_3_relic_trigger_10.json',
                         PACKET / 'original-values/items--rogue_6_bubble_04.json',
                         PACKET / 'community-marker-original.html'):
            with self.subTest(file=relative):
                self.reject_tamper_and_restore(relative)

    def test_warm_missing_data_is_rejected_and_unrelated_builder_change_is_tolerated(self):
        self.reference()
        source = self.root / PACKET / 'original-values/zones--zone_4_1.json'
        raw = source.read_bytes()
        source.unlink()
        self.assertEqual(self.module.stage_entry_reference('ro6_t_12')['rows'], [])
        source.write_bytes(raw)
        self.reference()
        before=self.reference()
        helper=self.root/'scripts/build_stage_entry_configuration_296.py'
        helper.parent.mkdir(parents=True,exist_ok=True);helper.write_text('# Unrelated build helper; never executed at runtime.\n','utf8')
        self.assertEqual(self.reference(),before)

    def test_runtime_does_not_write_files_or_need_original_large_table(self):
        def files():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = files()
        self.assertFalse((self.root / '.cache/p3-287-event-research/fixed-game-topic.json').exists())
        self.reference()
        self.module.source_data()
        self.assertEqual(before, files())


if __name__ == '__main__':
    unittest.main(verbosity=2)
