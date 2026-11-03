"""Existing enemy branches and image identities also drive the visible atlas."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_battle_view import CurrentBattlePanel
from rouge.player_catalog_grid import CatalogGrid


class EnemyAtlasReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def panel(self):
        p=CurrentBattlePanel('ro6_n_2_6');p.resize(900,720);p.show();p.tabs.setCurrentIndex(1)
        self.qt.processEvents();self.addCleanup(p.close);return p

    def keys(self,p):return [p.enemy_grid.item(i).data(Qt.ItemDataRole.UserRole)for i in range(p.enemy_grid.count())]

    def test_atlas_reuses_original_grid_and_has_every_exact_reference_without_selecting_one(self):
        p=self.panel();self.assertIsInstance(p.enemy_grid,CatalogGrid)
        self.assertEqual(set(self.keys(p)),{e['key']for e in p.result['enemies']})
        self.assertIsNone(p.enemy_grid.currentItem());self.assertIsNone(p.enemy_combo.currentData())
        self.assertTrue(all('不是实际出怪数量'in p.enemy_grid.item(i).toolTip()for i in range(p.enemy_grid.count())))

    def test_branch_filters_and_two_way_selection_share_exact_identity_and_original_text(self):
        p=self.panel()
        for tier,label in model.TIERS.items():
            if not p.enemy_choices.select_branch(label):continue
            self.assertEqual(set(self.keys(p)),{e['key']for e in p.result['enemies']if e['tier']==tier})
            if p.enemy_grid.count():
                p.enemy_grid.setCurrentRow(0);key=self.keys(p)[0]
                self.assertEqual(p.enemy_combo.currentData(),key)
                self.assertEqual(p.enemy_player.toPlainText(),model.enemy_text(next(e for e in p.result['enemies']if e['key']==key)))
        p.enemy_choices.select_branch('__overview__');p.enemy_combo.setCurrentIndex(p.enemy_combo.count()-1)
        self.assertEqual(p.enemy_grid.currentItem().data(Qt.ItemDataRole.UserRole),p.enemy_combo.currentData())

    def test_rebuilding_grid_reuses_verified_icons_without_rereading_image_source(self):
        p=self.panel();before=[p.enemy_grid.item(i).icon().cacheKey()for i in range(p.enemy_grid.count())]
        with patch.object(model,'picture_for_enemy',side_effect=AssertionError('Atlas must reuse existing icons')):p._sync_enemy_grid()
        self.assertEqual(before,[p.enemy_grid.item(i).icon().cacheKey()for i in range(p.enemy_grid.count())])

    def test_shared_tile_uses_full_grid_width_and_selected_body_retains_reading_space(self):
        p=self.panel();p.resize(760,650);self.qt.processEvents();p.enemy_grid.doItemsLayout()
        item=p.enemy_grid.item(0);self.assertGreaterEqual(p.enemy_grid.visualItemRect(item).width(),p.enemy_grid.gridSize().width()-8)
        p.enemy_grid.setCurrentItem(item);self.qt.processEvents()
        self.assertGreater(p.enemy_player.height(),160)
        self.assertLessEqual(p.enemy_portrait.width(),96);self.assertLessEqual(p.enemy_portrait.height(),96)

    def test_search_empty_result_clears_previous_selection_without_guessing_an_enemy(self):
        p=self.panel();p.enemy_grid.setCurrentRow(0);self.assertIsNotNone(p.enemy_key)
        p.enemy_search.setText('此文本不是敌人名称也不是图鉴能力__no_match')
        self.assertEqual(p.enemy_grid.count(),0);self.assertIsNone(p.enemy_key)
        self.assertEqual(p.enemy_player.toPlainText(),'请选择敌人或关联实体。')
        p.enemy_search.clear();self.assertIsNone(p.enemy_grid.currentItem());self.assertEqual(len(self.keys(p)),len(p.result['enemies']))

    def test_same_source_refresh_preserves_branch_selection_and_collapsed_state(self):
        p=self.panel();enemy=p.result['enemies'][-1];p.enemy_choices.select_value(enemy['key'])
        p.enemy_grid_toggle.setChecked(False);branch=p.enemy_choices.branch.currentData()
        self.assertTrue(p.refresh_reference());self.qt.processEvents()
        self.assertEqual(p.enemy_choices.branch.currentData(),branch);self.assertEqual(p.enemy_key,enemy['key'])
        self.assertEqual(p.enemy_grid.currentItem().data(Qt.ItemDataRole.UserRole),enemy['key'])
        self.assertFalse(p.enemy_grid.isVisible());self.assertEqual(p.enemy_grid_toggle.text(),'展开敌人图册')

    def test_missing_source_clears_atlas_and_restoration_does_not_reselect_old_enemy(self):
        p=self.panel();p.enemy_grid.setCurrentRow(0)
        with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
        self.assertEqual(p.enemy_grid.count(),0);self.assertIsNone(p.enemy_grid.selected_identity)
        self.assertTrue(p.refresh_reference());self.assertGreater(p.enemy_grid.count(),0);self.assertIsNone(p.enemy_key)
        self.assertIsNone(p.enemy_grid.currentItem())

    def test_same_name_distinct_reference_keys_are_not_merged(self):
        p=self.panel();fresh=deepcopy(p.result);duplicate=deepcopy(fresh['enemies'][0])
        duplicate['key']='separate-synthetic-reference';duplicate['reference_index']=1000;fresh['enemies'].append(duplicate)
        with patch.object(model,'stage_reference',return_value=fresh):p.refresh_reference()
        matches=[p.enemy_grid.item(i)for i in range(p.enemy_grid.count())if p.enemy_grid.item(i).text()==duplicate['name']]
        self.assertGreaterEqual(len(matches),2);self.assertIn(duplicate['key'],self.keys(p))
        item=next(item for item in matches if item.data(Qt.ItemDataRole.UserRole)==duplicate['key'])
        p.enemy_grid.setCurrentItem(item);self.assertEqual(p.enemy_key,duplicate['key']);self.assertIn('引用资料1001',item.toolTip())


if __name__=='__main__':unittest.main()
