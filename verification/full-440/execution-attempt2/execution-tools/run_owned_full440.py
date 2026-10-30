"""Root-only retained-Popen launch; no automatic relaunch or PID termination."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
from full440_common import BASE,ROOT,PYTHON,ATTEMPT,native,bound,sha,now,write_new
from execution440 import checkpoint


def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true')
    for name in('expected-parent-commit','freeze-sha256','activation-sha256'):p.add_argument('--'+name,required=True)
    args=p.parse_args()
    if not args.execute:raise ValueError('Explicit root execute required.')
    native();bound(args.expected_parent_commit,args.freeze_sha256,args.activation_sha256)
    folder=BASE/'root-launch'
    if folder.exists()or(BASE/'full440-once.json').exists():raise FileExistsError('This attempt has an existing launch. Inspect it; never launch a duplicate.')
    folder.mkdir()
    argv=[str(PYTHON),'-B','-X','utf8',str(BASE/'run_full440_controller.py'),'--execute',
          '--expected-parent-commit',args.expected_parent_commit,'--freeze-sha256',args.freeze_sha256,
          '--activation-sha256',args.activation_sha256]
    record={'section':440,'actual_validation_attempt':ATTEMPT,'kind':'root_actual_full_controller_retained_Popen',
            'status':'launch_pending','root_wrapper_pid':os.getpid(),'argv':argv,
            'owned_popen_retained':False,'actual_observed_exit':None,
            'wrapper_sha256':sha(Path(__file__)),'started_at':now(),
            'automatic_retry_allowed':False,'global_process_termination':False,
            'game_operations':0,'chat_requests':0}
    path=folder/'controller-process.json';write_new(path,record);process=None
    try:
        with(folder/'stdout.txt').open('xb')as out,(folder/'stderr.txt').open('xb')as err:
            process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                                     close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
            record.update(status='running',controller_pid=process.pid,owned_popen_retained=True);checkpoint(path,record)
            notice=time.monotonic()
            while process.poll()is None:
                if time.monotonic()-notice>=30:
                    print(json.dumps({'full440_attempt':ATTEMPT,'root_controller_still_running':True,'status_file':str(path)},ensure_ascii=False),flush=True);notice=time.monotonic()
                time.sleep(1)
            code=process.returncode
            with(folder/'process.exit').open('xb')as file:
                file.write((str(code)+'\n').encode('ascii'));file.flush();os.fsync(file.fileno())
            record.update(status='completed',actual_observed_exit=code,finished_at=now(),
                          exit_observed_directly_from_retained_popen=True,exit_inferred_from_output_json=False,
                          actual_process_exit_sha256=sha(folder/'process.exit'))
            checkpoint(path,record)
            print(json.dumps({'full440_attempt':ATTEMPT,'root_controller_actual_observed_exit':code,'status_file':str(path)},ensure_ascii=False),flush=True)
            return code
    except BaseException as event:
        record.update(status='wrapper_uncertain_no_duplicate_launch',exception={'type':type(event).__name__,'message':str(event),'traceback':traceback.format_exc()},
                      actual_observed_exit=None if process is None else process.poll(),
                      original_controller_may_still_run=bool(process is not None and process.poll()is None),duplicate_execution_forbidden=True)
        checkpoint(path,record);raise


if __name__=='__main__':raise SystemExit(main())
