"""Root-only actual five-window supplement, not a replacement for original full scope."""
import argparse
import json
from pathlib import Path
import tempfile
import uuid

from full290_runtime_common import BASE, ROOT, FREEZE, PYTHON, bound_bundles, native, sha, validate_freeze, write_new
from run_full290_orchestration import execute_observed, terminal_job_record, checkpoint, now
from supplementary290_launcher import SCRIPTS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    args = parser.parse_args()
    native()
    parent = args.expected_parent_commit
    validate_freeze(parent)
    bound_bundles(parent)
    out = Path(tempfile.gettempdir()).resolve() / ('rouge-full290-repair-p3-' + uuid.uuid4().hex)
    if out.exists() or out.is_relative_to(ROOT):
        raise ValueError('Use a fresh owned namespace outside the repository')
    out.mkdir()
    write_new(out / 'owned-execution.json', {
        'kind': 'FULL290_REPAIR_ROOT_OWNED_P3_SUPPLEMENTARY_EXECUTION', 'root': str(ROOT),
        'parent_commit': parent, 'root_freeze_sha256': sha(FREEZE),
        'controller_sha256': sha(Path(__file__)), 'created_at': now(),
        'game_or_chat_or_private_state_used': False,
        'original_four_commands_replaced': False,
    })
    record = {'kind': 'FULL290_REPAIR_P3_FIVE_WINDOW_ORCHESTRATION', 'status': 'created',
              'started_at': now(), 'steps': [], 'required_steps': list(SCRIPTS),
              'root_freeze_sha256': sha(FREEZE), 'validation_passed_claimed': False}
    ledger = out / 'orchestration.json'
    write_new(ledger, record)
    print(json.dumps({'supplementary_execution_namespace': str(out)}, ensure_ascii=False), flush=True)
    try:
        for mode in SCRIPTS:
            validate_freeze(parent)
            bound_bundles(parent)
            folder = out / mode
            folder.mkdir()
            argv = [str(PYTHON), '-X', 'utf8', str(BASE / 'legacy/supervisor275.py'),
                    '--status', str(folder / 'supervisor.json'), '--timeout', '1800', '--',
                    str(PYTHON), '-X', 'utf8', str(BASE / 'supplementary290_launcher.py'),
                    '--mode', mode, '--out', str(folder / 'actual'),
                    '--expected-parent-commit', parent]
            row = {'name': mode, 'canonical_script': SCRIPTS[mode], 'status': 'starting', 'argv': argv}
            record['steps'].append(row)
            checkpoint(ledger, record)
            observed = execute_observed(argv, folder)
            terminal, details = terminal_job_record(folder, observed)
            row.update(observed=observed, **details, status='terminal' if terminal else 'not_terminal_or_job_unclosed')
            checkpoint(ledger, record)
            if not terminal:
                raise RuntimeError('No later/duplicate window while owned execution may remain live')
            validate_freeze(parent)
            bound_bundles(parent)
        record.update(status='all_five_terminal', completed_at=now(),
                      actual_nonzero_steps=[row['name'] for row in record['steps']
                                            if row['observed']['actual_observed_popen_exit'] != 0],
                      full_pass_requires_raw_scope_and_visual_review=True)
        checkpoint(ledger, record)
        print(json.dumps({'container': str(out), 'all_five_terminal': True,
                          'actual_nonzero_steps': record['actual_nonzero_steps'],
                          'validation_passed_claimed': False}, ensure_ascii=False), flush=True)
        return 0
    except BaseException as exc:
        record.update(status='aborted_no_duplicate_execution', exception={
            'type': type(exc).__name__, 'message': str(exc)})
        checkpoint(ledger, record)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
