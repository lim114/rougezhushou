"""Archive a real parent-component invocation without altering source inputs."""
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
    test = Path(__file__).resolve().parent / 'test_panel_native_finalization_283.py'
    core = args.module_file.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = next(p for p in (test.parent, *test.parents) if (p / 'rouge/app.py').is_file())
    command = [sys.executable, '-X', 'utf8', str(test), '--module-file', str(core), '-v', *args.test_name]
    source_root = core.parents[1]
    manifest = source_root / 'research/p2-panel-native-finalization-283/source-manifest.json'
    raw = json.loads(manifest.read_bytes())
    pins = [manifest, *(source_root / p for p in raw['files'])]
    before = {'test': sha(test), 'core': sha(core)}
    pin_before = {str(p.relative_to(source_root)): sha(p) for p in pins}
    for name, path in [('test-source.py', test), ('core-source.py', core),
                       ('execution-runner.py', Path(__file__))]:
        (output / name).write_bytes(path.read_bytes())
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    actual = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output / 'stdout.log').write_bytes(actual.stdout)
    (output / 'stderr.log').write_bytes(actual.stderr)
    stderr = actual.stderr.decode('utf8', errors='replace')
    ran = re.search(r'Ran (\d+) tests? in ', stderr)
    failure = re.search(r'FAILED \(([^)]+)\)', stderr)
    after = {'test': sha(test), 'core': sha(core)}
    pin_after = {str(p.relative_to(source_root)): sha(p) for p in pins}
    receipt = {'kind': 'SECTION283_PARENT_INDEPENDENT_ACTUAL_CANDIDATE_INVOCATION',
               'command': command, 'cwd': str(root), 'started_utc': started, 'finished_utc': finished,
               'actual_exit_code': actual.returncode,
               'actual_tests_run': int(ran.group(1)) if ran else None,
               'raw_failure_summary': failure.group(1) if failure else None,
               'test_and_core_sha256_before': before, 'test_and_core_sha256_after': after,
               'test_and_core_unchanged': before == after,
               'source_pin_count': len(pins), 'source_pins_sha256_before': pin_before,
               'source_pins_sha256_after': pin_after, 'source_pins_unchanged': pin_before == pin_after,
               'stdout_sha256': hashlib.sha256(actual.stdout).hexdigest(),
               'stderr_sha256': hashlib.sha256(actual.stderr).hexdigest(),
               'independent_scope': 'parent main API, strict Read/Write/manager, fresh source guard',
               'numeric_dependency_authored_by_this_reviewer': True,
               'independent_numeric_reaudit_or_old_preparation_recounted': False,
               'production_or_tests_modified': False, 'native_game_execution': False,
               'game_or_chat_actions': 0, 'private_state_used': False,
               'status': 'pass' if actual.returncode == 0 else 'actual_failure'}
    (output / 'process.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt, ensure_ascii=False))
    print(stderr)
    sys.exit(actual.returncode)


if __name__ == '__main__': main()
