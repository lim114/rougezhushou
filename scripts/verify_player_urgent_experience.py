"""Focused native acceptance for the reported docking and selector regressions."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]


def main():
    out=Path(sys.argv[1]).resolve()
    if len(sys.argv)==2:
        out.mkdir(parents=True,exist_ok=False)
        with (out/'stdout.txt').open('wb')as stdout,(out/'stderr.txt').open('wb')as stderr:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,str(out),'child'],stdout=stdout,stderr=stderr)
            code=child.wait()
        (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
        print({'exit':code});print((out/'stderr.txt').read_text('utf8')[-2400:])
        return code
    from types import SimpleNamespace
    from copy import deepcopy
    from PySide6.QtCore import QTimer,QRect,QPoint,Qt
    from PySide6.QtWidgets import QComboBox,QSystemTrayIcon
    from PySide6.QtTest import QSignalSpy
    from rouge import player_acceptance,player_toolbar_acceptance
    from rouge.branch_choice import BranchChoice
    import player_ui_verification as ui

    def check(section,window,gui,require):
        for timer in window.findChildren(QTimer):timer.stop()
        before=deepcopy(window.run.state)
        player_toolbar_acceptance.check(window,gui,require)
        c=window.compact_window;b=c.game_binding
        for timer in c.findChildren(QTimer):timer.stop()
        area=c.screen().availableGeometry()
        snapshot={'key':(123,456),'active':True,'logical_client':QRect(area.left()+60,area.top()+60,area.width()-120,area.height()-140),'screen':c.screen()}
        b.apply(snapshot);gui.processEvents()
        require(c.isVisible()and not c.geometry().intersects(snapshot['logical_client']),'bound_toolbar_fully_outside_game_client')
        require(area.contains(c.geometry()),'bound_toolbar_fully_inside_available_screen')
        c._drag_dock(QPoint(-100,-100));gui.processEvents()
        require(not c.geometry().intersects(snapshot['logical_client']),'drag_cannot_put_bound_toolbar_inside_game')
        full={**snapshot,'logical_client':area};b.apply(full);gui.processEvents()
        require(not c.isVisible()and c.property('outsideSpaceHidden'),'fullscreen_hides_only_toolbar_without_inner_overlay')
        require(QSystemTrayIcon.isSystemTrayAvailable()and c.tray.isVisible(),'native_system_tray_available_and_entry_visible')
        c.tray_menu.actions()[0].trigger();gui.processEvents()
        require(c.reference_window.isVisible()and c.reference_window.pages.currentWidget()is c.overview_popup,'tray_action_opens_existing_shared_overview')
        b.apply(full);gui.processEvents()
        require(c.reference_window.isVisible()and not c.isVisible(),'fullscreen_tick_keeps_requested_reader_without_reshowing_toolbar')
        c.reference_window.close();b.apply(snapshot);gui.processEvents()
        require(c.isVisible()and not c.property('outsideSpaceHidden'),'leaving_fullscreen_restores_exterior_toolbar')
        moved={**snapshot,'logical_client':snapshot['logical_client'].translated(20,15)};b.apply(moved)
        require(not c.geometry().intersects(moved['logical_client']),'game_move_repositions_toolbar_outside')
        b.apply(full);b.set_enabled(False);gui.processEvents()
        require(c.isVisible()and not c.property('outsideSpaceHidden'),'disabling_follow_restores_independent_toolbar')
        b.enabled=True;b.apply(snapshot);c.toggle_visibility();b.apply(full);b.apply(snapshot)
        require(not c.isVisible(),'manual_hide_survives_fullscreen_and_game_restore')
        require([a.text()for a in c.tray_menu.actions()if a.text()][:-1]==[button.accessibleName()for button in c.tool_buttons],'tray_has_all_seven_toolbar_entries')
        c.tray_menu.actions()[6].trigger();gui.processEvents();b.apply(snapshot)
        require(c.hidden_windows is None and c.reference_window.isVisible()and c.reference_window.pages.currentWidget()is c.settings_popup,'tray_reopens_requested_page_after_manual_hide')
        c.reference_window.close();b.enabled=False;b.snapshot=None;b.previous=None
        combo=QComboBox();branches=BranchChoice(combo,[('近卫',[('干员甲','a',c.tool_buttons[0].normal_icon),('干员乙','b',c.tool_buttons[0].normal_icon)])],overview_label='总览')
        branches.select_value('b');combo.show();combo.showPopup();gui.processEvents()
        resets=QSignalSpy(combo.model().modelReset)
        for _ in range(10):branches.set_groups(branches.groups,emit=False)
        require(combo.view().isVisible()and combo.currentData()=='b'and resets.count()==0,'native_open_selector_survives_ten_identical_refreshes')
        combo.hidePopup();combo.close();branches.close();combo.deleteLater();branches.deleteLater()
        from rouge.current_battle_view import CurrentBattlePanel
        reader=CurrentBattlePanel('ro6_n_1_1')
        reader.set_context({'difficulty':{'value':15,'captured_at':1},'zone':{'id':'zone_1','captured_at':1}})
        previous=reader.enemy_forecasts
        reader.set_context({'difficulty':{'value':15,'captured_at':2},'zone':{'id':'zone_1','captured_at':2}})
        require(reader.enemy_forecasts is previous and reader.run_config['difficulty']['captured_at']==2,'unchanged_environment_keeps_forecast_but_updates_read_time')
        reader.set_context({'difficulty':{'value':14,'captured_at':3},'zone':{'id':'zone_1','captured_at':3}})
        require(reader.enemy_forecasts is not previous,'actual_difficulty_change_recomputes_enemy_forecast')
        reader.close();reader.deleteLater();gui.processEvents()
        require(window.run.state==before,'urgent_experience_fixes_preserve_run')
        window.player_validation_target=c
    player_acceptance.check=check
    return ui.run(472,out/'window.json')

if __name__=='__main__':raise SystemExit(main())
