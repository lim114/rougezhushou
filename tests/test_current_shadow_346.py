from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_shadow as model,node_catalog
def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files'],model.packet()['data']['icon_reference']['file']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())
JOIN_NODES=['node-1','node-3','node-5','node-7','node-9','node-11','node-13','node-15']
class CurrentShadow346Tests(unittest.TestCase):
    def test_full_build_and_every_original_preserved(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_shadow_346.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();d=r['data'];self.assertEqual((len(r['scenes']),len(r['choices']),len(d['originals']['scenes']),len(d['originals']['choices'])),(35,49,28,28));current=model.version.packet()['current']['details']
        for g,t in [('scenes','choiceScenes'),('choices','choices'),('items','items')]:
            for k,v in d['originals'][g].items():self.assertEqual(v,current[t][k])
    def test_each_round_cost_and_seven_random_result_menus_not_game_buttons(self):
        r=model.reference();costs=[]
        for sid in JOIN_NODES:
            c=model.choice_reference(r,sid,sid+':option:0');costs.append(c['description']);self.assertIn('每次加入分别消耗',model.player_text(r,sid,c['id']))
        self.assertEqual(costs,['消耗1目标生命值']*2+['消耗2目标生命值']*3+['消耗3目标生命值']*3)
        menus=[s for s in r['scenes'].values()if s['scope']=='results'];self.assertEqual(len(menus),7);self.assertEqual(sum(len(s['choice_ids'])for s in menus),16)
        for s in menus:
            self.assertIn('不能自行选择游戏随机结果',model.player_text(r,s['id']))
            for cid in s['choice_ids']:self.assertIs(r['choices'][cid]['actual_game_button'],False);self.assertEqual(r['choices'][cid]['variant_ids'],[])
    def test_all49_document_references_have_source_and_own_phase(self):
        r=model.reference()
        for c in r['choices'].values():
            self.assertEqual(model.choice_reference(r,c['scene_id'],c['id']),c);self.assertIsNone(model.choice_reference(r,'unrelated',c['id']));self.assertIn(c['next_scene_id'],r['scenes']);self.assertTrue(c['source']);self.assertEqual(c['stage_ids'],[])
        self.assertEqual(r['choices']['node-13:option:0']['next_scene_id'],'node-14');self.assertTrue(all(r['data']['originals']['choices'][k]['nextSceneId']is None for k in r['choices']['node-13:option:0']['variant_ids']))
    def test_eighth_action_point_returns_but_named_reward_ends_and_no_free_loop_claim(self):
        r=model.reference();c=r['choices']['node-16:option:0'];self.assertEqual(c['description'],'获得1行动力');self.assertEqual(c['next_scene_id'],'node-15');self.assertEqual(r['choices']['node-17:option:0']['next_scene_id'],'node-18');self.assertEqual(r['scenes']['node-18']['choice_ids'],[])
        for sid in('node-15','node-15:results','node-16'):self.assertIn('不能由此认定无限次数',model.player_text(r,sid))
        for sid in JOIN_NODES[1:]:self.assertEqual(r['choices'][sid+':option:1']['next_scene_id'],'node-19')
        self.assertEqual(r['choices']['node-1:option:1']['next_scene_id'],'node-28')
    def test_every56_original_entry_exact20_next_and8_missing_do_not_get_document_menu(self):
        d=model.reference()['data'];explicit=0;missing=0
        for category in('scenes','choices'):
            for key,v in d['originals'][category].items():
                r=model.reference(**model.locate(category,key));self.assertEqual(r['requested_original'],v)
                if category=='scenes':self.assertEqual(r['scenes']['source-scene']['choice_ids'],[])
                elif v['nextSceneId']:
                    explicit+=1;self.assertEqual(r['choices']['source-choice']['next_scene_id'],'source-next');self.assertEqual(r['scenes']['source-next']['description'],d['originals']['scenes'][v['nextSceneId']]['description']);self.assertEqual(r['scenes']['source-next']['choice_ids'],[])
                else:missing+=1;self.assertIsNone(r['choices']['source-choice']['next_scene_id']);self.assertIn('不根据相同消耗猜',model.player_text(r,'source-choice','source-choice'))
        self.assertEqual((explicit,missing),(20,8))
    def test_document_repeated_narratives_and_quiet_originals_not_forced_together(self):
        r=model.reference();self.assertEqual(len(r['scenes']['node-8']['source_scene_ids']),2);self.assertEqual(r['scenes']['node-27']['source_scene_ids'],['scene_ro6_normal4_1']);self.assertIn('不能仅凭文字或编号',model.player_text(r,'node-27'));self.assertIn('scene_ro6_normal4_3',r['data']['originals']['scenes']);self.assertIn('多份原对话全文相同',model.player_text(r,'node-8'))
    def test_relic_exact_pointer_image_and_effect_not_shifted_numeric_ordinal(self):
        r=model.reference();c=r['choices']['node-17:option:0'];self.assertTrue(model.shows_reward(r,c['scene_id'],c['id']));item=r['data']['originals']['items']['rogue_6_relic_artifact_4'];self.assertIn('攻击力+10%',item['usage']);self.assertEqual(model.locate('relics',item['id']),{'scene_id':'node-17','choice_id':c['id']});self.assertIsNotNone(model.icon_bytes());self.assertIn('不是获得6源石锭',model.player_text(r,c['scene_id'],c['id']))
        for key in r['choices']:
            c=r['choices'][key];self.assertIs(model.shows_reward(r,c['scene_id'],key),key=='node-17:option:0')
    def test_actual_state_and_random_pool_remain_unknown_no_total(self):
        r=model.reference();self.assertFalse(r['run_updated']);self.assertFalse(r['data']['complete_game_option_pool'])
        for key in('actual_eligible','actual_inventory','actual_received','actual_result','actual_choice','actual_transition','actual_pool','actual_life','actual_round'):self.assertIsNone(r[key])
        self.assertEqual(r['choices']['node-21:option:0']['description'],'回复3目标生命值');self.assertEqual(r['choices']['node-22:option:0']['description'],'获得5目标生命值');self.assertEqual(r['choices']['node-20:option:0']['description'],'可携带干员+1')
    def test_sources_fail_closed_and_icon_failure_only_falls_back(self):
        with TemporaryDirectory()as f:
            root=Path(f);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    p=root/name;raw=p.read_bytes();self.assertIsNotNone(model.reference());p.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);p.write_bytes(raw)
                pic=root/model.reference()['data']['icon_reference']['file'];pic.write_bytes(pic.read_bytes()+b'x');self.assertIsNone(model.icon_bytes());self.assertIsNotNone(model.reference())
    def test_invalid_source_requests_and_mutation_do_not_leak(self):
        for x in(True,[],{}, {'category':'scenes','key':1},{'category':'choices','key':'unknown'},{'category':'scenes','key':'scene_ro6_normal4_enter','extra':True}):self.assertIsNone(model.reference(source_request=x))
        self.assertIsNone(model.reference(True));self.assertIsNone(model.locate(True,1));r=model.reference();r['scenes'].clear();self.assertEqual(len(model.reference()['scenes']),35)
    def test_legacy21_links20_unique_and_full_identity_recheck(self):
        e=deepcopy(node_catalog._event('community_group_010'));b=model.catalogue_binding(e);self.assertEqual(len(b['exact_scene_links']),21);self.assertEqual(len({x['current_original_scene_id']for x in b['exact_scene_links']}),20);e['scenes'][0]['description']+='x';self.assertIsNone(model.catalogue_binding(e))
if __name__=='__main__':unittest.main()
