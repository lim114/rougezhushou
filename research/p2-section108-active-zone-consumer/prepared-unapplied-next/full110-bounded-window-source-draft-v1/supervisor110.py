"""Linux-only inactive full110 attempt1 Source launcher with an independent1200-second deadline.

Source only at preparation time. Root supplies the exact reviewed argv after '--'.
No shell, no global wineserver termination, no fabricated child exit code.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def session_members(session_id):
    members = []
    unreadable = []
    for folder in Path('/proc').iterdir():
        if not folder.name.isdigit():
            continue
        try:
            # comm may contain spaces and parentheses; the final ')' ends it.
            tail = (folder / 'stat').read_text().rpartition(')')[2].split()
            if int(tail[3]) == session_id:  # state, ppid, pgrp, session
                members.append({'pid': int(folder.name), 'state': tail[0]})
        except FileNotFoundError:
            pass
        except (OSError, ValueError, IndexError) as error:
            unreadable.append({'pid': int(folder.name), 'error': type(error).__name__})
    return sorted(members, key=lambda member: member['pid']), unreadable


def finish_owned_session(session_id):
    """Clean this launch's group even if its original leader already exited."""
    members, unreadable = session_members(session_id)
    receipt = {'members_before_cleanup': [member['pid'] for member in members],
               'owned_session_members_before_cleanup': members,
               'proc_entries_unreadable_before_cleanup': unreadable}
    # Linux proc_pid_stat(5): exactly Z denotes an already terminated zombie.
    # Every other or unknown state remains potentially live and is not excused.
    if any(member['state'] != 'Z' for member in members):
        receipt['termination_signal'] = 'SIGKILL'
        receipt['termination_scope'] = 'This launched OS process group only'
        try:
            os.killpg(session_id, signal.SIGKILL)
        except ProcessLookupError:
            receipt['process_group_already_absent'] = True
        # This is closure, not an extension of the product execution deadline.
        closure_deadline = time.monotonic() + 5
        while time.monotonic() < closure_deadline:
            members, unreadable = session_members(session_id)
            if not any(member['state'] != 'Z' for member in members):
                break
            time.sleep(0.05)
    receipt['owned_session_pids_after_completion'] = [member['pid'] for member in members]
    receipt['owned_session_members_after_completion'] = members
    receipt['proc_entries_unreadable'] = unreadable
    receipt['owned_session_absence_verified'] = not members and not unreadable
    possibly_live = [member['pid'] for member in members if member['state'] != 'Z']
    receipt['potentially_live_owned_session_pids_after_completion'] = possibly_live
    receipt['zombie_owned_session_pids_after_completion'] = [
        member['pid'] for member in members if member['state'] == 'Z']
    receipt['no_live_owned_execution_verified'] = not possibly_live and not unreadable
    receipt['retained_zombies_reaped_by_supervisor'] = False
    receipt['zombie_scope'] = (
        'Z denotes terminated but not necessarily reaped; no-live execution '
        'does not imply owned-session absence or reaping of retained entries.')
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', required=True)
    parser.add_argument('argv', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
    if not argv:
        raise ValueError('Exact reviewed launch argv is required after --')
    if sys.platform != 'linux':
        raise RuntimeError('This independent supervisor requires Linux /proc')
    status = Path(args.status).resolve()
    status.parent.mkdir(parents=True, exist_ok=True)
    stdout_path = status.with_name(status.name + '.stdout.log')
    stderr_path = status.with_name(status.name + '.stderr.log')
    record = {'format_version': 1, 'status': 'launch_pending',
              'argv': argv, 'cwd': str(Path.cwd().resolve()),
              'deadline_seconds': 1200, 'native_windows_verified': False,
              'after_section': 110, 'full110_attempt': 1,
              'global_wineserver_terminated': False, 'child_primary_exit': None,
              'supervisor_exit': None, 'timed_out': False,
              'runner_argv_is_reviewed_by_root': 'Required; not inferred by supervisor',
              'supervisor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    process = None
    started = time.monotonic()
    with status.open('x', encoding='utf-8') as status_stream:
        with stdout_path.open('xb') as stdout_stream, stderr_path.open('xb') as stderr_stream:
            try:
                process = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                    stdout=stdout_stream, stderr=stderr_stream, start_new_session=True)
                record.update({'status': 'running', 'pid': process.pid,
                               'owned_session': process.pid})
                status_stream.write(json.dumps(record, indent=2) + '\n')
                status_stream.flush()
                os.fsync(status_stream.fileno())
                try:
                    process.wait(timeout=max(0, 1200-(time.monotonic()-started)))
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    record['timed_out'] = True
                    record['deadline_observed_elapsed_seconds'] = time.monotonic()-started
                    record['termination_signal'] = 'SIGKILL'
                    record['termination_scope'] = 'This launched OS process group only'
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        record['termination_process_group_already_absent'] = True
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        record['child_completion_incomplete'] = True
                    exit_code = 124
                record['child_primary_exit'] = process.returncode
                closure = finish_owned_session(process.pid)
                record['owned_session_closure'] = closure
                if not closure['owned_session_absence_verified']:
                    record['owned_session_absence_unverified'] = True
                if not closure['no_live_owned_execution_verified']:
                    record['owned_session_completion_unverified'] = True
                    if exit_code == 0:
                        exit_code = 1
            except BaseException as error:
                record['launch_or_supervision_error'] = {
                    'type': type(error).__name__, 'message': str(error)}
                if process is not None and process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        record['child_completion_incomplete'] = True
                    record['child_primary_exit'] = process.returncode
                if process is not None:
                    # An exited leader can still have owned descendants.
                    record['owned_session_closure'] = finish_owned_session(process.pid)
                exit_code = 1
            finally:
                stdout_stream.flush()
                stderr_stream.flush()
                os.fsync(stdout_stream.fileno())
                os.fsync(stderr_stream.fileno())
        record['elapsed_seconds'] = time.monotonic()-started
        record['status'] = 'completed' if record['child_primary_exit'] is not None else 'incomplete'
        # Preserve the raw negative child signal separately from our actual exit.
        exit_code = exit_code if 0 <= exit_code <= 255 else 1
        record['supervisor_exit'] = exit_code
        record['stdout'] = {'file': stdout_path.name, 'bytes': stdout_path.stat().st_size,
            'sha256': hashlib.sha256(stdout_path.read_bytes()).hexdigest()}
        record['stderr'] = {'file': stderr_path.name, 'bytes': stderr_path.stat().st_size,
            'sha256': hashlib.sha256(stderr_path.read_bytes()).hexdigest()}
        status_stream.seek(0)
        status_stream.truncate()
        status_stream.write(json.dumps(record, indent=2) + '\n')
        status_stream.flush()
        os.fsync(status_stream.fileno())
    print(json.dumps({'supervisor_exit': exit_code,
                      'child_primary_exit': record['child_primary_exit'],
                      'timed_out': record['timed_out'], 'status_file': str(status)}))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
