"""Seal explicit independent public artifacts; manifest excludes itself."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
AUTHOR=OUT.with_name('p2-remaining-boolean-consumers-086-draft')


def digest(path):
    data=path.read_bytes()
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


manifest=AUTHOR/'archivable-author-review-manifest.json'
assert digest(manifest)['sha256']=='8e0d6a7607246573d16a97320a8cf71bf1db6e18765304b4f09916b99281443f'
for r in json.loads(manifest.read_bytes())['files']:
    assert digest(Path(r['source_path']))=={'sha256':r['sha256'],'bytes':r['bytes']}
freeze=AUTHOR/'review-freeze86.json'
assert digest(freeze)['sha256']=='aa066032869298b11b06819a2533fa53e78096dd725d4006f01bbde551edab55'
for r in json.loads(freeze.read_bytes())['files']:
    assert digest(Path(r['source_path']))=={'sha256':r['sha256'],'bytes':r['bytes']}
assert digest(AUTHOR/'section86.patch')['sha256']=='4834ec66e47ebdf8df0e8ef0c57e19dafe1693d80f51e9061245879c33005f87'
child=OUT/'source-subreview/public-artifacts-manifest-complete086.json'
assert digest(child)['sha256']=='112617d68411bb38910da04d7ef8f38d739f25a034fb430722083988d9f047f7'
child_rows=json.loads(child.read_bytes())['files'];assert len(child_rows)==15
for r in child_rows:assert digest(Path(r['source_path']))=={'sha256':r['sha256'],'bytes':r['bytes']}
for name in ('independent-saved-comparison086.json','independent-fresh-comparison086.json','independent-new-tests086.json'):
    assert json.loads((OUT/name).read_bytes())['status']=='PASS'
assert json.loads((OUT/'independent-new-tests086.json').read_bytes())['tests_run']==8
proof_names=('bound-review-freeze86.json','bound-author-review-handoff.json','bound-archivable-author-review-manifest.json',
             'independent-saved-comparison086.json','independent-fresh-comparison086.json','independent-new-tests086.json',
             'formatter-count-boundary086.json','preparation-diagnostics086.json','source-subreview/handoff-static-complete086.json',
             'source-subreview/public-artifacts-manifest-complete086.json')
final={'status':'PASS_FINAL_FROZEN','section':86,'baseline_commit':'9ef5a469673502754db3be320a8eece9a7fd18d4',
       'author_review_manifest_sha256':digest(manifest)['sha256'],'author_public_files_verified':84,
       'approved_patch_sha256':digest(AUTHOR/'section86.patch')['sha256'],
       'approved_product_and_test_files':json.loads(freeze.read_bytes())['files'],
       'independent_static_subreview':{'files':15,'bytes':276132,'manifest_sha256':digest(child)['sha256'],
          'fixed_tree723_path_blob_bytes_verified':True,'unchanged_old_draft721_verified':True,'strip_to_original_bytes':True,
          'actual_guard_qualification_signal_legacy_dominance_per_core_priority':True,'new_API_helper_tests':0},
       'saved_public_matrix':{'pairs':268,'public_calls_previously_captured_by_author':536,'new_calls_for_review':0,
          'counts':{'qualified_text_rejected':71,'whole_success_same':181,'old_errors_exact':16}},
       'saved_internal_isolated_cores':{'pairs':8,'previous_author_explicit_prepare_calls':8,'previous_author_explicit_core_calls':16,
          'review_new_helper_calls':0,'counts':{'qualified_text_rejected':2,'whole_success_same':6},
          'prepared_before_after_old_new_strict':True,'public_phase_or_native_clock_claimed':False},
       'fresh_independent':{'different_unique_inputs':12,'actual_public_calls':24,'counts':{'qualified_text_rejected':5,'whole_success_same':6,'old_errors_exact':1},
          'native_before_JSON_full_public_and_three_reports':True,'caller_catalog_isolation':True,'transparent_actual_internal_trace_only':True,
          'explicit_prepare_core_selected_talents_calls':0,'explicit_catalog_native_hash_cache_reads':26,
          'explicit_formatter_requests':51,'explicit_format_estimate_requests':17,'explicit_format_report_requests':34,
          'formatter_entries_or_internal_delegation_instrumented':False,'derived68_claimed_measured':False},
       'new_tests':{'methods':8,'failures':0,'errors':0,'skips':0,'exact_final_execution_count':1,
          'expectations_modified':False,'114_passed_existing_tests_repeated':False,'internal_API_counts_instrumented':False},
       'proofs':[{'source_path':str(OUT/name),**digest(OUT/name)} for name in proof_names],
       'unchanged_prior_source_packs':{'author28_manifest':'43fb5c6cfd2806cca065c734bbc0e30e20dc2a447ff0a2ade5d45baa71647de8',
          'independent17_manifest':'d72869af176ec745bfa9b4aee8e352b8fb791970ba8014960cf91d5949b48296',
          'original36_probes_or240_rank_or12_module_audit_repeated':False},
       'preparation_diagnostics':'One read-only guessed child receipt filename failed; corrected by manifest path, original error saved. No matrix/test retry.',
       'scope':'Per-core late errors and actual tested old errors only; no universal outer-error claim. Unknown native clocks/attachments remain unknown. Nonstring aliases retained.',
       'combined_grand_total_claimed':False,'normalization':None,'Qt':0,'Wine':0,'tracked_edits':0,'product_source_changes':0,
       'root_sole_integration_and_fresh_related_selected_full_checks':True,'root_checks_claimed_done_by_independent':False,
       'author_final_attachment_pack_pending':True,'all_listed_artifacts_stop_mutation_after_seal':True}
final_path=OUT/'independent-review-final086.json'
with final_path.open('x',encoding='utf-8') as f:json.dump(final,f,ensure_ascii=False,indent=2);f.write('\n')
paths=sorted(p for p in OUT.iterdir() if p.is_file())
paths.extend(Path(r['source_path']) for r in child_rows);paths.append(child)
assert len(paths)==len(set(paths))
rows=[{'source_path':str(p),'archive_path':str(p.relative_to(OUT)),**digest(p)} for p in paths]
manifest_final={'format_version':1,'status':'PASS_FINAL_FROZEN','files':rows,'count':len(rows),'bytes':sum(r['bytes'] for r in rows),
                'manifest_self_excluded':True,'includes_static_child_final15_plus_child_manifest':True,
                'includes_unchanged_original_pending_breakpoint':True,'excludes':['author baseline/draft full execution trees; their bytes verified and original source paths bound in author seal']}
manifest_path=OUT/'independent-public-manifest086.json'
with manifest_path.open('x',encoding='utf-8') as f:json.dump(manifest_final,f,ensure_ascii=False,indent=2);f.write('\n')
for r in rows:assert digest(Path(r['source_path']))=={'sha256':r['sha256'],'bytes':r['bytes']}
print(json.dumps({'status':'PASS_FINAL_FROZEN','final_path':str(final_path),'FINAL_SHA':digest(final_path)['sha256'],
                  'manifest_path':str(manifest_path),'MANIFEST_SHA':digest(manifest_path)['sha256'],
                  'public_files':len(rows),'public_bytes':sum(r['bytes'] for r in rows)},ensure_ascii=False))
