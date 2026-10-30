from pathlib import Path
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
from copy import deepcopy
import sys,json,ast,subprocess,time
R=Path.cwd();sys.path.insert(0,str(R));base=R/'verification/maintenance/node-card-review-20261031'
from rouge import public_node_statistics as current,node_catalog as catalog
baseline='cbe2a2609a704e1d8c7b20b3858c58792c7cef5c'
def old_module(name):
 path='rouge/'+name+'.py';raw=subprocess.check_output(['git','show',baseline+':'+path]);m=ModuleType('rouge._old_'+name);m.__package__='rouge';m.__file__=str(R/path);exec(compile(raw,m.__file__,'exec'),m.__dict__);return m,raw
old,old_raw=old_module('public_node_statistics');old_catalog,old_cat_raw=old_module('node_catalog')
data=current.load();queries=[(f,d)for f in('0','1','2','3','4','remembrance')for d in range(101)]
t=time.perf_counter();before=[old.frequency_rows(data,*q)for q in queries];before_ms=(time.perf_counter()-t)*1000
t=time.perf_counter();index=current.FrequencyIndex(data);after=[index.rows(*q)for q in queries];after_ms=(time.perf_counter()-t)*1000
assert before==after
def funcs(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
a=funcs(old_raw);b=funcs((R/'rouge/public_node_statistics.py').read_bytes())
for name in a:
 if name in('frequency_rows','validate'):continue
 assert ast.dump(a[name])==ast.dump(b[name]),name
check=deepcopy(b['validate']);guard=check.body[0].test
assert isinstance(guard,ast.BoolOp)and isinstance(guard.op,ast.Or)and len(guard.values)==2
assert ast.unparse(guard.values[0])=='not isinstance(data, dict)'
check.body[0].test=guard.values[1]
guard=check.body[3].test
assert isinstance(guard,ast.BoolOp)and isinstance(guard.op,ast.Or)and len(guard.values)==3
assert ast.unparse(guard.values[0])=='not isinstance(meta, dict)'
check.body[3].test.values=guard.values[1:]
assert ast.dump(a['validate'])==ast.dump(check),'Only the top-level and metadata object guards may differ.'
a=funcs(old_cat_raw);b=funcs((R/'rouge/node_catalog.py').read_bytes())
assert all(ast.dump(v)==ast.dump(b[k])for k,v in a.items()if k!='node_dossier')
cases=[]
for kind in('未知的诡秘','不期而遇','作战','林间空地','曲折密道'):
 for history in('none','event','battle'):
  node={'id':'n','row':1,'col':1,'observed_type':kind,'prediction':{'candidates':['不期而遇','诡意行商']}}
  if history=='event':node['remembered_content']={'kind':'event','title':'桑尼的邀请'}
  if history=='battle':node['remembered_content']={'kind':'battle','title':'遗忘时间','variant_id':'ro6_n_1_2'}
  graph={'zone_id':'zone_1','template_id':'isolated','nodes':[node]}
  outputs=[];reads=[]
  for m in(old_catalog,catalog):
   calls=[];method=m.battle_candidates
   def counted(*args,**kwargs):
    if not args and kwargs.get('context')=='all':calls.append(True)
    return method(*args,**kwargs)
   with patch.object(m,'battle_candidates',side_effect=counted):value=m.node_dossier(graph,'n',floor=1,difficulty=15)
   outputs.append(json.dumps(value,ensure_ascii=False,sort_keys=True));reads.append(len(calls))
  assert outputs[0]==outputs[1],(kind,history)
  assert reads==([1,1]if history=='battle'else[1,0]),reads
  cases.append({'type':kind,'history':history,'full_result_before_and_after_sha256':sha256(outputs[0].encode()).hexdigest(),'unfiltered_stage_directory_reads_before_after':reads})
result={'baseline_commit':baseline,'source':{n:{'before_sha256':sha256(raw).hexdigest(),'current_sha256':sha256((R/n).read_bytes()).hexdigest()}for n,raw in [('rouge/public_node_statistics.py',old_raw),('rouge/node_catalog.py',old_cat_raw)]},
 'public_query_cases':len(queries),'all_public_rows_exactly_equal':True,'rows_sha256':sha256(json.dumps(before,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
 'lookup_batch_ms':{'before':before_ms,'after_including_index_build':after_ms},'timing_scope':'one local direct-query batch, not warm map cache, application, or recognition speed',
 'domain_cases':cases,'full_domain_results_equal':True,'fetch_and_parser_AST_unchanged':True,'valid_schema_validation_unchanged_except_object_type_guards':True,
 'non_object_input_now_ValueError_not_AttributeError':True,'personal_or_game_inputs':False,'uploads':0}
(base/'before-after-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
(base/'comparison-current-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'queries':len(queries),'domain_cases':len(cases),'passed':True}))
