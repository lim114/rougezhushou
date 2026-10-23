"""Normal product pages contain all pinned reference categories."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from tests import test_batch185_mainwindow as fixture
from rouge import expansion_reference as model
from rouge.expansion_view import ExpansionUpdatePanel


class CommonContent352Tests(unittest.TestCase):
    setUpClass=classmethod(fixture.Batch185WindowTests.setUpClass.__func__)
    setUp=fixture.Batch185WindowTests.setUp

    def select(self,panel,key):
        row=next(i for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key)
        panel.entries.setCurrentRow(row);self.qt.processEvents()

    def test_no_update_tab_and_every_category_has_one_ordinary_home(self):
        tabs=self.window.centralWidget();labels=[tabs.tabText(i)for i in range(tabs.count())]
        self.assertNotIn('版本与更新',labels)
        homes={'战斗预览':{'stages'},'节点事件':{'scenes','choices','regions','endings'},
               '藏品与零件':{'relics','scrap'},'探索设置':{'squads','difficulty','initial'}}
        seen=[]
        for label,categories in homes.items():
            panel=tabs.widget(labels.index(label));self.assertIsInstance(panel,ExpansionUpdatePanel)
            actual={panel.category.itemData(i)for i in range(panel.category.count())}
            self.assertEqual(actual,categories);seen.extend(actual)
            self.assertFalse(panel.scope.currentData());self.assertTrue(panel.scope.isHidden())
        self.assertCountEqual(seen,dict(model.CATEGORIES))
        self.assertFalse(hasattr(self.window,'expansion_update'))

    def test_all_ten_categories_list_full_current_records_through_real_normal_pages(self):
        before=deepcopy(self.window.run.state);context=deepcopy(self.window.battle_preview.context)
        for category,_ in model.CATEGORIES:
            panel=self.window.reference_panel(category);self.qt.processEvents()
            if category=='relics':panel.item_kind.setCurrentIndex(panel.item_kind.findData(None));self.qt.processEvents()
            self.assertIs(self.window.centralWidget().currentWidget(),panel)
            self.assertTrue(panel.isVisible());self.assertEqual(panel.category.currentData(),category)
            actual=[panel.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.entries.count())]
            self.assertEqual(actual,[r['id']for r in model.rows(category,changes_only=False)])
        self.assertEqual(self.window.run.state,before);self.assertEqual(self.window.battle_preview.context,context)
        self.assertFalse(self.window.auto.isChecked())
        for invalid in(None,True,'unknown','../private'):self.assertIsNone(self.window.reference_panel(invalid))

    def test_collectible_default_and_real_type_branches_do_not_mislabel_squad_effects(self):
        panel=self.window.reference_panel('relics');self.qt.processEvents()
        self.assertEqual(panel.item_kind.currentData(),'RELIC')
        raw=model.rows('relics',changes_only=False)
        for i in range(panel.item_kind.count()):
            panel.item_kind.setCurrentIndex(i);self.qt.processEvents();kind=panel.item_kind.currentData()
            actual=[panel.entries.item(n).data(Qt.ItemDataRole.UserRole)for n in range(panel.entries.count())]
            self.assertEqual(actual,[r['id']for r in raw if kind is None or r['value']['item']['type']==kind])
        panel.item_kind.setCurrentIndex(panel.item_kind.findData('RELIC'))
        self.assertTrue(all((r['value']['item']['type']=='RELIC')for r in raw if r['id']in[panel.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.entries.count())]))
        self.window.reference_panel('scrap');self.qt.processEvents();self.assertFalse(panel.item_kind.isVisible())

    def test_pages_keep_independent_search_selection_and_nonzero_reading_after_refresh(self):
        items=self.window.reference_panel('relics');items.search.setText('谒日之祈');self.select(items,'rogue_6_relic_final_7')
        key=items.result['row']['id'];self.window.resize(1000,650);self.qt.processEvents()
        items.tabs.setCurrentIndex(1);self.qt.processEvents();reader=items.technical
        cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
        reader.verticalScrollBar().setValue(min(3,reader.verticalScrollBar().maximum()))
        previous=(reader.textCursor().selectedText(),reader.verticalScrollBar().value(),items.tabs.currentIndex())
        events=self.window.reference_panel('scenes');events.search.setText('险路尽头');self.qt.processEvents()
        self.assertEqual(items.search.text(),'谒日之祈');self.assertEqual(items.result['row']['id'],key)
        self.window.reference_panel('relics');self.assertTrue(items.refresh_reference());self.qt.processEvents()
        self.assertEqual(previous,(reader.textCursor().selectedText(),reader.verticalScrollBar().value(),items.tabs.currentIndex()))
        self.assertEqual(events.search.text(),'险路尽头')

    def test_current_battle_and_item_flow_open_from_their_ordinary_pages(self):
        stages=self.window.reference_panel('stages');self.select(stages,'ro6_b_7')
        self.assertTrue(stages.open_current_battle());battle=stages.current_battle_dialog
        self.assertEqual(battle.panel.result['id'],'ro6_b_7')
        items=self.window.reference_panel('relics');self.assertFalse(battle.isVisible())
        self.select(items,'rogue_6_relic_final_7');self.assertTrue(items.open_reward_origins())
        child=items.origins_dialog;self.assertTrue(child.isVisible())
        tabs=self.window.centralWidget();tabs.setCurrentWidget(stages);self.qt.processEvents()
        self.assertFalse(child.isVisible())

    def test_source_failure_clears_each_page_and_restoration_does_not_auto_select(self):
        panels=list(self.window.common_reference_panels.values())
        for panel in panels:panel.entries.setCurrentRow(0);self.assertIsNotNone(panel.result)
        with patch.object(model,'packet',return_value=None):
            for panel in panels:
                self.assertFalse(panel.refresh_reference());self.assertIsNone(panel.result)
                self.assertEqual(panel.entries.count(),0);self.assertEqual(panel.technical.toPlainText(),'')
        for panel in panels:
            self.assertTrue(panel.refresh_reference());self.assertIsNone(panel.result)
            self.assertIsNone(panel.entries.currentItem())

    def test_close_all_common_child_trees_and_keep_legacy_calculation_scope_explicit(self):
        panels=[];children=[]
        stage=self.window.reference_panel('stages');self.select(stage,'ro6_b_7');stage.open_current_battle()
        children.append(stage.current_battle_dialog);panels.append(stage)
        self.assertIn('更新前',self.window.battle_preview.version_notice.text())
        self.assertNotIn('版本与更新',self.window.battle_preview.version_notice.text())
        self.assertIn('尚未完整适配',self.window.damage_version_notice.text())
        self.window.close();self.qt.processEvents()
        self.assertTrue(all(not child.isVisible()for child in children))


if __name__=='__main__':unittest.main()
