from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import player_acceptance,current_battle_reference as model
from rouge.player_map_reader import make_reader
from player_ui_verification import run
out=R/'verification/maintenance/current-enemy-forecast-review-20261031/native-current';out.mkdir(exist_ok=False);images=[]

def check(section,w,gui,require):
    original_state=deepcopy(w.run.state)
    w.run.state['config']={'difficulty':{'value':15,'modeDifficulty':'NORMAL','captured_at':1},'zone':{'id':'zone_1','name':'玻利瓦尔肤层','main_zone_index':1,'captured_at':1}}
    w.run.state['last_node_content']={'kind':'battle','title':'作战参考','stage_id':'ro6_n_1_1'}
    w.show_compact();w.compact_window.open_scene_battle();gui.processEvents();scene=w.compact_window.scene_popup.panel
    scene.stages.setCurrentIndex(scene.stages.findData('ro6_n_1_1'));gui.processEvents()
    require(scene.open_button.isEnabled(),'exact_scene_stage_selected')
    QTest.mouseClick(scene.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
    dialog=scene.dialog;p=dialog.panel;dialog.resize(1120,800);gui.processEvents()
    require(dialog.isVisible()and p.isVisible(),'real_scene_button_opens_owned_current_reader')
    require(p.run_config['difficulty']['value']==15 and p.run_config['zone']['id']=='zone_1','local_conditions_automatically_imported')
    QTest.mouseClick(p.tabs.tabBar(),Qt.MouseButton.LeftButton,pos=p.tabs.tabBar().tabRect(1).center());gui.processEvents()
    tree=p.enemy_overview.tree
    def image(name,widget=dialog):
        gui.processEvents();file=out/(name+'.png');assert widget.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
    require(p.enemy_overview.isVisible()and tree.columnCount()==7,'seven_column_image_and_environment_component_overview')
    rows=[tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())]
    duck=next(e for e in p.result['enemies']if e['id']=='enemy_2001_duckmi');item=next(row for row in rows if row.data(0,Qt.ItemDataRole.UserRole)==duck['key'])
    require(item.text(1)=='28080'and item.text(2)=='138','visible_known_environment_numbers_match_declared_conditions')
    require('完整本局总量仍未知'in p.enemy_overview.notice.text(),'subtotal_not_advertised_as_full_current_panel')
    require(not item.icon(0).isNull(),'original_exact_enemy_portrait_retained')
    image('qualified-overview-1120')
    tree.scrollToItem(item);gui.processEvents();QTest.mouseClick(tree.viewport(),Qt.MouseButton.LeftButton,pos=tree.visualItemRect(item).center());gui.processEvents()
    require(p.enemy_key==duck['key']and p.enemy_player.isVisible(),'actual_table_row_opens_exact_enemy_detail')
    require('已证环境分项'in p.enemy_player.toPlainText()and'完整本局面板：未知'in p.enemy_player.toPlainText(),'detail_explains_known_subtotal_and_unknown_complete_total')
    image('qualified-detail')
    group=tree.topLevelItem(0);group.setExpanded(False);owned=id(scene.dialog)
    w.run.state['config']['difficulty']['value']=0;state=deepcopy(w.run.state);scene.refresh();gui.processEvents()
    require(id(scene.dialog)==owned and p.enemy_key==duck['key'],'same_scene_refresh_preserves_window_and_selected_enemy')
    require(p.enemy_forecasts[duck['key']]['environment_component']['maxHp']==10800,'same_scene_new_difficulty_updates_subtotal')
    require(not tree.topLevelItem(0).isExpanded(),'same_scene_update_preserves_group_fold')
    require(w.run.state==state,'viewing_and_recomputing_do_not_change_run_memory')
    image('updated-subtotal-preserved')
    before=p.enemy_forecasts
    with patch.object(model,'stage_reference',return_value=None):require(p.refresh_reference()is False,'source_loss_reported')
    require(not p.enemy_forecasts and tree.topLevelItemCount()==0,'source_loss_clears_numbers_and_rows')
    require(p.refresh_reference()and p.enemy_forecasts,'source_recovery_requalifies_inputs')
    require(p.enemy_key is None,'source_recovery_does_not_restore_old_enemy_selection')
    historical=make_reader('battle',{'id':'ro6_n_1_1','title':'隔离历史参考'},w,historical=True,config=w.run.state['config']);historical.resize(1120,800);historical.show();historical.panel.tabs.setCurrentIndex(1);gui.processEvents()
    require(historical.panel.run_config=={}and historical.panel.enemy_forecasts=={},'historical_reader_never_imports_current_conditions')
    image('historical-context-empty',historical);historical.close()
    w.run.state['last_node_content']['stage_id']='ro6_b_4_b';scene.refresh();scene.stages.setCurrentIndex(scene.stages.findData('ro6_b_4_b'));QTest.mouseClick(scene.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
    second=scene.dialog;second.resize(1120,800);enemy=next(e for e in second.panel.result['enemies']if e['id']=='enemy_1177_dufrbl_2');second.panel.tabs.setCurrentIndex(1);second.panel.enemy_choices.select_value(enemy['key']);gui.processEvents()
    require(second.panel.enemy_forecasts[enemy['key']]['environment_component']is None,'unknown_current_tier_does_not_borrow_old_normal_numbers')
    require('类别尚不能'in second.panel.enemy_player.toPlainText(),'unqualified_current_reference_has_plain_chinese_reason')
    image('unqualified-tier',second)
    w.player_validation_target=second
    # All assignments above are deliberate fixtures inside the verifier's
    # isolated run, not observations or edits of the user's actual run.
    w.run.state=original_state

with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'temporary_public_preview_only':True,'actual_game_or_independent_mechanism_calibration_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
