"""Strictly compare saved original-typed outputs, never rerun calculations."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

OUT=Path(__file__).parent
sys.path.insert(0,str(OUT/'baseline'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
a=json.loads((OUT/'public-baseline085.json').read_text())
b=json.loads((OUT/'public-draft085.json').read_text())
assert a['record_count']==b['record_count']==len(a['records'])==len(b['records'])
counts=Counter();rows=[];helper_calls=0
for old,new in zip(a['records'],b['records']):
    assert old['case']==new['case'] and canonical(old['scenario'])==canonical(new['scenario'])
    assert old['caller_input_preserved'] and new['caller_input_preserved']
    kind=old['expected'];row={'case':old['case'],'scenario':old['scenario'],'classification':kind}
    if kind=='text_rejected':
        assert old['outcome']=='accepted',old['case']
        assert new['outcome']=='error' and new['error_type']=='ValueError',old['case']
        assert new['error']=='near_previous_deployment 不接受文本条件；请使用布尔值。',old['case']
        chosen,_=selected_talents(catalog()['operators']['char_1048_orchd2'],old['scenario']);helper_calls+=1
        assert any(t.get('name')=='翔虫机动' for t in chosen),old['case']
        row.update(selected_helper_named_talent=True,old_attack=old['result']['attack'],new_error=new['error'])
    elif kind=='same_success':
        assert old['outcome']==new['outcome']=='accepted',old['case']
        assert canonical(old)==canonical(new),old['case']
        row['whole_typed_JSON_and_three_reports_identical']=True
    elif kind=='same_error':
        assert old['outcome']==new['outcome']=='error',old['case']
        assert canonical(old)==canonical(new),old['case']
        assert 'near_previous_deployment 不接受文本' not in new['error'],old['case']
        row.update(original_error_type=new['error_type'],original_error=new['error'])
    else:raise AssertionError(kind)
    counts[kind]+=1;rows.append(row)
result={'status':'passed_strict_full_saved_typed_comparison','pairs':len(rows),
    'classifications':dict(counts),'actual_matrix_calculate_damage_calls':a['public_calculate_damage_calls']+b['public_calculate_damage_calls'],
    'current_baseline_calls':a['public_calculate_damage_calls'],'draft_calls':b['public_calculate_damage_calls'],
    'historical_calls_reused_as_current_matrix':0,'new_calculate_damage_calls_during_comparison':0,
    'actual_source_helper_calls_during_comparison':helper_calls,
    'complete_results_and_format_estimate_default_technical_text_preserved':True,
    'type_comparison':'Strict canonical JSON retains bool versusint andint versusfloat/-0.0, original nested containers and all complete outputs; no whitelist subtraction.',
    'baseline_sha256':sha(OUT/'public-baseline085.json'),'draft_sha256':sha(OUT/'public-draft085.json'),
    'rows':rows}
with (OUT/'matrix-comparison085.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},ensure_ascii=False))
