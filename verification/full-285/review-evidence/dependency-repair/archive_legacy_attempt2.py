"""Root-only exact additive archive for completed285 Legacy attempt2.

Never rewrite attempt1 or run a fixture/auditor. Existing76 tool bytes are
referenced from the sealed first archive; seven added proof files are separate.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.cache/full285-preparation'
FREEZE = ROOT / 'verification/full-285/source-freeze.json'
FIRST = ROOT / 'verification/full-285/execution-attempt1'
LEDGER = HERE / 'additive-dependency-ledger-attempt2.json'
CONTROLLER = ROOT / '.cache/full285-legacy2-run.py'
CONTROL_NAMES = ('controller-process.json', 'controller-supervisor.stdout.log',
                 'controller-supervisor.stderr.log', 'supervisor.json',
                 'supervisor.json.stdout.log', 'supervisor.json.stderr.log',
                 'process.exit', 'process-exit-origin.json',
                 'independent-saved-readback-audit.json', 'readback.exit',
                 'readback.stdout.log', 'readback.stderr.log', 'readback-process.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open('xb') as file:
        file.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seal-actual-legacy-attempt2', action='store_true', required=True)
    parser.add_argument('--container', required=True, type=Path)
    parser.add_argument('--expected-freeze-sha256', required=True)
    args = parser.parse_args()
    source = args.container.resolve()
    if (not args.container.is_absolute() or source.is_relative_to(ROOT)
            or args.container.is_symlink() or not source.name.startswith('rouge-full285-legacy2-')):
        raise ValueError('Only the real owned independent Legacy2 namespace is accepted')
    if sha(FREEZE) != args.expected_freeze_sha256:
        raise ValueError('Original final285 source declaration changed')
    frozen = json.loads(FREEZE.read_bytes())
    own = json.loads((source / 'owned-legacy-retry.json').read_bytes())
    terminal = json.loads((source / 'legacy-retry-terminal.json').read_bytes())
    folder = source / 'legacy'
    supervisor = json.loads((folder / 'supervisor.json').read_bytes())
    observed = json.loads((folder / 'controller-process.json').read_bytes())
    origin = json.loads((folder / 'process-exit-origin.json').read_bytes())
    raw_exit = int((folder / 'process.exit').read_text(encoding='ascii').strip())
    if (own.get('kind') != 'ROOT285_DEPENDENCY_REPAIRED_LEGACY_RETRY'
            or own['root'] != str(ROOT) or own['parent_commit'] != frozen['parent_commit']
            or own['source_freeze_sha256'] != args.expected_freeze_sha256
            or own['controller_sha256'] != sha(CONTROLLER)
            or terminal.get('terminal') is not True
            or terminal['source_freeze_sha256'] != args.expected_freeze_sha256
            or observed.get('status') != 'completed' or supervisor.get('status') != 'completed'
            or observed['actual_observed_popen_exit'] != supervisor['supervisor_exit']
            or raw_exit != supervisor['supervisor_exit']
            or supervisor.get('owned_job_no_live_execution_verified') is not True
            or supervisor.get('owned_handle_retained') is not True
            or supervisor.get('owned_job_assigned') is not True
            or origin.get('derived_from_supervisor_json') is not False
            or origin.get('process_exit_sha256') != sha(folder / 'process.exit')):
        raise ValueError('Actual source/ownership/process/job closure is not intact')
    first_manifest = FIRST / 'archive-manifest.json'
    if sha(FIRST / 'root-source-freeze.json') != args.expected_freeze_sha256:
        raise ValueError('First attempt archive belongs to another source')
    old = json.loads(first_manifest.read_bytes())
    if old.get('status') != 'sealed_exact_outputs_no_pass_claim':
        raise ValueError('Preserve and reference the already sealed original failure archive')
    ledger = json.loads(LEDGER.read_bytes())
    mapping_path = BASE / 'legacy/expected-map125.json'
    mapping = json.loads(mapping_path.read_bytes())
    if (ledger['original_source_freeze_sha256'] != args.expected_freeze_sha256
            or ledger['all_seven_copied_byte_exact'] is not True
            or ledger['original_protected_bytes_changed'] is not False
            or ledger['original_expected_map_sha256'] != sha(mapping_path)
            or own['proof_files'] != mapping['proof_files'] or len(mapping['proof_files']) != 7):
        raise ValueError('Additive proof closure is not tied to the original map')
    for label in ('legacy', 'current'):
        binding = json.loads((BASE / label / 'activation275.json').read_bytes())
        for name, expected in binding['execution_tools_sha256'].items():
            if sha(BASE / label / name) != expected:
                raise ValueError('Already pinned execution tool changed: ' + label + '/' + name)
    for name, expected in {**frozen['source_sha256'], **frozen['preparation_tools_sha256']}.items():
        if sha(ROOT / name) != expected:
            raise ValueError('Original frozen source/controller changed: ' + name)
    destination = ROOT / 'verification/full-285/legacy-attempt2'
    if destination.exists():
        raise ValueError('Never overwrite a completed or partial second archive')
    destination.mkdir()
    record = {'kind': 'FULL285_SEPARATE_LEGACY_ATTEMPT2_ADDITIVE_ARCHIVE',
              'created_at': datetime.now(timezone.utc).isoformat(),
              'producer_sha256': sha(Path(__file__)), 'source_container': str(source),
              'source_freeze_sha256': args.expected_freeze_sha256,
              'original_first_archive': FIRST.relative_to(ROOT).as_posix(),
              'original_first_archive_manifest_sha256': sha(first_manifest),
              'original_failed_legacy_not_rewritten': True,
              'not_a_single_all_green_execution': True,
              'composition': {'offline': 'execution-attempt1/offline',
                              'current30': 'execution-attempt1/current30',
                              'current29': 'execution-attempt1/current29',
                              'legacy': 'legacy-attempt2/legacy'},
              'original76_legacy_tools': 'execution-attempt1/executed-tools/legacy',
              'additional7_proofs': 'additive-bundle-files',
              'actual_child_exit': supervisor['child_primary_exit'],
              'actual_supervisor_exit': raw_exit,
              'timed_out': supervisor['timed_out'],
              'available_checks_passed_claimed': False,
              'complete_repository_validation_claimed': False,
              'files': {}, 'status': 'archive_incomplete'}

    def exact(path, relative, expected=None, boundary=None):
        relative = Path(relative)
        if (relative.is_absolute() or '..' in relative.parts or not path.is_file() or path.is_symlink()
                or (boundary is not None and not path.resolve().is_relative_to(boundary.resolve()))):
            raise ValueError('Only an exact declared regular file inside its owned base is allowed')
        digest = sha(path)
        if expected is not None and digest != expected:
            raise ValueError('Original declared bytes differ: ' + relative.as_posix())
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open('rb') as source_file, target.open('xb') as target_file:
            shutil.copyfileobj(source_file, target_file)
        if sha(path) != digest or sha(target) != digest:
            raise ValueError('File changed during exact seal')
        record['files'][relative.as_posix()] = {'sha256': digest, 'bytes': target.stat().st_size,
                                               'original_path': str(path)}

    try:
        for name in ('owned-legacy-retry.json', 'legacy-retry-terminal.json'):
            exact(source / name, name, boundary=source)
        for name in CONTROL_NAMES:
            path = folder / name
            if path.is_file():
                exact(path, 'legacy/' + name, boundary=folder)
        actual = folder / 'actual'
        if actual.is_dir() and not actual.is_symlink():
            for path in sorted(actual.iterdir()):
                if not path.is_file() or path.is_symlink() or path.suffix not in ('.json', '.gz', '.png', '.log'):
                    raise ValueError('Unexpected nonflat output; review rather than traverse')
                exact(path, 'legacy/actual/' + path.name, boundary=actual)
        exact(FREEZE, 'root-source-freeze.json', args.expected_freeze_sha256, ROOT)
        exact(LEDGER, 'additive-dependency-ledger-attempt2.json', boundary=HERE)
        exact(CONTROLLER, 'executed-controller/full285-legacy2-run.py', own['controller_sha256'], ROOT / '.cache')
        exact(HERE / 'prepare_seven_original_proofs_attempt2.py',
              'executed-controller/prepare_seven_original_proofs_attempt2.py', ledger['producer_sha256'], HERE)
        for pin in mapping['proof_files'].values():
            path = BASE / 'legacy' / pin['path']
            if path.stat().st_size != pin['bytes']:
                raise ValueError('Original proof length changed')
            exact(path, 'additive-bundle-files/' + pin['path'], pin['sha256'], BASE / 'legacy')
        exact(mapping_path, 'original-map/expected-map125.json', ledger['original_expected_map_sha256'], BASE / 'legacy')
        if sha(first_manifest) != record['original_first_archive_manifest_sha256']:
            raise ValueError('Never rewrite the sealed first attempt while appending the second')
        record['status'] = 'sealed_exact_additive_files_no_pass_claim'
        write_new(destination / 'archive-manifest.json', record)
        print(json.dumps({'sealed': True, 'archive': str(destination), 'files': len(record['files']),
                          'manifest_sha256': sha(destination / 'archive-manifest.json'),
                          'not_single_all_green_execution': True, 'validation_passed_claimed': False}, ensure_ascii=False))
        return 0
    except BaseException as error:
        record['archive_error'] = {'type': type(error).__name__, 'message': str(error)}
        write_new(destination / 'archive-incomplete.json', record)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
