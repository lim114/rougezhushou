"""Complete fixed enemy panel coverage without manufacturing runtime behavior."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from rouge.battle_preview import battle_data,enemy_preview,enemy_text
from rouge.enemy_panel import panel_data,enemy_panel_reference,enemy_panel_text

SID='ro6_n_1_2';EID='enemy_1093_ccsbr'

def fixture():
    return {'scope':'fixture','source':{'game_commit':'fixed','enemy_database':{'url':'public'},
        'stages':{'stage':{'url':'stage'}}},
        'attribute_fields':['atk','damageHitratePhysical','spRecoveryPerSec'],
        'metadata_fields':['lifePointReduce','notCountInTotal','enemyTags'],
        'definitions':{'enemy':{
            '0':{'source_selector':'$.enemies[2].Value[0].enemyData','fields':{
                'attributes.atk':100,'attributes.spRecoveryPerSec':0,
                'metadata.lifePointReduce':0,'metadata.notCountInTotal':False,
                'metadata.enemyTags':[]}},
            '1':{'source_selector':'$.enemies[2].Value[1].enemyData','fields':{'attributes.atk':120}},
            '2':{'source_selector':'$.enemies[2].Value[2].enemyData','fields':{'attributes.damageHitratePhysical':.5}}}},
        'bindings':{'stage':{'enemy@1':{'source_index':3,'overrides':{'attributes.atk':150}}}}}

class EnemyPanelReferenceTests(unittest.TestCase):
    def test_complete_pinned_field_coverage_preserves_all_existing_panel_fields(self):
        data=panel_data();self.assertEqual(len(data['attribute_fields']),32)
        self.assertEqual(len(data['metadata_fields']),6)
        count=0
        for sid,stage in battle_data()['stages'].items():
            for e in stage['enemies']:
                ref=enemy_panel_reference(sid,e['id'],e['level'])
                self.assertEqual(set(ref['attributes']),set(data['attribute_fields']))
                for key,value in {**e['reference_stats'],**e['immunity_reference']}.items():
                    self.assertEqual(ref['source_projection']['attributes'][key],value,(sid,e['id'],key))
                if not ref['exact_level_present']:
                    self.assertTrue(all(v is None for v in ref['attributes'].values()))
                    self.assertFalse(ref['compiled_database_result_available'])
                self.assertIsNone(ref['complete_effective_panel'])
                self.assertFalse(ref['actual_gameplay_verified']);count+=1
        self.assertEqual(count,1087)

    def test_explicit_zero_false_and_empty_values_do_not_become_unknown(self):
        with patch('rouge.enemy_panel.panel_data',return_value=fixture()):
            r=enemy_panel_reference('stage','enemy',1)
        self.assertEqual(r['attributes']['spRecoveryPerSec'],0)
        self.assertEqual(r['metadata']['lifePointReduce'],0)
        self.assertIs(r['metadata']['notCountInTotal'],False)
        self.assertEqual(r['metadata']['enemyTags'],[])
        self.assertEqual(r['field_provenance']['metadata.lifePointReduce']['state'],'database_definition')

    def test_last_explicit_level_and_stage_write_keep_the_actual_source(self):
        with patch('rouge.enemy_panel.panel_data',return_value=fixture()):
            r=enemy_panel_reference('stage','enemy',1)
        self.assertEqual(r['attributes']['atk'],150)
        row=r['field_provenance']['attributes.atk']
        self.assertEqual(row['state'],'stage_override')
        self.assertEqual(row['source_selector'],'$.enemyDbRefs[3].overwrittenData.attributes.atk.m_value')
        self.assertIsNone(r['attributes']['damageHitratePhysical'])
        self.assertEqual(r['field_provenance']['attributes.damageHitratePhysical']['state'],'undefined')
        self.assertEqual(r['field_provenance']['attributes.spRecoveryPerSec']['source_level'],0)

    def test_missing_exact_level_is_not_filled_from_future_definitions(self):
        data=fixture();data['definitions']['enemy'].pop('1')
        with patch('rouge.enemy_panel.panel_data',return_value=data):
            r=enemy_panel_reference('stage','enemy',1)
        self.assertFalse(r['exact_level_present'])
        self.assertIsNone(r['attributes']['damageHitratePhysical'])
        self.assertIsNone(r['attributes']['atk'])
        self.assertEqual(r['source_projection']['attributes']['atk'],150)

    def test_identity_and_level_are_bound_without_defaulting(self):
        for args in ((SID,EID,True),(SID,EID,-1),(SID,EID,0.),(SID,EID,None),
            ('unknown',EID,0),(SID,'unknown',0),(SID,EID,999),(SID,[],0),([],EID,0)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):enemy_panel_reference(*args)

    def test_result_and_source_are_independent_copies(self):
        data=fixture();before=copy.deepcopy(data)
        with patch('rouge.enemy_panel.panel_data',return_value=data):
            r=enemy_panel_reference('stage','enemy',1)
            r['metadata']['enemyTags'].append('changed')
            r['source']['stage']['url']='changed'
            self.assertEqual(enemy_panel_reference('stage','enemy',1)['metadata']['enemyTags'],[])
        self.assertEqual(data,before)

    def test_actual_preview_and_text_expose_new_fields_separately_from_predictions(self):
        entry=enemy_preview(SID,EID,0)
        r=entry['fixed_panel_reference'];text=enemy_text(entry)
        self.assertEqual(r['attributes']['atk'],290)
        self.assertIn('【扩展属性预测】',text)
        self.assertIn('预计技力回复、嘲讽、物理/法术命中率',text)
        self.assertIn('漏怪扣血、分类和敌人计数适用性：未知',text)
        self.assertNotIn('【固定资料面板】',text)
        self.assertNotIn('生命：2600',text)
        self.assertNotIn('攻击：290',text)
        self.assertNotIn('每秒技力回复参数：',text)
        self.assertIn('预计攻击间隔：未知',text)
        self.assertNotIn('source_selector',text);self.assertNotIn('maxHp',text)
        self.assertNotIn('https://',text)
        technical=enemy_text(entry,technical=True)
        self.assertIn('完整固定属性字段：',technical)
        self.assertIn('各字段明确来源：',technical)

    def test_run_changes_do_not_rewrite_fixed_source_fields_or_combat_totals(self):
        a=enemy_preview(SID,EID,0,{'difficulty':{'value':0},'zone':{'id':'zone_3'}})
        b=enemy_preview(SID,EID,0,{'difficulty':{'value':15},'zone':{'id':'zone_3'}})
        self.assertEqual(a['fixed_panel_reference'],b['fixed_panel_reference'])
        self.assertNotEqual(a['environment']['stats']['maxHp'],b['environment']['stats']['maxHp'])
        self.assertFalse(a['skill_reference']['inheritance_resolved'])
        self.assertIsNone(a['skill_reference']['effective_skill_damage'])

    def test_numeric_and_boolean_metadata_are_not_reinterpreted_as_actual_events(self):
        with patch('rouge.enemy_panel.panel_data',return_value=fixture()):
            r=enemy_panel_reference('stage','enemy',1)
        ordinary=enemy_panel_text(r)
        self.assertNotIn('扣除关卡生命参数：0',ordinary)
        text=enemy_panel_text(r,technical=True)
        self.assertIn('扣除关卡生命参数：0',text)
        self.assertIn('否（明确字段）',text)
        self.assertIsNone(r['complete_effective_panel'])
        self.assertTrue(any('通过终点' in s for s in r['limits']))

    def test_ordinary_preview_keeps_only_environment_predictions_not_fixed_white_values(self):
        entry=enemy_preview(SID,EID,0,{'difficulty':{'value':15},'zone':{'id':'zone_3'}})
        text=enemy_text(entry)
        self.assertIn('预计生命值：5840.64',text)
        self.assertIn('预计攻击力：501.12',text)
        for raw in ('生命：2600','攻击：290','【固定资料面板】','扣除关卡生命参数：'):
            self.assertNotIn(raw,text)
        raw=enemy_text(entry,technical=True)
        self.assertIn('生命：2600',raw)
        self.assertIn('攻击：290',raw)

if __name__=='__main__':unittest.main()
