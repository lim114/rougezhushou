"""CACHE-only final component readback. Root must explicitly invoke after PASS.

No suite, GUI, freeze, state, chat or publication operation is performed. All
actual processes/archives/reviews must already exist; missing means refusal.
"""
import argparse
import ast
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / 'verification/full-290'
FINAL = FULL / 'source-freeze-final-A3.json'
FINAL_SHA = 'ad3842c95c4a4eadb6779611a337fbeb26c2682a25d6ed83945dcf7a0a8d65f7'
PREPARATION_SHA = 'cb31c0b40cf6c51a530df369c43ea56ee63040ecb301102d832a319206975852'
ACTIVATION_SHA = '4004536750136cf95748a41f20ab8354833b6db96c12457f8e354595ba3b075b'
A2_SHA = '75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'
OLD_HELPERS_SHA = 'c4cd99c2b2a83a42c07c7eee94d40faf36536a88ddcf1f67c30b49f5b8cedcd5'
CHANGES = {
    'tests/test_enemy_sp_inheritance_reference.py': {
        'old_sha256': '3523d3c99033412fd130994f9ab12e9e35faf663ed18eea35037a661cedda550',
        'new_sha256': '0eb99b4d079a945f6254f55a9a2cbadffc8d6d408aa24889dc9f0de8f13eedf4'},
    'scripts/verify_full_available.py': {
        'old_sha256': '857339d08274515133d0a26c46c5e3c74d9dff494449f1e3c6358fc1d8b8729d',
        'new_sha256': 'bb66e405fba57e880d5aa017d4fcd56dc61f697da85a82a67fbf9c8e43810a6a'}}
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]


def fresh_module(path, name, expected=None):
    raw = path.read_bytes()
    if expected is not None and sha256(raw).hexdigest() != expected:
        raise ValueError('Prepared read-only helper bytes changed')
    result = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, path))
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def verify_members(b, folder, manifest):
    for name, record in manifest['files'].items():
        path = b.safe_child(folder, name)
        b.require(b.sha(path) == record['sha256'] and path.stat().st_size == record['bytes'], 'exact archive bytes: ' + name)


