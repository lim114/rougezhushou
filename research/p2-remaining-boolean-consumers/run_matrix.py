"""One current public call per unique case; preserve native trees and three reports."""
import copy
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path
from matrix_plan import make_plan,typed,json_value

OUT=Path(__file__).resolve().parent


def encoded(v):return json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
def sha(v):return hashlib.sha256(encoded(typed(v))).hexdigest()


def main():
 package=sys.argv[1];assert package in ('baseline','draft');sys.path.insert(0,str(OUT/package))
 from rouge.catalog import catalog
 from rouge.damage import calculate_damage
 from rouge.estimate import format_estimate
 from rouge.reporting import format_report
 cases=make_plan();keys=[encoded(typed(row['input'])) for row in cases]
 assert len(keys)==len(set(keys))
 frozen=json.loads((OUT/'current-baseline-freeze.json').read_bytes())
 for row in frozen['files']:
  if package=='draft' and row['path'] in ('rouge/damage.py','rouge/operator_engine.py'):continue
  data=(OUT/package/row['path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
 before_catalog=sha(catalog());accepted=errors=reports=0;start=time.monotonic();decoded=hashlib.sha256();bytes_decoded=0
 name=OUT/(package+'-matrix.jsonl.gz')
 with name.open('xb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as stream:
  for i,case in enumerate(cases,1):
   value=copy.deepcopy(case['input']);before=typed(value)
   row={'index':i,'label':case['label'],'expect':case['expect'],'field':case['field'],
        'input':json_value(value),'input_typed_before':before}
   try:result=calculate_damage(value)
   except Exception as error:
    errors+=1;row.update(outcome='error',error_type=type(error).__name__,error_message=str(error))
   else:
    accepted+=1;native=typed(result)
    texts={'estimate':format_estimate(result),'user':format_report(result),'technical':format_report(result,technical=True)}
    reports+=3;row.update(outcome='accepted',result=result,result_typed=native,reports=texts)
   row['input_typed_after']=typed(value);row['input_unchanged']=before==row['input_typed_after']
   row['catalog_unchanged']=sha(catalog())==before_catalog
   data=encoded(row)+b'\n';stream.write(data);decoded.update(data);bytes_decoded+=len(data)
   assert row['input_unchanged'] and row['catalog_unchanged'],case['label']
   if i%40==0:print(json.dumps({'package':package,'completed':i,'total':len(cases)}),flush=True)
 summary={'passed':True,'package':package,'base_commit':frozen['base_commit'],'unique_public_calls':len(cases),
          'accepted':accepted,'errors':errors,'formatter_calls':reports,'new_project_helper_calls':0,
          'elapsed_seconds':time.monotonic()-start,'gzip_sha256':hashlib.sha256(name.read_bytes()).hexdigest(),
          'gzip_bytes':name.stat().st_size,'decoded_sha256':decoded.hexdigest(),'decoded_bytes':bytes_decoded,
          'typed_tree_captured_before_json_encoding':True,'all_caller_catalog_unchanged':True,
          'nonfinite_input_serialization':'native float hex retained in typed tree; raw input uses annotated saved_nonfinite_float only',
          'old_source_36_probes_repeated':False,'tests_run':0,'Qt':0,'Wine':0,'tracked_edits':0}
 with (OUT/(package+'-matrix-summary.json')).open('x',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
