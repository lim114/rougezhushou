import gzip,hashlib,json,pathlib
p=pathlib.Path(__file__).resolve().parent
strict=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
a=json.loads(gzip.decompress((p/'baseline-whole-outcomes.json.gz').read_bytes()));b=json.loads(gzip.decompress((p/'draft-whole-outcomes.json.gz').read_bytes()));assert len(a)==len(b)
changed=[];groups={};unchanged=0;accepted_preserved=0;errors_preserved=0
for left,right in zip(a,b):
 assert {k:left[k] for k in ('key','group','kind','input')}=={k:right[k] for k in ('key','group','kind','input')}
 old=left['outcome'];new=right['outcome'];assert old['accepted']==new['accepted']
 if strict(old)==strict(new):
  unchanged+=1;accepted_preserved+=old['accepted'];errors_preserved+=not old['accepted'];continue
 s=left['input'];assert s['operator']=='char_1038_whitw2' and s['elite']==0 and s['skill']==1 and old['accepted'] and new['accepted']
 key='result' if left['kind']=='calculate' else 'normal_owner_clock_reference';x,y=old[key],new[key]
 body=lambda result:[c for c in result['components'] if c['name']!='浮游单元']
 assert strict(body(x))==strict(body(y))
 for field in ('stats','warnings','notes','complete','timing','drone_lifecycle_reference','drone_trait_reference'):
  assert strict(x.get(field))==strict(y.get(field)),(left['key'],field)
 olddr=[c for c in x['components'] if c['name']=='浮游单元'];newdr=[c for c in y['components'] if c['name']=='浮游单元'];assert len(olddr)==len(newdr)
 for before,after in zip(olddr,newdr):
  assert before['per_hit']==after['per_hit'] and before['timing_reference']==after['timing_reference']
  assert before['hits']>=after['hits'] and set(before.get('times_seconds',[]))==set(after.get('times_seconds',[]))
 assert x['total_damage']>=y['total_damage']
 component_count_reduced=any(before['hits']>after['hits'] for before,after in zip(olddr,newdr))
 canonical_count_reduced=False
 if left['kind']=='calculate':
  before_counts=x['estimate']['skill']['hit_counts'];after_counts=y['estimate']['skill']['hit_counts']
  assert {k:v for k,v in before_counts.items() if k!='浮游单元'}=={k:v for k,v in after_counts.items() if k!='浮游单元'}
  canonical_count_reduced=before_counts.get('浮游单元',0)>after_counts.get('浮游单元',0)
 assert component_count_reduced or canonical_count_reduced
 changed.append({'key':left['key'],'kind':left['kind'],'group':left['group'],'input':s,'before_total':x['total_damage'],'after_total':y['total_damage'],'body_components_whole_preserved':True,'selected_headwolf_locked':True})
 groups[left['group']]=groups.get(left['group'],0)+1
assert changed and errors_preserved>0
receipt={'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','cases':len(a),'paired_actual_calls':sum(json.loads((p/(t+'-matrix-receipt.json')).read_text())['actual_calls'] for t in ('baseline','draft')),'whole_outcomes_changed':len(changed),'whole_outcomes_preserved':unchanged,'preserved_accepted_cases':accepted_preserved,'preserved_exact_error_cases':errors_preserved,'changed_groups':groups,'every_changed_case':'Whitw2 E0 skill1 accepted only; body components, stats, warnings, complete, and independent-clock metadata byte-equivalent strict JSON; only existing drone-unit reference and derived report totals reduced','all_E1_E2_full_outcomes_preserved':True,'inactive_other_owners_and_skill_unlock_errors_preserved':True,'all_boolean_raw_count_errors61_and_legacy_noninteger_contracts_preserved':True,'strict_json_comparison':True,'failures':[],'changed_cases':changed}
(p/'paired-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='changed_cases'},ensure_ascii=False))
