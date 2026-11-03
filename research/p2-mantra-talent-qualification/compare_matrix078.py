from pathlib import Path
import argparse,collections,copy,datetime,hashlib,json
base=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--supplement',action='store_true');args=parser.parse_args()
suffix='supplement-' if args.supplement else ''
before=json.loads((base/(suffix+'baseline-results078.json')).read_bytes());after=json.loads((base/(suffix+'draft-results078.json')).read_bytes())
OP='char_4204_mantra';NAME='麻痹触发天赋';LABEL='声明当前目标麻痹触发次数'
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
index={canonical(r['request']):r for r in before['records']}
assert before['paired_scenario_records']==after['paired_scenario_records']
if not args.supplement:assert before['paired_scenario_records']==1225
counts=collections.Counter();pairs=[];mismatches=[]
for old,new in zip(before['records'],after['records']):
 assert (old['group'],old['request'])==(new['group'],new['request'])
 for r in (old,new):
  if 'full_result' in r:assert digest(r['full_result'])==r['full_result_sha256']
 request=old['request'];golden_sha=None
 if 'error' in old:
  kind='prior_complete_errors_unchanged';passed=canonical(old['error'])==canonical(new.get('error'))
 elif request['operator']==OP and request.get('elite',2)==0 and float(request.get('palsy_triggers',0))>0:
  zero=index[canonical({**request,'palsy_triggers':0})]
  assert 'full_result' in zero
  expected=copy.deepcopy(zero['full_result']);declared=float(request['palsy_triggers'])
  references=[expected['external_event_reference']]
  if 'window_reference' in references[0]:references.append(references[0]['window_reference'])
  for ref in references:
   rows=[r for r in ref['parameter_rows'] if r[0]==LABEL];assert len(rows)==1;rows[0][1]=declared
  sections=[s for s in expected['report']['sections'] if s['id']=='external_events'];assert len(sections)==1
  metrics=[m for m in sections[0]['metrics'] if m['key']=='parameter_0' and m['label']==LABEL];assert len(metrics)==1
  metrics[0]['value']=declared
  # Compare complete canonical JSON, including every numerical total, derived
  # cycle/subtotal, status, unknown source, resource, cultivation and report row.
  passed=canonical(expected)==canonical(new.get('full_result'));golden_sha=digest(expected)
  component=next(c for c in new['full_result']['components'] if c['name']==NAME)
  passed=passed and component['hits']==component['total']==component['per_hit']==0 and 'actual_total' not in component
  kind='locked_talent_matches_complete_baseline_zero_count_plus_raw_metadata'
 else:
  kind='complete_json_unchanged';passed=canonical(old['full_result'])==canonical(new.get('full_result'))
 counts[kind]+=1
 pair={'group':old['group'],'request':request,'kind':kind,'passed':passed,'before_result_sha256':old.get('full_result_sha256'),'after_result_sha256':new.get('full_result_sha256'),'expected_complete_zero_count_counterfactual_sha256':golden_sha,'before_error':old.get('error'),'after_error':new.get('error')};pairs.append(pair)
 if not passed:mismatches.append(pair)
diag={'initial_draft_public_calls':0} if args.supplement else json.loads((base/'initial-zero-type-contract078-diagnostic.json').read_bytes())
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(pairs),'counts':dict(counts),'pairs':pairs,'mismatches':mismatches,'final_matrix_actual_new_public_calls':before['actual_fresh_public_calls']+after['actual_fresh_public_calls'],'reused_readonly_public_calls_without_rerun':before['reused_completed_readonly_calls_without_rerun'],'final_source_and_matrix_actual_public_calls':before['actual_fresh_public_calls']+after['actual_fresh_public_calls']+before['reused_completed_readonly_calls_without_rerun'],'initial_zero_type_contract_draft_calls_preserved':diag['initial_draft_public_calls'],'total_actual_author_public_calls_including_initial_type_contract_draft':before['actual_fresh_public_calls']+after['actual_fresh_public_calls']+before['reused_completed_readonly_calls_without_rerun']+diag['initial_draft_public_calls'],'strict_canonical_complete_zero_count_counterfactual_only_restores_three_raw_count_metadata_fields':True,'complete_eligible_outputs_zero_attack_overflow_global_sources_and_prior_errors_preserved':not mismatches,'callers_and_public_static_caches_preserved':before['callers_and_public_static_caches_preserved'] and after['callers_and_public_static_caches_preserved'],'77_patch_not_included':True}
(base/(suffix+'matrix-comparison078.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k not in ('pairs','mismatches')});print({'mismatches':mismatches[:5]});assert not mismatches
