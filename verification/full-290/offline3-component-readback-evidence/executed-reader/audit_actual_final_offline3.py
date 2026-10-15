"""Independent pure readback of final offline3; never execute archived tools."""
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / 'verification/full-290'
ARCHIVE = FULL / 'offline-attempt3'
MANIFEST_SHA = '466140d8659dad24bcdcd8ef58a91ade08cd406105531347e6f4ae69ebef5305'
FREEZE_SHA = 'ad3842c95c4a4eadb6779611a337fbeb26c2682a25d6ed83945dcf7a0a8d65f7'
PREP_SHA = 'cb31c0b40cf6c51a530df369c43ea56ee63040ecb301102d832a319206975852'
ACTIVATION_SHA = '4004536750136cf95748a41f20ab8354833b6db96c12457f8e354595ba3b075b'
CACHE_REPORT = Path(__file__).resolve().parent / 'FINAL-OFFLINE3-COMPONENT-READBACK.json'
PUBLIC_REPORT = FULL / 'offline3-component-readback.json'


def fail(condition, message):
    if condition is not True:
        raise ValueError(message)


def raw(path, boundary=ROOT):
    fail(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(boundary.resolve()), 'unsafe/nonregular path: ' + str(path))
    return path.read_bytes()


def digest(value):
    return sha256(value).hexdigest()


def read(relative):
    return json.loads(raw(ARCHIVE / relative, ARCHIVE))


