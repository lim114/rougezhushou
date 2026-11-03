from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_node_readers as model
from scripts import build_current_node_readers_332 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
class CurrentNodeReaders332Tests(unittest.TestCase):
    def test_reproducible_all25_groups23_titles8_readers116_exact_links(self):
        d,l,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(l,(ROOT/model.PACK/'source-ledger.json').read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();self.assertEqual(r['data']['counts'],{'catalogue_groups':25,'current_event_titles':23,'reader_types':8,'exact_scene_links':116,'unsupported_new_event_titles':3})
        for row in r['data']['bindings'].values():
            b=model.binding_for(row['expected_summary']);self.assertIsNotNone(b,row['title']);self.assertEqual(b['reader'],row['reader']);self.assertTrue(model.same(b,model.recheck(b)));self.assertIsNone(b['actual_same_game_version']);self.assertFalse(b['actual_node_version_confirmed']);self.assertFalse(b['run_updated']);self.assertIsNone(b['actual_scene'])
        self.assertEqual({v['title']for v in r['data']['unsupported_new_events']},{'大红按钮','制图桌','手术祭坛'})
    def test_each_admitted_link_checks_exact_current_record_text_not_title_only(self):
        data=model.packet()['data'];total=0
        for row in data['bindings'].values():
            for link in row['exact_scene_links']:
                total+=1;s=next(s for s in row['expected_legacy_event']['scenes']if s['key']==link['legacy_scene_key']);key=link['current_original_scene_id'];self.assertIn(key,s['game_scene_ids']);self.assertEqual(builder.canonical(s['description']),builder.canonical(row['current_original_scenes'][key]['description']))
        self.assertEqual(total,116);summary=deepcopy(data['bindings']['community_group_034']['expected_summary']);summary['id']='community_group_999';self.assertIsNone(model.binding_for(summary));summary['id']='community_group_034';summary['title']='金色凝滞';self.assertIsNone(model.binding_for(summary));del summary['entry'];self.assertIsNone(model.binding_for(summary))
    def test_full_warm_catalogue_and_reading_object_drift_rejected_with_strict_types(self):
        row=model.packet()['data']['bindings']['community_group_000'];bad=deepcopy(row['expected_legacy_event']);bad['scenes'][0]['choices'][0]['description']='unverified'
        with patch.object(model.node_catalog,'_event',return_value=bad):self.assertIsNone(model.binding_for(row['expected_summary']))
        reading=deepcopy(row['expected_summary']);reading['scenes']=bad['scenes'];self.assertIsNone(model.binding_for(reading));self.assertFalse(model.same(True,1));self.assertFalse(model.same([True],[1]))
    def test_current_reader_source_loss_is_optional_does_not_damage_old_catalogue(self):
        row=model.packet()['data']['bindings']['community_group_016'];old=deepcopy(model.node_catalog._event(row['legacy_event_id']))
        with patch('rouge.current_lake.reference',return_value=None):self.assertIsNone(model.binding_for(row['expected_summary']));self.assertEqual(model.node_catalog._event(row['legacy_event_id']),old)
        binding=model.binding_for(row['expected_summary']);binding['reader']='shop';self.assertIsNone(model.recheck(binding))
    def test_every_bridge_file_damage_fails_closed_and_recovery(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes());summary=model.packet()['data']['bindings']['community_group_000']['expected_summary']
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.binding_for(summary),name);f.write_bytes(raw);self.assertIsNotNone(model.binding_for(summary))
    def test_builder_rejects_same_title_with_no_exact_narrative_links(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            for _,_,file in builder.PROVIDERS:
                p=root/'rouge/data'/file;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'rouge/data'/file,p)
            p=root/builder.LEGACY;d=json.loads(p.read_bytes());event=next(e for e in d['events']if e['id']=='community_group_034')
            for scene in event['scenes']:scene['description']='unverified same title'
            p.write_bytes(builder.encoded(d))
            with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
