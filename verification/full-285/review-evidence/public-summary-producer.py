"""Authorized exact public evidence supplement and truthful same-source summary.

No source, checkpoint, docs/index, private state, tests, windows or archives are
changed or reexecuted. Existing first/second archives remain byte-exact.
"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC = ROOT / 'verification/full-285'
FIRST = PUBLIC / 'execution-attempt1'
SECOND = PUBLIC / 'legacy-attempt2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def relative(path):
    return path.relative_to(ROOT).as_posix()


def write_new(path, data):
    with path.open('xb') as file:
        file.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def main():
    frozen_path = PUBLIC / 'source-freeze.json'
    frozen, frozen_sha = read(frozen_path), sha(frozen_path)
    assert frozen_sha == '65530f2914ae82e0ef2707894b294c86fa6972ba18d0433f655e0f2e8610a468'
    assert len(frozen['source_sha256']) == 1193 and len(frozen['selectors']) == 419
    assert frozen['parent_commit'] == 'f2f8ac41ee59d92e4f0851172a9a81076c461181'
    assert not (PUBLIC / 'summary.json').exists() and not (PUBLIC / 'label-correction-285.json').exists()
    evidence = PUBLIC / 'review-evidence'
    assert not evidence.exists()
    archive_pins = {}
    for folder, expected, count in ((FIRST, 'e88097f37a9c73c3de4e852a6a605b7a380848a0ad3c98310507e05fa8704005', 220),
                                    (SECOND, 'fd0c26cda8a99eeb8a4f73116c61b23fb4c06554c7f75efd2acb84f6191b864c', 38)):
        path = folder / 'archive-manifest.json'
        assert sha(path) == expected
        manifest = read(path)
        assert len(manifest['files']) == count
        for name, item in manifest['files'].items():
            file = folder / name
            assert file.is_file() and not file.is_symlink() and file.resolve().is_relative_to(folder)
            assert sha(file) == item['sha256'] and file.stat().st_size == item['bytes']
        assert sha(folder / 'root-source-freeze.json') == frozen_sha
        archive_pins[relative(path)] = expected
    for name, expected in {**frozen['source_sha256'], **frozen['preparation_tools_sha256']}.items():
        assert sha(ROOT / name) == expected
    review = read(HERE / 'combined-scope-review-native-authority-corrected.json')
    assert sha(HERE / 'combined-scope-review-native-authority-corrected.json') == 'f95020fb9c3feddf4dc5998495893e4a4c0cb3587bb87ebc7f8508a20fad9fca'
    assert len(review['checks']) == 49 and not review['failures'] and review['same_source_combined_available_scope_reviewed'] is True
    assert review['single_execution_all_green'] is False and review['root_source_freeze_sha256'] == frozen_sha
    assert review['root_formal_typed_audit_present'] is True
    offline = read(FIRST / 'offline/actual/windows-offline.json')
    assert [offline[k] for k in ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'failures', 'errors', 'unavailable_records', 'unavailable_parent_count')] == [4684, 4605, 73, 0, 0, 16, 6]
    assert offline['source_sha256'] == frozen['source_sha256'] and offline['selectors'] == frozen['selectors']
    assert offline['available_checks_passed'] is True and offline['source_drift'] == [] and offline['complete_repository_validation'] is False
    assert all(row['counted_as_passed'] is False and row['winerror'] == 1314 for row in offline['unavailable'])
    formal_path = SECOND / 'legacy/independent-saved-readback-audit.json'
    formal = read(formal_path)
    assert sha(formal_path) == review['root_formal_typed_audit_sha256'] == '16e1603d4b53cb8cb8e14b1cda50e9de30ce36731db48a06df76c5f3c9811273'
    assert formal['passed'] is True and int((SECOND / 'legacy/readback.exit').read_text()) == 0
    assert formal['complete_runtime_checks'] == 4283 and formal['saved_rows'] == 52
    assert formal['codec_exact_typed_roundtrip'] is True and formal['codec_plain_JSON_order_and_values_match'] is True
    assert formal['current_revised_assertions'] == 862 and formal['original552_maintry_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
    supervisor = read(SECOND / 'legacy/supervisor.json')
    assert supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0 and supervisor['timed_out'] is False
    assert supervisor['owned_job_no_live_execution_verified'] is True
    first_failed = read(FIRST / 'legacy/actual/native275-launcher-closure.json')
    assert first_failed['passed'] is False and first_failed['fixture_exception']['message'] == 'Escaped/nonregular artifact pin'
    ledger = read(SECOND / 'additive-dependency-ledger-attempt2.json')
    assert ledger['all_seven_copied_byte_exact'] is True and len(ledger['copied']) == 7
    assert ledger['original_source_freeze_sha256'] == frozen_sha and ledger['original_protected_bytes_changed'] is False
    old_review = read(HERE / 'pre-native-authority-correction/combined-scope-review.json')
    assert len(old_review['checks']) == 49 and len(old_review['failures']) == 2
    assert old_review['same_source_combined_available_scope_reviewed'] is False
    previous = read(ROOT / 'verification/full-275/source-freeze-reset-repair.json')
    assert len(previous['selectors']) == 408 and set(previous['selectors']) <= set(frozen['selectors'])
    assert set(previous['source_sha256']) <= set(frozen['source_sha256'])

    # Exact allowlist only: no cache walk/dependency clone/private copy.
    copies = {
        'attempt1-readback/review_actual_285.py': HERE / 'review_actual_285.py',
        'attempt1-readback/first-actual-review.process.json': HERE / 'first-actual-review.process.json',
        'attempt1-readback/first-actual-review.stdout.log': HERE / 'first-actual-review.stdout.log',
        'attempt1-readback/first-actual-review.stderr.log': HERE / 'first-actual-review.stderr.log',
        'attempt1-readback/attempt1-failure-summary.json': HERE / 'attempt1-failure-summary.json',
        'attempt1-readback/record_attempt1_failure.py': HERE / 'record_attempt1_failure.py',
        'dependency-repair/prepare_seven_original_proofs_attempt2.py': HERE / 'prepare_seven_original_proofs_attempt2.py',
        'dependency-repair/additive-dependency-ledger-attempt2.json': HERE / 'additive-dependency-ledger-attempt2.json',
        'dependency-repair/legacy-attempt2-run-plan.json': HERE / 'legacy-attempt2-run-plan.json',
        'dependency-repair/archive_legacy_attempt2.py': HERE / 'archive_legacy_attempt2.py',
        'native-authority-review-before/root-first-review.stdout.log': ROOT / '.cache/full285-combined-review.log',
        'native-authority-review-after/review_combined_scope_285.py': HERE / 'review_combined_scope_285.py',
        'native-authority-review-after/combined-scope-review.json': HERE / 'combined-scope-review-native-authority-corrected.json',
        'native-authority-review-after/actual-process.json': HERE / 'corrected-native-authority-review.process.json',
        'native-authority-review-after/stdout.log': HERE / 'corrected-native-authority-review.stdout.log',
        'native-authority-review-after/stderr.log': HERE / 'corrected-native-authority-review.stderr.log',
        'public-summary-producer.py': Path(__file__)}
    for name in ('review_combined_scope_285.py', 'combined-scope-review.json', 'first-combined-review.process.json',
                 'first-combined-review.stdout.log', 'first-combined-review.stderr.log', 'preservation.json'):
        copies['native-authority-review-before/' + name] = HERE / 'pre-native-authority-correction' / name
    evidence.mkdir()
    copy_manifest = {'kind': 'FULL285_EXACT_PUBLIC_REVIEW_EVIDENCE_SUPPLEMENT',
                     'producer_sha256': sha(Path(__file__)), 'files': {},
                     'private_state_or_game_chat_samples_copied': False,
                     'recursive_cache_or_dependency_clone_copy': False,
                     'root_first_review_exit1_reported_not_fabricated_as_raw_exit_file': True,
                     'prepared_run_plan_is_not_the_actual_attempt2_controller': True}
    for name, source in copies.items():
        assert source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(ROOT / '.cache')
        digest = sha(source)
        destination = evidence / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as src, destination.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        assert digest == sha(source) == sha(destination)
        copy_manifest['files'][name] = {'sha256': digest, 'bytes': destination.stat().st_size,
                                        'original_public_source': relative(source)}
    write_new(evidence / 'manifest.json', copy_manifest)
    images = []
    descriptions = {'wine-window-100.png': '苏苏洛测试界面', 'wine-medical-trait-100.png': '医疗阿米娅测试界面',
                    'wine-movement-reference-100.png': '固定移动地图预览', 'wine-sown-tile-control-100.png': '黍控件'}
    for name, description in descriptions.items():
        path = SECOND / 'legacy/actual' / name
        assert path.is_file()
        images.append({'file': relative(path), 'sha256': sha(path), 'bytes': path.stat().st_size,
                       'description': description, 'visual_inspection': 'Root confirmed actual individual view_image inspection; no anomalies observed.'})
    checked_at = datetime.now(timezone(timedelta(hours=8))).isoformat()
    label = {'kind': 'FULL285_APPEND_ONLY_RAW_LABEL_AND_REVIEW_CORRECTION', 'actual_after_section': 285,
             'checked_at_Beijing': checked_at, 'source_freeze_sha256': frozen_sha,
             'tested_worktree_parent_commit': frozen['parent_commit'],
             'original_raw_receipts_or_flags_rewritten': False,
             'actual_platform': 'Native Windows project Python and QPA windows; genuine current visible Win32 windows.',
             'preserved_historical_labels': {
                 'wine_filenames': 'Inherited filenames do not prove Wine/Linux execution in this batch.',
                 'native275_filenames_and_kinds': 'Original transport/bootstrap filenames, not the actual functional section.',
                 'raw_typed_audit_261_and_attempt3': 'Historical kind/section/attempt retained; actual285 authority is this frozen source plus the separate actual Legacy2 process/closure.',
                 'raw_native_windows_verified_false': 'Original Windows/history certification remains unverified. Actual current Windows is separately proved by QPA windows, installed win32gui, visible HWND constructor ledgers and native launcher closures.'},
             'actual_current_native_windows_evidence': review['current_windows_authority'],
             'original_legacy_attempt1_failure': {
                 'file': relative(FIRST / 'legacy/actual/native275-launcher-closure.json'),
                 'sha256': sha(FIRST / 'legacy/actual/native275-launcher-closure.json'),
                 'classification': 'Preparation omitted seven expected-map proof artifacts; Bridge rejected before Qt or52/4283 execution.',
                 'retained_failed_not_relabelled_passed': True},
             'additive_dependency_repair': {'ledger': relative(SECOND / 'additive-dependency-ledger-attempt2.json'),
                 'ledger_sha256': sha(SECOND / 'additive-dependency-ledger-attempt2.json'),
                 'proof_files': 7, 'original76_tool_bytes_and6_controller_bytes_unchanged': True,
                 'original1193_source_files_and419_selectors_unchanged': True},
             'reviewer_metadata_error_correction': {
                 'original_check_count': 49, 'original_false_positive_count': 2,
                 'original_report': relative(evidence / 'native-authority-review-before/combined-scope-review.json'),
                 'original_report_sha256': sha(evidence / 'native-authority-review-before/combined-scope-review.json'),
                 'incorrect_premise': 'Reviewer required the fixed raw historical native_windows_verified flag to be True.',
                 'correction': 'Keep that flag False; require independent current QPA/installed Win32/visible HWND/bootstrap SHA/closure evidence, preserving original history unknown.',
                 'corrected_report': relative(evidence / 'native-authority-review-after/combined-scope-review.json'),
                 'corrected_report_sha256': sha(evidence / 'native-authority-review-after/combined-scope-review.json'),
                 'corrected_check_count': 49, 'corrected_failures': 0, 'corrected_actual_exit': 0,
                 'no_product_or_runtime_evidence_changed_to_satisfy_review': True,
                 'parallel_second_invocation': 'Original output existed; exclusive-write FileExistsError retained separately, did not overwrite first review or imply a new product failure.'},
             'composition_not_single_all_green_execution': True,
             'formal_typed_audit_real_exit': 0, 'formal_typed_audit': relative(formal_path),
             'formal_typed_audit_sha256': sha(formal_path),
             'PNG_visual_inspection_reported_by_root': images,
             'no_Linux_Wine_original_private_game_chat_certification': True}
    write_new(PUBLIC / 'label-correction-285.json', label)
    summary = {'after_section': 285, 'kind': 'functional_section_full_validation', 'checked_at_Beijing': checked_at,
               'available_checks_passed': True, 'complete_repository_validation': False, 'scope_not_reduced': True,
               'P2_complete': False, 'single_execution_all_green': False,
               'validation_composition': {'offline': relative(FIRST / 'offline'), 'current30': relative(FIRST / 'current30'),
                                          'current29': relative(FIRST / 'current29'), 'legacy': relative(SECOND / 'legacy'),
                                          'reason': 'Reuse unchanged first offline/current results and separately repair only missing original proof dependencies before Legacy2, all bound to the same exact freeze.'},
               'native_current_windows_gui_verified': True, 'native_windows_game_chat_verified': False,
               'historical_original_Windows_verified': False,
               'actual_platform': 'Native Windows offline and isolated real visible MainWindow; current WSL/Linux/Wine unavailable.',
               'source_files': 1193, 'maintained_selectors': 419, 'all_original408_selectors_retained': True,
               'source_drift': [], 'tested_worktree_parent_commit': frozen['parent_commit'],
               'source_freeze': relative(frozen_path), 'source_freeze_sha256': frozen_sha,
               'archive_manifests_sha256': archive_pins,
               'offline_windows': {key: offline[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                                  'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'qt_shutdown', 'qt_shutdown_error')},
               'offline_count_accounting': '4684 parents =4605 passed +73 declared/historical skipped +6 unavailable parents;16 unavailable subcase records are not extra passed tests.',
               'actual_offline_process_exit': 0, 'offline_receipt': relative(FIRST / 'offline/actual/windows-offline.json'),
               'legacy_window': {'passed': True, 'actual_child_and_supervisor_exit': 0,
                   'owned_job_no_live_execution_verified': True, 'runtime_seconds': supervisor['elapsed_seconds'],
                   'runtime_check_records': 4283, 'passed_flag_records': 4281, 'metadata_records': 2,
                   'saved_states': 52, 'explicit_text_requests': 156, 'current_assertion_AST_and_order': 862,
                   'original_maintry_checks': 552, 'original_maintry_bytes_unchanged': True,
                   'original_maintry_sha256': formal['original552_maintry_sha256'], 'historical_projection_records': 42,
                   'exact_bridge_indices': formal['exact_ten_admission_indices'], 'real_empty_trace_rows': 26,
                   'typed_readback_verified': True, 'formal_typed_readback_actual_exit': 0,
                   'typed_archive_sha256': formal['compressed_archive_sha256'],
                   'receipt': relative(SECOND / 'legacy/actual/wine-ui-100.json'),
                   'closure': relative(SECOND / 'legacy/actual/native275-launcher-closure.json'),
                   'independent_saved_readback': relative(formal_path), 'readback_stdout': relative(SECOND / 'legacy/readback.stdout.log'),
                   'readback_exit_file': relative(SECOND / 'legacy/readback.exit'),
                   'actual_current_Windows_authority': 'Fresh visible real HWND/QPA Windows constructor ledger plus owned Popen/job source-bound native closure; not original historical Windows/game/chat.',
                   'inherited_wine_261_275_names_and_false_history_flags_preserved': True,
                   'PNG_visual_inspection_confirmed_by_root': True, 'PNG_visual_inspection_count': 4, 'screenshots': images},
               'current_window': {'maintained_scope': 30, 'available_original_workflows_passed': 29,
                   'actual_full30_attempt_preserved': True, 'full30_actual_child_and_supervisor_exit': 1,
                   'current29_actual_child_and_supervisor_exit': 0,
                   'symlink_specialization': 'unavailable: actual Path.symlink_to -> os.symlink raised WinError1314 before its product assertions; not passed',
                   'current29_receipt': relative(FIRST / 'current29/actual/window.json'),
                   'full30_failure_receipt': relative(FIRST / 'current30/actual/window.json'),
                   'original_assertion_AST_counts': {'current30': 31, 'current29': 25},
                   'raw_native_windows_verified_flags_preserved_false': True},
               'independent_combined_scope_review': {'checks': 49, 'failures': 0, 'actual_process_exit': 0,
                   'receipt': relative(evidence / 'native-authority-review-after/combined-scope-review.json'),
                   'receipt_sha256': sha(evidence / 'native-authority-review-after/combined-scope-review.json'),
                   'same_source_composite_not_single_all_green_execution': True},
               'original_failures_preserved': {'legacy_attempt1': relative(FIRST / 'legacy/actual/native275-launcher-closure.json'),
                   'legacy_missing_proof_summary': relative(evidence / 'attempt1-readback/attempt1-failure-summary.json'),
                   'metadata_review_first_false_positives': relative(evidence / 'native-authority-review-before/combined-scope-review.json'),
                   'metadata_review_collision_originals': relative(evidence / 'native-authority-review-before/first-combined-review.stderr.log')},
               'unavailable_scopes': ['16 actual Windows symlink prerequisite subcases across6 parents, attempted and retained; no privilege changes or surrogate links.',
                   'Current Linux/WSL/Wine unavailable; historical261 Linux/Wine receipts remain historical.',
                   'Original historical Windows/private integration including deferred095/109 samples and game/chat actions remain unverified.'],
               'label_correction': relative(PUBLIC / 'label-correction-285.json'),
               'public_review_evidence_manifest': relative(evidence / 'manifest.json'),
               'public_review_evidence_manifest_sha256': sha(evidence / 'manifest.json'),
               'current_worktree_validation_authority': True, 'goal_target_section': 285,
               'next_section286_started': False, 'next_full_validation_after': None, 'stop_after_target285': True}
    write_new(PUBLIC / 'summary.json', summary)
    for path, expected in ((FIRST / 'archive-manifest.json', archive_pins[relative(FIRST / 'archive-manifest.json')]),
                           (SECOND / 'archive-manifest.json', archive_pins[relative(SECOND / 'archive-manifest.json')])):
        assert sha(path) == expected
    assert sha(frozen_path) == frozen_sha
    print(json.dumps({'summary_sha256': sha(PUBLIC / 'summary.json'),
                      'label_correction_sha256': sha(PUBLIC / 'label-correction-285.json'),
                      'review_evidence_manifest_sha256': sha(evidence / 'manifest.json'),
                      'copied_explicit_public_files': len(copies),
                      'available_checks_passed': True, 'complete_repository_validation': False,
                      'single_execution_all_green': False, 'P2_complete': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