def source_contract(b):
    b.require(b.sha(FINAL) == FINAL_SHA, 'actual final A3 input declaration')
    final = b.read(FINAL)
    old = b.read(FULL / 'source-freeze-repair.json')
    b.require(b.sha(FULL / 'source-freeze-repair.json') == A2_SHA and final['actual_validation_attempt'] == 3
        and final['root_declared'] is True and final['section'] == 290
        and final['preparation_sha256'] == PREPARATION_SHA and final['prior_attempt_freeze_sha256'] == A2_SHA,
        'distinct exact finalA3 and historicalA2 source authorities')
    b.require(len(final['source_sha256']) == len(old['source_sha256']) == 1221
        and set(final['source_sha256']) == set(old['source_sha256'])
        and final['selectors'] == old['selectors'] and len(final['selectors']) == 430
        and final['supplemental_public_inputs_sha256'] == old['supplemental_public_inputs_sha256']
        and len(final['supplemental_public_inputs_sha256']) == 42, 'complete1221/430 ordered/42 unchanged scope')
    changes = {n: {'old_sha256': old['source_sha256'][n], 'new_sha256': final['source_sha256'][n]}
        for n in old['source_sha256'] if old['source_sha256'][n] != final['source_sha256'][n]}
    b.require(changes == CHANGES == final['source_transition']['approved_changed_sources']
        and final['source_transition']['other_full_source_paths_unchanged'] == 1219,
        'exact two nonproduction source changes, not an only-test claim')
    with tarfile.open(FULL / 'execution-attempt2/frozen-public-source.tar.gz', 'r:gz') as archive:
        originals = {}
        for name in CHANGES:
            member = archive.getmember(name)
            b.require(member.isfile() and not member.issym() and not member.islnk(), 'regular original source member')
            with archive.extractfile(member) as stream:
                originals[name] = stream.read()
            b.require(sha256(originals[name]).hexdigest() == CHANGES[name]['old_sha256'], 'exact original source bytes')
    test = 'tests/test_enemy_sp_inheritance_reference.py'
    old_test = originals[test]
    expected_test = old_test.replace("self.assertIn('独立构造',text)".encode(),
        "self.assertIn('本关使用专属敌人资料',text)\n        self.assertIn('独立构造',enemy_text(entry,technical=True))".encode())
    b.require(old_test.count("self.assertIn('独立构造',text)".encode()) == 1
        and (ROOT / test).read_bytes() == expected_test, 'one player label replacement and retained technical assertion')
    runner = 'scripts/verify_full_available.py'
    old_runner = originals[runner]
    before = b"'platform': platform.system(), 'wine_compatibility': args.wine"
    after = b"'platform': ('Windows' if sys.platform == 'win32' else platform.system()), 'wine_compatibility': args.wine"
    b.require(old_runner.count(before) == 1 and (ROOT / runner).read_bytes() == old_runner.replace(before, after),
        'only Windows final receipt platform short-circuit; no selector/result/cleanup change')
    def available_result(raw):
        return ast.dump(next(n for n in ast.parse(raw).body if isinstance(n, ast.ClassDef) and n.name == 'AvailableResult'), include_attributes=False)
    b.require(available_result(old_runner) == available_result((ROOT / runner).read_bytes()), 'whole AvailableResult AST unchanged')
    old_native = b.read(FULL / 'execution-attempt2/executed-tools/legacy/current-source-guard.json')
    expected_native = dict(old_native['source_sha256'])
    expected_native.update({name: value['new_sha256'] for name, value in CHANGES.items()})
    b.require(final['legacy_native_source_sha256'] == expected_native and len(expected_native) == 1221
        and final['legacy_source_additional_sha256'] == old_native['source_additional_sha256']
        and len(final['legacy_source_additional_sha256']) == 86,
        'full distinct legacy native1221 and additional86 preserved, including offline_scope_retirement')
    for name, expected in {**final['source_sha256'], **final['supplemental_public_inputs_sha256'],
            **expected_native, **final['legacy_source_additional_sha256']}.items():
        b.require(b.sha(b.safe_child(ROOT, name)) == expected, 'fresh final public input: ' + name)
    base = ROOT / '.cache/p3-full290-final-A3-prep'
    b.require(b.sha(base / 'preparation.json') == PREPARATION_SHA
        and b.sha(base / 'activation-final-A3.json') == ACTIVATION_SHA, 'actual final prepared and bound runtime')
    meta, activation = b.read(base / 'preparation.json'), b.read(base / 'activation-final-A3.json')
    b.require(final['preparation_tools_sha256'] == meta['new_tools_sha256'] and len(meta['new_tools_sha256']) == 18
        and final['template_bundle_sha256'] == meta['template_bundle_sha256'] and len(meta['template_bundle_sha256']) == 84,
        'all18 control and84 immutable template paths preserved')
    for name, expected in meta['new_tools_sha256'].items():
        b.require(b.sha(b.safe_child(base, name)) == expected, 'actual final control bytes')
    for name, expected in meta['template_bundle_sha256'].items():
        b.require(b.sha(b.safe_child(base / 'template-legacy', name)) == expected, 'fresh immutable84 template bytes')
    for name, expected in meta['prior_public_tool_sha256'].items():
        b.require(b.sha(b.safe_child(ROOT, name)) == expected, 'prior actually executed public controls remain original')
    for name, expected in activation['execution_tools_sha256'].items():
        b.require(b.sha(b.safe_child(base / 'bound-legacy', name)) == expected, 'actual bound legacy84 bytes')
    b.require(len(activation['execution_tools_sha256']) == 84 and activation['root_freeze_sha256'] == FINAL_SHA
        and activation['preparation_sha256'] == PREPARATION_SHA and activation['actual_legacy_execution_ordinal'] == 4
        and b.sha(base / 'bound-legacy/activation-final-A3.json') == ACTIVATION_SHA,
        'actual final native binding')
    return final, old, meta, activation


