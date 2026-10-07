from pathlib import Path
import sys,json,hashlib,datetime,collections
base=Path(__file__).parent;sys.path.insert(0,str(base/'draft064'))
from rouge.damage import calculate_damage
from rouge.catalog import catalog
before=json.loads((base/'public-results064.json').read_bytes())
def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
records=[];pairs=[];mismatches=[];counter=collections.Counter();public_before=canonical(catalog())
for row in before['records']:
 request=json.loads(canonical(row['request']));copy=json.loads(canonical(request))
 try:
  result=calculate_damage(request)
  after={'group':row['group'],'value_label':row['value_label'],'request':copy,'full_result':result,'full_result_sha256':digest(result)}
 except Exception as error:
  after={'group':row['group'],'value_label':row['value_label'],'request':copy,'error':{'type':type(error).__name__,'message':str(error)}}
 assert request==copy
 records.append(after)
 args=row['request'];active=args['operator']=='silverash' and args['skill']==3 and args.get('elite',2)==2
 selected=active and isinstance(args.get('preexisting_fragile'),str)
 if selected:
  passed=after.get('error')=={'type':'ValueError','message':'preexisting_fragile不接受字符串，请提供明确的布尔条件。'}
  counter['active_string_rejected']+=1
 else:
  passed=(row.get('full_result_sha256')==after.get('full_result_sha256') if 'full_result' in row else row['error']==after.get('error'))
  counter['complete_result_or_prior_error_unchanged']+=1
  counter['existing_prior_qualification_errors_unchanged' if 'error' in row else 'success_full_json_unchanged']+=1
 pair={'request':args,'selected_guard_applies':selected,'passed':passed,'before_result_sha256':row.get('full_result_sha256'),'after_result_sha256':after.get('full_result_sha256'),'before_error':row.get('error'),'after_error':after.get('error')}
 pairs.append(pair)
 if not passed:mismatches.append(pair)
assert canonical(catalog())==public_before
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':str(base/'draft064'),'public_calls':len(records),'records':records}
(base/'draft-results064.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
comparison={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(pairs),'public_calls':len(records)+before['public_calculation_calls'],'counts':counter,'mismatches':mismatches,'pairs':pairs,'catalog_and_caller_unchanged':True,'source_sha256':hashlib.sha256((base/'draft064/rouge/damage.py').read_bytes()).hexdigest()}
(base/'matrix-comparison064.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in comparison.items() if k not in ('pairs','mismatches')},ensure_ascii=False));assert not mismatches
