"""Own exactly one offscreen diagnostic worker; never a native/full runner."""
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import subprocess,sys,time,traceback
import win32job

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
destination=HERE/'first-controller.json'
if destination.exists():raise FileExistsError(destination)
argv=[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(HERE/'verify_migration.py')]
started=time.monotonic();process=None;job=None
record={'kind':'OWNED_OFFSCREEN_FIVE_MODULE_MIGRATION','argv':argv,
 'qpa':'offscreen','timeout_seconds':360,'full_validation_claimed':False,
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'worker_source_sha256':hashlib.sha256((HERE/'verify_migration.py').read_bytes()).hexdigest(),
 'started_at':datetime.now(timezone.utc).isoformat(),'actual_child_exit':None,'timed_out':False}
with (HERE/'first.stdout.log').open('xb') as out,(HERE/'first.stderr.log').open('xb') as err:
    try:
        job=win32job.CreateJobObject(None,'')
        limits=win32job.QueryInformationJobObject(job,win32job.JobObjectExtendedLimitInformation)
        limits['BasicLimitInformation']['LimitFlags']|=win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(job,win32job.JobObjectExtendedLimitInformation,limits)
        env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen';env['PYTHONUTF8']='1';env['PYTHONIOENCODING']='utf-8'
        process=subprocess.Popen(argv,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
            creationflags=subprocess.CREATE_NO_WINDOW)
        record['pid']=process.pid
        win32job.AssignProcessToJobObject(job,int(process._handle));record['owned_job_assigned']=True
        try:process.wait(timeout=360)
        except subprocess.TimeoutExpired:
            record['timed_out']=True
            win32job.TerminateJobObject(job,124);process.wait(timeout=10)
        record['actual_child_exit']=process.returncode
        accounting=win32job.QueryInformationJobObject(job,win32job.JobObjectBasicAccountingInformation)
        if accounting['ActiveProcesses']:
            win32job.TerminateJobObject(job,125)
            until=time.monotonic()+5
            while accounting['ActiveProcesses'] and time.monotonic()<until:
                time.sleep(.05)
                accounting=win32job.QueryInformationJobObject(job,win32job.JobObjectBasicAccountingInformation)
        record['owned_job_no_live_execution_verified']=accounting['ActiveProcesses']==0
    except BaseException as error:
        record['exception']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        if process is not None and process.poll() is None:
            if record.get('owned_job_assigned'):win32job.TerminateJobObject(job,125)
            else:process.terminate()
            process.wait(timeout=10)
        if process is not None:record['actual_child_exit']=process.poll()
    finally:
        if job is not None:job.Close()
record['elapsed_seconds']=time.monotonic()-started
record['controller_exit']=124 if record['timed_out'] else record['actual_child_exit'] if type(record['actual_child_exit']) is int else 1
with destination.open('x',encoding='utf8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
with (HERE/'first.process.exit').open('x',encoding='ascii') as f:f.write(str(record['controller_exit'])+'\n')
print(json.dumps(record,ensure_ascii=False),flush=True)
raise SystemExit(record['controller_exit'])