def terminal(b, folder, deadline, supervisor_sha):
    sup, observed, origin = (b.read(folder / name) for name in
        ('supervisor.json', 'controller-process.json', 'process-exit-origin.json'))
    b.require(sup['status'] == observed['status'] == 'completed'
        and sup['child_primary_exit'] == sup['supervisor_exit'] == observed['actual_observed_popen_exit']
            == int(b.regular(folder / 'process.exit').read_text(encoding='ascii')) == 0
        and sup['timed_out'] is False and sup['deadline_seconds'] == deadline and sup['supervisor_sha256'] == supervisor_sha
        and sup['owned_handle_retained'] is True and sup['owned_job_assigned'] is True
        and sup['owned_job_no_live_execution_verified'] is True and origin['derived_from_supervisor_json'] is False
        and origin['actual_observed_popen_exit'] == 0 and origin['process_exit_sha256'] == b.sha(folder / 'process.exit')
        and sup['argv'] == observed['argv'][9:], 'actual retained Popen/job/exit0')
    return sup, observed


def final_archive(b, mode, final, meta, activation):
    folder = FULL / ('offline-attempt3' if mode == 'offline' else 'legacy-retry-attempt4')
    manifest = b.read(folder / 'archive-manifest.json')
    b.require(manifest['kind'] == 'FULL290_FINAL_A3_EXACT_SEGMENT_ARCHIVE' and manifest['mode'] == mode
        and manifest['source_freeze_sha256'] == FINAL_SHA and manifest['parent_commit'] == final['parent_commit']
        and manifest['preparation_sha256'] == PREPARATION_SHA and manifest['activation_sha256'] == ACTIVATION_SHA
        and manifest['actual_validation_attempt'] == 3 and manifest['actual_segment_passed'] is True
        and manifest['actual_original_typed_passed'] is (mode == 'legacy'), 'actual final component archive')
    verify_members(b, folder, manifest)
    b.require(b.sha(folder / 'root-source-freeze-final-A3.json') == FINAL_SHA
        and b.sha(folder / 'activation-final-A3.json') == ACTIVATION_SHA
        and b.sha(folder / 'execution-tools/preparation.json') == PREPARATION_SHA, 'actual archived inputs and binding')
    for name, expected in meta['new_tools_sha256'].items():
        b.require(b.sha(b.safe_child(folder / 'execution-tools', name)) == expected, 'all18 actual control files archived')
    for key, subdir in (('template_bundle_sha256', 'immutable-template-bundle'),):
        for name, expected in meta[key].items():
            b.require(b.sha(b.safe_child(folder / subdir, name)) == expected, 'all84 immutable template files archived')
    for name, expected in activation['execution_tools_sha256'].items():
        b.require(b.sha(b.safe_child(folder / 'executed-legacy-bundle', name)) == expected, 'all84 actual bound files archived')
    for name, expected in meta['necessary_module_public_sha256'].items():
        b.require(b.sha(b.safe_child(folder / 'necessary-module-public', name)) == expected, 'exact actual necessary proof archived')
    own, ledger = b.read(folder / 'owned-execution.json'), b.read(folder / 'orchestration.json')
    b.require(own['kind'] == 'FULL290_FINAL_A3_SEGMENT_EXECUTION' and own['mode'] == mode
        and own['root_freeze_sha256'] == FINAL_SHA and own['activation_sha256'] == ACTIVATION_SHA
        and own['controller_sha256'] == meta['new_tools_sha256']['run_segment.py']
        and ledger['status'] == 'terminal' and ledger.get('exception') is None, 'actual independently owned final component')
    sup, observed = terminal(b, folder / mode, 3600 if mode == 'offline' else 3690,
        meta['new_tools_sha256']['supervisor3690.py'])
    b.require(ledger['argv'] == observed['argv'], 'actual segment argv, not expected-only declaration')
    return folder, manifest, sup


