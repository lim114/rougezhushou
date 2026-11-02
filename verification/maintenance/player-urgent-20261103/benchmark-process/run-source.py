from pathlib import Path
import sys,ast,subprocess,types,json,time,statistics
from hashlib import sha256
r=Path.cwd();sys.path.insert(0,str(r))
from PySide6.QtWidgets import QApplication
from rouge.current_battle_view import CurrentBattlePanel
app=QApplication([])
base='a6923919b7d419f15b18d98b67a8ea0c8c5d7bfb'
raw=subprocess.check_output(['git','show',base+':rouge/current_battle_view.py'])
tree=ast.parse(raw.decode('utf8'));node=next(m for c in tree.body if isinstance(c,ast.ClassDef)and c.name=='CurrentBattlePanel'for m in c.body if isinstance(m,ast.FunctionDef)and m.name=='set_context')
namespace=dict(CurrentBattlePanel.set_context.__globals__);exec(compile(ast.Module(body=[node],type_ignores=[]),'<frozen-baseline-set_context>','exec'),namespace)
old=CurrentBattlePanel('ro6_n_1_1');new=CurrentBattlePanel('ro6_n_1_1');old.set_context=types.MethodType(namespace['set_context'],old)
config=lambda t:{'difficulty':{'value':15,'captured_at':t},'zone':{'id':'zone_1','captured_at':t}}
old.set_context(config(0));new.set_context(config(0));rows=[]
for round_id,order in enumerate(((old,new),(new,old))):
 for i in range(1,5):
  times={}
  for p in order:
   t=time.perf_counter();p.set_context(config(round_id*4+i));times['baseline'if p is old else'current']=(time.perf_counter()-t)*1000
  assert old.run_config==new.run_config and old.enemy_forecasts==new.enemy_forecasts
  rows.append({'times_ms':times,'same_latest_context_and_numbers':True})
old.close();new.close();app.processEvents()
result={'scope':'isolated original enemy reader; same synthetic public difficulty/zone repeated with changed read timestamps; warm AB and BA orders','gameplay_latency_improvement_claimed':False,'baseline_commit':base,'baseline_file_sha256':sha256(raw).hexdigest(),'current_file_sha256':sha256((r/'rouge/current_battle_view.py').read_bytes()).hexdigest(),'rounds':rows,'median_ms':{k:statistics.median(x['times_ms'][k]for x in rows)for k in('baseline','current')},'private_game_data_used':False}
out=r/'verification/maintenance/player-urgent-20261103/enemy-context-benchmark.json';out.write_text(json.dumps(result,indent=2)+'\n','utf8');print(result['median_ms'])
