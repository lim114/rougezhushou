"""Copy to .cache/run373.py; only root explicitly runs necessary installed checks."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,os,re,subprocess,sys,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
SELECTORS=('tests.test_current_stage_objects_373','tests.test_current_stage_objects_view_373','tests.test_common_content_352')
def enc(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')


def main():
    p=argparse.ArgumentParser();p.add_argument('kind',choices=('source','necessary','native'));p.add_argument('--attempt',type=int,default=1);p.add_argument('--native-visible-ms',type=int);args=p.parse_args()
    if args.attempt<1:raise ValueError('Positive unique attempt required')
    if not(ROOT/'rouge/current_stage_objects.py').is_file():raise RuntimeError('Install actual373 candidate and ordinary-page adapter first')
    output=ROOT/f'verification/sections/373-{args.kind}-attempt{args.attempt}';output.mkdir();sys.path.insert(0,str(ROOT))
    before={};after={};child=None;code=None;failure=None;native=None;argv=[];started=datetime.now(timezone.utc).isoformat()
    try:
        from scripts.verify_current_stage_objects_window_373 import bound_files
        before=bound_files();prefix=[sys.executable,'-B','-X','utf8']
        if args.kind=='source':argv=prefix+['scripts/build_current_stage_objects_373.py','--check','--original-root',str(ROOT/'.cache/batch371-380-battle')]
        elif args.kind=='necessary':argv=prefix+['-m','unittest','-v',*SELECTORS]
        else:
            argv=prefix+['scripts/verify_current_stage_objects_window_373.py','--receipt',str(output/'actual/window.json')]
            if args.native_visible_ms is not None:
                if args.native_visible_ms<=0:raise ValueError('Explicit positive native budget required')
                argv+=['--visible-ms',str(args.native_visible_ms)]
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='windows'if args.kind=='native'else'offscreen')
        with(output/'stdout.txt').open('xb')as stdout,(output/'stderr.txt').open('xb')as stderr:
            child=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=child.wait()
        path=output/'actual/window.json'
        if path.is_file():native=json.loads(path.read_bytes())
        after=bound_files()
    except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    log_path=output/'stderr.txt';log=log_path.read_text('utf8',errors='replace')if log_path.is_file()else'';match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
    passed=failure is None and code==0 and bool(before)and before==after
    if args.kind=='necessary':passed=passed and match is not None and int(match[1])>0
    if args.kind=='native':passed=passed and native is not None and native.get('passed')is True
    record={'section':373,'kind':args.kind,'argv':argv,'retained_popen_pid':child.pid if child else None,'actual_observed_exit':code,'exit_code':code,'start_utc':started,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':bool(before)and before==after,'source_guard_is_selected_not_all_transitive_dependencies':True,'selectors':list(SELECTORS)if args.kind=='necessary'else None,'methods_ran':int(match[1])if match else None,'native_original_default_budget_retained':args.kind=='native'and args.native_visible_ms is None,'native_explicit_budget_ms':args.native_visible_ms if args.kind=='native'else None,'passed':bool(passed),'failure':failure,'full_validation_rerun':False,'descendant_job_closure_claimed':False,'outer_process_timeout_provided_by_this_wrapper':False,'section_completed_or_published':False,'batch_pause_state_changed':False}
    if native is not None:record.update(actual_fixture_pid=native.get('process_id'),window_receipt=path.relative_to(ROOT).as_posix(),window_receipt_sha256=sha256(path.read_bytes()).hexdigest(),window_passed=native.get('passed'),PID_equality_assumed=False)
    (output/'process.json').write_bytes(enc(record));(output/'process.exit').write_text(('unknown'if code is None else str(code))+'\n',encoding='ascii');(output/'execution-runner.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha256')},ensure_ascii=False))
    if native is not None:print(json.dumps({'native_checks':native.get('unique_checks'),'native_failure':native.get('failure')},ensure_ascii=False))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
