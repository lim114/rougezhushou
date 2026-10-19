from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import box_event_reference as model
from scripts import build_box_event_reference_322 as builder
ROOT=Path(__file__).resolve().parents[1]
SCENES={'scene_ro6_end2_enter':['protect','leave','covenant','print'],'scene_ro6_end2_2':['normal_battle'],'scene_ro6_end2_1':[],'scene_ro6_end2_3':[]}
VARIANTS=['choice_ro6_end2_1','choice_ro6_end2_4','choice_ro6_end2_7']


def clone(root):
    manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*manifest['files']):
        out=root/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,out)


class BoxEventReference322Tests(unittest.TestCase):
    def test_rebuild_exact_bytes_full_table_and_all_variants_preserved(self):
        data,manifest=builder.build();self.assertEqual(data,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes())
        r=model.reference();self.assertIsNotNone(r);self.assertEqual({k:v['choice_ids']for k,v in r['scenes'].items()},SCENES)
        self.assertEqual((len(r['choices']),len(r['data']['originals']['choices']),len(r['data']['originals']['stages'])),(5,7,2))
        self.assertTrue(r['data']['document_under_investigation']);self.assertFalse(r['data']['all_game_options_verified']);self.assertFalse(r['data']['game_parent_script_restored']);self.assertIsNone(r['actual_eligible']);self.assertFalse(r['run_updated'])

    def test_three_same_wording_records_are_not_one_selected_variant(self):
        r=model.reference();c=model.choice_reference(r,'scene_ro6_end2_enter','protect');self.assertEqual(c['variant_ids'],VARIANTS);self.assertIsNone(c['actual_variant_id']);self.assertIsNone(r['actual_variant'])
        originals=r['data']['originals']['choices'];self.assertEqual({originals[k]['type']for k in VARIANTS},{'TRADE','NEXT'});self.assertNotEqual(originals[VARIANTS[0]]['displayData'],originals[VARIANTS[1]]['displayData'])
        for cid in VARIANTS:self.assertEqual(model.locate('choices',cid),{'event_id':'box','scene_id':'scene_ro6_end2_enter','choice_id':'protect'})

    def test_hard_link_stays_on_documented_NEXT_choice_not_neighboring_battle(self):
        r=model.reference();self.assertEqual(r['choices']['covenant']['stage_ids'],['ro6_b_5_b']);self.assertEqual(r['choices']['covenant']['next_scene_id'],'scene_ro6_end2_3')
        self.assertEqual(r['data']['originals']['choices']['choice_ro6_end2_5']['type'],'NEXT');self.assertEqual(r['choices']['normal_battle']['stage_ids'],['ro6_b_5'])
        self.assertEqual(r['choices']['print']['stage_ids'],[]);self.assertTrue(r['choices']['print']['battle_destination_unbound']);self.assertEqual(r['scenes']['scene_ro6_end2_3']['choice_ids'],[])

    def test_condition_false_unknown_true_are_distinct_and_never_actual_eligibility(self):
        for value in(None,False,True):
            r=model.reference('box',value);c=model.choice_reference(r,'scene_ro6_end2_enter','covenant');self.assertIs(c['listed_condition_match'],value);self.assertIsNone(r['actual_eligible']);self.assertIsNone(r['actual_received'])
            text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('祭日之契',text);self.assertIn('调查中',text);self.assertIn('失恒常量',text);self.assertNotIn('choice_ro6_',text)
        self.assertIn('不满足',model.player_text(model.reference('box',False),'scene_ro6_end2_enter','covenant'))
        self.assertIn('完整游戏前置仍待核验',model.player_text(model.reference('box',True),'scene_ro6_end2_enter','covenant'))
        for invalid in(0,1,'true',[],{}):
            with self.assertRaises(ValueError):model.reference('box',invalid)

    def test_no_cross_scene_or_prefix_links_and_no_feature_item_as_player_relic(self):
        r=model.reference();self.assertIsNone(model.choice_reference(r,'scene_ro6_end2_3','print'));self.assertIsNone(model.choice_reference(r,'scene_ro6_end2_enter','normal_battle'))
        for cat,key in(('scenes','scene_ro6_end2_missing'),('choices','choice_ro6_end2_0'),('scenes','scene_ro6_end4_enter'),('stages','ro6_b_5'),(False,'scene_ro6_end2_enter')):self.assertIsNone(model.locate(cat,key))
        for cid in r['choices']:
            text=model.player_text(r,r['choices'][cid]['scene_id'],cid);self.assertNotIn('二结局转变弹窗',text);self.assertNotIn('二结局激活2',text)

    def test_each_real_pinned_input_damage_clears_and_restores(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);manifest=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*manifest['files']):
                    file=root/name;raw=file.read_bytes();file.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);self.assertIsNone(model.locate('scenes','scene_ro6_end2_enter'));file.write_bytes(raw);self.assertIsNotNone(model.reference())

    def test_current_primary_drift_cannot_inherit_fixed_community_mapping(self):
        raw=deepcopy(model.version.packet());raw['current']['details']['stages']['ro6_b_5_b']['name']='changed'
        with patch.object(model.version,'packet',return_value=raw):self.assertIsNone(model.packet())

    def test_builder_rejects_missing_extra_or_disagreeing_variant_and_ambiguous_stage(self):
        for mode in('missing','extra','wording','destination','stage'):
            with self.subTest(mode=mode),TemporaryDirectory()as folder:
                root=Path(folder);clone(root);file=root/builder.CURRENT;current=json.loads(file.read_bytes());d=current['details']
                if mode=='missing':del d['choices'][VARIANTS[0]]
                elif mode=='extra':d['choices']['unproven_variant']=deepcopy(d['choices'][VARIANTS[0]])
                elif mode=='wording':d['choices'][VARIANTS[0]]['description']='不同文本'
                elif mode=='destination':d['choices'][VARIANTS[0]]['nextSceneId']='scene_ro6_end2_3'
                else:d['stages']['ambiguous']=deepcopy(d['stages']['ro6_b_5_b'])
                file.write_bytes(builder.encoded(current))
                with self.assertRaises(ValueError):builder.build(root)


if __name__=='__main__':unittest.main()