def historical(b, final):
    for name, record in final['prior_archives'].items():
        folder = FULL / name
        b.require(b.sha(folder / 'archive-manifest.json') == record['manifest_sha256'], 'original sealed history manifest')
        manifest = b.read(folder / 'archive-manifest.json')
        b.require(len(manifest['files']) == record['files'], 'original complete archive inventory')
        verify_members(b, folder, manifest)
    for attempt, deadline in ((1, 1200), (2, 1800)):
        folder = FULL / ('execution-attempt' + str(attempt))
        sup = b.read(folder / 'offline/supervisor.json')
        b.require(sup['child_primary_exit'] == sup['supervisor_exit'] == 124 and sup['timed_out'] is True
            and sup['deadline_seconds'] == deadline and not (folder / 'offline/actual/windows-offline.json').exists(),
            'original offline timeout and missing final JSON not filled from diagnostic')
    sup = b.read(FULL / 'execution-attempt2/legacy/supervisor.json')
    b.require(sup['child_primary_exit'] == 124 and sup['supervisor_exit'] == 1 and sup['timed_out'] is False
        and not (FULL / 'execution-attempt2/legacy/independent-saved-readback-audit.json').exists(), 'A2 internal1200 legacy failure not promoted')
    correction = FULL / 'legacy-retry-attempt3-failed-correction'
    b.require(b.sha(correction / 'archive-manifest.json') == '2cca65100549a15594911827225bb3d9fbd26388f1a939107138163ba2c9bfbc', 'append-only actual retry3 correction')
    verify_members(b, correction, b.read(correction / 'archive-manifest.json'))
    return {b.relative((FULL / name) / 'archive-manifest.json'): record['manifest_sha256'] for name, record in final['prior_archives'].items()} | {
        b.relative(correction / 'archive-manifest.json'): b.sha(correction / 'archive-manifest.json')}


