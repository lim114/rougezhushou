"""Native map/recent reader sharing, scoped palette and owned child closure."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPalette
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QPushButton
        import win32gui,win32process
        from rouge import current_battle_reference as model
        from rouge.player_map_reader import make_reader,REFERENCE_STYLE
        from rouge.player_feature_431_acceptance import check as retained_map_checks
        initial=deepcopy(window.run.state)
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
        def choose(combo,identity):
            index=combo.findData(identity);require(index>=0,'exact_source_choice_available')
            combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
            for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
            gui.processEvents();require(combo.currentData()==identity,'actual_keyboard_selects_exact_source')
        try:
            retained_map_checks(window,gui,require)
            require(window.run.state==initial,'retained_map_fixture_restores_owned_run')
            window.run.state['last_node_content']={'kind':'battle','stage_id':'ro6_n_2_6','title':'旧标题参考，不用于身份'}
            window.show_compact();window.hide();bar=window.compact_window;bar.open_scene_battle();gui.processEvents();scene=bar.scene_popup.panel
            choose(scene.stages,'ro6_n_2_6')
            with patch.object(model,'stage_reference',wraps=model.stage_reference)as load:QTest.mouseClick(scene.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
            dialog=scene.dialog;require(dialog is not None and load.call_count==1,'recent_scene_uses_single_shared_stage_load')
            require(dialog.panel.stage_id=='ro6_n_2_6'and dialog.objectName()=='mapReferenceWindow'and dialog.styleSheet()==REFERENCE_STYLE,'recent_scene_uses_actual_shared_factory_and_exact_source')
            require(dialog.palette().color(QPalette.ColorRole.Window).name()=='#262528','reference_canvas_matches_sampled_video_background')
            require(dialog.panel.details_toggle.palette().color(QPalette.ColorRole.WindowText).lightness()>200,'optional_reading_labels_visible_on_dark_canvas')
            require(dialog.windowFlags()&Qt.WindowType.FramelessWindowHint,'recent_scene_has_shared_frameless_tool_window');save(dialog,'recent-battle')
            dialog.panel.tabs.setCurrentWidget(dialog.panel.rewards);row=next(r for r in dialog.panel.rewards.result['rows']if r['source_action_keys']);dialog.panel.rewards.choices.select_value(row['id']);dialog.panel.rewards.source_combo.setCurrentIndex(1)
            selected=(dialog.panel.rewards.combo.currentData(),dialog.panel.rewards.source_combo.currentData());save(dialog,'recent-rewards')
            require(dialog.panel.open_spawn_candidates(),'owned_spawn_reader_opens');child=dialog.panel.spawn_candidates_dialog;gui.processEvents();require(child.isVisible(),'owned_spawn_reader_really_visible');save(child,'owned-spawn-reader')
            close=dialog.findChild(QPushButton,'popoverCloseButton');require(close is not None,'shared_window_has_actual_close_button');QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents()
            require(not dialog.isVisible()and not child.isVisible(),'actual_close_button_closes_owner_and_its_spawn_reader')
            require(dialog.panel.settlement.result is None,'owner_close_reuses_original_reader_cleanup')
            QTest.mouseClick(scene.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
            require(scene.dialog is dialog and dialog.isVisible()and dialog.panel.settlement.result is not None,'reopen_refreshes_same_window_and_rehydrates_base_reference')
            require(selected==(dialog.panel.rewards.combo.currentData(),dialog.panel.rewards.source_combo.currentData()),'reopen_preserves_exact_conditional_reward_and_source')
            old=dialog
            with patch.object(model,'packet',return_value=None):
                scene.refresh();gui.processEvents();require(scene.dialog is None and not old.isVisible()and not scene.open_button.isEnabled(),'source_loss_clears_recent_reader_and_old_window')
            scene.refresh();require(scene.stages.currentData()is None,'source_recovery_needs_new_exact_manual_choice')
            window.run.state['last_node_content']={'kind':'event','title':'桑尼的邀请'};scene.refresh();gui.processEvents();scene.event_choices.setCurrentIndex(1);scene.event_entries.setCurrentIndex(1)
            target=scene.event_result['selected']['event_id'];QTest.mouseClick(scene.event_open,Qt.MouseButton.LeftButton);gui.processEvents()
            require(scene.event_dialog is not None and scene.event_dialog.isVisible(),'recent_event_reader_opens_from_actual_button')
            require(scene.event_dialog.panel.result['event']['id']==target and scene.event_dialog.styleSheet()==REFERENCE_STYLE,'recent_event_keeps_exact_event_and_shared_theme');save(scene.event_dialog,'recent-event')
            bar.scene_popup.close();gui.processEvents();require(scene.event_dialog is None,'closing_recent_scene_closes_owned_event_reader')
            final=make_reader('battle',{'id':'ro6_n_2_6','title':'仅固定资料'},bar);require(final is not None,'map_factory_reader_still_available');final.resize(760,650);final.show();gui.processEvents()
            require(final.styleSheet()==REFERENCE_STYLE,'map_and_recent_battle_share_identical_style');save(final,'map-reader');window.player_validation_target=final
        finally:
            window.run.state=initial
        require(window.run.state==initial,'all_public_reader_operations_preserve_owned_fixture_run')
    player_acceptance.check=check;code=run(419,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)
