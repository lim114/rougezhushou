import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
before=json.loads((ROOT/'matrix-baseline-results.json').read_text())
after=json.loads((ROOT/'matrix-draft-results.json').read_text())
assert len(before['items'])==len(after['items'])==before['case_count']==after['case_count']
def typed_equal(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(typed_equal(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(typed_equal(x,y) for x,y in zip(a,b))
    return a==b
counts={'unchanged_accepted_whole_typed_and_3texts':0,'exact_old_errors':0,'new_back_successes':0}
for a,b in zip(before['items'],after['items']):
    assert a['label']==b['label'] and typed_equal(a['scenario'],b['scenario'])
    if a['expect']=='new_back_success':
        assert a['accepted'] is False and b['accepted'] is True,(a['label'],a,b)
        assert a['error_type']=='ValueError' and a['error']=='原版动画参考与当前干员/技能不符，或该动作不适合常规逐击参考。'
        r=b['result'];assert r['timing']['complete'] is False
        assert all(s['exact_binding'] is False for s in r['timing']['streams'])
        if a['scenario']['skill']==1:
            assert r['total_healing'] is None
            assert r['estimate']['skill']['cycle_healing'] is None
        counts['new_back_successes']+=1
    elif a['accepted']:
        assert b['accepted'] and typed_equal(a['result'],b['result']) and typed_equal(a['texts'],b['texts']),a['label']
        counts['unchanged_accepted_whole_typed_and_3texts']+=1
    else:
        assert b['accepted'] is False and typed_equal((a['error_type'],a['error']),(b['error_type'],b['error'])),a['label']
        counts['exact_old_errors']+=1
receipt={'version':1,'passed':True,'unique_pairs':len(before['items']),'counts':counts,
    'fresh_API_calls':before['fresh_API_calls']+after['fresh_API_calls'],'initial_API_results_reused':after['reused_initial_API_results'],
    'formatter_calls':before['formatter_calls']+after['formatter_calls'],'comparator_API_calls':0,'source_parser_or_download_calls':0,
    'new_success_scope':'Explicit Back Attack is a selectable offline reference; no completion, native binding or friendly acquisition clock was inferred'}
(ROOT/'matrix-comparison-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
