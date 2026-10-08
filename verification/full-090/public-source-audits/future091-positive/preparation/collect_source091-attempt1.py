"""Read named source and already-saved outputs; no project imports/calls."""
import ast
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
S16 = Path('/workspace/.continuation/p2-section088-candidate-audit')
M60 = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def write(name, data):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def named(relative):
    return subprocess.check_output(['git', 'show', f'{COMMIT}:{relative}'], cwd=REPO)

assert not (HERE / 'visibility-source-receipt091.json').exists()
paths = [f'rouge/{name}.py' for name in ('app', 'operator_engine', 'damage', 'relics',
    'catalog', 'estimate', 'sp_events', 'timing', 'amiya_continuous_reference', 'offline_scope')]
paths += ['rouge/data/operator-profiles.json', 'rouge/data/catalog.json', 'rouge/data/relic-mechanics.json']
bound = {}
bindings = []
fixed60 = json.loads((M60 / 'fixed-source-index088.json').read_bytes())
fixedmap = {row['path']: row for row in fixed60['files']}
static16 = json.loads((S16 / 'continuous-condition-static088.json').read_bytes())
old16map = {str(Path(row['source_path']).relative_to(REPO)): row for row in static16['source_index']}
for relative in paths:
    raw = named(relative)
    bound[relative] = raw
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    row = {'root_relative_path': relative, 'named_commit': COMMIT,
        'git_blob_sha1': blob, 'bytes': len(raw), 'sha256': sha(raw),
        'source088_matrix60_baseline_sha256': fixedmap[relative]['sha256'],
        'source088_matrix60_bytes_equal_named_current87': fixedmap[relative]['sha256'] == sha(raw),
        'source088_original16_sha256': old16map[relative]['sha256'],
        'source088_original16_bytes_equal_named_current87': old16map[relative]['sha256'] == sha(raw),
        'working_tree_matches_this_named_snapshot_at_collection': (REPO / relative).read_bytes() == raw}
    assert row['source088_matrix60_bytes_equal_named_current87']
    assert row['source088_original16_bytes_equal_named_current87']
    if relative.endswith('.py'):
        target = HERE / 'source87' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['copied_source_path'] = str(target)
    else:
        row['large_data_body_omitted_exact_named_git_reconstruction_available'] = True
    bindings.append(row)
write('source-reconstruction091.json', {'status': 'PASS_NAMED_ACTUAL87_AND_BOTH_EXISTING088_SOURCE_BINDINGS',
    'named_root_commit': COMMIT, 'files': bindings, 'file_count': len(bindings),
    'source088_16_captured_commit': static16['captured_git_HEAD'],
    'source088_matrix60_baseline_commit': fixed60['baseline_commit'],
    'reconstruct_data': 'git cat-file blob <git_blob_sha1>; verify byte count and sha256 before JSON reading',
    'new_project_calls': 0, 'working_tree_may_advance_independently': True})

app = bound['rouge/app.py'].decode()
tree = ast.parse(app)
parents = {}
for node in ast.walk(tree):
    for child in ast.iter_child_nodes(node):
        parents[child] = node

def function(node):
    while node in parents:
        node = parents[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
    return None

refs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr == 'continuous_attacks':
        parent = parents.get(node)
        refs.append({'line': node.lineno, 'expression': ast.get_source_segment(app, parent),
            'function': function(node), 'context': type(node.ctx).__name__})
refs.sort(key=lambda row: row['line'])
mutators = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == 'continuous_attacks'):
        mutators.append({'line': node.lineno, 'method': node.func.attr,
            'expression': ast.get_source_segment(app, node), 'function': function(node)})
