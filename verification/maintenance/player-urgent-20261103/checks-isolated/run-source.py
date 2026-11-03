from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,re
r=Path.cwd();out=r/'verification/maintenance/player-urgent-20261103/checks-isolated';out.mkdir(exist_ok=False)
prior=json.loads((r/'verification/maintenance/player-urgent-20261103/checks-final/process.json').read_bytes());paths=prior['source_sha256_after']
pins=lambda:{p:sha256((r/p).read_bytes()).hexdigest()for p in paths}
before=pins();results=[]
modules=['tests.test_player_toolbar_412','tests.test_player_urgent_experience','tests.test_owned_window_follow_review','tests.test_branch_choices_046','tests.test_current_enemy_forecast_review','tests.test_current_battle_view_314']
for module in modules:
 target=out/module.rsplit('.',1)[-1];target.mkdir()
 with(target/'stdout.txt').open('wb')as a,(target/'stderr.txt').open('wb')as b:
  c=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','unittest','-v',module],stdout=a,stderr=b);code=c.wait()
 text=(target/'stderr.txt').read_text('utf8');match=re.search(r'Ran (\d+) tests?',text);results.append({'module':module,'actual_retained_PID':c.pid,'actual_observed_exit':code,'tests':int(match[1])if match else None});print(results[-1],flush=True)
after=pins();value={'passed':all(v['actual_observed_exit']==0 for v in results)and before==after,'results':results,'tests':sum(v['tests']or 0 for v in results),'source_sha256_before':before,'source_sha256_after':after,'full_suite':False,'separate_native_Qt_processes':True};(out/'process.json').write_text(json.dumps(value,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());assert value['passed']
