"""Fixed-source static audit only. No product module imports or runtime calls."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path('/workspace/.continuation/p2-boolean-consumer-083-independent-static')
COMMIT = 'ea7866be6f2a8e89d382ec2982a45f1cb9231141'
PATHS = ('rouge/operator_engine.py', 'rouge/operator_options.py', 'rouge/app.py',
         'rouge/damage.py', 'rouge/run_modifiers.py', 'rouge/enemy_environment.py',
         'rouge/data/catalog.json')

def sha(raw): return hashlib.sha256(raw).hexdigest()
def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

sources = {}
frozen = []
for name in PATHS:
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', COMMIT + ':' + name])
    dest = OUT / 'fixed-current' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    sources[name] = raw.decode('utf-8')
    frozen.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'commit': COMMIT,
        'git_blob': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', COMMIT + ':' + name]).decode().strip()})

tree = ast.parse(sources['rouge/operator_engine.py'])
FIELDS = ('enemy_is_boss', 'enemy_in_neural_break', 'near_previous_deployment', 'double_charge')
references = {name: [] for name in FIELDS}
neural_calls = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute): continue
    if node.func.attr == 'get' and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in FIELDS:
        name = node.args[0].value
        references[name].append({'line': node.lineno, 'expression': ast.get_source_segment(sources['rouge/operator_engine.py'], node),
            'default': ast.literal_eval(node.args[1]) if len(node.args)>1 else None})
    if node.func.attr == 'neural':
        neural_calls.append({'line': node.lineno, 'expression': ast.get_source_segment(sources['rouge/operator_engine.py'], node)})
for rows in references.values(): rows.sort(key=lambda x:x['line'])
neural_calls.sort(key=lambda x:x['line'])
assert [x['line'] for x in references['enemy_is_boss']] == [248]
assert [x['line'] for x in references['enemy_in_neural_break']] == [257,277,918,996,1242]
assert [x['line'] for x in references['near_previous_deployment']] == [219]
assert [x['line'] for x in references['double_charge']] == [1028,1031,1310,1437]
assert [x['line'] for x in neural_calls] == [950,1237,1484]

option_tree = ast.parse(sources['rouge/operator_options.py'])
assignment = next(x for x in option_tree.body if isinstance(x, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == 'OPTIONS' for t in x.targets))
options = ast.literal_eval(assignment.value)
ui_fields = {oid: [dict(zip(('key','label','default','maximum','skills'), row)) for row in options[oid]
    if row[0] in FIELDS] for oid in ('char_1042_phatm2','char_4204_mantra','char_1048_orchd2')}
assert {x['key']:x['skills'] for x in ui_fields['char_4204_mantra']} == {
    'enemy_is_boss':(1,2), 'enemy_in_neural_break':(1,2)}
assert {x['key']:x['skills'] for x in ui_fields['char_1048_orchd2']} == {
    'near_previous_deployment':(1,2,3), 'double_charge':(1,)}
assert all(isinstance(x['default'], bool) for rows in ui_fields.values() for x in rows)

catalog = json.loads(sources['rouge/data/catalog.json'])
orchid = catalog['operators']['char_1048_orchd2']
selected_identity = [{'talent_index':i, 'candidate_index':j, 'candidate':c} for i,rows in enumerate(orchid['talents'])
    for j,c in enumerate(rows) if c['name']=='翔虫机动']
assert {x['candidate']['phase'] for x in selected_identity} == {1,2}
assert all(x['candidate']['level']==1 for x in selected_identity)
app = sources['rouge/app.py']
assert 'if isinstance(default,bool):' in app and 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'" in sources['rouge/enemy_environment.py']

write('static-consumer-receipt.json', {
    'status':'passed_readonly_source_scope_review', 'fixed_product_commit':COMMIT,
    'fixed_public_files':frozen, 'engine_boolean_references':references,
    'actual_neural_call_sites':neural_calls, 'ui_OPTIONS_data':ui_fields,
    'orchid_selected_talent_candidates':selected_identity,
    'consumer_scope': {
        'enemy_is_boss':'Combat.neural threshold. Phatm2 all skills and normal plans; Mantra all skills includingS3 and normal postmodifier plans; shared cycle recomputation when present. Applies even to empty event lists because threshold/initial state are still read.',
        'enemy_in_neural_break':'Combat.neural breaking_until plus optional reference bool; Phatm2 S1 binding-seed cutoff; Mantra S1 preexisting-break extra source and S2 extra source selection. Shared neural means Mantra S3 API consumption persists despite absentS3 UI checkbox.',
        'near_previous_deployment':'Only Orchid, only inside already-selected named talent 翔虫机动 qualification; no such named candidate atE0. All3 skills can qualify once named talent selected. UI visibility alone does not imply E0 consumer.',
        'double_charge':'Only Orchid skill1 active-arrow/reference branch, plus S1 initial/recharge and periodic/event-SP required cost. Inactive OrchidS2/S3 and other operators must remain ignored.'},
    'prepare_and_Qt_trace': {
        'public_entry':{'path':'rouge/damage.py','line':373,'preparation_line':375},
        'prepare_run':{'path':'rouge/damage.py','line':274},
        'resolve_enemy':{'path':'rouge/run_modifiers.py','line':53},
        'identity_overwrites_boss':{'path':'rouge/enemy_environment.py','line':110},
        'extended_engine_after_prepare':{'path':'rouge/damage.py','line':298},
        'Qt_bool_widget_creation':{'path':'rouge/app.py','line':665,'isChecked_serializer_line':1037},
        'Qt_visibility_owner_skill_gate':{'path':'rouge/app.py','line':968},
        'Qt_serializer_owner_skill_gate':{'path':'rouge/app.py','line':1035},
        'UI_fact':'bool defaults produce real QCheckBox instances; source serializer calls isChecked() only when owner/skill applies. Static trace, not executedQt.'},
    'guard_recommendations': [
        {'field':'enemy_is_boss','path':'rouge/operator_engine.py','before_line':248,
         'placement':'Consumer-local guard in Combat.neural, checking effective post-prepare scenario. Preserve selected fixed-enemy identity overriding stale manual strings; do not prevalidate raw input in damage global preparation.'},
        {'field':'enemy_in_neural_break','path':'rouge/operator_engine.py','before_line':257,
         'placement':'Shared neural consumer guard covers actual API consumption on all neural plans. Keeping initial_neural_buildup validation before this point preserves its original precedence. If guarding before every truthiness read is required, reuse a narrow read helper at918/996/1242 as well; do not use OPTIONS to suppress MantraS3 validation.'},
        {'field':'near_previous_deployment','path':'rouge/operator_engine.py','before_line':219,
         'placement':'Inside existing named-selected-talent condition at213, immediately before near_previous_deployment read. Preserve E0 absent-talent ignored-field behavior, selected module identity logic and original redeploy reference.'},
        {'field':'double_charge','path':'rouge/operator_engine.py','before_line':1028,
         'placement':'Inside existing Orchid S1 branch at1025, before arrow truthiness/reference consumption. All public calculations first call full=self.plan() at1297, before subsequent S1 SP consumers at1310/1437. Preserve S2/S3 ignored-field behavior and defaultTrue.'}],
    'type_boundary':'Reject textual conditions consistently with existing consumer-local string guards. Do not parse False/0/true/empty-string conventions, add a global bool validator, or silently tighten numeric/None/list domains beyond authorized text repair. Preserve true/false/missing/default contracts and unrelated inactive fields.',
    'mechanism_research':'No original mechanics were re-researched; this is current source consumer and type/serialization scope only.',
    'new_api_calls':0, 'tests_executed':0, 'gui_executed':False, 'wine_executed':False,
    'tracked_edits':False, 'runtime_imports':False,
    'preparation_diagnostics':[{'command':'rg consumer fields in app/run_environment/damage/engine',
       'missing_guessed_file':'rouge/run_environment.py','correct_files':'Fixed git grep locates prepare_run in run_modifiers.py and override in enemy_environment.py.',
       'command_exit_code':2,'public_calls_after_failure':0,'tracked_mutations_after_failure':0}],
})
print(json.dumps({'passed':True,'public_calls':0,'tests':0,'neural_call_sites':[x['line'] for x in neural_calls],
    'receipt_sha256':sha((OUT/'static-consumer-receipt.json').read_bytes())}))
