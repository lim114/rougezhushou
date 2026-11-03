from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_reward_reference as model
from scripts.build_current_reward_reference_315 import build
ROOT=Path(__file__).resolve().parents[1]

class CurrentRewardReference315Tests(unittest.TestCase):
    def test_full_current_character_and_skill_selections_match_pinned_actual_originals(self):
        ref=model.packet();self.assertIsNotNone(ref);cache=ROOT/'.cache/p3-current-rewards-315'
        if not(cache/'character_table.json').exists():self.skipTest('此机没有完整原件缓存，选片原件核对不可计通过。')
        originals={}
        for name,pin in ref['sources']['original_sources'].items():
            raw=(cache/(name+'.json')).read_bytes();self.assertEqual(len(raw),pin['bytes']);self.assertEqual(sha256(raw).hexdigest(),pin['sha256']);originals[name]=json.loads(raw)
        for eid,char in ref['selected']['characters'].items():self.assertEqual(char,originals['character_table'][eid])
        for sid,skill in ref['selected']['skills'].items():self.assertEqual(skill,originals['skill_table'][sid])
        # The original builder reproduces the historical recipe, not the new
        # runtime manifest that separates build-only provenance.
        self.assertEqual(build(ROOT),(ROOT/'research/p3-current-rewards-315/runtime-manifest.json').read_bytes())
    def test_every184_stage113_levels_all_supported_device_and_spawn_rows_preserved(self):
        ref=model.packet();stages=ref['current']['version']['current']['details']['stages'];self.assertEqual(len(stages),184);seen=set();counts={'device':0,'rare':0,'moving':0}
        with patch.object(model,'packet',return_value=ref):
            for sid,s in stages.items():
                r=model.stage_rewards(sid);level=ref['current']['inputs']['levels'][r['level_key']];expected=[]
                for c in('predefines','hardPredefines'):
                    for field in('characterInsts','tokenInsts'):
                        expected += [f'$.{c}.{field}[{i}]'for i,o in enumerate((level.get(c)or{}).get(field)or[])if(o.get('inst')or{}).get('characterKey')in model.DEVICES]
                for q in model.battle.queues(level):expected += [q['source_selector']+f'.actions[{i}]'for i,a in enumerate(q['actions'])if a['actionType']=='SPAWN'and a['key']in set(r['current_mimic_catalog_ids'])|{model.MOVING}]
                self.assertEqual([x['id']for x in r['rows']],expected);self.assertEqual(len(expected),len(set(expected)))
                self.assertIsNone(r['all_actual_rewards']);self.assertFalse(r['complete_reward_pool_known']);self.assertFalse(r['mutated_run']);self.assertTrue(r['raw_null_capsule_fields_mean_unknown_not_empty'])
                seen.add(r['level_key'])
                for row in r['rows']:counts[row['kind']]+=1;self.assertIsNone(row['actual_reward']);self.assertIsNone(row['position_on_original'])
        self.assertEqual(len(seen),113);self.assertEqual(counts,{'device':1056,'rare':543,'moving':256})
    def test_current_device_amounts_costs_and_shop_range_are_separate_resources(self):
        ref=model.packet()
        for eid,n,resource in [('trap_320_shtlbx',1,'随机零件'),('trap_321_shnbox',2,'源石锭'),('trap_322_shrbox',5,'源石锭'),('trap_323_shsbox',10,'源石锭'),('trap_327_shchst',1,'商店物品')]:
            raw={'skillIndex':0,'mainSkillLvl':1};rule=model.device_rule(eid,raw,ref);self.assertTrue(rule['quantity_qualified']);self.assertEqual(rule['outcomes'][0]['minimum'],n);self.assertEqual(rule['outcomes'][0]['resource'],resource)
            if eid=='trap_320_shtlbx':self.assertEqual(rule['outcomes'][0]['cost'],50);self.assertEqual(rule['outcomes'][0]['cost_resource'],'部署费用')
            if eid=='trap_327_shchst':self.assertEqual(rule['outcomes'][0]['maximum'],2);self.assertIn('无法再部署',rule['outcomes'][0]['restriction'])
    def test_unknown_skill_talent_template_or_amount_override_never_inherits_literal_quantity(self):
        ref=model.packet();base={'skillIndex':0,'mainSkillLvl':1}
        for change in({'skillIndex':False},{'mainSkillLvl':2},{'overrideTalents':[{}]},{'tmplId':'different'},{'uniEquipIds':['other']},{'overrideSkillBlackboard':[{'key':'cost','value':1}]},{'overrideSkillBlackboard':[{'key':'action_index','value':1}]}):
            rule=model.device_rule('trap_320_shtlbx',{**base,**change},ref);self.assertFalse(rule['quantity_qualified'],change);self.assertIsNone(rule['outcomes'][0]['minimum']);self.assertIsNone(rule['outcomes'][0].get('cost'))
    def test_random_groups_keep_complete_same_queue_scope_and_empty_members_without_weights_as_probability(self):
        ref=model.packet()
        with patch.object(model,'packet',return_value=ref):r=model.stage_rewards('ro6_n_2_6')
        level=ref['current']['inputs']['levels'][r['level_key']];queues={q['source_selector']:q for q in model.battle.queues(level)};empty=False
        for row in r['rows']:
            for group in row['candidate_groups']:
                expected=[a for a in queues[group['queue_selector']]['actions']if a.get('randomSpawnGroupKey')==group['group_key']and a.get('randomSpawnGroupPackKey')==group['pack_key']]
                self.assertEqual([m['raw']for m in group['members']],expected)
                if any(not a.get('key')for a in expected):empty=True;self.assertIn('空条目',model.row_text(row))
        self.assertTrue(empty)
    def test_alias_collision_keeps_both_declarations_but_refuses_arbitrary_jump(self):
        ref=model.packet();copy=deepcopy(ref);level=copy['current']['inputs']['levels']['levels/obt/roguelike/ro6/level_rogue6_2-6.json'];original=next(x for x in level['predefines']['tokenInsts']if x.get('alias')and(x.get('inst')or{}).get('characterKey')in model.DEVICES);duplicate=deepcopy(original);level['predefines']['tokenInsts'].append(duplicate)
        with patch.object(model,'packet',return_value=copy):r=model.stage_rewards('ro6_n_2_6')
        rows=[x for x in r['rows']if x.get('alias')==original['alias']];self.assertEqual(len(rows),2)
        for row in rows:self.assertFalse(row['alias_unique']);self.assertEqual(row['source_action_keys'],[]);self.assertIn('无法唯一对应',model.row_text(row))
    def test_box_and_spawn_chain_linked_but_not_double_counted_or_assumed_triggered(self):
        r=model.stage_rewards('ro6_n_2_6');boxes=[x for x in r['rows']if x['entity_id']=='trap_323_shsbox'];self.assertTrue(boxes)
        for box in boxes:
            self.assertTrue(box['explicit_branch_exists']);self.assertTrue(any(a['raw']['key']==model.MOVING for a in box['linked_branch_actions']));self.assertIn('不能把同一条奖励链',model.row_text(box));self.assertIsNone(box['actual_reward'])
        movers=[x for x in r['rows']if x['kind']=='moving'];self.assertTrue(movers)
        for row in movers:self.assertEqual([x['minimum']for x in row['rule']['outcomes']],[10,-10]);self.assertIn('互斥结果',model.row_text(row))
    def test_moving_and_rare_grade_overrides_unknown_are_not_ignored(self):
        ref=model.packet()
        for eid in(model.MOVING,'enemy_2001_duckmi'):
            valid={'id':eid,'level':0,'useDb':True,'overwrittenData':None};rule=model.enemy_rule(eid,[valid],ref);self.assertIsNotNone(rule['outcomes'][0]['minimum'])
            for change in({'level':True},{'level':3},{'overwrittenData':{}},{'useDb':False}):self.assertIsNone(model.enemy_rule(eid,[{**valid,**change}],ref)['outcomes'][0]['minimum'])
        self.assertEqual(ref['documentation_scope']['successful_new_HTML_downloads'],0)
        self.assertIn('Pinned prior',ref['documentation_scope']['reuse_scope'])
    def test_real_source_damage_clears_warm_model_and_recovers_exact_original(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for n in(model.MANIFEST,*manifest['files']):
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p=root/model.PACK/'selected-originals.json';raw=p.read_bytes();p.write_bytes(raw+b' ')
                self.assertIsNone(model.stage_rewards('ro6_n_2_6'));p.write_bytes(raw);self.assertIsNotNone(model.stage_rewards('ro6_n_2_6'))
    def test_no_rows_no_pool_or_mimic_metadata_does_not_mean_no_rewards_or_spawns(self):
        r=model.stage_rewards('ro6_b_7');self.assertEqual(r['rows'],[]);self.assertIn('完整结算奖励与可掉落物品清单：未知',model.summary_text(r));self.assertEqual(len(r['current_mimic_catalog_ids']),5);self.assertFalse(r['complete_reward_pool_known']);self.assertIsNone(model.stage_rewards('typo'))

if __name__=='__main__':unittest.main()
