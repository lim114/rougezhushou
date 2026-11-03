"""Exact actual290 observed-Popen/job helpers; no invocation at import."""
import json,os,subprocess,time,traceback
from full425_common import ROOT,now,sha,write_new

def checkpoint(path, record):
    """Replace only this execution's already owned mutable control record."""
    temporary = path.with_name(path.name + '.owned.tmp')
    with temporary.open('wb') as file:
        file.write((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)

def execute_observed(argv, folder, timeout=1890):
    """Retain the real supervisor Popen, preserving its observed actual exit.

    The mature supervisor alone owns/cleans its newly assigned Windows job.
    This controller never kills by PID or terminates global processes. If the
    supervisor itself fails to become terminal, it records uncertainty and
    forbids later steps; it does not turn a timer into process completion.
    """
    record = {'argv': argv, 'started_at': now(), 'status': 'launch_pending',
              'actual_observed_popen_exit': None, 'owned_popen_retained': False,
              'global_process_termination': False}
    path = folder / 'controller-process.json'
    write_new(path, record)
    started = time.monotonic()
    process = None
    with (folder / 'controller-supervisor.stdout.log').open('xb') as stdout, \
            (folder / 'controller-supervisor.stderr.log').open('xb') as stderr:
        try:
            process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            record.update(status='running', pid=process.pid, owned_popen_retained=True)
            checkpoint(path, record)
            last_notice = started
            while process.poll() is None:
                elapsed = time.monotonic() - started
                if elapsed > timeout:
                    record.update(status='supervisor_not_terminal',
                                  controller_outer_wait_elapsed=True,
                                  duplicate_execution_forbidden=True,
                                  actual_observed_popen_exit=None)
                    checkpoint(path, record)
                    return record
                if time.monotonic() - last_notice >= 30:
                    print(json.dumps({'step': folder.name, 'supervisor_still_running': True,
                                      'elapsed_seconds': round(elapsed, 1)}, ensure_ascii=False), flush=True)
                    last_notice = time.monotonic()
                time.sleep(1)
            record.update(status='completed', actual_observed_popen_exit=process.returncode,
                          elapsed_seconds=time.monotonic() - started, completed_at=now())
            # A new original file containing the immediately observed real exit,
            # not an inferred/derived shell-exit placeholder.
            exit_path = folder / 'process.exit'
            with exit_path.open('xb') as file:
                file.write((str(process.returncode) + '\n').encode('ascii'))
                file.flush()
                os.fsync(file.fileno())
            write_new(folder / 'process-exit-origin.json', {
                'kind': 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT',
                'actual_observed_popen_exit': process.returncode,
                'derived_from_supervisor_json': False, 'process_exit_sha256': sha(exit_path),
                'original_controller_pid': os.getpid(), 'observed_at': now()})
        except BaseException as error:
            record.update(status='controller_error', exception={
                'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()},
                actual_observed_popen_exit=None if process is None else process.poll(),
                duplicate_execution_forbidden=True,
                owned_supervisor_may_still_run=bool(process is not None and process.poll() is None))
            checkpoint(path, record)
            raise
    checkpoint(path, record)
    return record

def terminal_job_record(folder, observed):
    status = folder / 'supervisor.json'
    if observed.get('status') != 'completed' or type(observed.get('actual_observed_popen_exit')) is not int or not status.is_file():
        return False, {'terminal_supervisor_and_job_verified': False}
    data = json.loads(status.read_bytes())
    terminal = (data.get('status') == 'completed'
                and type(data.get('child_primary_exit')) is int
                and data.get('supervisor_exit') == observed['actual_observed_popen_exit']
                and data.get('owned_handle_retained') is True
                and data.get('owned_job_assigned') is True
                and data.get('owned_job_no_live_execution_verified') is True)
    return terminal, {'terminal_supervisor_and_job_verified': terminal,
                      'supervisor_sha256': sha(status),
                      'child_primary_exit': data.get('child_primary_exit'),
                      'supervisor_exit': data.get('supervisor_exit'),
                      'timed_out': data.get('timed_out'),
                      'owned_job_no_live_execution_verified': data.get('owned_job_no_live_execution_verified')}
