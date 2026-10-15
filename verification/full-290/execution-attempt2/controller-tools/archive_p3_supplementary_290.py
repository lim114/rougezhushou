"""Root-only exact declared public output archival; no tests or GUI."""
import argparse
import json
from pathlib import Path
import shutil

from full290_runtime_common import BASE, ROOT, FREEZE, bound_bundles, native, sha, validate_freeze, write_new
from run_full290_orchestration import terminal_job_record, now
from supplementary290_launcher import SCRIPTS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seal-actual-outputs', action='store_true', required=True)
    parser.add_argument('--container', type=Path, required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    args = parser.parse_args()
    native()
    parent = args.expected_parent_commit
    validate_freeze(parent)
    bound_bundles(parent)
    source = args.container.resolve()
    if (not args.container.is_absolute() or args.container.is_symlink()
            or source.is_relative_to(ROOT) or not source.name.startswith('rouge-full290-repair-p3-')):
        raise ValueError('Only a new owned external supplementary namespace may be sealed')
    own = json.loads((source / 'owned-execution.json').read_bytes())
    if (own.get('kind') != 'FULL290_REPAIR_ROOT_OWNED_P3_SUPPLEMENTARY_EXECUTION'
            or own.get('root') != str(ROOT) or own.get('parent_commit') != parent
            or own.get('root_freeze_sha256') != sha(FREEZE)
            or own.get('controller_sha256') != sha(BASE / 'run_p3_supplementary_windows_290.py')):
        raise ValueError('Actual ownership/freeze/controller does not match')
    ledger = json.loads((source / 'orchestration.json').read_bytes())
    if (ledger.get('status') != 'all_five_terminal'
            or [r['name'] for r in ledger['steps']] != list(SCRIPTS)):
        raise ValueError('Require all five real terminal attempts, even if some failed')
    for row in ledger['steps']:
        folder = source / row['name']
        observed = json.loads((folder / 'controller-process.json').read_bytes())
        terminal, details = terminal_job_record(folder, observed)
        supervisor = json.loads((folder / 'supervisor.json').read_bytes())
        origin = json.loads((folder / 'process-exit-origin.json').read_bytes())
        if (not terminal or origin.get('derived_from_supervisor_json') is not False
                or supervisor.get('supervisor_sha256') != sha(BASE / 'legacy/supervisor275.py')
                or observed.get('argv') != row.get('argv')
                or supervisor.get('argv') != row.get('argv', [])[9:]
                or origin.get('process_exit_sha256') != sha(folder / 'process.exit')
                or int((folder / 'process.exit').read_text(encoding='ascii')) != observed['actual_observed_popen_exit']):
            raise ValueError('Actual owned terminal exit missing: ' + row['name'])
    destination = ROOT / 'verification/full-290/p3-supplementary-attempt2'
    if destination.exists():
        raise ValueError('Never overwrite a previous actual archive')
    destination.mkdir(parents=True)
    manifest = {'kind': 'FULL290_P3_SUPPLEMENTARY_EXACT_OUTPUT_ARCHIVE',
                'created_at': now(), 'source_freeze_sha256': sha(FREEZE), 'parent_commit': parent,
                'source_container': str(source), 'files': {}, 'validation_passed_claimed': False,
                'executed_supervisor_sha256': sha(BASE / 'legacy/supervisor275.py'),
                'required_primary_full_archive': 'verification/full-290/execution-attempt2',
                'original_full_four_and_52_states_replaced': False}

    def copy(path, name, boundary):
        relative = Path(name)
        if (relative.is_absolute() or '..' in relative.parts or path.is_symlink()
                or not path.is_file() or not path.resolve().is_relative_to(boundary.resolve())):
            raise ValueError('Copy must be one exact declared regular public output')
        expected = sha(path)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        if sha(path) != expected or sha(target) != expected:
            raise ValueError('Actual file changed while copied')
        manifest['files'][name] = {'sha256': expected, 'bytes': target.stat().st_size}

    for name in ('owned-execution.json', 'orchestration.json'):
        copy(source / name, name, source)
    for mode in SCRIPTS:
        folder = source / mode
        for name in ('controller-process.json', 'controller-supervisor.stdout.log',
                     'controller-supervisor.stderr.log', 'supervisor.json', 'supervisor.json.stdout.log',
                     'supervisor.json.stderr.log', 'process.exit', 'process-exit-origin.json'):
            path = folder / name
            if path.is_file():
                copy(path, mode + '/' + name, folder)
        actual = folder / 'actual'
        if actual.exists():
            if actual.is_symlink() or not actual.resolve().is_relative_to(source):
                raise ValueError('Actual namespace escaped')
            for path in sorted(actual.iterdir()):
                if not path.is_file() or path.is_symlink() or path.suffix not in ('.json', '.png', '.log'):
                    raise ValueError('Unreviewed nested/other output: ' + path.name)
                copy(path, mode + '/actual/' + path.name, actual)
    copy(FREEZE, 'root-source-freeze.json', ROOT)
    validate_freeze(parent)
    bound_bundles(parent)
    write_new(destination / 'archive-manifest.json', manifest)
    print(json.dumps({'archive': str(destination), 'files': len(manifest['files']),
                      'manifest_sha256': sha(destination / 'archive-manifest.json'),
                      'validation_passed_claimed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
