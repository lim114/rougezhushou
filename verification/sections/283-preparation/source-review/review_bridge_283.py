"""Limited shared main-bridge composition review; no production integration."""
from copy import deepcopy
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREP = ROOT / '.cache/section283-preparation'
BRIDGE = ROOT / '.cache/panel_native_bridge_283.py'
SHA = '52800ba9d98a58790ec4a77eabd4eb195516f31ad1716a0fc49ee86909e671a6'
CORE_SHA = '536875942fe6222f7ab3d995fffc4d2ae31f043a6f67e3616cc5c39a1cd68190'
OUT = HERE / 'limited-bridge-review-283.json'
assert not OUT.exists()
raw = BRIDGE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == SHA
assert hashlib.sha256((PREP/'rouge/panel_native_finalization.py').read_bytes()).hexdigest() == CORE_SHA
snapshot = HERE / 'bridge-reviewed-52800ba9.py'
assert snapshot.read_bytes() == raw  # Original first-run exact bridge snapshot remains.
sys.path.insert(0, str(ROOT))
import rouge
rouge.__path__.insert(0, str(PREP / 'rouge'))
# The source-bound helper copy has no data tree; this review uses the real
# public catalog package rather than treating a cache layout error as a product failure.
spec = importlib.util.spec_from_file_location('rouge.catalog', ROOT/'rouge/catalog.py')
public_catalog = importlib.util.module_from_spec(spec); spec.loader.exec_module(public_catalog)
sys.modules['rouge.catalog'] = public_catalog
spec = importlib.util.spec_from_file_location('rouge.panel_native_finalization', PREP/'rouge/panel_native_finalization.py')
core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
sys.modules['rouge.panel_native_finalization'] = core
spec = importlib.util.spec_from_file_location('rouge._independent_bridge_283', BRIDGE)
bridge = importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)
checks, probes = [], []
Q = 4294967296


def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})


def finish_probe(name, cultivated, rune, runes, normal, skill=None):
    scenario = {'operator': 'kaltsit', 'skill': 1}
    original = deepcopy([cultivated, rune, runes])
    bridge.prepare(scenario, cultivated, rune, runes)
    estimate = {'base_stats': deepcopy(rune), 'skill': {'skill_attack': 150, 'skill_attack_speed_reference': 700},
                'warnings': ['existing-model-marker'], 'complete': False}
    result = {'estimate': estimate, 'total_damage': None, 'total_healing': 1001, 'complete': False,
              'warnings': ['existing-unknown'], 'attack_speed': 600, 'attack_speed_reference': 700}
    before = deepcopy(result)
    bridge.install(estimate, normal, skill or bridge.unknown_skill_terms())
    bridge.finish(scenario, result)
    probes.append({'name': name, 'cultivated': original[0], 'rune': original[1], 'runes': original[2],
                   'normal_terms': deepcopy(normal), 'actual_result': deepcopy(result)})
    sanitized = deepcopy(result)
    del sanitized['panel_native_finalization']
    del sanitized['estimate']['native_panel_reference_key']
    check(name+'/old_model_same', sanitized == before)
    check(name+'/primitive_inputs_same', [cultivated, rune, runes] == original)
    check(name+'/no_terms_leak', '_panel_native_terms' not in result['estimate'])
    return scenario, result


cultivated = {'hp': 1000.0, 'attack': 100.0, 'defense': 50.0, 'resistance': 10.0, 'attack_speed': 700.0}
rune = dict(cultivated)
normal = bridge.normal_terms(rune, 100, hp_multiplier=.25, attack_multiplier=.5,
                             defense_multiplier=.5, defense_flat=7,
                             resistance_addition=3, attack_speed_addition=25, attack_flat=4)
s, r = finish_probe('nominal_primitive_main_phases', cultivated, rune, [], normal)
rows = {row['id']: row for row in r['panel_native_finalization']['fields']}
check('normal/hp1250', bridge.conditional_value(rows['normal.hp']) == 1250)
check('normal/atk154', bridge.conditional_value(rows['normal.attack']) == 154)
check('normal/def82', bridge.conditional_value(rows['normal.defense']) == 82)
check('normal/mr13', bridge.conditional_value(rows['normal.resistance']) == 13)
check('normal/as725_not_timing_cap600', bridge.conditional_value(rows['normal.attack_speed']) == 725 and r['attack_speed'] == 600 and r['attack_speed_reference'] == 700)
check('unknown_extended_skill/remains_unknown', all(rows['skill.'+f]['references']['getter_result_raw'] is None for f in ('attack','attack_speed')))
check('independent_nominal_provenance', r['panel_native_finalization']['input_provenance']['protected_parent_result_propagated'] is False and r['panel_native_finalization']['input_provenance']['normal_native_calls_inferred'] is False)

# Explicitly different post-rune model snapshots must remain independent, even
# where the rune writer's conditional parameter happens to be another number.
runelist = [{'kind':'attack_pct','value':.5,'formula_item':'MULTIPLIER'},
           {'kind':'defense_pct','value':7,'formula_item':'ADDITION'},
           {'kind':'attack_speed','value':25,'formula_item':'ADDITION'}]
different = dict(rune, attack=999.25, defense=81.0, attack_speed=900.0)
normal = bridge.normal_terms(different, different['attack'])
s, r = finish_probe('independent_post_rune_snapshot_not_writer_readback', cultivated, different, runelist, normal)
rows = {row['id']: row for row in r['panel_native_finalization']['fields']}
check('independent/rune150', bridge.conditional_value(rows['rune.attack']) == 150)
check('independent/normal999_25', bridge.conditional_value(rows['normal.attack']) == 999.25)
check('independent/actual_all_unknown', all(x['actual_decoded_value'] is None and x['actual_getter_raw'] is None for x in rows.values()))
check('independent/four_phase_order', list(r['panel_native_finalization']['phase_ids']) == ['cultivation','rune','normal','skill'])

