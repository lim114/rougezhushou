from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_startup as m
def clone(root):
    for name in(m.MANIFEST,*json.loads((m.ROOT/m.MANIFEST).read_bytes())['files']):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((m.ROOT/name).read_bytes())
class CurrentStartup350Tests(unittest.TestCase):
    def test_build_twelve_current_full_records_and_six_direct_inherited_bindings(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_startup_350.py','--check'],cwd=m.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=m.reference();self.assertEqual(len(r['choices']),12);d=r['data'];self.assertEqual(len(d['regular_ids']),6);self.assertEqual(len(d['inherited_ids']),6)
        current=m.version.packet()['current']['details']
        for cid,row in r['choices'].items():
            self.assertEqual(row['original'],current['choices'][cid]);self.assertIsNone(row['next_scene_id']);self.assertEqual(row['stage_ids'],[])
            if row['kind']=='inherited':self.assertIn(row['force_add_choice_buff'],current['relics'][row['legacy_id']]['buffs']);self.assertTrue(row['source_scene_pointer_verified'])
            else:self.assertFalse(row['source_scene_pointer_verified'])
        self.assertIsNone(r['actual_displayed_choice_ids']);self.assertIsNone(r['actual_received']);self.assertFalse(r['run_updated'])
    def test_previous_regions_boundary_not_current_floor_and_mode_scope(self):
        cid='choice_ro6_startbuff_1'
        for regions,want in[(None,None),(0,False),(1,False),(2,True),(3,True)]:
            r=m.reference(previous_regions=regions,mode='NORMAL');self.assertIs(m.choice_reference(r,m.SCENE,cid)['listed_condition_match'],want)
        r=m.reference(previous_regions=2,mode='OTHER');self.assertIsNone(m.choice_reference(r,m.SCENE,cid)['listed_condition_match'])
        for cid in r['data']['inherited_ids']:self.assertIs(m.choice_reference(r,m.SCENE,cid)['listed_condition_match'],False)
    def test_six_same_name_inherited_sources_never_interchange_or_infer_from_holding(self):
        r=m.reference(previous_regions=2,mode='NORMAL');ids=r['data']['inherited_ids']
        self.assertEqual(len({r['data']['originals']['items'][r['choices'][cid]['legacy_id']]['name']for cid in ids}),1)
        for selected in ids:
            checked=m.reference(previous_regions=2,mode='NORMAL',inherited=selected)
            for cid in ids:self.assertIs(m.choice_reference(checked,m.SCENE,cid)['listed_condition_match'],cid==selected)
        self.assertIn('当前持有的襁褓生灵不能证明',m.player_text(r,m.SCENE,ids[0]))
    def test_cost_boundary_and_deferred_rewards_no_totals_or_new_mechanics(self):
        for gold,want in[(None,None),(5,False),(6,True),(7,True)]:
            r=m.reference(previous_regions=2,mode='NORMAL',gold=gold);row=m.choice_reference(r,m.SCENE,'choice_ro6_startbuff_3');self.assertIs(row['listed_condition_match'],want);self.assertIsNone(row['actual_received'])
        r=m.reference();self.assertIn('不是当前生命值',m.player_text(r,m.SCENE,'choice_ro6_startbuff_4'));self.assertIn('不在开局提前计入库存',m.player_text(r,m.SCENE,'choice_ro6_startbuff_12'));self.assertIn('不新增攻击或生命的计算假设',m.player_text(r,m.SCENE,'choice_ro6_startbuff_10'))
    def test_every_manifest_member_loss_fails_after_success_then_recovers(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(m,'ROOT',root):
                for name in(m.MANIFEST,*json.loads((root/m.MANIFEST).read_bytes())['files']):
                    path=root/name;raw=path.read_bytes();self.assertIsNotNone(m.packet());path.write_bytes(raw+b'x');self.assertIsNone(m.packet(),name);path.write_bytes(raw);self.assertIsNotNone(m.packet())
    def test_groups_exact_targets_types_and_mutable_isolation(self):
        for group in('regular','inherited'):
            r=m.reference(group=group);self.assertEqual(len(r['scenes'][m.SCENE]['choice_ids']),6)
        for kwargs in({'previous_regions':True},{'gold':True},{'previous_regions':-1},{'mode':'NORMALx'},{'group':True},{'inherited':'rogue_6_start_1'}):self.assertIsNone(m.reference(**kwargs))
        self.assertIsNone(m.locate('choices',True));self.assertIsNone(m.locate('choices','choice_ro6_startbuff_0'))
        for cid in m.reference()['choices']:self.assertEqual(m.locate('choices',cid)['choice_id'],cid)
        r=m.reference();r['choices'].clear();self.assertEqual(len(m.reference()['choices']),12)
if __name__=='__main__':unittest.main()
