"""Check saved changed report scalar values against their actual result fields."""
import json,math
from pathlib import Path

out=Path(__file__).parent
old=json.loads((out/'public-baseline80.json').read_text())
new=json.loads((out/'public-draft80.json').read_text())
checked=0
for a,b in zip(old,new,strict=True):
    if 'result' not in a:continue
    result=b['result'];skill=result['estimate']['skill']
    for sa,sb in zip(a['result']['report']['sections'],result['report']['sections'],strict=True):
        for ma,mb in zip(sa['metrics'],sb['metrics'],strict=True):
            if ma['value']==mb['value']:continue
            section=sb['id'];key=mb['key']
            if section=='amiya_phase':
                assert key=='opening_healing';expected=result['amiya_phase_reference']['opening_healing_reference']
            elif section=='known_healing_subtotals':
                expected=result['known_healing_subtotals'][{'cast':'total_healing','window':'window_healing'}[key]]
            else:
                assert section=='healing'
                if key=='active_hps':expected=skill['phase_healing']/skill['duration_seconds']
                elif key=='window_hps':expected=skill['window_healing']/skill['window_seconds']
                else:expected=skill[{'per_cast':'total_healing','hps':'cycle_hps','window_healing':'window_healing'}[key]]
            assert type(mb['value'])==type(expected)
            assert math.isclose(mb['value'],expected,rel_tol=1e-12,abs_tol=1e-9),(b['index'],section,key)
            checked+=1
assert checked==759,checked
payload={'passed':True,'changed_report_values_checked':checked,'new_api_calls':0,
         'source':'Saved final818 pairs only; actual public result fields and existing report contracts.'}
(out/'report-bindings80.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps(payload))
