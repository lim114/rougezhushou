import json,unittest
from copy import deepcopy
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from PySide6.QtWidgets import QApplication
from rouge import public_archive as archive,public_compendium as catalog,expansion_reference as ref
from rouge.player_inventory import inventory_rows,InventoryPanel

class Compendium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gui=QApplication.instance()or QApplication([])
        cls.data=archive.load();cls.packet=ref.packet();cls.docs=catalog.resolve(cls.data,'dlc1',cls.packet)
    def test_complete_exact_identity_coverage(self):
        self.assertEqual(len(self.docs),251)
        for key,row in self.docs.items():
            item=self.packet['current']['details']['items'][key]
            self.assertEqual((row['name'],row['iconId']),(item['name'],item['iconId']))
    def test_original_all_fields_preserved(self):
        raw=json.loads(catalog.SUPPLEMENT.read_bytes())
        self.assertEqual(self.data['versioned_collectibles'],raw['versioned_collectibles'])
        self.assertEqual(len({r['category']for r in self.docs.values()}),8)
    def test_legacy_snapshot_not_modified(self):
        historic=json.loads(archive.DEFAULT.read_bytes());before=deepcopy(historic)
        upgraded=catalog.complete(historic)
        self.assertEqual(historic,before);self.assertNotIn('versioned_collectibles',historic)
        self.assertEqual(upgraded['items'],historic['items']);self.assertEqual(upgraded['versions'],historic['versions'])
    def test_other_source_never_borrows_supplement(self):
        data=json.loads(archive.DEFAULT.read_bytes());data['provenance']['archive']['sha256']='different'
        self.assertNotIn('versioned_collectibles',catalog.complete(data));self.assertEqual(catalog.resolve(data,'dlc1'),{})
    def test_missing_or_tampered_supplement_not_used(self):
        data=json.loads(archive.DEFAULT.read_bytes())
        with patch.object(catalog,'SUPPLEMENT_SHA','wrong'):self.assertNotIn('versioned_collectibles',catalog.complete(data))
        with patch.object(catalog,'SUPPLEMENT',Path('missing-public-compendium')):self.assertNotIn('versioned_collectibles',catalog.complete(data))
    def test_version_never_falls_back(self):
        self.assertEqual(catalog.resolve(self.data,'base'),{});self.assertEqual(catalog.resolve(self.data,'dlc2'),{})
    def test_ambiguous_or_partial_identity_not_bound(self):
        row=next(iter(self.docs.values()));p=deepcopy(self.packet);items=p['current']['details']['items']
        key=next(k for k,r in self.docs.items()if r is row);items['duplicate']=deepcopy(items[key])
        self.assertNotIn(key,catalog.resolve(self.data,'dlc1',p))
        del items['duplicate'];items[key]['iconId']='different';self.assertNotIn(key,catalog.resolve(self.data,'dlc1',p))
        items[key]['iconId']=row['iconId'];items[key]['name']='different';self.assertNotIn(key,catalog.resolve(self.data,'dlc1',p))
    def test_duplicate_bad_count_and_text_rejected(self):
        for mode in ('duplicate','count','text'):
            data=deepcopy(self.data);p=data['versioned_collectibles']['dlc1']
            if mode=='duplicate':p['items'].append(deepcopy(p['items'][0]));p['count']+=1
            if mode=='count':p['count']+=1
            if mode=='text':p['items'][0]['effect']=False
            with self.assertRaises(ValueError):archive.validate(data)
    def test_all_six_tool_pool_names_and_effects(self):
        pool=next(p for p in self.data['versions']['dlc1']if all('rogue_6_active_tool_'+str(i)in p['collectibles']for i in range(1,7)))
        rows={r['id']:r for r in archive.members(self.data,pool,version='dlc1')}
        for i in range(1,7):
            key='rogue_6_active_tool_'+str(i);self.assertEqual(rows[key]['name'],self.docs[key]['name']);self.assertEqual(rows[key]['effect'],catalog.effect_text(self.docs[key]['effect']))
            self.assertIsNone(rows[key]['rate'])
    def test_search_missing_tool_and_grade_effect(self):
        self.assertTrue(archive.pool_rows(self.data,'dlc1','支援雾机'))
        self.assertTrue(archive.pool_rows(self.data,'dlc1','混沌化'))
    def test_grade_readout_and_base_separation(self):
        new=inventory_rows({},'精选兽肉罐头',False,public_data=self.data,version='dlc1');base=inventory_rows({},'精选兽肉罐头',False,public_data=self.data,version='base')
        self.assertEqual({r['id']for r in new},{'rogue_6_relic_legacy_22'+suffix for suffix in ('','_a','_b','_c')});self.assertIn('【混沌化】',new[0]['usage']);self.assertIn('\n【半结构化】',new[0]['usage'])
        self.assertIsNone(base[0]['compendium']);self.assertNotIn('【混沌化】',base[0]['usage'])
    def test_categories_intersect_existing_filters_without_state_changes(self):
        state={'relics':{i:{}for i in self.docs}};before=deepcopy(state)
        rows=inventory_rows(state,public_data=self.data,version='dlc1',category='生存助力',exchange=True)
        self.assertTrue(rows);self.assertTrue(all(r['category']=='生存助力'and r['exchange']is True and r['held']for r in rows));self.assertEqual(state,before)
        self.assertEqual(inventory_rows(state,public_data=self.data,version='base',category='生存助力'),[])
    def test_refresh_preserves_selection_reading_and_cache_bytes(self):
        with TemporaryDirectory()as d:
            path=Path(d)/'cache.json';path.write_bytes(archive.DEFAULT.read_bytes());before=path.read_bytes();panel=InventoryPanel(SimpleNamespace(state={}),path)
            try:
                panel.held.setChecked(False);panel.search.setText('精选兽肉罐头');panel.entries.setCurrentRow(0)
                selected=panel.entries.currentItem().data(256);text=panel.detail.toPlainText();self.assertIn('取得与解锁',text)
                panel.refresh();self.assertEqual(panel.entries.currentItem().data(256),selected);self.assertEqual(panel.detail.toPlainText(),text);self.assertEqual(path.read_bytes(),before)
                path.unlink();panel.refresh();self.assertNotIn('路标档案馆 · 拓展一图鉴',panel.detail.toPlainText());self.assertIsNone(panel.source_index)
            finally:panel.close()
    def test_normalize_preserves_provided_catalog_instead_of_old_supplement(self):
        pack={'items':[{'name':'新资料','iconId':'new','effect':'不同来源的新说明'}],'count':1}
        raw={'schemaVersion':2,'archive':{'topicId':'rogue_6'},'classifier':{'items':[],'versionedCollectibles':{'dlc1':pack}},'pools':{'pools':[],'defaultVersionId':'base'}}
        events={'schemaVersion':1,'topicId':'rogue_6','floors':[],'specialLayers':[]}
        data=archive.normalize(raw,events,{});self.assertEqual(data['versioned_collectibles']['dlc1'],pack)
        self.assertEqual(catalog.complete(data)['versioned_collectibles']['dlc1'],pack)
