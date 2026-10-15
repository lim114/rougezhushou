"""Bounded, offscreen diagnostic only; never a full validation receipt."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import traceback
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
os.environ['QT_QPA_PLATFORM']='offscreen'
FREEZE=ROOT/'verification/full-290/source-freeze.json'
LOG=Path(r'C:\Users\李娜\AppData\Local\Temp\rouge-full290-4d462dfd95354abf94a1aabdbbdc2df6\offline\actual\windows-offline.log')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-candidates',action='store_true')
    args=parser.parse_args()
    mode='candidates' if args.run_candidates else 'loader'
    output=HERE/(mode+'-receipt.json')
    if output.exists():raise FileExistsError(output)
    original_freeze=FREEZE.read_bytes();frozen=json.loads(original_freeze)
    expected={**frozen['source_sha256'],**frozen['supplemental_public_inputs_sha256']}
    before={name:sha(ROOT/name) for name in expected}
    if before!=expected:raise ValueError('Live frozen public source differs before diagnostic')
    raw=LOG.read_bytes();progress=raw.decode('utf8').strip()
    if not re.fullmatch(r'[.sFEUux]+',progress):raise ValueError('Do not infer progress from a mixed text log')
    marker_positions=[index+1 for index,char in enumerate(progress) if char=='F'][:5]
    safety_events=[]
    protected=(ROOT/'.local',ROOT/'local-settings.json')

    def audit(event,arguments):
        if event=='open' and arguments and isinstance(arguments[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(arguments[0])).resolve()
            if any(path==item or path.is_relative_to(item) for item in protected):
                safety_events.append({'event':'private_open_blocked','path_name':path.name})
                raise RuntimeError('Diagnostic refuses original private runtime data')
        if event in ('subprocess.Popen','socket.connect'):
            safety_events.append({'event':event+'_blocked'})
            raise RuntimeError('Diagnostic refuses external process or network connection')
    sys.addaudithook(audit)
    def forbidden(*_args,**_kwargs):
        safety_events.append({'event':'game_or_chat_entry_blocked'})
        raise RuntimeError('Diagnostic forbids game enumeration/capture and desktop chat')

    result=None;error=None;all_tests=[];candidate_indices=[];windows=[]
    try:
        from rouge import app as application,capture,desktop_backend
        from PySide6.QtWidgets import QApplication
        from verify_full_available import AvailableResult
        with tempfile.TemporaryDirectory(prefix='rouge-290-offscreen-diagnostic-') as directory,ExitStack() as stack:
            temporary=Path(directory)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json',
                'OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
                stack.enter_context(patch.object(application,name,value))
            for module,name in ((application,'list_game_windows'),(capture,'list_game_windows'),
                (capture.GameCapture,'connect'),(capture.GameCapture,'capture'),
                (capture.GameCapture,'next_frame'),(desktop_backend.DesktopBackend,'start'),
                (desktop_backend.DesktopBackend,'request')):
                stack.enter_context(patch.object(module,name,side_effect=forbidden))
            all_tests=list(flatten(unittest.defaultTestLoader.loadTestsFromNames(frozen['selectors'])))
            for position in marker_positions:
                lower=max(0,position-1-25);upper=min(len(all_tests),position+25)
                windows.append({'progress_F_character_position_1based':position,
                    'not_a_failure_identity':True,'candidate_indices_1based':[i+1 for i in range(lower,upper)],
                    'candidate_test_ids':[all_tests[i].id() for i in range(lower,upper)]})
                candidate_indices.extend(range(lower,upper))
            candidate_indices=sorted(set(candidate_indices))
            save(HERE/(mode+'-ordered-loader.json'),{'selectors':frozen['selectors'],
                'ordered_test_ids':[test.id() for test in all_tests],
                'F_search_windows':windows,'candidate_indices_1based':[i+1 for i in candidate_indices],
                'candidate_test_ids':[all_tests[i].id() for i in candidate_indices],
                'warning':'Outcome markers include subtests/class setup/skips; position-to-ID is only a search heuristic.'})
            if QApplication.instance() and QApplication.instance().platformName()!='offscreen':
                raise RuntimeError('Unexpected native QApplication during loader imports')
            if args.run_candidates:
                with (HERE/'candidates-unittest.log').open('x',encoding='utf8') as stream:
                    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=AvailableResult).run(
                        unittest.TestSuite([all_tests[index] for index in candidate_indices]))
            from qt_verification_cleanup import shutdown_verification_qt
            cleanup=shutdown_verification_qt()
    except BaseException as exc:
        error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        cleanup=None
    after={name:sha(ROOT/name) for name in expected}
    receipt={'kind':'OFFSCREEN_SEARCH_DIAGNOSTIC_NOT_FULL_VALIDATION','mode':mode,
        'time':datetime.now(timezone.utc).isoformat(),'original_freeze_sha256':hashlib.sha256(original_freeze).hexdigest(),
        'original_progress_log':str(LOG),'original_progress_log_sha256':hashlib.sha256(raw).hexdigest(),
        'original_progress_bytes':len(raw),'progress_marker_count':len(progress),
        'first_five_F_positions_1based':marker_positions,'loaded_tests':len(all_tests),
        'candidate_count':len(candidate_indices),'position_windows_are_only_search_clues':True,
        'test_execution_attempted':args.run_candidates,'exception':error,'qt_cleanup':cleanup,
        'qpa_environment':os.environ['QT_QPA_PLATFORM'],'safety_events':safety_events,
        'original_private_state_opened':False,'game_captures':0,'chat_requests':0,
        'before_matches_frozen_source':before==expected,'after_matches_frozen_source':after==expected,
        'freeze_bytes_unchanged':FREEZE.read_bytes()==original_freeze,'diagnostic_source_sha256':sha(Path(__file__)),
        'actual_test_failures':[] if result is None else [{'test':t.id(),'traceback':trace} for t,trace in result.failures],
        'actual_test_errors':[] if result is None else [{'test':t.id(),'traceback':trace} for t,trace in result.errors],
        'tests_run':None if result is None else result.testsRun,
        'actual_unavailable':None if result is None else result.unavailable,
        'actual_result_successful':None if result is None else result.wasSuccessful(),
        'complete_or_full_available_pass_claimed':False}
    save(output,receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('actual_test_failures','actual_test_errors','actual_unavailable')},ensure_ascii=False),flush=True)
    return 0 if error is None and before==after==expected and not safety_events and (result is None or result.wasSuccessful()) else 1

if __name__=='__main__':raise SystemExit(main())
