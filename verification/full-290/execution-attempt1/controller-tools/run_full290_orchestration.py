"""Future root-owned four-command execution. Never imported to start a fixture."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
import uuid

from full290_runtime_common import (BASE, ROOT, FREEZE, PYTHON, bound_bundles,
                                    native, sha, validate_freeze, write_new)

STEPS = ('offline', 'legacy', 'current30', 'current29')


def now():
    return datetime.now(timezone.utc).isoformat()


def checkpoint(path, record):
    """Replace only this execution's already owned mutable control record."""
    temporary = path.with_name(path.name + '.owned.tmp')
    with temporary.open('wb') as file:
        file.write((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)


def commands(out):
    supervisor = BASE / 'legacy/supervisor275.py'
    rows = []
    for name in STEPS:
        if name == 'offline':
            child = [str(PYTHON), '-X', 'utf8', str(BASE / 'legacy/offline290_launcher.py'),
                     '--root', str(ROOT), '--out', str(out / name / 'actual/windows-offline.json')]
        else:
            folder = 'legacy' if name == 'legacy' else 'current'
            child = [str(PYTHON), '-X', 'utf8', str(BASE / folder / 'launcher275.py'),
                     '--root', str(ROOT), '--out', str(out / name / 'actual'), '--mode', name]
        argv = [str(PYTHON), '-X', 'utf8', str(supervisor), '--status',
                str(out / name / 'supervisor.json'), '--timeout', '1200', '--', *child]
        rows.append((name, argv))
    return rows


def execute_observed(argv, folder, timeout=1290):
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


def observe(container):
    """Read only records; neither PID liveness guessing nor new process launch."""
    container = container.resolve()
    own = json.loads((container / 'owned-execution.json').read_bytes())
    if own.get('kind') != 'FULL290_ROOT_OWNED_ACTUAL_EXECUTION':
        raise ValueError('Not an owned290 execution namespace')
    result = {'container': str(container), 'orchestration': None, 'steps': {},
              'new_processes_started': False, 'pid_reuse_used_as_terminal_evidence': False}
    ledger = container / 'orchestration.json'
    if ledger.is_file():
        result['orchestration'] = json.loads(ledger.read_bytes())
    for name in STEPS:
        result['steps'][name] = {}
        for filename in ('controller-process.json', 'supervisor.json', 'process-exit-origin.json'):
            path = container / name / filename
            if path.is_file():
                result['steps'][name][filename] = json.loads(path.read_bytes())
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--observe', type=Path)
    parser.add_argument('--expected-parent-commit')
    parser.add_argument('--activate', action='store_true')
    args = parser.parse_args()
    if args.observe is not None:
        if args.activate:
            parser.error('Observation never activates or executes')
        observe(args.observe)
        return 0
    if not args.expected_parent_commit:
        parser.error('Execution needs the root-declared current parent')
    native()
    parent = args.expected_parent_commit
    frozen = validate_freeze(parent)
    out = Path(tempfile.gettempdir()).resolve() / ('rouge-full290-' + uuid.uuid4().hex)
    if out.is_relative_to(ROOT) or out.exists():
        raise ValueError('A unique owned temporary namespace outside the repository is required')
    out.mkdir()
    write_new(out / 'owned-execution.json', {
        'kind': 'FULL290_ROOT_OWNED_ACTUAL_EXECUTION', 'token': uuid.uuid4().hex,
        'root': str(ROOT), 'created_at': now(), 'parent_commit': parent,
        'source_freeze_sha256': sha(FREEZE), 'controller_sha256': sha(Path(__file__)),
        'scope': 'All four mandatory commands, never an available PASS summary',
        'game_operations': 0, 'chat_requests': 0, 'private_state_included': False})
    record = {'kind': 'FULL290_FOUR_COMMAND_ORCHESTRATION', 'started_at': now(),
              'parent_commit': parent, 'source_freeze_sha256': sha(FREEZE),
              'container': str(out), 'actual_source_count': len(frozen['source_sha256']),
              'actual_selector_count': len(frozen['selectors']), 'steps': [],
              'status': 'created', 'validation_passed_claimed': False,
              'all_four_required': list(STEPS), 'archive_not_yet_created': True}
    ledger = out / 'orchestration.json'
    write_new(ledger, record)
    print(json.dumps({'actual_execution_namespace': str(out), 'source_freeze_sha256': sha(FREEZE)}, ensure_ascii=False), flush=True)
    try:
        if args.activate:
            folder = out / 'activation'
            folder.mkdir()
            argv = [str(PYTHON), '-X', 'utf8', str(BASE / 'prepare_full290_window.py'),
                    '--activate', '--root-declared-freeze', str(FREEZE),
                    '--expected-parent-commit', parent]
            # Activation has no fixture/GUI and is short, but still gets a real
            # retained-process exit and raw stdout/stderr, not a fake success.
            activation = execute_observed(argv, folder, timeout=120)
            record['activation'] = activation
            checkpoint(ledger, record)
            if activation.get('actual_observed_popen_exit') != 0:
                raise RuntimeError('Actual source binding failed; preserve this namespace and do not execute fixtures')
        record['bound_bundles'] = bound_bundles(parent)
        record['status'] = 'running'
        checkpoint(ledger, record)
        for name, argv in commands(out):
            validate_freeze(parent)
            bound_bundles(parent)
            folder = out / name
            folder.mkdir()
            # Do not mkdir actual: original fixture freshness guards remain.
            current = {'name': name, 'argv': argv, 'status': 'starting'}
            record['steps'].append(current)
            checkpoint(ledger, record)
            observed = execute_observed(argv, folder)
            terminal, details = terminal_job_record(folder, observed)
            current.update(observed=observed, **details,
                           status='terminal' if terminal else 'not_terminal_or_job_unclosed')
            checkpoint(ledger, record)
            if not terminal:
                raise RuntimeError('Supervisor/job terminal evidence incomplete; no next or duplicate command')
            validate_freeze(parent)
            bound_bundles(parent)
            # Actual nonzero terminal errors remain recorded; current30 never
            # suppresses the independent complete current29 command.
        record.update(status='all_four_terminal', completed_at=now(),
                      actual_nonzero_steps=[row['name'] for row in record['steps']
                                            if row['observed']['actual_observed_popen_exit'] != 0],
                      full_available_pass_requires_independent_scope_review=True)
        checkpoint(ledger, record)
        print(json.dumps({'all_four_terminal': True, 'container': str(out),
                          'actual_nonzero_steps': record['actual_nonzero_steps'],
                          'validation_passed_claimed': False}, ensure_ascii=False), flush=True)
        # This return signifies orchestration completion, not four passing tests.
        return 0
    except BaseException as error:
        record.update(status='aborted_no_duplicate_execution', exception={
            'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()},
            validation_passed_claimed=False)
        checkpoint(ledger, record)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
