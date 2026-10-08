"""Seal existing fixed-source, tests and saved comparisons; zero new API calls."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-neural-condition-text-input-083')
OLD=Path('/workspace/.continuation/p2-boolean-consumer-083-independent-source')
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
freeze=json.loads((OUT/'formal-freeze-review083.json').read_bytes())
checked=0
for variant,key in [('baseline','all_baseline_git_blobs'),('draft','all_draft_blobs')]:
    for rel,row in freeze[key].items():
        data=(AUTHOR/variant/rel).read_bytes()
        assert len(data)==row['bytes'] and sha(data)==row['sha256']
        local=OUT/('fixed-'+variant)/rel
        if local.exists():assert local.read_bytes()==data
        checked+=1
comparison=json.loads((OUT/'independent-comparison083.json').read_bytes())
tests=json.loads((OUT/'new-tests083.json').read_bytes())
saved=json.loads((OUT/'saved-author-recomparison083.json').read_bytes())
assert comparison['status']=='passed' and comparison['independent_pairs']==40
assert comparison['counts']=={'text_rejected':11,'whole_success_unchanged':15,'exact_old_errors_unchanged':14}
assert tests['successful']is True and tests['tests_run']==9 and tests['failures']==tests['errors']==tests['skipped']==0
assert tests['actual_public_calls']==293 and tests['successful_calls']==84 and tests['error_calls']==209
assert saved['status']=='passed' and saved['new_API_calls']==0 and saved['saved_pairs']==432
assert saved['counts']=={'text_rejected':116,'whole_success_unchanged':256,'exact_old_errors_unchanged':60}
for row in saved['bindings']:
    data=(OUT/row['archive_path']).read_bytes()
    assert len(data)==row['bytes'] and sha(data)==row['sha256'] and Path(row['source_path']).read_bytes()==data
old_manifest=OLD/'public-artifacts-manifest.json'
assert sha(old_manifest.read_bytes())=='c16724af88468ca36477d1290fe04eac8b1baac9f8f9fde28be92c081d3b71b9'
for row in json.loads(old_manifest.read_bytes())['files']:
    data=Path(row['source_path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
author_fixed=json.loads((OUT/'fixed-author-inputs/formal-draft-freeze083.json').read_bytes())
for rel,row in author_fixed['files'].items():
    data=(OUT/'fixed-author-inputs'/rel).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
for variant in ['baseline','draft']:
    records=json.loads((OUT/f'{variant}-independent-public083.json').read_bytes())
    assert records['actual_public_calls']==40 and len(records['rows'])==40
    for index,row in enumerate(records['rows'],1):
        assert json.loads((OUT/f'{variant}-case-{index:02}.json').read_bytes())==row
save('seal-validation083.json',{'status':'passed','author_sources_rechecked':checked,
    'independent_per_case_aggregate_rows_rechecked':80,'fixed_author_metadata_files_checked':6,
    'old_sealed46_unchanged':True,'saved_author_results_and_receipt_unchanged':True,
    'fresh_API_calls':0,'tests_repeated':0,'tracked_mutations':False})
save('independent-review083.json',{'status':'passed_no_blocker','baseline_commit':freeze['baseline_commit'],
    'author_damage_sha256':author_fixed['files']['rouge/damage.py']['sha256'],
    'author_patch_sha256':author_fixed['files']['draft.patch']['sha256'],
    'author_new_tests_sha256':author_fixed['files']['tests/test_neural_condition_text_input.py']['sha256'],
    'baseline_public_blobs_verified':720,'draft_public_blobs_verified':721,
    'five_line_inverse_restores_complete_damage_bytes':True,'CRLF_retained':True,
    'threshold_damage_clocks_and_helpers_unchanged':True,
    'independent_pairs':40,'matrix_actual_public_calls':80,'matrix_counts':comparison['counts'],
    'new_tests_run':9,'new_test_failures':0,'new_test_errors':0,'new_test_skips':0,
    'instrumented_new_test_actual_public_calls':293,'test_successful_calls':84,'test_expected_error_calls':209,
    'total_formal_independent_fresh_public_calls':373,
    'total_formal_successful_calls':125,'total_formal_error_calls':248,
    'old_source8_calls_repeated':False,'old_source8_not_included_in_formal373':True,
    'author_saved_pairs_readonly_recompared':432,'author_saved_counts':saved['counts'],
    'saved_recomparison_new_API_calls':0,'no_related_or_large_matrix_rerun':True,
    'processed_enemy_identity_and_actual_two_owner_all_skill_scope':True,
    'all_legacy_errors_and_nontext_or_idle_owner_results_in_sample_preserved':True,
    'all_complete_results_and_three_text_fields_or_exact_errors_checked':True,
    'preparation_failure':'one missing tests/__init__.py source-copy error, zero API calls, original script/log preserved',
    'scope':'Reject only str of the two actual neural fields on effective prepared scene after original per-evaluation report, with no new native mechanism or global type domain',
    'limitations':['No Qt/Wine/native Windows executed','No root integration claim',
                   'Unknown native neural event order and River periodic/source clocks remain unknown',
                   'Multi-phase numerical behavior is existing author model, not native phase verification'],
    'tracked_mutations':False,'GUI':False,'Wine':False,'native_Windows':False})
top=['NOTE.md','prepare_review083.py','prepare-review083.log','initial-prep1-prepare_review083.py',
     'initial-prep1-prepare-review083.log','preparation-diagnostics083.json','formal-freeze-review083.json',
     'independent-cases083.json','run_independent083.py','baseline-run083.log','draft-run083.log',
     'baseline-independent-public083.json','draft-independent-public083.json','compare_independent083.py',
     'compare-independent083.log','independent-comparison083.json','run_new_tests083.py','new-tests083.log',
     'new-tests083.json','new-tests-wrapper083.log','recompare_author_saved083.py','recompare-author-saved083.log',
     'saved-author-recomparison083.json','seal_numeric083.py','seal-validation083.json','independent-review083.json']
top += [f'{variant}-case-{index:02}.json' for variant in ['baseline','draft'] for index in range(1,41)]
top += [str(p.relative_to(OUT)) for root in ['fixed-author-inputs','fixed-author-saved-results'] for p in sorted((OUT/root).rglob('*')) if p.is_file()]
assert len(top)==len(set(top))
save('handoff.json',{'status':'final_sealed_independent_numeric_passed','baseline_commit':freeze['baseline_commit'],
    'independent_review_sha256':sha((OUT/'independent-review083.json').read_bytes()),
    'source_candidate_manifest_path':str(old_manifest),'source_candidate_manifest_sha256':sha(old_manifest.read_bytes()),
    'independent_fresh_calls':373,'matrix_pairs':40,'matrix_counts':comparison['counts'],
    'new_tests':9,'new_test_actual_calls':293,'saved_author_pairs':432,'saved_author_counts':saved['counts'],
    'saved_matrix_recomparison_fresh_calls':0,'old8_not_rerun':True,'preparation_error_evidence_preserved':True,
    'no_blocker':True,'ready_for_root_integration':True,'tracked_mutations':False,'Qt':False,'Wine':False,
    'artifacts_excluding_this_handoff_and_manifest':len(top)})
top.append('handoff.json')
rows=[]
for name in sorted(top):
    p=OUT/name;data=p.read_bytes();rows.append({'source_path':str(p),'archive_path':name,'bytes':len(data),'sha256':sha(data)})
save('public-artifacts-manifest.json',{'format_version':1,'status':'final_sealed_independent_numeric_passed',
    'files':rows,'actual_fresh_public_calls':373,'bytes':sum(r['bytes'] for r in rows),
    'execution_copies_excluded':['fixed-baseline/','fixed-draft/'],
    'execution_copy_source_hashes_bound_by':'formal-freeze-review083.json'})
assert all(len(Path(r['source_path']).read_bytes())==r['bytes'] and sha(Path(r['source_path']).read_bytes())==r['sha256'] for r in rows)
print(json.dumps({'status':'passed','files':len(rows),'bytes':sum(r['bytes'] for r in rows),
    'fresh_independent_public_calls':373,'review_sha256':sha((OUT/'independent-review083.json').read_bytes()),
    'handoff_sha256':sha((OUT/'handoff.json').read_bytes()),'manifest_sha256':sha((OUT/'public-artifacts-manifest.json').read_bytes())}))