def main(args):
    b = fresh_module(HERE / 'build_summary_candidate.py', '_final_old_safe_helpers', OLD_HELPERS_SHA)
    q = b.require
    for output in (args.output, args.proof_output):
        q(output.is_absolute() and output.resolve().is_relative_to(HERE) and output.parent.is_dir()
          and not output.exists() and output.suffix == '.json', 'fresh cache-only candidate output')
    q(args.output != args.proof_output, 'distinct cache outputs')
    final, old, meta, activation = source_contract(b)
    q(subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
      and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == final['parent_commit'], 'current authorized tested parent')
    archive_pins = historical(b, final)
    offline_dir, offline_manifest, offline_sup = final_archive(b, 'offline', final, meta, activation)
    legacy_dir, legacy_manifest, legacy_sup = final_archive(b, 'legacy', final, meta, activation)
    offline = b.read(offline_dir / 'offline/actual/windows-offline.json')
    closure = b.read(offline_dir / 'offline/actual/final-A3-offline-source-closure.json')
    q(offline['available_checks_passed'] is True and offline['failures'] == offline['errors'] == 0
      and offline['source_sha256'] == final['source_sha256'] and offline['selectors'] == final['selectors']
      and offline['source_drift'] == [] and offline['verbosity'] == 2 and offline['platform'] == 'Windows'
      and offline['wine_compatibility'] is False
      and offline['tests_run'] == offline['tests_passed'] + offline['historical_or_declared_skips'] + offline['unavailable_parent_count'], 'actual complete430-selector offline and honest parent accounting')
    q(closure['kind'] == 'FULL290_FINAL_A3_ACTUAL_OFFLINE_SOURCE_CLOSURE' and closure['actual_suite_exit'] == 0
      and closure['exception'] is None and closure['after_guard_exception'] is None and closure['source_drift'] == []
      and closure['actual_receipt_exists'] is True and closure['actual_selector_list_matches_final_freeze'] is True
      and closure['actual_source_map_matches_final_freeze'] is True and closure['root_freeze_sha256'] == FINAL_SHA
      and closure['actual_suite_receipt_sha256'] == b.sha(offline_dir / 'offline/actual/windows-offline.json')
      and closure['runner_verbosity'] == 2 and closure['offline_available_checks_passed'] is True, 'actual final offline source closure')
    b.qt_clean(offline['qt_shutdown'], 'new offline3')
    q(offline['qt_shutdown_error'] is None, 'new offline actual cleanup')
    readback_sup, readback_obs = terminal(b, legacy_dir / 'readback', 120, meta['new_tools_sha256']['supervisor3690.py'])
    rledger = b.read(legacy_dir / 'readback/readback-orchestration.json')
    q(rledger['status'] == 'terminal' and rledger.get('exception') is None and rledger['typed_available_passed'] is True
      and rledger['argv'] == readback_obs['argv'], 'separate real original typed job0')
    argv = readback_sup['argv']
    q(Path(argv[3]).name == 'audit_full261_saved_readback.py'
      and Path(argv[argv.index('--freeze') + 1]).resolve() == FINAL
      and Path(argv[argv.index('--container') + 1]).resolve() == Path(legacy_manifest['source_container']) / 'legacy', 'typed actual argv belongs to this final result')
    q(b.sha(legacy_dir / 'executed-legacy-bundle/audit_full261_saved_readback.py') ==
      b.sha(FULL / 'execution-attempt2/executed-tools/legacy/audit_full261_saved_readback.py'), 'original complete typed auditor unchanged')
    b.native_window(legacy_dir / 'legacy', True, FINAL_SHA)
    legacy = b.read(legacy_dir / 'legacy/actual/wine-ui-100.json')
    typed = b.read(legacy_dir / 'legacy/independent-saved-readback-audit.json')
    q(legacy['passed'] is True and legacy['source_drift'] == legacy['source_additional_drift'] == []
      and legacy['source_sha256'] == legacy['source_sha256_after'] == final['legacy_native_source_sha256']
      and legacy['source_additional_sha256'] == legacy['source_additional_sha256_after'] == final['legacy_source_additional_sha256']
      and legacy['new_explicit_damage_button_requests090'] == 52 and legacy['new_explicit_three_text_requests090'] == 156,
      'actual full legacy4 scope and its complete native/additional maps')
    q(typed['passed'] is True and typed['timeout'] is False and typed['source_and_additional_drift'] == []
      and typed['process_exit'] == typed['child_primary_exit'] == typed['supervisor_exit'] == 0
      and typed['complete_runtime_checks'] == 4283 and typed['passed_flag_records'] == 4281 and typed['metadata_records'] == 2
      and typed['saved_rows'] == 52 and typed['current_revised_assertions'] == 862
      and typed['original552_maintry_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
      and typed['exact_ten_admission_indices'] == INDICES and typed['readonly_trace_empty_rows_not_invented'] == 26
      and typed['exact_ten_identity_types_input_and_full_row_hash_match'] is True
      and typed['codec_exact_typed_roundtrip'] is True and typed['codec_plain_JSON_order_and_values_match'] is True
      and typed['archive_declared_hash_and_size_match'] is True, 'actual full52/4283/862/552/exact10/26 typed audit')
    q(rledger['actual_audit_receipt_sha256'] == b.sha(legacy_dir / 'legacy/independent-saved-readback-audit.json'), 'typed actual process binds exact receipt')
    necessary = b.read(ROOT / final['necessary_module_check']['public_receipt_relative'])
    nref = final['necessary_module_check']
    q(b.sha(ROOT / nref['public_receipt_relative']) == nref['receipt_sha256'] and necessary['exit_code'] == 0
      and necessary['source_unchanged'] is True and necessary['source_sha256_before'] == necessary['source_sha256_after']
      and nref['actual_tests_run'] == 15 and len(necessary['source_sha256_after']) == nref['receipt_declared_source_coverage_count'], 'fresh actual15 necessary methods, not old15 or full1221')
    for name, expected in meta['necessary_module_public_sha256'].items():
        q(b.sha(ROOT / name) == expected, 'actual fresh15 logs and receipt')
    nlog = b.regular(ROOT / 'verification/sections/290-necessary-final-A3/stderr.txt').read_text(encoding='utf8')
    q(re.search(r'Ran 15 tests in [0-9.]+s\s+OK\s*$', nlog) is not None, 'actual fresh15 complete stderr')
    a2 = FULL / 'execution-attempt2'
    sup2_sha = b.sha(a2 / 'executed-tools/legacy/supervisor275.py')
    b.verify_terminal(a2 / 'current30', 1, sup2_sha); b.native_window(a2 / 'current30', False, A2_SHA)
    b.verify_terminal(a2 / 'current29', 0, sup2_sha); b.native_window(a2 / 'current29', True, A2_SHA)
    c30, c29 = b.read(a2 / 'current30/actual/window.json'), b.read(a2 / 'current29/actual/window.json')
    failure = c30['failure']
    q(c30['passed'] is False and failure['type'] == 'OSError' and '[WinError 1314]' in failure['message']
      and 'diagnostic.symlink_to(public_target.name)' in failure['traceback']
      and 'os.symlink(target, self, target_is_directory)' in failure['traceback']
      and c29['passed'] is True and len(c29['checks']) == 29 and c29['maintenance261_safe_save_check'] is False,
      'actual original1314 failure versus separate29 available pass')
    for raw in (c30, c29):
        q(raw['source_sha256_before'] == raw['source_sha256_after'] == old['source_sha256'] and raw['source_drift'] == [], 'current raw maps stay A2, not finalA3')
    p3_rows = {}
    p3dir = FULL / 'p3-supplementary-attempt2'
    for number in range(286, 291):
        folder = p3dir / ('p3_' + str(number))
        sup = b.verify_terminal(folder, 0, sup2_sha)
        raw, close = b.read(folder / 'actual/p3-window.json'), b.read(folder / 'actual/supplementary290-source-closure.json')
        q(raw['passed'] is True and close['passed'] is True and close['actual_fixture_exit'] == 0
          and close['root_freeze_sha256'] == A2_SHA and close['actual_validation_attempt'] == 2
          and close['fixture_exception'] is None and close['source_validation_error_after'] is None and close['qt_cleanup_error'] is None
          and close['actual_receipt_sha256'] == b.sha(folder / 'actual/p3-window.json'), 'real original A2 P3 result')
        b.qt_clean(close['qt_cleanup'], 'A2 P3')
        before = raw.get('source_sha256_before', raw.get('loaded_source_sha256', raw.get('source_sha256')))
        q(raw.get('source_sha256_after', before) == before, 'A2 P3 own source stable')
        for name, value in before.items():
            source = {**old['source_sha256'], **old['supplemental_public_inputs_sha256']}
            if name in source:
                q(source[name] == value, 'actual A2 P3 original source')
            else:
                q(number == 288 and name in b.MAP_ORIGINALS and source[b.MAP_ORIGINALS[name]] == value
                  and b.sha(ROOT / name) == value, 'exact three current PNG aliases equal frozen original source bytes')
        if number == 286:
            unique, executions = raw['completed_check_count'], raw['successful_assertion_executions_including_repeated_safety_guards']
            q(raw['qpa'] == 'windows' and raw['window_closed'] is True, '286 real native window')
        elif number == 287:
            unique, executions = raw['unique_checks'], len(raw['checks'])
            q('native_windows_qpa' in raw['checks'] and all(row['hwnd'] > 0 for row in raw['stages']), '287 actual HWNDs')
        else:
            unique, executions = raw['unique_checks'], raw['successful_assertion_executions_including_repeated_guards']
            q(raw['qpa'] == 'windows' and raw['verification_window_closed'] is True, 'closed actual P3 native window')
        p3_rows[str(number)] = {'passed': True, 'actual_execution_attempt': 2, 'component_source_freeze_sha256': A2_SHA,
            'actual_child_and_supervisor_exit': 0, 'unique_check_labels': unique, 'actual_assertion_executions': executions,
            'runtime_seconds': sup['elapsed_seconds'], 'receipt': b.relative(folder / 'actual/p3-window.json')}
    visual = fresh_module(HERE / 'component_visual_reviews.py', '_final_actual_A2_review')
    a2_review = visual.verify_A2_visual_review(b, args.A2_visual_review.resolve())
    legacy_review = b.read(args.legacy_visual_review.resolve())
    q(legacy_review['kind'] == 'root_manual_visual_review_not_test_execution'
      and legacy_review['source_freeze_sha256'] == FINAL_SHA and legacy_review['actual_legacy_execution_ordinal'] == 4
      and legacy_review['validation_segment'] == 'legacy' and legacy_review['full_validation_pass_claimed'] is False,
      'root separate real final legacy4 PNG review authority')
    pngs = {name: value['sha256'] for name, value in legacy_manifest['files'].items() if name.startswith('legacy/actual/') and name.endswith('.png')}
    q(len(pngs) == len(legacy_review['images']) == 4 and {row['relative_path'] for row in legacy_review['images']} == set(pngs), 'all four final legacy actual PNGs')
    for row in legacy_review['images']:
        q(row['sha256'] == pngs[row['relative_path']] and isinstance(row['review'], str) and bool(row['review'].strip()), 'individual actual final legacy image review')
    for folder in (offline_dir, legacy_dir):
        archive_pins[b.relative(folder / 'archive-manifest.json')] = b.sha(folder / 'archive-manifest.json')
    q(source_contract(b) == (final, old, meta, activation), 'fresh source/tool equality unchanged during full readback')
    component_freezes = {'offline3': {'path': b.relative(FINAL), 'sha256': FINAL_SHA},
        'legacy4_and_original_typed': {'path': b.relative(FINAL), 'sha256': FINAL_SHA},
        'A2_current_and_P3': {'path': 'verification/full-290/source-freeze-repair.json', 'sha256': A2_SHA}}
    proof = {'kind': 'FULL290_FINAL_A3_COMPONENT_COMPOSITION_PROOF', 'complete_available_components_passed': True,
        'all_historical_source_maps_same_freeze': False, 'new_offline_and_legacy_share_one_final_freeze': True,
        'A2_GUI_ran_final_complete_source': False, 'component_freezes': component_freezes,
        'exact_two_nonproduction_source_changes': CHANGES, 'unchanged_full_sources': 1219,
        'raw_archive_manifests_sha256': archive_pins, 'fresh_necessary15': nref,
        'legacy_original_typed_actual_exit': 0, 'offline_actual_exit': 0, 'legacy4_actual_exit': 0,
        'root_visual_reviews': [a2_review, {'path': b.relative(args.legacy_visual_review.resolve()),
            'sha256': b.sha(args.legacy_visual_review.resolve()), 'source_freeze_sha256': FINAL_SHA,
            'actual_legacy_execution_ordinal': 4, 'image_paths': 4}],
        'metadata_and_timer_tool_adaptation': 'Optional non-WMI receipt metadata and longer watchdogs only; original862 assertions/552 physical maintry and calculation/qualification/selector scope preserved. Not a diagnosis of prior native crash.',
        'complete_repository_validation': False, 'P2_complete': False,
        'builder_sha256': b.sha(Path(__file__)), 'visual_review_reader_sha256': b.sha(HERE / 'component_visual_reviews.py'),
        'public_write_or_Git_publication_performed': False}
    proof_bytes = (json.dumps(proof, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    offline_keys = ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'failures', 'errors',
                    'unavailable_records', 'unavailable_parent_count', 'qt_shutdown', 'qt_shutdown_error')
    summary = {'after_section': 290, 'kind': 'functional_section_full_validation',
        'checked_at_Beijing': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'available_checks_passed': True, 'complete_repository_validation': False, 'scope_not_reduced': True,
        'P2_complete': False, 'single_execution_all_green': False, 'actual_validation_attempt': 3,
        'all_historical_source_maps_same_freeze': False, 'new_offline_and_legacy_share_one_final_freeze': True,
        'A2_GUI_ran_final_complete_source': False, 'component_freezes': component_freezes,
        'exact_two_nonproduction_source_changes': CHANGES, 'source_files': 1221, 'maintained_selectors': 430,
        'supplemental_public_input_files': 42, 'legacy_native_sources': 1221, 'legacy_additional_sources': 86,
        'source_freeze': b.relative(FINAL), 'source_freeze_sha256': FINAL_SHA, 'source_drift': [],
        'source_drift_scope': 'New finalA3 offline/native scopes; A2 current/P3 raw maps remain their actual historical freeze with the two explicitly admitted nonproduction source differences.',
        'tested_worktree_parent_commit': final['parent_commit'], 'native_current_windows_gui_verified': True,
        'native_windows_game_chat_verified': False, 'historical_original_Windows_verified': False,
        'composite_admissibility': {'receipt': 'verification/full-290/composite-admissibility.json',
            'sha256': sha256(proof_bytes).hexdigest()}, 'archive_manifests_sha256': archive_pins,
        'offline_windows': {key: offline[key] for key in offline_keys}, 'actual_offline_process_exit': 0,
        'offline_receipt': b.relative(offline_dir / 'offline/actual/windows-offline.json'),
        'legacy_window': {'passed': True, 'actual_validation_attempt': 3, 'actual_legacy_execution_ordinal': 4,
            'component_source_freeze_sha256': FINAL_SHA, 'actual_child_and_supervisor_exit': 0,
            'runtime_seconds': legacy_sup['elapsed_seconds'], 'runtime_check_records': typed['complete_runtime_checks'],
            'passed_flag_records': typed['passed_flag_records'], 'metadata_records': typed['metadata_records'],
            'saved_states': typed['saved_rows'], 'explicit_text_requests': legacy['new_explicit_three_text_requests090'],
            'current_assertion_AST_and_order': typed['current_revised_assertions'], 'original_maintry_checks': 552,
            'original_maintry_bytes_unchanged': True, 'original_maintry_sha256': typed['original552_maintry_sha256'],
            'historical_projection_records': 42, 'exact_bridge_indices': INDICES, 'real_empty_trace_rows': 26,
            'typed_readback_verified': True, 'formal_typed_readback_actual_exit': 0,
            'typed_archive_sha256': typed['compressed_archive_sha256'],
            'receipt': b.relative(legacy_dir / 'legacy/actual/wine-ui-100.json'),
            'independent_saved_readback': b.relative(legacy_dir / 'legacy/independent-saved-readback-audit.json'),
            'readback_exit_file': b.relative(legacy_dir / 'readback/process.exit'), 'PNG_visual_inspection_count': 4},
        'current_window': {'maintained_scope': 30, 'actual_execution_attempt': 2, 'component_source_freeze_sha256': A2_SHA,
            'available_original_workflows_passed': 29, 'actual_full30_attempt_preserved': True,
            'full30_actual_child_and_supervisor_exit': 1, 'current29_actual_child_and_supervisor_exit': 0,
            'symlink_specialization': 'Original Path.symlink_to -> os.symlink WinError1314 unavailable, not passed.',
            'current29_receipt': b.relative(a2 / 'current29/actual/window.json'), 'full30_failure_receipt': b.relative(a2 / 'current30/actual/window.json')},
        'p3_supplementary_windows': p3_rows, 'fresh_necessary_module': nref,
        'original_failures_preserved': {'A1_offline_timeout': True, 'A2_offline_timeout': True,
            'A2_internal1200_legacy_timeout': True, 'legacy_retry3_native_crash': True,
            'retry3_append_only_correction': 'verification/full-290/legacy-retry-attempt3-failed-correction/correction.json',
            'diagnostic217_not_substituted_for_missing_full_JSON': True},
        'unavailable_scopes': ['Actual symlink subcases/current30 prerequisite1314 remain unavailable, not passed.',
            'Linux/WSL/Wine, original Windows/private095/109, game and chat are not verified by this run.'],
        'current_worktree_validation_authority': True, 'candidate_only_not_publicly_published': True}
    with args.proof_output.open('xb') as stream:
        stream.write(proof_bytes)
    with args.output.open('xb') as stream:
        stream.write((json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'cache_summary': str(args.output), 'cache_proof': str(args.proof_output),
        'public_summary_or_CP_written': False, 'tests_or_GUI_started': False}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--A2-visual-review', dest='A2_visual_review', type=Path, required=True)
    parser.add_argument('--legacy-visual-review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--proof-output', type=Path, required=True)
    main(parser.parse_args())
