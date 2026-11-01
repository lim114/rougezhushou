from pathlib import Path
from hashlib import sha256
import sys,json,re,subprocess
R=Path.cwd();B=R/'verification/maintenance/reward-overview-20261101';out=B/'related';out.mkdir(exist_ok=False)
modules=['tests.test_reward_overview_review','tests.test_current_reward_reference_315','tests.test_current_reward_view_315','tests.test_current_reward_integration_315','tests.test_current_settlement_modes_view_362','tests.test_compact_battle_review','tests.test_enemy_overview_review','tests.test_enemy_table_reading_review','tests.test_battle_overview_sections_review']
s=(R/'verification/maintenance/battle-overview-sections-20261101/related/bootstrap.py').read_text('utf8');s=re.sub(r'modules=\[.*?\]',f'modules={modules!r}',s,count=1).replace('battle-overview-sections-20261101/related','reward-overview-20261101/related');(out/'bootstrap.py').write_text(s,'utf8')
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*')if p.suffix in('.py','.cjs')};(out/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
assert sources=={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*')if p.suffix in('.py','.cjs')}
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'application_source_unchanged':True},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure':(out/'stderr.txt').read_text('utf8')[-3500:]if code else None},ensure_ascii=False));raise SystemExit(code)
