"""Root strict whole original/candidate API graph/text and caller audit."""
import argparse,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('guard','original','candidate','out'):p.add_argument('--'+k,required=True)
a=p.parse_args();R=Path('/workspace/rougezhushou');G=Path(a.guard);O=Path(a.out)
H=Path('/workspace/.continuation/section109-empty-target-original-probe-source-v1/native_evidence.py')
assert hashlib.sha256(H.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(H.parent))
from native_evidence import read_record,assert_native_equal,source_map
g=json.loads(G.read_text());assert source_map(R)==g['source_sha256'] and not O.exists()
for f,w in g['source_additional_sha256'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==w
count=0
def load(path):
 global count
 d=Path(path);r=json.loads((d/'observations.json').read_text())
 assert r['observation_complete'] and r['consumer_error_count']==0 and r['source_and_CORE_unchanged']
 rows={}
 for m in r['records']:
  v=read_record(d/'native',m);count+=1;assert_native_equal(v['after'],v['before'],m['case']+m['phase'])
  if m['kind']=='actual-public-consumer':assert v['error'] is None;rows[m['case'],m['phase']]=v
 assert len(rows)==r['actual_public_calls']
 return r,rows
old,ov=load(a.original);new,nv=load(a.candidate)
assert old['fixture']['sha256']==new['fixture']['sha256']
assert new['source_after']==g['source_sha256'] and old['CORE_after']==new['CORE_after']==g['source_additional_sha256']
assert ov.keys()==nv.keys()
for key,v in nv.items():assert_native_equal(v,ov[key],str(key)+':complete caller/results/types/order/alias graph')
assert source_map(R)==g['source_sha256']
r={'kind':'ROOT_ACTUAL_WHOLE_IDENTICAL_API_SAVED','section':g['section'],'passed':True,'workflow_complete':True,'source_drift':[],'cases':new['actual_completed_cases'],'native_records_decoded':count,'full_consumer_pairs':len(nv),'whole_numeric_graph_and_caller_unchanged':True,'whole_three_formatter_texts_unchanged':True,'no_project_formatter_reexecution':True,'native_windows_game_chat_verified':False}
O.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r))
