from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from rouge import current_settlement_modes_reference as model
from scripts.build_current_settlement_modes_362 import build, parse_html


class CurrentSettlementModes362Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = model.packet()
        if cls.source is None:
            raise AssertionError('Actual pinned sources must be available before domain checks')

    def test_actual_source_build_and_thirty_six_unambiguous_mode_pairs(self):
        output = build(model.ROOT)
        for name, raw in output.items():
            self.assertEqual((model.ROOT / name).read_bytes(), raw)
        data = self.source['data']
        self.assertEqual(data['source']['revision'], 442954)
        self.assertEqual(data['marked_nonzero_mode_pairs'], 36)
        self.assertEqual(len(data['main_floor_table']), 6)
        self.assertEqual(len(data['special_battle_table']), 18)
        self.assertFalse(data['source']['current_server_verified'])
        self.assertFalse(data['all_current_stage_rewards_known'])

    def test_first_main_rows_and_unknown_entry_never_select_player_technology(self):
        with patch.object(model, 'packet', return_value=self.source):
            for sid, base, full, gold in (('ro6_n_1_2', 10, 13, 1), ('ro6_e_1_2', 12, 15, 2), ('ro6_n_6_1', 20, 26, 5)):
                result = model.stage_reference(sid, 'map')
                self.assertEqual(result['conditional_base_experience'], base)
                self.assertEqual(result['conditional_full_technology_experience'], full)
                self.assertEqual(result['conditional_base_gold'], {'minimum': gold, 'maximum': gold})
                self.assertIsNone(result['conditional_current_experience'])
                self.assertIsNone(result['actual_player_technology'])
                self.assertIsNone(result['actual_reward_total'])
                self.assertFalse(result['inventory_updated'])
                unknown = model.stage_reference(sid)
                self.assertIsNone(unknown['conditional_base_experience'])
                self.assertIsNone(unknown['conditional_full_technology_experience'])
                self.assertIsNone(unknown['conditional_base_gold'])
                self.assertIn('不能相加', model.player_text(result))
                self.assertNotIn('1013', model.player_text(result))

    def test_new_crystal_event_and_ordinary_pursuit_stay_separate_for_both_configs(self):
        with patch.object(model, 'packet', return_value=self.source):
            for sid in ('ro6_t_16', 'ro6_c_9'):
                event = model.stage_reference(sid, 'event')
                self.assertEqual(event['conditional_base_experience'], 30)
                self.assertEqual(event['conditional_full_technology_experience'], 39)
                self.assertEqual(event['conditional_base_gold'], {'minimum': 3, 'maximum': 3})
                pursuit = model.stage_reference(sid, 'pursuit')
                self.assertEqual(pursuit['conditional_base_experience'], 0)
                self.assertEqual(pursuit['conditional_full_technology_experience'], 0)
                self.assertEqual(pursuit['conditional_base_gold'], {'minimum': 0, 'maximum': 0})
                self.assertIsNone(model.stage_reference(sid)['conditional_base_experience'])
                self.assertIsNone(model.stage_reference(sid, 'map')['conditional_base_experience'])
                self.assertIsNone(model.stage_reference(sid, 'event', 'portal')['conditional_base_experience'])
                self.assertFalse(event['actual_entry_verified'])

    def test_hidden_sixth_region_and_side_path_missing_rows_remain_unknown(self):
        with patch.object(model, 'packet', return_value=self.source):
            for sid in ('ro6_b_7', 'ro6_b_7_b', 'ro6_n_7_1', 'ro6_e_7_1'):
                result = model.stage_reference(sid, 'map')
                self.assertIsNone(result['conditional_base_experience'])
                self.assertIsNone(result['conditional_full_technology_experience'])
                self.assertIsNone(result['conditional_base_gold'])
            result = model.stage_reference('ro6_n_4_1_dlc1', 'map', 'side_path')
            self.assertIsNone(result['conditional_base_experience'])
            self.assertIsNone(result['conditional_base_gold'])
            self.assertEqual(result['documented_side_path_bonus']['random_relics'], 1)
            self.assertIsNone(model.stage_reference('ro6_n_4_1_dlc1', 'event', 'side_path')['documented_side_path_bonus'])

    def test_special_emergency_ranges_and_unknown_gold_cells(self):
        with patch.object(model, 'packet', return_value=self.source):
            for rule in self.source['data']['special_battle_table']:
                for sid in rule['stage_ids']:
                    result = model.stage_reference(sid, 'event')
                    self.assertEqual(result['conditional_base_experience'], rule['experience_modes']['base'])
                    self.assertEqual(result['conditional_full_technology_experience'], rule['experience_modes']['full_technology'])
                    self.assertEqual(result['conditional_base_gold'], rule['base_gold'])
            self.assertEqual(model.stage_reference('ro6_t_1', 'event')['conditional_base_gold'], {'minimum': 2, 'maximum': 3})
            self.assertIsNone(model.stage_reference('ro6_s_1', 'event')['conditional_base_gold'])

    def test_dom_classes_not_numeric_size_and_missing_markers_refused(self):
        html = (model.ROOT / model.HTML).read_text(encoding='utf8')
        stages = {key: row['original_stage'] for key, row in self.source['directory']['data']['rows'].items()}
        changed = html.replace('>10</span><span class="mw-collapsible mw-collapsed is6-exp is-fulltech"',
                               '>99</span><span class="mw-collapsible mw-collapsed is6-exp is-fulltech"', 1)
        self.assertNotEqual(changed, html)
        parsed, _ = parse_html(changed, stages)
        self.assertEqual(parsed['main_floor_table']['floor1']['normal']['experience_modes']['base'], 99)
        self.assertEqual(parsed['main_floor_table']['floor1']['normal']['experience_modes']['full_technology'], 13)
        with self.assertRaises(ValueError):
            parse_html(html.replace('is6-exp is-fulltech', 'is6-exp', 1), stages)
        with self.assertRaises(ValueError):
            parse_html(html.replace('显示满级生命游戏加成', '无法区分的按钮', 1), stages)

    def test_pinned_source_mutations_clear_and_recover(self):
        manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for name in (model.MANIFEST, *manifest['files']):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((model.ROOT / name).read_bytes())
            with patch.object(model, 'ROOT', root):
                for name in (model.MANIFEST, *manifest['files']):
                    path = root / name
                    raw = path.read_bytes()
                    self.assertIsNotNone(model.packet())
                    path.write_bytes(raw + b' ')
                    self.assertIsNone(model.packet(), name)
                    self.assertIsNone(model.stage_reference('ro6_n_1_2', 'map'), name)
                    path.write_bytes(raw)
                    self.assertIsNotNone(model.packet(), name)

    def test_invalid_context_exact_identity_and_defensive_results(self):
        with patch.object(model, 'packet', return_value=self.source):
            for stage in ('not-real', '晶矿惊蝗', True, None):
                self.assertIsNone(model.stage_reference(stage))
            for entry, region in (('wrong', 'catalog'), ('map', 'floor7'), ([], 'catalog')):
                with self.assertRaises(ValueError):
                    model.stage_reference('ro6_n_1_2', entry, region)
            result = model.stage_reference('ro6_n_1_2', 'map')
            result['rows'][0]['rule']['experience_modes']['base'] = 999
            self.assertEqual(model.stage_reference('ro6_n_1_2', 'map')['conditional_base_experience'], 10)
        with patch.object(model.prior, 'packet', return_value=None):
            self.assertIsNone(model.packet())


if __name__ == '__main__':
    unittest.main()
