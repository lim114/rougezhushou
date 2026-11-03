from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import tempfile,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import public_event_samples as model,node_catalog
from rouge.player_map_acceptance import fixtures
from rouge.player_map_hover import NodeHoverCard,NodeEntryButton
from rouge.player_map import PreviewMapView


class PublicEventSamplesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.graphs,self.candidate,_,_=fixtures();self.graph=self.graphs[0]
  self.addCleanup(model.samples.cache_clear);self.addCleanup(model.event_bindings.cache_clear)
 def test_fixed_source_denominators_and_independent_first_floor_count_example(self):
  meta,rows=model.samples();self.assertEqual(sum(map(lambda r:sum(r.values()),rows.values())),3836)
  self.assertEqual({k:sum(v.values())for k,v in rows.items()},{(1,False):438,(2,False):447,(3,False):970,(3,True):29,(4,False):674,(4,True):55,(5,False):786,(5,True):100,(6,False):337})
  r=model.references(self.graph)['community_group_000'];self.assertEqual((r['event_id'],r['count'],r['total']),('rogue_6:scene_ro6_res1',74,438));self.assertAlmostEqual(r['frequency'],74/438);self.assertEqual(model.label(r),'历史 16.89%');self.assertFalse(meta['difficultyStratified'])
 def test_titles_do_not_bind_identity_and_duplicate_original_entries_remain_unconfirmed(self):
  first=deepcopy(node_catalog._event('community_group_000'));second=deepcopy(node_catalog._event('community_group_001'));second['title']=first['title']
  with patch.object(node_catalog,'_data',return_value={'events':[first,second]}):
   model.event_bindings.cache_clear();b=model.event_bindings();self.assertNotEqual(b[first['id']],b[second['id']])
  duplicate=deepcopy(first);duplicate['id']='another_group'
  with patch.object(node_catalog,'_data',return_value={'events':[first,duplicate]}):
   model.event_bindings.cache_clear();self.assertEqual(model.event_bindings(),{})
 def test_unknown_hidden_or_missing_source_never_borrows_main_floor_counts(self):
  self.assertEqual(model.references({'zone_id':'not-a-known-zone'}),{})
  self.assertEqual(model.references({'zone_id':'zone_3b'}),{})
  with tempfile.TemporaryDirectory()as directory,patch.object(model,'DEFAULT',Path(directory)/'missing.json'):
   model.samples.cache_clear();self.assertEqual(model.references(self.graph),{})
  zero={'count':0,'total':447,'frequency':0,'floor':2,'model_version':'test'}
  self.assertEqual(model.label(zero),'样本未观测');self.assertIn('0次不表示不可能',model.explanation(zero))
 def test_same_node_candidate_filter_does_not_renormalize_public_event_denominator(self):
  before=model.references(self.graph);copy=deepcopy(self.graph);node=next(n for n in copy['nodes']if n['id']==self.candidate);node['prediction']={'candidates':['不期而遇']};node['content']={'title':'任选已读标题'}
  self.assertEqual(model.references(copy),before);self.assertTrue(all(r['total']==438 for r in before.values()))
 def test_real_card_has_separate_caption_sample_line_source_scope_and_exact_click(self):
  view=PreviewMapView();view.set_map(self.graph);self.addCleanup(view.close);card=NodeHoverCard(view);self.addCleanup(card.close);binding=('isolated',self.graph['zone_id'],self.graph['template_id'],self.candidate)
  self.assertTrue(card.install(binding,self.graph,self.candidate,{},view));card.show();QTest.qWait(20)
  rows=[b for k,i,b in card.entry_buttons if k=='event'];self.assertEqual(len(rows),5);button=next(b for b in rows if b.text()=='桑尼的邀请');self.assertEqual(model.label(button.sample_reference),'历史 16.89%')
  self.assertIn('74/438',button.toolTip());self.assertIn('混合保密等级',button.accessibleDescription());self.assertIn('不是本局概率',card.summary.text());self.assertTrue(button.rect().contains(button.caption_rect()));self.assertGreaterEqual(button.caption_rect().height(),button.fontMetrics().height())
  received=[];card.entryRequested.connect(lambda *args:received.append(args));card.scroll.ensureWidgetVisible(button);QTest.mouseClick(button,Qt.MouseButton.LeftButton);self.assertEqual(received,[(self.candidate,'event','community_group_000')])
  scroll=card.scroll.verticalScrollBar();scroll.setValue(min(30,scroll.maximum()));old=scroll.value();card.install(binding,self.graph,self.candidate,{},view,force=True);self.assertEqual(card.scroll.verticalScrollBar().value(),old)
  ordinary=NodeEntryButton('未绑定事件',None,QIcon());self.addCleanup(ordinary.close);self.assertIsNone(ordinary.sample_reference)


if __name__=='__main__':unittest.main()
