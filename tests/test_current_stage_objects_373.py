from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import unittest,json
from rouge import current_stage_objects as model,current_battle_reference as battle
from scripts.build_current_stage_objects_373 import build
ROOT=Path(__file__).resolve().parents[1]
class CurrentStageObjects373Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ref=model.packet();assert cls.ref;cls.stage=battle.stage_reference('ro6_n_1_1');assert cls.stage
    def test_all_original_instances_cards_entity_types_and_exact_activation_scope(self):
        blobs,counts=build();self.assertEqual(counts,{'instance':1652,'without_direct_activations':540,'with_direct_activations':1126,'card':14,'stages':184,'entity_types':37,'skill_records':34})
        for name,raw in blobs.items():self.assertEqual((ROOT/name).read_bytes(),raw)
    def test_all1666_declaration_records_bind_original_kind_position_and_alias(self):
        current=battle.packet();inventory=self.ref['inventory'];checked=0
        for sid,entry in inventory['stages'].items():
            level=current['inputs']['levels'][entry['level_key']];original=[]
            for container in('predefines','hardPredefines'):
                for field in('characterInsts','tokenInsts','characterCards','tokenCards'):
                    for i,raw in enumerate((level.get(container)or{}).get(field)or[]):original.append((f'$.{container}.{field}[{i}]',(raw.get('inst')or{}).get('characterKey')or raw.get('characterKey'),'instance'if field.endswith('Insts')else'card'))
            self.assertEqual([(r['key'],r['entity_id'],r['kind'])for r in entry['entries']],original);checked+=len(original)
        self.assertEqual(checked,1666)
    def test_37_complete_original_entities_and_34_skills_source_pinned(self):
        self.assertEqual(len(self.ref['selected']['characters']),37);self.assertEqual(len(self.ref['selected']['skills']),34);self.assertEqual(self.ref['selected']['characters']['trap_325_shfort']['name'],'“危朽”');audit=json.loads((ROOT/model.PACK/'source-extraction-audit.json').read_bytes());self.assertTrue(audit['complete_selected_records_equal_originals']);self.assertFalse(audit['server_verified'])
    def test_no_description_placeholder_or_markup_leaks_to_default_player_text(self):
        r=model.stage_reference('ro6_n_1_1');row=next(e for e in r['entries']if e['entity_id']=='trap_011_ore');text=model.player_text(r,row);self.assertIn('源石祭坛',text);self.assertIn('真实伤害',text);self.assertNotIn('{value}',text);self.assertNotIn('<@',text);self.assertIn('具体数值待核对',text)
    def test_same_name_independent_object_ids_kept_separate(self):
        chars=self.ref['selected']['characters'];self.assertEqual(chars['trap_345_shadvt']['name'],chars['trap_349_shadvt2']['name']);self.assertNotEqual(chars['trap_345_shadvt']['skills'][0]['skillId'],chars['trap_349_shadvt2']['skills'][0]['skillId'])
    def test_exact_activation_links_do_not_infer_visible_or_active_state(self):
        r=model.stage_reference('ro6_n_1_1');row=next(e for e in r['entries']if e['key']=='$.predefines.tokenInsts[0]');self.assertEqual([a['key']for a in row['activation_actions']],['4']);self.assertIsNone(row['actual_active']);self.assertTrue(row['raw']['hidden']);self.assertIn('不证明当前可见或已经启用',model.player_text(r,row))
    def test_missing_activation_does_not_exclude_automatic_or_script_effect(self):
        r=model.stage_reference('ro6_n_1_1');row=next(e for e in r['entries']if e['entity_id']=='trap_011_ore');self.assertEqual(row['activation_actions'],[]);self.assertIn('不等于不会出现或生效',model.player_text(r,row))
    def test_cards_keep_initial_count_reference_and_no_map_position(self):
        r=model.stage_reference('ro6_n_2_2');row=next(e for e in r['entries']if e['kind']=='card');self.assertEqual(row['name'],'罗德岛临时雇员');self.assertIn('5；不作为当前库存',model.player_text(r,row));self.assertIsNone(model.position_reference(r,row['key']));self.assertEqual(row['activation_actions'],[])
    def test_filters_are_independent_exact_branches_and_intersections(self):
        r=model.stage_reference('ro6_n_1_1');self.assertTrue(model.rows(r,'祭坛',kind='instance',link='unlinked'));self.assertEqual(model.rows(r,'祭坛',link='linked'),[]);self.assertEqual(model.rows(r,kind='card'),[]);self.assertEqual(model.rows(r,kind='guess'),[])
    def test_multiple_alias_targets_stay_distinct_without_arbitrary_position(self):
        fake=deepcopy(self.stage);raw=deepcopy(fake['level']['predefines']['tokenInsts'][0]);fake['level']['predefines']['tokenInsts'].append(raw);selector='$.predefines.tokenInsts['+str(len(fake['level']['predefines']['tokenInsts'])-1)+']'
        for a in fake['actions']:
            if a['raw']['actionType']=='ACTIVATE_PREDEFINED'and a['raw']['key']==raw['alias']:a['predefined_candidates'].append({'source_selector':selector,'raw':raw})
        r=model._derive(fake,self.ref);copies=[e for e in r['entries']if e['raw'].get('alias')==raw['alias']];self.assertEqual(len(copies),2);self.assertNotEqual(copies[0]['key'],copies[1]['key']);self.assertEqual([a['key']for a in copies[0]['activation_actions']],[a['key']for a in copies[1]['activation_actions']])
    def test_exact_resolve_and_forged_selection_rejected(self):
        r=model.stage_reference('ro6_n_1_1');key=r['entries'][0]['key'];action=r['entries'][0]['activation_actions'][0]['key'];self.assertIsNotNone(model.resolve(r,key,action));self.assertIsNone(model.resolve(r,key,'999999'));bad=deepcopy(r);bad['entries'][0]['raw']['hidden']=False;self.assertIsNone(model.resolve(bad,key))
    def test_bad_source_invalid_type_and_unknown_stage_fail_closed(self):
        self.assertIsNone(model.stage_reference(None));self.assertIsNone(model.stage_reference('missing'))
        with patch.object(model,'packet',return_value=None):self.assertIsNone(model.stage_reference('ro6_n_1_1'))
    def test_instance_position_matches_exact_nominal_cell_and_known_map_guard(self):
        r=model.stage_reference('ro6_n_1_1');key=r['entries'][0]['key'];p=model.position_reference(r,key);self.assertIsNotNone(p);self.assertEqual(p['key'],key);self.assertIsNone(p['actual_position']);self.assertIsNone(p['actual_active']);self.assertIsNone(p['actual_path'])
    def test_original_stats_never_rendered_as_current_player_panel(self):
        r=model.stage_reference('ro6_b_6');row=next(e for e in r['entries']if e['entity_id']=='trap_325_shfort');text=model.player_text(r,row);self.assertIn('灾厄之口',text);self.assertNotIn('maxHp',text);self.assertFalse(r['run_updated']);self.assertFalse(r['actual_server_verified'])
