import hashlib
import json
from pathlib import Path

OUT=Path(__file__).parent
old=json.loads((OUT/'baseline-public84.json').read_bytes())
new=json.loads((OUT/'draft-public84.json').read_bytes())
assert len(old)==len(new)
allowed='haruka_repeat 不接受文本条件；请使用布尔值。'
groups={'whole_success_same':[],'old_errors_exact':[],'active_text_rejected':[]}
for index,(a,b) in enumerate(zip(old,new,strict=True)):
    assert a['scenario']==b['scenario'] and a['label']==b['label']
    if 'error' in a:
        assert a==b,(index,'old error changed')
        groups['old_errors_exact'].append(index)
    elif 'error' in b:
        assert b['error']=={'type':'ValueError','message':allowed},(index,'unexpected error')
        assert a['scenario']['operator']=='char_4202_haruka'
        assert isinstance(a['scenario'].get('haruka_repeat'),str)
        assert a['scenario']['skill']==2
        assert a['scenario']['elite']>=1
        assert set(b)=={'label','scenario','error'}
        groups['active_text_rejected'].append(index)
    else:
        assert a['typed_result']==b['typed_result'],(index,'native typed result changed')
        assert a==b,(index,'whole result or reports/source selection changed')
        groups['whole_success_same'].append(index)
assert all(groups.values())
receipt={'passed':True,'pairs':len(old),'actual_author_matrix_calls':2*len(old),
         'counts':{k:len(v) for k,v in groups.items()},'case_indices':groups,
         'only_allowed_change':{'operator':'char_4202_haruka','skill':2,'actual_consumer':'nonnormal S2 independent of E2 flower talent',
                                'raw_value_type':'str','new_error':allowed},
         'comparison':'Exact native type tree before JSON serialization, complete public output, all three actual report texts, actual source selection and unchanged exact old errors. No numeric/text/unknown normalization.',
         'raw_sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest()
                       for name in ('baseline-public84.json','draft-public84.json')},
         'new_calculate_calls_during_comparison':0}
(OUT/'public-comparison84.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='case_indices'},ensure_ascii=False))
