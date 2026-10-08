from pathlib import Path
import datetime,difflib,hashlib,json,subprocess
base=Path(__file__).parent;root=Path('/workspace/rougezhushou');name='rouge/operator_engine.py';test_name='tests/test_mantra_talent_qualification.py'
old=(base/'baseline'/name).read_bytes().decode();new=(base/'draft078'/name).read_bytes().decode()
patch=f'diff --git a/{name} b/{name}\n'+''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
test=(base/'test_mantra_talent_qualification.py').read_text()
patch+=f'diff --git a/{test_name} b/{test_name}\nnew file mode 100644\n'+''.join(difflib.unified_diff([],test.splitlines(True),fromfile='/dev/null',tofile='b/'+test_name))
path=base/'section78.patch';path.write_bytes(patch.encode())
freeze=json.loads((base/'baseline-freeze078.json').read_bytes())
for relative,record in freeze['files'].items():
 raw=(base/'baseline'/relative).read_bytes();assert hashlib.sha256(raw).hexdigest()==record['sha256'] and len(raw)==record['bytes']
 if relative!=name:assert (base/'draft078'/relative).read_bytes()==raw
source=json.loads((base/'source-receipt078.json').read_bytes())
for rec in source['sources'].values():
 raw=Path(rec['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==rec['sha256'] and len(raw)==rec['bytes']
matrix=json.loads((base/'matrix-summary078.json').read_bytes());nt=json.loads((base/'new-tests078.json').read_bytes());rt=json.loads((base/'related-tests078.json').read_bytes())
assert not matrix['mismatches'] and nt['passed']==9 and rt['passed']==83 and nt['skipped']==rt['skipped']==0
assert nt['available_checks_passed'] and rt['available_checks_passed']
sha=hashlib.sha256((base/'draft078'/name).read_bytes()).hexdigest();assert sha==nt['source_start_sha256']==nt['source_end_sha256']==rt['source_start_sha256']==rt['source_end_sha256']
end={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_intact':True,'baseline_public_files_verified':freeze['file_count'],'other_draft_public_files_unchanged':freeze['file_count']-1,'changed_source_hashes':{name:sha},'new_test_sha256':hashlib.sha256((base/'test_mantra_talent_qualification.py').read_bytes()).hexdigest(),'raw_tables_rehashed_at_end':True,'no_final_product_source_changes_after_main_and_supplement_matrices':True,'77_patch_not_included':True}
(base/'author-end-source078.json').write_text(json.dumps(end,ensure_ascii=False,indent=2)+'\n')
check=subprocess.run(['git','apply','--check',str(path)],cwd=root,capture_output=True,text=True);reverse=None;applied=False
if check.returncode:
 reverse=subprocess.run(['git','apply','--reverse','--check',str(path)],cwd=root,capture_output=True,text=True);applied=reverse.returncode==0
rf=base/'independent-review078.json';review=json.loads(rf.read_bytes()) if rf.exists() else None
if review:
 assert review['status']=='independent_review_passed' and not review['blockers']
 assert review['patch_sha256']==hashlib.sha256(path.read_bytes()).hexdigest() and review['changed_source_hashes']==end['changed_source_hashes']
exclude={'manifest078.json','handoff-receipt078.json','package078.log','final-package078.log'}
names=[p.name for p in sorted(base.iterdir()) if p.is_file() and p.name not in exclude]
files={n:{'sha256':hashlib.sha256((base/n).read_bytes()).hexdigest(),'bytes':(base/n).stat().st_size} for n in names}
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'scope':'complete public original selectors, frozen source, full JSON/error matrices, all initial diagnostics and independent review; excludes package copies/private state'}
(base/'manifest078.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'section':78,'baseline_commit':freeze['commit'],'baseline_public_files':freeze['file_count'],'baseline_intact':True,'observed_root_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'root_apply_check':{'exit_code':check.returncode,'stderr':check.stderr},'root_patch_already_applied':applied,'root_reverse_apply_check':None if reverse is None else {'exit_code':reverse.returncode,'stderr':reverse.stderr},'patch_sha256':files['section78.patch']['sha256'],'changed_source_hashes':end['changed_source_hashes'],'new_test_sha256':end['new_test_sha256'],'changed_files':[name,test_name],'register_new_test_required':'scripts/verify_cloud.py MODULES tests.test_mantra_talent_qualification; no outdated runner hunk','suggested_research_directory':'research/p2-mantra-talent-qualification','new_tests_passed':9,'related_tests_passed':83,'skips':0,'paired_scenarios':matrix['paired_scenarios'],'matrix_counts':matrix['counts'],'final_source_and_matrix_actual_public_calls':matrix['final_source_and_matrices_actual_public_calls'],'initial_zero_type_contract_draft_calls_preserved':matrix['initial_zero_type_contract_draft_calls_preserved'],'total_actual_author_public_calls_including_initial_type_contract_draft':matrix['total_actual_author_public_calls_including_initial_type_contract_draft'],'source_audit_calls_reused_without_rerun':8,'locked_talent_only_effective_count_zeroed_retaining_raw_declaration':True,'strict_full_canonical_baseline_zero_count_counterfactual_plus_only_three_declared_count_metadata_fields':True,'qualified_zero_attack_and_immunity_unknowns_global_palsy_sources_S3_overflow_SP_and_prior_errors_unchanged':True,'native_palsy_snapshot_and_S1_S3_event_clocks_remain_unknown':True,'77_patch_not_included':True,'no_tracked_private_state_native_binaries_gui_or_wine':True,'independent_review_status':'passed' if review else 'pending_final_frozen_patch_review','independent_fresh_paired_scenarios':review['fresh_paired_scenarios'] if review else None,'independent_fresh_public_calls':review['public_calls'] if review else None,'independent_new_tests_passed':review['new_tests_passed'] if review else None,'independent_saved_author_pairs_strictly_recompared':review['saved_author_pairs_strictly_recompared'] if review else None,'independent_review_sha256':hashlib.sha256(rf.read_bytes()).hexdigest() if review else None,'manifest_sha256':hashlib.sha256((base/'manifest078.json').read_bytes()).hexdigest()}
(base/'handoff-receipt078.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(out);assert check.returncode==0 or applied