assert [row['method'] for row in mutators] == ['setChecked', 'isChecked']
assert mutators[0]['expression'] == 'self.continuous_attacks.setChecked(True)'
assert mutators[0]['function'] == 'make_damage_tab'
assert mutators[1]['function'] == 'calculate'
write('app-continuous-control-all-references091.json', {
    'status': 'PASS_EXHAUSTIVE_ATTRIBUTE_AST_NO_OPERATOR_SKILL_OR_RUN_RESET',
    'named_root_commit': COMMIT, 'app_sha256': sha(bound['rouge/app.py']),
    'all_self_continuous_attribute_references': refs, 'direct_widget_method_calls': mutators,
    'state_initialization': {'line': 566, 'widget': 'QCheckBox', 'checked_default': True, 'checked_line': 567},
    'visibility': {'line': 960, 'expression': "current.get('sp_type')=='INCREASE_WHEN_ATTACK'", 'form_row_apply_line': 967},
    'serialization': {'line': 1028, 'always_emitted': True, 'native_bool_producer': 'self.continuous_attacks.isChecked()'},
    'transition_dataflow': [
        {'source': 'operator.currentIndexChanged', 'line': 524, 'target': 'update_operator', 'target_lines': [791, 847]},
        {'source': 'skill.currentIndexChanged', 'line': 553, 'target': 'skill_changed', 'target_lines': [854, 856]},
        {'source': 'update_operator/skill_changed', 'target': 'update_skill_options', 'target_lines': [949, 998]},
        {'source': 'update_skill_options', 'target': 'damage_form.setRowVisible', 'line': 967},
        {'source': 'update_skill_options', 'target': 'calculate', 'line': 998},
        {'source': 'calculate', 'target': 'calculate_damage public dispatcher', 'always_serializes_hidden_bool': True}],
    'not_a_Qt_execution': True, 'no_hidden_inactivity_assumption': True, 'new_project_calls': 0})

catalogue = json.loads(bound['rouge/data/catalog.json'])['operators']
profiles = json.loads(bound['rouge/data/operator-profiles.json'])['operators']
mechanics = json.loads(bound['rouge/data/relic-mechanics.json'])
operator_data = []
for owner in ('char_002_amiya', 'char_1050_chen3', 'mechanist', 'silverash',
        'char_1044_hsgma2', 'char_196_sunbr', 'char_1029_yato2'):
    profile = {**profiles[owner], **catalogue.get(owner, {})}
    row = {'owner': owner, 'id': profile['id'], 'profession': profile['profession'],
        'phases_max_level': [phase['max_level'] for phase in profile['phases']],
        'skills': [{'number': i + 1, 'unlock_elite': skill.get('unlock_elite', i),
            'first_level_sp_type': skill['levels'][0]['sp_type'],
            'last_level_sp_type': skill['levels'][-1]['sp_type'], 'last_name': skill['levels'][-1]['name']}
            for i, skill in enumerate(profile['skills'])]}
    if owner == 'char_002_amiya':
        row['emotion_absorption_talent_group_original'] = profile['talents'][0]
        row['eligibility_from_direct_source'] = {
            'E0_E1_last_eligible_at_potential1': {'name': '？？？', 'values': {}},
            'E2L1_potential1': {'name': '情绪吸收', 'attack_sp': 2.0},
            'E2L1_potential6': {'name': '情绪吸收', 'attack_sp': 3.0},
            'E0_E1_talent_attack_credit_is_zero': True,
            'selection_source': 'operator_engine.py:13–26 eligibility plus Combat.talent:151 default0',
            'project_selected_talents_called': False}
    operator_data.append(row)
write('bounded-curated-source-data091.json', {
    'status': 'SOURCE_JSON_PROJECTION_NOT_PRODUCT_HELPER_EVALUATION', 'operators': operator_data,
    'warrior_attack_sp_relic67': mechanics['relics']['rogue_6_relic_legacy_67'],
    'retired_received_sp_relic118': mechanics['relics']['rogue_6_relic_legacy_118'],
    'raw_table_fresh_network_checked': False,
    'data_origin': 'Exact named root87 normalized project data with source URLs/raw_buff selectors retained',
    'new_project_calls': 0})

evidence_sources = [
    (S16, 'public-source16.jsonl.gz', 'original088-public16.jsonl.gz'),
    (S16, 'public-source16-summary.json', 'original088-public16-summary.json'),
    (S16, 'saved-source16-comparison.json', 'original088-saved16-comparison.json'),
    (S16, 'source-handoff088.json', 'original088-source-handoff.json'),
    (M60, 'baseline-public60.jsonl.gz', 'original088-baseline-public60.jsonl.gz'),
    (M60, 'matrix-plan088.json', 'original088-matrix-plan60.json'),
    (M60, 'fixed-source-index088.json', 'original088-fixed-source-index.json'),
    (Path('/workspace/.continuation/p2-continuous-attacks-088-independent'),
        'preapi-qualification-correction088.json', 'independent088-retired-received-correction.json')]
