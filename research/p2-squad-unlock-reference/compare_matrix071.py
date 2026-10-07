from pathlib import Path
import json,hashlib,collections,datetime
base=Path(__file__).parent
before=json.loads((base/'baseline-results071.json').read_bytes());after=json.loads((base/'draft-results071.json').read_bytes())
source=json.loads((base/'source-receipt071.json').read_bytes())
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
conditions={row['id']:row['raw_item_complete']['unlockCondDesc'] for row in source['strengthened_squads_complete_original_records']}
counts=collections.Counter();pairs=[];mismatches=[]
assert before['public_calls']==after['public_calls']==len(before['records'])==len(after['records'])
for old,new in zip(before['records'],after['records']):
    assert old['request']==new['request']
    for row in (old,new):
        if 'full_result' in row:assert digest(row['full_result'])==row['full_result_sha256']
    request=old['request'];squad=((request.get('run_config') or {}).get('squad') or {}).get('id')
    if 'error' in old:
        passed=old['error']==new.get('error');kind='prior_complete_errors_unchanged';counts[kind]+=1
    elif squad in conditions:
        trimmed=json.loads(canonical(new.get('full_result')))
        reference=trimmed['run_resolution'].pop('squad_unlock_reference',None)
        sections=trimmed['report']['sections'];new_sections=[section for section in sections if section['id']=='squad_unlock_reference']
        trimmed['report']['sections']=[section for section in sections if section['id']!='squad_unlock_reference']
        expected_reference=reference is not None and reference['squad_id']==squad and reference['unlock_condition_reference']==conditions[squad]
        expected_reference=expected_reference and reference['account_unlocked'] is None and reference['actual_activation'] is None and reference['reference_only'] is True
        passed=expected_reference and len(new_sections)==1 and trimmed==old['full_result']
        kind='only_new_strengthened_condition_reference_and_section';counts[kind]+=1
    else:
        passed=old['full_result']==new.get('full_result');kind='inactive_or_base_full_json_unchanged';counts[kind]+=1
    pair={'request':request,'kind':kind,'passed':passed,'before_result_sha256':old.get('full_result_sha256'),
          'after_result_sha256':new.get('full_result_sha256'),'before_error':old.get('error'),'after_error':new.get('error')}
    pairs.append(pair)
    if not passed:mismatches.append(pair)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(pairs),
     'public_calls':before['public_calls']+after['public_calls'],'counts':counts,'pairs':pairs,'mismatches':mismatches,
     'full_json_comparison_only_removes_exact_two_added_reference_locations':True,
     'all_existing_math_training_flags_source_resolutions_unknowns_and_errors_unchanged':not mismatches,
     'caller_and_cached_catalog_run_config_technology_preserved':before['caller_and_catalog_run_config_technology_cache_preserved'] and after['caller_and_catalog_run_config_technology_cache_preserved']}
(base/'matrix-comparison071.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k not in ('pairs','mismatches')});assert not mismatches
