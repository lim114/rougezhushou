"""Exact source nodes, distinct non-node origins and original shared atlas pixels."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
from copy import deepcopy
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QWidget,QLabel
from rouge import player_map as artwork,public_archive
from rouge.player_source_cards import source_cards,SourceCards
from rouge.player_source_map import PAIRS
from rouge.player_item_sources import ItemSourceIndex
from rouge.player_item_hover import ItemHoverCard
from tests.test_player_item_sources_394 import fixture

class SourceNodes445(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def test_every_original_node_sprite_keeps_exact_pixels_across_shared_views(self):
  old=ModuleType('rouge._source_nodes_before_map');old.__package__='rouge';old.__file__=artwork.__file__
  path=Path(__file__).resolve().parents[1]/'research/source-nodes-445/before-player_map.py'
  exec(compile(path.read_bytes(),str(path),'exec'),old.__dict__)
  before=old.PreviewMapView();after=artwork.PreviewMapView();self.addCleanup(before.close);self.addCleanup(after.close)
  artwork.node_sprite.cache_clear();artwork.node_atlas.cache_clear()
  for name in artwork.ICONS:self.assertEqual(before.sprite_for(name),after.sprite_for(name),name)
  self.assertTrue(after.sprite_for('not-a-node').isNull());self.assertEqual(artwork.node_atlas.cache_info().misses,1)
  again=artwork.PreviewMapView();self.addCleanup(again.close);again.sprite_for('作战');self.assertEqual(artwork.node_atlas.cache_info().misses,1)
 def test_current_public_pool_frequencies_and_bindings_are_not_combined_or_dropped(self):
  data=public_archive.load();index=ItemSourceIndex(data);before=deepcopy(data)
  for version,pools in data['versions'].items():
   for pool in pools:
    if not pool['collectibles']:continue
    identity=pool['collectibles'][0];rows=source_cards(index,version,identity)
    actual=[r for r in rows['nodes']if r['id']==pool['id']]
    expected=list(dict.fromkeys(b['nodeName']for b in pool.get('nodeBindings',[])if b.get('nodeName')))
    self.assertEqual([r['title']for r in actual],expected)
    summary=next(r for r in rows['pools']if r['id']==pool['id'])
    for row in actual:self.assertEqual(row['frequency'],summary['frequency']);self.assertEqual(row['counts'],summary['counts'])
  self.assertEqual(data,before)
 def test_only_exact_enum_name_pairs_are_map_nodes(self):
  data=fixture();pool=data['versions']['base'][0]
  pool['nodeBindings']=[{'nodeType':'BATTLE_NORMAL','nodeName':'作战'},{'nodeType':'WANDERING_RESIDENT','nodeName':'流窜的“居民”'},{'nodeType':'START','nodeName':'林间代步'},{'nodeType':'source','nodeName':'不期而遇'}]
  rows=source_cards(ItemSourceIndex(data),'base','a')['nodes']
  self.assertEqual([r['title']for r in rows if r['map_kind']],['作战']);self.assertTrue(all(r['map_kind']is None for r in rows[1:]))
 def test_separate_groups_keep_non_node_origin_readable_without_guessing_an_icon(self):
  data=fixture();data['versions']['base'][0]['nodeBindings']=[{'nodeType':'BATTLE_NORMAL','nodeName':'作战'},{'nodeType':'START','nodeName':'林间代步'}]
  cards=SourceCards();self.addCleanup(cards.close);cards.install(source_cards(ItemSourceIndex(data),'base','a'))
  labels=[w.text()for w in cards.findChildren(QLabel)]
  self.assertIn('对应地图节点',labels);self.assertIn('其它取得来源',labels)
  node=next(b for b in cards.buttons if b.property('mapKind')=='作战');origin=next(b for b in cards.buttons if b.caption.text().startswith('林间代步'))
  self.assertFalse(node.picture.pixmap().isNull());self.assertFalse(hasattr(origin,'picture'));self.assertIn('未直接对应地图节点',origin.toolTip())
 def test_node_click_carries_exact_pool_and_kind_and_pool_click_remains_unchanged(self):
  data=fixture();data['versions']['base'][0]['nodeBindings'][0]['nodeType']='BATTLE_NORMAL'
  cards=SourceCards();self.addCleanup(cards.close);cards.install(source_cards(ItemSourceIndex(data),'base','a'));pools=[];nodes=[]
  cards.poolChosen.connect(pools.append);cards.nodeChosen.connect(lambda p,k:nodes.append((p,k)))
  cards.buttons[0].click();next(b for b in cards.buttons if b.property('mapKind')).click()
  self.assertEqual(pools,['pool1']);self.assertEqual(nodes,[('pool1','作战')])
 def test_direct_node_action_uses_existing_map_and_never_changes_run(self):
  owner=QWidget();self.addCleanup(owner.close);seen=[];state={'id':'isolated','maps':{}};before=deepcopy(state)
  owner.run=SimpleNamespace(state=state);owner.open_map=lambda:seen.append('opened');owner.map_popup=SimpleNamespace(panel=SimpleNamespace(set_type_filter=seen.append))
  card=ItemHoverCard(owner);self.addCleanup(card.close);data=fixture();data['versions']['base'][0]['nodeBindings'][0]['nodeType']='BATTLE_NORMAL'
  card.install({'id':'a','name':'同名'},'base',ItemSourceIndex(data),'one')
  next(b for b in card.cards.buttons if b.property('mapKind')).click()
  self.assertEqual(seen,['opened','作战']);self.assertEqual(card.pools.currentData(),'pool1');self.assertEqual(state,before)
 def test_invalid_or_expired_node_action_cannot_open_map(self):
  owner=QWidget();self.addCleanup(owner.close);seen=[];owner.open_map=lambda:seen.append('opened');owner.map_popup=SimpleNamespace(panel=SimpleNamespace(set_type_filter=seen.append))
  card=ItemHoverCard(owner);self.addCleanup(card.close);card.install({'id':'a','name':'同名'},'base',ItemSourceIndex(fixture()),'one')
  self.assertFalse(card.open_map_source('pool1','不期而遇'));self.assertFalse(card.open_map_source('wrong-pool','作战'))
  card.install({'id':'a','name':'同名'},'base',None,'lost');self.assertFalse(card.open_map_source('pool1','作战'));self.assertEqual(seen,[])
 def test_standalone_node_click_still_opens_conditions_without_claiming_map_success(self):
  owner=QWidget();self.addCleanup(owner.close);card=ItemHoverCard(owner);self.addCleanup(card.close);data=fixture();data['versions']['base'][0]['nodeBindings'][0]['nodeType']='BATTLE_NORMAL'
  card.install({'id':'a','name':'同名'},'base',ItemSourceIndex(data),'one');self.assertFalse(card.open_map_source('pool1','作战'));self.assertTrue(card.show_conditions.isChecked())
 def test_node_cards_wrap_at_narrow_width_without_horizontal_scrolling(self):
  cards=SourceCards();self.addCleanup(cards.close);rows=[{'id':'p','title':'紧急作战','pool_name':'同名资料分别保留的收藏品集合','frequency':'历史候选频率 20.00%','counts':'2／10次候选出现','version':'base','map_kind':'紧急作战'}]
  cards.install({'pools':[],'nodes':rows});cards.resize(390,430);cards.show();self.qt.processEvents()
  self.assertTrue(cards.buttons[0].caption.wordWrap());self.assertEqual(cards.horizontalScrollBar().maximum(),0)

if __name__=='__main__':unittest.main()
