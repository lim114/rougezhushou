"""Review completed JSON proof without recalculating the large corpus."""
from collections import Counter
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-integer-option-audit-061')
FROZEN=AUTHOR/'frozen';DRAFT=AUTHOR/'draft'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
freeze=json.loads((AUTHOR/'freeze.json').read_text())
baseline_drift=[name for name,expected in freeze['public_source_hashes'].items() if sha(FROZEN/name)!=expected]
draft_changes=[name for name,expected in freeze['public_source_hashes'].items() if sha(DRAFT/name)!=expected]
assert not baseline_drift and draft_changes==['rouge/operator_engine.py']
patch=AUTHOR/'section61.patch'
assert sha(patch)=='b12e5ca02ca6587661e82651a2b586b0c563a78a18480250a9bbde490c44e27c'
paths=[line.removeprefix('+++ ') for line in patch.read_text().splitlines() if line.startswith('+++ ')]
assert paths==['b/rouge/operator_engine.py','b/tests/test_target_count_input_types.py','b/tests/test_integer_option_input_types.py']
new_tests=ast.parse((DRAFT/'tests/test_integer_option_input_types.py').read_text())
assert len([node for node in ast.walk(new_tests) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')])==8
base_ast=ast.parse((FROZEN/'rouge/operator_engine.py').read_text())
draft_ast=ast.parse((DRAFT/'rouge/operator_engine.py').read_text())
def without_option(tree):
    for node in ast.walk(tree):
        if isinstance(node,ast.ClassDef) and node.name=='Combat':
            node.body=[method for method in node.body if not (isinstance(method,ast.FunctionDef) and method.name=='option')]
    return ast.dump(tree,include_attributes=False)
assert without_option(base_ast)==without_option(draft_ast)
closure=json.loads((AUTHOR/'source-closure.json').read_text())
raw={}
for name,entry in closure['source_files'].items():
    path=Path(entry['path'])
    assert sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes']
    raw[name]=json.loads(path.read_text())
catalog=json.loads((FROZEN/'rouge/data/catalog.json').read_text())['operators']
patch_binding=json.loads((AUTHOR/'reused-research/amiya-phase-source-receipt.json').read_text())
binding_path='char_patch_table.patchChars.char_1001_amiya2.skills'
historical_skills=patch_binding['exact_selectors'][binding_path]
assert sha(AUTHOR/'reused-research/amiya-phase-source-receipt.json')==closure['reused_original_char_patch_receipt']['receipt_sha256']
assert not closure['reused_original_char_patch_receipt']['fresh_raw_verification_claimed']
rank_checks=0
for record in closure['per_control_records']:
    profile=catalog[record['operator']]
    original_char=raw['character_table'].get(profile['id'])
    skills=original_char['skills'] if original_char else historical_skills
    if original_char is None:assert profile['id']=='char_1001_amiya2'
    for source in record['original_skills']:
        skill_number=source['skill']; skill=profile['skills'][skill_number-1]
        assert skills[skill_number-1]['skillId']==skill['id']==source['skill_id']
        for rank in range(10):
            bb={entry['key']:entry['value'] for entry in raw['skill_table'][skill['id']]['levels'][rank]['blackboard']}
            assert canonical(bb)==canonical(skill['levels'][rank]['values'])
            rank_checks+=1
assert rank_checks==510 and len(closure['per_control_records'])==25

old=json.loads((AUTHOR/'baseline-public-results.json').read_text())['complete_public_cases']
new=json.loads((AUTHOR/'draft-public-results.json').read_text())['complete_public_cases']
assert len(old)==len(new)==1354
changed=[];preserved=[];preserved_groups=Counter()
for index,(before,after) in enumerate(zip(old,new)):
    assert canonical(before['scenario'])==canonical(after['scenario'])
    is_bool=type(before['scenario'].get(before['field'])) is bool
    reject=(before['group']=='active_integer' and is_bool and before['field_queried_as_integer'] and before['outcome']['accepted'])
    if reject:
        assert before['identity'] in ('false','true')
        expected={'accepted':False,'error_type':'ValueError','error':before['field']+'需要范围内的有限非负整数。'}
        assert canonical(after['outcome'])==canonical(expected),index
        changed.append(index)
    else:
        assert canonical(before['outcome'])==canonical(after['outcome']),index
        preserved.append(index);preserved_groups[before['group']]+=1
assert len(changed)==192 and len(preserved)==1162
main_comparison=json.loads((AUTHOR/'matrix-comparison.json').read_text())
assert main_comparison['changed_indices']==changed and main_comparison['preserved_indices']==preserved
for name,expected in main_comparison['verified_complete_artifacts'].items():assert sha(AUTHOR/name)==expected
old_failed=json.loads((AUTHOR/'matrix-comparison-v1-preparation-failure.json').read_text())
assert len(old_failed['failures'])==374
assert {row['index'] for row in old_failed['failures']}<=set(preserved)

small_old=json.loads((HERE/'final-baseline-probes.json').read_text())
small_new=json.loads((HERE/'final-draft-probes.json').read_text())
assert small_old['cases'].keys()==small_new['cases'].keys()
small_changed=[];small_preserved=[]
for key,before in small_old['cases'].items():
    after=small_new['cases'][key]
    assert canonical(before['input'])==canonical(after['input'])
    if before['new_bool_error_expected']:
        assert before['outcome']['accepted']
        assert after['outcome']['accepted'] is False and after['outcome']['error_type']=='ValueError'
        assert after['outcome']['error'].endswith('需要范围内的有限非负整数。')
        small_changed.append(key)
    else:
        assert canonical(before['outcome'])==canonical(after['outcome']),key
        small_preserved.append(key)
for payload in (small_old,small_new):
    assert payload['caller_inputs_unchanged'] and payload['catalog_and_mechanics_unchanged']
    diagnostic=payload['runtime_tuple_diagnostic']
    assert diagnostic['runtime_vs_saved_Python_equality'] is False
    assert diagnostic['strict_serialized_public_JSON_equal'] and len(diagnostic['tuple_vs_list_paths'])==10
tests=json.loads((HERE/'final-tests.json').read_text())
assert tests['passed'] and not tests['failures'] and not tests['errors'] and not tests['skips']
receipt={
 'independent_final_review_passed':True,'findings':[],'blockers':[],
 'baseline_head':freeze['baseline_head'],'reviewed_patch':str(patch),'reviewed_patch_sha256':sha(patch),
 'reviewed_production_change':'Combat.option only; raw bool rejected at actual integer query, with healing_targets capability exception',
 'runtime_manifest_files_checked':len(freeze['public_source_hashes']),'baseline_source_drift':baseline_drift,'draft_runtime_changes':draft_changes,
 'all_other_operator_engine_AST_unchanged':True,'new_test_methods':8,
 'source_closure_control_records_independently_checked':25,'cached_raw_tables_freshly_rehashed':True,
 'raw_skill_rank_blackboards_independently_compared':rank_checks,'amiya_char_patch_mapping_historical_receipt_only':True,
 'main_completed_JSON_pairs_independently_recompared_no_calculation_rerun':1354,
 'main_bool_errors_verified':192,'main_full_public_outcomes_preserved':1162,'preserved_group_counts':dict(preserved_groups),
 'old_comparator_false_differences_preserved':374,'old_failed_cases_all_preserved_in_completed_JSON':True,
 'tuple_diagnostic_live_example':small_new['runtime_tuple_diagnostic'],
 'independent_small_paired_cases':len(small_old['cases']),
 'independent_small_public_calls_with_diagnostic':small_old['public_calls']+small_new['public_calls'],
 'independent_small_new_bool_errors':len(small_changed),'independent_small_complete_outcomes_preserved':len(small_preserved),
 'independent_test_methods_run':tests['tests_run'],'independent_test_failures':[],'independent_test_errors':[],'independent_test_skips':[],
 'readonly_source_audit_files_not_overwritten':['NOTE.md','receipt.json','source_audit.py'],
 'current_guard_vs_initial_candidate':'Initial readonly review suggested a key set; final uses the existing integer=True contract except healing_targets. Current remaining fields and upstream guards were independently checked; no extra current public behavior changes.',
 'test54_migration_reviewed':'Only 4 active integer-count expectations move to new bool errors; legacy inactive charge_count/activation_count and capability guards remain tested.',
 'root_tracked_edits':0,'author_draft_edits':0,'private_state_read':False,'game_actions':0,
 'Wine_validated':False,'actual_GUI_validated':False,'native_Windows_validated':False,
 'remaining_validation':'Frozen HEAD58 final draft review only; root must integrate after full60 archive and run fresh related/selected checks and later batch validation.',
 'artifact_hashes':{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='final-receipt.json'},
}
(HERE/'final-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['independent_final_review_passed','main_bool_errors_verified','main_full_public_outcomes_preserved','independent_small_paired_cases','independent_small_new_bool_errors','independent_small_complete_outcomes_preserved','independent_test_methods_run','blockers']},ensure_ascii=False))
