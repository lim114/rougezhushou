"""Archive a real isolated candidate invocation without changing its module."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--test-name', action='append', default=[])
    args = parser.parse_args()
    test = Path(__file__).resolve().parent / 'test_skill_data_cost_consensus_independent_281.py'
    core = args.module_file.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = next(p for p in (test.parent, *test.parents) if (p / 'rouge/app.py').is_file())
    command = [sys.executable, '-X', 'utf8', str(test), '--module-file', str(core), '-v']
    command.extend(args.test_name)
    before = {'test': sha(test), 'core': sha(core)}
    (output / 'test-source.py').write_bytes(test.read_bytes())
    (output / 'core-source.py').write_bytes(core.read_bytes())
    (output / 'execution-runner.py').write_bytes(Path(__file__).read_bytes())
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output / 'stdout.log').write_bytes(result.stdout)
    (output / 'stderr.log').write_bytes(result.stderr)
    stderr = result.stderr.decode('utf-8', errors='replace')
    ran = re.search(r'Ran (\d+) tests? in ', stderr)
    failure = re.search(r'FAILED \(([^)]+)\)', stderr)
    after = {'test': sha(test), 'core': sha(core)}
    receipt = {'kind': 'SECTION281_INDEPENDENT_REAL_CANDIDATE_TEST_INVOCATION',
        'command': command, 'cwd': str(root), 'started_utc': start, 'finished_utc': end,
        'actual_exit_code': result.returncode,
        'actual_tests_run': int(ran.group(1)) if ran else None,
        'raw_failure_summary': failure.group(1) if failure else None,
        'test_and_core_sha256_before': before, 'test_and_core_sha256_after': after,
        'test_and_core_unchanged': before == after,
        'stdout_sha256': sha(output / 'stdout.log'),
        'stderr_sha256': sha(output / 'stderr.log'),
        'production_or_tests_modified': False,
        'native_game_execution': False, 'game_or_chat_actions': 0,
        'private_state_used': False,
        'status': 'pass' if result.returncode == 0 and ran and before == after else 'failed_or_incomplete'}
    (output / 'process.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'receipt': str(output / 'process.json'), 'actual_exit_code': result.returncode,
                      'actual_tests_run': receipt['actual_tests_run'],
                      'raw_failure_summary': receipt['raw_failure_summary'],
                      'test_and_core_unchanged': before == after}, ensure_ascii=False))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
