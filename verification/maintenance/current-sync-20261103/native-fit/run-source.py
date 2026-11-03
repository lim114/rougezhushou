"""Focused Windows checks for chronological backfill and compact shared readers."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]


def main():
    out=Path(sys.argv[1]).resolve()
    if len(sys.argv)==2:
        out.mkdir(parents=True,exist_ok=False)
        with(out/'stdout.txt').open('wb')as a,(out/'stderr.txt').open('wb')as b:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,str(out),'child'],stdout=a,stderr=b);code=child.wait()
        (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
        (out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});print((out/'stderr.txt').read_text('utf8')[-2000:]);return code
    from copy import deepcopy
    import time
    import numpy as np
    from PySide6.QtCore import QTimer,QRect,Qt
    from PySide6.QtTest import QSignalSpy
    from PySide6.QtWidgets import QApplication
    from rouge import player_acceptance
    from rouge.observation_timeline import ObservationTimeline
    from rouge.player_reference_window import ToolPage
    import player_ui_verification as ui

    def check(section,w,gui,require):
        before=deepcopy(w.run.state);account=deepcopy(w.account_cache.records)
        w.show_compact();c=w.compact_window
        for timer in w.findChildren(QTimer):timer.stop()
        c.game_binding.snapshot={'key':(123,456),'active':True,'logical_client':QRect(60,70,c.screen().availableGeometry().width()-120,c.screen().availableGeometry().height()-140),'screen':c.screen()}
        c.open_map();gui.processEvents();host=c.reference_window
        require(host.width()<=max(360,round(host.screen().availableGeometry().width()*.28))+24,'bound_reader_first_open_is_compact')
        area=host.screen().availableGeometry();require(area.contains(host.geometry()),'compact_reader_stays_on_screen')
        from rouge.player_map_acceptance import fixtures as maps
        w.run.state['maps']={'zone_1':deepcopy(maps()[0][0])};w.run.state['config']['zone']={'id':'zone_1','name':'玻利瓦尔肤层'}
        w.render_map();gui.processEvents();mp=c.map_popup.panel
        require(mp.scroll.horizontalScrollBar().maximum()==0 and mp.scroll.verticalScrollBar().maximum()==0,'compact_fit_map_has_no_internal_scroll_crop')
        _,points=mp.view._positions();require(bool(points)and all(mp.view.rect().contains(point.toPoint())for point in points.values()),'every_map_node_center_is_visible_in_compact_fit')
        mp.zoom.setCurrentIndex(2);gui.processEvents();require(mp.scroll.horizontalScrollBar().maximum()>0,'explicit_zoom_still_allows_map_scroll')
        mp.zoom.setCurrentIndex(0);gui.processEvents()
        actual=host.geometry();client=c.game_binding.snapshot['logical_client'];overlap=actual.intersected(client)
        require(overlap.width()*overlap.height()<client.width()*client.height()*.4,'fallback_reader_uses_under_40_percent_game_client_in_test_geometry')
        host.resize(650,450);gui.processEvents();size=host.size();position=host.pos();c.refresh();gui.processEvents()
        require(host.size()==size and host.pos()==position,'refresh_preserves_reader_user_size_and_position')
        w.run.state['last_node_content']={'kind':'battle','title':'遗忘时间','stage_id':'ro6_n_1_1'}
        c.open_scene_battle();source=c.scene_popup;p=source.panel;p.stages.setCurrentIndex(1);selected=p.stages.currentData()
        require(p.open_stage(),'recent_battle_opens_shared_reader');gui.processEvents();child=host.pages.currentWidget()
        require(isinstance(child,ToolPage)and child.source_parent is source and p.dialog is None,'recent_battle_no_independent_popover')
        reader=child.panel;reader.enemy_choices.select_value(reader.result['enemies'][0]['key']);reader.open_enemy_spawns();gui.processEvents()
        require(host.pages.currentWidget()is not child and isinstance(host.pages.currentWidget(),ToolPage),'recent_enemy_spawns_remain_in_shared_host')
        require(not any(type(v).__name__=='CurrentEnemySpawnsDialog'and v.isVisible()for v in QApplication.topLevelWidgets()),'no_second_enemy_spawn_window')
        require(c.present(source),'back_to_recent_source');require(p.stages.currentData()==selected,'recent_stage_choice_survives_shared_navigation')
        w.run.state['last_node_content']={'kind':'event','title':'呼吸的红苔'};p.refresh();p.event_choices.setCurrentIndex(1)
        require(p.open_event(),'recent_event_opens_shared_reader');gui.processEvents();event_page=host.pages.currentWidget()
        require(isinstance(event_page,ToolPage)and p.event_dialog is None,'recent_event_no_independent_dialog')
        c.present(source);require(p.open_event()and host.pages.currentWidget()is event_page and event_page.panel.result is not None,'return_retains_exact_event_reader')
        from PySide6.QtWidgets import QDialog
        from PySide6.QtTest import QTest
        import win32gui
        decoy=QDialog(w);decoy.setWindowTitle('助手焦点隔离验证');decoy.show();decoy.activateWindow();QTest.qWait(80);gui.processEvents()
        require(win32gui.GetForegroundWindow()==int(decoy.winId()),'owned_focus_probe_is_active')
        w.run.state['last_node_content']=None;c.refresh();gui.processEvents()
        require(win32gui.GetForegroundWindow()==int(decoy.winId()),'automatic_invalid_source_fallback_does_not_steal_focus')
        decoy.close();decoy.deleteLater();host.close()
        # Reset only these temporary verification objects before the sampling case.
        w.run.state=deepcopy(before);w.account_cache.records=deepcopy(account);w.operator_observations=w.account_cache.records
        timeline=ObservationTimeline(w.run,w.account_cache);at=max(time.time(),before['started_at']+1)
        rows=[{'page':'unknown','nodes':[],'captured_at':at,'run':{'resources':{'gold':{'value':2}},'node_content':{'kind':'event','title':'较早事件'}}},
              {'page':'unknown','nodes':[],'captured_at':at,'run':{'resources':{'gold':{'value':1}},'operators':[{'id':'mechanist','scope':'run','fields':{'elite':1,'level':80},'skill_ranks':{}}]}},
              {'page':'unknown','nodes':[],'captured_at':at,'run':{'resources':{'gold':{'value':9}},'node_content':{'kind':'battle','title':'较新关卡'}}}]
        image=np.full((24,36,3),65,np.uint8)
        for seq,floor in((3,1),(1,2),(2,None)):
            packet=deepcopy(rows[seq-1]);timeline=timeline.prepare(packet,seq,floor);packet['_timeline_result']=timeline
            packet['_sampling']={'epoch':w.sample_epoch,'generation':w.capture.stats()['generation'],'seq':seq}
            w.sample_received((image,packet));gui.processEvents()
            require(w.observation['captured_at']==at and w.observation['_sampling']['seq']==3,'display_remains_on_newest_frame_'+str(seq))
            require(w.run.state['resources']['gold']['value']==9,'older_frame_does_not_roll_back_resource_'+str(seq))
        require('mechanist'in w.run.state['operators'],'short_team_page_retained_after_current_read')
        require(any(e.get('kind')=='node_content_seen'and e.get('title')=='较早事件'for e in w.run.state['history']),'short_event_page_retained_in_history')
        require(w.run.state['last_node_content']['title']=='较新关卡','last_node_remains_newest_after_backfill')
        require(not timeline.pending,'chronological_journal_compacts_after_drain')
        w.operator_choices.select_value('kaltsit');w.update_operator();c.open_operators();gui.processEvents()
        w.skill.showPopup();gui.processEvents();resets=QSignalSpy(w.skill.model().modelReset);w.update_operator(preserve_level=True)
        require(resets.count()==0 and w.skill.view().isVisible(),'open_skill_menu_survives_same_training_refresh');w.skill.hidePopup()
        # The harness asserts its isolated baseline is restored; no private files exist here.
        w.run.state=before;w.account_cache.records=account;w.operator_observations=account
        w.observation=None;w.map_frame=None;w.sync_run_config();c.open_map();gui.processEvents()
        w.player_validation_target=host
    player_acceptance.check=check
    return ui.run(472,out/'window.json')

if __name__=='__main__':raise SystemExit(main())
