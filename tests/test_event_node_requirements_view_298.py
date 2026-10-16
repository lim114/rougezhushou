"""Actual Panel contracts for298; cache draft, root executes after promotion only."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import event_node_requirements as model,node_catalog as catalog
from rouge.node_catalog_view import NodeCatalogPanel,QUALIFICATIONS

ROOT=Path(__file__).resolve().parents[1]
RULES={'community_group_024':[1,5,6],'community_group_025':[1,6],
 'community_group_027':[1,2,6],'community_group_028':[1,2,6],
 'community_group_029':[1,2,6],'community_group_037':[1]}
KEY='documented_node_natural_main_floor'

class EventNodeRequirementsView298Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.panel=NodeCatalogPanel();self.panel.resize(1050,720);self.panel.show();self.qt.processEvents()
 def tearDown(self):
  self.panel.close();self.panel.deleteLater();self.qt.processEvents()
 def choose(self,control,value):
  i=control.findData(value);self.assertGreaterEqual(i,0);control.setCurrentIndex(i)
 def select(self,identity):
  self.panel.search.setText(catalog._event(identity)['title'])
  i=next(i for i,e in enumerate(self.panel.entries)if e['kind']=='event'and e['record']['id']==identity)
  self.panel.list.setCurrentRow(i);self.qt.processEvents();row=self.panel.entries[i]
  self.assertEqual(self.panel.list.selected_key(),row['key']);return row
 def directory(self,identity,floor,context=None):
  self.panel.show_directory();self.panel.set_map_context(None,runtime_context=context or {})
  self.choose(self.panel.kind,'event');self.choose(self.panel.node_type,None);self.choose(self.panel.floor,floor)
  return self.select(identity)
 def checks(self,row):return[r for r in row['qualification']['checks']if r['key']==KEY]
 def graph(self,mode):
  event=catalog._event('community_group_024');node={'id':'public298','row':0,'col':0,
   'observed_type':'林间空地'if mode=='history'else event['node_types'][0]}
  content={'kind':'event','title':event['title'],'source':'same_frame_selected_node','identity_status':'visible_scene',
   'scene_candidates':deepcopy(event['scenes'][0]['game_scene_ids'])}
  if mode=='current':node['content']=content
  if mode=='history':node.update(remembered_type=event['node_types'][0],remembered_content=content)
  return{'zone_id':'zone_1','template_id':'public298','nodes':[node]}
 def bind(self,graph,historical=False):
  self.panel.search.clear();self.choose(self.panel.kind,'event');self.choose(self.panel.node_type,None)
  self.panel.set_map_context(graph,{'floor':1,'special_region':False},epoch='public298',historical=historical)
  self.panel.set_node(graph,'public298',floor=1,special_region=False);self.panel.bind_current_node();self.qt.processEvents()
 def test_six_exact_negative_entries_stay_in_excluded_groups_and_are_manually_readable(self):
  for identity,floors in RULES.items():
   with self.subTest(event=identity):
    row=self.directory(identity,floors[0]);check=self.checks(row)
    self.assertEqual(len(check),1);self.assertIs(check[0]['matches'],False)
    self.assertEqual(check[0]['kind'],'source_node_floor_requirement');self.assertEqual(row['qualification']['status'],'excluded')
    self.assertIn(QUALIFICATIONS['excluded'],row['group']);text=self.panel.player_detail.toPlainText()
    self.assertIn(catalog._event(identity)['title'],text);self.assertIn('【自然出现的已知条件】',text)
    self.assertIn('仍可查阅完整事件资料',text)
    self.assertNotIn('community_group_',text);self.assertNotIn('https://',text)
    self.assertIsNone(row['qualification']['actual_server_eligible'])
 def test_allowed_by_new_rule_is_not_promoted_to_complete_generation_and_tech_is_not_required(self):
  tech_seen=0
  for identity in RULES:
   with self.subTest(event=identity):
    row=self.directory(identity,3);self.assertIs(self.checks(row)[0]['matches'],True)
    self.assertFalse(row['qualification']['all_server_conditions_known']);self.assertIsNone(row['qualification']['actual_server_eligible'])
    text=self.panel.player_detail.toPlainText();self.assertIn('其它出现条件和实际生成仍未知',text)
    reference=model.event_requirements(identity,floor=3,entry_mode='natural')
    if reference['technology_enabling_reference']:
     tech_seen+=1;self.assertIn('已知开启途径',text);self.assertIn('不能据未点亮就认定绝不出现',text)
  self.assertEqual(tech_seen,2)
 def test_unknown_floor_and_special_region_do_not_reuse_natural_negative_check(self):
  for floor,context in[(None,{}),(1,{'special_region':True})]:
   with self.subTest(floor=floor,context=context):
    row=self.directory('community_group_024',floor,context);self.assertEqual(self.checks(row),[])
    self.assertIn('不据此删除内容或判定不能进入',self.panel.player_detail.toPlainText())
 def test_bound_unread_node_keeps_excluded_candidate_as_manual_reference(self):
  graph=self.graph('unread');before=deepcopy(graph);self.bind(graph);row=self.select('community_group_024')
  self.assertIn('community_group_024',[r['id']for r in self.panel.dossier['excluded_event_candidates']])
  self.assertIs(self.checks(row)[0]['matches'],False);self.assertEqual(row['qualification']['status'],'excluded')
  self.assertIn('未涉足之树',self.panel.player_detail.toPlainText());self.assertEqual(graph,before)
 def test_current_observed_title_overrides_candidate_pool_and_is_content_not_natural(self):
  graph=self.graph('current');before=deepcopy(graph);self.bind(graph);row=self.select('community_group_024')
  self.assertEqual(self.panel.dossier['excluded_event_candidates'],[]);self.assertEqual(self.checks(row),[])
  self.assertEqual(self.panel._event_context(row['record'])['entry_mode'],'content')
  self.assertIn('不据此删除内容或判定不能进入',self.panel.player_detail.toPlainText());self.assertEqual(graph,before)
 def test_passed_clearing_keeps_historical_title_and_does_not_apply_todays_floor(self):
  graph=self.graph('history');before=deepcopy(graph);self.bind(graph,True);row=self.select('community_group_024')
  self.assertTrue(row['history_read']);self.assertEqual(self.checks(row),[])
  self.assertEqual(self.panel._event_context(row['record'])['reference_context_scope'],'historical_title_reference_only')
  self.assertIn('历史已读内容',self.panel.player_detail.toPlainText());self.assertEqual(graph,before)
 def test_warm_actual_public_source_failure_clears_specific_rule_and_restores_only_same_reference(self):
  self.directory('community_group_024',1);key=self.panel.list.selected_key()
  manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
  with tempfile.TemporaryDirectory(prefix='rouge298-public-source-test-')as folder:
   clone=Path(folder)
   for name in set(manifest['files'])|{model.MANIFEST}:
    source=ROOT/name;self.assertTrue(source.is_file());self.assertFalse(source.is_symlink())
    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
   target=clone/model.MANIFEST;original=target.read_bytes()
   with patch.object(model,'ROOT',clone):
    self.assertIsNotNone(model.source_data());self.assertIs(model.event_requirements('community_group_024',floor=1,entry_mode='natural')['documented_floor_match'],False)
    try:
     target.write_bytes(original+b' ');self.panel.refresh();self.qt.processEvents()
     row=next(r for r in self.panel.entries if r['key']==key);check=self.checks(row)
     self.assertEqual(len(check),1);self.assertIsNone(check[0]['matches']);self.assertIn('不能据此排除',check[0]['source_text'])
     text=self.panel.player_detail.toPlainText();self.assertIn('节点主层资料暂时无法核对',text)
     self.assertNotIn('资料记载：先行一步不会自然出现在',text);self.assertNotIn('已知开启途径：',text)
     self.assertEqual(self.panel.list.selected_key(),key);self.assertIsNone(row['qualification']['actual_server_eligible'])
    finally:target.write_bytes(original)
    self.assertEqual(target.read_bytes(),original);self.panel.refresh();self.qt.processEvents()
    row=next(r for r in self.panel.entries if r['key']==key);self.assertIs(self.checks(row)[0]['matches'],False)
    self.assertEqual(self.panel.list.selected_key(),key)
 def test_same_context_refresh_keeps_reader_filters_full_keys_nonzero_scroll_and_selection(self):
  self.directory('community_group_024',1);self.panel.reading_tabs.setCurrentWidget(self.panel.detail);self.qt.processEvents()
  cursor=self.panel.detail.textCursor();cursor.setPosition(5);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);self.panel.detail.setTextCursor(cursor)
  bar=self.panel.detail.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(max(1,bar.maximum()//2))
  self.panel.search.setSelection(0,2)
  def state():
   c=self.panel.detail.textCursor();return(self.panel.list.selected_key(),self.panel.search.text(),self.panel.search.selectedText(),
    self.panel.kind.currentData(),self.panel.floor.currentData(),self.panel.node_type.currentData(),self.panel.event_scene_filter.currentData(),
    self.panel.event_choice_filter.currentData(),self.panel.event_stage.currentData(),self.panel.reading_tabs.currentIndex(),
    self.panel.detail.toPlainText(),c.anchor(),c.position(),c.selectedText(),bar.value())
  expected=state();self.assertTrue(expected[-2]);self.assertGreater(expected[-1],0)
  for _ in range(3):self.panel.refresh();self.qt.processEvents();self.assertEqual(state(),expected)

if __name__=='__main__':unittest.main()
