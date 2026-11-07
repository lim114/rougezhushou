from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace,MethodType
from unittest.mock import patch
from copy import deepcopy
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication,QWidget
from rouge import public_archive as model
from rouge.public_archive_view import ArchivePanel
from rouge.player_compact import CompactAssistant
from rouge.player_reference_window import ReferenceWindow,ToolPage


class SharedArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.file=Path(self.temp.name)/'public.json'
        self.file.write_text(json.dumps(model.load(),ensure_ascii=False),'utf8')
        self.owner=QWidget();self.owner.owner=SimpleNamespace(public_archive=None);self.owner.archive_popup=None
        self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present
        for name in ['archive_reader','open_archive','open_archive_pool','open_archive_event']:
            setattr(self.owner,name,MethodType(getattr(CompactAssistant,name),self.owner))
        with patch('rouge.public_archive_view.ArchivePanel',side_effect=lambda *a,**k:ArchivePanel(self.file)):
            self.assertTrue(self.owner.open_archive())
        self.p=self.owner.owner.public_archive;self.page=self.owner.archive_popup;self.qt.processEvents();self.addCleanup(self.cleanup)
    def cleanup(self):self.host.close();self.owner.deleteLater();self.qt.processEvents()
    def choose_event(self):
        self.p.tabs.setCurrentIndex(1);self.p.floor.setCurrentIndex(self.p.floor.findData(1));self.p.event_search.clear()
        self.p.events.setCurrentRow(next(i for i in range(self.p.events.count())if self.p.events.item(i).data(Qt.ItemDataRole.UserRole)=='rogue_6:scene_ro6_bat1_enter'))
        self.qt.processEvents()
    def test_shared_host_and_unchanged_reopen_keep_pool_reading_without_reinstall(self):
        p=self.p;p.version.setCurrentIndex(p.version.findData('base'));p.pools.setCurrentRow(0);self.qt.processEvents();identity=p.pools.currentItem().data(Qt.ItemDataRole.UserRole)
        p.scope.setChecked(True);cursor=p.pool_note.textCursor();cursor.setPosition(1);cursor.setPosition(5,QTextCursor.MoveMode.KeepAnchor);p.pool_note.setTextCursor(cursor);selected=cursor.selectedText()
        other=ToolPage('其它资料',QWidget(),self.owner);self.host.present(other)
        with patch.object(p,'install',wraps=p.install)as install:self.assertTrue(self.owner.open_archive());self.qt.processEvents();install.assert_not_called()
        self.assertIs(p.window(),self.host);self.assertFalse(p.isWindow());self.assertEqual(p.pools.currentItem().data(Qt.ItemDataRole.UserRole),identity);self.assertEqual(p.pool_note.textCursor().selectedText(),selected)
        self.assertTrue(self.owner.open_archive_pool('base',identity));self.assertEqual(p.pool_note.textCursor().selectedText(),selected)
    def test_exact_pool_and_version_requests_clear_invalid_old_members(self):
        version='base';identity=self.p.data['versions'][version][0]['id']
        self.assertTrue(self.owner.open_archive_pool(version,identity));self.assertEqual(self.p.version.currentData(),version);self.assertEqual(self.p.pools.currentItem().data(Qt.ItemDataRole.UserRole),identity)
        self.assertFalse(self.owner.open_archive_pool('missing-version',identity));self.assertIsNone(self.p.pools.currentItem());self.assertEqual(self.p.members.rowCount(),0)
        self.assertFalse(self.owner.open_archive_pool(version,'missing-pool'));self.assertIsNone(self.p.pools.currentItem());self.assertEqual(self.p.members.rowCount(),0)
    def test_switch_version_with_active_search_builds_only_target_members(self):
        self.p.version.setCurrentIndex(self.p.version.findData('base'))
        self.p.pool_search.setText('报废轮子')
        pool = next(row for row in self.p.data['versions']['dlc1'] if row['collectibles'])
        with patch.object(model, 'pool_rows', wraps=model.pool_rows) as pool_rows, \
             patch.object(model, 'members', wraps=model.members) as members:
            self.assertTrue(self.p.select_exact_pool('dlc1', pool['id']))
        pool_rows.assert_called_once_with(self.p.data, 'dlc1', '')
        self.assertEqual(members.call_count, 1)
        self.assertIs(members.call_args.args[1], pool)
        self.assertEqual(self.p.members.rowCount(), len(pool['collectibles']))

    def test_pool_without_statistics_displays_items_and_effects_without_empty_numeric_columns(self):
        pool=self.p.data['versions']['base'][0];self.owner.open_archive_pool('base',pool['id'])
        self.assertGreater(self.p.members.rowCount(),0);self.assertFalse(self.p.sources.isVisible());self.assertTrue(self.p.members.isColumnHidden(1));self.assertTrue(self.p.members.isColumnHidden(2));self.assertFalse(self.p.members.isColumnHidden(0));self.assertFalse(self.p.members.isColumnHidden(3))
    def test_updated_public_file_keeps_valid_pool_row_and_explanation_reading(self):
        identity=next(r['id']for r in self.p.data['versions']['base']if r['collectibles'])
        self.owner.open_archive_pool('base',identity);self.qt.processEvents();self.p.members.setCurrentCell(0,2)
        selected=self.p.members.item(0,0).data(Qt.ItemDataRole.UserRole);cursor=self.p.pool_note.textCursor();cursor.setPosition(1);cursor.setPosition(5,QTextCursor.MoveMode.KeepAnchor);self.p.pool_note.setTextCursor(cursor)
        source=json.loads(self.file.read_bytes());source['retrieved_at']='public-fixture-update';self.file.write_text(json.dumps(source,ensure_ascii=False),'utf8');self.p.reload_local();self.qt.processEvents()
        self.assertEqual(self.p.pools.currentItem().data(Qt.ItemDataRole.UserRole),identity);self.assertEqual(self.p.members.item(self.p.members.currentRow(),0).data(Qt.ItemDataRole.UserRole),selected);self.assertEqual(self.p.members.currentColumn(),2);self.assertEqual(self.p.pool_note.textCursor().selectedText(),cursor.selectedText())
    def test_event_opens_existing_full_reader_and_back_keeps_event_selection(self):
        self.choose_event();context=deepcopy(self.p.reference_context());self.p.event_button.click();self.qt.processEvents();child=self.host.pages.currentWidget()
        self.assertIsNot(child,self.page);self.assertIs(child.source_parent,self.page);self.assertIs(child.window(),self.host);self.assertIn('思乡心切',child.windowTitle())
        self.host.navigate(0);self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),self.page);self.assertEqual(self.p.reference_context(),context)
        self.p.event_button.click();self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),child)
    def test_changed_event_range_removes_old_child_and_returns_to_archive(self):
        self.choose_event();self.p.event_button.click();self.qt.processEvents();child=self.host.pages.currentWidget()
        self.p.event_search.setText('this-event-does-not-exist');self.assertFalse(child.prepare());self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(),self.page);self.assertNotIn(child,self.host.history);self.assertFalse(self.p.event_button.isEnabled())
    def test_source_loss_clears_event_and_open_child_without_network(self):
        self.choose_event();self.p.event_button.click();self.qt.processEvents();child=self.host.pages.currentWidget();self.file.write_text('{}','utf8')
        self.assertFalse(child.prepare());self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),self.page);self.assertIsNone(self.p.data);self.assertEqual(self.p.events.count(),0);self.assertEqual(self.p.members.rowCount(),0)
    def test_unbound_event_does_not_open_other_same_name_reference(self):
        self.choose_event();history=list(self.host.history);self.assertFalse(self.owner.open_archive_event('scenes','missing-id'));self.assertEqual(self.host.history,history);self.assertIs(self.host.pages.currentWidget(),self.page)
