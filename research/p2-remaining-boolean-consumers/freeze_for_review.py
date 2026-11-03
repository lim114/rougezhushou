"""Freeze exact external draft and already saved checks for independent review."""
import ast,gzip,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')


def sha(v):return hashlib.sha256(v).hexdigest()
def save(name,v):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
 comparison=json.loads((OUT/'saved-matrix-comparison-attempt-1.json').read_bytes());assert comparison['passed']
 old=json.loads(gzip.decompress((OUT/'baseline-isolated-cores.json.gz').read_bytes()))
 new=json.loads(gzip.decompress((OUT/'draft-isolated-cores.json.gz').read_bytes()))
 counts={'whole_accepted_same':0,'qualified_text_rejected':0}
 for a,b in zip(old,new):
  assert all(a[k]==b[k] for k in ('index','case','expect','input_typed','phase_argument','prepared_before','prepared_after'))
  assert all(r['original_caller_unchanged'] and r['catalog_unchanged'] for r in (a,b))
  if a['expect']=='same':
   assert a['outcome']==b['outcome']=='accepted' and a['result_typed']==b['result_typed'] and a['reports']==b['reports']
   counts['whole_accepted_same']+=1
  else:
   assert a['outcome']=='accepted' and b['outcome']=='error' and b['error_type']=='ValueError'
   assert b['error_message']=='ranged_attack 不接受文本条件；请使用布尔值。'
   counts['qualified_text_rejected']+=1
 save('isolated-core-saved-comparison.json',{'passed':True,'pairs':8,'counts':counts,'new_public_calls':0,
    'new_project_helper_calls':0,'prepared_mutation_exact_to_old':True,'caller_catalog_unchanged':True,
    'scope':'Only explicit isolated _evaluate_damage_once phase arguments; public phase envelope not executed.'})
 first=(OUT/'draft-related.log').read_text();target=(OUT/'new-targeted-corrected.log').read_text()
 assert 'Ran 122 tests' in first and 'FAILED (failures=1)' in first and 'AssertionError: ValueError not raised' in first
 assert 'Ran 1 test' in target and target.rstrip().endswith('OK')
 oldtest=ast.parse((OUT/'new-test-attempt-1.py').read_text())
 newtest=ast.parse((OUT/'draft/tests/test_remaining_boolean_condition_text_input.py').read_text())
 methods=lambda tree:{n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree)
                      if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
 before=methods(oldtest);after=methods(newtest);assert before.keys()==after.keys() and len(after)==8
 changed=[k for k in before if before[k]!=after[k]]
 assert changed==['test_ranged_module_override_uses_actual_normal_plan_eligibility']
 save('current-test-evidence-binding.json',{'passed':True,'existing_baseline_tests':114,'existing_draft_tests':114,
   'existing_failures':0,'first_new_methods':8,'first_new_passed':7,'first_new_failed_expectation':1,
   'targeted_corrected_methods_run':1,'targeted_passed':1,'unchanged_new_methods_same_ast':7,
   'current_eight_methods_supported_by_prior_seven_and_targeted_one':True,
   'unittest_public_API_counts_not_instrumented':True,'no_claim_of_fresh_all_eight_rerun':True,
   'first_diagnostic_call_count_clarification':'The old diagnostic 183 is a source-derived estimate, not instrumentation; do not report it as measured API calls.',
   'product_bytes_unchanged_after_test_expectation_correction':True})
 frozen=json.loads((OUT/'current-baseline-freeze.json').read_bytes())
 changed_files=[]
 for row in frozen['files']:
  data=(OUT/'draft'/row['path']).read_bytes()
  if sha(data)!=row['sha256']:changed_files.append(row['path'])
 assert changed_files==['rouge/damage.py','rouge/operator_engine.py']
 e=(OUT/'draft/rouge/operator_engine.py').read_text();b=(OUT/'baseline/rouge/operator_engine.py').read_text()
 assert "def calculate_extended(scenario,attributes):return Combat(scenario,attributes).calculate()" in e
 assert e.index('self.ranged_attack_condition_consumed=False')<e.index('normal=self.plan(normal=True,window=recharge)')<e.index('self.ranged_attack_condition_consumed=not ranged_overridden or normal is not None')
 assert "if full['unbound_cast_reference'] is not None:\n            duration=None;recharge=None" in b
 assert b.index("if full['unbound_cast_reference'] is not None:\n            duration=None;recharge=None")<b.index('normal=self.plan(normal=True,window=recharge)')
 damage=(OUT/'draft/rouge/damage.py').read_text()
 assert damage.index("result['report']=build_report(scenario,result)")<damage.index("conditions={")
 assert "if op=='char_4182_oblvns':\n        conditions=((" in damage
 assert "_oblvns_ranged_attack_consumed" not in damage+e
 save('current-source-and-scope-check.json',{'passed':True,'base_commit':frozen['base_commit'],
   'baseline_files':723,'other_baseline_files_exact':721,'changed_product_files':changed_files,
   'existing_helper_wrapper_unchanged':True,'per_core_object_signal_reset':True,'signal_actual_normal_execution':True,
   'signal_not_user_scenario_or_public_schema':True,'late_guard_after_existing_report_and_83_85_errors':True,
   'S1_unbound_duration_recharge_None_before_cycle':True,'S3_actual_normal_gate':'cycle is not None and not (attack SP and not continuous)',
   'raw_240_ranks_12_module_source_or_old_36_probes_not_rerun':True,
   'root_registry_proposal':'tests.test_remaining_boolean_condition_text_input',
   'no_native_clock_probability_multiplier_change':True})
 patch=bytearray()
 for name in ('rouge/damage.py','rouge/operator_engine.py'):
  proc=subprocess.run(['git','diff','--no-index','--no-ext-diff','--no-renames','baseline/'+name,'draft/'+name],cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  assert proc.returncode==1 and not proc.stderr
  patch.extend(proc.stdout.replace(b'a/baseline/',b'a/').replace(b'b/draft/',b'b/'))
 name='tests/test_remaining_boolean_condition_text_input.py'
 proc=subprocess.run(['git','diff','--no-index','--no-ext-diff','/dev/null','draft/'+name],cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert proc.returncode==1 and not proc.stderr
 patch.extend(proc.stdout.replace(b'a/draft/',b'a/').replace(b'b/draft/',b'b/'))
 (OUT/'section86.patch').write_bytes(patch)
 check=subprocess.run(['git','apply','--check',str(OUT/'section86.patch')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert check.returncode==0,check.stderr.decode()
 rows=[]
 for name in ['rouge/damage.py','rouge/operator_engine.py','tests/test_remaining_boolean_condition_text_input.py']:
  data=(OUT/'draft'/name).read_bytes();rows.append({'path':name,'source_path':str(OUT/'draft'/name),'bytes':len(data),'sha256':sha(data)})
 save('review-freeze86.json',{'status':'FROZEN_FOR_FORMAL_REVIEW','base_commit':frozen['base_commit'],
   'patch_sha256':sha(patch),'patch_bytes':len(patch),'files':rows,
   'matrix_pairs':268,'matrix_public_calls':536,'matrix_counts':comparison['counts'],
   'isolated_core_pairs':8,'explicit_prepare_helper_calls':8,'explicit_core_helper_calls':16,
   'matrix_formatters':1299,'isolated_core_formatters':42,'new_tests':8,
   'unittest_counts':'114 baseline; first draft114 existing+8new=122, 1 wrong S1 expectation;7 unchangednewpass+1 corrected targetedpass',
   'unittest_API_call_counts':'not instrumented, do not infer fresh measured total',
   'catalog_cache_reads_for_isolation':{'matrix':538,'isolated_cores':18},
   'old_source_36_calls_preserved_original_not_reexecuted':True,'registered_module_proposal':'tests.test_remaining_boolean_condition_text_input',
   'other_source_28_and_independent_17':'immutable; final public manifest will include every original named attachment and both manifests',
   'complete_source_packets':'/workspace/.continuation/root-source-packets-086-verified.json',
   'unchanged_product_bytes_since_matrix_and_tests':True,'GUI':0,'Wine':0,'tracked_edits':0})
 print(json.dumps({'passed':True,'patch_sha256':sha(patch),'review_freeze_sha256':sha((OUT/'review-freeze86.json').read_bytes())}))


if __name__=='__main__':main()
