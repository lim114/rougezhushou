from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import current_enemy_spawns as model,current_battle_reference as battle
from scripts.build_current_enemy_spawns_371 import build
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CurrentEnemySpawns371Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=battle.packet();assert cls.current
        cls.stage=battle.stage_reference('ro6_n_1_1');assert cls.stage
    def test_exact_all184_levels2060_bindings_and7696_direct_records(self):
        blobs,counts=build();self.assertEqual(counts,{'stages':184,'enemy_references':2060,'spawn_records':7696,'no_direct_spawn_references':110})
        for n,b in blobs.items():self.assertEqual((ROOT/n).read_bytes(),b)
    def test_all_direct_relationships_derive_from_original_complete_queues(self):
        checked=0
        for sid,s in self.current['version']['current']['details']['stages'].items():
            level=self.current['inputs']['levels']['levels/'+s['levelId'].lower()+'.json'];enemies=battle.enemy_records(level,self.current);actions=[]
            for q in battle.queues(level):
                for i,a in enumerate(q['actions']):actions.append({'key':str(len(actions)),'raw':a,'queue':{k:v for k,v in q.items()if k!='actions'},'action_index':i+1,'source_selector':q['source_selector']+f'.actions[{i}]','enemy_candidates':[e for e in enemies if e['id']==a.get('key')]if a['actionType']=='SPAWN'else[]})
            fake={'id':sid,'name':s['name'],'enemies':enemies,'actions':actions,'level_key':'levels/'+s['levelId'].lower()+'.json','source':{},'source_identity':self.current['identity']}
            for enemy in enemies:
                result=model._derive(fake,enemy['key']);expected=[a['key']for a in actions if a['raw']['actionType']=='SPAWN'and a['raw']['key']==enemy['id']]
                self.assertEqual([e['key']for e in result['entries']],expected);self.assertEqual(result['enemy']['raw_binding'],enemy['raw_binding']);checked+=1
        self.assertEqual(checked,2060)
    def test_main_branch_filters_keep_order_and_no_automatic_selection(self):
        result=model._derive(self.stage,'0');a=model.rows(result,'main');b=model.rows(result,'branch');self.assertEqual(len(a)+len(b),len(result['entries']));self.assertEqual(model.rows(result,'bad'),[])
    def test_missing_direct_spawn_is_not_absence_claim(self):
        fake=deepcopy(self.stage);fake['actions']=[];r=model._derive(fake,'0');self.assertEqual(r['entries'],[]);self.assertIn('不表示它不会出现',model.NOTICE);self.assertIn('不能据此排除',model.player_text(r))
    def test_duplicate_id_candidates_are_preserved_without_level_guess(self):
        fake=deepcopy(self.stage);e=deepcopy(fake['enemies'][0]);e['key']='extra';e['level']=99;e['raw_binding']['level']=99;fake['enemies'].append(e)
        for a in fake['actions']:
            if a['raw']['actionType']=='SPAWN'and a['raw']['key']==e['id']:a['enemy_candidates'].append(deepcopy(e))
        r=model._derive(fake,'extra');self.assertTrue(r['entries']);self.assertTrue(all(not row['exact_level_selected']for row in r['entries']));self.assertIn('关联多个精确引用',model.player_text(r,r['entries'][0]))
    def test_same_name_different_id_is_not_direct_relation(self):
        fake=deepcopy(self.stage);fake['enemies'][0]['id']='unmatched';self.assertEqual(model._derive(fake,'0')['entries'],[])
    def test_empty_and_activation_are_not_enemy_spawn_entries(self):
        r=model._derive(self.stage,'0');self.assertTrue(all(e['action']['raw']['actionType']=='SPAWN'for e in r['entries']))
    def test_exact_action_resolve_and_stale_result_refused(self):
        r=model.stage_reference('ro6_n_1_1','0');self.assertTrue(r['entries']);key=r['entries'][0]['key'];self.assertEqual(model.resolve_action(r,key)['action_key'],key);bad=deepcopy(r);bad['enemy']['name']='forged';self.assertIsNone(model.resolve_action(bad,key));self.assertIsNone(model.resolve_action(r,'999999'))
    def test_bad_inputs_and_source_loss_fail_closed(self):
        for args in((None,'0'),('missing','0'),('ro6_n_1_1',0),('ro6_n_1_1','9999')):self.assertIsNone(model.stage_reference(*args))
        with patch.object(model,'evidence',return_value=None):self.assertIsNone(model.stage_reference('ro6_n_1_1','0'))
        with patch.object(battle,'packet',return_value=None):self.assertIsNone(model.stage_reference('ro6_n_1_1','0'))
    def test_actual_values_and_final_panel_remain_unknown(self):
        r=model.stage_reference('ro6_n_1_1','0')
        for k in('actual_occurrence','actual_count','absolute_time','actual_path','expected_stats'):self.assertIsNone(r[k])
        self.assertFalse(r['run_updated']);self.assertFalse(r['actual_server_verified'])
    def test_position_uses_existing_exact_action_guard(self):
        r=model.stage_reference('ro6_n_1_1','0');key=r['entries'][0]['key'];p=model.position_reference(r,key);self.assertIsNotNone(p);self.assertEqual(p['action_key'],key)
        with patch('rouge.current_action_positions.reference',return_value=None):self.assertIsNone(model.position_reference(r,key))
    def test_player_text_keeps_seconds_unknown_global_clock_and_count_scope(self):
        r=model._derive(self.stage,'0');text=model.player_text(r,r['entries'][0]);self.assertIn('不是实际出场数量',text);self.assertIn('准确时刻：未知',text);self.assertIn('秒',text);self.assertIn('条件',text)
