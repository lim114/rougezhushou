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
    from rouge import current_battle_reference as m,expansion_reference as v,current_reward_origins as n
    from rouge import current_named_reward_origins as named
    providers=[m,v]
    for provider in providers:
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(['scripts/verify_common_content_window_352.py','scripts/verify_full_available.py','tests/test_common_content_352.py','verification/sections/352-preparation/scope.json'])
    names.update(row['file'] for row in json.loads((ROOT/'verification/sections/352-migration/manifest.json').read_bytes())['files'])
    names.add('verification/sections/352-migration/manifest.json')
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=120000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
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
        from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_battle_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge352-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第352节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('stages',activate=False);state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
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
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_common_control_value_available')
                        combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents()
                        require(combo.currentData()==value,'real_common_category_selection')
                    def select(widget,key):
                        item=next(widget.item(i)for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key)
                        widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents()
                        require(widget.currentItem()is not None and widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'real_mouse_selects_exact_common_entry')
                    require('版本与更新'not in[tabs.tabText(i)for i in range(tabs.count())],'no_separate_version_update_tab')
                    homes={'stages':'战斗预览','scenes':'节点事件','choices':'节点事件','regions':'节点事件','endings':'节点事件','relics':'藏品与零件','scrap':'藏品与零件','squads':'探索设置','difficulty':'探索设置','initial':'探索设置'}
                    def home(category):
                        nonlocal panel
                        panel=window.common_reference_panels[window.common_reference_categories[category]]
                        idx=tabs.indexOf(panel);require(idx>=0 and tabs.tabText(idx)==homes[category],'exact_category_has_ordinary_main_page')
                        QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents()
                        require(tabs.currentWidget()is panel and panel.isVisible(),'real_tab_mouse_navigation_to_common_page')
                        choose(panel.category,category);require(panel.scope.currentData()is False and panel.scope.isHidden(),'ordinary_page_defaults_full_catalog_not_change_list')
                        return panel
                    for category,label in model.version.CATEGORIES:
                        home(category);require(panel.entries.count()==len(model.version.rows(category,changes_only=False)),'all_ten_categories_complete_current_directory')
                        first=panel.entries.item(0).data(Qt.ItemDataRole.UserRole);select(panel.entries,first)
                        require(panel.result['row']['category']==category and panel.result['actual_reward']is None and not panel.result['mutations_applied'],'real_player_detail_identity_and_unknown_rewards')
                        observations.append({'category':category,'main_page':homes[category],'first_exact_id':first,'total':panel.entries.count()})
                        if category in('stages','scenes','relics','difficulty'):shot('home-'+category)
                    home('stages');select(panel.entries,'ro6_b_7');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.current_battle_dialog
                    require(dialog.isVisible()and dialog.panel.stage_id=='ro6_b_7','ordinary_battle_page_exact_current_map_enemies_and_rewards_entry');child=dialog;panel=dialog.panel;shot('battle-child')
                    home('scenes');require(not child.isVisible(),'actual_mouse_page_change_closes_other_owned_child_tree');select(panel.entries,'scene_ro6_startbuff_enter');QTest.mouseClick(panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.flow_dialog;require(dialog.isVisible()and dialog.panel.scene_id=='scene_ro6_startbuff_enter','ordinary_event_page_exact_startup_flow')
                    home('relics');panel.search.setText('谒日之祈');select(panel.entries,'rogue_6_relic_final_7');QTest.mouseClick(panel.origins_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.origins_dialog;require(dialog.isVisible(),'ordinary_item_page_exact_acquisition_reader');child=dialog
                    item_page=panel
                    home('difficulty');require(not child.isVisible(),'real_setup_tab_mouse_change_closes_item_reader');select(panel.entries,'NORMAL|16')
                    home('relics');require(panel is item_page and panel.search.text()=='谒日之祈'and panel.result['row']['id']=='rogue_6_relic_final_7','each_common_page_keeps_its_own_search_selection_and_reading')
                    main_panel=panel
                    from rouge.expansion_view import ExpansionUpdatePanel
                    compact=QDialog(window);compact.setWindowTitle('第352节 · 常用页面紧凑阅读验收');compact.resize(900,430)
                    compact_layout=QVBoxLayout(compact);panel=ExpansionUpdatePanel(categories=('relics','scrap'),full_catalog=True);compact_layout.addWidget(panel);compact.show();gui.processEvents()
                    panel.search.setText('谒日之祈');select(panel.entries,'rogue_6_relic_final_7');shot('compact-common-reader')
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);scroll=reader.verticalScrollBar();require(scroll.maximum()>0,'actual_nonzero_reading_range');scroll.setValue(min(3,scroll.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex()
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.search.text()=='谒日之祈','two_common_readers_refresh_preserves_selection_scroll_tab_filter');refreshes.append({'before':prior,'after':reading(reader),'viewport':'actual compact ordinary reference widget','not_MainWindow_default_viewport':True})
                    compact.close();panel=main_panel;gui.processEvents()
                    version=model.version;damaged=temporary/'damaged';manifest=json.loads((version.ROOT/version.MANIFEST).read_bytes())
                    for name in(version.MANIFEST,*manifest['files']):
                        path=damaged/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((version.ROOT/name).read_bytes())
                    path=damaged/version.PACK/'current-topic.json';raw=path.read_bytes()
                    with patch.object(version,'ROOT',damaged):
                        path.write_bytes(raw+b'x')
                        for page in window.common_reference_panels.values():require(not page.refresh_reference()and page.result is None and page.entries.count()==0 and page.technical.toPlainText()=='','actual_corrupted_source_clears_all_four_common_pages')
                        shot('all-source-loss');path.write_bytes(raw)
                        for page in window.common_reference_panels.values():require(page.refresh_reference()and page.result is None and page.entries.currentItem()is None,'all_common_pages_recover_without_auto_selection')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero')
                    home('stages');select(panel.entries,'ro6_b_7');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.current_battle_dialog
                    native();window.close();gui.processEvents();require(not dialog.isVisible(),'actual_MainWindow_closes_all_common_owned_trees')
                    done=True;gui.exit(0)
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
    after=bound_files();result={'section':352,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
