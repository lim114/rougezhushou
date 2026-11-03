from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from unittest.mock import patch
from collections import Counter
import json,shutil,unittest
from rouge import current_stage_directory as model
from scripts.build_current_stage_directory_317 import build,parse
ROOT=Path(__file__).resolve().parents[1]

class CurrentStageDirectory317Tests(unittest.TestCase):
    def test_exact_complete_directory_and_reproducible_source(self):
        raw,manifest=build();self.assertEqual(raw,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes());r=model.packet();self.assertIsNotNone(r);self.assertEqual(len(r['data']['rows']),184);self.assertEqual(len(r['data']['documented_entries']),77);self.assertTrue(all(x['documented_entry']for x in r['data']['rows'].values()));self.assertIsNone(r['actual_generation_pool'])
    def test_each_filter_is_exact_intersection_no_missing_or_duplicate_stages(self):
        ref=model.packet();all_rows=model.rows(reference=ref);seen=[]
        for floor,_ in model.FLOORS[1:]:
            selected=model.rows(floor,reference=ref);seen.extend(r['id']for r in selected)
            for kind,_ in model.KINDS[1:]:self.assertEqual(model.rows(floor,kind,reference=ref),[r for r in all_rows if r['floor']==floor and r['play_kind']==kind])
        self.assertEqual(Counter(seen),Counter(list(ref['data']['rows'])));self.assertEqual(len(set(seen)),184)
    def test_sixth_layer_regions_not_seventh_or_main_floor(self):
        for sid,region in [('ro6_n_7_1','盲目者所见'),('ro6_e_7_2','盲目者所见'),('ro6_b_7','盲目者所见'),('ro6_b_7_b','盲目者所见'),('ro6_n_6_1','源流交汇处')]:
            r=model.detail(sid);self.assertEqual(r['row']['floor'],'floor6');self.assertEqual(r['row']['region'],region)
        self.assertNotIn('floor7',dict(model.FLOORS))
    def test_special_challenges_do_not_inherit_previous_floor(self):
        r=model.packet();unknown=[x for x in r['data']['rows'].values()if x['floor']=='unknown'];self.assertEqual(len(unknown),22)
        for row in unknown:self.assertIn(row['kind'],('duck','duel','challenge','resident','shop'));self.assertEqual(row['documented_entry']['floor'],'unknown')
        gray=model.detail('ro6_s_1');self.assertEqual(gray['row']['floor'],'unknown');self.assertEqual(gray['row']['kind'],'challenge');self.assertIn('不能',model.player_text(gray))
    def test_normal_and_emergency_are_separate_not_suffix_guesses(self):
        ref=model.packet()
        for r in model.rows(kind='emergency',reference=ref):self.assertEqual(r['original_stage']['isElite'],1);self.assertEqual(r['kind'],'normal')
        for r in model.rows(kind='normal',reference=ref):self.assertEqual(r['original_stage']['isElite'],0);self.assertEqual(r['original_stage']['isBoss'],0)
        self.assertEqual(len(model.rows(kind='normal',reference=ref)),64);self.assertEqual(len(model.rows(kind='emergency',reference=ref)),64)
    def test_same_name_indices_stable_across_filters_not_version_selection(self):
        ref=model.packet();a=model.detail('ro6_b_7',reference=ref);b=model.detail('ro6_b_7_b',reference=ref);self.assertEqual(a['variant_count'],2);self.assertNotEqual(a['variant_index'],b['variant_index'])
        for sid in (a['row']['id'],b['row']['id']):self.assertIsNone(model.detail(sid)['actual_eligible']);self.assertFalse(model.detail(sid)['row']['whole_variant_pool_proven'])
        self.assertEqual([r['id']for r in model.rows('floor6','boss',reference=ref)if r['name']=='熄日'],['ro6_b_7','ro6_b_7_b'])
    def test_all_stage_originals_match_whole_current_source_when_available(self):
        path=ROOT/'.cache/p3-313-dlc2-research/roguelike-topic.json'
        if not path.is_file():self.skipTest('完整当前原件不可用，未计独立原表核对通过。')
        source=json.loads(path.read_bytes())['details']['rogue_6']['stages'];ref=model.packet();self.assertEqual(set(source),set(ref['data']['rows']))
        for sid,row in ref['data']['rows'].items():self.assertEqual(row['original_stage'],source[sid])
    def test_category_reset_and_duplicate_document_names_are_not_guessed(self):
        text=(ROOT/model.PACK/'stage-table-441984-excerpt.md').read_text('utf8');rows=parse(text);self.assertEqual(len(rows),77)
        with self.assertRaises(AssertionError):parse(text+text)
        for floor,kind in [('floor7',None),(None,'madeup')]:
            with self.assertRaises(ValueError):model.rows(floor,kind)
    def test_actual_public_source_corruption_and_wrong_manifest_rejected(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p=root/model.PACK/'region-label-excerpts.json';raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet());self.assertIsNone(model.rows());p.write_bytes(raw);self.assertIsNotNone(model.packet())
    def test_player_summary_distinguishes_pursuit_special_and_unknown(self):
        ref=model.packet()
        for row in ref['data']['rows'].values():
            info=model.detail(row['id'],reference=ref);text=model.player_text(info);self.assertIn('目录',text);self.assertIn('不证明',text)
            if row['kind']=='pursuit':self.assertIn('节点外事件',text)

if __name__=='__main__':unittest.main()
