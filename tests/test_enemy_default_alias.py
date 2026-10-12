"""Fixed source constructor/alias inputs qualify real previews and targets."""
import copy,json,math,unittest
from pathlib import Path
from unittest.mock import patch
from rouge.enemy_panel import enemy_panel_reference,panel_data
from rouge.enemy_skills import enemy_skill_reference
from rouge.enemy_reference_construction import source_path,compiled_identity,construction_data
from rouge.battle_preview import battle_data,enemy_preview,enemy_text
from rouge.damage import calculate_damage
from rouge.enemy_configuration import compiled_configuration
from rouge.enemy_sp_reference import compiled_sp_reference

SID='ro6_n_2_3';EID='enemy_2133_shdopl_lancer'
def fixed_target(sid=SID,eid=EID,level=0):return {'stage_id':sid,'enemy_id':eid,'level':level}
def fixture(mode=True,present=True,exact=False):
    return {'scope':'fixture','source':{'game_commit':'fixed','enemy_database':{},'stages':{'stage':{}}},
        'attribute_fields':['maxHp','atk','def','magicResistance','spRecoveryPerSec','stunImmune'], 'metadata_fields':['lifePointReduce'],
        'definitions':{'enemy':{'0':{'source_selector':'db0','fields':{'attributes.atk':999,'attributes.def':888}}}},
        'bindings':{'stage':{'enemy@'+str(0 if exact else 1):{'use_db':mode,'overwritten_data_present':present,'reference_id':'enemy',
            'source_index':0,'identity_overrides':{'prefabKey':'base','name':'enemy'},'overrides':{'attributes.maxHp':1000,'attributes.atk':100}}}}}
