"""Retain map/recent-reader checks and exercise the shared candidate image atlas."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,runpy,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
import player_ui_verification
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    native_run=player_ui_verification.run;images=[]
    def augmented_run(section,receipt):
        previous=player_acceptance.check
        def check(section,window,gui,require):
            from PySide6.QtCore import Qt
            from PySide6.QtTest import QTest
            from rouge import current_battle_reference as model
            from rouge.player_catalog_grid import CatalogGrid
            import win32gui,win32process
            previous(section,window,gui,require)
            dialog=window.player_validation_target;p=dialog.panel
            def save(name,target=None):
                widget=dialog if target is None else target
                gui.processEvents();h=int(widget.winId())
                require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
                path=receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
            p.tabs.setCurrentIndex(1);gui.processEvents()
            require(isinstance(p.enemy_grid,CatalogGrid)and p.enemy_grid.isVisible(),'existing_catalog_grid_is_visible_enemy_atlas')
            require(p.enemy_grid.count()==len(p.result['enemies'])and p.enemy_grid.currentItem()is None,'all_exact_candidates_visible_without_default_enemy')
            save('enemy-atlas-overview')
            item=p.enemy_grid.item(0);p.enemy_grid.scrollToItem(item);gui.processEvents()
            require(p.enemy_grid.visualItemRect(item).width()>=p.enemy_grid.gridSize().width()-8,'shared_delegate_uses_full_image_and_name_tile_width')
            QTest.mouseClick(p.enemy_grid.viewport(),Qt.MouseButton.LeftButton,pos=p.enemy_grid.visualItemRect(item).center());gui.processEvents()
            key=item.data(Qt.ItemDataRole.UserRole);enemy=next(e for e in p.result['enemies']if e['key']==key)
            require(p.enemy_key==key and p.enemy_combo.currentData()==key,'actual_image_click_selects_exact_enemy_reference')
            require(p.enemy_player.toPlainText()==model.enemy_text(enemy),'image_selection_keeps_original_mechanism_and_unknown_stats')
            require(p.enemy_player.height()>160 and p.enemy_portrait.width()<=96,'selected_enemy_keeps_body_readable_beside_small_portrait')
            save('enemy-atlas-selected')
            branch=p.enemy_choices.branch;index=next(i for i in range(1,branch.count())if branch.itemData(i)!='__overview__')
            branch.setFocus();QTest.keyClick(branch,Qt.Key.Key_Home)
            for _ in range(index):QTest.keyClick(branch,Qt.Key.Key_Down)
            gui.processEvents();expected=[identity for _,identity,_ in p.enemy_choices.entries()]
            require([p.enemy_grid.item(i).data(Qt.ItemDataRole.UserRole)for i in range(p.enemy_grid.count())]==expected,'actual_classification_choice_filters_both_enemy_controls')
            item=p.enemy_grid.item(0);p.enemy_grid.scrollToItem(item);gui.processEvents();QTest.mouseClick(p.enemy_grid.viewport(),Qt.MouseButton.LeftButton,pos=p.enemy_grid.visualItemRect(item).center());gui.processEvents()
            key=p.enemy_key;chosen_branch=branch.currentData();QTest.mouseClick(p.enemy_grid_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
            require(not p.enemy_grid.isVisible()and p.enemy_grid_toggle.text()=='展开敌人图册','actual_atlas_collapse_keeps_enemy_reading')
            QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(p.enemy_key==key and branch.currentData()==chosen_branch and not p.enemy_grid.isVisible(),'parent_refresh_preserves_enemy_branch_selection_and_collapse')
            save('enemy-atlas-collapsed')
            QTest.mouseClick(p.enemy_grid_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
            p.enemy_search.setFocus();QTest.keyClicks(p.enemy_search,'__not_an_enemy_7843__');gui.processEvents()
            require(p.enemy_grid.count()==0 and p.enemy_key is None and p.enemy_combo.currentData()is None,'actual_search_no_match_clears_old_image_and_selection')
            save('enemy-atlas-empty-search')
            QTest.keyClick(p.enemy_search,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier);QTest.keyClick(p.enemy_search,Qt.Key.Key_Backspace);gui.processEvents()
            require(p.enemy_grid.count()>0 and p.enemy_grid.currentItem()is None,'actual_search_clear_restores_candidates_without_guess')
            branch.setFocus();QTest.keyClick(branch,Qt.Key.Key_Home);gui.processEvents()
            for width in (560,920):
                dialog.resize(width,700);gui.processEvents();p.enemy_grid.doItemsLayout();gui.processEvents()
                require(p.enemy_grid.viewport().width()>0 and p.enemy_grid.count()==len(p.result['enemies']),'atlas_resize_keeps_all_exact_references_'+str(width));save('enemy-atlas-width-'+str(width))
            with patch.object(model,'stage_reference',return_value=None):QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(p.enemy_grid.count()==0 and p.enemy_grid.selected_identity is None,'source_failure_clears_all_candidate_images')
            QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(p.enemy_grid.count()>0 and p.enemy_grid.currentItem()is None and p.enemy_key is None,'source_restore_requires_manual_enemy_choice')
            p.tabs.setCurrentIndex(1);save('enemy-atlas-restored')
            from rouge.player_feature_414_acceptance import check as inventory_checks
            from rouge.player_feature_421_acceptance import check as parts_checks
            inventory_checks(window,gui,require);save('shared-inventory-grid',window.player_validation_target)
            parts_checks(window,gui,require);save('shared-parts-grid',window.player_validation_target)
            window.compact_window.inventory_popup.close();window.player_validation_target=dialog
        player_acceptance.check=check
        result=native_run(section,receipt)
        receipt.with_name('atlas-images.json').write_text(json.dumps({'images':images,'temporary_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
        return result
    with patch.object(player_ui_verification,'run',augmented_run),patch.object(sys,'argv',['verify_scene_reader_review.py','--receipt',str(args.receipt)]):
        runpy.run_path(str(Path(__file__).with_name('verify_scene_reader_review.py')),run_name='__main__')
