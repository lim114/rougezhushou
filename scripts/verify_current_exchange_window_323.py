"""Actual native MainWindow update-reader exercise with temporary empty state."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-exchange-323'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-exchange-323/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_exchange_reference_323.py','scripts/verify_current_exchange_window_323.py','scripts/verify_full_available.py','tests/test_current_exchange_reference_323.py','tests/test_current_exchange_view_323.py'])
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=60000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')};failure=None;window=None;gui=None;exitcode=None;done=False
    def require(value,name):
        if not value:raise AssertionError(name)
        if name not in checks:checks.append(name)
    def forbidden(name):
        def fail(*a,**kw):calls[name]+=1;raise AssertionError('Forbidden real operation: '+name)
        return fail
    try:
        if sys.platform!='win32':raise RuntimeError('Actual Windows required')
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_exchange_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge323-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第323节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.expansion_update;state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native()})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                dialog=None
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is panel,'actual_MainWindow_update_tab_opened')
                    main_panel=panel
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_control_value_available');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'direct_exact_selection_no_long_prefix_traversal')
                    def select(widget,key):
                        index=next(i for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);item=widget.item(index);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_mouse_selects_exact_item_or_document_group')
                    def entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.exchange_button.isVisible(),'real_update_entry_exposes_current_exchange');QTest.mouseClick(main_panel.exchange_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.exchange_dialog
                    dialog=entry('relics','rogue_6_relic_final_8');panel=dialog.panel
                    require(dialog.isVisible()and panel.items.count()==284 and panel.item_id=='rogue_6_relic_final_8','actual_current_catalogue284_not395_effects_or272_legacy');require('不可交出'in panel.item_player.toPlainText()and '不能说明能否换到'in panel.item_player.toPlainText(),'new_covenant_cannot_be_offered_not_reward_pool');shot('new-covenant-cannot-offer')
                    choose(panel.offer,False);choose(panel.change,'added');require(panel.items.count()==4 and panel.item_id=='rogue_6_relic_final_8','four_new_nonoffer_items_and_existing_selection_retained');observations.append({'filtered_new_cannot_offer':panel.items.count(),'selected':panel.item_id})
                    choose(panel.offer,True);require(panel.items.count()==8 and panel.item_id is None and panel.item_technical.toPlainText()==''and '祭日之契'not in panel.item_player.toPlainText(),'opposite_filter_clears_hidden_prior_item');select(panel.items,'rogue_6_relic_cargo_15');require('可以交出'in panel.item_player.toPlainText(),'new_cargo_exact_offer_flag');shot('new-offerable-items')
                    panel.search.setText('不存在的测试名称');gui.processEvents();require(panel.items.count()==0 and panel.item_id is None,'empty_search_clears_old_item');panel.search.clear();choose(panel.rarity,'RARE');require(all(row['rarity']=='RARE'for row in model.catalogue_rows(panel.result,can_offer=True,change='added',rarity='RARE'))and panel.items.count()==len(model.catalogue_rows(panel.result,can_offer=True,change='added',rarity='RARE')),'independent_rarity_offer_update_filters_intersect');choose(panel.rarity,None);choose(panel.offer,False);select(panel.items,'rogue_6_relic_final_8')
                    panel.tabs.setCurrentIndex(1);gui.processEvents();require(panel.groups.count()==9 and sum(len(r['document_cells'])for r in panel.result['data']['document_groups'])==13 and len(panel.result['data']['original_choices'])==43,'all_nine_caption_groups_thirteen_cells_and43_candidates_preserved')
                    for row in panel.result['data']['document_groups']:
                        select(panel.groups,row['id']);require(panel.group_id==row['id']and row['title']in panel.doc_player.toPlainText(),'all_nine_groups_display_exact_chinese_caption');observations.append({'document_group':row['id'],'title':row['title'],'text':panel.doc_player.toPlainText(),'primary_candidates':row['primary_candidate_ids'],'reward_quantity_reference':row['explicit_reward_quantity'],'consumption_reference':row['consumption_reference']})
                    select(panel.groups,'3');require('1件零件'in panel.doc_player.toPlainText()and len(panel.result['data']['document_groups'][3]['primary_candidate_ids'])==16,'scrap_quantity_one_with_all_sixteen_candidates_not_sixteen_grants');shot('one-part-multiple-candidates')
                    select(panel.groups,'4');require('随机2件自然物'in panel.doc_player.toPlainText()and '不是任意2件零件'in panel.doc_player.toPlainText(),'two_random_natural_objects_not_all_part_types');shot('two-natural-object-cost')
                    select(panel.groups,'5');require('焚毁'in panel.doc_player.toPlainText()and '不自动补成1件'in panel.doc_player.toPlainText(),'named_reward_no_invented_quantity');shot('named-reward-unknown-count')
                    dialog.resize(900,550);gui.processEvents();select(panel.groups,'3')
                    for outer,inner,reader in((0,panel.item_tabs,panel.item_player),(0,panel.item_tabs,panel.item_technical),(1,panel.doc_tabs,panel.doc_player),(1,panel.doc_tabs,panel.doc_technical)):
                        panel.tabs.setCurrentIndex(outer);inner.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(14,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'four_readers_naturally_scroll_nonzero');bar.setValue(min(4,bar.maximum()));prior=reading(reader);keys=(panel.item_id,panel.group_id,panel.offer.currentData(),panel.rarity.currentData(),panel.change.currentData(),panel.tabs.currentIndex(),inner.currentIndex());QTest.mouseClick(main_panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.item_id,panel.group_id,panel.offer.currentData(),panel.rarity.currentData(),panel.change.currentData(),panel.tabs.currentIndex(),inner.currentIndex()),'parent_refresh_preserves_both_pages_four_readers_filters_and_selections');refreshes.append({'before':prior,'after':reading(reader),'keys':keys})
                    dialog.resize(1050,810);panel.doc_tabs.setCurrentIndex(0);gui.processEvents();clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        f=clone/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'public_copy_valid_before_actual_damage');target.write_bytes(raw+b' ')
                        try:
                            QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.items.count()==panel.groups.count()==0 and panel.item_technical.toPlainText()==panel.doc_technical.toPlainText()=='','actual_file_damage_clears_both_item_and_document_sources');shot('source-loss-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.item_id is None and panel.group_id is None,'restored_source_does_not_auto_select_old_item_or_option')
                    dialog.close();panel=main_panel
                    for category,key in(('scenes','scene_ro6_sacrifice1_enter'),('choices','choice_ro6_sacrifice2_23')):
                        dialog=entry(category,key);panel=dialog.panel;target=model.target_entry(category,key);require(panel.tabs.currentIndex()==1 and panel.group_id==target['group_id'],'exact_scene_overview_or_primary_choice_group_entry_without_parent_guess');observations.append({'catalog_category':category,'catalog_key':key,'group':panel.group_id});dialog.close();panel=main_panel
                    old=entry('relics','rogue_6_relic_final_8');QTest.mouseClick(main_panel.exchange_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not old.isVisible(),'repeat_open_closes_old_exchange_dialog');dialog=main_panel.exchange_dialog;main_panel._unavailable();require(not dialog.isVisible(),'parent_source_loss_closes_owned_exchange_dialog')
                    dialog.close();panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();done=True;window.close();gui.processEvents();gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            QTimer.singleShot(250,exercise)
            QTimer.singleShot(args.visible_ms,lambda:gui.exit(2)if not done else None)
            exitcode=gui.exec()
            require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    after=bound_files();result={'section':323,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
