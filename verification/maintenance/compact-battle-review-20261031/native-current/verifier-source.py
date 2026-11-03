"""Native grouped battle reader and optional sources, using temporary state."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtGui import QTextCursor
        from PySide6.QtGui import QPalette
        import win32gui,win32process
        from rouge.player_map_reader import make_reader
        from rouge import current_battle_reference as battle,current_reward_reference as reward_model
        before=deepcopy(window.run.state);window.show_compact();window.hide();gui.processEvents()
        dialog=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定关卡'},window.compact_window)
        require(dialog is not None,'actual_player_map_reference_factory_available');dialog.resize(760,650);dialog.show();gui.processEvents();p=dialog.panel
        def save(name):
            gui.processEvents();h=int(dialog.winId());require(dialog.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
            path=args.receipt.with_name(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
        def tab(tabs,widget):
            i=tabs.indexOf(widget);require(i>=0,'requested_player_page_has_actual_tab');QTest.mouseClick(tabs.tabBar(),Qt.MouseButton.LeftButton,pos=tabs.tabBar().tabRect(i).center());gui.processEvents();require(tabs.currentWidget()is widget,'actual_tab_click_selects_exact_page')
        require(p.tabs.count()==4,'four_main_player_sections')
        require(p.details_toggle.palette().color(QPalette.ColorRole.WindowText).lightness()<100,'disclosure_labels_readable_on_light_player_window')
        require(p.notice.isHidden()and p.rewards.notice.isHidden()and p.settlement.notice.isHidden(),'long_scope_notices_collapsed_by_default')
        require(not window.isVisible(),'reader_does_not_force_full_main_window');save('overview')
        tab(p.tabs,p.rewards);require(p.rewards.sections.count()==2,'both_reward_kinds_share_one_main_section')
        require(p.rewards.refresh_button.isHidden()and p.settlement.refresh_button.isHidden(),'one_parent_refresh_without_duplicate_child_buttons')
        row=next(r for r in p.rewards.result['rows']if r['source_action_keys']);p.rewards.choices.select_value(row['id']);p.rewards.source_combo.setCurrentIndex(1);key=p.rewards.source_combo.currentData();save('conditional-rewards')
        tab(p.rewards.sections,p.settlement);p.settlement.entry.setFocus();QTest.keyClick(p.settlement.entry,Qt.Key.Key_Home);QTest.keyClick(p.settlement.entry,Qt.Key.Key_Down);gui.processEvents()
        require(p.settlement.entry.currentData()=='map','actual_keyboard_selects_map_entry_declaration')
        require(p.settlement.result['actual_reward_total']is None,'documented_base_values_not_actual_total')
        base=deepcopy(p.settlement.result);QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
        require(p.rewards.sections.currentWidget()is p.settlement and p.settlement.result==base,'shared_refresh_keeps_base_page_and_declared_context')
        save('base-rewards')
        QTest.mouseClick(p.details_toggle,Qt.MouseButton.LeftButton);gui.processEvents();require(p.notice.isVisible()and p.notice.text()==battle.NOTICE,'explicit_details_reveal_full_original_scope')
        require(p.settlement.notice.isVisible(),'selected_base_scope_notice_available_on_request');save('scope-expanded')
        QTest.mouseClick(p.source_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
        require(p.technical.isVisible()and json.loads(p.technical.toPlainText())==p.result,'explicit_raw_source_preserves_complete_public_packet')
        cursor=p.technical.textCursor();cursor.setPosition(2);cursor.setPosition(20,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(cursor);p.technical.verticalScrollBar().setValue(30)
        old=(cursor.anchor(),cursor.position(),p.technical.verticalScrollBar().value());QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();cursor=p.technical.textCursor()
        require(p.source_toggle.isChecked()and old==(cursor.anchor(),cursor.position(),p.technical.verticalScrollBar().value()),'raw_reading_and_selection_survive_shared_refresh');save('raw-source')
        QTest.mouseClick(p.source_toggle,Qt.MouseButton.LeftButton);gui.processEvents();require(p.rewards.sections.currentWidget()is p.settlement,'closing_raw_source_returns_to_previous_reward_page')
        tab(p.rewards.sections,p.rewards.sections.widget(0));require(p.rewards.source_combo.currentData()==key,'conditional_reward_selection_survives_base_and_source_reading')
        QTest.mouseClick(p.rewards.source_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.action_key==key and p.tabs.currentIndex()==2,'reward_button_still_opens_exact_fixed_action')
        require('准确时刻：未知'in p.action_player.toPlainText(),'fixed_action_does_not_invent_actual_clock')
        configured=deepcopy(p.result)
        with patch.object(reward_model,'stage_rewards',return_value=None):
            require(p.refresh_reference(),'conditional_source_failure_preserves_battle_reader');require(p.rewards.result is None and not p.rewards.source_button.isEnabled(),'conditional_source_failure_clears_only_old_conditional_links');require(p.settlement.result==base and p.result==configured,'independent_base_and_battle_results_remain')
        with patch.object(battle,'stage_reference',return_value=None):
            require(not p.refresh_reference(),'parent_source_failure_rejected');require(p.result is None and p.rewards.result is None and p.settlement.result is None,'parent_loss_clears_all_three_result_sets');require(not p.source_toggle.isChecked()and not p.details_toggle.isChecked()and p.technical.toPlainText()=='','parent_loss_clears_optional_reading')
        require(p.refresh_reference(),'original_source_recovers');require(p.rewards.combo.currentData()is None and p.rewards.sections.currentIndex()==0,'recovery_requires_new_manual_reward_choice')
        require(window.run.state==before,'all_player_reading_preserves_owned_fixture_run')
        save('recovered-overview');window.player_validation_target=dialog
    player_acceptance.check=check;code=run(419,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)
