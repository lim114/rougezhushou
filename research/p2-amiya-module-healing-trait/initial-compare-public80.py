import copy,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'draft'))
from rouge.estimate import format_estimate
from rouge.reporting import format_report

out=Path(__file__).parent
baseline=json.loads((out/'public-baseline80.json').read_text())
draft=json.loads((out/'public-draft80.json').read_text())
assert len(baseline)==len(draft)==818
changed=[];same=[];errors=[];diff_paths={}
SCALE=.6/.5


def near(x,y):
    assert type(x)==type(y),(type(x),type(y),x,y)
    if x is None:assert y is None
    else:assert math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-9),(x,y)


def diff(a,b,path=()):
    assert type(a)==type(b),('type changed',path,a,b)
    if isinstance(a,dict):
        assert a.keys()==b.keys(),('keys changed',path)
        return [d for k in a for d in diff(a[k],b[k],(*path,k))]
    if isinstance(a,list):
        assert len(a)==len(b),('length changed',path)
        return [d for i in range(len(a)) for d in diff(a[i],b[i],(*path,i))]
    return [] if a==b else [(path,a,b)]


for old,new in zip(baseline,draft):
    idx=old['index'];assert new['index']==idx and old['scenario']==new['scenario']
    s=old['scenario']
    if 'error' in old:
        assert old==new;errors.append(idx);continue
    a=old['result'];b=new['result']
    is_medical=s['operator']=='char_1037_amiya3'
    qualified=(is_medical and s.get('module_id')=='uniequip_002_amiya3' and
               s.get('elite',2)>=2 and s.get('level',80)>=50)
    expected_ratio=(.6 if qualified else .5)*min(1,s.get('healing_targets',1))
    healidx=next((i for i,c in enumerate(b['components']) if c['name']=='咒愈师伤害转治疗'),None)
    if is_medical:
        assert healidx is not None
        assert b['components'][healidx]['damage_healing']['ratio']==expected_ratio
    deltas=diff(a,b)
    if not deltas:
        assert old==new;same.append(idx);continue
    assert qualified and s.get('healing_targets',1)>0,('ineligible change',idx,s)
    allowed_metric={('amiya_phase','opening_healing'),('healing','active_hps'),('healing','hps'),
                    ('healing','per_cast'),('healing','window_healing'),('healing','window_hps'),
                    ('known_healing_subtotals','cast'),('known_healing_subtotals','window')}
    for path,x,y in deltas:
        accepted=False
        if path[:2]==('components',healidx):
            tail=path[2:]
            accepted=(tail in (('per_hit',),('total',),('damage_healing','ratio')) or
                      len(tail)==2 and tail[0]=='event_amounts' or
                      len(tail)==3 and tail[0]=='known_healing_sources' and tail[2] in ('per_hit','total'))
            if accepted:near(x*SCALE,y)
        elif path==('total_healing',):
            near(x+(b['total_damage'] or 0)*.1,y);accepted=True
        elif path[:2]==('estimate','skill') and path[2] in (
                'total_healing','phase_healing','cycle_healing','cycle_hps','window_healing','window_hps'):
            key=path[2];sk=a['estimate']['skill']
            source={'total_healing':'total_damage','phase_healing':'phase_damage',
                    'cycle_healing':'cycle_damage','window_healing':'window_damage'}
            if key in source:delta=sk[source[key]]*.1
            elif key=='cycle_hps':delta=sk['cycle_damage']*.1/sk['cycle_seconds']
            else:delta=sk['window_damage']*.1/sk['window_seconds']
            near(x+delta,y);accepted=True
        elif path[0]=='known_healing_subtotals' and path[1] in ('total_healing','window_healing','window_hps'):
            near(x*SCALE,y);accepted=True
        elif path==('amiya_phase_reference','opening_healing_reference') or path==(
                'amiya_phase_reference','window_reference','opening_healing_reference'):
            near(x*SCALE,y);accepted=True
        elif len(path)==6 and path[:2]==('report','sections') and path[3]=='metrics' and path[5]=='value':
            section=b['report']['sections'][path[2]];metric=section['metrics'][path[4]]
            accepted=(section['id'],metric['key']) in allowed_metric
        assert accepted,('unexpected difference',idx,path,x,y)
        pretty='.'.join('*' if isinstance(k,int) else k for k in path)
        diff_paths[pretty]=diff_paths.get(pretty,0)+1
    for result,record in ((a,old),(b,new)):
        assert format_estimate(result)==record['estimate_text']
        assert format_report(result)==record['report_text']
        assert format_report(result,technical=True)==record['technical_report_text']
    changed.append(idx)

payload={'passed':True,'cases':818,'changed_eligible_cases':len(changed),
         'whole_unchanged_successes':len(same),'exact_old_errors':len(errors),
         'changed_case_indices':changed,'unchanged_case_indices':same,'error_case_indices':errors,
         'actual_final_matrix_public_calls':1636,'initial_environment_diagnostic_calls':1636,
         'total_author_matrix_public_calls':3272,'PYTHONHASHSEED':'0',
         'changed_numeric_scope':'Same-trait ratio and its existing dependency-derived heal scalar/report values only; all field/key/list/type contracts retained.',
         'zero_unknown_clock_or_error_drift':True,'strict_diff_paths':diff_paths,
         'report_strings_verified_from_saved_complete_results':True,
         'new_api_calls_for_recomparison':0}
(out/'matrix-comparison80.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in payload.items() if isinstance(v,(int,bool,str))},ensure_ascii=False))
