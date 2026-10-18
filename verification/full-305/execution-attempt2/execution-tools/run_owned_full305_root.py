"""Explicit root second execution wrapper retaining the actual controller Popen."""
import argparse,json,os,subprocess,sys,traceback
from full305_common import BASE,ROOT,PYTHON,READY_PATH,bound,sha,write_new,now
from execution305 import checkpoint


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true')
    for name in ('expected-parent-commit','freeze-sha256','activation-sha256'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    if not args.execute:raise ValueError('Root explicit second --execute required; never automatic retry.')
    bound(args.expected_parent_commit,args.freeze_sha256,args.activation_sha256)
    folder=BASE/'root-launch-attempt2'
    if folder.exists():raise FileExistsError('Second root execution is exclusive; never overwrite actual prior process evidence.')
    folder.mkdir()
    argv=[str(PYTHON),'-B','-X','utf8',str(BASE/'run_full305_controller.py'),'--execute',
        '--expected-parent-commit',args.expected_parent_commit,'--freeze-sha256',args.freeze_sha256,'--activation-sha256',args.activation_sha256]
    with(folder/'stdout.txt').open('xb')as stdout,(folder/'stderr.txt').open('xb')as stderr:
        process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
        value={'section':305,'actual_validation_attempt':2,'kind':'root_actual_full_controller_retained_Popen','status':'running',
            'controller_pid':process.pid,'root_wrapper_pid':os.getpid(),'argv':argv,'owned_popen_retained':True,'actual_observed_exit':None,
            'started_at':now(),'automatic_retry_allowed':False,'global_process_termination':False,
            'root_freeze_sha256':args.freeze_sha256,'activation_sha256':args.activation_sha256,'preparation_ready_sha256':sha(READY_PATH),
            'root_wrapper_source_sha256':sha(BASE/'run_owned_full305_root.py'),'controller_source_sha256':sha(BASE/'run_full305_controller.py')}
        write_new(folder/'controller-process.json',value)
        print(json.dumps({'root_process_receipt':str(folder/'controller-process.json'),'controller_launch_pid':process.pid,
                          'root_wrapper_pid':os.getpid(),'actual_full_PASS_claimed':False},ensure_ascii=False),flush=True)
        code=process.wait()
        with(folder/'process.exit').open('xb')as stream:stream.write((str(code)+'\n').encode('ascii'));stream.flush();os.fsync(stream.fileno())
        error=None
        try:bound(args.expected_parent_commit,args.freeze_sha256,args.activation_sha256)
        except BaseException as event:error={'type':type(event).__name__,'message':str(event),'traceback':traceback.format_exc()}
        value.update(status='completed',actual_observed_exit=code,finished_at=now(),exit_observed_directly_from_retained_popen=True,
            exit_inferred_from_output_json=False,source_guard_exception_after=error)
        checkpoint(folder/'controller-process.json',value)
    print(json.dumps({'actual_root_controller_exit':code,'root_wrapper_pid':os.getpid(),'controller_launch_pid':process.pid,
                      'source_guard_after_error':error,'actual_full_PASS_not_inferred_from_exit_alone':True},ensure_ascii=False))
    return code if error is None else 1


if __name__=='__main__':raise SystemExit(main())
