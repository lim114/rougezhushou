from pathlib import Path
from types import ModuleType,SimpleNamespace
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
from statistics import median
import ast,json,subprocess,sys,tempfile,time
R=Path.cwd();sys.path.insert(0,str(R));base=R/'verification/maintenance/history-reader-review-20261031';baseline='74b1f592434c5c39384580d9f9fd6ab26024391e'
from PySide6.QtWidgets import QApplication
from rouge import player_statistics_cohorts as cohorts,player_personal_statistics as stats,player_replay_nodes as nodes,player_cohort_ui as ui
from tests.test_player_statistics_cohorts_407 import record
from tests.test_history_reader_review import history_example
qt=QApplication([]);raws={}
def previous(name):
 path='rouge/'+name+'.py';raw=subprocess.check_output(['git','show',baseline+':'+path]);raws[path]=raw
 m=ModuleType('rouge._prior_'+name);m.__package__='rouge';exec(compile(raw,str(R/path),'exec'),m.__dict__);return m
old_cohorts=previous('player_statistics_cohorts');old_stats=previous('player_personal_statistics');old_nodes=previous('player_replay_nodes')
records=[]
from rouge.catalog import catalog
relic=next(iter(catalog()['relics']))
for i in range(40):
 rec=record('synthetic-'+str(i),[None,0,3,15,16][i%5],[None,'rogue_6_band_1','rogue_6_band_2','rogue_6_band_3'][i%4])
 state=rec['state'];state.update(history=[],resources={'gold':{'value':i%11}}if i%5 else{},relic_count=i%2,relics={relic:{'held':True}}if i%2 else{},tactical_tools={},inventory_verified=i%3!=0)
 rec['state_sha256']=sha256(json.dumps(state,sort_keys=True).encode()).hexdigest();records.append(rec)
records.append(record('synthetic-0',15,'rogue_6_band_3'));before=deepcopy(records);cases=0
for grade in(None,0,3,15,16,True,'15',cohorts.UNREAD):
 for squad in(None,'rogue_6_band_1','rogue_6_band_3','unknown',42,cohorts.UNREAD):
  assert old_cohorts.select_cohort(records,difficulty=grade,squad=squad)==cohorts.select_cohort(records,difficulty=grade,squad=squad)
  cases+=1
pages=[old_stats.PersonalStatisticsPage(SimpleNamespace(records=lambda:(records,[]))),stats.PersonalStatisticsPage(SimpleNamespace(records=lambda:(records,[])))]
page_cases=0
for grade in(None,0,3,15,cohorts.UNREAD):
 for squad in(None,'rogue_6_band_1','rogue_6_band_3',cohorts.UNREAD):
  outputs=[]
  for page,model in zip(pages,(old_cohorts,cohorts)):
   with patch.object(ui,'select_cohort',model.select_cohort):
    page.grade_filter.setCurrentIndex(page.grade_filter.findData(grade));page.squad_filter.setCurrentIndex(page.squad_filter.findData(squad));page.relic.setCurrentIndex(page.relic.findData(relic));page.render()
    outputs.append((deepcopy(page.result),deepcopy(page.samples.rows),page.detail.toPlainText()))
  assert outputs[0]==outputs[1],(grade,squad)
  page_cases+=1
calls=[];times=[]
for page,model in zip(pages,(old_cohorts,cohorts)):
 with patch.object(ui,'select_cohort',model.select_cohort),patch.object(model,'cohort',wraps=model.cohort)as qualified:
  page.render();calls.append(qualified.call_count)
 with patch.object(ui,'select_cohort',model.select_cohort):
  values=[]
  for repeat in range(5):
   start=time.perf_counter()
   for _ in range(20):page.render()
   values.append((time.perf_counter()-start)*1000)
  times.append(median(values))
assert calls==[160,40],calls
state,template,ids=history_example();a=old_nodes.node_steps(state);b=nodes.node_steps(state);fields=('index','zone_id','template','node_id','distance','event','label','time')
assert [{k:r[k]for k in fields}for r in a]==[{k:r[k]for k in fields}for r in b]
map_calls=[];map_times=[]
for model in(old_nodes,nodes):
 page=model.NodeReplayPage();working=deepcopy(state);page.refresh(working)
 with patch.object(model,'node_steps',wraps=model.node_steps)as projection:
  start=time.perf_counter()
  for i in range(50):
   working['history'].append({'kind':'resource_updated','resource':'gold','value':i,'at':200+i});page.refresh(working)
  map_times.append((time.perf_counter()-start)*1000);map_calls.append(projection.call_count)
 page.close();page.deleteLater()
assert map_calls==[50,0],map_calls
for name,raw in raws.items():
 if name.endswith('player_replay_nodes.py'):keep=('zone_label',)
 elif name.endswith('player_statistics_cohorts.py'):keep=('cohort','cohort_options','cohort_note')
 else:keep=('nonnegative_integer','complete_inventory','unique_archives','statistics','statistics_text')
 defs=lambda content:{n.name:ast.dump(n)for n in ast.parse(content).body if isinstance(n,ast.FunctionDef)}
 old,new=defs(raw),defs((R/name).read_bytes());assert all(old[k]==new[k]for k in keep)
for page in pages:page.close();page.deleteLater()
assert records==before
result={'passed':True,'baseline_commit':baseline,'sources':{n:{'before_sha256':sha256(raw).hexdigest(),'current_sha256':sha256((R/n).read_bytes()).hexdigest()}for n,raw in raws.items()},
 'cohort_input_cases_equal':cases,'full_statistic_sample_and_text_cases_equal':page_cases,'unique_synthetic_archives':40,'duplicate_old_version_not_counted':True,
 'classification_calls_per_full_render_before_after':calls,'median_twenty_stable_renders_ms':times,'timing_repeats':5,
 'unchanged_original_node_step_fields':list(fields),'original_node_step_fields_equal':True,'history_map_new_behavior':'Prefix-only accumulation, original passed type/content, exact prior position, qualified same-zone resources; deliberately differs from old single-selected-node view.',
 'unrelated_history_append_projection_calls_before_after':map_calls,'unrelated_history_append_fifty_refreshes_ms':map_times,'timing_scope':'isolated local component work only, not startup, drawing, recognition or whole application speed',
 'statistic_math_denominators_and_qualification_AST_unchanged':True,'personal_state_read':False,'external_calls':False,'whole_program_complete':False}
(base/'before-after.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');(base/'comparison-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'passed':True,'cohort_cases':cases,'page_cases':page_cases,'classification_calls':calls,'map_calls':map_calls,'render_ms':times,'map_ms':map_times}))
