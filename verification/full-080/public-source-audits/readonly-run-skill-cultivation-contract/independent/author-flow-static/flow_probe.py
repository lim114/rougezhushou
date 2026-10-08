import ast, copy, gzip, hashlib, json, pathlib, sys, types

sys.dont_write_bytecode = True
OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(OUT / 'frozen75'))
from rouge.catalog import operator_profiles
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

strict = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
source = (OUT / 'frozen75/rouge/app.py').read_text()
tree = ast.parse(source)
cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'MainWindow')
methods = {node.name: node for node in cls.body if isinstance(node, ast.FunctionDef)}
names = ('current_operator_state', 'training_conditions', 'skill_rank_value')
namespace = {'operator_profiles': operator_profiles}
exec(compile(ast.Module(body=[methods[name] for name in names], type_ignores=[]), 'immutable-app-exact-method-bodies', 'exec'), namespace)
choices_node = next(node for node in ast.walk(methods['update_operator']) if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'choices' for t in node.targets))
choices_code = compile(ast.Expression(choices_node.value), 'immutable-app-exact-choices-expression', 'eval')
scenario_node = next(node for node in methods['calculate'].body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'scenario' for t in node.targets))
scenario_code = compile(ast.Expression(scenario_node.value), 'immutable-app-exact-initial-scenario-expression', 'eval')

class Control:
    def __init__(self, value): self.given = value
    def currentData(self): return self.given
    def value(self): return self.given
    def isChecked(self): return self.given

def make_proxy(account, member, selected_skill=1, use_run=True):
    owner = 'char_437_mizuki'
    obj = types.SimpleNamespace(operator=Control(owner), skill=Control(selected_skill), use_run_training=Control(use_run), operator_observations={owner: copy.deepcopy(account)}, run=types.SimpleNamespace(state={'operators': {owner: copy.deepcopy(member)} if member else {}}))
    for name in names:
        setattr(obj, name, types.MethodType(namespace[name], obj))
    current = obj.current_operator_state()
    elite = current.get('fields', {}).get('elite', 2)
    maximum = operator_profiles()[owner]['phases'][elite]['max_level']
    # Synthetic controls model the clamping already visible in update_operator.
    obj.level = Control(min(current.get('fields', {}).get('level', maximum), maximum))
    for key, value in {'deployment_elapsed': 0, 'healing_targets': 1, 'continuous_attacks': True, 'defense': 0, 'resistance': 0, 'cooperative': False, 'fragile': False, 'charge_count': 0, 'shield_breaks': 0, 'activation_count': 1, 'companion_attack': 0, 'stacks': 0}.items():
        setattr(obj, key, Control(value))
    return obj

records = []
for elite in (0, 1, 2):
    for account_rank in (3, 10):
        for run_rank in (None, 3, 7, 10):
            for skill in (1, 2, 3):
                account = {'scope': 'account', 'fields': {'elite': 2, 'level': 90}, 'skill_ranks': {str(i): account_rank for i in (1, 2, 3)}}
                member = {'scope': 'run', 'present': True, 'fields': {'elite': elite, 'level': 1}, 'skill_ranks': {} if run_rank is None else {str(i): run_rank for i in (1, 2, 3)}}
                proxy = make_proxy(account, member, skill)
                state = proxy.current_operator_state()
                training = proxy.training_conditions()
                rank = proxy.skill_rank_value()
                available = eval(choices_code, {'profile': operator_profiles()['char_437_mizuki'], 'elite': training['elite']})
                scenario = eval(scenario_code, {'self': proxy, 'ids': []})
                scenario['window_seconds'] = 10
                before = strict(scenario)
                try:
                    result = calculate_damage(copy.deepcopy(scenario))
                    outcome = {'accepted': True, 'result': result, 'formatted_report': format_report(result), 'technical_report': format_report(result, technical=True), 'formatted_estimate': format_estimate(result)}
                except Exception as exc:
                    outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
                assert strict(scenario) == before
                records.append({'id': len(records), 'synthetic_account': account, 'synthetic_run_member': member, 'current_operator_state': state, 'training_conditions': training, 'skill_rank_value': rank, 'available_skill_choices_from_exact_frozen_expression': available, 'initial_calculate_scenario_from_exact_frozen_expression': scenario, 'public_outcome': outcome, 'selected_skill_available_in_ui': skill in available})

controls = []
account = {'scope': 'account', 'fields': {'elite': 2, 'level': 90}, 'skill_ranks': {'1': 10}}
for tag, member, use_run in (
    ('run_unknown_rank_does_not_borrow_account_mastery', {'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}}, True),
    ('run_known_rank_preserved_for_gate', {'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {'1': 10}}, True),
    ('run_invalid_rank_excluded', {'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {'1': 10}, 'invalid_skill_ranks': ['1']}, True),
    ('absent_run_member_returns_account', {'scope': 'run', 'present': False, 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}}, True),
    ('use_run_disabled_returns_account', {'scope': 'run', 'fields': {'elite': 0, 'level': 1}, 'skill_ranks': {}}, False),
):
    proxy = make_proxy(account, member, use_run=use_run)
    controls.append({'case': tag, 'synthetic_account': account, 'synthetic_run_member': member, 'use_run': use_run, 'current_operator_state': proxy.current_operator_state(), 'training_conditions': proxy.training_conditions(), 'skill_rank_value': proxy.skill_rank_value()})
assert [r['skill_rank_value'] for r in controls] == [7, 10, 7, 10, 10]
assert all((r['skill_rank_value'] == (r['synthetic_run_member']['skill_ranks'].get('1', 10 if r['training_conditions']['elite'] == 2 else 7))) for r in records)
raw = (strict(records) + '\n').encode()
blob = gzip.compress(raw, mtime=0)
(OUT / 'synthetic-flow-public-whole-outcomes.json.gz').write_bytes(blob)
(OUT / 'synthetic-flow-controls.json').write_text(json.dumps(controls, ensure_ascii=False, indent=2) + '\n')
receipt = {'baseline_head': 'a52a4bf9217aee3c11617135b7fc9cc6c38fd0f2', 'kind': 'readonly synthetic contract probes using exact immutable AST method bodies / choices and initial scenario expressions', 'actual_public_calculate_calls': len(records), 'accepted': sum(r['public_outcome']['accepted'] for r in records), 'errors': sum(not r['public_outcome']['accepted'] for r in records), 'all_complete_strict_public_results_three_texts_or_exact_errors_retained': True, 'native_or_actual_qt_validation': False, 'synthetic_controls': True, 'real_private_state_used': False, 'gate_changed': False, 'unavailable_ui_skills_exercised_only_as_public_api_controls': True, 'source_method_lines': {name: methods[name].lineno for name in names}, 'source_choices_line': choices_node.lineno, 'source_initial_scenario_line': scenario_node.lineno, 'raw_bytes': len(raw), 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'gzip_bytes': len(blob), 'gzip_sha256': hashlib.sha256(blob).hexdigest(), 'linux_full_app_import_attempt': {'attempts': 1, 'accepted': False, 'exception': 'ModuleNotFoundError', 'message': "No module named 'win32gui'", 'fallback': 'exact frozen AST selected bodies; no fake native modules or actual Qt claim'}}
(OUT / 'synthetic-flow-probe-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt))
