"""Root-only, source-only seal after actual95 focused completion/archive exists."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

from binding_validation095 import (bound_bytes, digest, file_ref, require,
                                   canonical_file, validate_actual_inputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--spec-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest_path = here / 'public-artifacts-manifest-regression095.json'
    manifest_data = manifest_path.read_bytes()
    manifest = json.loads(manifest_data)
    require(manifest['status'] == 'FINAL_PENDING_SOURCE_ONLY_NOT_FULL095_PASS',
            'Original source preparation manifest is not final')
    for row in manifest['payload_files']:
        bound_bytes(row)
    original = (here / 'originals/full_context090.py').read_bytes()
    pending = (here / 'full095_context_pending.py').read_bytes()
    inverse = json.loads((here / 'context-migration-inverse095.json').read_bytes())
    require(digest(original) == inverse['original_context_sha256']
            and digest(pending) == inverse['pending_context_sha256'],
            'Original/pending context source preservation digest differs')
    recovered = pending.decode()
    prefix = inverse['PENDING_prefix']
    require(recovered.startswith(prefix), 'PENDING early abort prefix differs')
    recovered = recovered[len(prefix):]
    for change in inverse['changes']:
        require(recovered.count(change['after']) == 1, 'Source delta inverse must be unique')
        recovered = recovered.replace(change['after'], change['before'], 1)
    require(recovered.encode() == original, 'Exact original context byte inverse failed')
    require(digest((here / 'originals/verify_full_available090.py').read_bytes())
            == inverse['original_classifier_sha256'], 'Preserved original classifier differs')
    spec_data = args.spec.read_bytes()
    require(digest(spec_data) == args.spec_sha256, 'Actual root binding spec hash differs')
    spec = json.loads(spec_data)
    source_input_paths = [row['path'] for row in manifest['payload_files']]
    source_input_paths.extend([str(manifest_path), str(here / 'final-handoff-regression095.json')])
    source_input_paths.extend(spec['immutable_root_input_paths'])
    actual = validate_actual_inputs(spec, source_input_paths + [str(args.spec.resolve())])
    require(Path(spec['ui']['console_log_path']).is_absolute(), 'Actual plannedUI console path required')
    require(not Path(spec['ui']['receipt_path']).exists(),
            'Fresh fullUI receipt already exists; do not recycle it into a new source seal')
    output = args.output_dir.resolve()
    require(output.is_relative_to(Path('/workspace/.continuation')) and output != here,
            'Final source packet must be a new external continuation directory')
    require(not output.exists(), 'Final source output must not overwrite an earlier packet')
    root_plan = actual['global_output_plan']
    require(not any(Path(path).is_relative_to(output) or output.is_relative_to(Path(path))
                    for path in (*root_plan['canonical_paths'].values(), *root_plan['fresh_evidence_directories'])),
            'Final sealed source directory overlaps an execution/review/status/native output sink')
    support = {}
    for name in ('binding_validation095.py', 'historical-classifications090.json'):
        support[name] = (here / name).read_bytes()
    support_refs = [{'path': str(output / name), 'bytes': len(data), 'sha256': digest(data)}
                    for name, data in support.items()]
    binding = {'format_version': 2, 'section': 95,
               'status': 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS',
               'root_spec': spec, 'root_spec_reference': file_ref(args.spec.resolve()),
               'source_package_input_paths': source_input_paths,
               'actual_inputs': actual, 'final_support_files': support_refs,
               'source_preparation_manifest': file_ref(manifest_path),
               'pending_context': file_ref(here / 'full095_context_pending.py'),
               'original_context_inverse': file_ref(here / 'context-migration-inverse095.json'),
               'original_classifier_unchanged': True, 'project_calls': 0,
               'full095_execution_performed': False, 'available_checks_passed': False,
               'commit_or_push_performed': False}
    binding_data = (json.dumps(binding, ensure_ascii=False, indent=2) + '\n').encode()
    replacements = [
        (b'PENDING = True\n', b'PENDING = False\n'),
        (b"BOUND_BINDING_SHA256 = '__ACTUAL_BINDING_SHA256_PENDING__'\n",
         ("BOUND_BINDING_SHA256 = '" + digest(binding_data) + "'\n").encode()),
    ]
    final = pending
    for before, after in replacements:
        require(final.count(before) == 1, 'Final seal may change only the two exact binding literals')
        final = final.replace(before, after, 1)
    reverse = final
    for before, after in reversed(replacements):
        require(reverse.count(after) == 1, 'Final binding inverse must be unique')
        reverse = reverse.replace(after, before, 1)
    require(reverse == pending, 'Final context differs beyond the two exact source bindings')
    ast.parse(final)
    # All checks above precede creation. A write failure keeps its partial packet;
    # it never becomes a completed/runtime-PASS handoff.
    output.mkdir()
    generated = {**support, 'actual-full095-source-binding.json': binding_data,
                 'full095_context_final.py': final}
    for name, data in generated.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
    seal_receipt = {'format_version': 2, 'section': 95,
                    'status': 'PASS_SOURCE_SEAL_ONLY_FULL095_RUNTIME_PENDING',
                    'source_binding_passed': True, 'available_checks_passed': False,
                    'actual_focused95_completion_bound': True,
                    'completed_chain': actual['completed_working_tree_chain'],
                    'actual_base_HEAD': actual['actual_base_HEAD'],
                    'maintained_source_files': actual['source_files'],
                    'pending_to_final_changes': [{'before': before.decode(), 'after': after.decode()}
                                                for before, after in replacements],
                    'pending_byte_inverse_exact': True,
                    'original_context_inverse_exact': True,
                    'original_classifier_byte_changes': 0,
                    'fresh_full_selected_pip_UI_execution': False,
                    'required_fresh_primary_executions': 8,
                    'physical_primary_exit_files_required': True,
                    'canonical_global_output_plan_bound': True,
                    'project_calls': 0, 'native_windows': False,
                    'commit_or_push_performed': False}
    with (output / 'seal-source-receipt095.json').open('x', encoding='utf-8') as stream:
        json.dump(seal_receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    rows = [file_ref(path) for path in sorted(output.iterdir())]
    final_manifest = {'format_version': 1, 'section': 95,
                      'status': 'FINAL_SOURCE_BINDING_RUNTIME_NOT_EXECUTED',
                      'payload_files': rows, 'payload_count': len(rows),
                      'original_source_packet': file_ref(manifest_path)}
    with (output / 'public-artifacts-manifest-sealed-regression095.json').open('x', encoding='utf-8') as stream:
        json.dump(final_manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
    handoff = {'format_version': 1, 'section': 95,
               'status': 'FINAL_STOPWRITE_SOURCE_BOUND_RUNTIME_PENDING',
               'source_binding_passed': True, 'available_checks_passed': False,
               'context_runner': file_ref(output / 'full095_context_final.py'),
               'source_binding': file_ref(output / 'actual-full095-source-binding.json'),
               'manifest': file_ref(output / 'public-artifacts-manifest-sealed-regression095.json'),
               'runtime_commands_authorized_for_root': ['full095_context_final.py start',
                   'eight fresh root-observed executions with physical exit-code files and exact argv specified by EXECUTION_CONTRACT095.md',
                   'full095_context_final.py finish --executions actual-root-primary-exits.json --ui-acceptance actual-ui-acceptance.json'],
               'project_calls': 0, 'commit_or_push_performed': False}
    with (output / 'final-handoff-sealed-regression095.json').open('x', encoding='utf-8') as stream:
        json.dump(handoff, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'status': handoff['status'], 'source_binding_passed': True,
                      'available_checks_passed': False, 'source_files': actual['source_files'],
                      'output_dir': str(output), 'runtime_executions': 0,
                      'commit_or_push_performed': False}))


if __name__ == '__main__':
    main()
