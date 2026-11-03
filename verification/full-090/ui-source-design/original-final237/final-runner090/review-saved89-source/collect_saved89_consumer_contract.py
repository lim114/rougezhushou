"""Static source/saved-data contract only; imports no project code."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '5e2ff697402d06e78b239e01f0b4307b50dd5633'
DESIGN = Path('/workspace/.continuation/root-transport-preparation090/saved89-five-state-UI-consumer-design090.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def native(value):
    if type(value) is dict:
        return {'type': 'dict', 'items': [[native(k), native(v)] for k, v in value.items()]}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [native(v) for v in value]}
    if type(value) is float:
        return {'type': 'float', 'hex': value.hex()}
    return {'type': type(value).__name__, 'value': value}


def write(name, value):
    with (OUT / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


source_names = ['rouge/app.py', 'rouge/run_state.py', 'rouge/operator_summary.py',
                'rouge/catalog.py', 'rouge/data/catalog.json', 'rouge/data/operator-profiles.json']
sources = {}
bindings = []
for name in source_names:
    raw = subprocess.check_output(['git', '-C', str(REPO), 'show', COMMIT + ':' + name])
    assert (REPO / name).read_bytes() == raw, name
    sources[name] = raw
    bindings.append({'root_path': name, 'source_path': str(REPO / name), 'named_commit': COMMIT,
                     'bytes': len(raw), 'sha256': sha(raw),
                     'current_working_bytes_equal_named_commit_at_static_read': True})
assert sha(sources['rouge/app.py']) == '6a107fa37d2c21b9160131aa8c901fc2342ef7a422c3134dc0579ea24f4b56a2'
assert sha(sources['rouge/run_state.py']) == '20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9'
profiles = json.loads(sources['rouge/data/operator-profiles.json'])['operators']
catalog = json.loads(sources['rouge/data/catalog.json'])['operators']
for owner, profile in catalog.items():
    # This is plain source-JSON projection of catalog.py's overlay, not a helper call.
    profiles[owner] = {**profiles[owner], **profile}
assert 'mechanist' in profiles and 'char_151_myrtle' in profiles
profile = profiles['mechanist']
plan = json.loads(DESIGN.read_bytes())
saved_path = Path(plan['original_saved38']['source_path'])
compressed = saved_path.read_bytes()
assert len(compressed) == plan['original_saved38']['bytes']
assert sha(compressed) == plan['original_saved38']['sha256'] == '3628dfb4dc36f360b05640f0471eb1612ec728541cb7a919e9564bcbcf0b3e51'
saved = json.loads(gzip.decompress(compressed))
by_sequence = {r['sequence']: r for r in saved['records']}
selected = plan['selected_saved_records']
assert len(selected) == 5 and [r['saved_sequence'] for r in selected] == [19, 9, 3, 22, 6]
account_fields = {'elite': 2, 'level': 60, 'trust': 100, 'potential': 1,
                  'module_id': None, 'module_level': 0}
account_ranks = {'1': 10, '2': 10, '3': 10}
contract_rows = []
selected_bindings = []
for row in selected:
    original = by_sequence[row['saved_sequence']]
    assert original['role'] == 'subject_apply'
    assert row['state_native'] == original['state_after_typed']
    assert native(row['state']) == row['state_native']
    assert row['observed_native'] == original['observed_before_typed']
    state = row['state']
    assert type(state['crew_count']) is int
    assert all(m['scope'] == 'run' and m['sources'] == {} and
               m['invalid_fields'] == [] and m['invalid_skill_ranks'] == []
               for m in state['operators'].values())
    roster = [key for key, member in state['operators'].items()
              if key in profiles and member.get('present', True) and member.get('scope') != 'account']
    flags = {owner: state['operators'].get(owner, {}).get('present')
             for owner in ('mechanist', 'char_151_myrtle')}
    selected_bindings.append({'saved_sequence': row['saved_sequence'], 'label': row['label'],
                              'state_native_sha256': sha(json.dumps(row['state_native'], ensure_ascii=False).encode()),
                              'original_saved_native_tree_exact': True,
                              'observed_crew_native': native(row['observed']['crew_count']),
                              'stored_crew_native': native(state['crew_count']),
                              'member_flags_native': native(flags), 'recruited_ids_expected': roster,
                              'public_synthetic_state_not_native_OCR': True})
    for use_run in (False, True):
        member = state['operators'].get('mechanist') if use_run else None
        if member and not member.get('present', True):
            member = None
        if member:
            current = {k: v for k, v in member['fields'].items() if k not in member.get('invalid_fields', [])}
            ranks = {k: v for k, v in member.get('skill_ranks', {}).items()
                     if k not in member.get('invalid_skill_ranks', [])}
            fields = {**account_fields, **current}
            confirmed = list(current)
            state_scope = 'run'
        else:
            fields, ranks, confirmed, state_scope = dict(account_fields), dict(account_ranks), None, 'account_fixture'
        elite = fields.get('elite', len(profile['phases']) - 1)
        maximum = profile['phases'][elite]['max_level']
        level = fields.get('level', maximum)
        assert 1 <= level <= maximum
        skill_choices = [i + 1 for i, s in enumerate(profile['skills']) if s.get('unlock_elite', i) <= elite]
        selected_skill = fields.get('selected_skill', 1)
        assert selected_skill in skill_choices
        rank = ranks.get(str(selected_skill), ranks.get(selected_skill, 10 if elite == 2 else 7))
        module_label = '未装备模组' if profile['modules'] else '此数据档案无可装备模组'
        suffix = '（账号档案参考，本局未确认）'
        trust_label = f"{fields['trust']}%（读取）"
        potential_label = str(fields['potential'])
        if member:
            if 'module_id' not in confirmed:
                module_label += suffix
            if 'trust' not in confirmed:
                trust_label += suffix
            if 'potential' not in confirmed:
                potential_label += suffix
        contract_rows.append({
            'saved_sequence': row['saved_sequence'], 'saved_label': row['label'],
            'use_run_training': use_run, 'owner_read_back': 'mechanist',
            'roster_expected': roster, 'member_flags_native': native(flags),
            'stored_crew_native': native(state['crew_count']),
            'summary_crew_line_expected': f"本局队伍：当前已识别 {sum(m.get('present', True) for m in state['operators'].values())} / {state['crew_count']} 人",
            'current_state_source_expected': state_scope,
            'current_fields_expected': fields, 'current_skill_ranks_expected': ranks,
            'run_confirmed_fields_expected_if_run': confirmed,
            'training_conditions_expected_after_update_operator': {'elite': elite, 'level': level,
                'trust': fields.get('trust', 100), 'potential': fields.get('potential', 1),
                'module_id': fields.get('module_id'), 'module_level': fields.get('module_level', 0)},
            'skill_choice_numbers_expected': skill_choices, 'selected_skill_expected': selected_skill,
            'skill_rank_expected': rank,
            'rank_label_expected': (f'等级 {rank}' if rank <= 7 else f'专精 {rank - 7}') +
                ('（读取）' if str(selected_skill) in ranks or selected_skill in ranks else '（未确认，档案预览）'),
            'elite_label_expected': f'精英 {elite}', 'trust_label_expected': trust_label,
            'potential_label_expected': potential_label, 'module_label_expected': module_label,
            'levels_widget_max_expected': maximum,
            'no_current_runstate_constructor_apply_or_game_observation_executed': True})
write('expected-ten-state-contract089.json', {
    'status': 'STATIC_DATA_EXPECTATIONS_NOT_MAINWINDOW_EXECUTION',
    'named_actual90_source_commit': COMMIT, 'rows': contract_rows, 'row_count': 10,
    'account_fixture_explicit_fields': account_fields, 'account_fixture_explicit_ranks': account_ranks,
    'account_fixture_required_source': 'Isolated operator_observations account/preview dictionary, not real private state.',
    'preconditions': ['skill_override=False', 'level_override=False', 'display_operator=None',
                      'deepcopy exact selected full saved state into existing isolated window.run.state',
                      'select mechanist and update_operator(preserve_level=False)',
                      'No inferred actual helper/API invocation count from these action steps'],
    'selected_saved_native_bindings': selected_bindings,
    'present_member_invalid_lists_empty_actual': True,
    'invalid_field_and_rank_filter_extra_branch_is_source_only_not_measured_here': True,
    'future_MainWindow_bootstrap_ctor_and_apply_counts_separate_from_snapshot_consumer': True,
    'original_source89_unpatched_case1_to5_used_as_UI_fixtures': False,
    'no_original_saved38_or_any_calls_recomputed': True,
    'new_ctor_apply_API_helper_formatter_tests_Qt_Wine_calls': 0})
write('source-hashes089-consumer.json', {'status': 'NAMED_ACTUAL90_SELECTED_SOURCE_HASH_BOUND',
    'named_source_commit': COMMIT, 'files': bindings,
    'selected_snapshot_projection': {'source_path': str(DESIGN), 'bytes': len(DESIGN.read_bytes()), 'sha256': sha(DESIGN.read_bytes())},
    'original_author_saved38_gzip': {'source_path': str(saved_path), 'bytes': len(compressed), 'sha256': sha(compressed)},
    'new_project_calls': 0, 'real_private_state_read': False})
with (OUT / 'source-excerpts089-consumer.txt').open('x', encoding='utf-8') as handle:
    for name, ranges in (
        ('rouge/app.py', [(739, 744), (767, 847)]),
        ('rouge/run_state.py', [(372, 445), (564, 592)]),
        ('rouge/operator_summary.py', [(1, 49)]),
        ('rouge/catalog.py', [(1, 20)]),
    ):
        lines = sources[name].decode().splitlines()
        for start, end in ranges:
            handle.write(f'{COMMIT}:{name}:{start}-{end} SHA256={sha(sources[name])}\n')
            for i in range(start, min(end, len(lines)) + 1):
                handle.write(f'{i}: {lines[i - 1]}\n')
            handle.write('\n')
print(json.dumps({'status': 'STATIC_DATA_SOURCE_CONTRACT_READY', 'states': 10,
                  'profile_module_count': len(profile['modules']), 'new_project_calls': 0}))
