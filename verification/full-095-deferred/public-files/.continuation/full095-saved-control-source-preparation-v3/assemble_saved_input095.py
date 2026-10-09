"""Bind actual full095 UI metadata after root observes its primary exit 0.

SOURCE preparation only: root reviews this file before invoking it. This script
imports no project, target validator, codec, Qt, or Wine module. It does not run
tests or launch a process. It writes only the reserved saved-input control file,
exclusively, after validating its actual physical metadata and root observation.
"""
import argparse
import hashlib
import json
import re
import stat
from datetime import datetime
from pathlib import Path, PureWindowsPath

BASE = Path('/workspace/.continuation')
REPO = Path('/workspace/rougezhushou')
COMPAT = Path('/workspace/.compat')
OUTPUT = BASE / 'root-full095-ui-cache-retry-v1-saved-input-spec.json'
BINDING = BASE / 'full095-regression-ui-cache-resume-final-v1/actual-full095-source-binding.json'
TEMPLATE = BASE / 'full095-saved-validator-ui-cache-pending-v4/root-input-template095.json'
BOUND_UI = BASE / 'full095-ui-cache-retry-source-v1/root-bound-input095.json'
PRELAUNCH = BASE / 'root-full095-ui-cache-retry-v1-prelaunch.json'
OBSERVATION = BASE / 'root-full095-wine_ui-cache-retry-v1-observation.json'
NATIVE = COMPAT / 'full095-ui-native-cache-retry-v1'
INDEX = NATIVE / 'wine-ui-full-native-index-095.json'
BASELINE = BASE / 'ui-095-module-report-pending/baseline094-v2'
BASELINE_FORMAL = BASE / 'baseline094-for095-final-source-review'
PINS = {
    str(TEMPLATE): '8213ce9ec95ef5fbc2b990f5c4f22ce437c9912fdd5491e7e370775e5a68ecd8',
    str(BOUND_UI): '8bbfa6d7217c44848cca1a5934776184d6870de7db8aded9243fa4fb2c431a34',
}
CHECKED = {}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    check(type(value) is str, 'Path must be a string')
    path = Path(value)
    check(path.is_absolute() and '..' not in path.parts, 'Explicit absolute safe Linux path required')
    resolved = path.resolve(strict=True)
    check(resolved.is_relative_to(Path('/workspace')), 'Public workspace inputs only')
    return str(resolved)


def reference(value, expected=None):
    original = Path(value)
    check(original.is_file() and not original.is_symlink(), 'Missing or symlinked actual file: ' + str(value))
    name = canonical(str(value))
    data = original.read_bytes()
    full = {'path': name, 'bytes': len(data), 'sha256': digest(data)}
    if expected is not None:
        check(type(expected) is dict and type(expected['sha256']) is str
              and re.fullmatch(r'[0-9a-f]{64}', expected['sha256']) is not None,
              'Source reference requires an actual SHA')
        check(full['sha256'] == expected['sha256'], 'Source SHA differs: ' + name)
        if 'bytes' in expected:
            check(type(expected['bytes']) is int and expected['bytes'] == full['bytes'], 'Source byte count differs: ' + name)
    check(name not in CHECKED or CHECKED[name] == full, 'Input changed during metadata assembly: ' + name)
    CHECKED[name] = full
    return full


def document(value, expected=None):
    full = reference(str(value), expected)
    return json.loads(Path(full['path']).read_bytes()), full


