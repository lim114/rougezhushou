"""Deferred hidden directories retain exact lookup and source-loss behaviour."""
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import expansion_view as view
ROOT=Path(__file__).resolve().parents[1]

class DeferredReferenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])
        old=ModuleType('rouge._before_deferred_reference');old.__package__='rouge';old.__file__=str(ROOT/'rouge/expansion_view.py')
        exec(compile((ROOT/'research/deferred-reference-review-20261031/before-expansion_view.py').read_bytes(),'<own-before-deferred-reference>','exec'),old.__dict__)
        cls.old=old
    def panel(self,**kw):
        p=view.ExpansionUpdatePanel(**kw);self.addCleanup(p.close);return p
    def test_deferred_constructor_does_not_read_sources_but_installs_all_query_controls(self):
        with patch.object(view.model,'packet',side_effect=AssertionError('Premature source read')):
            panel=self.panel(categories=('relics','scrap'),full_catalog=True,defer_population=True)
        self.assertEqual(panel.entries.count(),0);self.assertTrue(panel._population_pending)
        self.assertIsNotNone(panel.query_menu)
    def test_default_standalone_contract_still_populates_immediately(self):
        p=self.panel(categories=('relics',),full_catalog=True)
        self.assertGreater(p.entries.count(),0);self.assertFalse(p._population_pending)
    def test_ensure_only_populates_once_and_keeps_selected_reading(self):
        p=self.panel(categories=('relics',),full_catalog=True,defer_population=True)
        with patch.object(view.model,'packet',wraps=view.model.packet)as source:
            p.ensure_populated();self.assertEqual(source.call_count,1)
            p.entries.setCurrentRow(0);current=p.entries.currentItem();text=p.player.toPlainText();calls=source.call_count
            p.ensure_populated();self.assertEqual(source.call_count,calls)
            self.assertIs(p.entries.currentItem(),current);self.assertEqual(p.player.toPlainText(),text)
    def test_category_change_before_display_populates_only_the_requested_category(self):
        p=self.panel(categories=('relics','scrap'),full_catalog=True,defer_population=True)
        with patch.object(view.model,'packet',wraps=view.model.packet)as source:
            p.category.setCurrentIndex(p.category.findData('scrap'));count=source.call_count;p.ensure_populated()
        self.assertEqual(count,1);self.assertEqual(source.call_count,1);self.assertEqual(p.entries.count(),44)
    def test_first_show_populates_and_second_show_keeps_selection(self):
        p=self.panel(categories=('relics',),full_catalog=True,defer_population=True)
        p.show();self.qt.processEvents();self.assertTrue(p.isVisible());self.assertGreater(p.entries.count(),0)
        p.entries.setCurrentRow(0);item=p.entries.currentItem();p.hide();p.show();self.qt.processEvents()
        self.assertIs(p.entries.currentItem(),item)
    def test_explicit_refresh_before_show_does_not_repeat_initial_read(self):
        p=self.panel(categories=('relics',),full_catalog=True,defer_population=True)
        with patch.object(view.model,'packet',wraps=view.model.packet)as source:
            p.refresh_reference();p.show();self.qt.processEvents()
            self.assertEqual(source.call_count,1)
    def test_unavailable_first_read_clears_then_explicit_recovery_does_not_restore_selection(self):
        p=self.panel(categories=('relics',),full_catalog=True,defer_population=True)
        with patch.object(view.model,'packet',return_value=None):p.ensure_populated()
        self.assertEqual(p.entries.count(),0);self.assertFalse(p.tickets_button.isEnabled())
        p.refresh_reference();self.assertGreater(p.entries.count(),0);self.assertIsNone(p.entries.currentItem())
        p.entries.setCurrentRow(0)
        with patch.object(view.model,'packet',return_value=None):p.refresh_reference()
        self.assertEqual(p.entries.count(),0);self.assertEqual(p.player.toPlainText(),'')
        p.refresh_reference();self.assertIsNone(p.entries.currentItem())
    def test_all_ten_categories_have_same_order_titles_and_first_detail_as_before(self):
        old=self.old.ExpansionUpdatePanel(full_catalog=True);self.addCleanup(old.close)
        new=self.panel(full_catalog=True,defer_population=True)
        for category,_ in view.model.CATEGORIES:
            for p in (old,new):
                p.category.setCurrentIndex(p.category.findData(category))
                if hasattr(p,'ensure_populated'):p.ensure_populated()
            items=lambda p:[(p.entries.item(i).text(),p.entries.item(i).data(Qt.ItemDataRole.UserRole))for i in range(p.entries.count())]
            self.assertEqual(items(new),items(old),category)
            for p in (old,new):p.query_menu.sync()
            controls=lambda p:[(a.text(),a.isVisible(),a.isEnabled())for _,a in p.query_menu.actions]
            self.assertEqual(controls(new),controls(old),category)
            if old.entries.count():
                old.entries.setCurrentRow(0);new.entries.setCurrentRow(0)
                self.assertEqual(new.player.toPlainText(),old.player.toPlainText(),category)
                self.assertEqual(new.technical.toPlainText(),old.technical.toPlainText(),category)

