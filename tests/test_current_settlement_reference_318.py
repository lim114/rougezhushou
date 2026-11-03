from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_settlement_reference as model
from scripts.build_current_settlement_318 import build,quantity
ROOT=Path(__file__).resolve().parents[1]

class CurrentSettlementReference318Tests(unittest.TestCase):
    def test_reproducible_pins_and_all_current_identities_supported(self):
        raw,manifest=build();self.assertEqual(raw,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes());ref=model.packet();self.assertIsNotNone(ref);self.assertEqual(len(ref['data']['main_floor_table']),6);self.assertEqual(len(ref['data']['special_battle_table']),18)
        with patch.object(model,'packet',return_value=ref):
            for sid in ref['directory']['data']['rows']:
                r=model.stage_reference(sid);self.assertIsNotNone(r);self.assertIsNone(r['actual_reward_total']);self.assertFalse(r['inventory_updated']);self.assertFalse(r['complete_reward_pool_known']);self.assertIsNone(r['conditional_base_gold']);self.assertIsNone(r['conditional_current_experience'])
    def test_basic_gold_and_historical_experience_not_collapsed1013_current(self):
        r=model.stage_reference('ro6_n_1_2','map');self.assertEqual(r['conditional_base_gold'],{'minimum':1,'maximum':1});self.assertIsNone(r['conditional_current_experience']);h=r['rows'][0]['rule']['historical_experience_reference'];self.assertEqual((h['base'],h['full_technology']), (10,13));self.assertFalse(h['applied_to_current']);self.assertEqual(h['source_revision'],'433770');self.assertNotIn('1013',model.player_text(r));self.assertIn('旧版',model.player_text(r))
    def test_emergency_and_normal_use_distinct_current_columns(self):
        self.assertEqual(model.stage_reference('ro6_n_1_2','map')['conditional_base_gold'],{'minimum':1,'maximum':1});self.assertEqual(model.stage_reference('ro6_e_1_2','map')['conditional_base_gold'],{'minimum':2,'maximum':2})
    def test_two_sixth_regions_never_share_missing_hidden_reward_row(self):
        for sid in ('ro6_b_7','ro6_b_7_b','ro6_n_7_1','ro6_e_7_1'):
            r=model.stage_reference(sid,'map');self.assertIsNone(r['conditional_base_gold']);self.assertIn('同层另一特殊区域',model.player_text(r))
        r=model.stage_reference('ro6_n_6_1','map');self.assertEqual(r['conditional_base_gold'],{'minimum':5,'maximum':5})
    def test_unknown_entrance_is_not_no_reward_and_mismatches_do_not_sum(self):
        r=model.stage_reference('ro6_n_1_2');self.assertIsNone(r['conditional_base_gold']);self.assertEqual(r['rows'][0]['rule']['base_gold'],{'minimum':1,'maximum':1});self.assertEqual(r['rows'][0]['status'],'unknown');self.assertIsNone(model.stage_reference('ro6_n_1_2','event')['conditional_base_gold'])
    def test_same_named_event_and_ordinary_pursuit_are_separate(self):
        ref=model.packet();sid=next(sid for sid,row in ref['directory']['data']['rows'].items()if row['name']=='“闹乐”'and row['original_stage']['difficulty']=='NORMAL');r=model.stage_reference(sid);self.assertEqual(len(r['rows']),2);self.assertIsNone(r['conditional_base_gold'])
        event=model.stage_reference(sid,'event');pursuit=model.stage_reference(sid,'pursuit');self.assertEqual(event['conditional_base_gold'],{'minimum':3,'maximum':3});self.assertIsNone(event['conditional_current_experience']);self.assertEqual(pursuit['conditional_base_gold'],{'minimum':0,'maximum':0});self.assertEqual(pursuit['conditional_current_experience'],0);self.assertEqual(next(r['rule']for r in pursuit['rows']if r['status']=='listed_matched')['recruit_ticket_reference'],1)
    def test_boss_pursuit_not_ordinary_zero_and_declared_region_limits(self):
        ref=model.packet();sid=next(sid for sid,r in ref['directory']['data']['rows'].items()if r['play_kind']=='boss'and r['floor']=='floor3');r=model.stage_reference(sid,'boss_pursuit');self.assertEqual(r['conditional_base_gold'],{'minimum':5,'maximum':5});self.assertIsNone(r['conditional_current_experience']);self.assertIsNone(model.stage_reference(sid,'pursuit')['conditional_base_gold']);self.assertIsNone(model.stage_reference(sid,'boss_pursuit','portal')['conditional_base_gold'])
    def test_special_ranges_and_unknown_cells_are_not_midpoint_or_zero(self):
        r=model.stage_reference('ro6_t_1','event');self.assertEqual(r['conditional_base_gold'],{'minimum':2,'maximum':3});self.assertIn('2至3',model.player_text(r));self.assertIsNone(model.stage_reference('ro6_s_1','event')['conditional_base_gold']);self.assertIsNone(quantity('?'));self.assertIsNone(quantity('——'))
        with self.assertRaises(AssertionError):quantity('1~0')
    def test_portal_inherits_only_documented_normal_emergency_column(self):
        self.assertEqual(model.stage_reference('ro6_n_1_2','map','portal')['conditional_base_gold'],{'minimum':1,'maximum':1});self.assertIsNone(model.stage_reference('ro6_t_1','event','portal')['conditional_base_gold']);self.assertIsNone(model.stage_reference('ro6_n_7_1','map','portal')['conditional_base_gold'])
    def test_side_path_basic_unknown_bonus_only_normal_reference(self):
        r=model.stage_reference('ro6_n_4_1_dlc1','map','side_path');self.assertIsNone(r['conditional_base_gold']);self.assertEqual(r['documented_side_path_bonus']['random_relics'],1);self.assertIsNone(r['actual_reward_total']);self.assertIsNone(model.stage_reference('ro6_e_7_1','map','side_path')['documented_side_path_bonus']);self.assertIsNone(model.stage_reference('ro6_n_4_1_dlc1','event','side_path')['documented_side_path_bonus'])
    def test_unsupported_context_and_unrecognised_identity(self):
        for entry,region in [('x','catalog'),('map','floor7')]:
            with self.assertRaises(ValueError):model.stage_reference('ro6_t_1',entry,region)
        self.assertIsNone(model.stage_reference('made-up'))
    def test_actual_pinned_source_bytes_corruption_invalidates_warm_reference(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p=root/model.PACK/'settlement-441984-excerpt.md';raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet());p.write_bytes(raw);self.assertIsNotNone(model.packet())

if __name__=='__main__':unittest.main()