def main():
    fail(not CACHE_REPORT.exists() and not PUBLIC_REPORT.exists(), 'fresh readback outputs required')
    manifest_raw = raw(ARCHIVE / 'archive-manifest.json')
    fail(digest(manifest_raw) == MANIFEST_SHA, 'actual root-sealed offline archive manifest binding')
    manifest = json.loads(manifest_raw)
    fail(manifest['kind'] == 'FULL290_FINAL_A3_EXACT_SEGMENT_ARCHIVE' and manifest['mode'] == 'offline' and manifest['actual_validation_attempt'] == 3, 'actual final offline archive identity')
    fail(manifest['actual_segment_passed'] is True and manifest['actual_original_typed_passed'] is False and manifest['combined_full_pass_claimed'] is False, 'offline component, not typed/combined pass')
    fail(manifest['source_freeze_sha256'] == FREEZE_SHA and manifest['preparation_sha256'] == PREP_SHA and manifest['activation_sha256'] == ACTIVATION_SHA, 'exact final input authorities')
    fail(len(manifest['files']) == 213, 'actual sealed offline member scope')
    for name, record in manifest['files'].items():
        value = raw(ARCHIVE / name, ARCHIVE)
        fail(digest(value) == record['sha256'] and len(value) == record['bytes'], 'member hash/size: ' + name)
    final_raw = raw(ARCHIVE / 'root-source-freeze-final-A3.json')
    fail(digest(final_raw) == FREEZE_SHA == digest(raw(FULL / 'source-freeze-final-A3.json')), 'archived and actual final freeze bytes')
    final = json.loads(final_raw)
    fail(digest(raw(ARCHIVE / 'execution-tools/preparation.json')) == PREP_SHA and digest(raw(ARCHIVE / 'activation-final-A3.json')) == ACTIVATION_SHA, 'actual preparation and activation copies')
    fail(len(final['source_sha256']) == 1221 and len(final['selectors']) == 430 and len(final['supplemental_public_inputs_sha256']) == 42, 'unchanged complete maintained selector/source/supplemental scope')
    # Fresh file reads only; no production imports, selector discovery or tests.
    for scope in ('source_sha256', 'supplemental_public_inputs_sha256'):
        for name, expected in final[scope].items():
            fail(digest(raw(ROOT / name)) == expected, 'fresh source hash: ' + name)
    fail(len(final['preparation_tools_sha256']) == 18 and len(final['template_bundle_sha256']) == 84, 'complete tools and immutable templates')
    for name, expected in final['preparation_tools_sha256'].items():
        fail(digest(raw(ARCHIVE / 'execution-tools' / name)) == expected, 'archived final runtime tool: ' + name)
    for name, expected in final['template_bundle_sha256'].items():
        fail(digest(raw(ARCHIVE / 'immutable-template-bundle' / name)) == expected, 'archived immutable template: ' + name)
    original = json.loads(raw(FULL / 'source-freeze-repair.json'))
    fail(set(final['source_sha256']) == set(original['source_sha256']) and final['selectors'] == original['selectors'] and final['supplemental_public_inputs_sha256'] == original['supplemental_public_inputs_sha256'], 'A2-to-final exact paths/orderedselectors/research unchanged')
    changes = {name: {'old_sha256': original['source_sha256'][name], 'new_sha256': final['source_sha256'][name]} for name in final['source_sha256'] if original['source_sha256'][name] != final['source_sha256'][name]}
    fail(changes == final['source_transition']['approved_changed_sources'] and set(changes) == {'tests/test_enemy_sp_inheritance_reference.py', 'scripts/verify_full_available.py'} and final['source_transition']['other_full_source_paths_unchanged'] == 1219, 'only two approved nonproduction input changes')
    raw_receipt = raw(ARCHIVE / 'offline/actual/windows-offline.json')
    result = json.loads(raw_receipt)
    closure = read('offline/actual/final-A3-offline-source-closure.json')
    fail(closure['kind'] == 'FULL290_FINAL_A3_ACTUAL_OFFLINE_SOURCE_CLOSURE' and closure['actual_validation_attempt'] == 3 and closure['root_freeze_sha256'] == FREEZE_SHA, 'actual child closure identity')
    fail(closure['actual_suite_exit'] == 0 and closure['exception'] is None and closure['after_guard_exception'] is None and closure['source_drift'] == [] and closure['actual_receipt_exists'] is True, 'actual child suite terminal and fresh after-guard')
    fail(closure['actual_suite_receipt_sha256'] == digest(raw_receipt) and closure['actual_selector_list_matches_final_freeze'] is True and closure['actual_source_map_matches_final_freeze'] is True and closure['runner_verbosity'] == 2 and closure['offline_available_checks_passed'] is True, 'child receipt/selection/source binding')
    fail(result['selectors'] == final['selectors'] and result['source_sha256'] == final['source_sha256'] and result['source_drift'] == [], 'actual full ordered selector and source dictionaries')
    fail(result['platform'] == 'Windows' and result['wine_compatibility'] is False and result['verbosity'] == 2 and result['native_windows_integration_verified'] is False, 'offline Windows scope and honest integration boundary')
    fail(result['available_checks_passed'] is True and result['complete_repository_validation'] is False and result['tests_run'] == 4823 and result['tests_passed'] == 4744 and result['historical_or_declared_skips'] == 73 and result['unavailable_records'] == 16 and result['unavailable_parent_count'] == 6 and result['failures'] == result['errors'] == 0 and result['failed_cases'] == [], 'actual complete counts and failure boundary')
    fail(len(result['skips']) == 73 and len(result['unavailable']) == 16 and all(row['kind'] == 'native_symlink_privilege_prerequisite' and row['winerror'] == 1314 for row in result['unavailable']), 'all unavailable records remain actual 1314, never passed')
    fail(result['tests_run'] == result['tests_passed'] + result['historical_or_declared_skips'] + result['unavailable_parent_count'], 'unavailable parent tests distinct from subcase records')
    qt = result['qt_shutdown']
    fail(result['qt_shutdown_error'] is None and qt['application_present'] is True and qt['application_destroyed'] is True and qt['active_pool_threads_before_wait'] == 0 and qt['top_level_widgets_before_shutdown'] == 4991 and qt['valid_wrappers_after_shutdown'] == 0, 'actual Qt shutdown without wrapper/thread residue')
    log = raw(ARCHIVE / 'offline/actual/windows-offline.log').decode('utf-8')
    fail(re.search(r'Ran 4823 tests in 1958\.729s\s+OK \(skipped=73\)\s*$', log) is not None, 'actual terminal unittest log, not inferred from progress')
    supervisor = read('offline/supervisor.json')
    process = read('offline/controller-process.json')
    origin = read('offline/process-exit-origin.json')
    owned = read('owned-execution.json')
    ledger = read('orchestration.json')
    fail(owned['kind'] == ledger['kind'] == 'FULL290_FINAL_A3_SEGMENT_EXECUTION' and owned['mode'] == ledger['mode'] == 'offline' and owned['actual_validation_attempt'] == ledger['actual_validation_attempt'] == 3 and ledger['status'] == 'terminal', 'new final owned execution authority over preserved old labels')
    fail(owned['root_freeze_sha256'] == ledger['root_freeze_sha256'] == FREEZE_SHA and ledger['supervisor_sha256'] == digest(raw(ARCHIVE / 'offline/supervisor.json')), 'owned declaration/terminal supervisor SHA')
    fail(ledger['observed'] == process and process['status'] == 'completed' and process['actual_observed_popen_exit'] == 0 and process['owned_popen_retained'] is True and process['argv'] == ledger['argv'], 'retained actual controller Popen terminal')
    fail(supervisor['status'] == 'completed' and supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0 and supervisor['timed_out'] is False and supervisor['deadline_seconds'] == 3600.0 and supervisor['owned_handle_retained'] is True and supervisor['owned_job_assigned'] is True, 'actual child/supervisor0 without timeout')
    fail(supervisor['supervisor_sha256'] == final['preparation_tools_sha256']['supervisor3690.py'] and '--timeout' in process['argv'] and process['argv'][process['argv'].index('--timeout') + 1] == '3600', 'actual supervisor bytes and effective offline deadline')
    fail(supervisor['owned_job_active_processes_after_child_exit'] == 1 and supervisor['owned_descendants_still_live'] is True and supervisor['owned_job_no_live_execution_verified'] is True and ledger['owned_job_no_live_execution_verified'] is True, 'observed child residue then verified owned-job cleanup, not natural descendant exit')
    fail(origin['kind'] == 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT' and origin['actual_observed_popen_exit'] == 0 and origin['derived_from_supervisor_json'] is False and raw(ARCHIVE / 'offline/process.exit') == b'0\n' and origin['process_exit_sha256'] == digest(raw(ARCHIVE / 'offline/process.exit')), 'real returncode origin, not fabricated derived success')
    child_source = raw(ARCHIVE / 'execution-tools/offline_child.py').decode('utf-8')
    fail("'--verbosity','2'" in child_source and "runpy.run_path(str(ROOT/'scripts/verify_full_available.py'),run_name='__main__')" in child_source, 'actual bound child executes maintained runner with verbosity2')
    supervisor_source = raw(ARCHIVE / 'execution-tools/supervisor3690.py').decode('utf-8')
    fail("if accounting['ActiveProcesses']:" in supervisor_source and 'win32job.TerminateJobObject(job,125)' in supervisor_source and "record['owned_job_no_live_execution_verified']=not accounting['ActiveProcesses']" in supervisor_source, 'exact archived cleanup branch corresponding to actual fields')
    fail(digest(raw(ARCHIVE / 'archive-manifest.json')) == MANIFEST_SHA, 'sealed manifest remained unchanged')
    report = {
        'kind': 'INDEPENDENT_PURE_FINAL_OFFLINE3_COMPONENT_READBACK_NOT_TEST_EXECUTION',
        'auditor_sha256': digest(raw(Path(__file__))),
        'actual_offline_archive': ARCHIVE.relative_to(ROOT).as_posix(),
        'actual_archive_manifest_sha256': MANIFEST_SHA,
        'archive_members_sha256_and_sizes_verified': 213,
        'actual_final_freeze_sha256': FREEZE_SHA,
        'ordered_selectors': 430,
        'maintained_sources': 1221,
        'supplemental_public_sources': 42,
        'fresh_current_source_sha256_match': True,
        'actual_receipt_sha256': digest(raw_receipt),
        'actual_closure_sha256': digest(raw(ARCHIVE / 'offline/actual/final-A3-offline-source-closure.json')),
        'tests_run': 4823,
        'tests_passed': 4744,
        'historical_or_declared_skips': 73,
        'unavailable_subcase_records': 16,
        'unavailable_parent_tests': 6,
        'unavailable_winerror': 1314,
        'failures': 0,
        'errors': 0,
        'actual_qt_shutdown': qt,
        'actual_child_primary_exit': 0,
        'actual_supervisor_exit': 0,
        'actual_controller_popen_exit': 0,
        'actual_timed_out': False,
        'actual_supervisor_elapsed_seconds': supervisor['elapsed_seconds'],
        'actual_suite_elapsed_seconds_from_log': 1958.729,
        'owned_job_active_processes_after_child_exit': 1,
        'owned_descendants_still_live_at_that_observation': True,
        'subsequent_owned_job_no_live_execution_verified': True,
        'all_descendants_naturally_exited_claimed': False,
        'cleanup_interpretation': 'The primary child exited 0. One owned process was still active afterward; the exact archived supervisor branch terminates the owned job with code125 and then verifies zero active processes. This is successful owned-job cleanup, not proof that all descendants exited naturally. No descendant identity or root cause is inferred.',
        'supervisor_raw_kind_preserved': supervisor['kind'],
        'raw_old_label_is_current_execution_authority': False,
        'actual_offline_component_passed': True,
        'complete_repository_validation': False,
        'final_combined_full_pass_claimed': False,
        'tests_GUI_or_calculation_reexecuted_by_this_readback': False,
        'additional_test_count': 0,
        'private_game_chat_or_historical_windows_proof_added': False,
        'new_public_allowlist': [PUBLIC_REPORT.relative_to(ROOT).as_posix()],
    }
    encoded = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    for path in (CACHE_REPORT, PUBLIC_REPORT):
        with path.open('xb') as target:
            target.write(encoded)
        fail(raw(path) == encoded, 'readback report byte preservation')
    print(json.dumps({'public_readback': PUBLIC_REPORT.relative_to(ROOT).as_posix(), 'sha256': digest(encoded), 'archive_members_verified': 213, 'actual_offline_component_passed': True, 'final_combined_full_pass_claimed': False, 'additional_test_count': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
