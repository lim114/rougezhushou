"""Assemble actual full095 metadata after ROOT observes all eight primary zeros.

This SOURCE-prepared helper never runs tests, project code, codecs, Wine, Git,
or image viewing. It preserves the eight existing ROOT process observations
verbatim and accepts only an already-created ROOT visual-review receipt.
It writes two reserved metadata files exclusively, after all input checks.
It cannot certify the final regression context or native Windows.
"""
import argparse
import hashlib
import json
import re
import stat
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/workspace/.continuation')
COMPAT = Path('/workspace/.compat')
BINDING = BASE / 'full095-regression-ui-cache-resume-final-v1/actual-full095-source-binding.json'
BINDING_SHA = 'b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84'
NAMES = ('linux_full', 'wine_full', 'linux_selected', 'wine_selected',
         'linux_pip', 'wine_pip', 'wine_ui', 'saved_review')
CHECKED = {}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    check(type(value) is str and value, 'A real absolute file path is required')
    path = Path(value)
    check(path.is_absolute() and '..' not in path.parts, 'Unsafe or relative path')
    check(str(path.resolve(strict=False)) == value, 'Aliased/noncanonical path: ' + value)
    check(path.is_relative_to(Path('/workspace')), 'Only public workspace inputs/outputs')
    for ancestor in (path, *path.parents):
        check(not ancestor.is_symlink(), 'Symlinked input/output ancestry: ' + value)
    return path


def reference(value, expected=None):
    path = canonical(value)
    check(path.is_file() and stat.S_ISREG(path.stat().st_mode), 'Missing/nonregular actual file: ' + value)
    data = path.read_bytes()
    actual = {'path': value, 'bytes': len(data), 'sha256': digest(data)}
    if expected is not None:
        check(type(expected) is dict and expected.get('path', value) == value,
              'Expected reference path differs: ' + value)
        check(type(expected.get('bytes')) is int and expected['bytes'] == len(data)
              and type(expected.get('sha256')) is str
              and re.fullmatch(r'[0-9a-f]{64}', expected['sha256']) is not None
              and expected['sha256'] == actual['sha256'], 'Actual input bytes/SHA differ: ' + value)
    check(value not in CHECKED or CHECKED[value] == actual, 'Input changed during assembly: ' + value)
    CHECKED[value] = actual
    return actual


def document(value, expected=None):
    full = reference(value, expected)
    return json.loads(Path(value).read_bytes()), full


