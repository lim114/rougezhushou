"""Root-only exact fresh305 execution archive; no component can start here."""
import argparse
import json
from pathlib import Path
from full305_common import BASE, ROOT, FREEZE, READY_PATH, bound, public, sha, write_new, tool_pins, now

STEP_FILES = ('step.json', 'controller-process.json', 'controller-supervisor.stdout.log',
              'controller-supervisor.stderr.log', 'process.exit', 'process-exit-origin.json',
              'supervisor.json', 'supervisor.json.stdout.log', 'supervisor.json.stderr.log')
LEGACY_FILES = ('wine-ui-100.json', 'wine-ui-new-states-100.json.gz', 'full125-113-bridge-ledger.json',
                'full125-bridge-closure.json', 'full125-progress.json', 'native275-constructor-ledger.json',
                'native275-launcher-closure.json', 'recipient-false-reset-ledger.json', 'source100-guard-input.json',
                'hard-timeout-100.json', 'full305-source-closure.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='store_true'); parser.add_argument('--container', required=True, type=Path)
    parser.add_argument('--attempt-name', required=True)
    for name in ('expected-parent-commit', 'freeze-sha256', 'activation-sha256'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    if not args.archive: raise ValueError('Root explicit --archive required.')
    data, activation = bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    if args.attempt_name != 'execution-attempt1':
        raise ValueError('This reviewed one-shot controller has exactly one reviewed archive identity; no automatic retries.')
    container = args.container.resolve()
    if not args.container.is_absolute() or container.is_relative_to(ROOT) or container.is_symlink():
        raise ValueError('Exact original external owned namespace required.')
    authority = json.loads((container / 'owned-execution.json').read_bytes())
    once = json.loads((BASE / 'full305-once.json').read_bytes())
    if (Path(once['container']).resolve() != container or authority['root_freeze_sha256'] != args.freeze_sha256
            or authority['activation_sha256'] != args.activation_sha256 or authority['parent_commit'] != args.expected_parent_commit):
        raise ValueError('Wrong actual original305 namespace/freeze.')
    orchestration = json.loads((container / 'orchestration.json').read_bytes())
    # Failed terminal attempts are sealed intact. Uncertain live executions are
    # never sealed as finished; this function does not terminate any process.
    for row in orchestration['steps']:
        if row['status'].startswith('not_run_'): continue
        if row['status'] != 'terminal' or row.get('terminal_supervisor_and_job_verified') is not True:
            raise ValueError('Refuse final archive while an observed execution is uncertain/not closed.')
    target = ROOT / 'verification/full-305' / args.attempt_name
    if target.exists(): raise FileExistsError('Never overwrite any original actual execution archive.')
    target.mkdir(parents=True)
    files = {}

    def copy(source, relative, role):
        if not source.is_file() or source.is_symlink(): raise ValueError('Missing regular exact artifact: ' + str(source))
        name = Path(relative)
        if name.is_absolute() or '..' in name.parts or relative in files: raise ValueError('Unsafe/duplicate archive member.')
        destination = target / name; destination.parent.mkdir(parents=True, exist_ok=True)
        raw = source.read_bytes()
        with destination.open('xb') as stream: stream.write(raw)
        if destination.read_bytes() != raw: raise ValueError('Exact archive readback differs.')
        files[name.as_posix()] = {'sha256': sha(source), 'bytes': len(raw), 'role': role}

    for name in ('owned-execution.json', 'orchestration.json', 'automated-scope-review.json'):
        if (container / name).is_file(): copy(container / name, name, 'actual original control/observations; not regenerated')
    copy(FREEZE, 'source-freeze.json', 'root actual fresh305 source declaration')
    copy(BASE / 'activation305.json', 'activation305.json', 'root actual binding')
    copy(BASE / 'full305-once.json', 'full305-once.json', 'root one-shot namespace authority')
    copy(READY_PATH, 'execution-tools/' + READY_PATH.name, 'reviewed preparation identity')
    for name in tool_pins()['files']:
        copy(BASE / name, 'execution-tools/' + name, 'exact preparation/executed dependency; old raw labels preserved')
    for mode, value in activation['bundles'].items():
        folder = BASE / ('bound-' + mode)
        for name, expected in value['execution_tools_sha256'].items():
            if sha(folder / name) != expected: raise ValueError('Bound actual tool drift before archive.')
            copy(folder / name, 'executed-' + mode + '/' + name, 'actual source-bound complete original bundle')
        copy(folder / 'activation305.json', 'executed-' + mode + '/activation305.json', 'actual child capsule activation')
    for row in orchestration['steps']:
        if row['status'].startswith('not_run_'): continue
        name = row['name']; folder = container / name
        for entry in STEP_FILES:
            if (folder / entry).is_file(): copy(folder / entry, name + '/' + entry, 'original retained Popen / assigned ownedJob execution')
        if name == 'legacy_typed': continue
        actual = folder / 'actual'
        if not actual.is_dir(): continue
        # Only this known fixture output's flat evidence files. Never walk or
        # archive any temporary state, negative clone or dependency directory.
        for source in sorted(actual.iterdir()):
            if not source.is_file() or source.is_symlink(): continue
            entry = source.name
            allowed = (entry in LEGACY_FILES if name == 'legacy' else
                       entry in ('windows-offline.json', 'windows-offline.log', 'full305-source-closure.json') if name == 'offline' else
                       source.suffix in ('.json', '.png'))
            if name == 'legacy' and entry.startswith('wine-') and source.suffix == '.png': allowed = True
            if allowed: copy(source, name + '/actual/' + entry, 'actual public isolated fixture output; no private contents copied')
    for entry in ('independent-saved-readback-audit.json', 'full305-typed-audit-invocation.json'):
        if (container / 'legacy' / entry).is_file():
            copy(container / 'legacy' / entry, 'legacy/' + entry, 'actual unchanged original typed auditor output')
    bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    manifest = {'section': 305, 'kind': 'EXACT_FULL305_ORIGINAL_EXECUTION_ARCHIVE', 'sealed_at': now(),
        'source_freeze_sha256': args.freeze_sha256, 'activation_sha256': args.activation_sha256,
        'raw_namespace_preserved_in_original_bytes': str(container), 'files': files,
        'automated_available_scope_passed': orchestration.get('automated_available_scope_passed'),
        'final_available_checks_passed_not_claimed_by_archive': True,
        'private_or_dependency_directories_traversed_or_copied': False,
        'assigned_owned_job_closure_is_not_global_descendant_enumeration': True,
        'PNG_visual_inspection_claimed': False, 'complete_repository_validation': False}
    write_new(target / 'archive-manifest.json', manifest)
    # Verify bytes again after the manifest exists. Never recreate an exit from
    # other metadata; process.exit and its provenance above are original bytes.
    for name, expected in files.items():
        saved = target / name
        if sha(saved) != expected['sha256'] or saved.stat().st_size != expected['bytes']:
            raise ValueError('Sealed original archive readback drift.')
    bound(args.expected_parent_commit, args.freeze_sha256, args.activation_sha256)
    print(json.dumps({'archive': str(target), 'manifest_sha256': sha(target / 'archive-manifest.json'),
                      'files': len(files), 'final_PASS_claimed': False}, ensure_ascii=False))


if __name__ == '__main__': main()
