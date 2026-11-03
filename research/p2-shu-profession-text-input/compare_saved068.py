from pathlib import Path
import json,collections,datetime
base=Path(__file__).parent;data=json.loads((base/'public-results068.json').read_bytes());records=data['records'];fields=('three_professions','three_same_profession')
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def outcome(r):return r.get('full_result_sha256') or canonical(r['error'])
lookup=collections.defaultdict(dict);absents={}
for row in records:
 if not any(key in row['request'] for key in fields):absents[canonical(row['request'])]=row
 request={k:v for k,v in row['request'].items() if k!=row['field']};lookup[(row['field'],canonical(request))][row['value_label']]=row
checks=[];counterexamples=[];mismatches=[];uncompared=[]
for (field,raw_request),variants in lookup.items():
 request=json.loads(raw_request);eligible=request['operator']=='char_2025_shu' and request.get('elite',2)==2
 for label,row in variants.items():
  value=row['request'].get(field)
  if 'error' in row or not eligible:
   reference=variants.get('absent') or variants.get('bool_false') or absents.get(raw_request)
   if not reference:uncompared.append({'request':row['request'],'kind':'inactive_or_original_error'});continue
   same=outcome(row)==outcome(reference);checks.append({'request':row['request'],'kind':'inactive_or_original_error','same_full_result_or_error':same})
   if not same:mismatches.append(checks[-1])
  elif label in ('null','int_zero','int_one','float_zero','float_one','negative_zero'):
   reference=variants.get('bool_true' if bool(value) else 'bool_false');assert reference
   same=outcome(row)==outcome(reference);checks.append({'request':row['request'],'kind':'numeric_null_compatibility','same_full_result':same})
   if not same:mismatches.append(checks[-1])
  elif label in ('false_text','upper_false_text','zero_text'):
   reference=variants.get('bool_true');off=variants.get('bool_false');assert reference and off
   same=outcome(row)==outcome(reference);stats=row['full_result']['estimate']['base_stats'];offstats=off['full_result']['estimate']['base_stats']
   counterexamples.append({'request':row['request'],'text_equals_true_full_json':same,'differs_from_false_full_json':outcome(row)!=outcome(off),'field':field,
      'current_hp':stats['hp'],'false_hp':offstats['hp'],'current_attack_speed_reference':stats['attack_speed_reference'],'false_attack_speed_reference':offstats['attack_speed_reference']})
   if not same:mismatches.append(counterexamples[-1])
summary={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_commit':data['frozen_commit'],'public_calls':data['public_calls'],'groups':data['groups'],
 'success_calls':sum('full_result'in r for r in records),'error_counts':dict(collections.Counter(r['error']['message'] for r in records if 'error'in r)),
 'checks':checks,'counterexamples':counterexamples,'mismatches':mismatches,'uncompared_inactive_or_compatibility':uncompared,
 'shared_absent_rows_compare_both_field_lookups':True,'comparison_uses_saved_full_outcomes_not_new_public_calls':True,
 'read_only_no_patch':True,'caller_and_cached_catalog_preserved_in_original_probe':True}
(base/'public-comparison068-final.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_calls':data['public_calls'],'success_calls':summary['success_calls'],'error_counts':summary['error_counts'],'full_control_or_error_checks':len(checks),'checks_by_kind':collections.Counter(x['kind'] for x in checks),'counterexamples':len(counterexamples),'mismatches':len(mismatches),'uncompared':len(uncompared)},ensure_ascii=False));assert not mismatches and not uncompared
