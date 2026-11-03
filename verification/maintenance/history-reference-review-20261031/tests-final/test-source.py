"""Parent refresh and coherent local source reads, without game or chat calls."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.player_replay import ReplayPanel
from rouge.player_replay_archive import reload_history
from rouge import player_evidence_history as evidence,player_shop_memory as shops
from rouge.expansion_reference import packet


class HistoryReferenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        root=Path(self.enterContext(TemporaryDirectory(prefix='rouge-history-reference-')))
        self.run=RunState(root/'run.json');self.run.state['id']='isolated-current'
        self.run.state['history']=[{'kind':'relic_confirmed','id':'rogue_6_relic_cargo_15','at':1}]
        self.panel=ReplayPanel(self.run);self.addCleanup(self.panel.close)

    def test_parent_refresh_clears_lost_reference_and_restores_it_without_history_changes(self):
        page=self.panel.evidence;page.lists['relic'].setCurrentRow(0);state=deepcopy(self.run.state)
        self.assertIn('装饰性佯谬',page.detail.toPlainText())
        with patch('rouge.expansion_reference.packet',return_value=None):
            self.panel.refresh();self.assertIn('固定资料名称未核对',page.detail.toPlainText())
            self.assertTrue(page.lists['relic'].item(0).icon().pixmap(46,46).isNull())
        self.panel.refresh();self.assertIn('装饰性佯谬',page.detail.toPlainText())
        self.assertEqual(page.lists['relic'].currentRow(),0);self.assertEqual(self.run.state,state)

    def test_archived_reference_refresh_never_uses_current_history_or_rewrites_archive(self):
        state=deepcopy(self.run.state);state['id']='isolated-archive'
        self.panel.history_store.archive(state);reload_history(self.panel)
        self.panel.sessions.setCurrentIndex(self.panel.sessions.findData('archive:isolated-archive'))
        page=self.panel.evidence;page.lists['relic'].setCurrentRow(0)
        files={p.name:p.read_bytes()for p in self.panel.history_store.folder.iterdir()}
        self.run.state['history']=[]
        with patch('rouge.expansion_reference.packet',return_value=None):
            self.panel.refresh();self.assertIn('固定资料名称未核对',page.detail.toPlainText())
        self.panel.refresh();self.assertIn('装饰性佯谬',page.detail.toPlainText())
        self.assertEqual(self.panel.snapshot['id'],'isolated-archive');self.assertEqual(self.run.state['history'],[])
        self.assertEqual(files,{p.name:p.read_bytes()for p in self.panel.history_store.folder.iterdir()})

    def test_stable_parent_refresh_validates_source_but_does_not_rebuild_evidence(self):
        page=self.panel.evidence;page.lists['relic'].setCurrentRow(0);item=page.lists['relic'].item(0)
        current=packet()
        with patch('rouge.expansion_reference.packet',return_value=current)as source,patch.object(evidence,'evidence_rows',wraps=evidence.evidence_rows)as build:
            for _ in range(3):self.panel.refresh()
        self.assertEqual(build.call_count,0);self.assertGreaterEqual(source.call_count,3)
        self.assertIs(page.lists['relic'].item(0),item)

    def test_unrelated_history_append_keeps_existing_evidence_item_and_reading(self):
        page=self.panel.evidence;page.lists['relic'].setCurrentRow(0);item=page.lists['relic'].item(0);body=page.detail.toPlainText()
        self.run.state['history'].append({'kind':'resource_updated','at':2,'value':8});self.panel.refresh()
        self.assertIs(page.lists['relic'].item(0),item);self.assertEqual(page.detail.toPlainText(),body)

    def test_shop_history_uses_one_coherent_source_read_and_same_qualified_results(self):
        data=packet();identity='rogue_6_relic_cargo_15';name=data['current']['details']['items'][identity]['name']
        good={'kind':'shop_items_read','at':1,'source':'fresh_shop_exact_names','complete':False,'items':[{'id':identity,'name':name}]}
        state={'history':[deepcopy(good)for _ in range(12)]+[dict(good,at=True),dict(good,items=[{'id':identity,'name':'错误名称'}])]};before=deepcopy(state)
        expected=[(i,{**row,'items':[{'id':identity,'name':name}]})for i,row in enumerate(state['history'][:12])]
        with patch('rouge.expansion_reference.packet',return_value=data)as source:
            self.assertEqual(shops.recorded_shops(state),expected);self.assertEqual(source.call_count,1)
        with patch('rouge.expansion_reference.packet',return_value=None)as source:
            self.assertEqual(shops.recorded_shops(state),[]);self.assertEqual(source.call_count,1)
        self.assertEqual(state,before)

    def test_no_eligible_shop_history_does_not_load_source(self):
        with patch('rouge.expansion_reference.packet',side_effect=AssertionError('unneeded source read')):
            self.assertEqual(shops.recorded_shops({'history':[{'kind':'resource_updated'},None]}),[])
