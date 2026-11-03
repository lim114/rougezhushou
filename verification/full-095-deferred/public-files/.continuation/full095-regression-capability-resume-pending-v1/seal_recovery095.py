"""Root-only SOURCE seal; preserve original full095 epoch and review two adapters."""
import argparse
import ast
import json
from pathlib import Path

from binding_validation095 import bound_bytes, bound_json, digest, file_ref, require
from recovery_binding095 import REPLACED_OUTPUTS, validate_recovery_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--spec-sha256', required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--review-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest_path = here / 'public-artifacts-manifest-recovery095.json'
    manifest = json.loads(manifest_path.read_bytes())
    require(manifest['status'] == 'SOURCE_ONLY_PENDING_ACTUAL_ROOT_RECOVERY_BINDING',
            'Frozen recovery SOURCE manifest status differs')
    rows = manifest['payload_files']
    require(isinstance(rows, list) and rows and len({row['path'] for row in rows}) == len(rows),
            'Recovery SOURCE payload references must be unique and nonempty')
    for row in rows:
        require(Path(row['path']).parent == here, 'Recovery SOURCE payload must be a direct regular package member')
        bound_bytes(row)
    require({path.name for path in here.iterdir()}
            == {Path(row['path']).name for row in rows}
            | {manifest_path.name, 'handoff-recovery095.json'},
            'Recovery SOURCE package physical set differs from the frozen payload/manifest/handoff set')
    spec_data = args.spec.read_bytes()
    require(digest(spec_data) == args.spec_sha256, 'Actual root recovery spec hash differs')
    spec = json.loads(spec_data)
    review_ref = file_ref(args.review.resolve())
    require(review_ref['sha256'] == args.review_sha256, 'Actual independent recovery spec SOURCE review hash differs')
    review = bound_json(review_ref)
    pending_path = here / 'full095_context_recovery_pending.py'
    inverse_path = here / 'recovery-context-inverse095.json'
    pending = pending_path.read_bytes()
    inverse = json.loads(inverse_path.read_bytes())
    original_data = bound_bytes(inverse['original_context_reference'])
    require(digest(pending) == inverse['pending_context_sha256'], 'Pending recovery context source changed')
    recovered = pending.decode()
    for row in reversed(inverse['changes']):
        require(recovered.count(row['after']) == 1, 'Recovery source inverse must select one exact literal/body')
        recovered = recovered.replace(row['after'], row['before'], 1)
    require(recovered.encode() == original_data, 'Whole exact original context byte inverse failed')
    require(review.get('source_gate_passed') is True and review.get('runtime_pass') is False
            and review['recovery_spec_sha256'] == args.spec_sha256
            and review['source_manifest_sha256'] == digest(manifest_path.read_bytes())
            and review['pending_context_sha256'] == digest(pending)
            and review['recovery_helper_sha256'] == digest((here / 'recovery_binding095.py').read_bytes())
            and review['sealer_sha256'] == digest(Path(__file__).read_bytes()),
            'Independent SOURCE approval must bind this exact completed root spec/package/helper/context/sealer')
    output = args.output_dir.resolve()
    require(output == Path('/workspace/.continuation/full095-regression-capability-resume-final-v1')
            and not output.exists(), 'Recovery final SOURCE packet must use its declared new unused external directory')
    source_paths = [row['path'] for row in rows]
    source_paths.extend((str(manifest_path), str(here / 'handoff-recovery095.json'),
                         str(args.spec.resolve()), str(args.review.resolve())))
    support_names = ('binding_validation095.py', 'historical-classifications090.json', 'recovery_binding095.py')
    support = {name: (here / name).read_bytes() for name in support_names}
    support_refs = [{'path': str(output / name), 'bytes': len(data), 'sha256': digest(data)}
                    for name, data in support.items()]
    final_runner_path = output / 'full095_context_recovery.py'
    final_binding_path = output / 'actual-full095-source-binding.json'
    immutable_paths = source_paths + [row['path'] for row in support_refs]
    immutable_paths.extend((str(final_runner_path), str(final_binding_path)))
    original, original_context, actual = validate_recovery_inputs(spec, immutable_paths)
    plan = actual['global_output_plan']
    require(not any(Path(path).is_relative_to(output) or output.is_relative_to(Path(path))
                    for path in (*plan['canonical_paths'].values(), *plan['fresh_evidence_directories'])),
            'Recovery sealed SOURCE directory overlaps a planned output/native namespace')
    require(all(not Path(path).exists() for path in REPLACED_OUTPUTS.values())
            and not Path(plan['paths']['context_final']).exists(),
            'New recovery/retry/final sink already exists; preserve it and diagnose')
    binding = {'format_version': 2, 'section': 95,
               'status': 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS',
               'actual_original_epoch_recovery': True,
               'root_spec': original['root_spec'],
               'root_spec_reference': original['root_spec_reference'],
               'recovery_spec': spec, 'recovery_spec_reference': file_ref(args.spec.resolve()),
               'recovery_formal_source_review': review_ref,
               'source_package_input_paths': source_paths,
               'actual_inputs': actual, 'final_support_files': support_refs,
               'source_preparation_manifest': file_ref(manifest_path),
               'pending_context': file_ref(pending_path),
               'original_context_inverse': file_ref(inverse_path),
               'original_classifier_unchanged': True, 'project_calls': 0,
               'full095_execution_performed_by_sealer': False,
               'available_checks_passed': False, 'commit_or_push_performed': False}
    binding_data = (json.dumps(binding, ensure_ascii=False, indent=2) + '\n').encode()
    replacements = [
        (b'PENDING = True\n', b'PENDING = False\n'),
        (b"BOUND_BINDING_SHA256 = '__ACTUAL_RECOVERY_BINDING_SHA256_PENDING__'",
         ("BOUND_BINDING_SHA256 = '" + digest(binding_data) + "'").encode()),
    ]
    final = pending
    for before, after in replacements:
        require(final.count(before) == 1, 'Recovery seal may change only two exact binding literals')
        final = final.replace(before, after, 1)
    reverse = final
    for before, after in reversed(replacements):
        require(reverse.count(after) == 1, 'Recovery final-to-pending inverse must be unique')
        reverse = reverse.replace(after, before, 1)
    require(reverse == pending, 'Recovery final differs beyond two exact binding literals')
    ast.parse(final)
    # All source/binding/freshness checks finish before this exclusive new write.
    output.mkdir()
    for name, data in {**support, final_binding_path.name: binding_data,
                       final_runner_path.name: final}.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
    receipt = {'format_version': 2, 'section': 95,
               'status': 'PASS_SOURCE_RECOVERY_SEAL_ONLY_RUNTIME_PENDING',
               'source_binding_passed': True, 'available_checks_passed': False,
               'original_context': spec['original']['context'],
               'original_context_epoch_started_at': original_context['started_at'],
               'original_source_binding': spec['original']['binding'],
               'preserved_passed_executions': spec['preserved_passed_executions'],
               'prior_failed_execution': spec['prior_failed_execution'],
               'changed_execution_contracts': ['wine_full', 'wine_selected'],
               'changed_output_paths': REPLACED_OUTPUTS,
               'unchanged_original_binding_validator': file_ref(here / 'binding_validation095.py'),
               'pending_to_final_changes': [{'before': a.decode(), 'after': b.decode()} for a, b in replacements],
               'whole_original_context_inverse_exact': True,
               'original_classifier_byte_changes': 0,
               'runtime_executions': 0, 'project_calls': 0,
               'commit_or_push_performed': False}
    with (output / 'seal-source-recovery-receipt095.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    final_manifest = {'format_version': 1, 'section': 95,
                      'status': 'FINAL_RECOVERY_SOURCE_BOUND_RUNTIME_NOT_EXECUTED',
                      'payload_files': [file_ref(path) for path in sorted(output.iterdir())],
                      'original_source_packet': file_ref(manifest_path)}
    final_manifest_path = output / 'public-artifacts-manifest-sealed-recovery095.json'
    with final_manifest_path.open('x', encoding='utf-8') as stream:
        json.dump(final_manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
    handoff = {'format_version': 1, 'section': 95,
               'status': 'FINAL_STOPWRITE_RECOVERY_SOURCE_BOUND_RUNTIME_PENDING',
               'source_binding_passed': True, 'available_checks_passed': False,
               'context_runner': file_ref(final_runner_path),
               'source_binding': file_ref(final_binding_path), 'manifest': file_ref(final_manifest_path),
               'required_root_actions': ['independent FINAL source/spec projection review',
                   'actual full095_context_recovery.py resume with new real recovery_started_at',
                   'two fresh reviewed Wine adapter contracts; preserve unchanged already-passed original-epoch jobs',
                   'all eight real primary zero proofs and original strict fullUI/saved/visual gates',
                   'full095_context_recovery.py finish --executions ROOT_WITNESS --ui-acceptance ROOT_ACCEPTANCE'],
               'project_calls': 0, 'runtime_executions_by_sealer': 0, 'commit_or_push_performed': False}
    with (output / 'handoff-sealed-recovery095.json').open('x', encoding='utf-8') as stream:
        json.dump(handoff, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'status': handoff['status'], 'available_checks_passed': False,
                      'source_binding_passed': True, 'source_files': actual['source_files'],
                      'preserved_passed_executions': sorted(spec['preserved_passed_executions']),
                      'original_start_replayed': False, 'runtime_executions': 0,
                      'output_dir': str(output), 'commit_or_push_performed': False}))


if __name__ == '__main__':
    main()
