from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
from collections import Counter
import json,shutil,unittest
from rouge import current_exchange_reference as model
from scripts import build_current_exchange_reference_323 as builder
ROOT=Path(__file__).resolve().parents[1]


def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)


class CurrentExchangeReference323Tests(unittest.TestCase):
    def test_exact_full_catalogue_current_not_effect_rows_or_old272(self):
        data,manifest=builder.build();self.assertEqual(data,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes())
        r=model.packet();rows=r['data']['catalogue'];p=model.version.packet()['current']['details'];self.assertEqual(len(rows),284);self.assertEqual({x['id']:x['item']for x in rows},{k:v for k,v in p['items'].items()if v['type']=='RELIC'})
        self.assertEqual(Counter(x['can_offer']for x in rows),{True:259,False:25});self.assertEqual(Counter(x['rarity']for x in rows),{'NORMAL':66,'RARE':123,'SUPER_RARE':95})
        self.assertEqual(Counter(x['change']for x in rows),{'unchanged':272,'added':12});self.assertEqual(r['data']['scope']['effect_definition_rows'],395);self.assertIsNone(r['actual_reward_pool']);self.assertFalse(r['legacy_catalogue_replaced'])

    def test_every_new_and_old_offer_flag_query_preserves_exact_boolean(self):
        r=model.packet()
        for row in r['data']['catalogue']:
            self.assertIs(type(row['can_offer']),bool);self.assertEqual(model.target_entry('relics',row['id']),{'tab':'items','item_id':row['id'],'group_id':None});text=model.item_text(r,row['id']);self.assertIn(row['name'],text);self.assertIn('不能说明能否换到',text)
        for suffix in('7','8','9','10'):
            row=next(x for x in r['data']['catalogue']if x['id']=='rogue_6_relic_final_'+suffix);self.assertFalse(row['can_offer']);self.assertEqual(row['change'],'added')

    def test_filter_intersections_and_invalid_types_never_make_up_pool(self):
        r=model.packet();self.assertEqual(len(model.catalogue_rows(r,can_offer=False,change='added')),4);self.assertEqual(len(model.catalogue_rows(r,can_offer=True,change='added')),8);self.assertEqual(len(model.catalogue_rows(r,query='祭日之契')),1);self.assertEqual(model.catalogue_rows(r,query='不存在的名称'),[])
        for kwargs in({'can_offer':1},{'can_offer':'false'},{'rarity':'all'},{'change':False},{'query':None}):
            with self.assertRaises(ValueError):model.catalogue_rows(r,**kwargs)
        self.assertEqual(model.catalogue_rows(None),[])

    def test_all_document_cells_candidates_and_source_quantities_no_parent_guess(self):
        r=model.packet();groups=r['data']['document_groups'];self.assertEqual((len(groups),sum(len(g['document_cells'])for g in groups),len(r['data']['original_choices'])),(9,13,43));self.assertNotIn('choice_leave',r['data']['original_choices'])
        for row in groups:
            self.assertIsNone(row['actual_candidate_id']);self.assertIsNone(row['actual_quantity']);self.assertIsNone(row['actual_reward_pool']);self.assertFalse(row['game_parent_scene_verified']);text=model.document_text(r,row['id']);self.assertNotIn('choice_ro6_',text)
        self.assertEqual([(g['title'],g['explicit_reward_quantity'],g['reward_resource'])for g in groups if g['explicit_reward_quantity']is not None],[('接过藏品',1,'收藏品'),('接过零件',1,'零件')])
        cost=next(g for g in groups if g['title']=='复原“文明”');self.assertEqual(cost['consumption_reference'],{'quantity':2,'resource':'自然物','random':True})
        named=next(g for g in groups if g['title']=='等待结果');self.assertEqual(named['associated_relic_ids'],['rogue_6_relic_final_6']);self.assertIsNone(named['explicit_reward_quantity']);self.assertIn('不自动补成1件',model.document_text(r,named['id']))

    def test_exact_repeated_candidates_not_assigned_to_first_or_second_exchange(self):
        r=model.packet();groups=r['data']['document_groups'];scrap=next(x for x in groups if x['title']=='接过零件');self.assertEqual(len(scrap['primary_candidate_ids']),16);self.assertEqual(len(scrap['document_cells']),2)
        for key in('choice_ro6_sacrifice1_20','choice_ro6_sacrifice1_21','choice_ro6_sacrifice2_22','choice_ro6_sacrifice2_23'):self.assertIn(key,scrap['primary_candidate_ids']);self.assertEqual(model.target_entry('choices',key),{'tab':'document','item_id':None,'group_id':scrap['id']})
        for key in r['data']['related_scenes']:self.assertEqual(model.target_entry('scenes',key),{'tab':'document','item_id':None,'group_id':None})
        for cat,key in(('choices','choice_leave'),('choices','choice_ro6_sacrifice2_unknown'),('stages','ro6_b_6'),('scenes','scene_ro6_end2_enter'),('relics','rogue_6_end_2_change')):self.assertIsNone(model.target_entry(cat,key))

    def test_each_actual_public_input_damage_clears_and_restores(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())

    def test_primary_live_record_drift_does_not_keep_stale_offer_status(self):
        r=deepcopy(model.version.packet());r['current']['details']['items']['rogue_6_relic_final_8']['canSacrifice']=True
        with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
        r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_sacrifice2_23']['description']='获得2件零件'
        with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())

    def test_builder_rejects_invalid_flags_missing_candidates_and_empty_description_alias(self):
        for mode in('flag','missing','empty_description_alias'):
            with self.subTest(mode=mode),TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;p=json.loads(f.read_bytes());d=p['details']
                if mode=='flag':d['items']['rogue_6_relic_final_8']['canSacrifice']=0
                elif mode=='missing':del d['choices']['choice_ro6_sacrifice2_23']
                else:d['choices']['extra_full_caption_alias']=deepcopy(d['choices']['choice_ro6_sacrifice1_5'])
                f.write_bytes(builder.encoded(p))
                with self.assertRaises(ValueError):builder.build(root)
        self.assertNotIn('choice_leave',json.loads(builder.build()[0])['original_choices'])


if __name__=='__main__':unittest.main()
