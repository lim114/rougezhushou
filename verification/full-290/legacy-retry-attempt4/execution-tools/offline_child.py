"""Full unchanged430-selector runner under explicit final A3 input/activation gates."""
import argparse,json,runpy,sys,traceback
from pathlib import Path
from final_common import BASE,ROOT,bound,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    for k in ('expected-parent-commit','preparation-sha256','freeze-sha256','activation-sha256'):p.add_argument('--'+k,required=True)
    a=p.parse_args()
    _,_,_,data,_=bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    out=a.out.resolve()
    if not a.out.is_absolute() or out.is_relative_to(ROOT) or out.exists():raise ValueError('Fresh owned external offline receipt required')
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
    sys.argv=[str(ROOT/'scripts/verify_full_available.py'),'--output',str(out),'--verbosity','2']
    code=None;error=None;after_error=None
    try:runpy.run_path(str(ROOT/'scripts/verify_full_available.py'),run_name='__main__')
    except SystemExit as event:code=event.code
    except BaseException as exc:
        code=1;error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    try:bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    except BaseException as exc:after_error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    raw=json.loads(out.read_bytes()) if out.is_file() else None
    drift=[n for n,v in {**data['source_sha256'],**data['supplemental_public_inputs_sha256']}.items()
           if not (ROOT/n).is_file() or sha(ROOT/n)!=v]
    record={'kind':'FULL290_FINAL_A3_ACTUAL_OFFLINE_SOURCE_CLOSURE','actual_validation_attempt':3,
        'root_freeze_sha256':a.freeze_sha256,'actual_suite_exit':code,'exception':error,
        'after_guard_exception':after_error,'source_drift':drift,'actual_receipt_exists':raw is not None,
        'actual_selector_list_matches_final_freeze':bool(raw and raw['selectors']==data['selectors']),
        'actual_source_map_matches_final_freeze':bool(raw and raw['source_sha256']==data['source_sha256']),
        'actual_suite_receipt_sha256':sha(out) if out.is_file() else None,'runner_verbosity':2,
        'all_historical_segments_same_freeze':False,'new_offline_and_legacy_share_final_freeze':True,
        'complete_repository_validation_claimed':False,'game_chat_private_history_verified':False}
    passed=(code==0 and error is None and after_error is None and not drift and raw is not None
        and raw['available_checks_passed'] is True and record['actual_selector_list_matches_final_freeze']
        and record['actual_source_map_matches_final_freeze'])
    record['offline_available_checks_passed']=passed
    write_new(out.with_name('final-A3-offline-source-closure.json'),record)
    return 0 if passed else code if type(code) is int and code!=0 else 1

if __name__=='__main__':raise SystemExit(main())
