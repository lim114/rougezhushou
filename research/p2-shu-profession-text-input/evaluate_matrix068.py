from pathlib import Path
import sys,json,hashlib,datetime,collections

base=Path(__file__).parent
sys.path.insert(0,str(base/'draft068'))
from rouge.damage import calculate_damage
from rouge.catalog import catalog

before=json.loads((base/'public-results068.json').read_bytes())
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
records=[];pairs=[];mismatches=[];counter=collections.Counter()
public_before=canonical(catalog())
source=base/'draft068/rouge/operator_engine.py'
source_before=hashlib.sha256(source.read_bytes()).hexdigest()
for row in before['records']:
    request=json.loads(canonical(row['request']))
    copy=json.loads(canonical(request))
    try:
        result=calculate_damage(request)
        after={k:row[k] for k in ('group','field','value_label')}
        after.update(request=copy,full_result=result,full_result_sha256=digest(result))
    except Exception as error:
        after={k:row[k] for k in ('group','field','value_label')}
        after.update(request=copy,error={'type':type(error).__name__,'message':str(error)})
    assert request==copy
    records.append(after)
    selected_field=None
    if 'error' not in row and request['operator']=='char_2025_shu' and request.get('elite',2)==2:
        selected_field=next((f for f in ('three_professions','three_same_profession') if isinstance(request.get(f),str)),None)
    if selected_field:
        passed=after.get('error')=={'type':'ValueError','message':selected_field+' 不接受文本条件；请使用布尔值。'}
        counter['selected_talent_string_rejected']+=1
    else:
        passed=(canonical(row['full_result'])==canonical(after.get('full_result')) if 'full_result' in row else row['error']==after.get('error'))
        counter['complete_result_or_prior_error_unchanged']+=1
        counter['existing_prior_errors_unchanged' if 'error' in row else 'success_full_json_unchanged']+=1
    pair={'request':copy,'selected_string_field':selected_field,'passed':passed,
          'before_result_sha256':row.get('full_result_sha256'),'after_result_sha256':after.get('full_result_sha256'),
          'before_error':row.get('error'),'after_error':after.get('error')}
    pairs.append(pair)
    if not passed:mismatches.append(pair)
assert canonical(catalog())==public_before
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_before
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':str(base/'draft068'),'public_calls':len(records),'records':records}
(base/'draft-results068.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
comparison={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(pairs),
            'original_public_calls_reused':before['public_calls'],'draft_public_calls':len(records),
            'public_calls':len(records)+before['public_calls'],'counts':counter,'mismatches':mismatches,'pairs':pairs,
            'catalog_and_caller_unchanged':True,'source_sha256':source_before,'source_end_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(base/'matrix-comparison068.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in comparison.items() if k not in ('pairs','mismatches')},ensure_ascii=False))
assert not mismatches
