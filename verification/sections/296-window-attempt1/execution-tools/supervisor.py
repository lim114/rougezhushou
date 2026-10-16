"""Actual Windows owned-Popen/job supervisor; bounded, logged, no global process kill."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--status',required=True,type=Path)
    parser.add_argument('--timeout',type=float,default=1200)
    parser.add_argument('argv',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    argv=args.argv[1:] if args.argv[:1]==['--'] else args.argv
    if sys.platform!='win32' or not argv or not 0<args.timeout<=3690:
        raise ValueError('Actual Windows, exact child argv, and a bounded <=3690-second timeout are required')
    root=next(p for p in (Path(__file__).resolve().parent,*Path(__file__).resolve().parents) if (p/'rouge/app.py').is_file())
    status=args.status.resolve()
    if not args.status.is_absolute() or status.is_relative_to(root) or status.exists():
        raise ValueError('Use a fresh absolute status path outside the repository')
    if Path(argv[0]).resolve()!=root/'.venv/Scripts/python.exe':
        raise ValueError('The exact project Windows Python executable is required')
    status.parent.mkdir(parents=True,exist_ok=True)
    stdout=status.with_name(status.name+'.stdout.log');stderr=status.with_name(status.name+'.stderr.log')
    record={'kind':'SECTION296_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION',
            'status':'launch_pending','argv':argv,'cwd':str(root),
            'deadline_seconds':args.timeout,'native_windows_history_verified':False,
            'game_operations':0,'chat_requests':0,'global_process_termination':False,
            'child_primary_exit':None,'supervisor_exit':None,'timed_out':False,
            'supervisor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    process=None;job=None;started=time.monotonic()

    def checkpoint():
        temporary=status.with_name(status.name+'.owned.tmp')
        with temporary.open('w',encoding='utf-8') as stream:
            stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,status)

    # Own the initial status entry, then publish only this supervisor's updates.
    with status.open('x',encoding='utf-8') as initial:
        initial.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n');initial.flush();os.fsync(initial.fileno())
    exit_code=1
    with stdout.open('xb') as out,stderr.open('xb') as err:
        try:
            import win32job
            job=win32job.CreateJobObject(None,'')
            limits=win32job.QueryInformationJobObject(job,win32job.JobObjectExtendedLimitInformation)
            limits['BasicLimitInformation']['LimitFlags']|=win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            win32job.SetInformationJobObject(job,win32job.JobObjectExtendedLimitInformation,limits)
            env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONIOENCODING']='utf-8';env['PYTHONFAULTHANDLER']='1';env['QT_QPA_PLATFORM']='windows'
            process=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
            record.update(status='running',pid=process.pid,owned_handle_retained=True)
            # The live Popen process handle, not a newly resolved/possibly reused PID.
            win32job.AssignProcessToJobObject(job,int(process._handle))
            record['owned_job_assigned']=True
            checkpoint()
            try:
                process.wait(timeout=max(.01,args.timeout-(time.monotonic()-started)))
            except subprocess.TimeoutExpired:
                record['timed_out']=True;record['timeout_observed_elapsed_seconds']=time.monotonic()-started
                record['live_handle_confirmed_at_timeout']=process.poll() is None
                if process.poll() is None:
                    # Kill only the job that this supervisor just created and assigned.
                    record['termination_scope']='This supervisor-owned Windows job only'
                    win32job.TerminateJobObject(job,124)
                    process.wait(timeout=10)
            record['child_primary_exit']=process.returncode
            accounting=win32job.QueryInformationJobObject(job,win32job.JobObjectBasicAccountingInformation)
            record['owned_job_active_processes_after_child_exit']=accounting['ActiveProcesses']
            if accounting['ActiveProcesses']:
                record['owned_descendants_still_live']=True
                win32job.TerminateJobObject(job,125)
                until=time.monotonic()+5
                while time.monotonic()<until:
                    accounting=win32job.QueryInformationJobObject(job,win32job.JobObjectBasicAccountingInformation)
                    if not accounting['ActiveProcesses']:break
                    time.sleep(.05)
            record['owned_job_no_live_execution_verified']=not accounting['ActiveProcesses']
            exit_code=124 if record['timed_out'] else (0 if process.returncode==0 and not accounting['ActiveProcesses'] else 1)
        except BaseException as error:
            record['launch_or_supervision_error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
            if process is not None and process.poll() is None:
                if job is not None and record.get('owned_job_assigned'):
                    win32job.TerminateJobObject(job,125)
                else:
                    # Assignment failed: terminate the original retained child handle only.
                    process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:record['owned_child_closure_incomplete']=True
            if process is not None:record['child_primary_exit']=process.poll()
            exit_code=1
        finally:
            if job is not None:job.Close()
            record['elapsed_seconds']=time.monotonic()-started
            record['status']='completed' if record['child_primary_exit'] is not None else 'incomplete'
            record['supervisor_exit']=exit_code
            out.flush();err.flush();os.fsync(out.fileno());os.fsync(err.fileno())
    record['stdout']={'file':stdout.name,'bytes':stdout.stat().st_size,'sha256':hashlib.sha256(stdout.read_bytes()).hexdigest()}
    record['stderr']={'file':stderr.name,'bytes':stderr.stat().st_size,'sha256':hashlib.sha256(stderr.read_bytes()).hexdigest()}
    checkpoint()
    print(json.dumps({k:record[k] for k in ('status','pid','child_primary_exit','supervisor_exit','timed_out')} if 'pid' in record else {'status':record['status'],'supervisor_exit':exit_code},ensure_ascii=False))
    return exit_code


if __name__=='__main__':raise SystemExit(main())
