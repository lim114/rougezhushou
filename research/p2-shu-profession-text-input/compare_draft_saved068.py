"""Compare all already saved JSON outcomes without repeating either API matrix."""
from pathlib import Path
import json,hashlib,datetime,collections

base=Path(__file__).parent
before=json.loads((base/'public-results068.json').read_bytes())
after=json.loads((base/'draft-results068.json').read_bytes())
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
pairs=[];mismatches=[];counts=collections.Counter()
assert before['public_calls']==after['public_calls']==len(before['records'])==len(after['records'])
for old,new in zip(before['records'],after['records']):
    assert old['request']==new['request']
    for row in (old,new):
        if 'full_result' in row:assert row['full_result_sha256']==digest(row['full_result'])
    request=old['request'];selected_field=None
    if 'error' not in old and request['operator']=='char_2025_shu' and request.get('elite',2)==2:
        selected_field=next((f for f in ('three_professions','three_same_profession') if isinstance(request.get(f),str)),None)
    if selected_field:
        passed=new.get('error')=={'type':'ValueError','message':selected_field+' 不接受文本条件；请使用布尔值。'}
        counts['selected_talent_string_rejected']+=1
    else:
        passed=(old['full_result']==new.get('full_result') if 'full_result' in old else old['error']==new.get('error'))
        counts['complete_result_or_prior_error_unchanged']+=1
        counts['existing_prior_errors_unchanged' if 'error' in old else 'success_full_json_unchanged']+=1
    pair={'request':request,'selected_string_field':selected_field,'passed':passed,
          'before_result_sha256':old.get('full_result_sha256'),'after_result_sha256':new.get('full_result_sha256'),
          'before_error':old.get('error'),'after_error':new.get('error')}
    pairs.append(pair)
    if not passed:mismatches.append(pair)
initial=json.loads((base/'matrix-comparison068-initial-native-json-key-error.json').read_bytes())
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(pairs),
     'original_public_calls_reused':before['public_calls'],'draft_public_calls':after['public_calls'],
     'public_calls':before['public_calls']+after['public_calls'],'counts':counts,'pairs':pairs,'mismatches':mismatches,
     'comparison_of_saved_full_json_no_new_public_calls':True,
     'initial_comparator_native_vs_serialized_object_mismatches':len(initial['mismatches']),
     'all_initial_mismatch_saved_json_identical':all(p['before_result_sha256']==p['after_result_sha256'] for p in initial['mismatches']),
     'catalog_and_caller_unchanged':initial['catalog_and_caller_unchanged'],
     'source_sha256':initial['source_sha256'],'source_end_sha256':initial['source_end_sha256']}
assert out['source_sha256']==hashlib.sha256((base/'draft068/rouge/operator_engine.py').read_bytes()).hexdigest()
(base/'matrix-comparison068.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('pairs','mismatches')},ensure_ascii=False))
assert not mismatches