class EnemyDefaultAliasTests(unittest.TestCase):
    def test_all_fixed_modes_and_missing_exact_levels_are_not_conflated(self):
        d=panel_data();counts={'database':0,'stage_constructor':0};missing=[]
        for sid,rows in d['bindings'].items():
            for key,binding in rows.items():
                eid,level=key.rsplit('@',1);p=enemy_panel_reference(sid,eid,int(level));path=p['construction_reference']
                counts[path['mode']]+=1;self.assertIs(type(binding['use_db']),bool)
                self.assertEqual(path['database_records_used'],binding['use_db'] and p['exact_level_present'])
                if not p['exact_level_present']:
                    self.assertFalse(binding['use_db']);self.assertTrue(p['compiled_result_available']);missing.append((sid,eid,int(level)))
                self.assertIsNone(p['complete_effective_panel']);self.assertFalse(p['actual_gameplay_verified'])
        self.assertEqual(counts,{'database':1028,'stage_constructor':59});self.assertEqual(len(missing),58)
    def test_true_missing_grade_remains_denied_despite_lower_db_and_explicit_overrides(self):
        with patch('rouge.enemy_panel.panel_data',return_value=fixture(True,True,False)):
            p=enemy_panel_reference('stage','enemy',1)
        self.assertFalse(p['compiled_result_available']);self.assertEqual(p['source_state'],'unavailable_exact_database_level')
        self.assertTrue(all(v is None for v in p['attributes'].values()))
        self.assertEqual(p['source_projection']['attributes']['def'],888)
    def test_false_present_uses_no_db_even_when_exact_grade_exists(self):
        with patch('rouge.enemy_panel.panel_data',return_value=fixture(False,True,True)):
            p=enemy_panel_reference('stage','enemy',0)
        self.assertTrue(p['exact_level_present']);self.assertTrue(p['compiled_result_available'])
        self.assertEqual(p['attributes']['atk'],100);self.assertIsNone(p['attributes']['def'])
        self.assertEqual(p['attributes']['magicResistance'],0)
        self.assertNotEqual(p['field_provenance']['attributes.def']['state'],'database_definition')
        self.assertFalse(p['construction_reference']['database_records_used'])
    def test_false_missing_overwrite_denied_and_unstated_mode_not_guessed(self):
        for mode,present in [(False,False),(None,True),('false',True),(0,True)]:
            with patch('rouge.enemy_panel.panel_data',return_value=fixture(mode,present,True)):
                p=enemy_panel_reference('stage','enemy',0)
            self.assertFalse(p['compiled_result_available']);self.assertTrue(all(v is None for v in p['attributes'].values()))
    def test_compiled_key_and_alias_are_independent_of_name_and_description(self):
        p=enemy_panel_reference(SID,EID,0);i=p['compiled_identity']
        self.assertEqual(i['prefab_key'],'enemy_2133_shdopl');self.assertEqual(i['alias'],EID)
        self.assertEqual(i['key_in_level_reference'],EID);self.assertEqual(i['name'],'空植体')
        path=source_path({'use_db':False,'overwritten_data_present':True},False)
        identity=compiled_identity({'reference_id':'different','identity_overrides':{'prefabKey':'base','name':'different'}},path)
        self.assertEqual(identity['alias'],'different');self.assertEqual(identity['prefab_key'],'base')
        same=compiled_identity({'reference_id':'base','identity_overrides':{'prefabKey':'base'}},path)
        self.assertFalse(same['alias_written']);self.assertIsNone(same['alias']);self.assertFalse(same['alias_not_written_default_known'])
    def test_56_new_targets_calculate_and_two_missing_defenses_stay_denied(self):
        available=missing=0
        for sid,rows in panel_data()['bindings'].items():
            for key,b in rows.items():
                if b['use_db']:continue
                eid,level=key.rsplit('@',1);level=int(level);p=enemy_panel_reference(sid,eid,level)
                if p['exact_level_present']:continue
                target=fixed_target(sid,eid,level)
                if p['attributes']['def'] is None:
                    with self.assertRaisesRegex(ValueError,'不能填零'):
                        calculate_damage({'operator':'mechanist','skill':1,'target_enemy':target})
                    missing+=1
                else:
                    r=calculate_damage({'operator':'mechanist','skill':1,'target_enemy':target,
                        'run_config':{'difficulty':{'value':0},'zone':{'id':'zone_2'}}})
                    self.assertEqual(r['run_resolution']['enemy']['fixed_source_qualification']['state'],'stage_constructor_overrides_available')
                    self.assertEqual(r['run_resolution']['enemy']['reference_stats']['def'],p['attributes']['def'])
                    available+=1
        self.assertEqual((available,missing),(56,2))
    def test_real_target_source_overwrites_stale_manual_defense_and_matches_existing_arithmetic(self):
        r=calculate_damage({'operator':'mechanist','skill':1,'target_enemy':fixed_target(),
            'enemy_defense':99999,'enemy_resistance':99,'run_config':{'difficulty':{'value':0},'zone':{'id':'zone_2'}}})
        direct=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':200,'enemy_resistance':20})
        self.assertAlmostEqual(r['total_damage'],direct['total_damage']);self.assertEqual(r['run_resolution']['enemy']['stats']['def'],200)
        self.assertEqual(r['run_resolution']['enemy']['stats']['maxHp'],3600)
    def test_unwritten_fields_remain_unknown_while_explicit_ctor_zero_is_kept(self):
        p=enemy_panel_reference('ro6_n_3_2','enemy_1303_mhshep_2b',0)
        self.assertIsNone(p['attributes']['def']);self.assertEqual(p['attributes']['magicResistance'],0)
        self.assertEqual(p['field_provenance']['attributes.magicResistance']['state'],'constructor_explicit_default')
        with patch('rouge.enemy_panel.panel_data',return_value=fixture(False,True,True)):
            unwritten=enemy_panel_reference('stage','enemy',0)
        self.assertIsNone(unwritten['attributes']['stunImmune'])
        self.assertNotIn('attributes.def',construction_data()['defaults'])
    def test_partial_preview_applies_known_environment_without_authorizing_complete_target(self):
        e=enemy_preview('ro6_n_3_2','enemy_1303_mhshep_2b',0,{'difficulty':{'value':0},'zone':{'id':'zone_3'}})
        env=e['environment'];self.assertIsNotNone(env);self.assertTrue(env['panel_only'])
        self.assertEqual(env['stats']['maxHp'],4500);self.assertEqual(env['stats']['atk'],224)
        self.assertIsNone(env['stats']['def']);self.assertEqual(env['stats']['magicResistance'],0)
        text=enemy_text(e);self.assertIn('预计防御：未知',text);self.assertIn('生命值已证分项：4500',text)
        self.assertIn('防御已证分项：未知',text);self.assertNotIn('https://',text)
    def test_false_nonnull_sp_whole_write_is_known_without_constructor_pointer_baseline(self):
        count=0
        for sid,rows in panel_data()['bindings'].items():
            for key,b in rows.items():
                if b['use_db']:continue
                eid,level=key.rsplit('@',1);q=enemy_skill_reference(sid,eid,int(level));r=q['compiled_sp_reference']
                raw=q['stage_overrides'].get('spData')
                if raw is not None:
                    self.assertEqual(r['configuration'],raw);self.assertEqual(r['state'],'compiled_configuration_available')
                    self.assertEqual(r['applied_source']['origin'],'stage_override')
                    self.assertEqual(r['initialization_reference']['path'],'explicit_record_conversion');count+=1
                else:
                    self.assertIsNone(r['configuration']);self.assertEqual(r['state'],'constructor_sp_baseline_unknown')
                    self.assertEqual(r['initialization_reference']['state'],'unavailable_compiled_configuration')
                self.assertIsNone(r['first_activation_seconds']);self.assertIsNone(r['complete_cycle_seconds'])
        self.assertEqual(count,43)
    def test_false_skill_baseline_unknown_no_database_skill_leak(self):
        q=enemy_skill_reference('ro6_b_3_b','enemy_2154_shdfb',0);r=q['compiled_configuration']
        self.assertEqual(r['state'],'constructor_configuration_baseline_unknown');self.assertIsNone(r['configuration'])
        self.assertEqual(r['source_written_configuration'],q['stage_overrides'])
        self.assertFalse(r['compiled_inheritance_resolved']);self.assertIsNone(r['effective_skill_damage'])
        self.assertIsNone(r['current_runtime_controller']);self.assertFalse(q['construction_reference']['database_records_used'])
    def test_returned_fields_do_not_mutate_source_tables_or_later_query(self):
        before=copy.deepcopy(panel_data());r=enemy_panel_reference(SID,EID,0)
        r['attributes']['maxHp']=0;r['compiled_identity']['prefab_key']='wrong';r['construction_reference']['compiled_result_available']=False
        self.assertEqual(panel_data(),before);again=enemy_panel_reference(SID,EID,0)
        self.assertEqual(again['attributes']['maxHp'],6000);self.assertEqual(again['compiled_identity']['prefab_key'],'enemy_2133_shdopl')
    def test_partial_preview_option_is_explicit_boolean_and_not_a_damage_scenario_escape(self):
        from rouge.run_modifiers import prepare_run
        from rouge.enemy_environment import resolve_enemy
        for value in (None,0,1,'false',[]):
            with self.assertRaisesRegex(ValueError,'布尔值'):prepare_run({},enemy_panel_only=value)
            with self.assertRaisesRegex(ValueError,'布尔值'):resolve_enemy({}, {},panel_only=value)
        with self.assertRaisesRegex(ValueError,'不能填零'):
            calculate_damage({'operator':'mechanist','skill':1,'enemy_panel_only':True,
                'target_enemy':fixed_target('ro6_n_3_2','enemy_1303_mhshep_2b')})
    def test_partial_preview_does_not_admit_invalid_known_attributes(self):
        from rouge.run_modifiers import prepare_run
        for value in (-1,True,float('nan'),float('inf'),'200'):
            p=enemy_panel_reference(SID,EID,0);p['attributes']['def']=value
            with patch('rouge.enemy_panel.enemy_panel_reference',return_value=p):
                with self.assertRaisesRegex(ValueError,'不能填零'):
                    prepare_run({'operator':'mechanist','target_enemy':fixed_target()},enemy_panel_only=True)
if __name__=='__main__':unittest.main()
