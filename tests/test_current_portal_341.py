from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_portal as m,node_catalog

def clone(root):
    for name in {m.MANIFEST,*json.loads((m.ROOT/m.MANIFEST).read_bytes())['files']}:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((m.ROOT/name).read_bytes())

class CurrentPortal341Tests(unittest.TestCase):
    def test_complete_build_reproduces76_scenes114_choices_six_fogs(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_portal_341.py','--check'],cwd=m.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr);r=m.reference();self.assertEqual((len(r['scenes']),len(r['choices']),len(r['data']['originals']['scenes']),len(r['data']['originals']['choices'])),(13,10,76,114))
        self.assertEqual([sid for sid in r['scenes']if sid.startswith('fog:')],['fog:'+s for s in('红雾','蓝雾','绿雾','金雾','橙雾','紫雾')])
    def test_all_original_records_match_complete_current_not_id_prefixes(self):
        r=m.reference();d=m.version.packet()['current']['details']
        for kind,table in [('scenes','choiceScenes'),('choices','choices')]:
            for key,v in r['data']['originals'][kind].items():self.assertEqual(v,d[table][key])
        self.assertEqual({k for s in r['scenes'].values()for k in s['source_scene_ids']},set(r['data']['originals']['scenes']))
        self.assertEqual({k for c in r['choices'].values()for k in c['variant_ids']},set(r['data']['originals']['choices']))
        for sid,scene in r['scenes'].items():
            for cid in [None,*scene['choice_ids']]:self.assertNotIn('父脚本',m.player_text(r,sid,cid))
    def test_green_conflict_preserved_red_alternative_not_applied_to_all_fogs(self):
        r=m.reference();self.assertIn('leave:0',r['scenes']['fog:绿雾']['choice_ids']);self.assertIn('leave:1',r['scenes']['fog:绿雾']['choice_ids']);self.assertIn('实际选择依据未知',m.player_text(r,'fog:绿雾'));self.assertNotIn('父脚本',m.player_text(r,'fog:绿雾'));self.assertNotIn('原始组/',m.player_text(r,'fog:绿雾'))
        for sid,s in r['scenes'].items():
            if sid.startswith('fog:'):self.assertEqual('no-engine:alt'in s['choice_ids'],sid=='fog:红雾')
    def test_has_and_no_processed_parts_boundaries_not_total_parts(self):
        for count in(None,0,1,2):
            r=m.reference(processed_parts=count)
            for cid in r['scenes']['fog:红雾']['choice_ids']:
                c=m.choice_reference(r,'fog:红雾',cid);self.assertIs(c['listed_condition_match'],None if count is None else count>=1 if c['inventory_rule']=='has'else count==0)
            self.assertIsNone(r['actual_inventory']);self.assertIsNone(r['actual_consumed'])
    def test_three_payments_are_alternatives_and_confirmation_not_second_cost(self):
        r=m.reference(processed_parts=1)
        for i in(1,2,3):
            c=m.choice_reference(r,'fog:红雾','pay:'+str(i));self.assertEqual(c['next_scene_id'],'after:'+str(i));text=m.player_text(r,'fog:红雾',c['id']);self.assertIn('不一起消耗3件',text)
            c=m.choice_reference(r,c['next_scene_id'],'confirm:'+str(i));self.assertIsNone(c['inventory_rule']);self.assertIsNone(c['next_scene_id']);self.assertIsNone(c['listed_condition_match']);self.assertEqual(c['stage_ids'],[])
            self.assertIn('不把确认当作再次支付1件',m.player_text(r,'after:'+str(i),c['id']))
    def test_leave_group_is_has_parts_only_in_document_not_raw_parent(self):
        r=m.reference(processed_parts=0);self.assertFalse(m.choice_reference(r,'fog:红雾','leave:0')['listed_condition_match'])
        key=next(k for k,v in r['data']['originals']['choices'].items()if v['title']=='不应该冒进');r=m.reference(processed_parts=0,source_request=m.locate('choices',key)['source_request']);c=m.choice_reference(r,'source-choice','source-choice');self.assertIsNone(c['inventory_rule']);self.assertIsNone(c['listed_condition_match'])
    def test_all190_exact_source_entries_no_guessed_outgoing_edges(self):
        raw=m.reference()['data']['originals'];count=0
        for cat in('scenes','choices'):
            for key,original in raw[cat].items():
                target=m.locate(cat,key);r=m.reference(source_request=target['source_request']);self.assertEqual(r['requested_original'],original);self.assertEqual(r['source_request'],{'category':cat,'key':key})
                if cat=='scenes':self.assertEqual(r['scenes']['source-scene']['source_scene_ids'],[key]);self.assertEqual(r['scenes']['source-scene']['choice_ids'],[])
                else:
                    c=r['choices']['source-choice'];self.assertEqual(c['variant_ids'],[key]);self.assertTrue(c['source_only'])
                    if original['nextSceneId']:self.assertEqual(r['scenes']['source-next']['source_scene_ids'],[original['nextSceneId']]);self.assertEqual(r['scenes']['source-next']['choice_ids'],[])
                    else:self.assertIsNone(c['next_scene_id'])
                count+=1
        self.assertEqual(count,190)
        kinds=list(raw and m.reference()['data']['original_choice_association'].values());self.assertEqual(kinds.count('explicit_destination_scene'),95);self.assertEqual(kinds.count('full_literal_teleport_candidate'),19)
        r=m.reference(source_request=m.locate('choices','choice_ro6_portal1a_4')['source_request']);self.assertEqual(r['requested_choice_association'],'full_literal_teleport_candidate');self.assertIn('尚未证明其属于溯源',m.player_text(r,'source-choice','source-choice'))
    def test_unknown_input_and_foreign_same_name_rejected(self):
        for v in(True,-1,1.2,'1'):self.assertIsNone(m.reference(processed_parts=v))
        for cat,key in [('scenes','溯源'),('choices','成功了'),('relics','choice_ro6_portal1a_1'),('choices','choice_ro6_portal1a_1extra'),(True,'choice_ro6_portal1a_1')]:self.assertIsNone(m.locate(cat,key))
        self.assertIsNone(m.reference(source_request={'category':'choices','key':'missing'}));self.assertIsNone(m.reference(source_request={'category':'choices','key':'choice_ro6_portal1a_1','extra':True}))
    def test_each_manifest_member_damage_fails_closed_after_success(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(m,'ROOT',root):
                for n in(m.MANIFEST,*json.loads((root/m.MANIFEST).read_bytes())['files']):
                    p=root/n;raw=p.read_bytes();self.assertIsNotNone(m.reference());p.write_bytes(raw+b' ');self.assertIsNone(m.reference(),n);p.write_bytes(raw)
    def test_legacy_initial_entry_not_repaired_by_same_title(self):
        e=deepcopy(node_catalog._event('community_group_027'));b=m.catalogue_binding(e);self.assertIsNotNone(b);self.assertEqual(len(b['exact_scene_links']),44);self.assertTrue(b['legacy_initial_scene_remains_unbound']);e['scenes'][0]['description']+='changed';self.assertIsNone(m.catalogue_binding(e))
    def test_return_isolation_no_actual_inventory_destination_or_variant(self):
        r=m.reference();r['choices'].clear();self.assertEqual(len(m.reference()['choices']),10)
        r=m.reference();self.assertTrue(all(r[k]is None for k in('actual_inventory','actual_consumed','actual_teleported','actual_destination','actual_variant','actual_eligible')));self.assertFalse(r['run_updated'])
if __name__=='__main__':unittest.main()
