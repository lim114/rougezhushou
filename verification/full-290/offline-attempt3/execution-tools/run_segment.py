"""One explicit owned segment at a time; controller0 means terminal, not PASS."""
import argparse,json,tempfile,uuid
from pathlib import Path
from final_common import BASE,ROOT,BOUND,PYTHON,bound,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute-final-A3-segment',choices=('offline','legacy'),required=True)
    for k in ('expected-parent-commit','preparation-sha256','freeze-sha256','activation-sha256'):p.add_argument('--'+k,required=True)
    a=p.parse_args();mode=a.execute_final_A3_segment
    _,_,execution,data,_=bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
    out=Path(tempfile.gettempdir()).resolve()/('rouge-full290-final-A3-'+mode+'-'+uuid.uuid4().hex)
    if out.exists() or out.is_relative_to(ROOT):raise ValueError('Fresh owned external namespace required')
    write_new(BASE/(mode+'-once.json'),{'output':str(out),'root_freeze_sha256':a.freeze_sha256,'automatic_retry_allowed':False})
    out.mkdir()
    record={'kind':'FULL290_FINAL_A3_SEGMENT_EXECUTION','status':'created','root':str(ROOT),'mode':mode,
        'parent_commit':a.expected_parent_commit,'root_freeze_sha256':a.freeze_sha256,
        'preparation_sha256':a.preparation_sha256,'activation_sha256':a.activation_sha256,
        'controller_sha256':sha(Path(__file__)),'actual_validation_attempt':3,
        'actual_legacy_execution_ordinal':4 if mode=='legacy' else None,
        'raw_old_labels_preserved_not_execution_authority':True,'combined_full_pass_claimed':False,
        'game_actions':0,'chat_requests':0,'private_state_included':False}
    write_new(out/'owned-execution.json',record);write_new(out/'orchestration.json',record)
    folder=out/mode;folder.mkdir()
    if mode=='legacy':
        child=[str(PYTHON),'-X','utf8',str(BOUND/'launcher275.py'),'--root',str(ROOT),'--out',str(folder/'actual'),'--mode','legacy']
        deadline,outer=3690,3780
    else:
        child=[str(PYTHON),'-X','utf8',str(BASE/'offline_child.py'),'--out',str(folder/'actual/windows-offline.json'),
            '--expected-parent-commit',a.expected_parent_commit,'--preparation-sha256',a.preparation_sha256,
            '--freeze-sha256',a.freeze_sha256,'--activation-sha256',a.activation_sha256]
        deadline,outer=3600,3690
    argv=[str(PYTHON),'-X','utf8',str(BASE/'supervisor3690.py'),'--status',str(folder/'supervisor.json'),
        '--timeout',str(deadline),'--',*child]
    print(json.dumps({'actual_segment_namespace':str(out),'mode':mode,'actual_pass_claimed':False},ensure_ascii=False),flush=True)
    try:
        observed=execution.execute_observed(argv,folder,timeout=outer)
        terminal,details=execution.terminal_job_record(folder,observed)
        record.update(status='terminal' if terminal else 'not_terminal_do_not_retry',argv=argv,observed=observed,**details)
        execution.checkpoint(out/'orchestration.json',record)
        if not terminal:raise RuntimeError('Segment supervisor/job not terminal; duplicate forbidden')
        bound(a.expected_parent_commit,a.preparation_sha256,a.freeze_sha256,a.activation_sha256)
        print(json.dumps({'terminal':True,'mode':mode,'actual_supervisor_exit':observed['actual_observed_popen_exit'],
            'container':str(out),'combined_full_pass_claimed':False},ensure_ascii=False),flush=True)
        return 0
    except BaseException as error:
        record['exception']={'type':type(error).__name__,'message':str(error)}
        execution.checkpoint(out/'orchestration.json',record);raise

if __name__=='__main__':raise SystemExit(main())
