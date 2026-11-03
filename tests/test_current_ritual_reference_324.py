from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_ritual_reference as model
from scripts import build_current_ritual_reference_324 as builder
ROOT=Path(__file__).resolve().parents[1]

def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)

class CurrentRitualReference324Tests(unittest.TestCase):
    def test_reproducible_complete_documented_records_full_current_comparison(self):
        raw,m=builder.build();self.assertEqual(raw,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes())
        d=model.packet()['data'];self.assertEqual((len(d['events']),len(d['scenes']),len(d['choices'])),(2,9,13));self.assertEqual({g:len(v)for g,v in d['originals'].items()},{'choices':15,'scenes':9,'items':7,'stages':2})
        self.assertTrue(all(v for rows in d['complete_selected_record_comparison_to_baseline'].values()for v in rows.values()));self.assertFalse(d['game_parent_script_restored']);self.assertFalse(d['delivery_quantities_verified']);self.assertIsNone(d['one_key_satisfies_three_steps'])

    def test_document_parents_skip_branches_and_explicit_next_not_suffix_guess(self):
        r=model.reference();self.assertEqual(r['scenes']['scene_ro6_end3_enter']['choice_ids'],['choice_ro6_end3_1','choice_ro6_end3_2'])
        self.assertEqual(r['scenes']['scene_ro6_end3_1']['choice_ids'],['choice_ro6_end3_'+str(n)for n in(3,4,5)])
        for nums,parent,dest in(((3,4,5),'1','3'),((6,7,8),'3','4'),((9,10,11),'4','5')):
            self.assertEqual(r['scenes']['scene_ro6_end3_'+parent]['choice_ids'],['choice_ro6_end3_'+str(n)for n in nums])
            for n in nums:self.assertEqual(r['choices']['choice_ro6_end3_'+str(n)]['next_scene_id'],'scene_ro6_end3_'+dest)
        self.assertEqual(r['scenes']['scene_ro6_end3_2']['choice_ids'],[]);self.assertTrue(all(not c['stage_ids']for c in r['choices'].values()))

    def test_three_paired_effects_keep_quantities_unknown_and_exact_acquisitions(self):
        r=model.reference();d=r['data'];primary=model.version.packet()['current']['details']
        for a,b,feature,item in((3,4,'1','4'),(6,7,'3','6'),(9,10,'2','5')):
            for n,other,iid in((a,b,'rogue_6_relic_final_'+item),(b,a,'rogue_6_relic_cargo_13')):
                cid='choice_ro6_end3_'+str(n);c=r['choices'][cid];self.assertEqual(c['weakening_id'],'rogue_6_chimera_weaken_'+feature);self.assertEqual(c['offered_item_id'],iid);self.assertIsNone(c['offered_quantity']);self.assertIsNone(c['actual_effect']);self.assertEqual(c['alternative_choice_id'],'choice_ro6_end3_'+str(other));self.assertEqual(d['originals']['items'][c['weakening_id']],primary['items'][c['weakening_id']])
                text=model.player_text(r,c['scene_id'],cid);self.assertIn('不默认每次消耗1件',text);self.assertIn('不重复相加',text);self.assertNotIn('choice_ro6_',text);self.assertNotIn('FEATURE',text)
            self.assertIsNotNone(model.acquisition_reference(r,r['choices']['choice_ro6_end3_'+str(a)]['scene_id'],'choice_ro6_end3_'+str(a)));self.assertIsNone(model.acquisition_reference(r,r['choices']['choice_ro6_end3_'+str(b)]['scene_id'],'choice_ro6_end3_'+str(b)))
        self.assertIn('首次',model.player_text(r,'scene_ro6_end3_1','choice_ro6_end3_3'));self.assertIn('伤害归零',model.player_text(r,'scene_ro6_end3_4','choice_ro6_end3_9'))
        sources=d['acquisitions'];self.assertEqual(sources['rogue_6_relic_final_5']['stage_id'],'ro6_t_12');self.assertEqual(sources['rogue_6_relic_final_4']['source_choice_id'],'choice_ro6_chimera2_1');self.assertEqual(sources['rogue_6_relic_final_6']['recipe_choice_id'],'choice_ro6_sacrifice2_20')

    def test_exact_entry_membership_all_events_materials_source_key_no_auto_choice(self):
        d=model.packet()['data']
        for k,v in d['scenes'].items():self.assertEqual(model.locate('scenes',k),{'event_id':v['event_id'],'scene_id':k,'choice_id':None})
        for k,v in d['choices'].items():self.assertEqual(model.locate('choices',k),{'event_id':v['event_id'],'scene_id':v['scene_id'],'choice_id':k})
        for iid in model.MATERIALS[:3]:self.assertEqual(d['choices'][model.locate('relics',iid)['choice_id']]['offered_item_id'],iid)
        key=model.locate('relics',model.MATERIALS[-1]);self.assertIsNone(key['choice_id']);self.assertEqual(key['scene_id'],'scene_ro6_end3_enter')
        for cat,key in(('choices','choice_ro6_end3_999'),('choices','choice_ro6_sacrifice2_21'),('scenes','scene_ro6_end2_enter'),('relics','rogue_6_relic_final_7'),('stages','ro6_b_6')):self.assertIsNone(model.locate(cat,key))
        self.assertIsNone(model.reference('unknown'));self.assertIsNone(model.choice_reference(model.reference(),'scene_ro6_end3_enter','choice_ro6_end3_3'))

    def test_each_public_file_corruption_and_primary_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        for group,key in(('choices','choice_ro6_end3_3'),('choiceScenes','scene_ro6_end3_1'),('items','rogue_6_relic_final_4'),('stages','ro6_b_6')):
            p=deepcopy(model.version.packet());p['current']['details'][group][key]['unverified_drift']=True
            with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())

    def test_builder_rejects_ambiguous_caption_or_next_and_missing_feature(self):
        for mode in('duplicate','next','feature'):
            with self.subTest(mode=mode),TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
                if mode=='duplicate':d['details']['choices']['injected_duplicate']=deepcopy(d['details']['choices']['choice_ro6_end3_3'])
                if mode=='next':d['details']['choices']['choice_ro6_end3_3']['nextSceneId']='scene_ro6_end3_5'
                if mode=='feature':d['details']['choices']['choice_ro6_end3_3']['displayData']['itemId']='rogue_6_relic_final_4'
                f.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)

if __name__=='__main__':unittest.main()