transport = []
for origin, oldname, newname in evidence_sources:
    source = origin / oldname
    target = HERE / 'saved088' / newname
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes()
    target.write_bytes(raw)
    transport.append({'original_source_path': str(source), 'source_path': str(target),
        'archive_path': target.relative_to(HERE).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
write('saved-evidence-transport091.json', {'status': 'PASS_EXISTING088_BYTES_COPIED_NO_RECALCULATION',
    'files': transport, 'source16_used_as_existing_verified_result': True,
    'matrix60_used_as_existing_baseline_source_result_not_final088_product': True,
    'new_API_formatter_helper_calls': 0})

rs16 = [json.loads(line) for line in gzip.decompress((S16 / 'public-source16.jsonl.gz').read_bytes()).splitlines()]
rs60 = [json.loads(line) for line in gzip.decompress((M60 / 'baseline-public60.jsonl.gz').read_bytes()).splitlines()]
assert len(rs16) == 16 and len(rs60) == 60
def projection(row, index_key):
    result = row['result']
    skill = result['estimate']['skill']
    return {'index': row[index_key], 'label': row['label'], 'input': row['input'],
        'outcome': row['outcome'], 'whole_public_json_sha256': sha(json.dumps(result, ensure_ascii=False, separators=(',', ':')).encode()),
        'whole_native_tree_sha256': sha(json.dumps(row['result_typed'], ensure_ascii=False, separators=(',', ':')).encode()),
        'report_sha256': {name: sha(value.encode()) for name, value in row['reports'].items()},
        'caller_native_unchanged': row['input_typed_before'] == row['input_typed_after'],
        'initial_recharge_cycle': {key: skill[key] for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds')},
        'amiya_reference': result.get('amiya_continuous_reference'),
        'relic_resolution': result.get('relic_resolution'),
        'sp_events_in_estimate': 'sp_events' in result['estimate']}
selected16 = [projection(row, 'index') for row in rs16 if row['index'] in (1, 2, 9, 10, 13, 14)]
selected60 = [projection(row, 'case') for row in rs60 if row['case'] in (15, 16, 17, 18, 19, 20, 33, 34, 39, 40, 41, 42)]
m16 = {row['index']: row for row in selected16}
m60 = {row['index']: row for row in selected60}
assert m16[9]['input']['continuous_attacks'] is False and m16[10]['input']['continuous_attacks'] is True
assert m16[9]['initial_recharge_cycle'] == {'initial_seconds': 15.0, 'recharge_seconds': 30.0, 'cycle_seconds': 60.0}
assert m16[10]['initial_recharge_cycle'] == {'initial_seconds': 6.000000000000002, 'recharge_seconds': 11.2, 'cycle_seconds': 41.2}
assert m16[1]['initial_recharge_cycle']['initial_seconds'] is None
assert m16[2]['initial_recharge_cycle']['initial_seconds'] == 8.433333333333334
assert m60[33]['input']['continuous_attacks'] is False and m60[34]['input']['continuous_attacks'] is True
assert m60[33]['initial_recharge_cycle']['initial_seconds'] == 7.0
assert m60[34]['initial_recharge_cycle']['initial_seconds'] == 2.9999999999999996
assert m60[19]['whole_native_tree_sha256'] == m60[20]['whole_native_tree_sha256']
assert m16[13]['whole_native_tree_sha256'] == m16[14]['whole_native_tree_sha256']
write('existing-saved-output-projection091.json', {
    'status': 'PASS_READ_ONLY_EXISTING_BOOL_POSITIVES_AND_QUALIFIED_INACTIVE_SOURCE_PROJECTIONS',
    'source16_rows': selected16, 'baseline60_rows': selected60,
    'source16_bool_Amiya_E2_hidden_positive': True,
    'baseline60_bool_chen3_S3_warrior67_hidden_positive': True,
    'legacy_mechanist_checkbox_can_be_disabled_then_operator_switched': 'Static Qt producer/control transition only; actual switch not executed',
    'E0_E1_saved_reference_original_inputs_are_text_not_new_UI_bool_calls': True,
    'reference_only_Gummy_received118_False_True_whole_native_same': True,
    'no_recomputed_results_or_regenerated_report_texts': True,
    'new_API_formatter_helper_calls': 0})

spans = {
    'rouge/app.py': [(520, 568), (778, 857), (925, 940), (949, 999), (1024, 1039), (1090, 1113)],
    'rouge/operator_engine.py': [(13, 28), (149, 153), (1297, 1345), (1439, 1476)],
    'rouge/relics.py': [(18, 23), (55, 61), (93, 123), (286, 308)],
    'rouge/damage.py': [(271, 282), (292, 304)],
    'rouge/estimate.py': [(90, 102), (172, 186), (198, 207)],
    'rouge/offline_scope.py': [(1, 14), (34, 47)],
    'rouge/amiya_continuous_reference.py': [(5, 21), (73, 85)],
    'rouge/sp_events.py': [(85, 96), (128, 139), (171, 181)]}
out = []
for relative, ranges in spans.items():
    lines = bound[relative].decode().splitlines()
    for start, end in ranges:
        out.append(f'--- {COMMIT}:{relative}:{start}-{end} SHA256={sha(bound[relative])} ---')
        out.extend(f'{i + 1}: {lines[i]}' for i in range(start - 1, min(end, len(lines))))
(HERE / 'source-excerpts091.txt').write_text('\n'.join(out) + '\n')
write('visibility-source-receipt091.json', {
    'status': 'POSITIVE_READ_ONLY_P2_UI_DECLARATION_CANDIDATE_FUTURE91_PENDING',
    'numbered_section_completed': False, 'product_draft_created': False,
    'named_actual_source_commit': COMMIT,
    'positive_dataflow': 'MechanistS1 visible False persists through operator/skill change; Amiya naturalS1 row hidden solely by sp_type while native bool stays serialized and changes existing public initial/recharge/cycle.',
    'second_positive': 'Chen3 naturalS3 + correctly prepared active warrior attack-SP relic67: hidden bool changes saved initial seconds7 vs2.9999999999999996.',
    'source_call_counts': {'API': 0, 'helper': 0, 'formatter': 0, 'tests': 0, 'Qt': 0, 'Wine': 0, 'network': 0},
    'actual_GUI_transition_verified': False, 'native_game_mechanism_newly_asserted': False,
    'original_UI090107_modified': False, 'private_application_state_touched': False,
    'future91_after_full90_only': True,
    'safe_conservative_visibility_candidate': "A valid selected implemented skill with sp_type in {'INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME'}; keeps input bool/default, shows inactive natural cases conservatively without asserting extra SP.",
    'precise_visibility_candidate': 'Attack-SP OR natural Amiya actual source/reference consumer OR natural extended owner with prepare-resolved active attack_sp credit. Do not substitute raw held-ID or raw effects for processed partition/matches rules.',
    'unclosed_minimal_scope': 'A precise all-owner prepared-rule visibility helper/refactor is not implemented or executed here; post90 draft must preserve current input/order/unknown references and respond to relic changes.',
    'qualification_boundaries': [
        'Amiya E2L1+ selected情绪吸收 has attack credit2 atP1 /3 atP6. All three actual natural skills consume branch; S3 nonrepeat can mask recharge/cycle, do not infer initial inactivity.',
        'Amiya E0/E1 has no情绪吸收 attack credit. It is not a proven extra-SP numerical positive; existing bounded continuousS1 reference still exposes enabled-condition metadata, even with unknown actual native clock. E0 is not blanket inactive.',
        'Chen3 S2 unlockE1 /S3 unlockE2; actual warrior67 profession selector has no elite gate, so E0S1 cannot be labelled inactive solely forE0. The saved bool positive is specifically E2S3; E1/E0 new bool calculation not executed.',
        'Legacy Silverash naturalS3 without attack-SP/event outgoing credits is saved whole-native inactive despite hidden state; display visibility alone does not claim numerical activation.',
        'No-SP category8 deployment/passive cases have no natural/Attack-SP charge branch; no outgoing/next-attack event producer is established for them in active offline scope.',
        'Received/event118 is normalized raw received_sp but reference-only under offline_scope; prepare overwrites _relic_rules with active rules. Gummy False/True remains saved whole same; no active public tail is inferred.',
        'Native defensive/periodic incoming_interval branch takes precedence over outgoing continuous branch; 39/40 saved native remains same.',
        'Native target acquisition, SP release ordering, attachment, fullclock and unknown totals remain existing source limitations.']})
print(json.dumps({'status': 'SOURCE_READ_ONLY_POSITIVE', 'named_commit': COMMIT,
    'application_calls': 0, 'Qt_Wine': 0, 'receipt': describe(HERE / 'visibility-source-receipt091.json')}, ensure_ascii=False))
