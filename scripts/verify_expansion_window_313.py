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
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-expansion-313').rglob('*')if p.is_file()}
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
    names.update(['scripts/build_expansion_reference_313.py','scripts/verify_expansion_window_313.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
    images=json.loads((ROOT/'research/p3-expansion-313/map-images.json').read_bytes())['images'];names.update(v['file']for v in images.values())
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
        from rouge import app as app_module,expansion_reference as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge313-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第313节 · 国服更新资料（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.reference_panel('stages');state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native()})
            def category(key):
                nonlocal panel
                if tabs.indexOf(panel)>=0:
                    panel=window.reference_panel(key);gui.processEvents()
                    require(tabs.currentWidget()is panel and panel.isVisible()and panel.scope.currentData()is False and panel.scope.isHidden(),'actual_common_page_for_requested_category')
                combo=panel.category;index=combo.findData(key);require(index>=0,'category_value_exists')
                QTest.keyClick(combo,Qt.Key.Key_Home)
                for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==key,'actual_QTest_category_selects_exact_branch')
            def choose(key):
                item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key)
                panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());gui.processEvents()
                require(panel.result is not None and panel.result['row']['id']==key,'actual_QTest_list_selects_exact_source_identity')
                require(json.loads(panel.technical.toPlainText())==panel.result,'actual_Qt_technical_JSON_roundtrips_complete_record')
                require(panel.result['actual_reward']is None and panel.result['actual_eligibility']is None and panel.result['mutations_applied']is False,'reading_does_not_claim_actual_reward_eligibility_or_mutate_state')
                observations.append({'category':panel.category.currentData(),'id':key,'name':panel.result['row']['name'],'image_loaded':panel.image_raw is not None})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents()
                    require(tabs.currentWidget()is panel and panel.isVisible(),'actual_main_tab_button_opens_common_battle_preview')
                    require(panel.result is None and panel.entries.count()==184 and panel.scope.currentData()is False and panel.scope.isHidden(),'full_current_default_is_manual_and_has184_stage_entries')
                    for key in('ro6_b_7','ro6_n_7_1','ro6_n_4_1_dlc1'):
                        choose(key);require(panel.image_raw is not None and panel.map_image.pixmap()is not None and not panel.map_image.pixmap().isNull(),'exact_current_map_bytes_load_without_coordinate_markers')
                        if key=='ro6_b_7':shot('new-boss-map')
                    category('choices');panel.search.setText('帮助倒下');gui.processEvents();choose('choice_ro6_final1_8');shot('choice-item-hint')
                    # Other MainWindow tabs impose a larger minimum size. Verify
                    # compact scrolling in a second real owned reader rather than
                    # pretend the main tab shrank or add synthetic text padding.
                    main_panel=panel
                    from rouge.expansion_view import ExpansionUpdatePanel
                    panel=ExpansionUpdatePanel();panel.setWindowTitle('第313节 · 紧凑阅读验收');panel.resize(900,400);panel.show();gui.processEvents()
                    category('choices');panel.search.setText('帮助倒下');choose('choice_ro6_final1_8')
                    compact_native=native(panel)
                    for widget in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(widget);gui.processEvents();c=widget.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(c);b=widget.verticalScrollBar();require(b.maximum()>0,'real_reader_has_nonzero_scroll_without_padding');b.setValue(min(9,b.maximum()));prior=reading(widget);tab=panel.tabs.currentIndex()
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(widget)==prior and panel.tabs.currentIndex()==tab and panel.search.text()=='帮助倒下'and panel.result['row']['id']=='choice_ro6_final1_8','refresh_preserves_filter_identity_tab_selection_and_nonzero_scroll')
                        refreshes.append({'before':prior,'after':reading(widget),'tab':tab,'compact_owned_reader':compact_native,'not_MainWindow_default_viewport':True})
                    panel.close();panel=main_panel;gui.processEvents();QTest.mouseClick(panel.next_button,Qt.MouseButton.LeftButton);gui.processEvents()
                    require(panel.result['row']['id']=='scene_ro6_final1_4'and panel.category.currentData()=='scenes'and panel.scope.currentData()is False,'actual_next_scene_button_follows_only_explicit_destination')
                    require('不是本场景内的选项'in panel.player.toPlainText(),'incoming_choices_not_misrepresented_as_current_scene_options');shot('explicit-next-scene')
                    category('difficulty');choose('NORMAL|16');shot('new-difficulty16')
                    # Read representative new parts, bands, ending and text-only new scenes.
                    for cat,key in(('scrap','rogue_6_scrap_P_07'),('squads','rogue_6_band_23'),('relics','rogue_6_relic_final_7'),('regions','zone_7'),('endings','ro6_ending_4'),('scenes','scene_ro6_end4_enter')):
                        category(cat);choose(key)
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.PACK/'current-topic.json';original=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'actual_complete_public_source_clone_valid_before_damage');target.write_bytes(original+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and not panel.player.toPlainText()and not panel.technical.toPlainText()and panel.entries.count()==0 and panel.image_raw is None and not panel.next_button.isEnabled(),'real_byte_damage_clears_old_selection_readers_image_and_link');shot('source-loss-cleared')
                        finally:target.write_bytes(original)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and panel.entries.currentRow()==-1 and panel.entries.count()==355,'source_recovery_restores_full_scene_list_without_auto_selection');choose('scene_ro6_end4_enter')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_legacy_calculation_context_unchanged')
                    require(all(value==0 for value in calls.values())and not window.auto.isChecked(),'all_real_capture_chat_credential_operations_zero')
                    require('更新前'in window.battle_preview.version_notice.text()and'尚未完整适配'in window.damage_version_notice.text(),'both_legacy_pages_display_version_boundary')
                    native();done=True;window.close();gui.processEvents();gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};window.close();gui.exit(1)
            QTimer.singleShot(250,exercise)
            QTimer.singleShot(args.visible_ms,lambda:gui.exit(2)if not done else None)
            exitcode=gui.exec()
            require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    after=bound_files();result={'section':313,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
