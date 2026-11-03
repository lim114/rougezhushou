"""Root-only serial complete320 controller. Importing is not execution."""
import argparse
import json
from pathlib import Path
import tempfile
import uuid

from full320_common import BASE, ROOT, PYTHON, bound, native, now, sha, write_new
from execution320 import execute_observed, terminal_job_record, checkpoint


def observed_step(container, name, child, deadline, outer, parent, freeze_sha, activation_sha):
    bound(parent, freeze_sha, activation_sha)
    folder = container / name; folder.mkdir()
    argv = [str(PYTHON), '-B', '-X', 'utf8', str(BASE / 'supervisor320.py'),
            '--status', str(folder / 'supervisor.json'), '--timeout', str(deadline), '--', *child]
    row = {'name': name, 'argv': argv, 'status': 'starting', 'started_at': now()}
    write_new(folder / 'step.json', row)
    observed = execute_observed(argv, folder, timeout=outer)
    terminal, details = terminal_job_record(folder, observed)
    row.update(observed=observed, **details, status='terminal' if terminal else 'uncertain_no_further_execution', finished_at=now())
    checkpoint(folder / 'step.json', row)
    if not terminal: raise RuntimeError('Owned job not closed; no later step, automatic retry or PID termination.')
    bound(parent, freeze_sha, activation_sha)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    for name in ('expected-parent-commit', 'freeze-sha256', 'activation-sha256'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    if not args.execute: raise RuntimeError('Root explicit --execute required. Preparation never starts a suite/window.')
    native(); parent = args.expected_parent_commit
    data, activation = bound(parent, args.freeze_sha256, args.activation_sha256)
    destination = Path(tempfile.gettempdir()).resolve() / ('rouge-full320-attempt2-' + uuid.uuid4().hex)
    if destination.exists() or destination.is_relative_to(ROOT): raise ValueError('Fresh owned external namespace required.')
    once = BASE / 'full320-once.json'
    write_new(once, {'section': 320, 'container': str(destination), 'root_freeze_sha256': args.freeze_sha256,
                     'automatic_retry_allowed': False, 'explicit_root_execute': True})
    destination.mkdir()
    authority = {'section': 320, 'kind': 'FULL320_ROOT_OWNED_SERIAL_FULL_EXECUTION_ATTEMPT2', 'actual_validation_attempt': 2, 'controller_fixture_pid': __import__('os').getpid(), 'root': str(ROOT),
                 'parent_commit': parent, 'root_freeze_sha256': args.freeze_sha256,
                 'activation_sha256': args.activation_sha256, 'controller_sha256': sha(Path(__file__)),
                 'created_at': now(), 'game_actions': 0, 'chat_requests': 0, 'private_state_copied': False}
    write_new(destination / 'owned-execution.json', authority)
    record = {'section': 320, 'status': 'created', 'started_at': now(), 'steps': [],
              'required_components': ['offline', 'legacy', 'legacy_typed', 'current30', 'current29', *data['p3_scripts']],
              'complete_repository_validation': False, 'available_checks_passed': None}
    ledger = destination / 'orchestration.json'; write_new(ledger, record)
    print(json.dumps({'full320_namespace': str(destination), 'passed_claimed': False}, ensure_ascii=False), flush=True)
    shared = ['--expected-parent-commit', parent, '--freeze-sha256', args.freeze_sha256, '--activation-sha256', args.activation_sha256]
    try:
        definitions = [('offline', 3600, 3690), ('legacy', 3690, 3780), ('current30', 1200, 1290), ('current29', 1200, 1290)]
        for name, deadline, outer in definitions:
            child = [str(PYTHON), '-B', '-X', 'utf8', str(BASE / 'component_child320.py'), '--mode', name,
                     '--out', str(destination / name / 'actual'), *shared]
            row = observed_step(destination, name, child, deadline, outer, parent, args.freeze_sha256, args.activation_sha256)
            record['steps'].append(row); checkpoint(ledger, record)
            if name == 'legacy':
                if row['supervisor_exit'] == row['child_primary_exit'] == 0 and row['timed_out'] is False:
                    child = [str(PYTHON), '-B', '-X', 'utf8', str(BASE / 'readback_child320.py'),
                             '--legacy-container', str(destination / 'legacy'), *shared]
                    audit = observed_step(destination, 'legacy_typed', child, 120, 210, parent, args.freeze_sha256, args.activation_sha256)
                    record['steps'].append(audit)
                else:
                    record['steps'].append({'name': 'legacy_typed', 'status': 'not_run_legacy_not_passed', 'passed': False})
                checkpoint(ledger, record)
        for name in data['p3_scripts']:
            child = [str(PYTHON), '-B', '-X', 'utf8', str(BASE / 'component_child320.py'), '--mode', name,
                     '--out', str(destination / name / 'actual'), *shared]
            row = observed_step(destination, name, child, 1200, 1290, parent, args.freeze_sha256, args.activation_sha256)
            record['steps'].append(row); checkpoint(ledger, record)
        from review_results320 import review
        result = review(destination, data, activation, parent, args.freeze_sha256)
        record.update(status='all_required_components_terminal', finished_at=now(), **result)
        checkpoint(ledger, record)
        print(json.dumps({'container': str(destination), 'all_components_terminal': True,
                          'automated_available_scope_passed': result['automated_available_scope_passed'],
                          'final_public_summary_requires_root_visual_review_and_seal': True,
                          'complete_repository_validation': False}, ensure_ascii=False), flush=True)
        return 0 if result['automated_available_scope_passed'] else 1
    except BaseException as error:
        record.update(status='aborted_no_duplicate_execution', exception={'type': type(error).__name__, 'message': str(error)})
        checkpoint(ledger, record)
        raise


if __name__ == '__main__': raise SystemExit(main())
