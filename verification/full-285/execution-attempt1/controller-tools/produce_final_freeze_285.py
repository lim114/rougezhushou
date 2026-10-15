"""Future root-only final285 freeze producer; preparation never invokes this."""
import argparse
from datetime import datetime, timezone
import json
from full285_runtime_common import BASE, ROOT, FREEZE, git, native, preparation_pins, runner_api_snapshot, safe_public_source, sha, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--declare-root-final285', action='store_true', required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    args = parser.parse_args()
    native()
    parent = args.expected_parent_commit
    if git('branch', '--show-current') != 'codex/p2-development' or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Root must pass the actual current development parent')
    if FREEZE.exists():
        raise ValueError('Never overwrite a previous actual freeze; retain it and prepare a new reviewed attempt')
    before = runner_api_snapshot()
    previous = json.loads((ROOT / 'verification/full-275/source-freeze-reset-repair.json').read_bytes())
    if not set(previous['selectors']) <= set(before['selectors']) or not set(previous['source_sha256']) <= set(before['source_sha256']):
        raise ValueError('Original full275 scope was removed')
    for name, expected in before['source_sha256'].items():
        if sha(safe_public_source(name)) != expected:
            raise ValueError('Maintained public source changed: ' + name)
    after = runner_api_snapshot()
    if before != after or git('rev-parse', 'HEAD') != parent:
        raise ValueError('Source, selector APIs or parent changed during declaration')
    record = {'section': 285, 'root_declared': True,
              'phase': 'final_full_available_validation_pending_actual_execution',
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'parent_commit': parent, 'branch': 'codex/p2-development',
              **before, 'preparation_tools_sha256': preparation_pins(),
              'scope_producer': 'existing verify_full_available.source_hashes plus exact main selector union',
              'current_counts_are_declaration_not_actual_tests_run': True,
              'actual_full_suite_or_window_execution_claimed': False,
              'private_state_included': False, 'goal_target_section': 285,
              'next_section286_authorized': False}
    write_new(FREEZE, record)
    print(json.dumps({'root_final285_declared': True, 'execution_started': False,
                      'parent_commit': parent, 'source_count': len(before['source_sha256']),
                      'selector_count': len(before['selectors']), 'freeze_sha256': sha(FREEZE)}))


if __name__ == '__main__':
    main()
