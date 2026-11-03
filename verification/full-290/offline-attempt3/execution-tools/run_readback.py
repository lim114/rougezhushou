"""Explicit complete original typed readback after a truly successful new retry."""
import argparse,json
from pathlib import Path
from final_common import BASE,ROOT,BOUND,PYTHON,FREEZE,bound,owned_segment,closed,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-closed-final-A3-legacy4',action='store_true',required=True)
    p.add_argument('--container',type=Path,required=True);p.add_argument('--expected-parent-commit',required=True)
    p.add_argument('--preparation-sha256',required=True);p.add_argument('--activation-sha256',required=True)
    p.add_argument('--freeze-sha256',required=True);a=p.parse_args()
    meta,common,execution,frozen,binding=bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    source,own=owned_segment(a.container,'legacy',a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    ledger=json.loads((source/'orchestration.json').read_bytes())
    observed,sup,details=closed(source/'legacy',execution)
    if (ledger.get('status')!='terminal' or observed['actual_observed_popen_exit']!=0 or sup['child_primary_exit']!=0
            or sup['timed_out'] is not False or sup['supervisor_sha256']!=sha(BASE/'supervisor3690.py')
            or observed.get('argv')!=ledger.get('argv') or sup.get('argv')!=ledger.get('argv',[])[9:]):
        raise ValueError('Never read incomplete or failed legacy work as a complete typed result')
    folder=source/'readback';folder.mkdir()
    record={'kind':'ROOT_ACTUAL_ORIGINAL_TYPED_READBACK_OF_LEGACY_RETRY',
        'status':'created','controller_sha256':sha(Path(__file__)),
        'original_auditor_sha256':sha(BOUND/'audit_full261_saved_readback.py'),
        'input_legacy_container':str(source/'legacy'),'new_readback_pass_claimed':False}
    write_new(folder/'readback-orchestration.json',record)
    argv=[str(PYTHON),'-X','utf8',str(BASE/'supervisor3690.py'),'--status',str(folder/'supervisor.json'),
        '--timeout','120','--',str(PYTHON),'-X','utf8',str(BOUND/'audit_full261_saved_readback.py'),
        '--root',str(ROOT),'--container',str(source/'legacy'),'--bundle',str(BOUND),'--freeze',str(FREEZE)]
    try:
        result=execution.execute_observed(argv,folder,timeout=210)
        terminal,detail=execution.terminal_job_record(folder,result)
        record.update(status='terminal' if terminal else 'not_terminal_do_not_retry',argv=argv,observed=result,**detail)
        execution.checkpoint(folder/'readback-orchestration.json',record)
        if not terminal:raise RuntimeError('Readback supervisor/job not terminal')
        bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
        raw=source/'legacy/independent-saved-readback-audit.json'
        record['actual_audit_receipt_sha256']=sha(raw) if raw.is_file() else None
        record['typed_available_passed']=bool(result['actual_observed_popen_exit']==0 and raw.is_file()
            and json.loads(raw.read_bytes()).get('passed') is True)
        execution.checkpoint(folder/'readback-orchestration.json',record)
        print(json.dumps({'terminal':True,'actual_typed_supervisor_exit':result['actual_observed_popen_exit'],
            'actual_typed_passed':record['typed_available_passed'],'combined_pass_claimed':False},ensure_ascii=False))
        return 0
    except BaseException as error:
        record['exception']={'type':type(error).__name__,'message':str(error)}
        execution.checkpoint(folder/'readback-orchestration.json',record);raise

if __name__=='__main__':raise SystemExit(main())