def native_check(window,gui,require):
    from copy import deepcopy
    from rouge import expansion_reference
    before=deepcopy(window.run.state)
    # The shared native harness has already opened relics once.
    require(all(p._population_pending and p.entries.count()==0 for key,p in window.common_reference_panels.items()if key!='items'),'deferred_three_unopened_directories_not_populated')
    require(not window.common_reference_panels['items']._population_pending,'deferred_prior_exact_lookup_initialized_its_directory')
    require(all(hasattr(p,'query_menu')for p in window.common_reference_panels.values()),'deferred_all_query_menus_created_before_reading')
    require(all(hasattr(window.common_reference_panels[key],'reference_note_action')for key in('battle','events')),'deferred_eligible_note_actions_created_before_reading')
    with patch.object(expansion_reference,'packet',wraps=expansion_reference.packet)as source:
        first=window.reference_panel('choices');gui.processEvents()
        require(first.category.currentData()=='choices'and source.call_count==1,'deferred_first_activated_lookup_skips_unrequested_default_category')
    for category in window.common_reference_categories:
        panel=window.reference_panel(category,activate=False)
        panel.search.clear()
        require(panel.category.currentData()==category and not panel._population_pending,'deferred_direct_category_lookup_'+category)
        require(panel.entries.count()>0,'deferred_exact_category_has_rows_'+category)
    window.show();panel=window.reference_panel('relics');gui.processEvents()
    panel.entries.setCurrentRow(0);identity=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)
    require(window.open_item_reference(identity)and panel.result['row']['id']==identity,'deferred_exact_item_jump_keeps_identity')
    require(window.reference_panel('missing-category',activate=False)is None,'deferred_unknown_category_rejected_at_entry')
    require(window.reference_panel([],activate=False)is None,'deferred_bad_category_type_rejected_at_entry')
    text=panel.player.toPlainText();window.reference_panel('scenes');window.reference_panel('relics');gui.processEvents()
    require(panel.result['row']['id']==identity and panel.player.toPlainText()==text,'deferred_page_return_preserves_reading')
    with patch.object(expansion_reference,'packet',return_value=None):panel.refresh_reference()
    require(panel.entries.count()==0 and panel.result is None,'deferred_source_loss_clears_content')
    panel.refresh_reference();gui.processEvents()
    require(panel.entries.count()>0 and panel.entries.currentItem()is None,'deferred_source_recovery_does_not_restore_old_choice')
    panel.entries.setCurrentRow(0);gui.processEvents()
    require(window.run.state==before,'deferred_reference_navigation_does_not_change_run')
    window.player_validation_target=panel

if __name__=='__main__':unittest.main()
