"""Actual readback of legacy4 only. Does not run the final builder or any GUI."""
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / 'verification/full-290'
FOLDER = FULL / 'legacy-retry-attempt4'
BUILDER_SHA = 'ecd97b6c11a4e4721ea2a3d55f2f702134951b14586a643260626e0ea1055f2c'
MANIFEST_SHA = 'f307d8b47ea246c0983853b78b60cbd14246f68c0766b688d64cf242aaac5929'
REVIEW = ROOT / 'verification/sections/290-preparation/root-final-A3-legacy-visual-review.json'
REVIEW_SHA = '2f897d81609e65473d033e718e703c9c967128bb50a592308b6c8bea3d024742'


def main():
    producer = HERE / 'build_final_A3_summary_candidate.py'
    if sha256(producer.read_bytes()).hexdigest() != BUILDER_SHA:
        raise ValueError('Root-reviewed final reader bytes changed')
    import importlib.util
    spec = importlib.util.spec_from_file_location('_component_only_final_reader', producer)
    api = importlib.util.module_from_spec(spec)
    exec(compile(producer.read_bytes(), str(producer), 'exec'), api.__dict__)
    b = api.fresh_module(HERE / 'build_summary_candidate.py', '_component_only_safe_helpers', api.OLD_HELPERS_SHA)
    q = b.require
    q(b.sha(FOLDER / 'archive-manifest.json') == MANIFEST_SHA, 'actual root-sealed legacy4 manifest')
    final, old, meta, activation = api.source_contract(b)
    folder, manifest, supervisor = api.final_archive(b, 'legacy', final, meta, activation)
    q(folder == FOLDER and manifest['actual_legacy_execution_ordinal'] == 4, 'this actual legacy4 only')
    rsup, robs = api.terminal(b, folder / 'readback', 120, meta['new_tools_sha256']['supervisor3690.py'])
    rledger = b.read(folder / 'readback/readback-orchestration.json')
    q(rledger['status'] == 'terminal' and rledger.get('exception') is None
      and rledger['typed_available_passed'] is True and rledger['argv'] == robs['argv'], 'actual independent typed job0')
    argv = rsup['argv']
    q(Path(argv[3]).name == 'audit_full261_saved_readback.py'
      and Path(argv[argv.index('--freeze') + 1]).resolve() == api.FINAL
      and Path(argv[argv.index('--container') + 1]).resolve() == Path(manifest['source_container']) / 'legacy'
      and Path(argv[argv.index('--bundle') + 1]).name == 'bound-legacy', 'original auditor bound to actual final legacy4 inputs')
    auditor = folder / 'executed-legacy-bundle/audit_full261_saved_readback.py'
    q(b.sha(auditor) == b.sha(FULL / 'execution-attempt2/executed-tools/legacy/audit_full261_saved_readback.py')
      == b.sha(ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools/audit_full261_saved_readback.py'), 'whole original typed auditor byte identical')
    native_closure = b.native_window(folder / 'legacy', True, api.FINAL_SHA)
    legacy = b.read(folder / 'legacy/actual/wine-ui-100.json')
    typed = b.read(folder / 'legacy/independent-saved-readback-audit.json')
    q(legacy['passed'] is True and legacy['complete_ui_validation'] is True
      and legacy['source_drift'] == legacy['source_additional_drift'] == []
      and legacy['source_sha256'] == legacy['source_sha256_after'] == final['legacy_native_source_sha256']
      and legacy['source_additional_sha256'] == legacy['source_additional_sha256_after'] == final['legacy_source_additional_sha256']
      and legacy['new_explicit_damage_button_requests090'] == 52 and legacy['new_explicit_three_text_requests090'] == 156,
      'actual full public legacy scope and exact native/additional sources')
    q(len(legacy['checks']) == legacy['total_actual_checks'] == 4283
      and sum(row.get('passed') is True for row in legacy['checks']) == 4281
      and sum(row.get('passed') is False for row in legacy['checks']) == 0,
      '4281 passed flags plus two metadata records; no false flags or invented extra checks')
    q(typed['passed'] is True and typed['timeout'] is False and typed['source_and_additional_drift'] == []
      and typed['process_exit'] == typed['child_primary_exit'] == typed['supervisor_exit'] == 0
      and typed['complete_runtime_checks'] == 4283 and typed['passed_flag_records'] == 4281 and typed['metadata_records'] == 2
      and typed['current_revised_assertions'] == 862 and typed['original_assertions_outside_two_helpers'] == 807
      and typed['original552_maintry_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
      and typed['saved_rows'] == len(typed['rows']) == 52
      and [row['index'] for row in typed['rows']] == list(range(52)) and typed['row_sections'] == {'86': 44, '88': 8}
      and typed['exact_ten_admission_indices'] == api.INDICES
      and typed['exact_ten_identity_types_input_and_full_row_hash_match'] is True
      and len(legacy['saved89_actual_window_consumer_records090']) == 10
      and typed['readonly_trace_empty_rows_not_invented'] == typed['readonly_trace_variants_preserved']['[]'] == 26
      and sum(typed['readonly_trace_variants_preserved'].values()) == 52
      and typed['codec_exact_typed_roundtrip'] is True and typed['codec_plain_JSON_order_and_values_match'] is True
      and typed['archive_declared_hash_and_size_match'] is True,
      'all actual original typed52/862/552/42+10/26 scope and ordered row identities')
    q(typed['maintained_source_count'] == 1221 and typed['additional_source_count'] == 86
      and typed['root_freeze_common_source_count'] == 1220 and typed['root_freeze_CORE_protected_by_additional'] is True
      and typed['guard_extra_source_preserved'] == 'tests/offline_scope_retirement.py'
      and typed['native_windows_verified'] is False and typed['game_actions'] == typed['chat_requests'] == 0
      and typed['PNG_visual_inspection_claimed_by_this_readback'] is False,
      'original raw history/private/game limitations preserved; current native authority stays separate')
    q(rledger['actual_audit_receipt_sha256'] == b.sha(folder / 'legacy/independent-saved-readback-audit.json'), 'actual readback ledger binds this complete receipt')
    state = legacy['new_state_archive090']
    archive = b.safe_child(folder / 'legacy/actual', state['file'])
    q(b.sha(archive) == state['sha256'] == typed['compressed_archive_sha256']
      and archive.stat().st_size == state['bytes'] and state['records'] == 52, 'exact actual newly saved typed-state archive')
    decoded = sha256(); decoded_bytes = 0
    with gzip.open(archive, 'rb') as stream:
        while chunk := stream.read(1024 * 1024):
            decoded.update(chunk); decoded_bytes += len(chunk)
    q(decoded.hexdigest() == state['decoded_sha256'] == typed['decoded_archive_sha256']
      and decoded_bytes == state['decoded_bytes'], 'streamed decoded bytes/hash match original typed proof, without reexecuting model')
    q(b.sha(REVIEW) == REVIEW_SHA, 'actual root manual visual review exact bytes')
    review = b.read(REVIEW)
    q(review['kind'] == 'root_manual_visual_review_not_test_execution' and review['validation_segment'] == 'legacy'
      and review['actual_legacy_execution_ordinal'] == 4 and review['source_freeze_sha256'] == api.FINAL_SHA
      and review['all_images_accepted'] is True and review['full_validation_pass_claimed'] is False,
      'root explicitly accepted actual four PNGs, never inferred from nonempty text')
    pngs = {name: value['sha256'] for name, value in manifest['files'].items()
        if name.startswith('legacy/actual/') and name.endswith('.png')}
    q(len(pngs) == len(review['images']) == 4 and {row['relative_path'] for row in review['images']} == set(pngs), 'all exact actual final legacy PNGs')
    for image in review['images']:
        q(image['acceptable'] is True and image['sha256'] == pngs[image['relative_path']]
          == b.sha(b.safe_child(folder, image['relative_path']))
          and isinstance(image['review'], str) and bool(image['review'].strip()), 'each root manual image accepted and SHA correct')
    q(api.source_contract(b) == (final, old, meta, activation)
      and b.sha(FOLDER / 'archive-manifest.json') == MANIFEST_SHA, 'source and sealed output unchanged during pure readback')
    report = {'kind': 'FINAL_A3_LEGACY4_COMPONENT_READBACK_NOT_FINAL_FULL_SUMMARY',
        'actual_component_readback_passed': True, 'actual_legacy_execution_ordinal': 4,
        'source_freeze_sha256': api.FINAL_SHA, 'actual_segment_archive_manifest_sha256': MANIFEST_SHA,
        'actual_archived_files_verified': len(manifest['files']),
        'actual_legacy_child_and_supervisor_exit': 0, 'actual_original_typed_child_and_supervisor_exit': 0,
        'actual_legacy_runtime_seconds': supervisor['elapsed_seconds'], 'actual_typed_runtime_seconds': rsup['elapsed_seconds'],
        'legacy_deadline_seconds': supervisor['deadline_seconds'], 'typed_deadline_seconds': rsup['deadline_seconds'],
        'no_timeout_and_owned_jobs_closed': True,
        'records': {'total': 4283, 'passed_flag_records': 4281, 'metadata_records': 2, 'saved_typed_rows': 52,
            'current_assert_AST': 862, 'original_maintry_assertions': 552,
            'original_maintry_sha256': typed['original552_maintry_sha256'], 'historical_projection_rows': 42,
            'exact_admission_indices': api.INDICES, 'real_empty_trace_rows': 26, 'explicit_damage_requests': 52, 'explicit_text_requests': 156},
        'actual_legacy_native_sources': 1221, 'actual_legacy_additional_sources': 86, 'source_drift': [],
        'current_native_constructor_closure_verified': native_closure['actual_current_native_windows_window_verified'],
        'original_historical_native_windows_flag_preserved_false': True,
        'typed_archive': {'file': b.relative(archive), 'compressed_sha256': b.sha(archive),
            'decoded_sha256': decoded.hexdigest(), 'decoded_bytes': decoded_bytes},
        'root_actual_visual_review': {'path': b.relative(REVIEW), 'sha256': REVIEW_SHA,
            'image_count': 4, 'all_explicitly_acceptable': True, 'independent_readback_made_visual_judgment': False},
        'offline3_not_checked_or_claimed_here': True, 'final_full_available_checks_passed_claimed': False,
        'complete_repository_validation_claimed': False, 'P2_complete_claimed': False,
        'tests_or_new_GUI_or_game_chat_or_private_state_operation_performed': False,
        'producer_sha256': b.sha(Path(__file__)), 'final_builder_main_called': False,
        'readback_is_not_new_test_count_or_calculation_run': True}
    raw = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    cache_path = HERE / 'FINAL-LEGACY4-COMPONENT-READBACK.json'
    public_path = FULL / 'legacy4-component-readback.json'
    q(not cache_path.exists() and not public_path.exists(), 'fresh append-only component readback destinations')
    with cache_path.open('xb') as stream: stream.write(raw)
    with public_path.open('xb') as stream: stream.write(raw)
    print(json.dumps({'public_readback': b.relative(public_path), 'sha256': b.sha(public_path),
        'archive_members_verified': len(manifest['files']), 'actual_component_passed': True,
        'final_full_pass_claimed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
