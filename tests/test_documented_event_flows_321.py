from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from hashlib import sha256
import json, shutil, unittest
from rouge import documented_event_flows as model
from scripts import build_documented_event_flows_321 as builder

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'scene_ro6_end4_enter': ['choice_ro6_end4_1', 'choice_ro6_end4_2'],
    'scene_ro6_end4_1': ['choice_ro6_end4_3'], 'scene_ro6_end4_2': [],
    'scene_ro6_end5_enter': ['choice_ro6_end5_1', 'choice_ro6_end5_3', 'choice_ro6_end5_5'],
    'scene_ro6_end5_1': ['choice_ro6_end5_2'], 'scene_ro6_end5_2': ['choice_ro6_end5_4'], 'scene_ro6_end5_3': [],
    'scene_ro6_revive_enter': ['choice_ro6_revive_1', 'choice_ro6_revive_3'],
    'scene_ro6_revive_1': ['choice_ro6_revive_2'], 'scene_ro6_revive_2': [],
}


def clone(root):
    manifest = json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in (model.MANIFEST, *manifest['files']):
        target = root/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, target)


class DocumentedEventFlows321Tests(unittest.TestCase):
    def test_complete_document_tables_match_explicit_scene_map_and_rebuild_bytes(self):
        data, manifest = builder.build(); self.assertEqual(data, (ROOT/model.DATA).read_bytes()); self.assertEqual(manifest, (ROOT/model.MANIFEST).read_bytes())
        ref = model.packet(); self.assertIsNotNone(ref); d = ref['data']
        self.assertEqual({k:v['choice_ids'] for k,v in d['scenes'].items()}, EXPECTED)
        self.assertEqual((len(d['events']),len(d['choices']),len(d['originals']['items']),len(d['originals']['stages'])), (3,11,2,1))
        self.assertEqual(len({c for cs in EXPECTED.values() for c in cs}),11)
        for key in ('complete_game_option_pool','original_game_parent_choice_script_restored','generation_prerequisites_restored','actual_server_verified','run_state_updated'): self.assertIs(d[key],False)
        self.assertIsNone(ref['actual_eligible']); self.assertIsNone(ref['actual_received'])

    def test_trade_choice_has_exact_documented_battle_destination_not_type_inference(self):
        r = model.reference('button'); c = model.choice_reference(r,'scene_ro6_end4_1','choice_ro6_end4_3')
        self.assertEqual(r['data']['originals']['choices'][c['id']]['type'],'TRADE'); self.assertEqual(c['stage_ids'],['ro6_s_1'])
        self.assertIn('灰坑', model.player_text(r,c['scene_id'],c['id']))
        self.assertEqual([k for k,c in r['data']['choices'].items() if c['stage_ids']],['choice_ro6_end4_3'])

    def test_scene_membership_not_prefix_or_shared_title(self):
        for event in ('button','blueprint','revive'):
            r = model.reference(event)
            for sid,ids in EXPECTED.items():
                if sid not in r['scenes']: continue
                self.assertEqual(model.event_for_scene(sid),event)
                for cid in r['choices']:
                    self.assertEqual(model.choice_reference(r,sid,cid) is not None,cid in ids)
        for value in (None,False,123,'scene_ro6_end5_missing','scene_ro6_final1_enter'):
            self.assertIsNone(model.event_for_scene(value));self.assertIsNone(model.reference(value))

    def test_known_costs_rewards_and_unknown_rounding_are_plain_text(self):
        r=model.reference('revive'); text=model.player_text(r,'scene_ro6_revive_enter','choice_ro6_revive_1')
        self.assertIn('生命',text);self.assertIn('整数处理尚未核验',text);self.assertIn('不会扣除资源',text)
        r=model.reference('blueprint');t=model.player_text(r,'scene_ro6_end5_enter','choice_ro6_end5_1');self.assertIn('1件珍贵收藏品',t);self.assertIn('完整随机池仍未知',t)
        for sid in ('scene_ro6_end5_3',):self.assertIn('不补入',model.player_text(r,sid))
        self.assertNotIn('choice_ro6_',text);self.assertNotIn('scene_ro6_',text)

    def test_every_pinned_public_input_damage_fails_closed_and_restores(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);clone(root);manifest=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in (model.MANIFEST,*manifest['files']):
                    file=root/name;raw=file.read_bytes();file.write_bytes(raw+b' ')
                    self.assertIsNone(model.packet(),name);file.write_bytes(raw);self.assertIsNotNone(model.packet(),name)

    def test_current_primary_record_drift_rejects_even_unchanged_excerpt(self):
        raw=model.version.packet();mutated=deepcopy(raw);mutated['current']['details']['choices']['choice_ro6_end4_3']['type']='BATTLE'
        with patch.object(model.version,'packet',return_value=mutated):self.assertIsNone(model.packet())
        with patch.object(model.version,'packet',return_value=None):self.assertIsNone(model.packet())

    def test_builder_rejects_absent_ambiguous_and_contradictory_current_text(self):
        for mode in ('missing','ambiguous','next','battle_hint','stage_ambiguous'):
            with self.subTest(mode=mode),TemporaryDirectory()as folder:
                root=Path(folder);clone(root);file=root/builder.CURRENT;current=json.loads(file.read_bytes());d=current['details']
                if mode=='missing':del d['choices']['choice_ro6_end4_3']
                elif mode=='ambiguous':d['choices']['different_id']=deepcopy(d['choices']['choice_ro6_end4_3'])
                elif mode=='next':d['choices']['choice_ro6_end4_1']['nextSceneId']='scene_ro6_end4_2'
                elif mode=='battle_hint':d['choices']['choice_ro6_end4_3']['displayData']['funcIconId']='unknown'
                else:d['stages']['different_id']=deepcopy(d['stages']['ro6_s_1'])
                file.write_bytes(builder.encoded(current))
                with self.assertRaises(ValueError):builder.build(root)

    def test_builder_rejects_changed_revision_or_missing_document_branch(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.PACK/'source-receipt.json';r=json.loads(file.read_bytes());r['revision']=0;file.write_bytes(builder.encoded(r))
            with self.assertRaises(ValueError):builder.build(root)
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.PACK/'documented-tables.html';raw=file.read_bytes();raw=raw.replace('大红按钮'.encode(), '无关事件'.encode());file.write_bytes(raw)
            rp=root/model.PACK/'source-receipt.json';r=json.loads(rp.read_bytes());r['selected_sha256']=sha256(raw).hexdigest();r['selected_bytes']=len(raw);rp.write_bytes(builder.encoded(r))
            with self.assertRaises(ValueError):builder.build(root)


if __name__=='__main__':unittest.main()
