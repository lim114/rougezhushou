"""Execute only an explicitly activated current275 source-bound native fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import traceback

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in (HERE,*HERE.parents) if (p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--mode',choices=('legacy','current30','current29'),default='legacy')
    args=parser.parse_args()
    if sys.platform!='win32' or args.root.resolve()!=ROOT.resolve():
        raise ValueError('Actual Windows and the exact original project root are required')
    out=args.out.resolve()
    if not args.out.is_absolute() or out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Use a fresh absolute fixture output directory outside the project')
    binding=json.loads((HERE/'activation275.json').read_bytes())
    if binding['status']!='CURRENT285_SOURCE_BOUND_NOT_EXECUTED' or binding['binding_ready'] is not True:
        raise RuntimeError('Inactive fixture: root must declare and bind the final current275 freeze first')
    if args.mode not in binding['allowed_modes']:
        raise ValueError('The requested mode is not present in this exact fixture bundle')
    for relative,expected in binding['execution_tools_sha256'].items():
        if digest(HERE/relative)!=expected:raise AssertionError('Activated executed-tool bytes changed: '+relative)
    freeze=ROOT/binding['root_freeze_relative']
    if digest(freeze)!=binding['root_freeze_sha256']:
        raise AssertionError('Root-declared source-freeze bytes changed')
    frozen=json.loads(freeze.read_bytes())
    for relative,expected in frozen['source_sha256'].items():
        if digest(ROOT/relative)!=expected:raise AssertionError('Root-frozen source changed: '+relative)
    if args.mode=='legacy':
        target=HERE/'launcher125.py'
        argv=[str(target),'--root',str(ROOT),'--guard',str(HERE/'current-source-guard.json'),'--out',str(out)]
    else:
        target=HERE/('window.py' if args.mode=='current30' else 'window29.py')
        argv=[str(target),'--output',str(out),'--revision',binding['tested_worktree_parent_commit']]
    code=None;error=None;cleanup=None;cleanup_error=None
    # The original fixture creates its output itself; no early mkdir masks its fresh-path checks.
    sys.argv=argv
    try:
        runpy.run_path(str(target),run_name='__main__')
    except SystemExit as event:
        code=event.code
    except BaseException as exc:
        error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};code=1
    finally:
        try:
            import native275_bootstrap
            native275_bootstrap.finish_all()
            from qt_verification_cleanup import shutdown_verification_qt
            cleanup=shutdown_verification_qt()
        except BaseException as exc:
            cleanup_error={'type':type(exc).__name__,'message':str(exc)}
    if type(code) is not int:code=1
    after_drift=[name for name,expected in frozen['source_sha256'].items() if digest(ROOT/name)!=expected]
    tool_drift=[name for name,expected in binding['execution_tools_sha256'].items() if digest(HERE/name)!=expected]
    out.mkdir(parents=True,exist_ok=True)
    constructor=out/'native275-constructor-ledger.json'
    ledger=json.loads(constructor.read_bytes()) if constructor.is_file() else None
    actual_windows=bool(ledger and ledger['original_class_reference_restored'] and ledger['records'] and
        any(row['kind']=='normal_public_show' and row['real_win32_window_visible'] for row in ledger['records']) and
        all(row.get('qt_platform','windows')=='windows' for row in ledger['records']))
    record={'kind':'SECTION285_ACTUAL_NATIVE_FIXTURE_LAUNCHER_CLOSURE','mode':args.mode,
            'original_fixture_exit':code,'fixture_exception':error,
            'qt_cleanup':cleanup,'qt_cleanup_error':cleanup_error,
            'source_drift':after_drift,'executed_tool_drift':tool_drift,
            'actual_current_native_windows_window_verified':actual_windows,
            'historical_original_windows_or_game_chat_verified':False,
            'original_assertions_and_results_rewritten':False,
            'root_freeze_sha256':binding['root_freeze_sha256'],
            'execution_tools_sha256':binding['execution_tools_sha256'],
            'game_operations':0,'chat_requests':0,'private_state_isolated':True}
    passed=code==0 and not error and not cleanup_error and not after_drift and not tool_drift and actual_windows
    record['passed']=passed
    record['process_exit_requested']=0 if passed else code if code!=0 else 1
    (out/'native275-launcher-closure.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'mode':args.mode,'passed':passed,'original_fixture_exit':code,'actual_current_native_windows_window_verified':actual_windows,'source_drift':after_drift,'qt_cleanup_error':cleanup_error},ensure_ascii=False))
    return record['process_exit_requested']


if __name__=='__main__':raise SystemExit(main())
