"""Full typed JSON and three report records from ordinary public calls."""
import hashlib
import json
from pathlib import Path
import sys
from copy import deepcopy

OUT=Path(__file__).parent
OP='char_1048_orchd2';MOD='uniequip_002_orchd2';FIELD='near_previous_deployment'
def base(skill=1,mode='frames',**extra):
    return {'operator':OP,'skill':skill,'skill_rank':10,'elite':2,'level':90,
            'base_attack':1000,'timing_mode':mode,'window_seconds':10,**extra}
def cases():
    rows=[]
    def add(name,args,expected):rows.append({'case':name,'scenario':args,'expected':expected})
    cohort=[]
    for mode in ('frames','continuous'):
        for skill in (1,2):cohort.append(base(skill,mode,elite=1,level=1,skill_rank=7))
        for skill in (1,2,3):cohort.append(base(skill,mode,level=1))
    for stage in (1,2,3):
        for skill in (1,2,3):cohort.append(base(skill,level=60,module_id=MOD,module_level=stage))
    for skill in (1,2,3):cohort.append(base(skill,'continuous',level=59,module_id=MOD,module_level=3))
    for skill,mode in ((1,'frames'),(2,'continuous'),(3,'frames')):
        cohort.append(base(skill,mode,skill_rank=1))
    for n,args in enumerate(cohort):
        for j,text in enumerate(('false','',' 未知 ')):
            add(f'active-{n}-{j}',{**args,FIELD:text},'text_rejected')
    for n,args in enumerate((base(1,'frames',elite=1,level=1,skill_rank=1),
                             base(2,'continuous'),base(3,'frames',level=60,module_id=MOD,module_level=2),
                             base(2,'continuous',level=60,module_id=MOD,module_level=3))):
        add(f'nontext-{n}-missing',args,'same_success')
        for j,value in enumerate((False,True,None,0,0.0,-0.0,1,1.0,-1,[],{},[False],{'enabled':False})):
            add(f'nontext-{n}-{j}',{**args,FIELD:value},'same_success')
    for n,(mode,level,rank,stage) in enumerate((('frames',1,1,0),('continuous',50,7,0),
                                               ('frames',1,7,3),('continuous',50,1,3))):
        args=base(1,mode,elite=0,level=level,skill_rank=rank)
        if stage:args.update(module_id=MOD,module_level=stage)
        for j,text in enumerate(('false','',' 未知 ')):
            add(f'inactive-e0-{n}-{j}',{**args,FIELD:text},'same_success')
    for n,(owner,skill) in enumerate((('char_133_mm',2),('char_2025_shu',3),('char_1041_angel2',2),
                                      ('char_298_susuro',2),('char_206_gnosis',3),('char_4202_haruka',3))):
        add(f'inactive-owner-{n}',{'operator':owner,'skill':skill,'window_seconds':10,FIELD:'false'},'same_success')
    bad=({'elite':0,'skill':2,'skill_rank':1},{'elite':1,'skill_rank':10},
         {'skill':0},{'skill_rank':True},{'module_id':MOD,'module_level':0},
         {'level':91},{'enemy_defense':-1},{'enemy_resistance':101},
         {'timing':{'target_windows':[[10,0]]}}, {'effects':[{'kind':'unsupported','value':1}]},
         {'target_enemy':{'stage_id':'missing','enemy_id':'missing','level':0}}, {'window_seconds':-1})
    for n,options in enumerate(bad):
        for j,near in enumerate((False,'false')):
            add(f'olderror-{n}-{j}',base(**{**options,FIELD:near}),'same_error')
    for skill in (1,2,3):
        for mode in ('frames','continuous'):
            for n,options in enumerate(({'window_seconds':0},{'base_attack':0},
                                       {'timing':{'target_disappears_seconds':0}})):
                add(f'zero-{skill}-{mode}-{n}',base(skill,mode,**{**options,FIELD:'false'}),'text_rejected')
    for skill in (1,2,3):
        add(f'double-old-domain-{skill}',base(skill,**{FIELD:False,'double_charge':'false'}),'same_success')
    # Existing direct redeploy rune. No guessed event clock or new composition.
    for value in (False,True,'false'):
        add('existing-rune-'+str(value),base(3,**{FIELD:value,'relic_ids':['rogue_6_relic_artifact_6']}),
            'text_rejected' if isinstance(value,str) else 'same_success')
    return rows

def run(package, destination):
    sys.path.insert(0,str(Path(package)))
    from rouge.catalog import catalog
    from rouge.damage import calculate_damage
    from rouge.estimate import format_estimate
    from rouge.reporting import format_report
    catalog_before=deepcopy(catalog())
    data=[];count=0
    for case in cases():
        args=deepcopy(case['scenario']);before=deepcopy(args);count+=1
        row=deepcopy(case)
        try:
            result=calculate_damage(args)
            row.update(outcome='accepted',result=result,estimate_text=format_estimate(result),
                       report_text=format_report(result),technical_report_text=format_report(result,technical=True))
        except Exception as exc:
            row.update(outcome='error',error_type=type(exc).__name__,error=str(exc))
        row['caller_input_preserved']=args==before
        assert row['caller_input_preserved'],case['case']
        data.append(row)
    assert catalog()==catalog_before
    output={'package':str(Path(package).resolve()),'public_calculate_damage_calls':count,
            'record_count':len(data),'catalog_preserved':True,'records':data}
    path=Path(destination)
    with path.open('x',encoding='utf-8') as stream:json.dump(output,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'written':str(path),'count':len(data),'public_calls':count,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))

if __name__=='__main__':run(sys.argv[1],sys.argv[2])
