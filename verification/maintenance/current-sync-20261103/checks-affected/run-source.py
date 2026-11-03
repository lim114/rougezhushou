from pathlib import Path
from hashlib import sha256
import subprocess,json,os,sys,re
r=Path.cwd();out=r/'verification/maintenance/current-sync-20261103/checks-affected';out.mkdir(exist_ok=False)
paths=[p.relative_to(r).as_posix()for p in(r/'rouge').glob('*.py')]+['scripts/verify_current_sync.py','tests/test_sampling_flow.py','tests/test_current_sync_ui.py','tests/test_new_run_capture_view_112.py']
pins=lambda:{p:sha256((r/p).read_bytes()).hexdigest()for p in paths};before=pins();results=[];env=dict(os.environ);env['QT_QPA_PLATFORM']='offscreen'
for module in ['tests.test_sampling_flow','tests.test_current_sync_ui','tests.test_new_run_capture_view_112']:
 target=out/module.rsplit('.',1)[-1];target.mkdir()
 with(target/'stdout.txt').open('wb')as a,(target/'stderr.txt').open('wb')as b:child=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','unittest','-v',module],stdout=a,stderr=b,env=env);code=child.wait()
 text=(target/'stderr.txt').read_text('utf8');match=re.search(r'Ran (\d+) tests?',text);row={'module':module,'actual_retained_PID':child.pid,'actual_observed_exit':code,'tests':int(match[1])if match else None};results.append(row);print(row,flush=True)
after=pins();value={'passed':all(x['actual_observed_exit']==0 for x in results)and before==after,'tests':sum(x['tests']or 0 for x in results),'results':results,'source_sha256_before':before,'source_sha256_after':after,'full_suite':False};(out/'process.json').write_text(json.dumps(value,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());assert value['passed']
