"""Source-only observer: Root runs the original/candidate new-run lifecycle."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback
from native_evidence import freeze, assert_native_equal, write_record, source_map

HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE=450
def sha(raw):return hashlib.sha256(raw).hexdigest()
def error_record(error):return {'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','out','phase'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--source-count',type=int,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    guard_path=Path(args.guard).resolve();artifact=Path(__file__).resolve().parent
    assert args.phase in ('original','candidate') and not out.exists() and root not in out.parents and out!=root
    assert artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==112 and len(expected)==args.source_count and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    assert {name:sha((root/name).read_bytes()) for name in extra}==extra
    out.mkdir();(out/'records').mkdir();(out/'public-state').mkdir()
    records=[];snapshots=[];pngs=[];errors=[];calls=[];active={'step':'bootstrap'}
    done=threading.Event();started=time.perf_counter();window=None;module=None;backend=None;calculator=None;enumerator=None
    receipt={'kind':'ROOT_ACTUAL_112_REAL_MAINWINDOW_LIFECYCLE','phase':args.phase,
        'passed':False,'workflow_complete':False,'observation_complete':False,'product_pass':False,
        'observation_only':args.phase=='original','runner_sha256':sha(Path(__file__).read_bytes()),
        'native_helper_sha256':HELPER_SHA,'source_guard_sha256':sha(guard_raw),
        'source_before':expected,'source_additional_before':extra,'source_count':args.source_count,
        'records':records,'snapshots':snapshots,'pngs':pngs,'Qt_errors':errors,'deadline_seconds':DEADLINE,
        'scope':'One actual visible sampling window: accepted account/node/crew samples, real reset, refused old epoch/time samples, accepted new crew sample.',
        'PNG_scope':'Two sampling-tab captures per phase: reset observation and fresh new sample. Stage tooltip is recorded natively on its damage control, not claimed visible in sampling PNG.',
        'restart_scope':'One actual close then direct original RunState and AccountCache reload; no second MainWindow/live JSON alias claim.',
        'private_state_access':False,'game_OCR_chat_sampling_executed':False,'native_Windows_verified':False}
    def save(kind,**value):
        ref=write_record(out/'records',len(records)+1,{'kind':kind,**active,**value})
        ref.update(kind=kind,**active);records.append(ref);return ref
    def watchdog():
        if not done.wait(DEADLINE):
            (out/'timeout.json').write_text(json.dumps({'passed':False,'active':active,'deadline_seconds':DEADLINE}))
            os._exit(124)
    threading.Thread(target=watchdog,daemon=True).start();old_hook=sys.excepthook
    def hook(kind,value,tb):
        errors.append({'step':active['step'],'type':kind.__name__,'message':str(value)});old_hook(kind,value,tb)
    sys.excepthook=hook
    try:
        sys.dont_write_bytecode=True;sys.path.insert(0,str(root))
        import numpy as np
        from PySide6.QtCore import QByteArray,QBuffer,QIODevice,qVersion
        from PySide6.QtWidgets import QApplication
        from rouge import app as module
        from rouge.run_state import RunState
        from rouge.account_cache import AccountCache
        application=QApplication.instance() or QApplication([])
        receipt.update(python=sys.version,qt=qVersion())
        backend=module.DesktopBackend;calculator=module.calculate_damage;enumerator=module.list_game_windows
        def observed(*positional,**keywords):
            before=freeze({'args':positional,'kwargs':keywords})
            try:value=calculator(*positional,**keywords)
            except Exception as error:
                ref=save('actual_calculate_exception',before=before,after={'args':positional,'kwargs':keywords},error=error_record(error))
                calls.append(ref);assert_native_equal({'args':positional,'kwargs':keywords},before,'original exception caller purity');raise
            ref=save('actual_calculate_result',before=before,after={'args':positional,'kwargs':keywords},result=value)
            calls.append(ref);assert_native_equal({'args':positional,'kwargs':keywords},before,'original numeric caller purity');return value
        module.calculate_damage=observed;module.list_game_windows=lambda:[]
        with tempfile.TemporaryDirectory(prefix='public112-',dir=out/'public-state') as directory:
            folder=Path(directory);run_path=folder/'run.json';account_path=folder/'account.json'
            module.RUN_STATE=run_path;module.OPERATOR_STATE=account_path;module.SETTINGS=folder/'settings.json'
            module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
            window=module.MainWindow();window.resize(1400,1050);window.show();window.centralWidget().setCurrentIndex(0)
            image=np.full((24,36,3),65,dtype=np.uint8);image[:,::2,1]=120
            def idle():
                application.processEvents();assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                assert window.desktop.process is None and not window.desktop.pending and not errors
            def pixmap_bytes(pixmap):
                if pixmap is None or pixmap.isNull():return None
                data=QByteArray();buffer=QBuffer(data);assert buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                assert pixmap.save(buffer,'PNG');buffer.close();return bytes(data)
            def views():
                picture=window.capture_operator_picture
                return {'subject':{'key':picture.key,'caption':picture.caption.text(),'image_png':pixmap_bytes(picture.image.pixmap())},
                    'operator_summary':window.operator_summary.toPlainText(),
                    'preview':{'image_png':pixmap_bytes(window.preview.pixmap()),'text':window.preview.text()},
                    'observed_text':window.observed_text.toPlainText(),'capture_status':window.capture_status.text(),
                    'stage_tooltip':window.target_stage.toolTip()}
            def joint():
                return {'run':window.run.state,'account':window.account_cache.records,'observation':window.observation,
                    'views':views(),'disks':{p.relative_to(folder).as_posix():p.read_bytes() for p in sorted(folder.rglob('*')) if p.is_file()}}
            def snapshot(step):
                active['step']=step;idle();ref=save('actual_window_snapshot',value=joint(),sampling_status=window.sampling_status.text(),
                    epoch=window.sample_epoch,generation=window.capture.stats()['generation'],damage_result=window.damage_result)
                snapshots.append({'step':step,'snapshot':ref});return freeze(joint())
            def stamp():return max(time.time(),window.run.state['started_at']+.001,window.last_sample_at+.001)
            def crew(level,gold):
                return {'page':'crew','nodes':[],'captured_at':stamp(),'run':{'operators':[{'id':'mechanist','scope':'run',
                    'fields':{'elite':1,'level':level,'module_id':None,'module_level':0},'skill_ranks':{'1':7,'2':7},
                    'recruitment_kind':'non_emergency','char_buff_ids':[],'char_buffs_complete':True}],
                    'selected_operator':'mechanist','crew_count':1,'relics':{'ids':[],'icons':[],'count':0,'source':'public112-empty-held-bar'},
                    'resources':{'gold':{'value':gold,'source':'public112-confirmed-counter'},
                                 'parts_count':{'value':1,'source':'public112-confirmed-counter'}}}}
            def sample(step,observation,rejected=False):
                active['step']=step;before=freeze(joint());caller=freeze(observation)
                window.sample_received((image,observation));idle();after=freeze(joint())
                assert_native_equal(observation,caller,'whole original sample input purity')
                if rejected:assert_native_equal(after,before,'old sample cannot change state/disks/sixviews')
                save('actual_sample_received',before=before,after=after,caller=observation,rejected_expected=rejected)
            def clear_contract(value):
                current=value['views'];assert value['observation'] is None
                assert current['subject']=={'key':(None,None,''),'caption':'','image_png':None}
                assert current['operator_summary']=='本局已重置，等待新的干员页面读取；账号档案仍保留。'
                assert current['preview']=={'image_png':None,'text':'本局尚未采样'} and current['observed_text']==''
                assert current['capture_status']=='已开始新局，等待新的页面采样；账号档案已保留。'
                assert current['stage_tooltip']=='本局节点详情尚未确认；可手动选择关卡进行局外预览。'
                assert '待识别0帧' in window.sampling_status.text()
            def screenshot(step):
                active['step']=step;idle();assert window.centralWidget().currentIndex()==0 and window.reset_run_button.isVisible()
                before=freeze(joint());path=out/(step+'.png');assert window.grab().save(str(path),'PNG')
                assert_native_equal(joint(),before,'PNG state/account/disk/sixview purity')
                pngs.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),
                    'snapshot':save('actual_sampling_tab_PNG',value=joint(),sampling_tab=window.centralWidget().tabText(0))})
            idle();active['step']='accepted_account_profile'
            account={'id':'mechanist','scope':'account','fields':{'elite':2,'level':90,'trust':100,'potential':1,
                'module_id':None,'module_level':0},'skill_ranks':{'1':10,'2':10,'3':10}}
            caller=freeze(account);window.apply_operator_observation(account,stamp());idle()
            assert_native_equal(account,caller,'original account input purity')
            assert_native_equal(window.account_cache.records['mechanist']['fields'],account['fields'],'real account fields accepted')
            assert_native_equal(window.account_cache.records['mechanist']['skill_ranks'],account['skill_ranks'],'real account ranks accepted')
            identity='ro6_n_1_2';stage=module.catalog()['stages'][identity]
            sample('accepted_node_detail',{'page':'node_detail','nodes':[],'captured_at':stamp(),
                'stage':{'id':identity,'visible_variant_id':identity,'name':stage['name']}})
            old=crew(20,10);sample('accepted_old_crew',old);pre=snapshot('before_reset')
            assert pre['views']['subject']['key'][:2]==('operator','mechanist') and pre['views']['preview']['image_png'] is not None
            assert json.loads(pre['views']['observed_text'])['page']=='crew' and '最近节点详情' in pre['views']['stage_tooltip']
            account_bytes=account_path.read_bytes();account_graph=freeze(window.account_cache.records)
            queued=deepcopy(old);queued['_sampling']={'epoch':window.sample_epoch,'generation':window.capture.stats()['generation']}
            active['step']='real_reset_run';before=freeze(joint());window.reset_run();idle();post=snapshot('after_reset')
            save('actual_reset_run',before=before,after=post)
            assert post['run']['id']!=pre['run']['id'] and post['run']['operators']=={} and post['run']['resources']=={}
            assert_native_equal(post['account'],account_graph,'original account preserved across reset')
            assert account_path.read_bytes()==account_bytes
            if args.phase=='candidate':clear_contract(post)
            screenshot(args.phase+'-after-reset')
            sample('old_epoch_rejected',queued,rejected=True)
            stale=deepcopy(queued);stale.pop('_sampling');stale['captured_at']=window.run.state['started_at']-1
            sample('old_time_rejected',stale,rejected=True);snapshot('after_old_rejections')
            fresh=crew(30,2);fresh['_sampling']={'epoch':window.sample_epoch,'generation':window.capture.stats()['generation']}
            sample('accepted_new_crew',fresh);new=snapshot('new_valid_sample')
            assert new['run']['id']==post['run']['id'] and new['run']['operators']['mechanist']['fields']['level']==30
            assert new['run']['resources']['gold']['value']==2 and new['views']['subject']['key'][:2]==('operator','mechanist')
            assert new['views']['preview']['image_png'] is not None and json.loads(new['views']['observed_text'])['run']['resources']['gold']['value']==2
            assert 'crew' in new['views']['capture_status'] and '等待新的页面采样' not in new['views']['capture_status']
            assert_native_equal(new['account'],account_graph,'original account preserved after new sample');assert account_path.read_bytes()==account_bytes
            screenshot(args.phase+'-new-sample');active['step']='actual_close_direct_reload'
            live=freeze(joint());window.close();application.processEvents()
            restarted=RunState(run_path);reaccount=AccountCache(account_path,window.account_cache.profiles,window.account_cache.implemented_ids)
            assert not restarted.preserve_unreadable and restarted.save_issue is None
            assert not reaccount.preserve_original and reaccount.load_issue is None and reaccount.save_issue is None
            expected_notice='已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
            assert_native_equal(restarted.state['notice'],expected_notice,'exact constructor recovery notice')
            notice_transition={'key':'notice','live':live['run']['notice'],'restart':restarted.state['notice'],
                'expected_restart_literal':expected_notice,'constructor_source_path':'rouge/run_state.py',
                'constructor_source_sha256':expected['rouge/run_state.py']}
            normalized_restart=freeze(restarted.state);normalized_restart['notice']=live['run']['notice']
            assert_native_equal(normalized_restart,live['run'],'whole direct reload with qualified constructor notice transition')
            assert_native_equal(reaccount.records,account_graph,'actual original account direct reload')
            assert_native_equal(joint()['disks'],live['disks'],'close/direct reload all public disks')
            receipt['close_reload']=save('actual_close_direct_reload',live=live,restart_state=restarted.state,notice_transition=notice_transition,
                restart_account=reaccount.records,disks_after=joint()['disks'])
            window.deleteLater();application.processEvents();window=None
        assert len(snapshots)==4 and len(pngs)==2 and not errors
        receipt.update(passed=True,workflow_complete=True,observation_complete=True,product_pass=args.phase=='candidate',actual_windows=1)
    except BaseException as error:receipt['failure']=error_record(error)
    finally:
        if window is not None:window.close()
        if module is not None:
            if backend is not None:module.DesktopBackend=backend
            if calculator is not None:module.calculate_damage=calculator
            if enumerator is not None:module.list_game_windows=enumerator
        sys.excepthook=old_hook;receipt['actual_numeric_calls']=len(calls)
        receipt['source_after']=source_map(root);receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
        receipt['source_drift']=[name for name in set(expected)|set(receipt['source_after']) if expected.get(name)!=receipt['source_after'].get(name)]
        if receipt['source_drift'] or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw or errors:
            receipt.update(passed=False,workflow_complete=False,observation_complete=False,product_pass=False)
        receipt['elapsed_seconds']=time.perf_counter()-started
        with (out/'receipt.json').open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed':receipt['passed'],'phase':args.phase,'product_pass':receipt['product_pass'],'snapshots':len(snapshots)}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
