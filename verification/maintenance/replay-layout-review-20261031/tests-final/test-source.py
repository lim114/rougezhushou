"""Archive cards, floor tabs and resource pills preserve exact history scope."""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.player_replay import ReplayPanel
from rouge.player_replay_archive import reload_history,card_text
from rouge.player_replay_nodes import NodeReplayPage
from tests import test_history_reader_review as old


class ReplayLayoutReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        root=Path(self.enterContext(TemporaryDirectory(prefix='rouge-replay-layout-')))
        self.run=RunState(root/'run.json');self.run.state['id']='public-current'
        self.panel=ReplayPanel(self.run);self.addCleanup(self.panel.close)
    def archive(self,identity='public-old'):
        state,template,ids=old.history_example();state['id']=identity;state['started_at']=100
        self.panel.history_store.archive(state);reload_history(self.panel)
        return state,template,ids
    def card(self,identity):
        return next(self.panel.session_cards.item(i)for i in range(self.panel.session_cards.count())if self.panel.session_cards.item(i).data(Qt.ItemDataRole.UserRole)==identity)
    def open(self,identity):self.panel.session_cards.itemClicked.emit(self.card(identity));self.qt.processEvents()

    def test_card_click_reads_exact_archive_latest_saved_map_and_never_restores_current(self):
        state,t,ids=self.archive();current=deepcopy(self.run.state)
        files={p.name:p.read_bytes()for p in self.panel.history_store.folder.iterdir()}
        self.open('archive:public-old')
        self.assertEqual(self.panel.snapshot['id'],'public-old');self.assertIs(self.panel.tabs.currentWidget(),self.panel.nodes)
        self.assertEqual(self.panel.nodes.view.selected,ids[-1]);self.assertEqual(self.panel.nodes.view.graph['template_id'],t['id'])
        self.assertEqual(self.run.state,current);self.assertEqual(files,{p.name:p.read_bytes()for p in self.panel.history_store.folder.iterdir()})
        self.panel.history_list_button.click();self.assertIs(self.panel.tabs.currentWidget(),self.panel.archive_page)

    def test_extra_record_pages_and_timeline_are_available_without_occupying_default_map(self):
        self.panel.show();self.archive();self.open('archive:public-old')
        self.assertFalse(self.panel.tabs.tabBar().isVisible());self.assertFalse(self.panel.nodes.entries.isVisible())
        self.panel.history_views_button.click();self.panel.nodes.readings_toggle.click();self.qt.processEvents()
        self.assertTrue(self.panel.tabs.tabBar().isVisible());self.assertTrue(self.panel.nodes.entries.isVisible())

    def test_cards_disclose_missing_results_and_invalid_difficulty_without_guessing(self):
        text=card_text({'id':'a','history':[],'config':{'difficulty':{'value':True,'captured_at':5}},
                        'relics':{'good':{},'bad':None},'operators':{'good':{'present':True},'unknown':{'present':'true'}}},'本机历史')
        self.assertIn('保密等级未读到',text);self.assertIn('分队未读到',text)
        self.assertIn('已确认藏品 1 件 · 干员 1 名',text);self.assertIn('结算分数与种子尚未确认',text)

    def test_same_source_refresh_reuses_card_objects_and_does_not_rescan_archives(self):
        from rouge import player_replay_archive as module
        self.archive();self.archive('second');self.open('archive:public-old')
        items=[self.panel.session_cards.item(i)for i in range(self.panel.session_cards.count())]
        with patch.object(module,'card_text',wraps=module.card_text)as summary,patch.object(self.panel.history_store,'records',side_effect=AssertionError('unsolicited disk scan')):
            for _ in range(3):self.panel.refresh()
        self.assertEqual(summary.call_count,3)
        self.assertEqual(items,[self.panel.session_cards.item(i)for i in range(self.panel.session_cards.count())])

    def test_unavailable_archive_clears_card_and_detail_without_current_fallback(self):
        self.archive();self.open('archive:public-old')
        with patch.object(self.panel.history_store,'records',side_effect=OSError('isolated read error')):reload_history(self.panel)
        self.assertEqual(self.panel.sessions.currentData(),'unavailable');self.assertEqual(self.panel.entries.count(),0)
        self.assertEqual(self.panel.session_cards.count(),1);self.assertEqual(self.panel.snapshot,{'id':None,'history':[]})
        reload_history(self.panel);self.assertEqual(self.panel.sessions.currentData(),'unavailable')
        self.open('archive:public-old');self.assertEqual(self.panel.snapshot['id'],'public-old')

    def test_floor_tabs_select_saved_prefix_and_share_original_filter(self):
        state,t,ids=old.history_example();p=self.panel.nodes;p.refresh(state)
        index=p.floors.findData(t['zone_id']);self.assertGreater(index,0)
        self.assertEqual(p.floor_tabs.tabData(index),t['zone_id']);p.floor_tabs.setCurrentIndex(index)
        self.assertEqual(p.floors.currentIndex(),index);self.assertEqual(p.view.selected,ids[-1])
        self.assertEqual(p.resource_pills.rows[0]['value'],'99')
        p.entries.setCurrentRow(0);self.assertEqual(p.resource_pills.rows,[])
        self.assertEqual(p.resource_pills.flow.count(),0);self.assertIn('尚未记录',p.resources.text())
        p.entries.setCurrentRow(2);self.assertEqual(p.resource_pills.rows[0]['value'],'7')
        self.assertNotIn('999',p.resource_pills.toolTip());self.assertNotIn('href=',next(iter(p.resource_pills.chips.values())).text())

    def test_other_region_or_missing_template_never_uses_current_resources(self):
        state,t,ids=old.history_example();p=self.panel.nodes;p.refresh(state);p.entries.setCurrentRow(p.entries.count()-1)
        self.assertTrue(p.resource_pills.rows)
        state['history']+=[{'kind':'map_layout_changed','zone_id':t['zone_id'],'current_template':'unavailable'},
                          {'kind':'map_position_updated','zone_id':t['zone_id'],'current':ids[0]}]
        before=deepcopy(state);p.refresh(state);p.entries.setCurrentRow(p.entries.count()-1)
        self.assertIsNone(p.view.graph);self.assertEqual(p.resource_pills.rows,[]);self.assertFalse(p.resource_pills.chips)
        self.assertEqual(state,before)

    def test_archive_view_and_floor_selection_survive_current_run_updates(self):
        self.archive();self.open('archive:public-old');page=self.panel.nodes;page.entries.setCurrentRow(2)
        selected=page.entries.currentItem().data(Qt.ItemDataRole.UserRole);floor=page.floor_tabs.currentIndex()
        self.run.state['id']='new-current';self.run.state['history'].append({'kind':'node_content_seen','title':'new reading'})
        self.panel.refresh()
        self.assertEqual(self.panel.snapshot['id'],'public-old');self.assertEqual(page.floor_tabs.currentIndex(),floor)
        self.assertEqual(page.entries.currentItem().data(Qt.ItemDataRole.UserRole),selected)

    def test_resource_strip_current_mode_is_unchanged_after_historical_rows(self):
        from rouge.player_resource_strip import ResourceStrip
        from rouge.player_resource_facts import resource_rows
        strip=ResourceStrip();self.addCleanup(strip.close)
        strip.set_rows([{'key':'history:gold','name':'源石锭','value':'7','note':'historical fixture'}])
        strip.refresh({'resources':{'gold':{'value':9}}})
        self.assertEqual(strip.rows,resource_rows({'resources':{'gold':{'value':9}}}))
        self.assertNotIn('history:gold',strip.chips);self.assertEqual(strip.flow.count(),len(strip.rows))