def pointer(value, expression):
    check(type(expression) is str and expression.startswith('/'), 'Explicit real JSON pointer required')
    for token in expression[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if type(value) is list else value[token]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--binding-sha256', required=True)
    parser.add_argument('--prelaunch', type=Path, required=True)
    parser.add_argument('--prelaunch-sha256', required=True)
    args = parser.parse_args()
    check(str(args.output) == str(OUTPUT), 'Only the exact bound future control path is allowed')
    check(str(args.binding) == str(BINDING) and str(args.prelaunch) == str(PRELAUNCH),
          'Only exact new immutable binding and actual root prelaunch paths are allowed')
    check(not OUTPUT.exists() and not OUTPUT.is_symlink(), 'Preserve every previous control file')
    pinned = {name: document(name, {'sha256': sha})[0] for name, sha in PINS.items()}
    binding, binding_ref = document(BINDING, {'sha256': args.binding_sha256})
    pre, pre_ref = document(PRELAUNCH, {'sha256': args.prelaunch_sha256})
    check(binding['actual_original_epoch_recovery'] is True and binding['actual_ui_retry'] is True,
          'Actual original recovery with Source-qualified new UI retry binding required')
    root = binding['root_spec']
    actual = binding['actual_inputs']
    paths = actual['global_output_plan']['paths']
    contract = actual['execution_contracts']['wine_ui']
    saved_contract = actual['execution_contracts']['saved_review']
    spec = pinned[str(TEMPLATE)]
    ui = pinned[str(BOUND_UI)]
    retry = actual['ui_retry']
    retry_contract, retry_contract_ref = document(retry['source_contract']['path'], retry['source_contract'])
    check(retry['planned_root_prelaunch_path'] == str(PRELAUNCH)
          and retry['planned_saved_input_path'] == str(OUTPUT), 'Immutable UI retry root control reservations differ')
    check(retry['ui'] == root['ui'] == actual['UI_source_binding']
          and retry['runner'] == root['ui']['runner'] == contract['runner'] == retry_contract['runner'],
          'Projected retry UI and exact runner binding differ')
    check(retry_contract['source_gate_passed'] is True and retry_contract['runtime_pass'] is False
          and retry_contract['execution_ready'] is False, 'Retry SOURCE contract must not claim runtime')
    check(pre['runner'] == retry['runner'] and pre['source_contract'] == retry['source_contract']
          and pre['formal_source_review'] == retry['source_review'], 'Actual prelaunch exact retry input references differ')
    check(binding['section'] == root['section'] == actual['section'] == 95, 'Actual section95 binding required')
    check(root['repo'] == str(REPO) and contract['cwd'] == str(REPO), 'Exact bound working directory required')
    check(saved_contract['argv'][3] == str(OUTPUT), 'Future saved argv control reservation differs')
    saved_bundle = retry['saved_review_source']
    check(saved_bundle['argv'] == saved_contract['argv']
          and saved_bundle['runner'] == root['saved_review']['runner'] == saved_contract['runner']
          and saved_bundle['source_review'] == root['saved_review']['execution_contract']['source_review'],
          'New saved v4 future runner, Source review and argv bundle differ')
    retry_paths = retry_contract['replacement_output_paths']
    check(all(paths[name] == value for name, value in retry_paths.items())
          and retry_contract['exact_argv'] == contract['argv'] and retry_contract['cwd'] == contract['cwd']
          and root['ui']['required_saved_outputs'] == retry_contract['required_saved_outputs']
          and root['ui']['optional_output_paths'] == retry_contract['optional_output_paths']
          and root['ui']['fresh_evidence_directories'] == retry_contract['fresh_evidence_directories'],
          'Immutable Source contract and actual UI path/entry reservations differ')

    mapping = root['wine_path_mapping']
    check(mapping['drive'] == 'Z:' and mapping['drive_link'] == '/workspace/.compat/wine-prefix/dosdevices/z:', 'Exact configured Z drive required')
    link = Path(mapping['drive_link'])
    check(link.is_symlink() and str(link.resolve(strict=True)) == mapping['linux_root'], 'Actual Z symlink differs from root binding')
    wrapper = reference(root['wine_wrapper']['path'], root['wine_wrapper'])
    proof, proof_ref = document(mapping['proof']['path'], mapping['proof'])
    mp = mapping['proof_pointers']
    check(pointer(proof, mp['drive_link']) == mapping['drive_link']
          and pointer(proof, mp['linux_target']) == mapping['linux_root']
          and pointer(proof, mp['wrapper_sha256']) == wrapper['sha256'], 'Actual mapping proof differs')

    def linux(value):
        if value.startswith('/'):
            return canonical(value)
        win = PureWindowsPath(value)
        check(win.drive == mapping['drive'] and win.root == '\\' and '..' not in win.parts, 'Only configured absolute Z paths allowed')
        return canonical(str(Path(mapping['linux_root']).joinpath(*win.parts[1:])))

    def expand(row):
        return reference(linux(row['path']), row)

    def collect(value, result):
        if type(value) is dict:
            if {'path', 'sha256'} <= set(value):
                full = expand(value)
                check(full['path'] not in result or result[full['path']] == full, 'Conflicting canonical refs')
                result[full['path']] = full
            for item in value.values():
                collect(item, result)
        elif type(value) is list:
            for item in value:
                collect(item, result)

    refs = {}
    collect(ui, refs)
    collect(retry, refs)
    collect(retry_contract, refs)
    refs[binding_ref['path']] = binding_ref
    refs[pre_ref['path']] = pre_ref
    guard = expand(ui['source_guard'])
    check(guard == spec['actual_source_guard'], 'Exact actual095 SOURCE guard required')
    guard_json, _ = document(guard['path'], guard)
    source_map = actual['source_sha256']
    check(guard_json['passed'] is True and guard_json['candidate_bytes_exact'] is True
          and guard_json['source_sha256_after'] == source_map, 'Whole guarded source differs')
    # The recovery acceptance binds the already-archived section95 guard path.
    # Register its real full_ref so saved.py independently reads that exact file.
    archived_chain_row = root['completed_working_tree_chain'][-1]
    check(archived_chain_row['section'] == 95, 'Archived guard must belong to actual section95 chain')
    archived_guard_json, archived_guard = document(archived_chain_row['source_guard']['path'],
                                                  archived_chain_row['source_guard'])
    check(archived_guard['path'] == '/workspace/rougezhushou/research/p2-section095-selected-module-source-report/root-source-095-v2.json'
          and archived_guard['bytes'] == guard['bytes']
          and archived_guard['sha256'] == guard['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
          and archived_guard_json == guard_json, 'Actual archived/external section95 guards must have identical bytes/SHA and JSON')
    check(archived_guard['path'] not in refs or refs[archived_guard['path']] == archived_guard,
          'Conflicting archived section95 guard registry reference')
    refs[archived_guard['path']] = archived_guard

    current = {path.relative_to(REPO).as_posix(): digest(path.read_bytes())
               for folder in ('rouge', 'tests', 'scripts') for path in sorted((REPO / folder).rglob('*'))
               if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
    check(current == source_map, 'Maintained source addition/deletion/drift before assembly')
    for name, sha in source_map.items():
        reference(str(REPO / name), {'sha256': sha})

    final_runner = reference(root['ui']['runner']['path'], root['ui']['runner'])
    final_mf = reference(retry['manifest']['path'], retry['manifest'])
    formal, formal_ref = document(retry['source_review']['path'], retry['source_review'])
    fp = {'source_gate': '/source_gate_passed', 'runtime': '/runtime_pass',
          'runner_sha256': '/runner_sha256', 'manifest_sha256': '/final_manifest_sha256', 'guard_sha256': '/guard_sha256'}
    check(pointer(formal, fp['source_gate']) is True and pointer(formal, fp['runtime']) is False
          and pointer(formal, fp['runner_sha256']) == final_runner['sha256']
          and pointer(formal, fp['manifest_sha256']) == final_mf['sha256']
          and pointer(formal, fp['guard_sha256']) == guard['sha256'], 'Actual FINAL five-pointer SOURCE gate differs')
    reference(spec['pending_UI']['manifest']['path'], spec['pending_UI']['manifest'])
    pp = {'source_gate': '/source_gate_passed', 'outputs_absent': '/outputs_absent', 'argv': '/actual_argv',
          'cwd': '/cwd', 'runner_sha256': '/runner_sha256', 'guard_sha256': '/guard_sha256'}
    check(pre['source_gate_passed'] is True and pre['outputs_absent'] is True and pre['runtime_pass'] is False
          and pre['actual_argv'] == contract['argv'] and pre['cwd'] == contract['cwd']
          and pre['runner_sha256'] == final_runner['sha256'] and pre['guard_sha256'] == guard['sha256'], 'Actual prelaunch source admission differs')

    observation, observation_ref = document(OBSERVATION)
    op = {'observed': '/actual_root_observed_primary_exit', 'captured': '/primary_exit_code_captured',
          'argv': '/argv', 'cwd': '/cwd', 'exit_code': '/primary_exit_code', 'exit_code_file': '/exit_code_file',
          'console_log': '/stdout_log', 'UI_receipt': '/UI_receipt'}
    check(observation['actual_root_observed_primary_exit'] is True and observation['primary_exit_code_captured'] is True
          and type(observation['primary_exit_code']) is int and observation['primary_exit_code'] == 0
          and observation['fresh_execution'] is True, 'Trusted root actual UI primary0 is required')
    check(all(observation[k] == contract[k] for k in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')), 'Observed exact execution contract differs')
    context, _ = document(paths['context_start'])
    check(datetime.fromisoformat(context['started_at']) <= datetime.fromisoformat(observation['started_at'])
          <= datetime.fromisoformat(observation['completed_at']), 'Actual process observation timestamps differ')
    check(observation['actual_tool_observation']['completion_tool_chunk'], 'Actual root completion tool observation required')
    exit_ref = reference(contract['exit_code_path'], observation['exit_code_file'])
    console_ref = reference(paths[contract['stdout_key']], observation['stdout_log'])
    check(exit_ref == observation['exit_code_file'] and console_ref == observation['stdout_log']
          and Path(exit_ref['path']).read_bytes() in (b'0\n', b'0\r\n'), 'Physical UI exit/console root full_refs differ')
    receipt, receipt_ref = document(paths['wine_ui'], observation['UI_receipt'])
    check(receipt_ref == observation['UI_receipt'] and receipt['passed'] is True
          and receipt['complete_ui_validation'] is True and 'failure' not in receipt, 'Actual fullUI receipt incomplete')
    check(receipt['native_windows_verified'] is False and type(receipt['game_captures']) is int
          and type(receipt['chat_requests']) is int and receipt['game_captures'] == receipt['chat_requests'] == 0
          and receipt['private_state_isolated'] is True, 'Native/game/chat/private-state boundary differs')
    rg = receipt['source_guard095']
    check(linux(rg['path']) == guard['path'] and rg['sha256'] == guard['sha256']
          and rg['before'] == rg['after'] == source_map and rg['source_drift'] == [] and rg['read_error'] is None, 'Actual receipt whole source guard differs')
    own = {k: v for k, v in source_map.items() if k.startswith('rouge/')}
    check(receipt['source_sha256'] == receipt['source_sha256_after'] == own and receipt['source_drift'] == [], 'Actual own source selector differs')
    failure = receipt['full095_evidence_failure']
    check(failure['pending_entry_sequences'] == failure['Qt_slot_exceptions'] == failure['capture_or_write_errors'] == [], 'Actual UI evidence has an incomplete or failed entry')
    check(type(receipt['checks']) is list and receipt['checks']
          and all(type(row) is dict and row.get('passed') is not False for row in receipt['checks'])
          and receipt['actual_total_checks095'] == receipt['total_actual_checks'] == len(receipt['checks']), 'Actual UI measured check ledger differs')

    index, index_ref = document(INDEX)
    meta = receipt['full_native095']
    check(meta['schema'] == index['schema'] == 'full-ui095-native-index-v1' and index['outcome'] == 'passed'
          and index['source_guard_sha256'] == guard['sha256'] and index['source_drift'] == []
          and str(COMPAT / meta['file']) == str(INDEX) and meta['index_bytes'] == index_ref['bytes']
          and meta['index_sha256'] == index_ref['sha256'], 'Actual successful native index metadata differs')
    declared = {}
    for row in meta['files']:
        name = Path(row['file'])
        check(not name.is_absolute() and '..' not in name.parts and name.parts[0] == NATIVE.name, 'Unsafe native file path')
        full = reference(str(COMPAT / name), row)
        check(full['path'] not in declared, 'Duplicate native physical file')
        declared[full['path']] = full
    check(NATIVE.is_dir() and not NATIVE.is_symlink(), 'Actual native directory absent or symlinked')
    physical = set()
    for path in NATIVE.rglob('*'):
        mode = path.lstat().st_mode
        check(stat.S_ISDIR(mode) or stat.S_ISREG(mode), 'Native directory contains a nonregular entry')
        if stat.S_ISREG(mode):
            physical.add(canonical(str(path)))
    check(physical == set(declared) and declared[str(INDEX)] == index_ref, 'Actual native physical set differs')
    chunk_paths = {canonical(str(COMPAT / row['file'])) for row in index['chunks']}
    check(len(chunk_paths) == len(index['chunks']) == meta['chunks'] and chunk_paths | {str(INDEX)} == physical, 'Actual indexed chunk coverage differs')
    for number, row in enumerate(index['chunks'], 1):
        name = canonical(str(COMPAT / row['file']))
        check(Path(name).parent == NATIVE and Path(name).name == 'wine-ui-full-native-095-%06d.json.gz' % number
              and row['bytes'] == declared[name]['bytes'] and row['sha256'] == declared[name]['sha256'], 'Actual ordered chunk compressed metadata differs')

    required = root['ui']['required_saved_outputs']
    legacy_rows = [row for row in required if row['kind'] == 'native-evidence' and row['path'] != str(INDEX)]
    png_rows = [row for row in required if row['kind'] == 'screenshot']
    check(len(legacy_rows) == 1 and len(png_rows) == 4, 'Exact source-bound legacy and four PNG output roles required')
    legacy_meta = receipt['new_state_archive090']
    check(legacy_rows[0]['path'] == str(COMPAT / legacy_meta['file']), 'Actual legacy output role differs from receipt')
    legacy_ref = reference(legacy_rows[0]['path'], legacy_meta)
    png_refs = [reference(row['path']) for row in png_rows]

    prerequisites = {}
    baseline_proof, _ = document(linux(ui['baseline_saved_verifier']['path']), ui['baseline_saved_verifier'])
    check(baseline_proof['passed'] is True and baseline_proof['validation_kind'] == 'SAVED_ONLY'
          and baseline_proof['actual']['states'] == 41
          and baseline_proof['actual_runtime_receipt_sha256'] == ui['baseline_receipt']['sha256'], 'Actual existing41-state baseline proof differs')
    for name, row in baseline_proof['input_bindings'].items():
        full = reference(name, row)
        prerequisites[full['path']] = full
    baseline_pre, baseline_pre_ref = document(BASE / 'root-baseline094-for095-prelaunch.json')
    prerequisites[baseline_pre_ref['path']] = baseline_pre_ref
    collect(baseline_pre, prerequisites)
    baseline_formal, _ = document(baseline_pre['formal_review']['path'], baseline_pre['formal_review'])
    check(baseline_formal['source_gate_passed'] is True and baseline_formal['runtime_pass'] is False
          and baseline_formal['runner_sha256'] == baseline_pre['runner']['sha256']
          and baseline_formal['source_guard_sha256'] == baseline_pre['actual94_guard']['sha256']
          and baseline_formal['plan_sha256'] == baseline_pre['plan']['sha256'], 'Actual historical baseline SOURCE gate differs')
    for directory, hand_name in ((BASELINE, 'handoff-baseline094.json'), (BASELINE_FORMAL, 'handoff-formal-baseline094-review.json')):
        hand, hand_ref = document(directory / hand_name)
        collect(hand, prerequisites)
        prerequisites[hand_ref['path']] = hand_ref
        mf, mf_ref = document(hand['manifest']['path'], hand['manifest'])
        prerequisites[mf_ref['path']] = mf_ref
        if directory == BASELINE:
            collect(mf['payload'], prerequisites)
        else:
            for row in mf['files']:
                full = reference(row['source_path'], row)
                prerequisites[full['path']] = full
    plan_ref = expand(baseline_pre['plan'])
    baseline_exit = reference(str(BASE / 'root-baseline094-for095.exit-code'), baseline_proof['input_bindings'][str(BASE / 'root-baseline094-for095.exit-code')])
    check(Path(baseline_exit['path']).read_bytes() in (b'0\n', b'0\r\n'), 'Actual historical baseline physical primary0 required')
    collect(ui['baseline_saved_verifier'], prerequisites)

    saved_review_row = root['saved_review']['execution_contract']['source_review']
    saved_review, saved_review_ref = document(saved_review_row['path'], saved_review_row)
    sp = {'source_gate': '/source_gate_passed', 'runtime': '/runtime_pass', 'runner_sha256': '/runner_sha256', 'argv': '/execution_argv'}
    saved_runner = reference(root['saved_review']['runner']['path'], root['saved_review']['runner'])
    check(saved_review['source_gate_passed'] is True and saved_review['runtime_pass'] is False
          and saved_review['runner_sha256'] == saved_runner['sha256']
          and saved_review['execution_argv'] == saved_contract['argv'], 'Saved v3 exact SOURCE gate and future argv differ')

    spec.update(status='ROOT_BOUND_ACTUAL_FULL095_SAVED_INPUTS', wine_wrapper=wrapper,
                wine_path_mapping={'drive': mapping['drive'], 'drive_link': mapping['drive_link'],
                                   'linux_root': mapping['linux_root'], 'proof': proof_ref,
                                   'pointers': {'drive_link': mp['drive_link'], 'linux_root': mp['linux_target'], 'wrapper_sha256': mp['wrapper_sha256']}},
                final_UI={'runner': final_runner, 'manifest': final_mf, 'formal_source_review': formal_ref, 'formal_pointers': fp},
                ui_retry=retry,
                ui_binding_input_refs=list(refs.values()),
                actual_UI_primary={'prelaunch': CHECKED[str(PRELAUNCH)], 'root_observation': observation_ref,
                                   'exit_code_file': exit_ref, 'console_log': console_ref, 'argv': contract['argv'],
                                   'prelaunch_pointers': pp, 'observation_pointers': op},
                actual_UI_receipt=receipt_ref, actual_native_index=index_ref, actual_legacy_state_archive=legacy_ref,
                actual_PNGs=png_refs, actual_baseline_plan=plan_ref, actual_baseline_primary_exit=baseline_exit,
                baseline_prerequisite_refs=list(prerequisites.values()), saved_source_review={'file': saved_review_ref, 'pointers': sp})
    # This assembler validates metadata, never native graphs or target behavior.
    # Recheck every source/evidence reference immediately before the exclusive write.
    for full in list(CHECKED.values()):
        reference(full['path'], full)
    encoded = (json.dumps(spec, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    check(json.loads(encoded) == spec, 'Control JSON round trip differs before write')
    with OUTPUT.open('xb') as handle:
        handle.write(encoded)
    print(json.dumps({'status': 'ACTUAL_FULL095_METADATA_CONTROL_BOUND_NOT_SAVED_PROOF',
                      'output': reference(str(OUTPUT)), 'ui_binding_input_refs': len(refs),
                      'baseline_prerequisite_refs': len(prerequisites), 'target_or_project_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
