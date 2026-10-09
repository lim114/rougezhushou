"""SOURCE preparation only. ROOT may run this metadata assembler after actual finish0.

This never imports the project, executes a verifier, runs Git/Wine, or mutates
tracked files. It writes one NEW external completed archive spec from actual
closed receipts. That spec still requires the existing independent helper/spec
SOURCE review and the existing archive helper preflight before archive execution.
"""
import argparse
import hashlib
import json
import stat
from datetime import datetime
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
HERE = Path(__file__).resolve().parent
DOCS = {'DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md',
        'PROJECT_COMPLETED.md', 'BATCH_CONTINUOUS_P2.md'}
JOBS = ('linux_full', 'wine_full', 'linux_selected', 'wine_selected',
        'linux_pip', 'wine_pip', 'wine_ui', 'saved_review')
UI_POINTERS = {
    'passed': '/passed', 'complete_ui': '/complete_ui_validation',
    'private_isolation': '/private_state_isolated',
    'native_windows': '/native_windows_verified', 'source_drift': '/source_drift',
    'game_captures': '/game_captures', 'chat_requests': '/chat_requests',
    'source_before': '/source_sha256', 'source_after': '/source_sha256_after',
    'checks': '/checks', 'actual_checks': '/total_actual_checks',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    p = Path(path)
    require(p.is_absolute() and stat.S_ISREG(p.lstat().st_mode),
            'Explicit regular absolute public input required: ' + str(p))
    return p.read_bytes()


def ref(path):
    raw = read(path)
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def bound(reference):
    require(type(reference) is dict and set(reference) == {'path', 'bytes', 'sha256'},
            'Exact physical file_ref required')
    raw = read(reference['path'])
    require(len(raw) == reference['bytes'] and sha(raw) == reference['sha256'],
            'Immutable physical reference changed: ' + reference['path'])
    return raw


def pointer(value, path):
    require(type(path) is str and path.startswith('/'), 'Exact source JSON pointer required')
    for token in path[1:].split('/'):
        key = token.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if type(value) is list else value[key]
    return value


def relative(name):
    p = PurePosixPath(name)
    require(type(name) is str and '\\' not in name and name == p.as_posix()
            and p.parts and not p.is_absolute()
            and all(x not in ('.', '..', '.git') for x in p.parts),
            'Exact public POSIX archive/repository path required')
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finish-exit-file', type=Path, required=True)
    parser.add_argument('--finish-console', type=Path, required=True)
    parser.add_argument('--product-file', action='append', required=True,
                        help='ROOT explicit changed product/policy/metadata path; no enumeration or Git here')
    parser.add_argument('--public-file', action='append', nargs=2, default=[],
                        metavar=('ABSOLUTE_SOURCE_PATH', 'RELATIVE_ARCHIVE_PATH'),
                        help='ROOT explicit supplemental public evidence; no runtime/private directory scan')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.output.parent == LOCAL and not args.output.exists(), 'New external spec only')
    config = json.loads(read(HERE / 'source-inputs095.json'))
    for reference in config['pinned_source_inputs'].values():
        bound(reference)
    template = json.loads(bound(config['pinned_source_inputs']['template']))
    binding_reference = config['pinned_source_inputs']['recovery_binding']
    binding = json.loads(bound(binding_reference))
    require(binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
            and binding['actual_original_epoch_recovery'] is True,
            'Exact reviewed recovery SOURCE binding required')
    actual = binding['actual_inputs']
    paths = actual['global_output_plan']['paths']
    start_reference, final_reference = ref(paths['context_start']), ref(paths['context_final'])
    start, final = json.loads(bound(start_reference)), json.loads(bound(final_reference))
    require(start['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and final['status'] == 'PASS_ACTUAL_FULL095_AVAILABLE_NOT_NATIVE_WINDOWS'
            and final['available_checks_passed'] is final['complete_ui_validation'] is True,
            'Actual full095 finish PASS required before this assembler')
    require(read(args.finish_exit_file) in (b'0\n', b'0\r\n'), 'Actual captured finish raw0 required')
    read(args.finish_console)
    runner_reference = config['pinned_source_inputs']['recovery_runner']
    for context in (start, final):
        require(context['binding'] == binding_reference
                and context['final_context_runner'] == runner_reference
                and context['actual_original_epoch_recovery'] is True,
                'Started/final recovery source refs differ')
    recovery = binding['recovery_spec']
    original_context = json.loads(bound(recovery['original']['context']))
    require(start['started_at'] == final['started_at'] == original_context['started_at']
            and datetime.fromisoformat(start['started_at']) <= datetime.fromisoformat(start['recovery_started_at'])
            and start['recovery_started_at'] == final['recovery_started_at'],
            'Original actual epoch and recovery start must remain unchanged')
    for name in ('original_context', 'original_source_binding', 'original_context_runner'):
        key = {'original_context': 'context', 'original_source_binding': 'binding',
               'original_context_runner': 'runner'}[name]
        require(start[name] == final[name] == recovery['original'][key], 'Original epoch evidence changed')
    require(final['source_sha256'] == final['source_sha256_after'] == actual['source_sha256']
            and final['source_drift'] == [] and final['prior_failed_wine_full_preserved'] is True
            and final['recovery_contract_projection_verified'] is True,
            'Actual full095 source/recovery closure invalid')
    witness_ref = ref(paths['execution_witness'])
    witness = json.loads(bound(witness_ref))
    require(witness['format_version'] == 2 and witness['section'] == 95
            and witness['actual_root_observed_primary_exits'] is True
            and set(witness['executions']) == set(JOBS)
            and final['actual_root_primary_exits'] == witness
            and final['physical_primary_exit_files_verified'] == 8
            and final['exact_execution_contracts_verified'] is True,
            'Exactly eight actual ROOT execution proofs required')
    preserved = recovery['preserved_passed_executions']
    require(set(preserved) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip'}
            and start['preserved_passed_executions'] == final['preserved_passed_executions'] == preserved,
            'Four original successful observations must remain immutable')
    for job, row in preserved.items():
        require(json.loads(bound(row['observation'])) == witness['executions'][job],
                'Reused actual primary proof was altered: ' + job)
        if row['receipt'] is not None:
            bound(row['receipt'])
    failed = recovery['prior_failed_execution']
    require(start['prior_failed_execution'] == final['prior_failed_execution'] == failed,
            'Original failed Winefull was dropped or altered')
    failed_observation = json.loads(bound(failed['observation']))
    require(failed_observation['primary_exit_code'] == 1
            and failed_observation['primary_exit_code_captured'] is True
            and bound(failed_observation['exit_code_file']) in (b'1\n', b'1\r\n'),
            'Preserve actual Winefull first-attempt primary1; never count it as PASS')
    bindings = template['bindings']

    def add(role, reference, archive_path=None, kind=None):
        bound(reference)
        old = bindings.get(role, {})
        item = {'source_path': reference['path'], 'archive_path': relative(archive_path or old['archive_path']),
                'bytes': reference['bytes'], 'sha256': reference['sha256'],
                'kind': kind or old.get('kind', 'text'), 'public': True}
        require(role not in bindings or old.get('source_path') in (None, reference['path']),
                'Unexpected original role path change: ' + role)
        bindings[role] = item

    for role, old in tuple(bindings.items()):
        if old.get('source_path') is not None:
            add(role, {'path': old['source_path'], 'bytes': old['bytes'], 'sha256': old['sha256']})
    add('context_start', start_reference)
    add('context_final', final_reference)
    add('context_source_binding', binding_reference)
    add('context_final_runner', runner_reference, 'context/full095_context_recovery.py')
    output_role_keys = {'linux_full': 'linux_full', 'wine_full': 'wine_full',
        'linux_selected': 'linux_selected', 'wine_selected': 'wine_selected',
        'linux_pip_log': 'linux_pip', 'wine_pip_log': 'wine_pip',
        'root_primary_exits': 'execution_witness', 'ui_receipt': 'wine_ui',
        'ui_extra_acceptance': 'ui_extra_acceptance', 'ui_saved_review': 'saved_review_receipt',
        'ui_visual_review': 'visual_review', 'linux_full_console': 'linux_full_console',
        'wine_full_console': 'wine_full_console', 'ui_saved_console': 'saved_review_stdout'}
    for role, key in output_role_keys.items():
        add(role, ref(paths[key]))
    add('ui_preflight', config['pinned_source_inputs']['ui_prelaunch'])
    require(set(actual['execution_contracts']) == set(JOBS), 'Actual exact8 launch contracts required')
    for job in JOBS:
        entry, contract = witness['executions'][job], actual['execution_contracts'][job]
        require(entry['actual_root_observed_primary_exit'] is entry['primary_exit_code_captured']
                is entry['fresh_execution'] is True and type(entry['primary_exit_code']) is int
                and entry['primary_exit_code'] == 0 and entry['argv'] == contract['argv']
                and entry['cwd'] == contract['cwd'] == str(ROOT) and entry['runner'] == contract['runner'],
                'Actual closed exact primary contract required: ' + job)
        require(entry['stdout_log'] == ref(paths[contract['stdout_key']])
                and entry['exit_code_file'] == ref(contract['exit_code_path'])
                and bound(entry['exit_code_file']) in (b'0\n', b'0\r\n'),
                'Actual primary source/stdout/status changed: ' + job)
        require(datetime.fromisoformat(start['started_at']) <= datetime.fromisoformat(entry['started_at'])
                <= datetime.fromisoformat(entry['completed_at']) <= datetime.fromisoformat(final['completed_at']),
                'Actual primary execution outside original closed epoch: ' + job)
        if job in ('wine_full', 'wine_selected'):
            require(datetime.fromisoformat(entry['started_at']) >= datetime.fromisoformat(start['recovery_started_at']),
                    'Wine adapters cannot predate the actual recovery resume')
        add(template['primary_exit_roles'][job], entry['exit_code_file'])
        add('primary_console_' + job, entry['stdout_log'], 'primary-console/' + job + '.log', 'text')
        if entry['runner'] is not None:
            add('primary_runner_' + job, entry['runner'], 'primary-source/' + job + '.py', 'text')
    saved_execution = witness['executions']['saved_review']
    require(saved_execution['output_receipt'] == ref(paths['saved_review_receipt']), 'Saved actual output differs')
    add('ui_saved_verifier', saved_execution['runner'])
    saved = json.loads(bound(saved_execution['output_receipt']))
    input_spec_ref = saved['input_spec']
    require(input_spec_ref['path'] == actual['execution_contracts']['saved_review']['argv'][3],
            'Saved proof must bind actual planned control spec')
    add('ui_saved_input_spec', input_spec_ref, 'saved-review/actual-input-spec.json', 'json')
    ui = json.loads(read(paths['wine_ui']))
    template['contracts']['ui'] = UI_POINTERS.copy()
    require(all(pointer(ui, value) is not None for value in UI_POINTERS.values()), 'Actual UI producer pointer missing')
    require(ui['passed'] is ui['complete_ui_validation'] is True
            and ui['private_state_isolated'] is True and ui['native_windows_verified'] is False
            and ui['game_captures'] == ui['chat_requests'] == 0
            and ui['source_drift'] == [], 'Actual fullUI producer not available PASS')
    require(type(ui['checks']) is list and len(ui['checks']) == ui['total_actual_checks'] == final['ui_checks'],
            'Actual fullUI checks must come from physical final receipt, never prefilled counts')
    template['expected_actual_UI_checks'] = len(ui['checks'])
    template['actual_UI_source_contract_assertions'] = [
        {'pointer': '/source_guard095/sha256', 'expected': bindings['source095_guard']['sha256']},
        {'pointer': '/source_guard095/before', 'expected': actual['source_sha256']},
        {'pointer': '/source_guard095/after', 'expected': actual['source_sha256']},
        {'pointer': '/source_guard095/source_drift', 'expected': []},
        {'pointer': '/source_guard095/read_error', 'expected': None},
        {'pointer': '/legacy085_prefix4217_and090_additional66_preserved', 'expected': True},
        {'pointer': '/legacy090_source_fields_are_historical', 'expected': True},
        {'pointer': '/historical093_original_Wine_shell_status', 'expected': None},
    ]
    for assertion in template['actual_UI_source_contract_assertions']:
        require(pointer(ui, assertion['pointer']) == assertion['expected'], 'Actual qualified fullUI source contract differs')
    acceptance = final['actual_ui_acceptance']
    receipts = acceptance['receipts']
    require(len(receipts) == 2 and {x['kind'] for x in receipts} == {'saved-validation', 'visual-review'},
            'Exact saved/visual actual acceptance required')
    for index, row in enumerate(receipts):
        role = 'ui_saved_review' if row['kind'] == 'saved-validation' else 'ui_visual_review'
        require(row['file'] == ref(bindings[role]['source_path']), 'Actual normalized proof reference differs')
        template['context_check_links'][role] = '/actual_ui_acceptance/receipts/' + str(index) + '/file'
    template['actual_UI_output_roles'], template['actual_PNG_roles'] = [], []
    for index, row in enumerate(acceptance['artifacts']):
        require(row['kind'] in ('native-evidence', 'screenshot'), 'Unknown actual UI artifact kind')
        role = 'actual_ui_output_' + str(index)
        add(role, row['file'], 'actual-ui-output/' + str(index).zfill(6) + '-' + Path(row['file']['path']).name,
            'json' if Path(row['file']['path']).suffix == '.json' else 'binary')
        template['actual_UI_output_roles'].append(role)
        if row['kind'] == 'screenshot':
            template['actual_PNG_roles'].append(role)
    require(len(template['actual_PNG_roles']) == len([x for x in binding['root_spec']['ui']['required_saved_outputs']
                                                   if x['kind'] == 'screenshot']),
            'Actual screenshot artifacts disagree with declared final UI source')
    require(final['completed_working_tree_chain'] == actual['completed_working_tree_chain'], 'Actual section chain changed')
    for row, declared in zip(final['completed_working_tree_chain'], template['sections']):
        require(row['section'] == declared['number'], 'Actual section chain order changed')
        for key, role in (('receipt', declared['receipt_role']), ('closure', declared['closure_role']),
                          ('source_guard', declared['source_role'])):
            add(role, row[key])
    template['selected_receipt_kinds'] = {'linux_selected': 'last_json_line', 'wine_selected': 'last_json_line'}
    template['public_packets'] = config['public_packets']
    for packet in template['public_packets']:
        require(sha(read(packet['manifest_path'])) == packet['manifest_sha256'], 'Pinned explicit SOURCE manifest changed')
    # Original failed outcome is separate history, not one of the eight passing jobs.
    for key, reference in recovery['original'].items():
        add('original_epoch_' + key, reference, 'original-epoch/' + Path(reference['path']).name,
            'json' if Path(reference['path']).suffix == '.json' else 'text')
    for key, reference in failed.items():
        if key != 'execution_name':
            add('failed_wine_full_' + key, reference, 'failed-first-wine-full/' + Path(reference['path']).name,
                'json' if Path(reference['path']).suffix == '.json' else 'text')
    for key in ('stdout_log', 'exit_code_file'):
        reference = failed_observation[key]
        add('failed_wine_full_' + key, reference, 'failed-first-wine-full/' + Path(reference['path']).name, 'text')
    for job, row in preserved.items():
        add('preserved_primary_' + job, row['observation'], 'original-passed-primary/' + job + '-observation.json', 'json')
    for name, reference in config['supplemental_public_inputs'].items():
        add('public_source_' + name, reference, 'source-preparation/supplemental/' + name + '-' + Path(reference['path']).name,
            'json' if Path(reference['path']).suffix == '.json' else 'text')
    add('finish_primary_exit', ref(args.finish_exit_file), 'context/root-finish.exit-code', 'text')
    add('finish_console', ref(args.finish_console), 'context/root-finish.log', 'text')
    add('archive_spec_assembler_source', ref(Path(__file__).resolve()), 'archive-source/assemble_archive_spec095.py', 'text')
    add('archive_spec_assembler_input_config', ref(HERE / 'source-inputs095.json'), 'archive-source/assembler-source-inputs095.json', 'json')
    for name in ('README095.md', 'source-findings095.json',
                 'public-artifacts-manifest-source-preparation095.json', 'handoff-source-preparation095.json'):
        add('archive_spec_assembler_packet_' + name.replace('.', '_'), ref(HERE / name),
            'source-preparation/archive-spec-assembler/' + name,
            'json' if name.endswith('.json') else 'text')
    for index, (path, archive_name) in enumerate(args.public_file):
        p = Path(path)
        require(p.is_relative_to(LOCAL) or p.is_relative_to(Path('/workspace/.compat'))
                or p.is_relative_to(ROOT / 'research') or p.is_relative_to(ROOT / 'verification'),
                'Explicit supplemental public evidence root required')
        add('root_additional_public_' + str(index), ref(p), archive_name,
            'json' if p.suffix == '.json' else 'binary')
    require(len(args.product_file) == len(set(args.product_file)), 'Duplicate explicit batch product path')
    template['batch_product_and_metadata_files'] = []
    section_archives = [json.loads(bound(row['receipt']))['research_archive'] for row in final['completed_working_tree_chain']]
    for name in args.product_file:
        name = relative(name)
        require(name not in DOCS and not name.startswith('verification/full-095/')
                and not any(name == prefix or name.startswith(prefix + '/') for prefix in section_archives)
                and name not in {str(Path(row['receipt']['path']).relative_to(ROOT)) for row in final['completed_working_tree_chain']},
                'Existing archive/generated metadata cannot be batch product role')
        reference = ref(ROOT / name)
        template['batch_product_and_metadata_files'].append({'path': name, 'bytes': reference['bytes'], 'sha256': reference['sha256']})
    require(all(item['public'] is True and item['source_path'] is not None for item in bindings.values()),
            'Original pending archive role remains unresolved')
    template['status'] = 'ROOT_ACTUAL_FULL095_BINDINGS_READY'
    # The completed spec claims no archive, commit or push execution.
    raw = (json.dumps(template, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with args.output.open('xb') as stream:
        stream.write(raw)
    require(read(args.output) == raw, 'Exclusive completed spec bytes changed')
    print(json.dumps({'metadata_assembly_only': True, 'actual_full_context_pass_read': True,
                      'output': ref(args.output), 'bindings': len(bindings),
                      'actual_UI_outputs': len(template['actual_UI_output_roles']),
                      'actual_UI_checks': template['expected_actual_UI_checks'],
                      'archive_helper_executed': False, 'project_calls': 0, 'Wine_calls': 0,
                      'Git_calls': 0, 'tracked_mutations': 0, 'commit_or_push_performed': False}))


if __name__ == '__main__':
    main()
