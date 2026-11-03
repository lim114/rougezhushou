from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,runpy
R=Path.cwd();B=R/'verification/maintenance/full-checks-cancelled-20261101';out=B/'targeted-index-tests';out.mkdir(exist_ok=False)
files=['scripts/update_cloud_index.py','tests/test_cloud_index_sync.py'];before={p:sha256((R/p).read_bytes()).hexdigest()for p in files}
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','unittest','-v','tests.test_cloud_index_sync'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
same=before=={p:sha256((R/p).read_bytes()).hexdigest()for p in files};(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'source_sha256':before,'tested_source_unchanged':same,'scope':'Only28 cloud-index consistency and cancelled-policy tests;not full suite.','full_check_executed':False},indent=2)+'\n','utf8');assert code==0 and same,(out/'stderr.txt').read_text('utf8')[-3000:]
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==449 and cp['next_section']==450
assert all(v is None for v in (cp['next_full_validation_after'],cp['policy']['next_full_validation_after'],cp['current_batch_commit_policy']['next_full_validation_after'],cp['current_batch']['next_full_validation_after']))
for p in files+['AGENTS.md']:(B/('before-'+Path(p).name)).write_bytes(subprocess.check_output(['git','show','ce7b27f044f7e92c70717663f217c5aca5996dcb:'+p]))
summary=json.loads((B/'summary.json').read_bytes());summary.pop('verification_pending');summary.update(passed=True,targeted_index_tests=28,targeted_tests_receipt='verification/maintenance/full-checks-cancelled-20261101/targeted-index-tests/process.json',restoration_guard_tested=True,old_historical_receipt_retained=True);(B/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf8')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
(B/'verify-source.py').write_bytes(Path(__file__).read_bytes())
names=['AGENTS.md','DEVELOPMENT_CHECKPOINT.json','PROJECT_REQUIREMENTS.md','PROJECT_PROGRESS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','CLOUD_INDEX.json','CLOUD_HANDOFF.md',*files]+[p.relative_to(R).as_posix()for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json']
manifest={n:{'sha256':sha256((R/n).read_bytes()).hexdigest(),'bytes':(R/n).stat().st_size}for n in names};(B/'archive-manifest.json').write_text(json.dumps({'scope':'Explicit public policy and index maintenance;no private state,UI or full-suite run.','files':manifest},ensure_ascii=False,indent=2)+'\n','utf8');print({'passed':True,'targeted_tests':28,'functional_section_unchanged':449,'full_schedule_cancelled':True})
