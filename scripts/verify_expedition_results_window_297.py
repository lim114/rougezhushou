"""Cache-only candidate: manual expedition results in an actual isolated MainWindow.

Root reviews/promotes/binds final source bytes and supervises the only real run.
No claim about actual dispatch, return, eligibility, rewards or current server.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import sys,tempfile,traceback
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_expedition_results_window_297.py'
PACKET='research/p3-expedition-results-297'
MANIFEST=PACKET+'/source-manifest.json'
DATA='rouge/data/expedition-results.json'
MANIFEST_SHA='5227f6fc7171430dc820668daf636489c72673d62a5f1e9b82d26d0021cf323e'
DATA_SHA='f83ca0ec16a24e634e48500186da6f6f7f3269092d51045d99779f1a9439d3ff'
EVENT='community_group_024';SCENE=EVENT+':scene:0';OTHER='community_group_021'
CHOICES=tuple(SCENE+':choice:'+str(i)for i in range(3))
REFS=tuple(c+':expedition-result'for c in CHOICES)
ITEM='rogue_6_relic_final_3'
SIZE=(1050,720);DIALOG_SIZE=(900,680)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def text_sha(value):return hashlib.sha256(value.encode('utf8')).hexdigest()


def bound_files():
    names={CANONICAL,'rouge/app.py','rouge/node_catalog_view.py','rouge/player_node_information.py',
        'rouge/node_catalog.py','rouge/event_planning.py','rouge/ui_state.py','rouge/branch_choice.py',
        'rouge/expedition_results.py','rouge/expedition_results_view.py',DATA,MANIFEST,
        'rouge/node_rewards.py','rouge/data/node-reward-reference.json',
        'rouge/event_named_reward_links.py','rouge/data/event-planning-reference.json',
        'scripts/build_expedition_results_297.py','tests/test_expedition_results_297.py'}
    manifest=read(ROOT/MANIFEST);names.update(manifest['files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
    # Root publishes the change-specific UI/integration tests before source freeze.
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tests').glob('test_expedition*297.py'))
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Selected source must be a regular public project file: '+name)
        result[name]=sha(path)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',required=True);parser.add_argument('--visible-ms',type=int,default=120000)
    args=parser.parse_args();destination=Path(args.receipt).resolve()
    if destination.exists():raise FileExistsError('Preserve first actual receipt.')
    if args.visible_ms<=0:raise ValueError('Positive visible interval required.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();before={};after={};checks=[];images=[];handles=[]
    rows=[];negative_rows=[];refresh_rows=[];executions=0;failure=None;done=False;closed=False;qpa=None;qt_exit=None
    attempts={name:0 for name in('game_enumeration','game_connect','game_capture','game_next_frame',
        'desktop_start','desktop_request','provider_chat','credential_read')}
    def require(value,label):
        nonlocal executions
        if not value:raise AssertionError(label)
        executions+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*_,**__):
            attempts[name]+=1;raise AssertionError('Forbidden original external entry: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Actual native Windows required.')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache draft is not executable acceptance.')
        require(sha(ROOT/MANIFEST)==MANIFEST_SHA and sha(ROOT/DATA)==DATA_SHA,
            'fixed_accepted_expedition_source_and_data_bytes_before_window')
        from rouge import expedition_results as results
        packet=results.event_reference(EVENT)
        require(packet is not None and packet['status']=='documented_reference'
            and packet['source_valid']is True,'actual_source_packet_valid_before_Qt_or_window')
        before=bound_files()
        from PySide6.QtCore import Qt,QPoint,QRect,QTimer
        from PySide6.QtGui import QTextCursor,QPixmap
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui,win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','native_windows_QPA')
        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):self.windows.clear()
        with tempfile.TemporaryDirectory(prefix='rouge-297-expedition-window-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for key,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json',
                'OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
                stack.enter_context(patch.object(app_module,key,value))
            stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
            for method,name in[('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
            for method,name in[('start','desktop_start'),('request','desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=PublicWindow();dialog=None
            try:
                window.setWindowTitle('第297节 · 派出与归来资料（公开隔离验收）')
                window.resize(*SIZE);window.show();panel=window.node_catalog;tabs=window.centralWidget()
                initial_run=deepcopy(window.run.state);typed_before=deepcopy(catalog.event_reward_options(EVENT))
                other_typed_before=deepcopy(catalog.event_reward_options(OTHER))
                parent_saved=None;dialog_saved=None;refresh_index=0;source_reads=[]
                def isolated():
                    require(not window.auto.isChecked()and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
                    require(window.capture.target is None and window.desktop.process is None,'capture_and_desktop_backend_inactive')
                    require(all(value==0 for value in attempts.values()),'all_eight_external_original_entry_attempts_zero')
                def native(widget,kind):
                    hwnd=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
                    require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and widget.isVisible(),kind+'_actual_owned_native_HWND_visible')
                    require(pid==os.getpid()and not win32gui.IsIconic(hwnd),kind+'_HWND_owned_by_actual_fixture_not_minimized')
                    require([widget.width(),widget.height()]==list(SIZE if kind=='parent'else DIALOG_SIZE),
                        kind+'_actual_client_size_exact')
                    return{'kind':kind,'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,
                        'client_size':[widget.width(),widget.height()]}
                def choose(control,value):
                    index=control.findData(value);require(index>=0,'exact_full_reference_control_value_present');control.setCurrentIndex(index)
                def event(identity):
                    panel.show_directory();choose(panel.kind,'event');choose(panel.floor,None);choose(panel.node_type,None)
                    panel.search.setText(catalog._event(identity)['title'])
                    index=next(i for i,e in enumerate(panel.entries)if e['kind']=='event'and e['record']['id']==identity)
                    panel.list.setCurrentRow(index);tabs.setCurrentWidget(panel)
                    require(panel.entries[index]['record']['id']==identity,'exact_public_directory_event_identity_selected')
                def reader(widget):
                    cursor=widget.textCursor()
                    return{'text_sha256':text_sha(widget.toPlainText()),'anchor':cursor.anchor(),'position':cursor.position(),
                        'selected':cursor.selectedText(),'vertical':widget.verticalScrollBar().value(),
                        'horizontal':widget.horizontalScrollBar().value()}
                def parent_state():
                    return{'key':panel.list.selected_key(),'tab':panel.reading_tabs.currentIndex(),
                        'scene':panel.event_scene_filter.currentData(),'choice':panel.event_choice_filter.currentData(),
                        'stage':panel.event_stage.currentData(),'search':panel.search.text(),
                        'search_cursor':panel.search.cursorPosition(),'search_selection':panel.search.selectedText(),
                        'player':reader(panel.player_detail),'source':reader(panel.detail)}
                def empty_icon():
                    pixmap=dialog.icon.pixmap()
                    return not dialog.icon.isVisible()and(pixmap is None or pixmap.isNull())
                def dialog_state():
                    pixmap=dialog.icon.pixmap()
                    return{'event':dialog.event_id,'scope':deepcopy(dialog.scope_key),'choice':dialog.choice.currentData(),
                        'tab':dialog.reading_tabs.currentIndex(),'details_identity':deepcopy(dialog._details_identity),
                        'icon_visible':dialog.icon.isVisible(),
                        'icon_size':None if pixmap is None or pixmap.isNull()else[pixmap.width(),pixmap.height()],
                        'result':reader(dialog.result_text),'item':reader(dialog.item_text),'source':reader(dialog.source_text)}
                def click(button,owner,label):
                    gui.processEvents();rect=QRect(button.mapTo(owner,QPoint(0,0)),button.size())
                    require(button.isVisible()and button.isEnabled()and not button.visibleRegion().isEmpty()
                        and owner.rect().contains(rect),label+'_visible_enabled_inside_actual_client')
                    QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=button.rect().center())
                def select_text(widget,need_scroll=False):
                    gui.processEvents();require(widget.document().characterCount()>17,'real_existing_reader_text_available')
                    cursor=widget.textCursor();cursor.setPosition(5);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                    if need_scroll:
                        bar=widget.verticalScrollBar();require(bar.maximum()>0,'real_existing_reader_has_nonzero_scroll_range')
                        bar.setValue(max(1,bar.maximum()//2));require(bar.value()>0,'actual_reader_nonzero_scroll_set')
                    require(bool(widget.textCursor().selectedText()),'actual_reader_nonempty_text_selection')
                def screenshot(name,widget,kind):
                    isolated();handle=native(widget,kind);path=destination.with_name(destination.stem+'-'+name+'.png')
                    if path.exists():raise FileExistsError('First actual screenshot must not be overwritten.')
                    pixels=widget.grab();require(not pixels.isNull()and pixels.save(str(path),'PNG'),'actual_owned_native_PNG_saved')
                    images.append({'name':name,'path':str(path),'sha256':sha(path),'native_window':handle})
                def close_owned():
                    if dialog is not None:dialog.close()
                    window.close()
                def fail(error):
                    nonlocal failure,done
                    if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    done=False;close_owned();gui.exit(1)
                def later(callback,delay=200):
                    def guarded():
                        try:isolated();callback()
                        except BaseException as error:fail(error)
                    QTimer.singleShot(delay,guarded)
                def actual_unknown(row):
                    return all(row[k]is None for k in('actual_dispatched_operator','actual_returned','actual_reward',
                        'actual_quantity','actual_advanced','actual_return_clock','actual_selectable'))
                def begin():
                    nonlocal parent_saved
                    event(EVENT);panel.reading_tabs.setCurrentWidget(panel.detail);select_text(panel.detail,True)
                    panel.search.setSelection(0,2);parent_saved=parent_state()
                    require(panel.expedition_window is None,'expedition_dialog_not_precreated_before_manual_main_entry')
                    require(panel.expedition_button.isVisible()and panel.expedition_button.isEnabled(),'only_exact_tree_event_has_source_valid_manual_entry')
                    screenshot('parent-entry',window,'parent');click(panel.expedition_button,window,'actual_MainWindow_expedition_entry_QTest_click')
                    later(opened)
                def opened():
                    nonlocal dialog
                    dialog=panel.expedition_window
                    require(dialog is not None and dialog.parent()is panel,'actual_main_entry_constructs_and_retains_owned_modeless_dialog')
                    dialog.resize(*DIALOG_SIZE);gui.processEvents();handles.extend([native(window,'parent'),native(dialog,'dialog')])
                    require(handles[-2]['hwnd']!=handles[-1]['hwnd'],'parent_and_dialog_have_distinct_owned_HWNDs')
                    require(dialog.event_id==EVENT and dialog.scope_key==panel.list.selected_key(),'dialog_exact_event_and_actual_parent_scope')
                    require(dialog.choice.count()==3 and{dialog.choice.itemData(i)for i in range(3)}==set(REFS)
                        and dialog.choice.currentIndex()==-1 and dialog.choice.currentData()is None
                        and dialog._details_identity is None and empty_icon()and not dialog.open_item_button.isVisible(),
                        'default_three_choices_unselected_no_icon_no_manual_item_open')
                    require(parent_state()==parent_saved,'opening_dialog_preserves_actual_parent_reading')
                    source_reads.extend(packet['source_reference']['original_choice_ids'])
                    require(source_reads==['choice_ro6_scout_1','choice_ro6_scout_3','choice_ro6_scout_2','choice_ro6_scout_4'],
                        'four_exact_original_choice_identities_kept_separate')
                    annotation=packet['return_explanatory_reference']
                    require(annotation['choice_key']==EVENT+':scene:2:choice:1'and annotation['game_choice_ids']==[]
                        and annotation['is_actual_button']is False and annotation['effect_phase']=='on_return',
                        'return_explanation_remains_note_not_a_fourth_actual_choice')
                    choose(dialog.choice,REFS[2]);later(rest)
                def rest():
                    row=results.choice_reference(EVENT,SCENE,CHOICES[2]);text=dialog.result_text.toPlainText()
                    require(row['original_choice_id']=='choice_ro6_scout_2'and row['effect_phase_reference']=='on_choice'
                        and row['immediate_resource_references']==[{'resource':'hope','quantity_reference':2}]
                        and row['return_resource_references']==[]and row['dispatch_reference']is None
                        and row['documented_return_item']is None and actual_unknown(row),'rest_two_hope_is_immediate_reference_not_dispatch_or_actual_grant')
                    require('休息'in text and'2希望'in text and any(word in text for word in('当场','即时','选择时'))
                        and not dialog.open_item_button.isVisible()and empty_icon(),'actual_player_rest_reader_explains_immediate_two_hope_without_beacon_control')
                    require(not any(word in text for word in('rogue_6_','community_group_','https://')),'default_result_text_has_no_raw_ids_or_URLs')
                    rows.append({'choice_key':CHOICES[2],'reference_id':REFS[2],'effect_phase_reference':'on_choice',
                        'hope_reference':2,'actual_reward':None,'actual_quantity':None})
                    screenshot('rest-immediate',dialog,'dialog');choose(dialog.choice,REFS[0]);later(normal)
                def normal():
                    row=results.choice_reference(EVENT,SCENE,CHOICES[0]);text=dialog.result_text.toPlainText()
                    require(row['original_choice_id']=='choice_ro6_scout_1'and row['effect_phase_reference']=='on_return'and row['immediate_resource_references']==[]
                        and row['return_resource_references']==[]and row['documented_return_item']is None
                        and row['dispatch_reference']['operator_count_reference']==1
                        and row['dispatch_reference']['temporarily_unavailable_for_squad']is True
                        and row['promotion_reference']is None and row['complete_return_rewards_known']is False
                        and actual_unknown(row),'ordinary_dispatch_never_borrows_root_reward_or_guaranteed_promotion')
                    require('内部'in text and'归来'in text and any(word in text for word in('未知','尚未确认','未核验'))
                        and not dialog.open_item_button.isVisible()and empty_icon(),'actual_ordinary_dispatch_reader_keeps_loot_and_promotion_unknown')
                    rows.append({'choice_key':CHOICES[0],'reference_id':REFS[0],'effect_phase_reference':'on_return',
                        'hope_reference':None,'promotion_reference':None,'actual_reward':None})
                    choose(dialog.choice,REFS[1]);later(root_reference)
                def root_reference():
                    row=results.choice_reference(EVENT,SCENE,CHOICES[1]);text=dialog.result_text.toPlainText()
                    require(row['original_choice_id']=='choice_ro6_scout_3'and row['effect_phase_reference']=='on_return'and row['immediate_resource_references']==[]
                        and row['return_resource_references']==[{'resource':'hope','quantity_reference':2}]
                        and row['dispatch_reference']['operator_count_reference']==1
                        and row['dispatch_reference']['temporarily_unavailable_for_squad']is True
                        and row['documented_return_item']['item_id']==ITEM
                        and row['documented_return_item']['quantity_reference']is None
                        and row['promotion_reference']is False and row['beak_reference']['applies_to_root_branch']is None
                        and actual_unknown(row),'root_two_hope_beacon_and_no_advance_are_return_references_not_current_inventory')
                    require(all(word in text for word in('源头','归来','2希望','怦然信标','进阶','喙'))
                        and dialog.open_item_button.isVisible()and dialog.open_item_button.isEnabled()
                        and dialog._details_identity is None and empty_icon(),'root_reader_explains_return_and_keeps_beak_relation_unknown_without_auto_item')
                    rows.append({'choice_key':CHOICES[1],'reference_id':REFS[1],'effect_phase_reference':'on_return',
                        'hope_reference':2,'quantity_reference':None,'promotion_reference':False,
                        'beak_applies_to_root_branch':None,'actual_reward':None})
                    click(dialog.open_item_button,dialog,'actual_source_return_item_QTest_click');later(item_opened)
                def item_opened():
                    details=results.item_details(EVENT,SCENE,CHOICES[1]);icon=details['icon_reference'];pixmap=dialog.icon.pixmap()
                    require(dialog._details_identity is not None and dialog.reading_tabs.currentWidget()is dialog.item_text
                        and dialog.icon.isVisible()and pixmap is not None and not pixmap.isNull(),'manual_item_button_loads_real_return_item_icon_and_reader')
                    require(details['item']['id']==icon['item_id']==icon['icon_id']==ITEM
                        and before[icon['file']]==icon['sha256'],'actual_icon_is_bound_to_exact_beacon_public_bytes')
                    expected=QPixmap(str(ROOT/icon['file'])).scaledToWidth(pixmap.width(),Qt.TransformationMode.SmoothTransformation)
                    require(not expected.isNull()and pixmap.toImage()==expected.toImage(),'actual_label_pixmap_equals_exact_fixed_source_icon')
                    require(all(word in dialog.item_text.toPlainText()for word in('怦然信标','用途','说明','解锁'))
                        and details['quantity_reference']is None and details['actual_reward']is None
                        and details['actual_quantity']is None and details['inventory_updated']is False
                        and details['eligibility_evaluated']is False,'manual_item_reader_has_chinese_details_without_quantity_or_inventory_upgrade')
                    screenshot('source-return-item',dialog,'dialog');later(refresh_prime)
                def refresh_prime():
                    nonlocal dialog_saved
                    select_text(dialog.result_text);select_text(dialog.item_text)
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text);select_text(dialog.source_text,True)
                    dialog_saved=dialog_state();later(refresh_once)
                def refresh_once():
                    nonlocal refresh_index
                    callbacks=(dialog.refresh_reference,panel.refresh,
                        lambda:dialog.set_reference(EVENT,scope_key=panel.list.selected_key()))
                    labels=('dialog_refresh','parent_refresh','same_scope_set_reference')
                    callbacks[refresh_index]();gui.processEvents()
                    require(dialog_state()==dialog_saved,'same_scope_refresh_preserves_choice_tab_icon_item_state_selection_and_nonzero_scroll')
                    require(parent_state()==parent_saved,'same_scope_refresh_preserves_parent_filters_selection_reading_and_scroll')
                    refresh_rows.append({'path':labels[refresh_index],'choice_reference':dialog.choice.currentData(),
                        'source_scroll':dialog.source_text.verticalScrollBar().value(),'manual_item_retained':dialog._details_identity is not None})
                    refresh_index+=1
                    if refresh_index<len(callbacks):later(refresh_once)
                    else:later(event_source_failure)
                def source_failure(kind):
                    manifest=read(ROOT/MANIFEST);clone=temporary/('source-negative-'+kind)
                    for name in set(manifest['files'])|{MANIFEST}:
                        original=ROOT/name
                        require(original.is_file()and not original.is_symlink()and original.resolve().is_relative_to(ROOT.resolve()),
                            'source_negative_fixture_copies_only_regular_public_members')
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
                    damaged_name=MANIFEST if kind=='event'else packet['icon_reference']['file'];target=clone/damaged_name;raw=target.read_bytes()
                    with patch.object(results,'ROOT',clone):
                        require(results.source_data()is not None and results.event_reference(EVENT)['status']=='documented_reference'
                            and results.item_details(EVENT,SCENE,CHOICES[1])['status']=='documented_reference',
                            'complete_public_clone_and_both_queries_valid_before_warm_source_damage')
                        try:
                            target.write_bytes(raw+b' ')
                            dialog.refresh_reference();panel.refresh();gui.processEvents()
                            require(dialog.packet is None and dialog._view_key is None
                                and dialog.choice.count()==0 and dialog.choice.currentIndex()==-1 and dialog.choice.currentData()is None
                                and dialog._details_identity is None and empty_icon()and not dialog.open_item_button.isVisible()
                                and not panel.expedition_button.isEnabled(),kind+'_warm_source_damage_clears_choice_icon_item_and_parent_entry')
                            require(all('已清除'in text.toPlainText()and'rogue_6_'not in text.toPlainText()
                                for text in(dialog.result_text,dialog.item_text,dialog.source_text)),
                                kind+'_source_failure_clears_all_three_old_reading_pages')
                            screenshot(kind+'-source-invalidated',dialog,'dialog')
                        finally:target.write_bytes(raw)
                        require(sha(target)==before[damaged_name],'damaged_public_clone_restored_from_exact_original_bytes')
                        dialog.refresh_reference();panel.refresh();gui.processEvents()
                        require(dialog.packet is not None and dialog._view_key is None
                            and dialog.choice.count()==3 and dialog.choice.currentIndex()==-1
                            and dialog._details_identity is None and empty_icon()and not dialog.open_item_button.isVisible(),
                            kind+'_source_restore_leaves_manual_choice_and_item_unselected')
                    negative_rows.append({'kind':kind,'manifest':MANIFEST,'damaged_member':damaged_name,'public_clone_only':True,
                        'restored_sha256':sha(target),'actual_reward':None})
                def event_source_failure():
                    source_failure('event');choose(dialog.choice,REFS[1])
                    click(dialog.open_item_button,dialog,'reopen_beacon_before_icon_source_negative_QTest_click')
                    later(item_source_failure)
                def item_source_failure():
                    require(dialog._details_identity is not None and not empty_icon(),'item_negative_starts_from_actual_warm_opened_icon')
                    source_failure('item');later(switch_choice_clear)
                def switch_choice_clear():
                    choose(dialog.choice,REFS[1]);click(dialog.open_item_button,dialog,'reopen_beacon_before_choice_change_QTest_click')
                    require(not empty_icon(),'manual_beacon_open_before_switching_choice')
                    choose(dialog.choice,REFS[0])
                    require(empty_icon()and dialog._details_identity is None and not dialog.open_item_button.isVisible(),
                        'switching_to_ordinary_dispatch_clears_prior_beacon_and_special_item_control')
                    event(OTHER);gui.processEvents()
                    require(not panel.expedition_button.isVisible()and not panel.expedition_button.isEnabled(),
                        'non_target_event_has_no_expedition_entry')
                    require(dialog.event_id is None and dialog.packet is None and dialog._view_key is None
                        and dialog.choice.currentIndex()==-1 and dialog.choice.currentData()is None
                        and dialog._details_identity is None and empty_icon()
                        and all('怦然信标'not in w.toPlainText()for w in(dialog.result_text,dialog.item_text,dialog.source_text)),
                        'scope_change_clears_old_result_item_source_and_icon')
                    panel.reading_tabs.setCurrentWidget(panel.detail);select_text(panel.detail,True);saved=parent_state()
                    dialog.refresh_reference();gui.processEvents()
                    require(parent_state()==saved,'out_of_scope_existing_node_reading_unchanged_by_child_refresh')
                    require(catalog.event_reward_options(EVENT)==typed_before and catalog.event_reward_options(OTHER)==other_typed_before,
                        'existing_typed_reward_queries_unchanged_during_manual_reference_reading')
                    require(window.run.state==initial_run,'manual_expedition_reading_never_changes_temporary_run_memory')
                    require(bound_files()==before,'selected_public_sources_stable_before_completion')
                    later(finish)
                def finish():
                    nonlocal done
                    require({r['choice_key']for r in rows}==set(CHOICES)and len(rows)==3,'all_three_exact_documented_choices_actually_read')
                    require({r['kind']for r in negative_rows}=={'event','item'},'both_distinct_warm_public_source_negatives_exercised')
                    handles.append(native(window,'parent'))
                    if dialog.isVisible():handles.append(native(dialog,'dialog'))
                    done=True
                def deadline():
                    nonlocal failure
                    if not done and failure is None:failure={'type':'TimeoutError','message':'Manual expedition entry/source/reading checks incomplete.'}
                    close_owned()
                later(begin,500);QTimer.singleShot(max(30000,args.visible_ms),deadline)
                qt_exit=gui.exec();closed=not window.isVisible()and(dialog is None or not dialog.isVisible())
                if qt_exit!=0 or not closed or not done:
                    if failure is None:failure={'type':'RuntimeError','message':'Actual checks/Qt/owned-window closure incomplete.'}
                if failure is None:isolated()
                after=bound_files()
                if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected sources changed before actual closure.'}
            finally:
                # Source/state/external-entry guards remain installed until closure.
                if dialog is not None:dialog.close()
                window.close();gui.processEvents();closed=not window.isVisible()and(dialog is None or not dialog.isVisible())
    except BaseException as error:
        failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    report={'section':297,'kind':'isolated_native_windows_expedition_choice_results','passed':done and failure is None,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),
        'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':executions,
        'requested_parent_client_size':list(SIZE),'requested_dialog_client_size':list(DIALOG_SIZE),
        'native_observations':handles,'screenshots':images,'screenshot_count':len(images),
        'choice_readings':rows,'source_negative_fixtures':negative_rows,'same_scope_refresh_observations':refresh_rows,
        'four_original_choice_ids':source_reads if'source_reads'in locals()else[],
        'source_sha256_before':before,'source_sha256_after':after,
        'source_guard_is_selected_not_all_transitive_dependencies':True,
        'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,
        'external_entrypoints_blocked_before_original_call':True,'game_operated':False,'game_captures':0,
        'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
        'original_project_window_operated_or_restarted':False,
        'actual_process_termination_verified_by_this_script':False,'owned_supervisor_exit_and_cleanup_required_separately':True,
        'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
        'scope':'Only three exact documented choices and return explanation in real MainWindow/modeless reader; immediate rest versus return phase, manual fixed beacon image, both warm source failures/recovery, same-scope reading retention and scope clear. No actual dispatch/return/reward/eligibility or current-server verification; no full rerun.'}
    with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1


if __name__=='__main__':raise SystemExit(main())
