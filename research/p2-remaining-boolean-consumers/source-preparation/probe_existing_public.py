"""At most 36 first public calls on immutable section-82 git bytes."""
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = 'b5a40f30683bfc0945decaabbd4db5914c28427f'


def typed(value):
    if isinstance(value,dict):
        return {'type':'dict','items':[[typed(k),typed(v)] for k,v in value.items()]}
    if isinstance(value,(list,tuple)):
        return {'type':type(value).__name__,'items':[typed(v) for v in value]}
    return {'type':type(value).__name__,'value':value}


def dump(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')


def difference_paths(a,b,path='$'):
    if type(a) is not type(b):return [path+':type']
    if isinstance(a,dict):
        rows=[]
        for key in a.keys()|b.keys():
            if key not in a or key not in b:rows.append(path+'.'+str(key)+':presence')
            else:rows.extend(difference_paths(a[key],b[key],path+'.'+str(key)))
        return rows
    if isinstance(a,(list,tuple)):
        rows=[]
        if len(a)!=len(b):rows.append(path+':length')
        for i,(x,y) in enumerate(zip(a,b)):rows.extend(difference_paths(x,y,f'{path}[{i}]'))
        return rows
    return [] if a==b else [path]


def main():
    source=json.loads((OUT/'source-preparation-complete.json').read_bytes())
    assert source['passed'] is True and source['public_calls']==0 and source['base_commit']==BASE
    freeze=json.loads((OUT/'baseline-git-object-freeze.json').read_bytes())
    assert freeze['base_commit']==BASE
    for row in freeze['files']:
        data=(OUT/'baseline'/row['path']).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    sys.path.insert(0,str(OUT/'baseline'))
    from rouge.catalog import catalog
    from rouge.damage import calculate_damage
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    plan=json.loads((OUT/'source-first-public-probe-plan.json').read_bytes())
    assert plan['base_commit']==BASE and plan['maximum_calls']==36 and len(plan['scenarios'])==36
    catalog_before=typed(catalog())
    rows=[];start=time.monotonic()
    with (OUT/'first-public-probes.jsonl').open('x',encoding='utf-8') as stream:
        for index,original in enumerate(plan['scenarios'],1):
            scenario=copy.deepcopy(original);before=typed(scenario)
            row={'index':index,'input':copy.deepcopy(scenario),'input_typed_before':before}
            try:
                result=calculate_damage(scenario)
                row.update({'outcome':'accepted','result_typed':typed(result),'result':result,
                            'reports':{'estimate':format_estimate(result),'user':format_report(result),
                                       'technical':format_report(result,technical=True)}})
            except Exception as error:
                row.update({'outcome':'error','error_type':type(error).__name__,'error_message':str(error)})
            row['input_typed_after']=typed(scenario)
            row['input_unchanged']=row['input_typed_after']==before
            row['catalog_unchanged']=typed(catalog())==catalog_before
            assert row['input_unchanged'] and row['catalog_unchanged'],index
            stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');stream.flush()
            rows.append(row)
            print(json.dumps({'index':index,'owner':original['operator'],'field':next(k for k in original if k not in ('operator','skill','skill_rank','elite','base_attack','timing_mode')),'outcome':row['outcome']},ensure_ascii=False),flush=True)
    groups=[]
    for i in range(0,len(rows),3):
        false,true,text=rows[i:i+3]
        assert all(r['outcome']=='accepted' for r in (false,true,text))
        field=next(k for k in false['input'] if k not in ('operator','skill','skill_rank','elite','base_attack','timing_mode'))
        groups.append({'operator':false['input']['operator'],'field':field,'skill':false['input']['skill'],
                       'bool_values_differ':false['result_typed']!=true['result_typed'],
                       'text_false_exactly_equals_true':text['result_typed']==true['result_typed'],
                       'text_false_reports_exactly_equal_true':text['reports']==true['reports'],
                       'false_true_result_difference_paths':sorted(difference_paths(false['result'],true['result']))})
    summary={'passed':True,'base_commit':BASE,'new_public_calls':len(rows),'accepted':sum(r['outcome']=='accepted' for r in rows),
             'errors':sum(r['outcome']=='error' for r in rows),'elapsed_seconds':time.monotonic()-start,
             'all_input_and_catalog_unchanged':True,'typed_tree_captured_before_json_encoding':True,
             'reports_per_accepted_result':3,'groups':groups,'tests_run':0,'gui_calls':0,'wine_calls':0,
             'matrix_or_draft':False,'mechanical_change':False,
             'native_clocks_probabilities_attachment_or_unknown_rule_verified':False}
    dump(OUT/'first-public-probe-summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('passed','new_public_calls','accepted','errors','elapsed_seconds')},ensure_ascii=False))


if __name__=='__main__':main()
