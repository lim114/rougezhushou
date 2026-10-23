"""Candidate357 public-source tests; not executed during candidate preparation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_real_domain as model


def clone(root):
    for name in(model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())


class CurrentRealDomain357Tests(unittest.TestCase):
    def test_rebuild_all30_ideology_and4_policy_complete_exact_originals(self):
        result=subprocess.run([sys.executable,'-B','scripts/build_current_real_domain_357.py','--check'],cwd=model.ROOT,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        reference=model.reference();self.assertEqual(len(reference['rows']),34);self.assertIsNone(reference['selected'])
        current=model.version.packet()['current'];weather=current['modules']['weather']
        for row in reference['rows']:
            table=weather['mainWeatherData'if row['kind']=='idea'else'subWeatherData']
            self.assertEqual(row['original'],table[row['id']]);self.assertTrue(row['documented']['complete_table'])
            self.assertIsNone(row['actual_active']);self.assertIsNone(row['actual_affected_nodes'])
        self.assertEqual(len(model.reference(kind='idea')['rows']),30);self.assertEqual(len(model.reference(kind='policy')['rows']),4)
        self.assertEqual(len(reference['data']['documented']),14)
        for key in('actual_weather','actual_phase','actual_combination','actual_affected_nodes','actual_received','actual_eligible'):self.assertIsNone(reference[key])
        self.assertFalse(reference['calculation_applied']);self.assertFalse(reference['run_updated'])

    def test_exact_type_filter_and_independent_three_phases_not_stacked(self):
        for i in range(1,11):
            rows=model.reference(type_id=f'rogue_6_weather_{i}')['rows']
            self.assertEqual([row['level']for row in rows],[1,2,3]);self.assertEqual(len({row['name']for row in rows}),1)
        self.assertEqual(len(model.reference(query='储藏室')['rows']),3)
        self.assertEqual(model.reference(kind='policy',type_id='rogue_6_weather_1')['rows'],[])
        self.assertIsNone(model.reference('rogue_6_weather_1_a',kind='policy'))

    def test_normal_phase_boundaries_are_reference_not_live_generation(self):
        for grade,phase in[(0,None),(1,None),(2,1),(5,1),(6,2),(11,2),(12,3),(16,3)]:
            result=model.reference('rogue_6_weather_2_a',mode='NORMAL',difficulty=grade)
            self.assertEqual(result['comparison']['ordinary_phase'],phase)
            self.assertIsNone(result['actual_phase']);self.assertIsNone(result['actual_eligible'])
        result=model.reference('rogue_6_weather_2_a',mode='OTHER',difficulty=16)
        self.assertIsNone(result['comparison']['ordinary_phase']);self.assertEqual(result['comparison']['status'],'unknown')
        result=model.reference('rogue_6_weather_1_a',mode='NORMAL',difficulty=2,floor=1)
        fact=next(f for f in result['comparison']['facts']if f['name']=='不是第一主层');self.assertFalse(fact['matched'])

    def test_node_internal_and_passing_conditions_are_not_mutually_exclusive(self):
        for identity in('rogue_6_weather_2_a','rogue_6_subweather_1'):
            result=model.reference(identity,action='both',affected=True)
            fact=next(f for f in result['comparison']['facts']if f['name']=='进入与经过分别核对');self.assertTrue(fact['matched'])
        result=model.reference('rogue_6_subweather_1',action='enter')
        fact=next(f for f in result['comparison']['facts']if f['name']=='进入与经过分别核对');self.assertIsNone(fact['matched'])
        result=model.reference('rogue_6_weather_2_a',action='pass')
        fact=next(f for f in result['comparison']['facts']if f['name']=='进入与经过分别核对');self.assertFalse(fact['matched'])
        self.assertFalse(next(f for f in model.reference('rogue_6_weather_2_a',affected=False)['comparison']['facts']if f['name']=='节点是否受影响')['matched'])

    def test_hope_gain_pair_and_squad_immunity_exception_are_separate_facts(self):
        for paired,want in[(None,None),('rogue_6_subweather_1',False),(model.GAIN,True)]:
            result=model.reference('rogue_6_weather_8_a',paired=paired)
            fact=next(f for f in result['comparison']['facts']if f['name']=='仅配增益方针');self.assertIs(fact['matched'],want)
        result=model.reference(model.GAIN,paired='rogue_6_weather_2',squad='rogue_6_band_16')
        self.assertFalse(next(f for f in result['comparison']['facts']if f['name']=='仅配希望的沃土')['matched'])
        for squad in model.SQUADS:
            gain=model.reference(model.GAIN,paired=model.HOPE,squad=squad)
            self.assertTrue(next(f for f in gain['comparison']['facts']if f['name']=='文明开化方针例外')['matched'])
            negative=model.reference('rogue_6_subweather_1',squad=squad)
            self.assertIs(next(f for f in negative['comparison']['facts']if f['name']=='文明开化方针例外')['matched'],squad not in model.IMMUNE_SQUADS)
        early_gain=model.reference(model.GAIN,mode='NORMAL',difficulty=2,paired=model.HOPE)
        self.assertIsNone(next(f for f in early_gain['comparison']['facts']if f['name']=='常规自然生成难度')['matched'])

    def test_document_supplements_do_not_rewrite_originals_or_invent_effects(self):
        storage=model.reference('rogue_6_weather_5_a');row=storage['selected']
        self.assertNotIn('应急助力',row['original']['functionDesc']);self.assertIn('应急助力',row['documented']['stages']['1'])
        self.assertIn('不会因该实托邦消除而恢复栏位',model.player_text(storage))
        mist=model.player_text(model.reference('rogue_6_weather_9_c'))
        self.assertIn('不影响节点类型自身的揭示效果',mist);self.assertIn('可重复进入的节点在进入1次后',mist)
        gain=model.player_text(model.reference(model.GAIN));self.assertIn('不是当场增加源石锭',gain)
        aggressive=model.player_text(model.reference('rogue_6_subweather_3'));self.assertIn('最低降至1目标生命',aggressive)
        beautiful=model.player_text(model.reference('rogue_6_weather_10_b'));self.assertIn('具体触发',beautiful);self.assertIn('不等于不可选中、隐匿或无敌',beautiful)

    def test_precise_existing_event_entries_and_no_fabricated_phase(self):
        from rouge import current_vine_events as vine,current_resting as resting
        for key,provider,category,identity,type_id in[
            ('red_controller',vine,'choices','choice_ro6_normal3_1',model.HOPE),
            ('red_seed',vine,'choices','choice_ro6_normal3_2',model.HOPE),
            ('resting',resting,'scenes','scene_ro6_surprise_enter','rogue_6_weather_10')]:
            link=model.destination(key);self.assertEqual(link['target'],provider.locate(category,identity))
            target=model.locate(category,identity);self.assertEqual(target['type_id'],type_id)
            self.assertNotIn('row_id',target);self.assertIsNone(link['actual_trigger'])
        self.assertEqual(len(model.reference('rogue_6_weather_8_a')['related_origins']),2)
        self.assertEqual(len(model.reference('rogue_6_weather_10_a')['related_origins']),1)
        self.assertEqual(model.reference('rogue_6_weather_9_a')['related_origins'],[])
        self.assertIsNone(model.locate('relics','rogue_6_relic_artifact_5'));self.assertIsNone(model.destination(True))

    def test_every_manifest_member_real_damage_and_underlying_provider_loss(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    path=root/name;raw=path.read_bytes();self.assertIsNotNone(model.packet());path.write_bytes(raw+b'x')
                    self.assertIsNone(model.packet(),name);path.write_bytes(raw);self.assertIsNotNone(model.packet())
        from rouge import current_vine_events as vine,current_resting as resting
        for provider in(vine,resting):
            with patch.object(provider,'packet',return_value=None):self.assertIsNone(model.packet())

    def test_invalid_values_and_mutable_results_do_not_change_source_or_run(self):
        for kwargs in({'row_id':True},{'row_id':'rogue_6_weather_99_a'},{'kind':True},{'type_id':'bad'},
                       {'mode':False},{'difficulty':True},{'difficulty':17},{'floor':0},{'floor':True},
                       {'affected':1},{'action':'move'},{'squad':'rogue_6_band_1'},
                       {'paired':'rogue_6_weather_8_a'},
                       {'row_id':model.GAIN,'paired':'rogue_6_subweather_1'},
                       {'row_id':'rogue_6_weather_8_a','paired':'rogue_6_weather_2'},
                       {'query':None}):self.assertIsNone(model.reference(**kwargs))
        result=model.reference();result['rows'].clear();result['data']['links'].clear()
        self.assertEqual(len(model.reference()['rows']),34);self.assertEqual(len(model.reference()['data']['links']),3)


if __name__=='__main__':unittest.main()
