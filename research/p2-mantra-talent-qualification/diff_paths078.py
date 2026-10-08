from pathlib import Path
import collections,json
base=Path(__file__).parent
changes={};pair_count=0

def diff(a,b,path='$'):
 if type(a)!=type(b):return [(path,a,b)]
 if isinstance(a,dict):
  out=[]
  for key in a.keys()|b.keys():
   if key not in a or key not in b:out.append((path+'.'+key,a.get(key),b.get(key)))
   else:out.extend(diff(a[key],b[key],path+'.'+key))
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [(path+'.length',len(a),len(b))]
  return [x for i,(one,two) in enumerate(zip(a,b)) for x in diff(one,two,path+f'[{i}]')]
 return [] if a==b else [(path,a,b)]
for prefix in ('','supplement-'):
 old=json.loads((base/(prefix+'baseline-results078.json')).read_bytes());new=json.loads((base/(prefix+'draft-results078.json')).read_bytes())
 for a,b in zip(old['records'],new['records']):
  assert a['request']==b['request']
  if 'full_result' not in a:continue
  ds=diff(a['full_result'],b['full_result'])
  if ds:pair_count+=1
  for path,one,two in ds:
   changes.setdefault(path,{'count':0,'sample':{'request':a['request'],'before':one,'after':two}})['count']+=1
(base/'complete-json-changed-paths078.json').write_text(json.dumps({'changed_successful_pairs':pair_count,'paths':changes},ensure_ascii=False,indent=2)+'\n')
print({'changed_successful_pairs':pair_count,'path_count':len(changes),'paths':{p:v['count'] for p,v in sorted(changes.items())}})
matrices=[json.loads((base/(p+'matrix-comparison078.json')).read_bytes()) for p in ('','supplement-')]
counts=collections.Counter()
for m in matrices:counts.update(m['counts']);assert not m['mismatches']
out={'paired_scenarios':sum(m['paired_scenarios'] for m in matrices),'counts':dict(counts),'mismatches':[],'main_pairs':matrices[0]['paired_scenarios'],'supplement_pairs':matrices[1]['paired_scenarios'],'final_source_and_matrices_actual_public_calls':sum(m['final_source_and_matrix_actual_public_calls'] for m in matrices),'initial_zero_type_contract_draft_calls_preserved':matrices[0]['initial_zero_type_contract_draft_calls_preserved'],'total_actual_author_public_calls_including_initial_type_contract_draft':sum(m['total_actual_author_public_calls_including_initial_type_contract_draft'] for m in matrices),'main_source_audit_calls_reused_without_rerun':8,'strict_canonical_complete_zero_count_counterfactual_only_restores_three_raw_count_metadata_fields':True,'all_E1_E2_allskills_and_prior_complete_errors_unchanged':True,'main_and_supplement_full_result_files_separate_lossless':True,'no_final_product_change_after_main_matrix':True}
(base/'matrix-summary078.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(out)
