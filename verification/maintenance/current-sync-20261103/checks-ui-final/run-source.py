from pathlib import Path
from hashlib import sha256
import subprocess,json,sys,os,re
r=Path.cwd();out=r/'verification/maintenance/current-sync-20261103/checks-ui-final';out.mkdir(exist_ok=False)
paths=[p.relative_to(r).as_posix()for p in(r/'rouge').glob('*.py')]+['tests/test_current_sync_ui.py','tests/test_player_urgent_experience.py','scripts/verify_current_sync.py'];pins=lambda:{p:sha256((r/p).read_bytes()).hexdigest()for p in paths};before=pins();results=[];env=dict(os.environ);env['QT_QPA_PLATFORM']='offscreen'
for module in ['tests.test_current_sync_ui','tests.test_player_urgent_experience']:
 target=out/module.rsplit('.',1)[-1];target.mkdir()
 with(target/'stdout.txt').open('wb')as a,(target/'stderr.txt').open('wb')as b:child=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','unittest','-v',module],stdout=a,stderr=b,env=env);code=child.wait()
 match=re.search(r'Ran (\d+) tests?',(target/'stderr.txt').read_text('utf8'));row={'module':module,'actual_retained_PID':child.pid,'actual_observed_exit':code,'tests':int(match[1])if match else None};results.append(row);print(row,flush=True)
after=pins();v={'passed':all(x['actual_observed_exit']==0 for x in results)and before==after,'results':results,'tests':sum(x['tests']or 0 for x in results),'source_sha256_before':before,'source_sha256_after':after,'full_suite':False};(out/'process.json').write_text(json.dumps(v,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());assert v['passed']
