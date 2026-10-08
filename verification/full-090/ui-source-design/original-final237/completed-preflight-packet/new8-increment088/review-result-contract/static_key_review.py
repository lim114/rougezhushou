"""Source-text/AST review only. Never imports or calls product code."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
COMMIT = '66df88c3274e37ba0f176adcd862a439a6f99767'
PLAN = Path('/workspace/.continuation/root-transport-preparation090/additional8-input-plan090.json')
HIST = Path('/workspace/.continuation/p2-continuous-attack-control-visibility091-source')
EXPECTED = {
    'damage': 'b48c86b2f02c4ea76f9b6cbd1b32a57abd925b2d8d22e8527a0cd6cb8c61be09',
    'operator_engine': 'd8091732fd0559c9ef49b45a8b0c906d61c2ab57469fc0afba4469e0ff977b7c',
    'amiya_continuous_reference': 'd8638b7c62c04575714eebe5a3fe9da46151ef3808da5518fc765c5cc4d506e7',
    'estimate': 'c1f73f1663454578f8b38b0caa2cba1dd99a082104e339dc4f3c8ff893c96a91',
    'reporting': '70ef12ed860c08ce4f471d2be0e9c5cbcec40a64ad7b91d6078c2d99d11254ae',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

sources = []
texts = {}
for name, expected in EXPECTED.items():
    relative = 'rouge/' + name + '.py'
    blob = subprocess.check_output(['git', 'show', COMMIT + ':' + relative], cwd=ROOT)
    snapshot = HERE / ('actual088-' + name + '.py')
    assert sha(blob) == expected and snapshot.read_bytes() == blob
    ast.parse(blob)
    texts[name] = blob.decode()
    sources.append({'git_commit': COMMIT, 'git_path': relative,
                    'snapshot': snapshot.name, 'bytes': len(blob), 'sha256': expected})

plan_bytes = PLAN.read_bytes()
assert sha(plan_bytes) == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
plan = json.loads(plan_bytes)
assert len(plan['pairs']) == 4 and len(plan['cases']) == 8
assert len({json.dumps(c['input'], sort_keys=True) for c in plan['cases']}) == 8
for case in plan['cases']:
    assert type(case['input']['continuous_attacks']) is bool
    assert case['input']['continuous_attacks'] is case['widget_checked']
    assert case['input']['window_seconds'] == 12.75
    assert 'base_attack' not in case['input']

amiya = texts['amiya_continuous_reference']
tree = ast.parse(amiya)
attach = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'attach_result')
reference_dict = next(n.value for n in attach.body if isinstance(n, ast.Assign)
                      and isinstance(n.value, ast.Dict)
                      and any(isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant)
                              and t.slice.value == 'amiya_continuous_reference' for t in n.targets))
ref_values = {k.value: v for k, v in zip(reference_dict.keys, reference_dict.values) if isinstance(k, ast.Constant)}
unknown = ['actual_acquisition_times_seconds', 'actual_impact_times_seconds',
           'actual_recharge_seconds', 'actual_cycle_seconds']
for key in unknown:
    assert isinstance(ref_values[key], ast.Constant) and ref_values[key].value is None
assert isinstance(ref_values['native_clock_binding_verified'], ast.Constant)
assert ref_values['native_clock_binding_verified'].value is False
cycle_unknown = ['recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps']
cycle_loop = next(n for n in attach.body if isinstance(n, ast.For)
                  and isinstance(n.iter, ast.Tuple)
                  and [e.value for e in n.iter.elts] == cycle_unknown)
assert isinstance(cycle_loop.body[0], ast.Assign) and cycle_loop.body[0].value.value is None
assert "options.get('target_windows') == []" in amiya
assert "c['damage_type'] not in ('healing', 'regeneration', 'buildup')" in amiya
assert "'attack_sp_per_attack_parameter': attack_credit" in amiya
assert "'attack_sp_enabled_in_reference': bool(read_continuous_attacks(scenario))" in amiya
assert "result['timing']['resource_and_damage_shared_clock'] = False" in amiya
assert "result['complete'] = result['estimate']['complete'] = False" in amiya

assert "recharge=initial=None" in texts['estimate']
assert "if read_continuous_attacks(scenario) or has_periodic_sp(scenario):" in texts['estimate']
assert "cycle=(duration+recharge) if duration is not None and recharge is not None else None" in texts['estimate']
assert "return self.tv.get(name,{}).get(key,default)" in texts['operator_engine']
assert "phase<=elite and (phase<elite or minimum<=level) and rank<=potential" in texts['operator_engine']
assert "elif read_continuous_attacks(self.s,active=lambda:any(r['kind']=='attack_sp'" in texts['operator_engine']
assert "first=mixed_charge_seconds(self.s,max(0,sp['sp_cost']-initial),rate,0" in texts['operator_engine']
assert "'actual_collision_times_seconds':None,'collision_clock_verified':False" in texts['operator_engine']
assert "result['chen_phase_reference']={**full['chen_phase_reference']" in texts['operator_engine']
assert "'sections':sections}" in texts['reporting']
assert "'report']=build_report(scenario,result)" in texts['damage']

historical_sources = []
for filename, expected in {
    'existing-saved-output-projection091.json': '5164407e6448723d1d45c02de695591fa224a65aa8b4e9ab2bd77552a8abf936',
    'saved-evidence-transport091.json': '0554c6391a3a4d489f3bd08db0db971f051721e99014d67657bf19e8addbb395',
}.items():
    data = (HIST / filename).read_bytes()
    assert sha(data) == expected
    historical_sources.append({'path': str(HIST / filename), 'sha256': expected, 'bytes': len(data),
                               'role': 'historical saved shape only, not new8 result evidence'})
history = json.loads((HIST / 'existing-saved-output-projection091.json').read_bytes())
historical_rows = []
for setname, indices in [('source16_rows', (1, 2, 9, 10)), ('baseline60_rows', (15, 16, 33, 34))]:
    for row in history[setname]:
        if row['index'] not in indices:
            continue
        ref = row.get('amiya_reference')
        rr = row['relic_resolution']
        historical_rows.append({'set': setname, 'index': row['index'], 'label': row['label'],
            'input': row['input'], 'initial_recharge_cycle': row['initial_recharge_cycle'],
            'amiya_reference_keys': sorted(ref.keys()) if ref else [],
            'amiya_reference_parameters': {k: ref[k] for k in
                ('attack_sp_per_attack_parameter', 'attack_sp_enabled_in_reference', 'enemy_source_excluded')}
                if ref else None,
            'relic_resolution_keys': sorted(rr.keys()),
            'record_shapes': [{'id': r['id'], 'status': r['status'],
                              'applied_kinds': [a['kind'] for a in r['applied']]} for r in rr['records']]})

adapter = HERE.parent / 'preflight_ui090_section088.py'
adapter_bytes = adapter.read_bytes()
adapter_text = adapter_bytes.decode()
ast.parse(adapter_bytes)
assert "frame.f_code.co_name == 'build_report'" in adapter_text
assert "scenario = deepcopy(frame.f_locals['scenario'])" in adapter_text
assert "for key in case['input']:" in adapter_text
assert "assert typed(scenario[key]) == typed(case['input'][key])" in adapter_text
assert "assert 'total_healing' not in result" in adapter_text
assert "assert skill['total_healing'] == 0 and skill['window_healing'] == 0" in adapter_text
assert "assert skill['sp_type'] == 'INCREASE_WHEN_ATTACK'" in adapter_text
assert "reference['attack_sp_per_attack_parameter'] == (0 if excluded else 2)" in adapter_text
assert "assert false > true >= 0" in adapter_text
assert "report['scenario']" not in adapter_text and "result['scenario']" not in adapter_text
(HERE / 'preflight-adapter-reviewed.py.txt').write_bytes(adapter_bytes)

inventory = {
 'status': 'STATIC_KEY_INVENTORY_READY_PENDING_UNIQUE_NEW8_SAVED_RESULTS',
 'named_calculation_source_commit': COMMIT,
 'plan_sha256': sha(plan_bytes), 'source_blobs': sources,
 'plan_pair_ids': [p['id'] for p in plan['pairs']],
 'public_common_paths': ['attack', 'total_damage', 'components', 'estimate.training', 'estimate.skill',
                         'timing', 'report.schema_version', 'report.operator.id', 'report.skill_number', 'report.sections'],
 'timing_report_metrics': {'section_id': 'timing', 'keys': ['initial', 'duration', 'cycle', 'recharge'],
                           'source': 'reporting.py:280; metric values consume estimate.skill clocks'},
 'mechanist_S1': {
    'source': ['damage.py:298', 'damage.py:232', 'estimate.py:62', 'estimate.py:96', 'estimate.py:184', 'estimate.py:229'],
    'clock_paths': ['estimate.skill.' + k for k in ('initial_seconds', 'recharge_seconds', 'cycle_seconds')],
    'false_expected': 'all three None without additional attack/periodic/event credit',
    'true_expected': 'finite positive actual frame-clock values; do not reuse historical numerics',
    'top_total_healing': 'absent for this legacy damage branch',
    'estimate_skill_total_and_window_healing': 'zero for this damage-only skill',
    'sp_type': 'estimate.skill.sp_type = INCREASE_WHEN_ATTACK; no generic sp_type requirement on extended Combat skill dicts'},
 'amiya_continuous_common': {
    'source': ['amiya_continuous_reference.py:52', 'operator_engine.py:1769'],
    'reference_keys': list(ref_values),
    'explicit_actual_None_paths': ['amiya_continuous_reference.' + k for k in unknown],
    'explicit_cycle_None_paths': ['estimate.skill.' + k for k in cycle_unknown],
    'flags': {'native_clock_binding_verified': False, 'timing.phase_clock_unbound': True,
              'timing.resource_and_damage_shared_clock': False, 'complete': False, 'estimate.complete': False},
    'parameter_fields': ['attack_sp_per_attack_parameter', 'attack_sp_enabled_in_reference',
                         'natural_sp_rate_parameter', 'required_sp_parameter',
                         'natural_only_recharge_seconds_reference', 'parameter_clock_reference'],
    'reference_enabled': 'matches the native requested False/True; reference flag alone does not qualify a talent',
    'initial_scope': 'existing independent pre-cast reference unchanged',
    'report_section': 'amiya_continuous; actual_recharge metric None, other displayed numbers qualified references'},
 'amiya_E2_bounded': {
    'declared_target_lifetime_seconds': 5.75, 'declared_target_windows_seconds': None,
    'enemy_source_excluded': False,
    'attack_sp_per_attack_parameter_expected_by_fixed_cultivation_contract': 2,
    'source_data_leaf_numeric_rechecked_in_this_small_five_blob_review': False,
    'actual_damage_boundary': 'preserve_plan marks positive possible hostile components actual_total=None; attach_result calls mask_pending_damage; actual new8 unknown totals must be read from saved public outputs',
    'do_not_assert': ['bounded reference result absent because historical unbounded source16 projection was None',
                      'postcast lifetime uniformly scales the old reference damage', 'reference clock is verified native acquisition or impact']},
 'chen3_S3_active_warrior67': {
    'public_rule_path': 'relic_resolution.rules', 'required_rule': {'kind': 'attack_sp', 'relic_id': 'rogue_6_relic_legacy_67'},
    'initial_path': 'estimate.skill.initial_seconds', 'pair_requirement': 'False initial > True initial >= 0, both finite actual numbers',
    'source': ['operator_engine.py:1338', 'operator_engine.py:438', 'operator_engine.py:1625'],
    'swordwave_reference_keys': ['kind', 'declared_current_hp', 'hp_ratio_parameter', 'minimum_attack_scale_parameter',
                               'body_duration_parameter_seconds', 'actual_collision_times_seconds', 'collision_clock_verified'],
    'actual_collision_times_seconds': None, 'collision_clock_verified': False,
    'report_section': 'chen_swordwave; collision metric None',
    'do_not_require_pair_difference': ['total_damage', 'estimate.skill.total_damage', 'estimate.skill.cycle_seconds',
                                      'estimate.skill.cycle_damage', 'estimate.skill.cycle_dps'],
    'historical_attribution': 'baseline60 rows33/34 used different training/input; finite initial changed, recharge25 and cycle45 did not'},
 'amiya_E0_empty': {
    'declared_target_windows_seconds': [], 'declared_target_lifetime_seconds': None, 'enemy_source_excluded': True,
    'attack_sp_per_attack_parameter_expected': 0,
    'qualification_source': 'selected_talents eligibility; talent default0; historical E0 credit0, not a new8 execution',
    'enemy_math': 'current hostile components are zeroed; do not generalize to healing/regeneration/buildup',
    'reference_flag': 'False/True requested native bool remains serialized even with attack credit0',
    'own_regeneration_numeric_contract': None,
    'own_regeneration_not_invented': True},
 'same_call_scenario_boundary': {
    'source': 'damage.py:323 build_report(scenario,result)',
    'adapter': 'profile observes reporting.py build_report actual frame.f_locals[scenario] during the same API call',
    'claimed_public_report_scenario_field': False,
    'input_comparison': 'compare every original requested key to each actual processed report scenario; auto derived base_attack is extra'},
 'historical_shapes': historical_rows, 'historical_sources': historical_sources,
 'reviewed_preflight_adapter': {'path': str(adapter), 'snapshot': 'preflight-adapter-reviewed.py.txt',
                              'sha256': sha(adapter_bytes), 'bytes': len(adapter_bytes), 'executed': False},
 'new8_result_evidence_available_in_this_review': False,
 'raw_historical_source16_or_baseline60_reloaded_or_recomputed': False,
}
write('key-inventory.json', inventory)
write('receipt.json', {
 'status': 'STATIC_RESULT_KEY_CONTRACT_PASS_PENDING_UNIQUE_NEW8_SAVED_REVIEW',
 'named_calculation_source_commit': COMMIT,
 'plan_path': str(PLAN), 'plan_sha256': sha(plan_bytes), 'plan_unchanged': True,
 'named_git_blob_read_method': 'git show exact commit:path; byte-identical to five review snapshots',
 'named_source_blob_count': 5,
 'inventory_path': str(HERE / 'key-inventory.json'),
 'inventory_sha256': sha((HERE / 'key-inventory.json').read_bytes()),
 'preflight_adapter_sha256': sha(adapter_bytes),
 'source_only_assertions_passed': True,
 'sealed_prior_review_input_plan_directory_modified': False,
 'live_runner_or_tracked_files_modified': False,
 'root089_inheritance': {'parent_reported_commit': '3a59aa0c3d09199caea14de3c5fe89781225a8d6',
    'parent_reported_proof': 'actual-root089-ui090-source-proof.json',
    'parent_reported_proof_sha256': '41bf44ddcc68ccc812cf1d8cacbfa07d062c3d9b3ac59eb429929c8f4f992634',
    'parent_reported_088_to_089_difference': 'run_state only; other125 public blobs unchanged',
    'independently_rechecked_in_this_five_blob_review': False},
 'calls': {'new_API': 0, 'product_helpers': 0, 'formatter': 0, 'RunState_constructor': 0,
           'RunState_apply': 0, 'Qt': 0, 'Wine': 0, 'tests': 0, 'original_source16_or_baseline60_reruns': 0},
 'gui_executed': False, 'wine_executed': False,
 'remaining': ['parent freezes exact actual root089 source/adapter/contract before unique8 execution',
               'independent saved8 readback verifies complete public unknown/damage values without fresh product calls'],
})
print('PASS: five named source blobs, four pairs/eight original inputs, public key and reference boundaries, same-call scenario trace; 0 product calls.')
