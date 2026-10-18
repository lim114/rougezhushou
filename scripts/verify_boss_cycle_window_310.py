"""Actual native Windows manual boss reader; only root runs after promotion."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os,sys,tempfile,traceback
from pathlib import Path
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_boss_cycle_window_310.py'
MANIFEST='research/p3-boss-cycle-310/source-manifest.json'
PACK='research/p3-boss-cycle-310'
DATA='rouge/data/boss-cycle-reference.json'
KEYS=(('ro6_b_5','enemy_2147_shophm',0),('ro6_b_5','enemy_2148_shorbb',0))
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bound_files():
    names={CANONICAL,MANIFEST,DATA,'rouge/boss_cycle_reference.py','rouge/boss_cycle_view.py',
        'rouge/battle_view.py','rouge/battle_preview.py','rouge/enemy_skills.py','rouge/view_catalog.py','rouge/ui_state.py',
        'rouge/branch_choice.py','rouge/enemy_form_reference.py','rouge/enemy_form_view.py',
        'rouge/boss_phase_reference.py','rouge/boss_phase_view.py','rouge/app.py',
        'rouge/capture.py','rouge/desktop_backend.py','rouge/chat.py','rouge/credentials.py',
        'rouge/data/battle-previews.json','rouge/data/view-catalog.json','rouge/data/enemy-skill-references.json',
        'scripts/build_boss_cycle_reference_310.py','tests/test_boss_cycle_reference_310.py',
        'tests/test_boss_cycle_view_310.py','tests/test_boss_cycle_integration_310.py'}
    manifest=read(ROOT/MANIFEST);names.update(manifest['runtime_files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACK).rglob('*')if p.is_file())
    catalog=read(ROOT/'rouge/data/view-catalog.json')
    for identity in KEYS:
        portrait=catalog['enemies'][identity[1]].get('portrait')
        if portrait is not None:names.add('rouge/data/'+catalog['images'][portrait]['file'])
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages']
    names.update('rouge/data/'+stages[sid]['image']['file']for sid in{identity[0]for identity in KEYS})
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular selected public source required: '+name)
        result[name]=sha(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',required=True,type=Path)
    parser.add_argument('--visible-ms',type=int,default=60000);args=parser.parse_args();destination=args.receipt.resolve()
    if destination.exists():raise FileExistsError('Preserve first actual receipt.')
    if args.visible_ms<15000:raise ValueError('At least15000ms required for staged actual reading.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();before={};after={};checks=[];calls=0
    readings=[];entry_overviews=[];images=[];windows=[];refreshes=[];negative=None;failure=None;done=False;closed=False;qt_exit=None;qpa=None;panel=None;gui=None
    attempts={k:0 for k in('game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    def require(value,label):
        nonlocal calls
        if not value:raise AssertionError(label)
        calls+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*a,**k):attempts[name]+=1;raise AssertionError('Forbidden external operation: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Actual Windows required.')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache candidate must not be executed.')
        before=bound_files()
        from rouge import app as app_module,boss_cycle_reference as model
        from rouge.battle_view import BattlePreviewPanel
        from rouge.battle_preview import battle_data
        from rouge.branch_choice import OVERVIEW
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui,win32process
        packets={identity:model.cycle_reference(*identity)for identity in KEYS}
        require(model.TARGETS==KEYS and all(packet is not None and packet['source_valid']is True for packet in packets.values()),
            'both_exact_source_defined_entries_valid_before_GUI')
        topics=[];topic_ids=[]
        gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','actual_native_windows_QPA')
        with tempfile.TemporaryDirectory(prefix='rouge-310-boss-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for key,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,key,value))
            stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
            for method,name in(('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')):stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
            for method,name in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            panel=BattlePreviewPanel();panel.setWindowTitle('第310节 · 首领交替激活与模块条件资料（公开隔离验收）');panel.resize(1280,900);panel.show()
            context_before=deepcopy(panel.context)
            entry_index=0;key=KEYS[0]
            def native(widget,kind):
                hwnd=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and pid==os.getpid()and not win32gui.IsIconic(hwnd),
                    'actual_visible_owned_HWND_and_fixture_PID')
                observation={'kind':kind,'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[widget.width(),widget.height()]}
                windows.append(observation);return observation
            def choose(combo,value):
                index=next((i for i in range(combo.count())if type(combo.itemData(i))is type(value)and combo.itemData(i)==value),-1)
                if index<0:raise AssertionError('Exact identity missing from actual combo: '+str(value))
                combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
                for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                require(type(combo.currentData())is type(value)and combo.currentData()==value,'real_combo_selects_exact_reference_identity')
            def select_target():
                if panel.current_stage!=key[0]:
                    panel.stage_choices.select_branch(OVERVIEW);choose(panel.stage_combo,key[0])
                panel.enemy_choices.select_branch(OVERVIEW);choose(panel.enemy_combo,(key[1],key[2]))
                require(panel._shown_enemy==key and panel.boss_cycle_button.isVisible()and panel.boss_cycle_button.isEnabled(),
                    'real_stage_and_enemy_combos_expose_only_exact_target_manual_entry')
            def reader(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'vertical':widget.verticalScrollBar().value()}
            def parent_state():
                return deepcopy({'stage':panel.current_stage,'wave':panel.wave_combo.currentData(),'enemy_branch':panel.enemy_choices.branch.currentData(),
                    'enemy':panel.enemy_combo.currentData(),'branches':panel.include_branches.isChecked(),'technical':panel.technical.isChecked(),
                    'row':panel.grid.selected,'tile':panel._tile_cell,'original_row':panel.original.selected,'original_cell':panel.original.reference_cell,
                    'context':panel.context,'spawn_text':panel.spawn_detail.toPlainText(),'enemy_text':panel.enemy_detail.toPlainText(),
                    'spawn_reading':reader(panel.spawn_detail),'enemy_reading':reader(panel.enemy_detail)})
            def screenshot(name,widget):
                path=destination.with_name('window-'+name+'.png')
                if path.exists():raise FileExistsError('Preserve first screenshot.')
                widget.repaint();gui.processEvents();require(widget.grab().save(str(path),'PNG'),'actual_widget_PNG_saved')
                images.append({'name':name,'path':str(path),'sha256':sha(path),'direct_player_text':True,'native_window':native(widget,name)})
            def close_all():
                nonlocal closed
                if panel.boss_cycle_window is not None:panel.boss_cycle_window.close()
                panel.close();gui.processEvents();closed=not panel.isVisible()and(panel.boss_cycle_window is None or not panel.boss_cycle_window.isVisible())
            def fail(error):
                nonlocal failure
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                close_all();gui.exit(1)
            def later(function,delay=200):
                def guarded():
                    try:function()
                    except BaseException as error:fail(error)
                QTimer.singleShot(delay,guarded)
            def begin():
                nonlocal key,topics,topic_ids
                key=KEYS[entry_index];prior=panel.boss_cycle_window
                native(panel,'battle-preview')
                if entry_index==0:require(panel.boss_cycle_window is None,'no_boss_reader_opened_automatically')
                select_target()
                if prior is not None:require(prior.identity is None and prior.topic.count()==0 and not prior.player.toPlainText(),
                    'switching_exact_entry_clears_prior_topic_before_manual_reopen')
                saved=parent_state();QTest.mouseClick(panel.boss_cycle_button,Qt.MouseButton.LeftButton);gui.processEvents()
                dialog=panel.boss_cycle_window;dialog.resize(980,660);gui.processEvents()
                require(dialog.identity==key and dialog.topic.currentData()is None and not dialog.isModal(),
                    'actual_manual_button_opens_exact_modeless_overview')
                require(parent_state()==saved,'manual_open_keeps_parent_filters_map_selection_and_reading')
                require(dialog.lorentz_picture.key[:2]==('enemy',KEYS[0][1])and dialog.cube_picture.key[:2]==('enemy',KEYS[1][1])
                    and all(picture.image.pixmap()is not None and not picture.image.pixmap().isNull()
                        for picture in(dialog.lorentz_picture,dialog.cube_picture)),
                    'both_exact_original_boss_portraits_loaded_without_module_or_current_mode_substitution')
                topics=dialog.result['reference']['topics'];topic_ids=[row['id']for row in topics]
                require(bool(topic_ids)and len(set(topic_ids))==len(topic_ids)and all(type(value)is str for value in topic_ids),
                    'topic_options_are_all_source_defined_ids_not_hardcoded_workflow_count')
                entry_overviews.append({'identity':list(key),'entry_name':dialog.result['reference']['entry_name'],
                    'topic_ids':list(topic_ids),'default_topic':dialog.topic.currentData(),
                    'lorentz_picture_subject':list(dialog.lorentz_picture.key[:2]),'cube_picture_subject':list(dialog.cube_picture.key[:2]),
                    'native_window':native(dialog,'entry-overview')})
                screenshot('entry-'+str(entry_index+1)+'-overview-player',dialog);state['parent']=saved;later(lambda:topic_case(0))
            state={}
            def topic_case(index):
                dialog=panel.boss_cycle_window;topic=topics[index];choose(dialog.topic,topic['id'])
                require(dialog.identity==key and dialog.result['reference']['enemy_id']==key[1]
                    and dialog.result['reference']['entry_name']in dialog.windowTitle()
                    and dialog.player.toPlainText()==model.reference_text(dialog.result,topic_id=topic['id'])
                    and all(raw not in dialog.player.toPlainText()for raw in('enemy_2147_','enemy_2148_','trap_324')),'manual_topic_has_exact_ordinary_player_text_not_raw_enemy_identity')
                technical=json.loads(dialog.technical.toPlainText())
                require(technical['selected_topic_id']==topic['id']and technical['result']==dialog.result,
                    'technical_page_retains_complete_source_and_exact_selected_topic')
                require(bool(model.ACTUAL_FIELDS)and all(dialog.result[field]is None for field in model.ACTUAL_FIELDS)
                    and all(dialog.result[flag]is False for flag in('current_server_verified','numerical_phase_model_added',
                        'run_state_updated','inventory_updated','modifiers_changed','maps_changed')),
                    'documentary_topic_selection_never_applies_actual_stats_damage_clock_inventory_or_map_effects')
                require(parent_state()==state['parent'],'topic_reading_keeps_parent_context_map_filters_and_reading')
                readings.append({'identity':list(key),'topic_id':topic['id'],'name':topic['name'],'native_window':native(dialog,'topic-reader')})
                if(entry_index==0 and index==0)or(entry_index==1 and index==len(topics)-1):
                    dialog.tabs.setCurrentWidget(dialog.player);cursor=dialog.player.document().find(topic['name'])
                    if not cursor.isNull():dialog.player.setTextCursor(cursor);dialog.player.ensureCursorVisible()
                    gui.processEvents();screenshot('entry-'+str(entry_index+1)+'-topic-'+str(index+1)+'-player',dialog)
                if index+1<len(topics):later(lambda:topic_case(index+1))
                else:later(check_refresh)
            def check_refresh():
                nonlocal entry_index
                dialog=panel.boss_cycle_window
                richest=max(topics,key=lambda row:len(model.reference_text(dialog.result,topic_id=row['id'])))['id']
                choose(dialog.topic,richest);dialog.resize(840,420);gui.processEvents();selected=dialog.topic.currentData()
                for widget in(dialog.player,dialog.technical):
                    dialog.tabs.setCurrentWidget(widget);gui.processEvents();cursor=widget.textCursor()
                    cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                    bar=widget.verticalScrollBar();require(bar.maximum()>0,'real_reader_content_has_nonzero_scroll_without_padding')
                    bar.setValue(min(17,bar.maximum()));saved=reader(widget);scope=dialog.scope_key
                    panel._refresh_boss_cycle();gui.processEvents()
                    require(dialog.tabs.currentWidget()is widget and dialog.topic.currentData()==selected and dialog.scope_key==scope and reader(widget)==saved,
                        'same_identity_source_and_topic_refresh_keeps_tab_selection_and_nonzero_scroll')
                    refreshes.append({'identity':list(key),'topic_id':selected,'tab':dialog.tabs.indexOf(widget),'before':saved,'after':reader(widget)})
                if entry_index+1<len(KEYS):
                    entry_index+=1;later(begin)
                else:later(check_negative)
            def check_negative():
                nonlocal negative
                dialog=panel.boss_cycle_window;clone=temporary/'public-source-clone';manifest=read(ROOT/MANIFEST);names=[MANIFEST,*manifest['runtime_files']]
                for name in names:
                    source=ROOT/name;dest=clone/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
                damaged_relative=PACK+'/selected-original-records.json'
                require(damaged_relative in names,'negative_fixture_damages_an_actual_runtime_authority_member')
                with patch.object(model,'ROOT',clone):
                    require(model.cycle_reference(*key)['source_valid']is True,'exact_complete_temporary_public_clone_is_valid_before_damage')
                    target=clone/damaged_relative;original=target.read_bytes();target.write_bytes(original+b' ')
                    try:
                        panel._refresh_boss_cycle();gui.processEvents()
                        require(not panel.boss_cycle_button.isEnabled()and dialog.identity is None and dialog.result is None
                            and dialog.topic.count()==0 and not dialog.topic.isEnabled()and not dialog.player.toPlainText()
                            and not dialog.technical.toPlainText()and dialog.lorentz_picture.key==(None,None,'')and dialog.cube_picture.key==(None,None,''),
                            'actual_bad_source_clears_readers_pictures_and_topic_and_disables_entry')
                        screenshot('source-unavailable-cleared',dialog)
                    finally:target.write_bytes(original)
                    panel._refresh_boss_cycle();gui.processEvents()
                    require(panel.boss_cycle_button.isEnabled()and dialog.identity is None and not dialog.player.toPlainText(),
                        'source_recovery_alone_cannot_restore_old_topic_or_refill_reader')
                    QTest.mouseClick(panel.boss_cycle_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    require(dialog.identity==key and dialog.topic.currentData()is None,'source_recovery_requires_actual_manual_overview_reopen')
                    negative={'exact_copied_public_files':names,'damaged_source':damaged_relative,'restored_exact_bytes':target.read_bytes()==original,'reopened_identity':list(dialog.identity)}
                other=next(e for e in battle_data()['stages'][key[0]]['enemies']if e['id']=='enemy_2149_shorsm'and e['level']==0)
                choose(panel.enemy_combo,(other['id'],other['level']))
                require(panel.boss_cycle_button.isHidden()and dialog.identity is None and not dialog.player.toPlainText()
                    and dialog.lorentz_picture.key==(None,None,'')and dialog.cube_picture.key==(None,None,''),'real_other_enemy_selection_hides_entry_and_clears_old_boss_content')
                require(panel.context==context_before and all(v==0 for v in attempts.values()),'parent_calculation_context_unchanged_and_eight_external_attempts_zero')
                require(all([r['topic_id']for r in readings if r['identity']==list(identity)]==[topic['id']for topic in packets[identity]['reference']['topics']]for identity in KEYS),
                    'both_exact_entries_manually_read_all_topics_without_changing_their_identity')
                later(finish)
            def finish():
                nonlocal done
                done=True;close_all();gui.exit(0)
            def timeout():
                if not done:fail(TimeoutError('Boss reader native fixture did not finish before its deadline.'))
            try:
                later(begin,350);QTimer.singleShot(args.visible_ms,timeout);qt_exit=gui.exec()
                require(qt_exit==0 and done and closed,'actual_Qt_success_and_all_owned_widgets_closed')
            finally:close_all()
        after=bound_files();require(before==after,'selected_public_sources_unchanged_through_actual_window_close')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if panel is not None:
            try:
                if panel.boss_cycle_window is not None:panel.boss_cycle_window.close()
                panel.close()
                if gui is not None:gui.processEvents()
                closed=not panel.isVisible()and(panel.boss_cycle_window is None or not panel.boss_cycle_window.isVisible())
            except BaseException as error:
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        if before and not after:
            try:after=bound_files()
            except BaseException:pass
    report={'section':310,'kind':'isolated_native_windows_boss_cycle_reader','passed':done and failure is None and qt_exit==0 and closed,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'qpa':qpa,
        'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':calls,'actual_entry_overviews':entry_overviews,'actual_topic_readings':readings,
        'same_identity_refresh_observations':refreshes,'source_negative_fixture':negative,'screenshots':images,'screenshot_count':len(images),
        'native_observations':windows,'source_sha256_before':before,'source_sha256_after':after,'selected_sources_not_all_transitive_dependencies':True,
        'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,'game_operated':False,'game_captures':0,'chat_sent':False,
        'actual_activation_cycle_module_stats_damage_time_or_server_verified':False,
        'actual_full_MainWindow_or_process_descendant_closure_claimed':False,
        'scope':'Actual BattlePreviewPanel two exact entries and manual modeless documentary workflow reader only. Both entries retain all cross-subject topics; topics do not establish actual events/modes/module effects. Exact temporary public clone source damage; no numerical application, run state, live boss state or game operation.'}
    with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
