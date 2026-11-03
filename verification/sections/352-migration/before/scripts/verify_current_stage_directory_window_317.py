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
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-battle-314').rglob('*')if p.is_file())
    portraits=json.loads((ROOT/'research/p3-current-battle-314/enemy-images.json').read_bytes())['images'];names.update(v['file']for v in portraits.values())
    names.update(['tests/test_current_stage_directory_317.py','tests/test_current_stage_directory_view_317.py','tests/test_current_stage_directory_integration_317.py'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-rewards-315').rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-stage-directory-317/runtime-manifest.json').read_bytes());names.update(manifest['files']);names.add('research/p3-current-stage-directory-317/runtime-manifest.json')
    names.update(['scripts/build_current_stage_directory_317.py','scripts/verify_current_stage_directory_window_317.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','rouge/data/battle-previews.json'])
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
        from rouge import app as app_module,current_stage_directory as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge317-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第317节 · 当前关卡层数与来源（公开隔离验收）');window.show();gui.processEvents()
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
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'requested_filter_available');QTest.keyClick(combo,Qt.Key.Key_Home)
                        for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
                        QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'actual_QTest_filter_selected')
                    def select(sid):
                        item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);panel.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(panel.entries.viewport(),Qt.MouseButton.LeftButton,pos=panel.entries.visualItemRect(item).center());gui.processEvents();require(panel.result['row']['id']==sid,'actual_exact_stage_selected')
                    choose(panel.scope,False);require(panel.entries.count()==184 and panel.result is None,'all184_before_filters_no_auto_selection')
                    choose(panel.stage_floor,'floor6');require(panel.entries.count()==11,'sixth_layer_has_two_documented_regions')
                    for kind,sid in [('normal','ro6_n_7_1'),('emergency','ro6_e_7_1'),('boss','ro6_b_7'),('boss','ro6_b_7_b')]:
                        choose(panel.stage_kind,kind);select(sid);require(panel.stage_info['row']['floor']=='floor6'and panel.stage_info['row']['region']=='盲目者所见','hidden_sixth_layer_not_seventh_or_source_region');require(json.loads(panel.technical.toPlainText())==panel.result and json.loads(panel.stage_source.toPlainText())==panel.stage_info,'separate_original_and_classification_source_roundtrips');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.current_battle_dialog;require(dialog.isVisible()and dialog.panel.stage_id==sid and not dialog.panel.map_image.pixmap().isNull(),'actual_exact_current_stage_original_map_opened');observations.append({'stage':sid,'kind':kind,'floor':panel.stage_info['row']['floor'],'region':panel.stage_info['row']['region'],'variant':panel.stage_info['variant_index']});dialog.close()
                    shot('sixth-layer-two-boss-configurations');window.resize(1000,670);gui.processEvents()
                    for reader in (panel.player,panel.technical,panel.stage_source):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();require(bar.maximum()>0,'actual_three_readers_have_nonzero_scroll');bar.setValue(min(5,bar.maximum()));prior=reading(reader);keys=(panel.stage_floor.currentData(),panel.stage_kind.currentData(),panel.scope.currentData(),panel.tabs.currentIndex(),panel.result['row']['id']);QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(reading(reader)==prior and keys==(panel.stage_floor.currentData(),panel.stage_kind.currentData(),panel.scope.currentData(),panel.tabs.currentIndex(),panel.result['row']['id']),'actual_refresh_preserves_filters_stage_tab_and_reading');refreshes.append({'before':prior,'after':reading(reader),'keys':keys,'actual_MainWindow_size':[window.width(),window.height()]})
                    panel.tabs.setCurrentIndex(2);shot('classification-evidence');choose(panel.stage_floor,'floor1');choose(panel.stage_kind,'pursuit');require(panel.entries.count()>0 and panel.result is None,'pursuit_first_layer_filter_not_boss_or_normal_pool');sid=panel.entries.item(0).data(Qt.ItemDataRole.UserRole);select(sid);require('节点外事件'in panel.player.toPlainText(),'pursuit_is_outside_map_node');observations.append({'stage':sid,'kind':'pursuit','floor':'floor1'});panel.tabs.setCurrentIndex(0);shot('pursuit-outside-nodes')
                    choose(panel.stage_floor,'unknown');choose(panel.stage_kind,'challenge');require(panel.entries.count()==4,'unknown_layer_keeps_special_challenge_entries');select('ro6_s_1');require('层数未确认'in panel.player.toPlainText()and'不能'in panel.player.toPlainText(),'graypit_not_arbitrarily_assigned_a_layer');QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=panel.current_battle_dialog;require(dialog.isVisible()and dialog.panel.stage_id=='ro6_s_1'and not dialog.panel.map_image.pixmap().isNull(),'actual_unknown_layer_exact_graypit_map');observations.append({'stage':'ro6_s_1','kind':'challenge','floor':'unknown'});shot('unknown-layer-graypit')
                    clone=temporary/'public-clone';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST,*manifest['files']):
                        target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    target=clone/model.DATA;raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.packet()is not None,'public_clone_valid_before_byte_damage');target.write_bytes(raw+b' ')
                        try:QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.result is None and not panel.technical.toPlainText()and not panel.stage_source.toPlainText()and not panel.battle_button.isEnabled()and not dialog.isVisible(),'actual_classification_damage_clears_detail_and_closes_preview');shot('classification-source-cleared')
                        finally:target.write_bytes(raw)
                        QTest.mouseClick(panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(panel.entries.count()==4 and panel.entries.currentRow()==-1 and not panel.battle_button.isEnabled(),'recovery_preserves_filters_but_requires_manual_stage_selection')
                    require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();done=True;window.close();gui.processEvents();gui.exit(0)
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
    after=bound_files();result={'section':317,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
