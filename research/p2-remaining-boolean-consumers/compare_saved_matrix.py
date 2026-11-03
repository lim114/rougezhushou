"""Strict comparison of saved current calls, no API or project helpers."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent


def load(package):
 path=OUT/(package+'-matrix.jsonl.gz');data=gzip.decompress(path.read_bytes())
 summary=json.loads((OUT/(package+'-matrix-summary.json')).read_bytes())
 assert summary['passed'] and summary['decoded_sha256']==hashlib.sha256(data).hexdigest()
 assert summary['decoded_bytes']==len(data)
 return [json.loads(line) for line in data.splitlines()]


def main():
 old=load('baseline');new=load('draft');assert len(old)==len(new)==268
 counts=Counter();errors=[]
 for a,b in zip(old,new):
  assert all(a[k]==b[k] for k in ('index','label','expect','field','input_typed_before'))
  assert all(r['input_unchanged'] and r['catalog_unchanged'] and r['input_typed_before']==r['input_typed_after'] for r in (a,b))
  if a['expect']=='changed':
   ok=a['outcome']=='accepted' and b['outcome']=='error' and b['error_type']=='ValueError' and b['error_message']==a['field']+' 不接受文本条件；请使用布尔值。'
   category='qualified_text_rejected'
  elif a['expect']=='old_error':
   ok=a['outcome']==b['outcome']=='error' and (a['error_type'],a['error_message'])==(b['error_type'],b['error_message'])
   category='exact_old_error'
  else:
   ok=a['outcome']==b['outcome']=='accepted' and a['result_typed']==b['result_typed'] and a['result']==b['result'] and a['reports']==b['reports']
   category='whole_accepted_native_and_three_reports_unchanged'
  if not ok:errors.append({'index':a['index'],'label':a['label'],'expected':a['expect'],
                            'old_outcome':a['outcome'],'new_outcome':b['outcome'],
                            'new_error_message':b.get('error_message')})
  else:counts[category]+=1
 result={'passed':not errors,'pairs':len(old),'counts':dict(counts),'mismatches':errors,
         'fresh_public_calls':0,'fresh_project_helper_calls':0,'saved_public_calls_compared':536,
         'strict_preencoding_native_trees':True,'all_caller_catalog_unchanged':True,
         'three_texts_exact_for_every_unchanged_accepted_pair':True}
 with (OUT/'saved-matrix-comparison-attempt-1.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
 if errors:raise SystemExit(1)


if __name__=='__main__':main()
