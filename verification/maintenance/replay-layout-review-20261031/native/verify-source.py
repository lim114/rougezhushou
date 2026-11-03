from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import player_acceptance
from rouge.player_replay_archive import reload_history
from rouge.map_recognition import map_data
from tests.test_history_reader_review import history_example
from player_ui_verification import run
out=R/'verification/maintenance/replay-layout-review-20261031/native'
out.mkdir(exist_ok=False);images=[]

def check(section,w,gui,require):
    before=deepcopy(w.run.state)
    try:
        state,t,ids=history_example();state['started_at']=100;state['id']='public-archived-map'
        second=next(t for t in map_data()['templates']if t['zone_id']=='zone_2')
        state['history'] += [{'kind':'map_confirmed','zone_id':second['zone_id'],'template_id':second['id'],'at':200},
            {'kind':'floor_resources_read','zone_id':second['zone_id'],'template_id':second['id'],'source':'same_frame_zone_and_resources','values':{'gold':11,'parts_count':2},'at':201},
            {'kind':'map_position_updated','zone_id':second['zone_id'],'current':second['nodes'][0]['id'],'at':202}]
        w.show_compact();bar=w.compact_window;bar.open_replay();gui.processEvents();popup=bar.replay_popup;p=popup.panel;popup.resize(900,720)
        require(p.tabs.currentWidget()is p.archive_page,'first_open_shows_readable_session_cards')
        for identity,at in [('public-archived-map',100),('second-archive',90)]:
            copy=deepcopy(state);copy.update(id=identity,started_at=at);p.history_store.archive(copy)
        reload_history(p);gui.processEvents()
        require(p.session_cards.count()==3,'current_and_two_real_temporary_archives_listed')
        require('结算分数与种子尚未确认'in p.session_cards.item(1).text(),'unread_result_fields_not_invented_on_cards')
        files={q.name:q.read_bytes()for q in p.history_store.folder.iterdir()}
        def image(name):
            gui.processEvents();q=out/(name+'.png');assert popup.grab().save(str(q));images.append({'path':q.relative_to(R).as_posix(),'sha256':sha256(q.read_bytes()).hexdigest()})
        def card(identity):
            return next(p.session_cards.item(i)for i in range(p.session_cards.count())if p.session_cards.item(i).data(Qt.ItemDataRole.UserRole)==identity)
        def click_card(identity):
            item=card(identity);p.session_cards.scrollToItem(item);QTest.mouseClick(p.session_cards.viewport(),Qt.MouseButton.LeftButton,pos=p.session_cards.visualItemRect(item).center());gui.processEvents()
        image('session-cards');click_card('archive:public-archived-map');page=p.nodes
        require(p.snapshot['id']=='public-archived-map'and p.tabs.currentWidget()is page,'real_card_click_opens_exact_archive_map')
        require(page.floor_tabs.currentIndex()==page.floors.findData(second['zone_id']),'card_opens_latest_saved_floor_without_guessing_path')
        require({r['value']for r in page.resource_pills.rows}=={'11','2'},'latest_floor_resource_pills_use_saved_snapshot')
        require(page.view.graph['template_id']==second['id'],'exact_latest_floor_template_used');image('second-floor')
        first=page.floors.findData(t['zone_id']);QTest.mouseClick(page.floor_tabs,Qt.MouseButton.LeftButton,pos=page.floor_tabs.tabRect(first).center());gui.processEvents()
        require(page.floors.currentIndex()==first and page.view.selected==ids[-1],'real_floor_tab_selects_latest_saved_read_in_that_floor')
        require(page.resource_pills.rows[0]['value']=='99','first_floor_keeps_its_own_resource_snapshot');image('first-floor')
        QTest.mouseClick(page.entries.viewport(),Qt.MouseButton.LeftButton,pos=page.entries.visualItemRect(page.entries.item(0)).center());gui.processEvents()
        require(not page.resource_pills.rows and page.resource_pills.flow.count()==0,'earliest_record_clears_later_resource_pills')
        require(page.resources.isVisible()and '尚未记录'in page.resources.text(),'missing_resource_snapshot_explained_visibly')
        item=page.entries.item(2);QTest.mouseClick(page.entries.viewport(),Qt.MouseButton.LeftButton,pos=page.entries.visualItemRect(item).center());gui.processEvents()
        require(page.resource_pills.rows[0]['value']=='7','earlier_prefix_reads_7_instead_of_later99_or_current999')
        selected=page.entries.currentRow();original=deepcopy(page.view.graph)
        w.run.state['resources']['gold']={'value':777,'captured_at':900};bar.refresh();gui.processEvents()
        require(p.snapshot['id']=='public-archived-map'and page.entries.currentRow()==selected and page.view.graph==original,'current_run_refresh_does_not_replace_archive_reading')
        for width,height in [(720,580),(1100,700),(900,720)]:
            popup.resize(width,height);gui.processEvents()
            require(page.entries.currentRow()==selected and page.view.graph==original,'map_reading_survives_'+str(width)+'x'+str(height))
        image('historical-prefix')
        p.history_list_button.click();gui.processEvents();require(p.session_cards.isVisible(),'back_to_session_cards_uses_same_window')
        click_card('archive:public-archived-map');require(page.entries.currentRow()==selected,'reopening_same_card_retains_selected_prefix')
        with patch.object(p.history_store,'records',side_effect=OSError('isolated archive read error')):reload_history(p)
        gui.processEvents();require(p.sessions.currentData()=='unavailable'and p.snapshot['id']is None,'lost_archive_clears_old_source_without_current_fallback')
        require(page.view.graph is None and not page.resource_pills.rows,'lost_archive_clears_map_and_resources');image('unavailable-archive')
        reload_history(p);require(p.sessions.currentData()=='unavailable','source_recovery_requires_explicit_selection')
        p.history_list_button.click();gui.processEvents();click_card('archive:public-archived-map')
        require(p.snapshot['id']=='public-archived-map','manual_reselection_recovers_exact_source')
        require(files=={q.name:q.read_bytes()for q in p.history_store.folder.iterdir()},'reading_and_reload_never_rewrite_archived_bytes')
        w.player_validation_target=popup
    finally:w.run.state=before

with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'not_game_samples':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
