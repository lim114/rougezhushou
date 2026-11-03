import unittest
from copy import deepcopy
from rouge.catalog import catalog,stage_previews
from rouge.damage import calculate_damage
from rouge.enemy_comparison import compare_enemies,format_enemy_comparison

BASE={'operator':'mechanist','skill':3,'window_seconds':10}
def selection(sid):
    record=stage_previews()[sid]['possible_enemies'][0]
    return {'enemy_id':record['id'],'level':record['level']}
def preview():return {'stage_id':'ro6_n_1_1','enemies':[selection('ro6_n_1_1')],'grades':[4,5],'orb_mode':'unknown'}

class EnemyComparisonTests(unittest.TestCase):
    def test_grade5_life_threshold_and_existing_damage_engine(self):
        result=compare_enemies(BASE,preview());normal,increased=result['rows']
        self.assertAlmostEqual(increased['max_hp'],normal['max_hp']*1.3)
        self.assertEqual(increased['window_damage'],calculate_damage(increased['scenario'])['estimate']['skill']['window_damage'])
        self.assertEqual(increased['scenario']['run_config']['difficulty']['source'],'手动局外难度对照')

    def test_multi_targets_and_manual_panel_overridden_by_identity(self):
        data=preview();sid=data['stage_id'];records=stage_previews()[sid]['possible_enemies'][:2]
        data['enemies']=[{'enemy_id':r['id'],'level':r['level']} for r in records]
        result=compare_enemies({**BASE,'enemy_defense':99999,'enemy_resistance':99},data)
        self.assertEqual(len(result['rows']),len(records)*2)
        self.assertEqual(result['rows'][0]['defense'],records[0]['reference_stats']['def'])
        self.assertIn('候选',format_enemy_comparison(result));self.assertIn('已计修正',format_enemy_comparison(result))

    def test_preserves_input_zone_and_source_caches(self):
        scenario={**BASE,'run_config':{'zone':{'id':'zone_4','source':'public fixture'},'future':{'keep':True}}}
        data=preview();before=deepcopy((scenario,data,catalog(),stage_previews()))
        result=compare_enemies(scenario,data)
        self.assertEqual(result['rows'][0]['scenario']['run_config']['zone'],scenario['run_config']['zone'])
        self.assertEqual((scenario,data,catalog(),stage_previews()),before)

    def test_boss_reduction_and_unknown_dynamic_scripts_retained(self):
        for sid,p in stage_previews().items():
            bosses=[r for r in p['possible_enemies'] if r['level_type']=='BOSS']
            if bosses:break
        r=bosses[0];data={'stage_id':sid,'enemies':[{'enemy_id':r['id'],'level':r['level']}],'grades':[10,11],'orb_mode':'unknown'}
        result=compare_enemies(BASE,data)
        self.assertEqual(result['rows'][1]['enemy']['damage_factor'],.8)
        self.assertIn('实际死亡时间',format_enemy_comparison(result))

    def test_invalid_selection_and_bounds(self):
        for grades in ([],[True],[1.0],[16],[5,5],list(range(7))):
            with self.assertRaises(ValueError):compare_enemies(BASE,{**preview(),'grades':grades})
        for enemies in ([],[{'enemy_id':'not-stage-enemy','level':0}],[selection('ro6_n_1_1')]*2,[{'enemy_id':[],'level':0}]):
            with self.assertRaises(ValueError):compare_enemies(BASE,{**preview(),'enemies':enemies})
        with self.assertRaises(ValueError):compare_enemies(BASE,{**preview(),'orb_mode':'random'})
