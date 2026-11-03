from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_battle_reference as model
from scripts.build_current_battle_reference_314 import build
ROOT=Path(__file__).resolve().parents[1]

class CurrentBattleReference314Tests(unittest.TestCase):
    def test_selected_full_originals_equal_actual_pinned_cache_or_unavailable(self):
        ref=model.packet();self.assertIsNotNone(ref)
        cache=ROOT/'.cache/p3-expansion-314'
        if not cache.exists():self.skipTest('完整原件缓存不在此机，原始选择与下载核对不可计通过。')
        for name,pin in ref['selection']['original_sources'].items():
            raw=(cache/name).read_bytes();self.assertEqual(len(raw),pin['bytes']);self.assertEqual(sha256(raw).hexdigest(),pin['sha256'])
            if name.startswith('levels/obt/'):self.assertEqual(json.loads(raw),ref['inputs']['levels'][name])
        raw=json.loads((cache/'levels/enemydata/enemy_database.json').read_bytes());db={r['Key']:r['Value']for r in raw['enemies']}
        self.assertEqual(ref['inputs']['enemy_definitions'],{k:db[k]for k in ref['selection']['selected_enemy_ids']if k in db})
        hand=json.loads((cache/'excel/enemy_handbook_table.json').read_bytes())['enemyData']
        self.assertEqual(ref['inputs']['handbook'],{k:hand[k]for k in ref['selection']['selected_enemy_ids']if k in hand})

    def test_every184_exact_stage113_level_and_all_actions_are_preserved(self):
        ref=model.packet();self.assertEqual(len(ref['inputs']['levels']),113)
        # One bound packet reused for source-independent identity checks, not reparsing inputs184 times.
        with patch.object(model,'packet',return_value=ref):
            for sid,stage in ref['version']['current']['details']['stages'].items():
                r=model.stage_reference(sid);raw=ref['inputs']['levels']['levels/'+stage['levelId'].lower()+'.json']
                self.assertEqual(r['stage'],stage);self.assertEqual(r['level'],raw)
                self.assertEqual([e['raw_binding']for e in r['enemies']],raw['enemyDbRefs'])
                expected=[a for q in model.queues(raw)for a in q['actions']]
                self.assertEqual([a['raw']for a in r['actions']],expected)
                self.assertEqual(len({a['key']for a in r['actions']}),len(expected))
                for a in r['actions']:
                    self.assertIsNone(a['absolute_time']);self.assertIsNone(a['actual_occurrence']);self.assertIsNone(a['position_on_original']);self.assertIsNone(a['probability'])
                self.assertEqual(r['image'],ref['version']['images']['images'][sid]);self.assertFalse(r['map_projection_verified'])
        self.assertEqual(build(ROOT),(ROOT/model.MANIFEST).read_bytes())

    def test_normal_elite_and_dlc_same_name_stay_exact_separate_and_difficulty_retained(self):
        a=model.stage_reference('ro6_n_4_1');b=model.stage_reference('ro6_n_4_1_dlc1');c=model.stage_reference('ro6_e_4_1_dlc1')
        self.assertEqual(a['name'],b['name']);self.assertNotEqual(a['level_key'],b['level_key'])
        self.assertEqual(b['level_key'],c['level_key']);self.assertNotEqual(b['id'],c['id']);self.assertEqual(c['stage']['difficulty'],'FOUR_STAR')
        self.assertIn('紧急作战',model.summary_text(c));self.assertFalse(c['numeric_environment_migrated'])
        self.assertNotEqual(a['image']['git_blob_sha1'],b['image']['git_blob_sha1'])

    def test_independent_constructor_does_not_borrow_db_name_mechanics_or_zero_placeholders(self):
        ref=model.packet();copy=deepcopy(ref);copy['inputs']['enemy_definitions']={'synthetic':[{'level':0,'enemyData':{'name':{'m_defined':True,'m_value':'借用名'},'levelType':{'m_defined':True,'m_value':'BOSS'}}}]};copy['inputs']['handbook']={'synthetic':{'name':'图鉴名','enemyLevel':'BOSS','abilityList':[{'text':'不能借用'}]}}
        level={'enemyDbRefs':[{'id':'synthetic','useDb':False,'level':0,'overwrittenData':{'name':{'m_defined':True,'m_value':'独立单位'},'levelType':{'m_defined':False,'m_value':'NORMAL'}}}]}
        e=model.enemy_records(level,copy)[0];self.assertEqual(e['name'],'独立单位');self.assertIsNone(e['tier']);self.assertFalse(e['handbook_applied']);self.assertEqual(e['abilities'],[]);self.assertIsNone(e['expected_stats'])

    def test_all_images_are_exact_and_failed_missing_images_stay_unknown(self):
        ref=model.packet();images=ref['portraits'];self.assertEqual(len(images['images']),354)
        for info in images['images'].values():self.assertIsNotNone(model.picture_bytes(info))
        self.assertEqual({v['identity']for v in images['failures']},{'enemy_1250_lyengs_2'})
        self.assertEqual(len(images['missing_exact_ids']),33)
        no_image=deepcopy(next(iter(images['images'].values())));no_image['sha256']='0'*64;self.assertIsNone(model.picture_bytes(no_image))
        self.assertIsNone(model.picture_bytes({'file':'.local/run-state.json'}))
        self.assertIsNone(model.picture_bytes({'file':'rouge/data/current-enemies/../../../../private.png'}))

    def test_complete_branch_and_random_candidates_do_not_become_actual_totals_clocks_or_rewards(self):
        ref=model.packet();seen=set()
        with patch.object(model,'packet',return_value=ref):
            for sid in ref['version']['current']['details']['stages']:
                r=model.stage_reference(sid)
                for a in r['actions']:
                    if a['queue']['kind']=='branch':seen.add('branch');self.assertIn('原始分支名称不证明触发条件',model.action_text(a))
                    if a['raw'].get('randomSpawnGroupKey'):seen.add('random');self.assertIn('不能把同组所有条目一起相加',model.action_text(a))
                    if a['raw']['actionType']=='ACTIVATE_PREDEFINED'and a['predefined_candidates']:seen.add('predefined');self.assertIn('不等于实际生成',model.action_text(a))
                    if len(seen)==3:break
                if len(seen)==3:break
        self.assertEqual(seen,{'branch','random','predefined'})

    def test_actual_bytes_damage_after_warm_read_invalidates_packet_and_recovery(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            temp=Path(folder)
            for n in(model.MANIFEST,*manifest['files']):
                dest=temp/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,dest)
            with patch.object(model,'ROOT',temp):
                self.assertIsNotNone(model.packet())
                for n in(model.MANIFEST,*manifest['files']):
                    p=temp/n;raw=p.read_bytes();p.write_bytes(raw+b' ')
                    self.assertIsNone(model.packet());self.assertIsNone(model.stage_reference('ro6_b_7'))
                    p.write_bytes(raw);self.assertIsNotNone(model.packet())

    def test_player_text_avoids_internal_markup_white_values_and_unsupported_inference(self):
        self.assertEqual(model.plain('<$ba.stun>晕眩</>与<城防路障>'),'晕眩与<城防路障>')
        ref=model.stage_reference('ro6_b_7');text=model.summary_text(ref);self.assertIn('不能相加为实际敌人数',text)
        for e in ref['enemies']:
            text=model.enemy_text(e);self.assertNotIn('<$',text);self.assertIn('不以白值替代',text);self.assertIn('未知',text)
        self.assertIsNone(model.stage_reference('ro6_b_7_typo'));self.assertIsNone(model.stage_reference('../private'))

if __name__=='__main__':unittest.main()
