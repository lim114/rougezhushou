"""Read-only assessment of actual full3 evidence while its source is still unchanged.

This is not a successful-full-suite seal. Preserve its actual root1 and failures.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys
R=Path(__file__).resolve().parents[1];B=R/'.cache/full425-prepared/attempt-3';A=R/'verification/full-425/execution-attempt3'
sys.path[:0]=[str(B),str(R),str(R/'scripts')]
from full425_common import bound,sha
launch=json.loads((R/'.cache/full425-launch-input-attempt3.json').read_bytes());data,activation=bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256'])
process=json.loads((B/'root-launch/controller-process.json').read_bytes());assert process['status']=='completed'and process['actual_observed_exit']==1
spec=importlib.util.spec_from_file_location('actual425_baseline3_reader',R/'.cache/full425-post-attempt3/seal_summary425.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.BASE=B;m.ARCHIVE=A;m.FREEZE=R/'verification/full-425/source-freeze-attempt3.json';m.PARENT=launch['parent'];m.ATTEMPT=3;m.FREEZE_SHA=launch['freeze_sha256'];m.ACTIVATION_SHA=launch['activation_sha256'];m.REVIEW_SHA=sha(B/'review_results425.py')
manifest,files,container=m.verify_archive(sha(A/'archive-manifest.json'))
ledger=json.loads((A/'orchestration.json').read_bytes());review=json.loads((A/'automated-scope-review.json').read_bytes())
required=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']]
assert ledger['status']=='all_required_components_terminal'and ledger['required_components']==required and[r['name']for r in ledger['steps']]==required
assert len(required)==145 and len(data['p3_scripts'])==140 and len(data['selectors'])==672
assert {r['name']for r in ledger['steps']if r.get('child_primary_exit')not in(None,0)}=={'offline','legacy','current30'}
assert [r['name']for r in ledger['steps']if r['status'].startswith('not_run_')]==['legacy_typed']
assert all(r['status']=='terminal'for r in ledger['steps']if r['name']!='legacy_typed')
assert review['automated_available_scope_passed']is False and {r['component']for r in review['review_failures']}<={'offline','legacy','legacy_typed'}
_,terminal,closure,source_stable=m.load_readonly_helpers()
subset={'steps':[r for r in ledger['steps']if r['name']not in('offline','legacy','legacy_typed')]}
for row in subset['steps']:
 if row.get('child_primary_exit')!=0:continue
 log=(A/row['name']/'supervisor.json.stderr.log').read_text('utf8',errors='replace')
 assert not any(marker in log for marker in ['Traceback (most recent call last):','Error calling Python override','Exception ignored in:']),row['name']
raws,supers,proofs=m.verify_components(data,container,subset,review,terminal,closure,source_stable)
current=m.verify_current30(raws,supers,proofs,review);floor=m.verify_scope_floor(data)
from review_results425 import verify_diagnostic_layout
legacy_layout=verify_diagnostic_layout(container/'legacy','legacy',True)
# The original failed review never reached this independent layout observation.
# Assess it now without editing that original review or calling legacy a PASS.
layout_review={**review,'actual_diagnostic_layout_compatibility':{**review['actual_diagnostic_layout_compatibility'],'legacy':legacy_layout}}
layouts=m.verify_layout_scope(data,layout_review,container)
assert set(raws)==set(data['p3_scripts'])|{'current30','current29'}
offline=json.loads((A/'offline/actual/windows-offline.json').read_bytes());failed={r['test']for r in offline['failed_cases']}
expected={'tests.test_player_compact_389.Compact.test_compact_facts_pin_and_no_note_without_context','tests.test_player_feature_416.BindingTests.test_owned_native_identity_and_geometry'}
assert failed==expected and offline['failures']==2 and offline['errors']==0 and offline['tests_run']==7055
assert offline['source_sha256']==data['source_sha256']and offline['selectors']==data['selectors']and offline['source_drift']==[]and offline['qt_shutdown_error']is None
visual=R/'verification/full-425/root-visual-review.json';assert visual.exists();m.VISUAL=visual;view=m.verify_visual(sha(visual),files,sha(A/'archive-manifest.json'))
bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256'])
result={'section':425,'kind':'actual_full3_evidence_assessment_not_a_full_PASS','passed':True,'baseline_full_suite_passed':False,'actual_original_root_exit':1,'actual_failed_components_preserved':['offline','legacy'],'actual_not_run_preserved':['legacy_typed'],'original_current30_unavailable_not_passed':current['original_symlink_prerequisite_unavailable'],'scope_floor':floor,'actual_complete_source_sha256':data['source_sha256'],'actual_verified_native_supplements':len(data['p3_scripts']),'actual_verified_ordered_positions_including_unavailable30':len(subset['steps']),'actual_component_proofs':proofs,'original_current_scope':current,'actual_layout_scope_assessment':layouts,'failed_legacy_layout_independently_read_now_not_original_review_PASS':True,'original_offline':{k:offline[k]for k in ['tests_run','tests_passed','historical_or_declared_skips','failures','errors','failed_cases','unavailable_records','unavailable_parent_count','unavailable','skips']},'original_offline_receipt':m.proof(A/'offline/actual/windows-offline.json'),'original_full_archive':m.proof(A/'archive-manifest.json'),'original_freeze':m.proof(m.FREEZE),'baseline_visual':view,'original_review':m.proof(A/'automated-scope-review.json'),'reader_source_sha256':sha(Path(__file__)),'no_tests_or_windows_reexecuted':True,'future_repair_required':True,'no_private_state_access_or_copy':True}
out=R/'verification/full-425/baseline3-readonly-audit.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'assessment_written':True,'baseline_full_suite_passed':False,'actual_original_root_exit':1,'native_supplements_verified':len(data['p3_scripts']),'future_repair_required':True}))