# Main finishers append exactly the additional flat-defense and time-qualified
# attack-speed primitives; they do not overwrite the chosen base snapshots.
estimate = {}
normal = bridge.normal_terms(rune, 100)
skills = {'attack': bridge._term(100), 'attack_speed': bridge._term(700)}
bridge.install(estimate, normal, skills)
bridge.add_final_term(estimate, 'normal', 'defense', 'final_addition', 11)
bridge.add_final_term(estimate, 'normal', 'attack_speed', 'addition', 40)
bridge.add_final_term(estimate, 'skill', 'attack_speed', 'addition', 70)
_, r = finish_probe('flat_defense_and_finite_attack_speed_primitives', cultivated, rune, [], normal, skills)
rows = {row['id']: row for row in r['panel_native_finalization']['fields']}
check('finishers/defense61', bridge.conditional_value(rows['normal.defense']) == 61)
check('finishers/normalAS740', bridge.conditional_value(rows['normal.attack_speed']) == 740)
check('finishers/skillAS770', bridge.conditional_value(rows['skill.attack_speed']) == 770)

# A lost basis stays unknown; adding a known finite buff is not a zero basis.
normal = bridge.normal_terms(rune, 100)
skill = bridge.unknown_skill_terms()
temp = {}; bridge.install(temp, normal, skill)
bridge.add_final_term(temp, 'skill', 'attack_speed', 'addition', 40)
_, r = finish_probe('unknown_skill_plus_known_finite_buff', cultivated, rune, [], normal, skill)
rows = {row['id']: row for row in r['panel_native_finalization']['fields']}
check('finite_unknown/not40_or20', bridge.conditional_value(rows['skill.attack_speed']) is None)

# Literal primitives from a fixed public first-three skill are used directly;
# neither skill/model output ratios nor writer returns are used as an oracle.
from rouge.catalog import catalog
for op, n in [('kaltsit', 2), ('silverash', 3), ('mechanist', 1)]:
    scenario = {'operator': op, 'skill': n, 'skill_rank': 10, 'base_attack': 100}
    bb = catalog()['operators'][op]['skills'][n-1]['levels'][9]['values']
    effects = [{'kind':'attack_pct','value':.25}, {'kind':'attack_speed','value':15}]
    terms = bridge.first_three_skill_terms(scenario, cultivated, effects)
    probes.append({'name':'first_three_'+op+'_'+str(n), 'scenario':scenario, 'catalog_values':bb,
                   'effects':effects, 'actual_terms':deepcopy(terms)})
    check('first_three/'+op+'/basis', terms['attack']['basis'] == 100 and terms['attack_speed']['basis'] == 700)
    check('first_three/'+op+'/direct_bonus', terms['attack']['multiplier'] == [bb.get('atk',0)+.25] and terms['attack_speed']['addition'] == [bb.get('attack_speed',0)+15])

# The bridge strips caller-manufactured prepared data by fresh preparation and
# returns a source list copy; it never consumes declared normal/native facts.
forged = {'_panel_native_prepared': {'fields': ['forged'], 'rune_sources': ['forged']}}
bridge.prepare(forged, cultivated, rune, [])
probes.append({'name':'fresh_preparation_replaces_caller_private_input', 'actual_prepared':deepcopy(forged['_panel_native_prepared'])})
check('preparation/no_forged_fields', len(forged['_panel_native_prepared']['fields']) == 10 and all(type(x) is dict for x in forged['_panel_native_prepared']['fields']))
check('preparation/no_forged_sources', forged['_panel_native_prepared']['rune_sources'] == [])

tree = ast.parse(raw)
public_callers = {node.func.id for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)}
check('bridge/no_dynamic_eval_exec', not {'eval','exec','compile','__import__'} & public_callers)
check('bridge/no_qualified_normality_inference', b'read_field_reference(' not in raw and b'write_field_reference(' not in raw and b'manager_flow_reference(' not in raw)
check('bridge/main_finish_evaluates_once', raw.count(b"evaluated=panel_native_finalization({'fields':rows})") == 1)

report = {'kind':'LIMITED_INDEPENDENT_283_MAIN_BRIDGE_REVIEW', 'bridge_sha256':SHA, 'core_sha256':CORE_SHA,
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'probe_count':len(probes), 'check_count':len(checks), 'failed':[c for c in checks if not c['passed']],
          'checks':checks, 'probes':probes,
          'static_integration_script_review': {
              'path':'.cache/integrate283-main.py',
              'sha256':hashlib.sha256((ROOT/'.cache/integrate283-main.py').read_bytes()).hexdigest(),
              'observed':'Insertion-only bridge wiring except named defense-flat variable preserving identical legacy expression, then append its nominal term; finite-AS normal/skill additions use existing active/skill_bonus; calculate/report/calibration consume one final evaluation.',
              'not_executed_by_reviewer':True},
          'scope':'Synthetic public arithmetic/bridge process only, 3 direct catalog primitives and static integration anchors; not root33 full model freeze, installed production, Windows UI, native execution, actual state, current RC or codec roundtrip validation.',
          'source_review_reused':'source-gates-283.json', 'reviewer_first_run_error_preserved':'first-catalog-path-error.json', 'new_fresh_native_spans':0,
          'production_or_other_author_cache_modified':False, 'game_or_chat_operation':False}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'probes':len(probes),'checks':len(checks),'failed':report['failed'],
                  'receipt_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}))
raise SystemExit(bool(report['failed']))
