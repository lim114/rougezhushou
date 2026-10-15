"""Root-only ONE full legacy retry; original retained-Popen/job supervision."""
import argparse,json,tempfile,uuid
from pathlib import Path
from retry_common import BASE,ROOT,BUNDLE,PYTHON,FREEZE_SHA,activated,sha,write_new

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute-full-legacy-retry',action='store_true',required=True)
    p.add_argument('--expected-parent-commit',required=True);p.add_argument('--preparation-sha256',required=True)
    p.add_argument('--activation-sha256',required=True);a=p.parse_args()
    meta,common,execution,frozen,binding=activated(a.expected_parent_commit,a.preparation_sha256,a.activation_sha256)
    out=Path(tempfile.gettempdir()).resolve()/('rouge-full290-legacy-retry-'+uuid.uuid4().hex)
    if out.exists() or out.is_relative_to(ROOT):raise ValueError('Fresh external namespace required')
    write_new(BASE/'execution-once.json',{'output':str(out),'root_freeze_sha256':FREEZE_SHA,
        'parent_commit':a.expected_parent_commit,'actual_legacy_execution_ordinal':3,
        'automatic_or_duplicate_retry_allowed':False})
    out.mkdir()
    record={'kind':'FULL290_SAME_SOURCE75_LEGACY_RETRY_EXECUTION3','status':'created',
        'root':str(ROOT),'parent_commit':a.expected_parent_commit,'root_freeze_sha256':FREEZE_SHA,
        'preparation_sha256':a.preparation_sha256,'activation_sha256':a.activation_sha256,
        'controller_sha256':sha(Path(__file__)),'validation_segment':'legacy_retry',
        'actual_legacy_execution_ordinal':3,'raw_old_labels_preserved_not_execution_authority':True,
        'full_scope':binding['full_scope'],'available_checks_passed_claimed':False,
        'game_actions':0,'chat_requests':0,'private_state_included':False}
    write_new(out/'owned-execution.json',record);write_new(out/'orchestration.json',record)
    print(json.dumps({'actual_legacy_retry_namespace':str(out),'started_pass_claimed':False},ensure_ascii=False),flush=True)
    folder=out/'legacy';folder.mkdir()
    argv=[str(PYTHON),'-X','utf8',str(BASE/'supervisor3690.py'),'--status',str(folder/'supervisor.json'),
        '--timeout','3690','--',str(PYTHON),'-X','utf8',str(BUNDLE/'launcher275.py'),
        '--root',str(ROOT),'--out',str(folder/'actual'),'--mode','legacy']
    try:
        observed=execution.execute_observed(argv,folder,timeout=3780)
        terminal,details=execution.terminal_job_record(folder,observed)
        record.update(status='terminal' if terminal else 'not_terminal_do_not_retry',argv=argv,observed=observed,**details)
        execution.checkpoint(out/'orchestration.json',record)
        if not terminal:raise RuntimeError('Actual supervisor/job not terminal; retry forbidden')
        activated(a.expected_parent_commit,a.preparation_sha256,a.activation_sha256)
        record['complete']='terminal_only_NOT_pass';execution.checkpoint(out/'orchestration.json',record)
        print(json.dumps({'terminal':True,'actual_supervisor_exit':observed['actual_observed_popen_exit'],
                          'container':str(out),'typed_or_combined_pass_claimed':False},ensure_ascii=False),flush=True)
        return 0
    except BaseException as error:
        record['exception']={'type':type(error).__name__,'message':str(error)}
        execution.checkpoint(out/'orchestration.json',record);raise

if __name__=='__main__':raise SystemExit(main())
