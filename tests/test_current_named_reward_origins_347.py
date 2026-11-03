from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,subprocess,sys,unittest
from rouge import current_named_reward_origins as model,current_reward_origins as unified
def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())
class CurrentNamedRewardOrigins347Tests(unittest.TestCase):
    def test_build_all11_new_rewards_exact_current_records_and_seven_providers(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_named_reward_origins_347.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        d=model.packet()['data'];self.assertEqual(len(d['rows']),11);self.assertEqual(len({r['item_id']for r in d['rows']}),11);self.assertEqual(len({r['reader_key']for r in d['rows']}),7);current=model.version.packet()['current']['details']
        for row in d['rows']:self.assertEqual(row['item'],current['items'][row['item_id']]);self.assertEqual(row['choice'],current['choices'][row['choice_id']]);self.assertEqual(row['target'],model.providers()[row['reader_key']].locate('choices',row['choice_id']))
    def test_existing_six_rows_and_three_items_unchanged_combined14_items17_choices(self):
        old=unified.packet()['data']['rows'];new=model.packet()['data']['rows'];self.assertEqual((len(old),len(new)),(6,11));self.assertEqual(len({r['item_id']for r in old+new}),14)
        for iid in {r['item_id']for r in old}:self.assertNotIn(iid,model.ITEM_IDS);self.assertNotIn('kind',unified.reference('scrap'if iid=='rogue_6_scrap_G_12'else'relics',iid))
    def test_roles_held_consumed_and_hints_not_acquisition_rows(self):
        rows=model.packet()['data']['rows'];hunt=next(r for r in rows if r['item']['name']=='猎印');self.assertEqual(hunt['item_id'],'rogue_6_relic_cargo_12');self.assertEqual(hunt['original_item_pointer'],hunt['item_id']);self.assertIn('持有笼控器是条件',model.player_text(model.reference('relics',hunt['item_id']),hunt['key']))
        key=next(r for r in rows if r['item']['name']=='源私钥');self.assertEqual(key['choice_id'],'choice_ro6_surprise_1');self.assertTrue(all(not r['choice_id'].startswith('choice_ro6_end3_')for r in rows));self.assertNotIn('rogue_6_scrap_G_12',model.ITEM_IDS)
    def test_missing_key_pointer_and_outer_quote_differences_not_fuzzy_name_binding(self):
        rows=model.packet()['data']['rows'];missing=[r for r in rows if r['original_item_pointer']is None];self.assertEqual(len(missing),1);self.assertEqual(missing[0]['item']['name'],'源私钥');self.assertEqual(missing[0]['binding_basis'],'unique_full_literal_name_missing_original_pointer')
        for row in rows:
            if row not in missing:self.assertEqual(row['binding_basis'],'explicit_original_item_pointer_and_full_name');self.assertEqual(row['original_item_pointer'],row['item_id'])
        self.assertEqual({r['item']['name']for r in rows if r['reader_key']=='resources'},{'他缚','“剑锤”','一串钱伥','翱翼','虬蜕'})
    def test_strict_gate_rejects_wrong_pointer_consumption_or_wrong_name(self):
        mods=model.providers();packets={k:p.packet()for k,p in mods.items()};current=model.version.packet()['current']['details'];cid='choice_ro6_normal2_1'
        for change in('pointer','role','name'):
            c=deepcopy(current);p=deepcopy(packets);v=c['choices'][cid]
            if change=='pointer':v['displayData']['itemId']='rogue_6_relic_cargo_8'
            elif change=='role':v['description']='交出收藏品<@ro6.lose>猎印</>'
            else:v['description']='持有笼控器，获得收藏品<@ro6.get>猎影</>'
            p['encounters']['data']['originals']['choices'][cid]=deepcopy(v)
            with self.assertRaises(ValueError):model.source_rows(p,c,mods)
    def test_quantities_and_actual_state_unknown_not_complete_pool_or_auto_apply(self):
        r=model.reference('relics','rogue_6_relic_final_6');self.assertIsNone(r['actual_quantity']);self.assertFalse(r['run_updated']);self.assertFalse(r['complete_acquisition_pool']);self.assertIsNone(r['actual_received']);self.assertIsNone(r['actual_eligible']);text=model.player_text(r,r['rows'][0]['key']);self.assertIn('不能在本项再扣一次',text);self.assertIn('不补成1件',text)
        for iid in('rogue_6_relic_cargo_13','rogue_6_relic_cargo_11','rogue_6_relic_final_4','rogue_6_relic_artifact_4'):
            r=model.reference('relics',iid);t=model.player_text(r,r['rows'][0]['key']);self.assertIn('仍未知',t);self.assertIsNone(r['rows'][0]['actual_quantity'])
    def test_each_manifest_member_damage_fails_closed_after_success_and_restores(self):
        with TemporaryDirectory()as f:
            root=Path(f);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    p=root/name;raw=p.read_bytes();self.assertIsNotNone(model.packet());p.write_bytes(raw+b'x');self.assertIsNone(model.packet(),name);p.write_bytes(raw)
    def test_each_upstream_provider_unavailable_closes_new_sources_not_old338(self):
        for key,provider in model.providers().items():
            with patch.object(provider,'packet',return_value=None):self.assertIsNone(model.packet(),key);self.assertIsNotNone(unified.reference('relics','rogue_6_relic_artifact_5'))
    def test_unsupported_category_bad_ids_and_mutable_return_isolation(self):
        for a,b in[(True,'rogue_6_relic_final_6'),('scrap','rogue_6_relic_final_6'),('relics',True),('relics','rogue_6_relic_final_6x')]:self.assertIsNone(model.reference(a,b))
        r=model.reference('relics','rogue_6_relic_cargo_12');r['rows'][0]['target'].clear();r['item']['name']='x';fresh=model.reference('relics','rogue_6_relic_cargo_12');self.assertTrue(fresh['rows'][0]['target']);self.assertEqual(fresh['item']['name'],'猎印')
if __name__=='__main__':unittest.main()
