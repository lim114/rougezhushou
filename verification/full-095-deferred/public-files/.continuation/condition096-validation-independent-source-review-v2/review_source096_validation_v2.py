"""Independent SOURCE inspection only: do not import or execute inspected code."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
PACKET = Path('/workspace/.continuation/p2-condition096-validation-source-pending-v2')
OLD = Path('/workspace/.continuation/p2-condition096-validation-source-pending-v1')
CANDIDATE = Path('/workspace/.continuation/p2-condition096-candidate-v1')
REPO = Path('/workspace/rougezhushou')
REPORT = HERE / 'formal-source-review-validation096-v2.json'
checks = []

def reference(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def matches(row):
    return reference(row['path']) == {key: row[key] for key in ('path', 'bytes', 'sha256')}

def ordered_typed_json(value):
    """Reviewer-owned JSON identity; no target native codec is invoked."""
    kind = type(value)
    if kind is dict:
        return ('dict', tuple((ordered_typed_json(k), ordered_typed_json(v)) for k, v in value.items()))
    if kind in (list, tuple):
        return (kind.__name__, tuple(ordered_typed_json(v) for v in value))
    if kind is float:
        return ('float', value.hex())
    return (kind.__name__, value)

def same(left, right):
    return ordered_typed_json(left) == ordered_typed_json(right)

def record(identifier, condition, explanation, evidence=None):
    checks.append({'id': identifier, 'status': 'PASS' if condition else 'BLOCK',
                   'finding': explanation, 'evidence': evidence})

def parsed(path):
    text = Path(path).read_text(encoding='utf-8')
    return text, ast.parse(text)

def segment(text, tree, name):
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    return ast.get_source_segment(text, node)

def has_all(text, pieces):
    return all(piece in text for piece in pieces)

manifest_path = PACKET / 'public-artifacts-manifest-validation096-v2.json'
manifest = load(manifest_path)
handoff = load(PACKET / 'handoff-validation096-v2.json')
plan = load(PACKET / 'condition096-validation-plan.json')
binding = load(PACKET / 'condition096-binding-template.json')
correction = load(PACKET / 'source-correction-record096-v2.json')
clarification_path = Path('/workspace/.continuation/condition096-validation-v2-codec-span-clarification.json')
clarification = load(clarification_path)
gap_path = Path('/workspace/.continuation/condition096-validation-source-gap-review-v1/source-gap-review-condition096.json')
gap = load(gap_path)
guard_path = Path('/workspace/.continuation/root-source-095-v2.json')
guard = load(guard_path)
sources = {}
trees = {}
for name in ('linux-condition096-worker-pending.py', 'compare-condition096-linux-pending.py', 'wine-condition096-window-pending.py'):
    sources[name], trees[name] = parsed(PACKET / name)
wine = sources['wine-condition096-window-pending.py']
worker = sources['linux-condition096-worker-pending.py']
comparator = sources['compare-condition096-linux-pending.py']
wtree = trees['wine-condition096-window-pending.py']
def wine_function(name):
    return segment(wine, wtree, name)

physical = sorted(str(p) for p in PACKET.rglob('*') if p.is_file())
expected = sorted([r['path'] for r in manifest['payload_files']] + [str(manifest_path), str(PACKET / 'handoff-validation096-v2.json')])
record('V2-01', len(physical) == 10 and physical == expected and len(manifest['payload_files']) == 8
       and all(matches(r) for r in manifest['payload_files']) and matches(handoff['manifest'])
       and reference(manifest_path)['sha256'] == 'db668d3c84066e98a2c0bb29b8005eaa66ad9835816e59d3d5ab9550f74cf7a4'
       and not any(p.is_symlink() for p in PACKET.rglob('*')),
       'The frozen packet has exactly 10 physical regular files, 8 exact payloads and the manifest/handoff; no symlink or undeclared file.', reference(manifest_path))
record('V2-02', all(matches(r) for r in correction['original_v1_files_preserved']) and matches(correction['previous_source_gap_review'])
       and len(gap['source_blockers']) == 3 and len(gap['contract_gaps']) == 4,
       'All six original v1 files and the original three-blocker/four-gap review remain exact; their historical failures are preserved.', reference(gap_path))
formal = load(binding['condition096_formal_source_review']['path'])
record('V2-03', all(matches(binding[k]) for k in ('candidate_code_manifest', 'condition096_formal_source_review', 'gold095_source_guard'))
       and formal['source_gate_passed'] is True and formal['runtime_pass'] is False
       and all(matches(r) for r in plan['source_evidence_files']),
       'The exact already approved functional candidate/source evidence and its independent SOURCE-only review are bound; this does not admit runtime.', binding['condition096_formal_source_review'])
hashes = guard['source_sha256_after']
drift = [rel for rel, sha in hashes.items() if reference(REPO / rel)['sha256'] != sha]
record('V2-04', guard['passed'] is True and len(hashes) == 735 and drift == [],
       'The actual 735-file gold095 source map is unchanged at this SOURCE inspection; it is not a96 runtime/source guard.', {'guard': reference(guard_path), 'source_count': len(hashes), 'source_drift': drift})
pending = []
for name, tree in trees.items():
    first = tree.body[0]
    second = tree.body[1]
    value = ast.literal_eval(first.value) if isinstance(first, ast.Assign) else None
    pending.append(isinstance(first, ast.Assign) and isinstance(first.targets[0], ast.Name)
                   and first.targets[0].id == 'PENDING_PREPARATION' and value is True
                   and isinstance(second, ast.If) and any(isinstance(n, ast.Raise) for n in ast.walk(second)))
record('V2-05', all(pending) and all('EXPECTED_BINDING_SHA256=None' in sources[n] for n in ('linux-condition096-worker-pending.py', 'wine-condition096-window-pending.py')),
       'Each target exits under a true pending flag before its imports or execution. The two binding hashes remain None; no FINAL was created.', {'pending_templates': list(sources)})
future_keys = ('mode', 'source_root', 'fresh_output_directory', 'actual_source_guard', 'actual_maintained_count',
               'actual_full095_validation_receipt', 'actual_post_full095_commit_push_proof', 'required_actual_prerequisite_gates',
               'actual_baseline_receipt', 'actual_baseline_records', 'actual_baseline_shell_status', 'actual_baseline_saved_review',
               'actual_FINAL_runner_formal_review', 'actual_independent_related_unittest_primary',
               'actual_isolated_Linux_saved_comparison', 'actual_root_PNG_view')
record('V2-06', all(binding[k] is None for k in future_keys) and binding['root_runtime_authorized'] is False
       and binding['actual096_completed'] is False and binding['completed_section_increment'] == 0
       and all(has_all(sources[n], ["BINDING['root_runtime_authorized'] is True", "BINDING['actual_full095_validation_receipt'] is not None", "BINDING['actual_post_full095_commit_push_proof'] is not None", 'type(value) is type(gate[\'expected\'])']) for n in ('linux-condition096-worker-pending.py', 'wine-condition096-window-pending.py')),
       'Actual full095/save/gold/FINAL/runtime prerequisites remain pending; root must fill full references and typed gates only from real completed evidence.', {'null_binding_keys': list(future_keys)})
old_plan = load(OLD / 'condition096-validation-plan.json')
counts = plan['counts']
record('V2-07', same(plan['Linux_cases'], old_plan['Linux_cases'])
       and [s['id'] for s in plan['steps']] == [s['id'] for s in old_plan['steps']]
       and all(same({k:v for k,v in new.items() if k not in ('expected_field_qualification','expected_presentation')}, old) for old,new in zip(old_plan['steps'],plan['steps']))
       and len(plan['Linux_cases']) == counts['Linux_API_cases_planned'] == 1132
       and len(plan['steps']) == counts['states_planned'] == 146
       and sum(s['action']=='fresh_window' for s in plan['steps']) == counts['fresh_windows_planned'] == 2
       and sum(s['action']!='fresh_window' for s in plan['steps']) == counts['manual_button_requests_planned'] == 144
       and sum(bool(s.get('PNG')) for s in plan['steps']) == counts['PNG_planned'] == 1
       and matches(binding['validation_plan'])
       and all("PLAN=json.loads(bound_file(BINDING['validation_plan'])" in sources[n] for n in ('linux-condition096-worker-pending.py','wine-condition096-window-pending.py')),
       'One unchanged original action/scenario table is shared by both modes; only source qualification expectations were added. 1132/146/2/144/1 are planned counts, not actual results.', counts)
app_text, app_tree = parsed(CANDIDATE / 'rouge/app.py')
app_class = next(n for n in app_tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
app_method = next(n for n in app_class.body if isinstance(n, ast.FunctionDef) and n.name == 'update_condition_cultivation_explanations')
make_tab = next(n for n in app_class.body if isinstance(n, ast.FunctionDef) and n.name == 'make_damage_tab')
lambda_nodes = [n for n in ast.walk(make_tab) if isinstance(n, ast.Lambda) and n.lineno == 695]
import_nodes = [n for n in ast.walk(make_tab) if isinstance(n, ast.ImportFrom) and n.lineno == 691 and n.module == 'condition_cultivation']
partition = plan['presentation_partition']
record('V2-08', partition['candidate_app_sha256'] == reference(CANDIDATE / 'rouge/app.py')['sha256']
       and partition['method'] == {'qualname':'MainWindow.update_condition_cultivation_explanations','co_firstlineno':app_method.lineno}
       and partition['new_signal_lambda'] == {'qualname':'MainWindow.make_damage_tab.<locals>.<lambda>','co_firstlineno':695}
       and len(lambda_nodes) == len(import_nodes) == 1
       and has_all(wine_function('presentation_stack'), ['co_qualname', 'co_firstlineno', "['method']", "['new_signal_lambda']"])
       and has_all(wine_function('exact_constructor_import'), ["site['caller_lineno']", "site['caller_qualname']", "site['phase']", "site['request']", "site['qualname']"]),
       'Exact frozen candidate method/lambda sites and the one make_damage_tab constructor import are qualified by actual source location, phase/request and caller; selector names do not form an exclusion.', partition)
record('V2-09', has_all(wine_function('profile'), ['import_event=None if present else exact_constructor_import(frame)', 'constructor_import_events.append(import_event)', 'assert present or import_event is not None'])
       and "assert len(constructor_import_events)==1" in wine,
       'Historical IMPORT_PROFILE is fixed: first condition module execution is separately recorded under its exact constructor import. All other helper calls require the exact presentation stack.', {'resolved_original_blocker':'IMPORT_PROFILE'})
record('V2-10', has_all(wine_function('fresh_window'), ["'all_project_entries'", "'original_project_entries'", "'presentation_project_entries'", "'constructor_import_project_entries'"])
       and "for key in ('actual_entries','original_project_entries','API_sequences','prepared_sequences','targeted_call_sequences','UI')" in wine_function('run_step')
       and "record['startup']==baseline['startup']" not in wine,
       'Historical STARTUP_TOTAL_VECTOR is fixed: original constructor calls/UI/native sequence data pair with gold; complete added presentation/import vectors are retained separately, without claiming total equality.', {'resolved_original_blocker':'STARTUP_TOTAL_VECTOR'})
record('V2-11', has_all(wine_function('condition_probe'), ["'tooltip':widget.toolTip()", "'old_controls_comparison':old_control_projection(old_controls)"])
       and wine_function('condition_probe').count("'old_controls_comparison':old_control_projection(old_controls)") == 2
       and has_all(wine_function('old_control_projection'), ['projected=clone(rows)', "row['tooltip']='EXACT_NINE_SOURCE_BOUND_PRESENTATION_TOOLTIP_DELTA'", "(row['owner'],row['field']) in allowed"])
       and "old_controls_comparison']['native']==baseline['condition_probe']['old_controls_comparison']['native']" in wine_function('compare_capture'),
       'Historical TARGET_TOOLTIP_SCHEMA is fixed: both sides retain identical complete original-control fields/tooltips and compare the same exact-nine tooltip projection. All other fields and non-target tooltips remain exact.', {'resolved_original_blocker':'TARGET_TOOLTIP_SCHEMA'})
provenance = load(PACKET / 'codec-source-provenance096.json')
original_text, original_tree = parsed(provenance['source']['path'])
codec_rows = []
for name in sources:
    for function in provenance['functions']:
        current = segment(sources[name], trees[name], function['name']).encode('utf-8')
        original = segment(original_text, original_tree, function['name']).encode('utf-8')
        codec_rows.append({'file':name,'function':function['name'],'bytes':len(current),'sha256':hashlib.sha256(current).hexdigest(),
                           'exact_original_AST_segment':current == original,
                           'exact_declared_AST_segment':len(current)==function['bytes'] and hashlib.sha256(current).hexdigest()==function['sha256']})
record('V2-12', matches(provenance['source']) and len(codec_rows)==27
       and all(r['exact_original_AST_segment'] and r['exact_declared_AST_segment'] for r in codec_rows)
       and matches(clarification['affected_frozen_author_record']) and matches(clarification['frozen_manifest'])
       and clarification['source_gate_passed'] is False and clarification['runtime_pass'] is False,
       'All 27 complete codec AST segments are byte-identical to the original actual focused095 source; no codec was executed. The original whole-line LF measurements and false observations are preserved, and the separate clarification correctly fixes the comparison boundary.', {'clarification':reference(clarification_path),'segments':codec_rows})
catalog = load(CANDIDATE / 'rouge/data/condition-cultivation-source.json')['operators']
options_text, options_tree = parsed(REPO / 'rouge/operator_options.py')
options = ast.literal_eval(next(n.value for n in options_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets)))
control_checks = []
for control in plan['condition_controls']:
    matching = [x for x in options[control['owner']] if x[0] == control['field']]
    entry = matching[0]
    default = entry[2]
    widget_class = 'QCheckBox' if type(default) is bool else 'QSpinBox' if type(default) is int else 'QDoubleSpinBox'
    control_checks.append(len(matching)==1 and control['skills']==list(entry[4]) and same(control['default'],default)
                          and control['source_options_maximum_argument']==entry[3] and control['widget_class']==widget_class
                          and control['signal']==('toggled' if type(default) is bool else 'valueChanged') and matches(control['SOURCE_options_file']))
record('V2-13', len(control_checks)==9 and all(control_checks)
       and set(plan['target_fields'])=={r['field'] for r in plan['condition_controls']}
       and has_all(wine_function('observe_signals'), ['model_option_index', "list(skills)==planned[0]['skills']", "type(widget).__name__==planned[0]['widget_class']", "len(PLAN['condition_controls'])==9"])
       and has_all(wine_function('action'), ["len(actual)==1", "actual[0]['value']['native']==flat_native(step['value'])", "actual[0]['current_widget_value']['native']==flat_native(step['value'])"])
       and "flat_native(signals)==flat_native(BASELINE['signals'])" in wine,
       'All nine original owner/field/skills/default/widget/signal facts match the actual OPTIONS literal; each changed typed value must emit its paired signal. The full common-plus-nine original signal vector is compared to gold.', {'condition_controls':plan['condition_controls']})
coordinate_checks = []
for path, fact in plan['source_coordinate_facts'].items():
    owner = plan['source_coordinate_owners'][path]
    source = catalog[owner]
    if fact['table']=='character_table':
        raw=source['raw_character_talents'][fact['talent_index']]['candidates'][fact['candidate_index']]
        expected_path=f"{owner}.talents[{fact['talent_index']}].candidates[{fact['candidate_index']}]"
        valid=path==expected_path and same(fact['raw_candidate'],raw)
    else:
        module=source['modules'][fact['module_id']]
        raw=module['raw_phases'][fact['module_stage']-1]['parts'][fact['part_index']]['addOrOverrideTalentDataBundle']['candidates'][fact['candidate_index']]
        expected_path=f"{fact['module_id']}.phases[{fact['module_stage']-1}].parts[{fact['part_index']}].addOrOverrideTalentDataBundle.candidates[{fact['candidate_index']}]"
        valid=path==expected_path and same(fact['raw_candidate'],raw) and fact['module_name']==module['raw_metadata']['uniEquipName'] and fact['talent_index']==raw['talentIndex']
    coordinate_checks.append(valid and fact['path']==path)
record('V2-14', len(coordinate_checks)==76 and all(coordinate_checks)
       and set(plan['source_coordinate_owners'])==set(plan['source_coordinate_facts'])
       and all(same(plan['field_source_definitions'][owner], source['fields']) for owner,source in catalog.items()),
       'All 76 complete pinned raw coordinate facts and the six owners\' complete field definitions match the already approved source catalog with JSON scalar types, float.hex and key/list order preserved.', {'raw_coordinate_count':len(coordinate_checks),'source_catalog':reference(CANDIDATE / 'rouge/data/condition-cultivation-source.json')})
profiles=load(REPO / 'rouge/data/operator-profiles.json')['operators']
preview_ok=all(fact=={'maximum_elite':len(profiles[owner]['phases'])-1,'maximum_level':profiles[owner]['phases'][-1]['max_level']} for owner,fact in plan['profile_preview_facts'].items())
elite_steps=[s for s in plan['steps'] if 'expected_field_qualification' in s]
elite_ok=True
for step in elite_steps:
    fields=step['observation']['fields']
    definitions=catalog[step['observation']['id']]['fields']
    for definition in definitions:
        gate=definition['first_original_gate']
        status='met' if (fields['elite']>gate['elite'] or fields['elite']==gate['elite'] and fields['level']>=gate['level']) and fields['potential']>=gate['potential_one_based'] else 'unmet'
        elite_ok=elite_ok and step['expected_field_qualification'][definition['field']]==status
record('V2-15', preview_ok and len(elite_steps)==18 and elite_ok,
       'Maximum preview facts come from the actual operator-profile file; 18 E0/E1/E2 first-gate expectations follow pinned original field gates, rather than an invented activation mechanic.', {'first_gate_steps':len(elite_steps),'preview_facts':plan['profile_preview_facts']})
designated=[s for s in plan['steps'] if 'expected_presentation' in s]
designated_by_id={s['id']:s['expected_presentation'] for s in designated}
expected_levels={'missing/shu-preview':90,'missing/manual-level':89,'priority/account-susuro':40,'priority/sparse-run':1,'priority/manual-level':2,'priority/account-only':40,'priority/return-run':1}
designated_ok=set(designated_by_id)==set(expected_levels)
for key,expected_level in expected_levels.items():
    fact=designated_by_id[key]
    designated_ok=designated_ok and fact['effective_training']['level']==expected_level and fact['original_source_path'] in plan['source_coordinate_facts']
    designated_ok=designated_ok and fact['eligibility_status']=='met' and fact['source_status']=='located'
    designated_ok=designated_ok and set(fact['training_provenance'])=={'elite','level','potential','module_id','module_level'}
    designated_ok=designated_ok and fact['level_override']==('manual-level' in key)
    designated_ok=designated_ok and fact['uses_unconfirmed_preview']==(key.startswith('missing/') or key=='priority/manual-level')
    designated_ok=designated_ok and fact['uses_account_reference']==key.startswith('priority/')
record('V2-16', len(designated)==7 and designated_ok
       and has_all(wine_function('condition_probe'), ["row['training_provenance']==provenance", "flat_native(row['effective_training'])==flat_native(expected_effective)", "PLAN['source_coordinate_owners'][original['path']]==op", "flat_native(original[key])==flat_native(value)", "flat_native(row[key])==flat_native(designated[key])", "designated['source_text_contains'] in widget.toolTip()"]),
       'Seven missing/manual/account/sparse-run/off/on transitions assert effective training, all five provenance fields, original source, eligibility and visible text. Existing training merge/manual-reset methods support level40/level1 restoration; the probe reads current public state and never calls the helper to generate its expected answer.', {'designated_steps':designated,'source_methods':['MainWindow.current_operator_state','MainWindow.training_conditions','MainWindow.update_operator','MainWindow.level_changed']})
test_ref=plan['written_boundary_tests']['source']
test_text,test_tree=parsed(test_ref['path'])
test_names=[n.name for cls in test_tree.body if isinstance(cls,ast.ClassDef) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
test_plan=plan['root_primary_execution_plan']['independent_related_tests']
record('V2-17', matches(test_ref) and test_names==plan['written_boundary_tests']['method_names'] and len(test_names)==16
       and plan['written_boundary_tests']['actual_tests_run']==0 and plan['written_boundary_tests']['actual_primary_exit_code'] is None
       and all(value is None for key,value in test_plan.items() if key.startswith('actual_'))
       and test_plan['argv_template']==['<ROOT_PYTHON>','-m','unittest','discover','-s','<ROOT_AUTHORISED_CANDIDATE_SOURCE_ROOT>/tests','-p','test_condition_cultivation.py','-v']
       and "'actual_tests_run':0" in worker and "'independent_boundary_unittest_primary_required':True" in worker,
       'The 16 meaningful candidate test methods have a separate real root primary plan; worker API records do not claim these tests ran. Their actual status/log/argv/count remain null. This is a root closure obligation, not an automatic worker test gate.', {'test_source':test_ref,'method_names':test_names,'primary_plan':test_plan})
record('V2-18', has_all(worker, ["path.endswith('/rouge/app.py'):raise AssertionError", "path.endswith('/rouge/condition_cultivation.py'):raise AssertionError", "snapshot({'caller':scenario,'result':value})", "'actual_API_and_prepare_entries'", "'original_numeric_function_vector'", "'actual_formatter_function_vector'", "'all_three_texts'"])
       and "assert x==y" in comparator and "no field removal" in comparator,
       'Linux captures full caller/result/alias/errors/prepare native snapshots and exact numerical/formatter vectors plus three texts. It forbids app or presentation calls; saved comparator compares entire records without dropping fields.', {'worker':reference(PACKET/'linux-condition096-worker-pending.py'),'comparator':reference(PACKET/'compare-condition096-linux-pending.py')})
record('V2-19', has_all(wine_function('profile'), ["row['complete_row_native']=flat_native(row)", "'caller_and_returned_graph'", "'assembled_scenario_at_exit'", "'local_prepared_scenario_at_exit'", "'original_numeric_subtree_vector'"])
       and has_all(wine, ["len(CALLS)==len(BASELINE['targeted_calls'])", "for actual,old in zip(CALLS,BASELINE['targeted_calls'])", "actual['complete_row_native']==old['complete_row_native']", "row['complete_row_native']==flat_native({key:value for key,value in row.items() if key!='complete_row_native'})"])
       and has_all(wine_function('compare_entries'), ["set(byseq[a])==set(oldrows[b])", "['complete_row_native']==oldrows[b]['complete_row_native']"]),
       'Every completed targeted call is bound before JSON serialization, including exact original tuple types, order, float, cross-root alias, MainWindow.calculate exit scenario, RunState.apply and AccountCache.observe callers/returns/errors. Full ordered targeted rows and API/prepared subsets are paired, rather than merely captured.', {'targeted_methods':['MainWindow.calculate','calculate_damage','_prepare_damage','RunState.apply','AccountCache.observe']})
record('V2-20', has_all(wine_function('compare_capture'), ["actual['damage_result']['native']==baseline['damage_result']['native']", "actual['UI']==baseline['UI']", "actual['three_texts']==baseline['three_texts']"])
       and has_all(wine_function('run_step'), ["record['durable_after']==baseline['durable_after']", "assert_unchanged(durable,durable_snapshot())"])
       and has_all(wine, ['entries_by_scope==BASELINE[\'original_entries_by_phase\']', "partitioned==all_entries"]),
       'All old95 reports, current UI/errors, durable run/account/raw bytes/files and three texts remain strict. Every actual project function entry is classified once and the entire original call vector equals gold; selector calls are not broadly filtered.', {'strict_pairing_contracts':plan['strict_pairing_contracts']})
record('V2-21', has_all(wine_function('fresh_window'), ['tempfile.TemporaryDirectory', 'account_path.write_text', 'run_path.write_text', 'assert not list_game_windows()'])
       and has_all(wine_function('external_idle'), ['not window.auto.isChecked()', 'window.capture.target is None', 'not window.desktop.process', 'not window.desktop_request_busy'])
       and "actual_view_by_root_pending" in wine and "root_actual_PNG_view_actual" in plan['root_primary_execution_plan']
       and plan['root_primary_execution_plan']['root_actual_PNG_view_actual'] is None,
       'Real future Wine work uses fresh synthetic public state, checks game/capture/chat idle, records one real PNG and requires root actual viewing before closure. Wine is compatibility only; native Windows/game/chat remain unverified.', {'scope_limits':plan['scope_limits']})
record('V2-22', has_all(wine, ["BINDING['actual_FINAL_runner_formal_review'] is not None", "bound_file(BINDING[key])", "any(row['path']==BINDING[key]['path'] for row in BINDING['required_actual_prerequisite_gates'])"])
       and 'actual_FINAL_runner_formal_review' not in comparator,
       'The embedded actual_FINAL_runner_formal_review label does not enforce a reverse self-hash in code. It may only be used as an explicitly scoped preseal SOURCE admission reference. Root must keep the actual postseal runner/binding review outside that binding and independently verify it before launch. This report is not an actual FINAL review. Requiring the embedded report itself to hash the final runner would create an impossible hash cycle.', {'preseal_reference_scope':'PENDING template/source admission only','postseal_gate_location':'separate external actual FINAL review and root launch proof','no_final_runner_or_binding_created':True})

passed = all(row['status']=='PASS' for row in checks)
report = {
    'format_version': 2,
    'status': 'INDEPENDENT_PENDING_TEMPLATE_SOURCE_PASS_RUNTIME_NOT_ADMITTED' if passed else 'INDEPENDENT_PENDING_TEMPLATE_SOURCE_BLOCK_RUNTIME_NOT_ADMITTED',
    'source_gate_passed': passed, 'runtime_pass': False,
    'review_scope': 'Independent read-only SHA/JSON/AST/source reasoning of frozen pending validation templates and pinned source facts only. No inspected target/helper/codec/project/API/test/Qt/Wine/Git/network execution.',
    'manifest_sha256': reference(manifest_path)['sha256'],
    'wine_runner_sha256': reference(PACKET/'wine-condition096-window-pending.py')['sha256'],
    'linux_worker_sha256': reference(PACKET/'linux-condition096-worker-pending.py')['sha256'],
    'linux_comparator_sha256': reference(PACKET/'compare-condition096-linux-pending.py')['sha256'],
    'plan_sha256': reference(PACKET/'condition096-validation-plan.json')['sha256'],
    'candidate_manifest_sha256': binding['candidate_code_manifest']['sha256'],
    'guard_sha256': reference(guard_path)['sha256'],
    'checks': checks,
    'check_count': len(checks), 'PASS_count': sum(r['status']=='PASS' for r in checks), 'BLOCK_count': sum(r['status']=='BLOCK' for r in checks),
    'resolved_historical_source_blockers': [r['id'] for r in gap['source_blockers']],
    'resolved_contract_gaps': [r['id'] for r in gap['contract_gaps']],
    'source_references': {'manifest':reference(manifest_path),'handoff':reference(PACKET/'handoff-validation096-v2.json'),
        'corrections':reference(PACKET/'source-correction-record096-v2.json'),'codec_boundary_clarification':reference(clarification_path),
        'original_gap_review':reference(gap_path),'implementation_formal_source_review':binding['condition096_formal_source_review'],
        'candidate_code_manifest':binding['candidate_code_manifest'],'gold095_source_guard':reference(guard_path)},
    'proposed_argv_templates': {
        'Linux_gold_and_candidate':['<ROOT_PYTHON>','<ACTUAL_ROOT_SOURCE_ADMITTED_FINAL_WORKER>'],
        'Linux_saved_comparator':['<ROOT_PYTHON>','<ACTUAL_ROOT_SOURCE_ADMITTED_FINAL_COMPARATOR>','<ACTUAL_GOLD_RECEIPT>','<ACTUAL_CANDIDATE_RECEIPT>','<FRESH_COMPARISON_RECEIPT>'],
        'related_tests':test_plan['argv_template'],
        'Wine_gold_and_candidate':['/workspace/.compat/run-wine-python.sh','<ACTUAL_Z_MAPPED_SOURCE_ADMITTED_FINAL_WINE_RUNNER>']},
    'formal_TRUE_gates': [
        {'pointer':'/source_gate_passed','expected':True}, {'pointer':'/runtime_pass','expected':False},
        {'pointer':'/manifest_sha256','expected':reference(manifest_path)['sha256']},
        {'pointer':'/wine_runner_sha256','expected':reference(PACKET/'wine-condition096-window-pending.py')['sha256']},
        {'pointer':'/linux_worker_sha256','expected':reference(PACKET/'linux-condition096-worker-pending.py')['sha256']},
        {'pointer':'/linux_comparator_sha256','expected':reference(PACKET/'compare-condition096-linux-pending.py')['sha256']},
        {'pointer':'/guard_sha256','expected':reference(guard_path)['sha256']}],
    'root_runtime_prerequisites': [
        'Actual full095 available PASS, real batch commit/push and fresh remote equality proof.',
        'Fresh actual gold/candidate source roots/guards/counts and absent output paths; Windows-readable references explicitly bound by root.',
        'All typed actual prerequisite gates and real source admissions; pending flag/hash substitutions physically sealed and externally reviewed.',
        'Embedded review may identify only this preseal SOURCE template admission with explicit scope; separate actual postseal FINAL runner/binding review outside the binding is required before root launch.',
        'Candidate Wine requires real successful fresh gold receipt, complete native records, shell raw0 and saved review.',
        'Root captures actual isolated Linux pair/comparator/test and Wine primary completions, real stdout/raw statuses; no successful old095 matrix replay is required.',
        'Root runs relevant/selected regressions, physically views actual PNG and verifies actual source/window/durable closure before96 archive/checkpoint.'],
    'actual_FINAL_source_review_completed': False,
    'actual_final_binding_or_runner_created': False,
    'actual_helper_codec_project_API_tests_Qt_Wine_executions': 0,
    'actual_runtime_argv': None, 'actual_primary_exit_codes': None,
    'git_or_network_operations': 0, 'tracked_files_written': 0, 'original_packet_files_written': 0,
    'completed_section_increment': 0, 'actual096_completed': False,
    'planned_counts_are_runtime_results': False,
    'reviewer_read_probe_diagnostics': [
        'Initial rg used a non-existent guessed independent-review directory; corrected to actual source-gap-review-v1 before reading.',
        'One schema inspection attempted a list slice of the module dictionary and raised KeyError before any file write or target execution; corrected to the actual modules mapping.'],
    'reviewer_SOURCE_script': reference(__file__),
}
HERE.mkdir(exist_ok=True)
with REPORT.open('x',encoding='utf-8') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
review_manifest={'format_version':1,'status':'STOPWRITE_INDEPENDENT_SOURCE_REVIEW_ONLY','directory':str(HERE),
                 'payload_files':[reference(__file__),reference(REPORT)],'payload_count':2,
                 'excluded_control_files':['public-artifacts-manifest-source-review-validation096-v2.json','handoff-source-review-validation096-v2.json'],
                 'source_gate_passed':passed,'runtime_pass':False,'actual096_completed':False,'completed_section_increment':0}
mf_path=HERE/'public-artifacts-manifest-source-review-validation096-v2.json'
with mf_path.open('x',encoding='utf-8') as stream:
    json.dump(review_manifest,stream,ensure_ascii=False,indent=2);stream.write('\n')
hand={'format_version':1,'status':report['status'],'source_gate_passed':passed,'runtime_pass':False,
      'manifest':reference(mf_path),'report':reference(REPORT),'SOURCE_checker':reference(__file__),
      'checks':len(checks),'PASS':report['PASS_count'],'BLOCK':report['BLOCK_count'],
      'actual_FINAL_review_completed':False,'actual_runtime_prerequisites':None,'actual_target_executions':0,
      'actual096_completed':False,'completed_section_increment':0}
with (HERE/'handoff-source-review-validation096-v2.json').open('x',encoding='utf-8') as stream:
    json.dump(hand,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'report':reference(REPORT),'manifest':reference(mf_path),'handoff':reference(HERE/'handoff-source-review-validation096-v2.json'),
                  'source_gate_passed':passed,'checks':len(checks),'PASS':report['PASS_count'],'BLOCK':[r['id'] for r in checks if r['status']=='BLOCK']},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
