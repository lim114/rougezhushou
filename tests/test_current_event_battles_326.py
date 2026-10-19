from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_event_battles as model
from scripts import build_current_event_battles_326 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
class CurrentEventBattles326Tests(unittest.TestCase):
    def test_all_selected_battle_cells_full_current_records_and_reproducible_bytes(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.reference();data=r['data'];self.assertEqual(data['counts'],{'events':9,'document_cells':13,'choices':12,'admitted_choice_stage_refs':20,'excluded_refs':3,'unbound_refs':0,'admitted_stage_ids':17});self.assertEqual(len(data['originals']['scenes']),36);self.assertEqual(set(data['originals']['stages']),model.SUPPORTED_STAGES)
        comparison=data['complete_selected_record_comparison_to_baseline'];changed={(g,k)for g,rows in comparison.items()for k,same in rows.items()if not same}
        self.assertEqual(changed,{('choices','choice_ro6_end4_3'),('scenes','scene_ro6_end4_enter'),('scenes','scene_ro6_end4_1'),('scenes','scene_ro6_end4_2'),('stages','ro6_s_1')})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for group,rows in data['originals'].items():
            table='choiceScenes'if group=='scenes'else group
            for key,value in rows.items():self.assertEqual(value,current[table][key]);self.assertIs(comparison[group][key],old[table].get(key)==value)
        self.assertFalse(data['complete_event_option_pool']);self.assertFalse(data['parent_script_restored']);self.assertIsNone(r['actual_stage_id'])
    def test_three_explicit_emergency_cells_exclude_normal_but_no_exclusion_from_omission(self):
        r=model.reference()
        for cid,normal,urgent in(('choice_ro6_bat3_5','ro6_t_3','ro6_e_t_3'),('choice_ro6_bat4_5','ro6_t_4','ro6_e_t_4'),('choice_ro6_bat5_9','ro6_t_5','ro6_e_t_5')):
            c=model.choice(r,cid);self.assertTrue(c['explicit_emergency']);self.assertEqual(c['stage_ids'],[urgent]);self.assertEqual(c['excluded_stage_ids'],[normal]);self.assertNotIn(normal,{x['id']for x in model.stage_rows(r,cid)})
        for cid in('choice_ro6_bat3_3','choice_ro6_bat4_3','choice_ro6_bat5_5'):self.assertEqual(len(model.stage_rows(r,cid)),2);self.assertFalse(model.choice(r,cid)['explicit_emergency'])
    def test_black_three_names_six_configs_same_level_per_name_not_six_battles(self):
        r=model.reference('黑诞');c=model.choice(r,'choice_ro6_normal2_2');self.assertFalse(c['explicit_emergency']);self.assertEqual(len(c['pages']),3);self.assertEqual(len(c['stage_ids']),6);self.assertEqual(c['excluded_stage_ids'],[])
        for p in c['pages']:
            self.assertEqual(len(p['admitted_stage_ids']),2);self.assertEqual(len({r['data']['originals']['stages'][s]['levelId']for s in p['admitted_stage_ids']}),1);self.assertIsNone(p['actual_stage_id'])
        self.assertIn('不表示一次连续进入',model.player_text(r,c['id']));self.assertTrue(all('同名配置'in model.stage_label(r,c['id'],s)for s in c['stage_ids']))
    def test_repeated_lake_cell_not_duplicate_option_reward_or_map_edge(self):
        r=model.reference('湖中仙女');c=model.choice(r,'choice_ro6_bat5_5');self.assertEqual(len(r['rows']),2);self.assertEqual(len(c['document_cells']),2);self.assertEqual(len(c['stage_ids']),2);self.assertNotEqual(c['document_cells'][0]['row'],c['document_cells'][1]['row']);self.assertIn('不当作两次战斗',model.player_text(r,c['id']))
    def test_forward_related_scenes_not_claimed_parents_and_reverse_exact_stage(self):
        d=model.packet()['data']
        for key,c in d['choices'].items():
            self.assertIsNone(c['parent_scene_id']);self.assertEqual(model.locate('choices',key)['choice_id'],key)
            for sid in c['stage_ids']:
                r=model.reference(stage_id=sid);self.assertIn(key,{x['id']for x in r['rows']});self.assertEqual([v['id']for v in model.stage_rows(r,key)],[sid])
        for key,s in d['originals']['scenes'].items():
            target=model.locate('scenes',key);self.assertEqual(target['event_id'],s['title']);self.assertIsNone(target['choice_id']);self.assertEqual(target['source_scene_id'],key)
        self.assertIsNone(model.reference(stage_id='ro6_b_6'));self.assertFalse(model.stage_has_reference('ro6_b_6'));self.assertIsNone(model.reference('黑诞','ro6_t_13'));self.assertIsNone(model.locate('choices','choice_ro6_normal2_999'))
    def test_every_file_actual_corruption_restoration_and_complete_primary_drift(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    p=root/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);p.write_bytes(raw);self.assertIsNotNone(model.packet())
        for table,key in(('choices','choice_ro6_normal2_2'),('stages','ro6_c_6'),('choiceScenes','scene_ro6_normal2_enter')):
            p=deepcopy(model.version.packet());self.assertIn(key,p['current']['details'][table]);p['current']['details'][table][key]['unexpected_drift']=True
            with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())
    def test_builder_rejects_duplicate_full_caption_and_mixed_level_family(self):
        for mode in('caption','level'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);p=root/builder.CURRENT;d=json.loads(p.read_bytes())
                if mode=='caption':d['details']['choices']['duplicate']=deepcopy(d['details']['choices']['choice_ro6_bat3_3'])
                else:d['details']['stages']['ro6_c_6']['levelId']='different/unproven/map'
                p.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)

if __name__=='__main__':unittest.main()
