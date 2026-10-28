"""Focused actual Windows player navigation checks, exclusively in temporary state."""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import json,os,sys,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def source_hashes():
    paths=list((ROOT/'rouge').glob('*.py'))+[Path(__file__).resolve(),ROOT/'scripts/verify_full_available.py']
    paths+=list((ROOT/'tests').glob('test_player*py'))
    paths+=list((ROOT/'scripts').glob('verify_player*py'))
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()for p in sorted(set(paths))}

def run(section,receipt):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    import win32gui,win32process
    from rouge import app as a
    from rouge.player_workspace import GROUPS
    receipt=Path(receipt).resolve();assert not receipt.exists();receipt.parent.mkdir(parents=True,exist_ok=True)
    before=source_hashes();checks=[];calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    def require(value,label):
        if not value:raise AssertionError(label)
        if label not in checks:checks.append(label)
    def forbidden(key):
        def f(*args,**kwargs):calls[key]+=1;raise AssertionError('Forbidden real operation: '+key)
        return f
    gui=QApplication.instance()or QApplication([]);window=None;failure=None;images=[]
    try:
        require(sys.platform=='win32'and gui.platformName()=='windows','real_Windows_QPA')
        with TemporaryDirectory(prefix=f'rouge-player{section}-')as folder,ExitStack()as stack:
            tmp=Path(folder)
            for key,value in {'ROOT':tmp,'SETTINGS':tmp/'settings.json','OPERATOR_STATE':tmp/'operators.json','RUN_STATE':tmp/'run.json'}.items():stack.enter_context(patch.object(a,key,value))
            backend=a.DesktopBackend;stack.enter_context(patch.object(a,'DesktopBackend',lambda _path,callback:backend(tmp/'chat',callback)))
            stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
            for name,key in [('connect','game_connect'),('capture','capture'),('next_frame','next_frame')]:stack.enter_context(patch.object(a.GameCapture,name,side_effect=forbidden(key)))
            for name,key in [('start','desktop_start'),('request','desktop_request')]:stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(a,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(a,'read_key',side_effect=forbidden('credential_read')))
            from rouge import public_node_statistics
            calls['public_statistics_read']=0
            stack.enter_context(patch.object(public_node_statistics,'fetch',side_effect=forbidden('public_statistics_read')))
            window=a.MainWindow();window.setWindowTitle(f'第{section}节 · 玩家界面隔离验证');window.resize(1100,790);window.show();gui.processEvents()
            h=int(window.winId());require(win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),'visible_owned_native_window')
            state=deepcopy(window.run.state);ws=window.centralWidget()
            require(tuple(ws.tabText(i)for i in range(ws.count()))==GROUPS,'five_player_groups_only')
            panel=window.reference_panel('relics');gui.processEvents();require(ws.currentWidget()is panel,'exact_reference_navigation')
            require(not ws.developer_dialog.isVisible(),'development_tools_not_default_visible')
            panel.search.setText('支援');query=panel.search.text()
            ws.setCurrentWidget(window.exploration_map_tab);ws.setCurrentWidget(panel);gui.processEvents()
            require(panel.search.text()==query,'reference_query_survives_page_switch')
            require(window.run.state==state,'navigation_does_not_modify_run')
            # Later sections install one focused acceptance extension alongside the feature.
            from rouge import player_acceptance
            player_acceptance.check(section,window,gui,require)
            require(all(x==0 for x in calls.values()),'all_seven_external_operations_zero')
            require(window.run.state==state,'feature_does_not_reset_run')
            from PySide6.QtTest import QTest
            QTest.qWait(120);gui.processEvents()
            shot=receipt.with_suffix('.png');shot_target=window.player_notes if section==387 else window.public_statistics if section==388 else window
            assert shot_target.grab().save(str(shot))
            images.append({'file':shot.relative_to(ROOT).as_posix(),'sha256':sha256(shot.read_bytes()).hexdigest()})
            window.close();gui.processEvents();require(not window.isVisible(),'normal_owned_window_close');window=None
    except Exception:
        failure=traceback.format_exc()
    finally:
        if window is not None:window.close();gui.processEvents()
    after=source_hashes();passed=failure is None and before==after
    result={'section':section,'passed':passed,'checks':checks,'unique_checks':len(checks),'qpa':gui.platformName(),
        'source_sha256_before':before,'source_sha256_after':after,'source_drift':before!=after,
        'external_operation_attempts':calls,'screenshots':images,'failure':failure,
        'temporary_state_only':True,'private_contents_read_copied_or_restored':False,
        'game_operated':False,'chat_sent':False,'full_suite_rerun':False,
        'historical_full_receipt':'verification/full-380/summary.json','old_full_proves_current_UI':False}
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'section':section,'passed':passed,'unique_checks':len(checks),'failure':failure},ensure_ascii=False))
    return 0 if passed else 1
