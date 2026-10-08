"""Strict saved-only44 review, no imports/calls of product or formatters."""
import ast,gzip,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;AUTHOR=OUT.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def bind(p):
 b=p.read_bytes();return {'source_path':str(p),'bytes':len(b),'sha256':sha(b)}
def write(name,obj):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def native(v):
 if isinstance(v,dict):return ('dict',tuple((native(k),native(x)) for k,x in v.items()))
 if isinstance(v,(tuple,list)):return (type(v).__name__,tuple(native(x) for x in v))
 if isinstance(v,float):return ('float',v.hex())
 return (type(v).__name__,v)
def decode(t):
 kind=t['type']
 if kind=='dict':
  pairs=[(decode(k),decode(v)) for k,v in t['items']];result=dict(pairs);assert len(result)==len(pairs);return result
 if kind in ('tuple','list'):
  values=[decode(v) for v in t['items']];return tuple(values) if kind=='tuple' else values
 assert kind in ('str','int','float','bool','NoneType')
 value=t['value'];assert type(value).__name__==kind
 return value
def main():
 full=AUTHOR/'api-ui090-section086.json.gz';raw_gz=full.read_bytes()
 assert sha(raw_gz)=='3b8dcf9afa046360e1fdbb7f7e004ee968dc7fe8b4fb15ee7b9dd1e6b1761db8'
 raw=gzip.decompress(raw_gz);r=json.loads(raw)
 assert gzip.decompress(gzip.compress(raw,mtime=0))==raw
 summary=json.loads((AUTHOR/'api-ui090-section086-summary.json').read_bytes())
 proof=json.loads((AUTHOR/'root086-ui090-source-proof.json').read_bytes())
 cases=json.loads((AUTHOR/'cases090-section086.json').read_bytes())['rows']
 assert r['root_source_commit']==proof['root_commit']=='0f27027e7e1f49c08f298706b599e310e299238b'
 assert r['source_hashes']==proof['public_source_sha256'] and len(r['source_hashes'])==125
 assert r['source_hashes']['rouge/operator_engine.py']=='c6a7b5e5cd444480f3579a8174246a31f891cb7a2b1c93bbf0826aa4a7765c68'
 assert r['source_hashes']['rouge/damage.py']=='6cc15cf93eb52fc42120fff6b795e2cbbf2903cf0af8d7d293ffea9f73f121c6'
 for k,v in summary.items():
  if k in r:assert native(v)==native(r[k]),k
 assert len(r['records'])==r['UI_state_design_records']==r['actual_API_calls']==r['successful_results']==44
 assert r['pair_groups']==22 and r['unique_requested_calculation_inputs']==31 and r['expected_error_rows']==0
 assert r['formatter_text_requests']==132 and r['actual_formatter_function_entries']==176
 assert r['formatter_entry_counts']=={'format_estimate':44,'format_report_default':88,'format_report_technical':44}
 assert r['catalog_helper_entries_internally_observed']['API']==221 and r['external_product_helper_calls']==0
 assert r['source_drift']==[] and r['old_source36_or4217_API_cases_repeated']==0
 adapter=(AUTHOR/'preflight_ui090_section086.py').read_text();ast.parse(adapter)
 assert 'assert canonical(catalog_ref) == catalog_baseline' in adapter
 anchors={};pairs=[];traces=0
 assert len(cases)==44
 for row,case in zip(r['records'],cases):
  assert native(row['case'])==native(case)
  before=decode(row['input_typed_before']);after=decode(row['input_typed_after']);result=decode(row['result_typed'])
  assert native(before)==native(after)==native(row['input'])==native(case['input'])
  assert native(result)==native(row['result'])
  assert all(type(row['reports'][name]) is str for name in ('estimate','default','technical'))
  assert row['reports']['estimate']==row['reports']['default']
  assert row['all_three_texts_preserve_result_typed_and_JSON'] is True and row['cached_catalog_canonical_JSON_unchanged'] is True
  assert all(key in result for key in ('components','timing','estimate','report'))
  assert type(case['widget_checked']) is bool and type(before['continuous_attacks']) is bool and before['continuous_attacks'] is True
  if case['kind']=='hidden':assert case['field'] not in before
  else:assert type(before[case['field']]) is bool and before[case['field']] is case['widget_checked']
  for trace in row['internal_same_call_trace']:
   traces+=1;assert trace['operator']=='char_4182_oblvns'
   assert (trace['normal_plan_calls_observed']>0) is trace['normal_local_is_not_None']
   assert trace['actual_object_ranged_attack_condition_consumed'] is (not trace['ranged_overridden_local'] or trace['normal_local_is_not_None'])
  if not case['widget_checked']:anchors[case['pair_id']]=row;continue
  anchor=anchors[case['pair_id']];same=native(result)==native(decode(anchor['result_typed']))
  if case['kind']=='hidden' or case['pair_id']=='qualification:mizuki-E1':
   assert same and native(row['reports'])==native(anchor['reports'])
  else:assert not same
  if case['kind']=='hidden':assert native(before)==native(decode(anchor['input_typed_before']))
  if case['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal':
   assert native(result['components'])==native(anchor['result']['components'])
   assert native(result['estimate']['skill']['skill_attack'])==native(anchor['result']['estimate']['skill']['skill_attack'])
   for member in (anchor,row):
    assert len(member['internal_same_call_trace'])==1
    trace=member['internal_same_call_trace'][0]
    assert trace['selected_note_max_cnt']==12 and trace['normal_plan_calls_observed']==1
    assert trace['normal_local_is_not_None'] and trace['ranged_overridden_local'] and trace['actual_object_ranged_attack_condition_consumed']
  pairs.append({'pair_id':case['pair_id'],'kind':case['kind'],'whole_native_same':same,'three_texts_same':native(row['reports'])==native(anchor['reports'])})
 assert len(anchors)==len(pairs)==22 and traces==12
 assert sum(p['whole_native_same'] for p in pairs)==9
 receipt=write('saved44-review-receipt.json',{'status':'FINAL_PASS_SAVED_ONLY_STRICT44','base_commit':r['root_source_commit'],
  'bound_author_artifacts':[bind(AUTHOR/n) for n in ('api-ui090-section086.json.gz','api-ui090-section086-summary.json','root086-ui090-source-proof.json','cases090-section086.json','cases090_section086.py','preflight_ui090_section086.py')],
  'decoded_gzip':{'bytes':len(raw),'sha256':sha(raw),'lossless_compression_verified':True},
  'records_strict_native_decode_to_wholepublic':44,'input_before_after_wholecaller_bound':44,'three_texts_saved_nonempty_typechecked':44,
  'same_native_pairs':9,'different_native_pairs':13,'pairs':pairs,'actual_same_call_oblvns_trace_records':12,
  'coveredmodule_two_observednormal_plans':2,'hidden_key_omission_pairs':8,
  'author_execution_ledger':{'API_calls':44,'unique_inputs':31,'success':44,'errors':0,'text_requests':132,'actual_formatter_entries':176,
   'formatter_entry_counts':r['formatter_entry_counts'],'catalog_API_internal_entries':221,'external_helper_calls':0},
  'catalog_scope':'Saved per-call canonical-cache assertion flags and bound adapter assertion checked; no separate past cache object recreated/replayed by reviewer.',
  'float_scope':'Saved value-based float typed nodes decoded to actualfloat and compared byhex, with bool/int/list/tuple/order preserved; no±0 orFalse/0 equality collapse.',
  'new_API_calls':0,'new_formatter_calls':0,'new_project_helper_calls':0,'Qt':0,'Wine':0,'tests':0,'tracked_edits':0,
  'actual_Qt_UI090_full87_90':False,'old_static7_modified':False,'original35_snapshot38_modified':False})
 checkpoint=OUT/'CHECKPOINT.md'
 with checkpoint.open('x',encoding='utf-8') as f:f.write('Saved-only44正式通过。44完整native/result/输入前后绑定，float按hex比较。22组：hidden8+MizuE1共9组whole同，active12+module1共13组whole异；moduleS3两flags各同次normal1/max12/markerTrue，windowcomponents与skillattack同。作者实测44API/31unique、132requests/176formatterentries、catalog内部API221；本复核0API/helper/formatter/Qt/Wine/tests。原静态7与历史35/snapshot38不改，真实UI090与87–90仍pending。\n')
 handoff=write('handoff-final.json',{'status':'FINAL_PASS_SAVED_ONLY_STRICT44','receipt':bind(receipt),'new_API_calls':0,'runtime_UI090_pending':True,'stop_changes':True})
 files=[{**bind(p),'archive_path':p.name} for p in (Path(__file__),receipt,checkpoint,handoff)]
 manifest=write('manifest.json',{'version':1,'status':'FINAL_SEALED','files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files)})
 for row in files:assert bind(Path(row['source_path']))=={k:row[k] for k in ('source_path','bytes','sha256')}
 print(json.dumps({'status':'FINAL_PASS_SAVED_ONLY_STRICT44','manifest':bind(manifest),'handoff':bind(handoff),'files':len(files),'bytes':sum(x['bytes'] for x in files),'new_API_calls':0}))
if __name__=='__main__':main()
