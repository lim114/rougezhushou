"""Actual Windows panel-only manual disguise reader; root runs after promotion."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json,os,sys,tempfile,traceback
from pathlib import Path
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_enemy_form_window_306.py'
PACK='research/p3-enemy-form-306'
MANIFEST=PACK+'/source-manifest.json'
DATA='rouge/data/enemy-form-reference.json'

def sha(path):return sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def bound_files():
    names={CANONICAL,MANIFEST,DATA,'rouge/enemy_form_reference.py','rouge/enemy_form_view.py',
        'rouge/battle_view.py','rouge/battle_preview.py','rouge/view_catalog.py','rouge/ui_state.py',
        'rouge/branch_choice.py','rouge/app.py','rouge/capture.py','rouge/desktop_backend.py',
        'rouge/chat.py','rouge/credentials.py','rouge/map_projection.py','rouge/spawn_reference.py',
        'rouge/data/view-catalog.json','rouge/data/battle-map-projections.json',
        'rouge/data/fixed-landmark-references.json','rouge/data/stage-context-reference.json',
        'scripts/build_enemy_form_reference_306.py','tests/test_enemy_form_reference_306.py',
        'tests/test_enemy_form_view_306.py'}
    manifest=read(ROOT/MANIFEST);names.update(manifest['runtime_files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACK).iterdir()if p.is_file())
    catalog=read(ROOT/'rouge/data/view-catalog.json');rows=read(ROOT/DATA)['rows']
    for row in rows:
        for eid in(row['enemy_id'],row['disguise_enemy_reference']['id']):
            portrait=catalog['enemies'].get(eid,{}).get('portrait')
            if portrait is not None:names.add('rouge/data/'+catalog['images'][portrait]['file'])
    stages=read(ROOT/'rouge/data/battle-previews.json')['stages']
    for sid in{row['stage_id']for row in rows}:names.add('rouge/data/'+stages[sid]['image']['file'])
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT):raise ValueError('Missing regular selected source: '+name)
        result[name]=sha(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--visible-ms',type=int,default=60000)
    args=parser.parse_args();destination=args.receipt.resolve()
    if destination.exists():raise FileExistsError('Never overwrite an original actual receipt.')
    if args.visible_ms<15000:raise ValueError('Allow at least15000ms for actual staged reading.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();before={};after={};checks=[];calls=0
    readings=[];images=[];windows=[];refreshes=[];negative=None;failure=None
    done=False;closed=False;qt_exit=None;qpa=None;panel=None;gui=None
    attempts={k:0 for k in('game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    def require(condition,label):
        nonlocal calls
        if not condition:raise AssertionError(label)
        calls+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*a,**k):
            attempts[name]+=1;raise AssertionError('Forbidden external operation: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Actual native Windows required.')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Promote this canonical script before actual acceptance.')
        before=bound_files()
        from rouge import enemy_form_reference as model,app as app_module
        from rouge.battle_view import BattlePreviewPanel
        from rouge.branch_choice import OVERVIEW
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui,win32process
        packet=model.source_data()
        require(packet is not None and len(packet['rows'])==8,'documented_source_and_all_eight_exact_rows_valid')
        cases=[(r['stage_id'],r['enemy_id'],r['level'])for r in packet['rows']]
        require(len(set(cases))==8 and cases==[(s,e,0)for s in model.STAGES for e in model.ALIASES],'eight_tuple_identity_not_name_or_prefix_lookup')
        gui=QApplication([]);qpa=gui.platformName()
        require(qpa=='windows','actual_native_windows_QPA')
        with tempfile.TemporaryDirectory(prefix='rouge-306-native-public-')as temporary,ExitStack()as stack:
            temp=Path(temporary)
            for key,value in{'ROOT':temp,'SETTINGS':temp/'settings.json','OPERATOR_STATE':temp/'operators.json','RUN_STATE':temp/'run.json'}.items():stack.enter_context(patch.object(app_module,key,value))
            stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
            for method,name in(('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')):stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
            for method,name in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            panel=BattlePreviewPanel();panel.setWindowTitle('第306节 · 本性难移伪装与现身（公开隔离验收）');panel.resize(1280,900);panel.show()
            context_before=deepcopy(panel.context)
            def native(widget,kind):
                hwnd=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and pid==os.getpid()and not win32gui.IsIconic(hwnd),'actual_visible_owned_HWND_and_fixture_PID')
                item={'kind':kind,'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[widget.width(),widget.height()]}
                windows.append(item);return item
            def choose(combo,value):
                index=next((i for i in range(combo.count())if combo.itemData(i)==value),-1)
                if index<0:raise AssertionError('Exact tuple absent from actual combo: '+str(value))
                combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
                for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                if combo.currentData()!=value:raise AssertionError('Real combo did not select exact identity.')
            def select(key):
                sid,eid,level=key
                if panel.current_stage!=sid:
                    panel.stage_choices.select_branch(OVERVIEW);choose(panel.stage_combo,sid)
                panel.enemy_choices.select_branch(OVERVIEW);choose(panel.enemy_combo,(eid,level));gui.processEvents()
                require(panel._shown_enemy==key and panel.enemy_form_button.isVisible()and panel.enemy_form_button.isEnabled(),'real_combos_select_exact_body_and_manual_entry')
            def screenshot(name,widget,player):
                path=destination.with_name('window-'+name+'.png')
                if path.exists():raise FileExistsError('Preserve actual screenshot.')
                widget.repaint();gui.processEvents()
                if not widget.grab().save(str(path)):raise RuntimeError('Actual screenshot save failed.')
                images.append({'name':name,'path':str(path),'sha256':sha(path),'direct_player_text':player,'native_window':native(widget,name)})
            def reader_state(widget):
                cursor=widget.textCursor()
                return{'anchor':cursor.anchor(),'position':cursor.position(),'selected_text':cursor.selectedText(),'vertical':widget.verticalScrollBar().value()}
            def fail(error):
                nonlocal failure
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                close_all()
                gui.exit(1)
            def later(function,delay=200):
                def guarded():
                    try:function()
                    except BaseException as error:fail(error)
                QTimer.singleShot(delay,guarded)
            def close_all():
                nonlocal closed
                if panel.enemy_form_window is not None:panel.enemy_form_window.close()
                panel.close();gui.processEvents()
                closed=not panel.isVisible()and(panel.enemy_form_window is None or not panel.enemy_form_window.isVisible())
            def inspect_case(index):
                key=cases[index];prior=panel.enemy_form_window
                select(key)
                if prior is not None:require(prior.identity is None and prior.result is None and prior.player.toPlainText()==''and prior.technical.toPlainText()==''
                    and prior.body_picture.key==(None,None,'')and prior.disguise_picture.key==(None,None,''),'changing_tuple_clears_previous_identity_readers_and_portraits')
                QTest.mouseClick(panel.enemy_form_button,Qt.MouseButton.LeftButton);gui.processEvents()
                dialog=panel.enemy_form_window;dialog.resize(980,660);gui.processEvents()
                row=dialog.result['reference'];target=row['disguise_enemy_reference'];text=dialog.player.toPlainText()
                require(dialog.identity==key and not dialog.isModal()and dialog.tabs.currentWidget()is dialog.player,'manual_button_opens_exact_modeless_player_reader')
                require(dialog.body_picture.key[:2]==('enemy',key[1])and dialog.disguise_picture.key[:2]==('enemy',target['id']),'body_and_disguise_picture_subjects_are_independent')
                pictures=[]
                for picture,eid in((dialog.body_picture,key[1]),(dialog.disguise_picture,target['id'])):
                    from rouge.view_catalog import portrait_record
                    record=portrait_record('enemy',eid);pixmap=picture.image.pixmap()
                    exists=record is not None
                    require((exists and pixmap is not None and not pixmap.isNull())or(not exists and picture.image.text()=='图片未取得'),'exact_available_portrait_or_explicit_missing_no_borrowed_image')
                    pictures.append({'enemy_id':eid,'fixed_portrait_available':exists,'actual_pixmap_nonnull':pixmap is not None and not pixmap.isNull()})
                require(target['name']in text and all(a in text for a in target['abilities'])and'enemy_2133_'not in text
                    and'complete_original_reference'in dialog.technical.toPlainText(),'Chinese_player_explanation_and_complete_technical_source_separated')
                require(all(dialog.result[f]is None for f in model.ACTUAL_FIELDS)and not any(dialog.result[k]for k in('modifiers_changed','maps_changed','level_type_applied','run_state_updated','current_server_verified')),'documentary_reading_does_not_become_actual_game_or_calculation')
                readings.append({'identity':list(key),'declared_disguise_enemy_id':target['id'],'title':row['documented_variant_name'],'pictures':pictures,'native_window':native(dialog,'reader')})
                if index in(0,1,6):screenshot('player-'+str(index+1),dialog,True)
                if index==7:
                    dialog.tabs.setCurrentWidget(dialog.technical);gui.processEvents();screenshot('technical-complete-source',dialog,False)
                    later(check_refresh)
                else:later(lambda:inspect_case(index+1))
            def check_refresh():
                dialog=panel.enemy_form_window
                for widget in(dialog.player,dialog.technical):
                    dialog.tabs.setCurrentWidget(widget);gui.processEvents()
                    cursor=widget.textCursor();cursor.setPosition(4);cursor.setPosition(18,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                    bar=widget.verticalScrollBar();require(bar.maximum()>0,'real_content_has_nonzero_scroll_without_padding')
                    bar.setValue(min(19,bar.maximum()));prior=reader_state(widget);scope=dialog.scope_key
                    panel._refresh_enemy_form();gui.processEvents()
                    require(dialog.tabs.currentWidget()is widget and dialog.scope_key==scope and reader_state(widget)==prior,'same_identity_refresh_preserves_tab_nonempty_selection_and_nonzero_scroll')
                    refreshes.append({'tab':dialog.tabs.indexOf(widget),'before':prior,'after':reader_state(widget),'identity':list(dialog.identity)})
                later(check_negative)
            def check_negative():
                nonlocal negative
                dialog=panel.enemy_form_window;key=tuple(dialog.identity);clone=temp/'runtime-source-clone'
                manifest=read(ROOT/MANIFEST);names=[MANIFEST,*manifest['runtime_files']]
                for name in names:
                    source=ROOT/name;dest=clone/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
                with patch.object(model,'ROOT',clone):
                    require(model.disguise_reference(*key)['source_valid']is True,'six_runtime_members_plus_manifest_real_warm_clone_valid')
                    damaged=clone/model.AUTHORITY;original=damaged.read_bytes();damaged.write_bytes(original+b' ')
                    try:
                        panel._refresh_enemy_form();gui.processEvents()
                        require(not panel.enemy_form_button.isEnabled()and dialog.identity is None and dialog.result is None
                            and not dialog.player.toPlainText()and not dialog.technical.toPlainText()
                            and dialog.body_picture.key==(None,None,'')and dialog.disguise_picture.key==(None,None,''),'real_bad_source_clears_readers_portraits_and_disables_entry')
                        screenshot('source-unavailable-cleared',dialog,True)
                    finally:damaged.write_bytes(original)
                    panel._refresh_enemy_form();gui.processEvents()
                    require(panel.enemy_form_button.isEnabled()and dialog.identity is None and not dialog.technical.toPlainText(),'source_recovery_enables_entry_but_does_not_restore_old_choice')
                    QTest.mouseClick(panel.enemy_form_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    require(dialog.identity==key and dialog.tabs.currentWidget()is dialog.player,'source_recovery_requires_actual_manual_reopen')
                    negative={'copied_exact_public_files':names,'damaged_source':model.AUTHORITY,'restored_exact_bytes':damaged.read_bytes()==original,'actual_identity_after_manual_reopen':list(dialog.identity)}
                ordinary=dialog.result['reference']['declared_summon_enemy_key']
                choose(panel.enemy_combo,(ordinary,0));gui.processEvents()
                require(panel.enemy_form_button.isHidden()and dialog.identity is None and not dialog.player.toPlainText(),'non_target_enemy_hides_entry_and_clears_old_reader')
                require(panel.context==context_before and all(v==0 for v in attempts.values()),'parent_context_unchanged_and_all_eight_external_attempts_zero')
                require(len(readings)==8 and len({tuple(x['identity'])for x in readings})==8,'all_eight_distinct_documented_tuple_readings_completed')
                later(finish)
            def finish():
                nonlocal done
                done=True;close_all();gui.exit(0)
            def timeout():
                if not done:fail(TimeoutError('Native fixture did not finish before its explicit deadline.'))
            try:
                native(panel,'battle-preview');require(panel.enemy_form_window is None,'no_reader_opened_automatically')
                later(lambda:inspect_case(0),350);QTimer.singleShot(args.visible_ms,timeout)
                qt_exit=gui.exec()
                require(qt_exit==0 and done and closed,'actual_Qt_event_loop_success_and_all_owned_windows_closed')
            finally:close_all()
        after=bound_files();require(before==after,'selected_public_sources_unchanged_through_window_close')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if panel is not None:
            try:
                if panel.enemy_form_window is not None:panel.enemy_form_window.close()
                panel.close()
                if gui is not None:gui.processEvents()
                closed=not panel.isVisible()and(panel.enemy_form_window is None or not panel.enemy_form_window.isVisible())
            except BaseException as error:
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        if before and not after:
            try:after=bound_files()
            except BaseException:pass
    report={'section':306,'kind':'isolated_native_windows_enemy_form_panel','passed':done and failure is None and qt_exit==0 and closed,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'qpa':qpa,'process_id':os.getpid(),
        'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':calls,'actual_tuple_readings':readings,
        'same_identity_refresh_observations':refreshes,'source_negative_fixture':negative,'screenshots':images,'screenshot_count':len(images),
        'native_observations':windows,'source_sha256_before':before,'source_sha256_after':after,
        'selected_sources_not_a_claim_of_all_transitive_dependencies':True,
        'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,'game_operated':False,'game_captures':0,'chat_sent':False,
        'actual_full_MainWindow_or_game_or_process_descendant_closure_claimed':False,
        'scope':'Actual BattlePreviewPanel combo/manual-button reading only; source damage is an exact temporary public clone. No actual disguise/reveal/position/level/effect or current-server verification.'}
    with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(main())
