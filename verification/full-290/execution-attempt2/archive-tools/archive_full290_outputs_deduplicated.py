"""Seal only explicit owned290 outputs and exact pinned public dependencies.

This producer never runs a test/Qt object, reads a private state directory,
recursively copies an arbitrary tree, or declares the available suite passed.
"""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import tarfile

from full290_runtime_common import (BASE, ROOT, FREEZE, bound_bundles, native,
                                    safe_public_source, safe_supplemental_source, sha, validate_freeze, write_new)

STEPS = ('offline', 'legacy', 'current30', 'current29')
CONTROL_FILES = ('controller-process.json', 'controller-supervisor.stdout.log',
                 'controller-supervisor.stderr.log', 'supervisor.json',
                 'supervisor.json.stdout.log', 'supervisor.json.stderr.log',
                 'process.exit', 'process-exit-origin.json',
                 'independent-saved-readback-audit.json', 'readback.exit',
                 'readback.stdout.log', 'readback.stderr.log', 'readback-process.json')
PREPARATION_EVIDENCE = ('RUN_PLAN.md', 'ORCHESTRATION_NOTES.md',
                        'prepare.stdout.log', 'prepare.stderr.log', 'prepare.process.exit',
                        'create_repair_controllers.py', 'create_repair_check.py',
                        'orchestration-preparation-check-290-final.json',
                        'environment-inventory-290.json', 'scope-and-dependencies-290.json',
                        'game-window-prerequisite-290.json', 'draft-preservation-290.json',
                        'controller-adaptation-290.json', 'preparation-delta-290.json',
                        'preparation-ready-290.json',
                        'orchestration-preparation-check-290.json',
                        'orchestration-preparation-check-290-ready.json',
                        'check_preparation_290-first.py', 'check_preparation_290.py',
                        'static-check-observed.stdout.log', 'static-check-observed.stderr.log',
                        'static-check-observed.process.exit',
                        'static-check-corrected.stdout.log', 'static-check-corrected.stderr.log',
                        'static-check-corrected.process.exit',
                        'static-check-final.stdout.log', 'static-check-final.stderr.log',
                        'static-check-final.process.exit',
                        'static-check-ready.stdout.log', 'static-check-ready.stderr.log',
                        'static-check-ready.process.exit')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seal-actual-outputs', action='store_true', required=True)
    parser.add_argument('--container', type=Path, required=True)
    parser.add_argument('--expected-parent-commit', required=True)
    parser.add_argument('--allow-closed-partial', action='store_true')
    parser.add_argument('--derive-missing-process-exit', action='store_true')
    args = parser.parse_args()
    native()
    parent = args.expected_parent_commit
    frozen = validate_freeze(parent)
    bundles = bound_bundles(parent)
    source = args.container.resolve()
    if (not args.container.is_absolute() or source.is_relative_to(ROOT)
            or args.container.is_symlink() or not source.name.startswith('rouge-full290-repair-')):
        raise ValueError('Only a previously owned absolute290 namespace outside the repository can be sealed')
    own_path = source / 'owned-execution.json'
    own = json.loads(own_path.read_bytes())
    if (own.get('kind') != 'FULL290_REPAIR_ROOT_OWNED_ACTUAL_EXECUTION'
            or own.get('root') != str(ROOT) or own.get('parent_commit') != parent
            or own.get('source_freeze_sha256') != sha(FREEZE)
            or own.get('controller_sha256') != sha(BASE / 'run_full290_orchestration.py')):
        raise ValueError('Owned execution provenance does not match this exact final290 source')
    control = json.loads((source / 'orchestration.json').read_bytes())
    step_rows = control.get('steps', [])
    names = [row['name'] for row in step_rows]
    if names != list(STEPS[:len(names)]):
        raise ValueError('Execution steps must retain the mandatory ordered prefix')
    if not args.allow_closed_partial and (names != list(STEPS) or control.get('status') != 'all_four_terminal'):
        raise ValueError('Default sealing requires four actual terminal commands; do not label partial outputs complete')

    terminal_records = {}
    for name in names:
        status_path = source / name / 'supervisor.json'
        data = json.loads(status_path.read_bytes())
        if (data.get('status') != 'completed' or type(data.get('supervisor_exit')) is not int
                or type(data.get('child_primary_exit')) is not int
                or data.get('owned_handle_retained') is not True
                or data.get('owned_job_assigned') is not True
                or data.get('owned_job_no_live_execution_verified') is not True):
            raise ValueError('Never seal possibly live child/job outputs as terminal: ' + name)
        observed_path = source / name / 'controller-process.json'
        observed = json.loads(observed_path.read_bytes()) if observed_path.is_file() else {}
        observed_exit = observed.get('actual_observed_popen_exit')
        if type(observed_exit) is int and observed_exit != data['supervisor_exit']:
            raise ValueError('Genuine observed process exit disagrees with supervisor: ' + name)
        actual_exit = source / name / 'process.exit'
        if actual_exit.is_file():
            origin_path = source / name / 'process-exit-origin.json'
            origin = json.loads(origin_path.read_bytes())
            if (int(actual_exit.read_text(encoding='ascii').strip()) != data['supervisor_exit']
                    or origin.get('kind') != 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT'
                    or origin.get('derived_from_supervisor_json') is not False
                    or origin.get('process_exit_sha256') != sha(actual_exit)
                    or observed_exit != data['supervisor_exit'] or observed.get('status') != 'completed'):
                raise ValueError('Actual raw exit file/origin is not intact: ' + name)
        elif not args.derive_missing_process_exit:
            raise ValueError('Raw process.exit missing; explicit derived-input permission required: ' + name)
        terminal_records[name] = {'supervisor': data,
                                 'original_os_exit_observed': observed.get('status') == 'completed'
                                     and type(observed_exit) is int,
                                 'original_process_exit_file_present': actual_exit.is_file()}

    # Check no undeclared live activation process exists. The optional activation
    # path does not own a fixture/job and has its own actual observed Popen exit.
    activation = source / 'activation'
    if activation.exists():
        record = json.loads((activation / 'controller-process.json').read_bytes())
        if record.get('status') != 'completed' or type(record.get('actual_observed_popen_exit')) is not int:
            raise ValueError('Actual activation controller is not terminal')

    destination = ROOT / 'verification/full-290/execution-attempt2'
    if destination.exists():
        raise ValueError('Never overwrite a sealed/partial archive; retain it and review a new attempt')
    destination.mkdir(parents=True)
    manifest = {'kind': 'FULL290_ACTUAL_OUTPUT_ARCHIVE',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'producer_sha256': sha(Path(__file__)), 'source_container': str(source),
                'parent_commit': parent, 'source_freeze_sha256': sha(FREEZE),
                'actual_started_steps': names, 'all_four_started': names == list(STEPS),
                'files': {}, 'derived_readback_inputs': [],
                'available_checks_passed_claimed': False, 'complete_repository_validation_claimed': False,
                'source_tree_walk_or_private_copy_used': False,
                'status': 'archive_incomplete_do_not_claim_pass',
                'producer_adaptation': {
                    'original_frozen_producer_sha256': frozen['preparation_tools_sha256'][
                        '.cache/p3-full290-repair-prep/archive_full290_outputs.py'],
                    'change': 'Deduplicate one repeated identical preparation filename; all unique files and validation gates preserved.',
                    'original_producer_executed_and_failed_claimed': False,
                    'original_A2_controls_or_results_modified': False}}

    def copy_exact(path, relative, expected=None, boundary=None):
        """Copy one declared file, never a directory tree or symlink."""
        relative = Path(relative)
        if (relative.is_absolute() or '..' in relative.parts or path.is_symlink()
                or not path.is_file() or (boundary is not None and not path.resolve().is_relative_to(boundary.resolve()))):
            raise ValueError('Unexpected link/tree/path refused during exact-file sealing')
        before = sha(path)
        if expected is not None and before != expected:
            raise ValueError('Declared original file changed: ' + relative.as_posix())
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        if before != sha(path) or before != sha(target):
            raise ValueError('File changed while copied: ' + relative.as_posix())
        manifest['files'][relative.as_posix()] = {'sha256': before, 'bytes': target.stat().st_size,
                                                'original_file': str(path)}

    try:
        copy_exact(FREEZE, 'root-source-freeze.json', sha(FREEZE), ROOT)
        copy_exact(Path(__file__), 'archive-tools/archive_full290_outputs_deduplicated.py', sha(Path(__file__)), BASE)
        copy_exact(BASE / 'archive_full290_outputs.py', 'archive-tools/archive_full290_outputs-original.py',
                   frozen['preparation_tools_sha256']['.cache/p3-full290-repair-prep/archive_full290_outputs.py'], BASE)
        for filename in ('owned-execution.json', 'orchestration.json'):
            copy_exact(source / filename, filename, boundary=source)
        for name in names + (['activation'] if activation.exists() else []):
            folder = source / name
            for filename in CONTROL_FILES:
                path = folder / filename
                if path.is_file():
                    copy_exact(path, name + '/' + filename, boundary=folder)
            actual = folder / 'actual'
            if actual.exists():
                if actual.is_symlink() or not actual.resolve().is_relative_to(source):
                    raise ValueError('Actual output path escaped its owned namespace')
                # Existing complete fixtures use a flat actual output directory.
                # A new nested tree is a review condition, never recursively read.
                for path in sorted(actual.iterdir()):
                    if not path.is_file() or path.is_symlink() or path.suffix not in ('.json', '.log', '.png', '.gz'):
                        raise ValueError('Unexpected actual output entry requires review: ' + path.name)
                    copy_exact(path, name + '/actual/' + path.name, boundary=actual)
            if name in terminal_records and not terminal_records[name]['original_process_exit_file_present']:
                # Only this archived input is derived; the original raw namespace
                # stays untouched. This does not claim an observed original OS exit.
                exit_path = destination / name / 'process.exit'
                with exit_path.open('xb') as file:
                    file.write((str(terminal_records[name]['supervisor']['supervisor_exit']) + '\n').encode('ascii'))
                annotation = {
                    'kind': 'DERIVED_FROM_SEALED_REAL_SUPERVISOR_READBACK_INPUT',
                    'derived_from_supervisor_json': True,
                    'original_process_exit_file_present': False,
                    'original_os_exit_observed': terminal_records[name]['original_os_exit_observed'],
                    'not_an_original_raw_shell_or_popen_exit_file': True,
                    'does_not_independently_prove_original_supervisor_OS_exit': True,
                    'sealed_supervisor_sha256': sha(destination / name / 'supervisor.json'),
                    'process_exit_sha256': sha(exit_path)}
                write_new(destination / name / 'derived-process-exit-origin.json', annotation)
                manifest['derived_readback_inputs'].append({'step': name, **annotation})
                for filename in ('process.exit', 'derived-process-exit-origin.json'):
                    path = destination / name / filename
                    manifest['files'][name + '/' + filename] = {
                        'sha256': sha(path), 'bytes': path.stat().st_size,
                        'original_file': None, 'derived_input': True}
        for label, bound in bundles.items():
            folder = BASE / label
            copy_exact(folder / 'activation275.json', 'executed-tools/' + label + '/activation275.json',
                       bound['activation_sha256'], folder)
            # Every exact runtime/dependency path comes from the actual activated
            # map. There is no recursive dependency-clone walk or private copy.
            for name, expected in bound['binding']['execution_tools_sha256'].items():
                copy_exact(folder / name, 'executed-tools/' + label + '/' + name, expected, folder)
        for name, expected in frozen['preparation_tools_sha256'].items():
            copy_exact(ROOT / name, 'controller-tools/' + Path(name).name, expected, BASE)
        for name in PREPARATION_EVIDENCE:
            path = BASE / name
            if path.is_file():
                copy_exact(path, 'preparation/' + name, boundary=BASE)

        archive_path = destination / 'frozen-public-source.tar.gz'
        with tarfile.open(archive_path, 'x:gz') as archive:
            for name, expected in {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items():
                path = safe_public_source(name) if name in frozen['source_sha256'] else safe_supplemental_source(name)
                raw = path.read_bytes()
                import hashlib
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError('Frozen public source bytes changed before archival: ' + name)
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(raw))
                if sha(path) != expected:
                    raise ValueError('Frozen public source bytes changed during archival: ' + name)
        manifest['files'][archive_path.name] = {'sha256': sha(archive_path), 'bytes': archive_path.stat().st_size,
                                               'public_source_members': len(frozen['source_sha256']),
                                               'supplemental_public_source_members': len(frozen['supplemental_public_inputs_sha256']),
                                               'source_map': 'root-source-freeze.json:source_sha256'}
        validate_freeze(parent)
        bound_bundles(parent)
        annotation = {
            'kind': 'ACTUAL290_AUTHORITY_FOR_PRESERVED_HISTORICAL_RAW_LABELS',
            'actual_section': 290, 'actual_validation_attempt': 2, 'root_freeze_sha256': sha(FREEZE),
            'parent_commit': parent,
            'legacy_raw_wine_filenames_and_261_headers_preserved': True,
            'native275_filename_is_inherited_not_current_section_authority': True,
            'original_raw_labels_or_results_rewritten': False,
            'actual_native290_authority': 'Fresh root freeze, original argv, true supervisor/child/job records and new launcher closure',
            'native_Windows_historical_game_or_chat_integration_claimed': False,
            'original_readback261_label_requires_this_append_only_annotation': True,
            'no_PNG_visual_inspection_claimed': True,
            'process_exit_origins': {name: {key: val for key, val in data.items() if key != 'supervisor'}
                                     for name, data in terminal_records.items()},
            'unavailable_Linux_Wine_private_history_and_symlink_not_converted_to_pass': True}
        write_new(destination / 'label-authority.json', annotation)
        manifest['files']['label-authority.json'] = {'sha256': sha(destination / 'label-authority.json'),
                                                    'bytes': (destination / 'label-authority.json').stat().st_size,
                                                    'append_only_authority_annotation': True}
        manifest.update(status='sealed_exact_outputs_no_pass_claim',
                        required_followup=['Original unchanged full typed readback, if not already present',
                                           'Actual terminal exits, zero source drift and all stated scope totals',
                                           'Actual PNG visual inspection',
                                           'Separate full30 unavailable specialization from the actual29 pass',
                                           'Final truthful available-versus-complete summary and remote verification'])
        write_new(destination / 'archive-manifest.json', manifest)
        print(json.dumps({'sealed': True, 'archive': str(destination), 'files': len(manifest['files']),
                          'manifest_sha256': sha(destination / 'archive-manifest.json'),
                          'validation_passed_claimed': False}, ensure_ascii=False))
        return 0
    except BaseException as error:
        # Keep the partially copied original bytes as failure evidence; never
        # delete/replace them or silently reuse this archive path.
        manifest['archive_error'] = {'type': type(error).__name__, 'message': str(error)}
        write_new(destination / 'archive-incomplete.json', manifest)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
