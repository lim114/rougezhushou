"""Seal explicit public080 design/evidence after root80 source and static review."""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
commit=sys.argv[1]
review_name=sys.argv[2]
commit=subprocess.check_output(['git','rev-parse',commit],cwd=REPO,text=True).strip()
assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()=='codex/p2-development'
freeze=json.loads((HERE/'public-source-freeze-080.json').read_text())
same=json.loads((HERE/'root-source-compatibility-080.json').read_text())
static=json.loads((HERE/'runner-static-review.json').read_text())
review=json.loads((HERE/review_name).read_text())
api=json.loads(gzip.decompress((HERE/'public-schema-final-080.json.gz').read_bytes()))
assert freeze['base_commit']==same['root_commit']==commit
assert same['git_blob_mismatch']==[] and len(freeze['source_sha256'])==same['public_file_count']
assert static['old1455_full_body_reconstructed_exactly'] and static['syntax_valid']
assert static['ready_for_actual_execution'] and not static['sections77_80_pending']
runner=HERE/'wine-ui-smoke-080.py'
digest=hashlib.sha256(runner.read_bytes()).hexdigest()
assert digest==static['runner_sha256']==review['runner_sha256']
assert review['status']=='FINAL_STATIC_PASS_READY_FOR_ROOT_ACTUAL_EXECUTION'
assert review['gui_executed'] is False and review['wine_executed'] is False
assert api['source_drift']==[] and api['source_hashes']==freeze['source_sha256']
assert api['gui_executed'] is False and api['wine_executed'] is False
assert api['sections']==static['new_case_design_by_section']
assert api['calls']==len(api['records'])==static['new_case_design_count']
handoff={
 'status':'READY_FOR_ROOT_ACTUAL_EXECUTION','base075_sha256':static['base075_sha256'],
 'root_source_commit':commit,'public_source_files':same['public_file_count'],
 'runner':{'source_path':str(runner),'bytes':runner.stat().st_size,'sha256':digest},
 'preserved_actual075_checks':1455,'preserved_skill_count':87,
 'old1455_complete_body_reconstructed_exactly':True,
 'new_design_checks_by_section':static['new_case_design_by_section'],
 'new_design_checks':static['new_case_design_count'],
 'planned_total_actual_checks':static['total_case_design_count'],
 'final_api_only_calls':api['calls'],'final_api_source_drift':[],
 'final_API_call_attribution':api['actual_API_call_attribution'],
 'API_preparation_failure_preserved':{'scope':'Initial UI contract wrongly required unknown damage-dependent healing at zero enemy lifetime; root production source was unchanged',
  'full_saved_receipt':'public-schema-final-080-failure.json.gz',
  'receipt_sha256':'53e99996dcffe475f8074e7dbad4759da20c692fe457f2b95bc0eb86312f98cc',
  'narrow_correction':'Zero enemy lifetime requires conversion total0 with no actual_total; own regeneration retains actual_totalNone.',
  'prior_completed_API_calls_repeated':0,'strict_related_saved_case_review_required':True},
 'new_qt_or_wine_execution_by_author':False,'actual_root_execution_still_required':True,
 'native_windows_game_desktop_verified':False,
 'independent_review':review_name,
 'public_manifest':str(HERE/'archivable-public-manifest.json'),
 'earlier_API_receipts_are_historical_design_preflight':{'interim076':432,'interim077':840},
 'prepared_output_files_are_external_public_only':True,
 'archive_scope':'All external public design, proofs, historical API receipts and initial/preparation diagnostics; duplicated public packages are reproducible from exact root git blobs and recorded hashes.',
 'excluded_duplicate_public_package_directories':[p.name for p in sorted(HERE.iterdir())if p.is_dir()and p.name.startswith('public-schema-')],
 'limits':['API/static evidence does not prove actual MainWindow execution.',
  'Wine compatibility does not establish native Windows/game/desktop behavior.',
  'No live capture, chat, game action, private state reset, or scheduling occurred.',
  'Actual native times, attachment/order, source acquisition and recipients remain within existing unknown boundaries.'],
}
(HERE/'handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
rows=[]
for path in sorted(HERE.rglob('*')):
 if not path.is_file():continue
 relative=path.relative_to(HERE)
 if any(part=='__pycache__'or part.startswith('public-schema-')and(HERE/part).is_dir()for part in relative.parts):continue
 if relative.as_posix()=='archivable-public-manifest.json':continue
 raw=path.read_bytes()
 rows.append({'source_path':str(path),'archive_path':relative.as_posix(),
  'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
manifest={'format_version':1,'scope':handoff['archive_scope'],'files':rows,
 'excluded_duplicate_public_package_directories':handoff['excluded_duplicate_public_package_directories'],
 'root_source_commit':commit,'all_initial_and_preparation_diagnostics_included':True}
manifest_path=HERE/'archivable-public-manifest.json'
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'handoff_sha256':hashlib.sha256((HERE/'handoff.json').read_bytes()).hexdigest(),
 'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'files':len(rows),
 'runner_sha256':digest,'API_only_calls':api['calls'],'new_Qt_or_Wine_executions':0},ensure_ascii=False))
