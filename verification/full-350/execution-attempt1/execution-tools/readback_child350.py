"""Invoke the unchanged original complete typed auditor after genuine legacy0."""
import argparse
import json
from pathlib import Path
import runpy
import sys
from full350_common import BASE, ROOT, FREEZE, bound, sha, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-container', type=Path, required=True)
    for name in ('expected-parent-commit', 'freeze-sha256', 'activation-sha256'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    data, activation = bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    container = args.legacy_container.resolve()
    if not container.is_absolute() or container.is_relative_to(ROOT) or container.name != 'legacy':
        raise ValueError('Actual owned legacy step directory required.')
    process = json.loads((container / 'controller-process.json').read_bytes())
    supervisor = json.loads((container / 'supervisor.json').read_bytes())
    if (process.get('status') != 'completed' or process.get('actual_observed_popen_exit') != 0
            or supervisor.get('child_primary_exit') != 0 or supervisor.get('supervisor_exit') != 0
            or supervisor.get('timed_out') is not False or supervisor.get('owned_job_no_live_execution_verified') is not True):
        raise ValueError('No typed readback without a complete actual successful closed legacy execution.')
    script = BASE / 'bound-legacy/audit_full261_saved_readback.py'
    if sha(script) != data['original_typed_auditor_sha256']:
        raise ValueError('Original complete typed auditor source changed.')
    argv = [str(script), '--root', str(ROOT), '--container', str(container),
            '--bundle', str(BASE / 'bound-legacy'), '--freeze', str(FREEZE)]
    sys.argv = argv
    code = 0
    try: runpy.run_path(str(script), run_name='__main__')
    except SystemExit as event: code = event.code if type(event.code) is int else 1
    bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    raw_path = container / 'independent-saved-readback-audit.json'
    raw = json.loads(raw_path.read_bytes()) if raw_path.is_file() else None
    passed = code == 0 and raw is not None and raw.get('passed') is True
    write_new(container / 'full350-typed-audit-invocation.json', {'section': 350, 'kind': 'ORIGINAL_COMPLETE_TYPED_AUDITOR_ACTUAL_INVOCATION',
        'argv': argv, 'actual_auditor_exit': code, 'original_source_sha256': sha(script),
        'actual_audit_sha256': sha(raw_path) if raw is not None else None,
        'original_raw_labels_preserved': True, 'passed': passed, 'root_freeze_sha256': args.freeze_sha256})
    return 0 if passed else code if code else 1


if __name__ == '__main__': raise SystemExit(main())
