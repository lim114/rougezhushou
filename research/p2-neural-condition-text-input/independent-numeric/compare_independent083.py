"""Strict comparison of saved independent pairs; no new calculation."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
a=json.loads((OUT/'baseline-independent-public083.json').read_bytes())
b=json.loads((OUT/'draft-independent-public083.json').read_bytes())
assert a['actual_public_calls']==b['actual_public_calls']==40 and len(a['rows'])==len(b['rows'])==40
counts={'text_rejected':0,'whole_success_unchanged':0,'exact_old_errors_unchanged':0}
rows=[]
for old,new in zip(a['rows'],b['rows'],strict=True):
    assert old['case']==new['case'] and old['scenario']==new['scenario']
    assert old['caller_input_preserved'] and new['caller_input_preserved']
    expectation=old['expectation']
    if expectation=='reject':
        assert 'result'in old, (old['case'],old.get('error'))
        expected={'type':'ValueError','message':old['field']+' 不接受文本条件；请使用布尔值。'}
        assert new.get('error')==expected,(old['case'],new.get('error'))
        counts['text_rejected']+=1;status='text_rejected'
    elif expectation=='old_error':
        assert 'error'in old and new.get('error')==old['error'],(old['case'],old.get('error'),new.get('error'))
        counts['exact_old_errors_unchanged']+=1;status='exact_old_errors_unchanged'
    else:
        assert 'result'in old and 'result'in new,(old['case'],old.get('error'),new.get('error'))
        assert canonical(old['result'])==canonical(new['result']),old['case']
        for key in ['report_text','technical_report_text','estimate_text']:assert old[key]==new[key],(old['case'],key)
        counts['whole_success_unchanged']+=1;status='whole_success_unchanged'
    rows.append({'case':old['case'],'status':status,'legacy_error':old.get('error')})
report={'status':'passed','independent_pairs':40,'actual_fresh_public_calls':80,'comparison_fresh_calls':0,
    'counts':counts,'strict_whole_results_all_three_texts_and_errors':True,'rows':rows,
    'no_new_native_clock_threshold_damage_parameters':True,'tracked_mutations':False,'Qt':False,'Wine':False}
with (OUT/'independent-comparison083.json').open('x',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':'passed','pairs':40,'actual_public_calls':80,'counts':counts}))
