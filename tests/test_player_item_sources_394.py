import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_inventory import InventoryPanel,inventory_rows
from rouge.player_item_sources import ItemSourceIndex,pool_label
from rouge import public_archive

def fixture():
    return {'schema':'rouge-public-archive-v1','items':{'a':{'id':'a','name':'同名藏品','effect':''},'b':{'id':'b','name':'同名藏品','effect':''}},'versions':{'base':[{'id':'pool1','name':'藏品','collectibles':['a'],'nodeBindings':[{'nodeName':'作战'}],'observedDistribution':{'interpretation':'observedFrequencyOnly','totalOccurrenceCount':10,'members':[{'itemId':'a','occurrenceCount':2,'totalOccurrenceCount':10,'occurrenceRate':.2}]}}], 'dlc1':[{'id':'input','name':'失与得：N藏品输入','collectibles':['a']},{'id':'pool2','name':'藏品','collectibles':['b']}]},'events':{'topicId':'rogue_6','floors':[],'specialLayers':[]},'default_version':'dlc1','version_applicability':'隔离资料，当前版本适用性待核验。'}

class ItemSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
    def test_exact_id_not_shared_name(self):
        model=ItemSourceIndex(fixture());self.assertEqual([p['id']for p in model.pools('dlc1','a')],['input']);self.assertEqual([p['id']for p in model.pools('dlc1','b')],['pool2']);self.assertEqual(model.pools('dlc1','同名藏品'),[])
    def test_versions_never_fall_back(self):
        model=ItemSourceIndex(fixture());self.assertEqual(model.pools('dlc2','a'),[]);self.assertIn('不可用',model.describe('dlc1','a','pool1'))
    def test_input_not_reward_pool(self):
        text=ItemSourceIndex(fixture()).describe('dlc1','a','input');self.assertIn('不是交换奖励池',text);self.assertIn('暂无可核对',text)
    def test_pool_condition_not_lost(self):
        data=fixture();data['versions']['base'][0]['description']='消耗2目标生命上限后领取'
        self.assertIn('消耗2目标生命上限',ItemSourceIndex(data).describe('base','a','pool1'))
    def test_source_time_requires_timezone_and_is_readable(self):
        data=fixture();distribution=data['versions']['base'][0]['observedDistribution'];distribution['updatedAt']='2026-10-25T10:17:18.849719Z'
        self.assertIn('2026-10-25 18:17（北京时间）',ItemSourceIndex(data).describe('base','a','pool1'))
        distribution['updatedAt']='2026-10-25T10:17:18';self.assertIn('未提供可核对的时间',ItemSourceIndex(data).describe('base','a','pool1'))
    def test_frequency_denominator_and_limit(self):
        text=ItemSourceIndex(fixture()).describe('base','a','pool1');self.assertIn('20.00%（2 / 10',text);self.assertIn('不是抽取权重',text);self.assertIn('不是本局最终获得概率',text)
    def test_zero_valid_and_bad_denominator_unknown(self):
        data=fixture();m=data['versions']['base'][0]['observedDistribution']['members'][0];m.update(occurrenceCount=0,occurrenceRate=0)
        self.assertIn('0.00%',ItemSourceIndex(data).describe('base','a','pool1'));m['totalOccurrenceCount']=True
        self.assertIn('未知',ItemSourceIndex(data).describe('base','a','pool1'))
    def test_sources_not_combined(self):
        data=fixture();pool=data['versions']['base'][0];pool['frequencyColumns']={'autobattle':{'status':'observed','observedDistribution':deepcopy(pool['observedDistribution'])}}
        text=ItemSourceIndex(data).describe('base','a','pool1');self.assertEqual(text.count('20.00%'),2);self.assertNotIn('40.00%',text);self.assertIn('不相加',text)
    def test_lookup_no_mutation_or_duplicate_membership(self):
        data=fixture();data['versions']['base'][0]['collectibles']*=2;before=deepcopy(data);model=ItemSourceIndex(data);self.assertEqual(len(model.pools('base','a')),1);self.assertEqual(data,before)
    def test_labels_disambiguate_node(self):self.assertEqual(pool_label(fixture()['versions']['base'][0]),'藏品 · 作战')
    def test_all_real_memberships_reverse_exactly(self):
        data=public_archive.load();model=ItemSourceIndex(data)
        for version,pools in data['versions'].items():
            for pool in pools:
                for identity in set(pool['collectibles']):self.assertIn(pool,model.pools(version,identity))
    def test_rarity_and_exchange_intersection(self):
        state={'relics':{'rogue_6_relic_legacy_1':{},'rogue_6_relic_legacy_3':{}}};before=deepcopy(state)
        rows=inventory_rows(state,rarity='NORMAL',exchange=True,kind='RELIC');self.assertEqual([r['name']for r in rows],['热水壶']);self.assertEqual(state,before)
        self.assertEqual(inventory_rows(state,rarity='RARE',exchange=False),[])
    def test_unconfirmed_held_and_unknown_filter(self):
        self.assertEqual(inventory_rows({'relics':{'rogue_6_relic_legacy_1':{'held':'true'}}}),[])
        self.assertEqual(inventory_rows({},held_only=False,rarity='NONEXISTENT'),[])
    def test_initial_missing_optional_cache_keeps_bundled_data(self):
        with TemporaryDirectory()as d:
            panel=InventoryPanel(SimpleNamespace(state={}),Path(d)/'missing.json')
            try:
                panel.refresh();self.assertIsNotNone(panel.source_index);self.assertEqual(panel.source_path,public_archive.DEFAULT)
            finally:panel.close()
    def test_installed_cache_loss_clears_instead_of_fallback(self):
        with TemporaryDirectory()as d:
            p=Path(d)/'cache.json';p.write_text(json.dumps(fixture()),encoding='utf8');panel=InventoryPanel(SimpleNamespace(state={}),p)
            try:
                self.assertIsNotNone(panel.source_index);p.unlink();panel.refresh();self.assertIsNone(panel.source_index);self.assertEqual(panel.version.count(),0)
            finally:panel.close()
    def test_invalid_cache_never_uses_stale_members(self):
        with TemporaryDirectory()as d:
            p=Path(d)/'cache.json';p.write_text('broken');panel=InventoryPanel(SimpleNamespace(state={}),p)
            try:self.assertIsNone(panel.source_index)
            finally:panel.close()
    def test_non_object_cache_clears_without_crashing(self):
        with TemporaryDirectory()as d:
            p=Path(d)/'cache.json';p.write_text('[]');panel=InventoryPanel(SimpleNamespace(state={}),p)
            try:self.assertIsNone(panel.source_index);self.assertEqual(panel.version.count(),0)
            finally:panel.close()
    def test_unchanged_refresh_keeps_item_instance_and_reading(self):
        panel=InventoryPanel(SimpleNamespace(state={}))
        try:
            panel.held.setChecked(False);panel.entries.setCurrentRow(12);item=panel.entries.currentItem();panel.refresh();self.assertIs(panel.entries.currentItem(),item)
        finally:panel.close()
    def test_source_loss_clears_item_detail(self):
        panel=InventoryPanel(SimpleNamespace(state={'relics':{'rogue_6_relic_legacy_1':{}}}))
        try:
            panel.entries.setCurrentRow(0)
            with patch('rouge.player_inventory.reference.packet',return_value=None):panel.refresh();self.assertEqual(panel.entries.count(),0);self.assertEqual(panel.detail.toPlainText(),'')
        finally:panel.close()
    def test_exact_navigation_reload_never_uses_missing_installed_cache(self):
        from rouge.public_archive_view import ArchiveDialog
        with TemporaryDirectory()as d:
            p=Path(d)/'cache.json';p.write_text(json.dumps(fixture()),encoding='utf8');view=ArchiveDialog(p)
            try:
                self.assertTrue(view.select_exact_pool('base','pool1'));p.unlink();view.reload_local()
                self.assertIsNone(view.data);self.assertFalse(view.select_exact_pool('base','pool1'));self.assertEqual(view.members.rowCount(),0)
            finally:view.close()
