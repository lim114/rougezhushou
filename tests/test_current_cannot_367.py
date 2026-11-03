"""Source and role boundaries; prepared, not executed in the cache task."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json, unittest
from rouge import current_cannot_reference as model


def clone(root):
    manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
    for name in (model.MANIFEST,*manifest['files']):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((model.ROOT/name).read_bytes())


class CurrentCannot367Tests(unittest.TestCase):
    def test_current_two_exact_enemy_bindings_and_seventeen_devices(self):
        packet=model.packet();self.assertIsNotNone(packet)
        rows=packet['data']['stages'];self.assertEqual(set(rows),set(model.STAGES))
        self.assertEqual([len(rows[s]['vaults'])for s in model.STAGES],[7,10])
        self.assertEqual([v['grade']for v in rows['ro6_t_6']['vaults']],[2,1,2,1,2,1,1])
        self.assertEqual([v['grade']for v in rows['ro6_t_7']['vaults']],[1]*10)
        for sid,row in rows.items():
            self.assertEqual(row['boss']['enemy_id'],model.BOSS);self.assertEqual(row['boss']['key'],'0')
            self.assertEqual(row['boss']['level'],0)
            for v in row['vaults']:
                self.assertEqual(v['original']['inst']['characterKey'],model.VAULT)
                self.assertIsNone(v['actual_appeared']);self.assertIsNone(v['actual_picked_up']);self.assertIsNone(v['actual_free_slots'])

    def test_covered_life_only_does_not_apply_false_identity_placeholders(self):
        data=model.packet()['data']
        self.assertEqual(data['stages']['ro6_t_6']['boss']['effective_override_reference'],{'.attributes.maxHp':60000})
        self.assertTrue(data['stages']['ro6_t_6']['boss']['hp_override_only'])
        self.assertFalse(data['stages']['ro6_t_7']['boss']['hp_override_only'])
        self.assertIsNone(data['stages']['ro6_t_7']['boss']['original']['overwrittenData'])
        self.assertFalse(data['stages']['ro6_t_6']['boss']['original']['overwrittenData']['name']['m_defined'])
        ref=model.reference(model.target_for_enemy('ro6_t_6','0'))
        text=model.player_text(ref)
        self.assertIn('单独生命设定',text)
        self.assertNotIn('60000',text);self.assertNotIn('80000',text)

    def test_exact_enemy_and_reward_admission_rejects_names_indices_and_other_stage(self):
        self.assertEqual(model.target_for_enemy('ro6_t_6','0'),{'kind':'enemy','stage_id':'ro6_t_6','key':'0'})
        for sid,key in (('ro6_t_6',0),('ro6_t_6','1'),('ro6_b_2','0'),('死箱','0'),('ro6_t_7',True)):
            self.assertIsNone(model.target_for_enemy(sid,key))
        key='$.predefines.tokenInsts[0]'
        target=model.target_for_reward('ro6_t_6',key)
        self.assertIsNotNone(target)
        self.assertEqual(model.reference(target)['selected']['pickup_free_slots_reference'],2)
        self.assertIsNone(model.target_for_reward('ro6_t_7',key))
        self.assertIsNone(model.target_for_reward('ro6_t_6','trap_327_shchst#1'))
        self.assertIsNone(model.reference({'kind':'vault','stage_id':'ro6_t_6','key':key,'extra':1}))

    def test_shop_function_exact_binding_and_three_four_boundary(self):
        expected=model.packet()['data']['shop_function_original']
        self.assertIsNotNone(model.shop_target(expected))
        self.assertIsNone(model.shop_target({'node_type':'诡意行商'}))
        changed=deepcopy(expected);changed['node_type']='秘境行商';self.assertIsNone(model.shop_target(changed))
        changed=deepcopy(expected);changed['extra_condition_references'][0]['description_text']='已解锁';self.assertIsNone(model.shop_target(changed))
        self.assertEqual([r['id']for r in model.reference()['stages']],list(model.STAGES))
        for floor,sid in ((1,'ro6_t_6'),(3,'ro6_t_6'),(4,'ro6_t_7'),(6,'ro6_t_7')):
            r=model.reference(floor=floor);self.assertEqual([s['id']for s in r['stages']],[sid]);self.assertIsNone(r['actual_shop_eligible'])
        for invalid in (True,False,0,7,'3',3.0,[]):self.assertIsNone(model.reference(floor=invalid))
        self.assertIsNone(model.reference(model.target_for_enemy('ro6_t_6','0'),floor=3))

    def test_whole_mechanisms_and_conflicting_free_slots_are_kept_separate(self):
        r=model.reference();docs=r['documents']
        self.assertEqual(len(docs['cannot']['cards']),2)
        skill=docs['cannot']['cards'][0]['full_visible']
        self.assertIn('强制击杀',skill);self.assertIn('跳过重生',skill)
        self.assertTrue(docs['cannot']['cards'][0]['tooltips'])
        self.assertIn('最高投资额',docs['theme_shop']['full_visible'])
        self.assertIn('历史累计投资额',docs['theme_investment']['full_visible'])
        text=model.player_text(r)
        for phrase in ('持续8秒','最多50%','0.667秒','最多5个','数量和等级','余额不足99','原地投降','秘境行商'):
            self.assertIn(phrase,text)
        self.assertIsNone(r['data']['actual_complete_free_slot_formula'])
        self.assertIsNone(r['data']['actual_complete_goods_pool'])
        self.assertFalse(r['data']['existing_315_reward_model_replaced'])
        self.assertFalse(r['numerical_combat_model_added'])
        for field in ('actual_recovered_vaults','actual_opened_vaults','actual_free_slots','actual_goods','actual_gold_lost','actual_outcome'):
            self.assertIsNone(r[field])

    def test_exact_forward_reverse_links_never_forge_event_choice(self):
        shop=model.reference(floor=3)
        links=model.links(shop)
        self.assertEqual({r['target']['stage_id']for r in links},{'ro6_t_6'})
        stage_target=next(r['target']for r in links if r['target']['kind']=='stage')
        stage=model.reference(model.qualify_link(shop,stage_target))
        back=next(r['target']for r in model.links(stage)if r['target']['kind']=='shop')
        self.assertEqual(model.reference(model.qualify_link(stage,back))['target'],{'kind':'shop','stage_id':None,'key':None})
        self.assertIsNone(model.qualify_link(shop,{'kind':'stage','stage_id':'ro6_t_7','key':None}))
        self.assertIsNone(model.qualify_link(stage,{'kind':'choice','key':'choice_ro6_shop'}))
        self.assertTrue(any(r['target'].get('reward_id')=='$.predefines.tokenInsts[0]'for r in model.links(stage)))

    def test_every_source_member_mutation_and_dependency_failure_closes(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet())
                for name in (model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    path=root/name;body=path.read_bytes();path.write_bytes(body+b'x')
                    self.assertIsNone(model.packet(),name);self.assertIsNone(model.reference(),name)
                    path.write_bytes(body);self.assertIsNotNone(model.packet(),name)
        with patch.object(model.rewards,'packet',return_value=None):self.assertIsNone(model.packet())

    def test_selected_original_stage_and_device_changes_are_rejected(self):
        actual=model.rewards.packet()
        for mutation in ('enemy_level','device_grade','handbook','skill'):
            changed=deepcopy(actual)
            level=changed['current']['inputs']['levels']['levels/obt/roguelike/ro6/level_rogue6_t-6.json']
            if mutation=='enemy_level':level['enemyDbRefs'][0]['level']=True
            elif mutation=='device_grade':level['predefines']['tokenInsts'][0]['inst']['level']=1
            elif mutation=='handbook':changed['current']['inputs']['handbook'][model.BOSS]['abilityList'][3]['text']='没有损失'
            else:changed['selected']['skills']['sktok_shchst']['levels'][0]['description']='免费领取'
            with patch.object(model.rewards,'packet',return_value=changed):self.assertIsNone(model.packet(),mutation)
        first=model.reference();first['data']['stages']['ro6_t_6']['vaults'].clear()
        self.assertEqual(len(model.reference()['data']['stages']['ro6_t_6']['vaults']),7)


if __name__=='__main__':unittest.main()
