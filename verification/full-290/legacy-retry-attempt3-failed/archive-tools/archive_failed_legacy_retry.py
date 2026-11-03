"""Strict failed-retry archive; never calls/weakens the success archiver.

No application, tests, Qt, private state or game/chat calls. This producer
accepts only the explicitly observed source75 ordinal3 non-timeout crash.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.cache/p3-full290-legacy-retry-prep'
BUNDLE = BASE / 'legacy'
FREEZE = ROOT / 'verification/full-290/source-freeze-repair.json'
FREEZE_SHA = '75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'
PREPARATION_SHA = 'ecb0787cd58d4131e77b1aa5a4f4aa07bbced0d98ca24aec4665ca810b784fa7'
ACTIVATION_SHA = '11b7b7d6f082d777b88911fe8863712258332b6ae298a9453eeb249993c970f0'
PARENT = 'b68229bb586ef3a11c520a4814be3c09c72ef088'
SOURCE = Path(r'C:\Users\李娜\AppData\Local\Temp\rouge-full290-legacy-retry-88fb507330eb4c5eb18653e2d9257dc6')
DESTINATION = ROOT / 'verification/full-290/legacy-retry-attempt3-failed'
A2_ARCHIVES = {
    'execution-attempt2': '4c8b281bbaccc955636f95ef6d2ff461427c07107237e58ef732457adc0640aa',
    'p3-supplementary-attempt2': '917fd9eb0800f92ba38e0d7d197be1482fc739f68bbb11193a799c0289cbac09'}
CONTROLS = ('controller-process.json', 'controller-supervisor.stdout.log', 'controller-supervisor.stderr.log',
    'supervisor.json', 'supervisor.json.stdout.log', 'supervisor.json.stderr.log', 'process.exit', 'process-exit-origin.json')


def demand(condition, message):
    if condition is not True:
        raise ValueError(message)


def regular(path, boundary):
    demand(path.is_file() and not path.is_symlink() and not boundary.is_symlink()
           and path.resolve().is_relative_to(boundary.resolve()), 'exact regular declared public file: ' + str(path))
    for parent in path.parents:
        if parent == boundary:
            break
        demand(not parent.is_symlink(), 'no linked public parent')
    return path


def digest(path, boundary=ROOT):
    return sha256(regular(path, boundary).read_bytes()).hexdigest()


def read(path, boundary=ROOT):
    regular(path, boundary)
    return json.loads(path.read_bytes())


def member(boundary, name):
    relative = Path(name)
    demand(not relative.is_absolute() and '..' not in relative.parts and '\\' not in name
           and relative.as_posix() == name, 'canonical declared member')
    return regular(boundary / relative, boundary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seal-exact-failed-retry', action='store_true', required=True)
    parser.parse_args()
    demand(not DESTINATION.exists(), 'never overwrite a failed or partial archive')
    demand(subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
           == 'codex/p2-development' and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
           == PARENT, 'same authorized source75 parent')
    demand(digest(FREEZE) == FREEZE_SHA and digest(BASE / 'preparation.json') == PREPARATION_SHA
           and digest(BUNDLE / 'activation-retry290.json') == ACTIVATION_SHA, 'unchanged actually executed source/preparation/activation')
    frozen, meta, activation = read(FREEZE), read(BASE / 'preparation.json'), read(BUNDLE / 'activation-retry290.json')
    declared = {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}
    native_guard = read(BUNDLE / 'current-source-guard.json')
    def live_snapshot():
        return {name: digest(member(ROOT, name)) for name in {**declared, **native_guard['source_sha256'],
                                                             **native_guard['source_additional_sha256']}}
    expected_live = {**declared, **native_guard['source_sha256'], **native_guard['source_additional_sha256']}
    demand(live_snapshot() == expected_live and len(meta['new_tools_sha256']) == 25
           and len(meta['candidate_bundle_tools_sha256']) == 84
           and activation['execution_tools_sha256'] == meta['candidate_bundle_tools_sha256'],
           'complete exact25 tools/84 bundle plus full/native/additional source bindings')
    for name, expected in meta['new_tools_sha256'].items():
        demand(digest(member(BASE, name)) == expected, 'actually executed preparation tool: ' + name)
    for name, expected in meta['candidate_bundle_tools_sha256'].items():
        demand(digest(member(BUNDLE, name)) == expected, 'actually executed84 bundle: ' + name)
    own, ledger = read(SOURCE / 'owned-execution.json', SOURCE), read(SOURCE / 'orchestration.json', SOURCE)
    demand(own['kind'] == 'FULL290_SAME_SOURCE75_LEGACY_RETRY_EXECUTION3' and own['root'] == str(ROOT)
           and own['parent_commit'] == PARENT and own['root_freeze_sha256'] == FREEZE_SHA
           and own['preparation_sha256'] == PREPARATION_SHA and own['activation_sha256'] == ACTIVATION_SHA
           and own['controller_sha256'] == meta['new_tools_sha256']['run_legacy_retry.py']
           and own['actual_legacy_execution_ordinal'] == 3 and own['validation_segment'] == 'legacy_retry'
           and ledger['status'] == 'terminal', 'actual source75 retry3 owner and terminal ledger')
    step = SOURCE / 'legacy'
    supervisor, observed, origin = (read(step / name, SOURCE) for name in
        ('supervisor.json', 'controller-process.json', 'process-exit-origin.json'))
    demand(supervisor['status'] == observed['status'] == 'completed'
           and supervisor['child_primary_exit'] == 3221227274
           and supervisor['supervisor_exit'] == observed['actual_observed_popen_exit'] == 1
           and int(regular(step / 'process.exit', SOURCE).read_text(encoding='ascii').strip()) == 1
           and supervisor['timed_out'] is False and supervisor['deadline_seconds'] == 3690
           and supervisor['owned_handle_retained'] is True and supervisor['owned_job_assigned'] is True
           and supervisor['owned_job_no_live_execution_verified'] is True
           and supervisor['supervisor_sha256'] == meta['new_tools_sha256']['supervisor3690.py']
           and origin['derived_from_supervisor_json'] is False and origin['actual_observed_popen_exit'] == 1
           and origin['process_exit_sha256'] == digest(step / 'process.exit', SOURCE)
           and observed['argv'] == ledger['argv'] and supervisor['argv'] == observed['argv'][9:],
           'observed real non-timeout crash and closed owned job, never derived success')
    actual = step / 'actual'
    actual_names = {path.name for path in actual.iterdir()}
    demand(actual_names == {'full125-progress.json', 'source100-guard-input.json'}
           and not (SOURCE / 'readback').exists()
           and not (step / 'independent-saved-readback-audit.json').exists(), 'exact incomplete original output set; no complete/typed material')
    stderr = regular(step / 'supervisor.json.stderr.log', SOURCE).read_bytes()
    demand(sha256(stderr).hexdigest() == supervisor['stderr']['sha256'] and len(stderr) == supervisor['stderr']['bytes']
           and b'Windows fatal exception: code 0x8007000e' in stderr
           and b'_wmi_query' in stderr and b'line 1267' in stderr, 'exact actual fatal stderr retained')
    for archive, expected in A2_ARCHIVES.items():
        demand(digest(ROOT / 'verification/full-290' / archive / 'archive-manifest.json') == expected,
               'original A2 archives remain unchanged')
    DESTINATION.mkdir(parents=True)
    manifest = {'kind': 'FULL290_EXACT_FAILED_LEGACY_RETRY3_ARCHIVE_NO_PASS',
        'created_at': datetime.now(timezone.utc).isoformat(), 'files': {}, 'source_container': str(SOURCE),
        'source_freeze_sha256': FREEZE_SHA, 'parent_commit': PARENT, 'preparation_sha256': PREPARATION_SHA,
        'activation_sha256': ACTIVATION_SHA, 'actual_validation_segment': 'legacy_retry',
        'actual_legacy_execution_ordinal': 3, 'actual_child_exit': supervisor['child_primary_exit'],
        'actual_supervisor_exit': supervisor['supervisor_exit'], 'supervisor_timed_out': supervisor['timed_out'],
        'actual_runtime_seconds': supervisor['elapsed_seconds'], 'available_checks_passed_claimed': False,
        'complete_legacy_passed_claimed': False, 'actual_typed_passed': False, 'combined_pass_claimed': False,
        'success_archiver_executed_or_weakened': False, 'original_failed_tools_or_raw_changed': False,
        'private_state_or_arbitrary_tree_copied': False, 'tests_GUI_or_game_chat_started_by_archive': False,
        'producer_sha256': digest(Path(__file__)), 'status': 'copying_original_failed_evidence'}
    def copy(path, name, boundary):
        target_name = Path(name)
        demand(not target_name.is_absolute() and '..' not in target_name.parts and '\\' not in name
               and target_name.as_posix() == name, 'safe exact archive destination')
        before = digest(path, boundary)
        target = DESTINATION / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        with regular(path, boundary).open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        demand(digest(path, boundary) == before == digest(target), 'original failed evidence changed during copy')
        manifest['files'][name] = {'sha256': before, 'bytes': target.stat().st_size}
    try:
        for name in ('owned-execution.json', 'orchestration.json'):
            copy(SOURCE / name, name, SOURCE)
        for name in CONTROLS:
            copy(step / name, 'legacy/' + name, SOURCE)
        for name in sorted(actual_names):
            copy(actual / name, 'legacy/actual/' + name, SOURCE)
        for name in meta['new_tools_sha256']:
            copy(member(BASE, name), 'execution-tools/' + name, BASE)
        for name in ('preparation.json', 'READY.json', 'static-preparation-evidence.json', 'execution-once.json'):
            copy(BASE / name, 'execution-tools/' + name, BASE)
        for name in meta['candidate_bundle_tools_sha256']:
            copy(member(BUNDLE, name), 'executed-legacy-bundle/' + name, BUNDLE)
        copy(BUNDLE / 'activation-retry290.json', 'executed-legacy-bundle/activation-retry290.json', BUNDLE)
        copy(FREEZE, 'root-source-freeze-repair-original.json', ROOT)
        for name in A2_ARCHIVES:
            copy(ROOT / 'verification/full-290' / name / 'archive-manifest.json',
                 'prior-A2/' + name + '-archive-manifest.json', ROOT)
        copy(Path(__file__), 'archive-tools/archive_failed_legacy_retry.py', ROOT)
        annotation = {'kind': 'ACTUAL_FAILED_RETRY_OBSERVATION_NOT_MECHANISM_OR_PASS',
            'actual_child_exit_hex': hex(supervisor['child_primary_exit']),
            'stderr_fatal_code_observed': '0x8007000e', 'platform_WMI_stack_observed': True,
            'window_finalizer_line1267_in_stack': True, 'underlying_functional_exception_ruled_out': False,
            'finalizer_crash_may_mask_prior_exception': True,
            'complete_legacy_or_typed_claimed': False, 'original_status_or_labels_rewritten': False,
            'missing_files_not_synthesized': ['legacy/actual/wine-ui-100.json',
                'legacy/actual/native275-launcher-closure.json', 'legacy/independent-saved-readback-audit.json'],
            'source_production_and_private_settings_changed_by_archive': False}
        note = DESTINATION / 'failure-observation.json'
        with note.open('x', encoding='utf8') as stream:
            json.dump(annotation, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        manifest['files']['failure-observation.json'] = {'sha256': digest(note), 'bytes': note.stat().st_size,
            'append_only_observation_not_original_raw': True}
        demand(live_snapshot() == expected_live and digest(FREEZE) == FREEZE_SHA
               and digest(BASE / 'preparation.json') == PREPARATION_SHA
               and digest(BUNDLE / 'activation-retry290.json') == ACTIVATION_SHA, 'source/tools not modified by archive')
        manifest['status'] = 'sealed_exact_failed_outputs_no_pass'
        with (DESTINATION / 'archive-manifest.json').open('x', encoding='utf8') as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({'archive': str(DESTINATION), 'manifest_sha256': digest(DESTINATION / 'archive-manifest.json'),
            'files': len(manifest['files']), 'original_child_exit': supervisor['child_primary_exit'],
            'original_supervisor_exit': supervisor['supervisor_exit'], 'pass_claimed': False}, ensure_ascii=False))
    except BaseException as error:
        manifest['archive_error'] = {'type': type(error).__name__, 'message': str(error)}
        with (DESTINATION / 'archive-incomplete.json').open('x', encoding='utf8') as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        raise


if __name__ == '__main__':
    main()
