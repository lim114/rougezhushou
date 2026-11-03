from pathlib import Path
from types import ModuleType
from hashlib import sha256
import sys,json,subprocess,time
R=Path.cwd();out=R/'verification/sections/448-current-enemy-component/matrix'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
sys.path.insert(0,str(R))
from rouge import current_battle_reference as model
from rouge.current_enemy_forecast import forecasts
raw=(R/'research/current-enemy-component-448/before-current_enemy_forecast.py').read_bytes();old=ModuleType('rouge._forecast_before448');old.__package__='rouge';old.__file__=str(R/'rouge/current_enemy_forecast.py');exec(compile(raw,'<exact-before448-forecast>','exec'),old.__dict__)
paths=list((R/'rouge').glob('*.py'));before={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in paths};rows=[];counts={'stages':0,'references':0,'old_environment_components':0,'new_environment_components':0,'added_components':0,'legacy_rich_rows_exact_equal':0,'full_totals_unknown':0};cfg={'difficulty':{'value':15},'zone':{'id':'zone_1'}}
for sid in model.packet()['version']['current']['details']['stages']:
 stage=model.stage_reference(sid);a=old.forecasts(stage,cfg);b=forecasts(stage,cfg);assert a.keys()==b.keys();counts['stages']+=1
 for enemy in stage['enemies']:
  key=enemy['key'];prior=a[key];now=b[key];counts['references']+=1;was=prior['environment_component']is not None;has=now['environment_component']is not None;counts['old_environment_components']+=int(was);counts['new_environment_components']+=int(has);counts['added_components']+=int(has and not was)
  if was:assert prior==now,(sid,key);counts['legacy_rich_rows_exact_equal']+=1
  assert now['complete_current_total']is None and not now['actual_gameplay_verified'];counts['full_totals_unknown']+=1
  rows.append({'stage':sid,'reference_key':key,'enemy_id':enemy['id'],'level':enemy['level'],'tier':enemy['tier'],'prior_supported':was,'now_supported':has,'environment_component':now['environment_component'],'scope':now['scope'],'pending':now['pending']})
 assert counts['stages']%25 or True
 if counts['stages']%25==0:print({'completed_stages':counts['stages']},flush=True)
assert counts['old_environment_components']==counts['legacy_rich_rows_exact_equal']==1049 and counts['references']==2060 and counts['stages']==184 and counts['added_components']>0
assert all(sha256((R/p).read_bytes()).hexdigest()==h for p,h in before.items())
(out/'results.json').write_text(json.dumps({'passed':True,'counts':counts,'rows':rows,'source_sha256':before,'conditions':cfg,'scope':'Fixed current candidate references,not distinct enemies/spawns or actual game panels;new current components still omit unverified scripts/relics/phases.Original1049full rich rows equal,not independent actual-game accuracy.','private_state_or_game_operations':False},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(counts))