def pointer(value, expression):
    check(type(expression) is str and expression.startswith('/'), 'Real JSON pointer required')
    for token in expression[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if type(value) is list else value[token]
    return value


def token(value):
    return value.replace('~', '~0').replace('/', '~1')


def file_pointer(path):
    return '/checked_file_refs/' + token(path)


def timestamp(value):
    check(type(value) is str, 'Actual process timestamp required')
    result = datetime.fromisoformat(value)
    check(result.utcoffset() is not None, 'Actual timestamps must include their timezone')
    return result


def verified_binding(proof, expression, expected):
    check(pointer(proof, expression) == expected, 'Proof does not bind actual file at ' + expression)
    reference(expected['path'], expected)
    return {'pointer': expression, 'projection': 'full_ref'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--visual-review', type=Path, required=True)
    args = parser.parse_args()
    binding_bytes = BINDING.read_bytes()
    check(digest(binding_bytes) == BINDING_SHA, 'Exact actual recovery FINAL binding required')
    binding, _ = document(str(BINDING), {'path': str(BINDING), 'bytes': len(binding_bytes), 'sha256': BINDING_SHA})
    check(binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
          and binding['section'] == 95 and binding['actual_original_epoch_recovery'] is True,
          'PENDING/source-only plan is not the sealed actual recovery binding')
    check(binding['format_version'] == 3 and binding['actual_ui_retry'] is True
          and binding['root_spec_projection_from_ui_retry'] is True,
          'Exact actual UI retry SOURCE projection required')
    actual = binding['actual_inputs']
    contracts = actual['execution_contracts']
    plan = actual['global_output_plan']
    outputs = plan['paths']
    check(set(contracts) == set(NAMES), 'All eight exact execution contracts required')
    witness_path = canonical(outputs['execution_witness'])
    acceptance_path = canonical(outputs['ui_extra_acceptance'])
    check(witness_path != acceptance_path and all(not p.exists() for p in (witness_path, acceptance_path)),
          'Preserve any earlier witness/acceptance; only fresh exclusive sinks are allowed')
    check(str(args.visual_review) == outputs['visual_review'], 'Only the declared genuine ROOT visual receipt is allowed')
    context, _ = document(outputs['context_start'])
    check(context['actual_original_epoch_recovery'] is True
          and context['binding']['path'] == str(BINDING)
          and context['binding']['sha256'] == BINDING_SHA,
          'Actual resumed recovery context must bind this FINAL source')
    reference(context['binding']['path'], context['binding'])
    start = timestamp(context['started_at'])
    recovery_start = timestamp(context['recovery_started_at'])
    ui_retry_start = timestamp(context['ui_retry_started_at'])
    check(context['actual_ui_retry'] is True
          and context['prior_incomplete_ui'] == binding['recovery_spec']['prior_incomplete_ui']
          and context['prior_selected_failed_execution'] == binding['recovery_spec']['prior_selected_failed_execution']
          and start <= recovery_start <= ui_retry_start,
          'Actual UI retry epoch and immutable incomplete/failed evidence must remain bound')
    now = datetime.now(timezone.utc)
    executions = {}
    raw_paths = set()
    for name in NAMES:
        row, _ = document(str(BASE / ('root-full095-' + name + '-observation.json')))
        contract = contracts[name]
        check(all(row.get(key) is True for key in ('actual_root_observed_primary_exit',
              'primary_exit_code_captured', 'fresh_execution'))
              and type(row['primary_exit_code']) is int and row['primary_exit_code'] == 0,
              'ROOT must already have observed the actual captured primary zero: ' + name)
        began, ended = timestamp(row['started_at']), timestamp(row['completed_at'])
        check(start <= began <= ended <= now, 'Execution is outside the actual original full095 epoch: ' + name)
        if name in ('wine_full', 'wine_selected'):
            check(began >= recovery_start, 'New adapter must run after the actual recovery: ' + name)
        if name in ('wine_ui', 'saved_review'):
            check(began >= ui_retry_start, 'New UI/saved execution predates the actual UI retry: ' + name)
        check(all(row[key] == contract[key] for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')),
              'Actual entry/argv/cwd/runner differs from the sealed recovery contract: ' + name)
        tool = row['actual_tool_observation']
        check(type(tool) is dict and type(tool['completion_tool_chunk']) is str and tool['completion_tool_chunk']
              and (tool['session_id'] is None or type(tool['session_id']) is int),
              'Existing ROOT trusted completion observation is required: ' + name)
        check(row['runtime_environment']['PYTHONDONTWRITEBYTECODE'] == '1', 'Actual launch environment differs: ' + name)
        stdout = outputs[contract['stdout_key']]
        check(row['stdout_log']['path'] == stdout and row['exit_code_file']['path'] == contract['exit_code_path'],
              'Actual stdout or primary sink differs: ' + name)
        reference(stdout, row['stdout_log'])
        raw_ref = reference(contract['exit_code_path'], row['exit_code_file'])
        check(Path(raw_ref['path']).read_bytes() in (b'0\n', b'0\r\n'), 'Actual strict integer zero is missing: ' + name)
        check(raw_ref['path'] not in raw_paths, 'Eight unique primary raw files are required')
        raw_paths.add(raw_ref['path'])
        if row['runner'] is not None:
            reference(row['runner']['path'], row['runner'])
        preserved = binding['recovery_spec']['preserved_passed_executions']
        if name in preserved:
            old, _ = document(preserved[name]['observation']['path'], preserved[name]['observation'])
            check(row == old, 'Preserved successful ROOT observation changed: ' + name)
        preserved_recovery = binding['recovery_spec']['preserved_recovery_passed_executions']
        if name in preserved_recovery:
            earlier, _ = document(preserved_recovery[name]['observation']['path'], preserved_recovery[name]['observation'])
            check(row == earlier, 'Preserved actual recovery primary-zero proof changed: ' + name)
        executions[name] = row

    ui, ui_ref = document(outputs['wine_ui'])
    check(executions['wine_ui']['UI_receipt'] == ui_ref, 'Actual UI observation binds another receipt')
    check(ui['passed'] is True and ui['complete_ui_validation'] is True
          and ui['source_drift'] == [] and ui['native_windows_verified'] is False
          and ui['game_captures'] == ui['chat_requests'] == 0 and ui['private_state_isolated'] is True,
          'Actual available fullUI receipt must pass its isolated compatibility scope')
    saved, saved_ref = document(outputs['saved_review_receipt'])
    check(executions['saved_review']['output_receipt'] == saved_ref, 'Actual eighth primary binds another saved proof')
    saved_true = ['/passed', '/actual_fullUI_saved_evidence_verified', '/actual_UI_primary_exit0_verified',
                  '/original_pending_and_final_inverse_exact', '/actual_phase_ledger_verified']
    check(all(pointer(saved, p) is True for p in saved_true)
          and saved['status'] == 'PASS_SAVED_ONLY_ACTUAL_FULL095_UI_EVIDENCE'
          and saved['validation_kind'] == 'SAVED_ONLY' and saved['project_calls'] == 0
          and saved['native_Windows_game_chat_verified'] is False
          and saved['complete_full095_or_section_validation'] is False,
          'Actual saved-only proof has not passed its exact scope')
    spec, spec_ref = document(contracts['saved_review']['argv'][3])
    check(saved['input_spec'] == spec_ref, 'Actual saved proof input_spec differs from the real control file')
    ui_runner = reference(binding['root_spec']['ui']['runner']['path'], binding['root_spec']['ui']['runner'])
    chain_row = binding['root_spec']['completed_working_tree_chain'][-1]
    check(chain_row['section'] == 95, 'Current archived source guard must belong to section95')
    guard = reference(chain_row['source_guard']['path'], chain_row['source_guard'])
    check(guard in spec['ui_binding_input_refs'],
          'Actual saved control must have registered the real archived section95 guard before saved execution')
    saved_common = {
        'ui_receipt': verified_binding(saved, '/actual_runtime_receipt', ui_ref),
        'ui_runner': verified_binding(saved, '/actual_final_runner', ui_runner),
        'source_guard': verified_binding(saved, file_pointer(guard['path']), guard),
    }

    artifacts = {}
    for item in binding['root_spec']['ui']['required_saved_outputs']:
        check(item['kind'] in ('native-evidence', 'screenshot') and item['path'] not in artifacts,
              'Unique fixed native/PNG artifacts required')
        artifacts[item['path']] = {'kind': item['kind'], 'file': reference(item['path'])}
    physical_native = set()
    for name in plan['fresh_evidence_directories']:
        directory = canonical(name)
        check(directory.is_dir(), 'Actual fresh native directory is absent')
        for path in sorted(directory.rglob('*')):
            check(not path.is_symlink(), 'Actual native namespace contains a symlink')
            mode = path.lstat().st_mode
            check(stat.S_ISDIR(mode) or stat.S_ISREG(mode), 'Actual native namespace contains a nonregular entry')
            if stat.S_ISREG(mode):
                full = reference(str(path))
                check(full['path'] not in physical_native, 'Duplicate native directory file')
                physical_native.add(full['path'])
                if full['path'] in artifacts:
                    check(artifacts[full['path']] == {'kind': 'native-evidence', 'file': full}, 'Native file aliases a PNG')
                else:
                    artifacts[full['path']] = {'kind': 'native-evidence', 'file': full}
    meta_rows = ui['full_native095']['files']
    declared_native = set()
    for row in meta_rows:
        name = row['file']
        check(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts,
              'Actual receipt native path must be safe and compat-relative')
        path = str(COMPAT / name)
        full = reference(path, {'path': path, 'bytes': row['bytes'], 'sha256': row['sha256']})
        check(full['path'] not in declared_native, 'Duplicate native receipt entry')
        declared_native.add(full['path'])
    check(declared_native == physical_native and physical_native, 'Receipt/native physical namespace coverage differs')
    saved_artifact_bindings = []
    for path, item in artifacts.items():
        contract = verified_binding(saved, file_pointer(path), item['file'])
        saved_artifact_bindings.append({'artifact_path': path, **contract})

    visual, visual_ref = document(outputs['visual_review'])
    visual_true = ['/passed', '/actual_root_view_image']
    check(all(pointer(visual, p) is True for p in visual_true),
          'Only an already-created genuine ROOT image-tool review is accepted')
    visual_common = {'ui_receipt': verified_binding(visual, '/actual_runtime_receipt', ui_ref)}
    screenshots = {path: item for path, item in artifacts.items() if item['kind'] == 'screenshot'}
    check(len(screenshots) == 4 and visual['actual_PNGs_viewed'] == 4, 'ROOT must actually inspect all four current PNGs')
    viewed = visual['screenshots']
    check(type(viewed) is list and len(viewed) == len(screenshots), 'Exact four genuine ROOT screenshot rows required')
    visual_artifact_bindings = []
    covered = set()
    for index, row in enumerate(viewed):
        check(row['actual_root_view_image'] is True and type(row['observed']) is str and row['observed'],
              'Actual ROOT per-image inspection and visible observation text required')
        path = row['file']['path']
        check(path in screenshots and path not in covered, 'Visual review screenshot set differs from actual current artifacts')
        contract = verified_binding(visual, '/screenshots/%d/file' % index, screenshots[path]['file'])
        visual_artifact_bindings.append({'artifact_path': path, **contract})
        covered.add(path)
    check(covered == set(screenshots), 'Visual proof omits an actual current PNG')
    check(visual['native_Windows_game_chat_verified'] is False, 'Visual pixels cannot certify native Windows/game/chat')

    # Complete all metadata checks, then re-read every input before exclusive writes.
    for full in list(CHECKED.values()):
        reference(full['path'], full)
    witness = {'format_version': 2, 'section': 95, 'actual_root_observed_primary_exits': True,
               'executions': executions}
    witness_bytes = (json.dumps(witness, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')
    with witness_path.open('xb') as handle:
        handle.write(witness_bytes)
    witness_ref = reference(str(witness_path))
    acceptance = {
        'format_version': 2, 'section': 95, 'actual_ui_receipt': ui_ref,
        'artifacts': list(artifacts.values()),
        'receipts': [
            {'kind': 'saved-validation', 'file': saved_ref, 'required_true_pointers': saved_true,
             'common_file_bindings': saved_common, 'artifact_bindings': saved_artifact_bindings,
             'execution_name': 'saved_review'},
            {'kind': 'visual-review', 'file': visual_ref, 'required_true_pointers': visual_true,
             'actual_view_image_pointer': '/actual_root_view_image', 'common_file_bindings': visual_common,
             'artifact_bindings': visual_artifact_bindings},
        ],
        'primary_exit_witness': witness_ref,
    }
    with acceptance_path.open('x', encoding='utf-8') as handle:
        json.dump(acceptance, handle, ensure_ascii=False, allow_nan=False, indent=2)
        handle.write('\n')
    print(json.dumps({'metadata_only': True, 'project_calls': 0, 'full_context_PASS_claimed': False,
                      'actual_primary_observations': len(executions), 'actual_artifact_files': len(artifacts),
                      'actual_native_files': len(physical_native), 'actual_PNGs': len(screenshots),
                      'execution_witness': witness_ref, 'ui_extra_acceptance': reference(str(acceptance_path))},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
