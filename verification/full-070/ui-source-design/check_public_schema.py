"""API-only planned UI contracts; never actual Qt or Wine proof."""
import gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;PACKAGE=P/'public-schema-70'
sys.path.insert(0,str(PACKAGE));sys.dont_write_bytecode=True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report
from public_contracts import require_wisdel,require_incoming,require_professions,require_cooperative,require_sown
def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in('.py','.json')}
before=hashes();rows=[];counts=Counter();expected_errors=Counter()
def scenario(op,skill,mode,rank=10,**extra):
    args={'operator':op,'skill':skill,'skill_rank':rank,'elite':2,
          'level':catalog()['operators'][op]['phases'][2]['max_level'],
          'potential':1,'trust':100,'module_id':None,'module_level':0,
          'window_seconds':10,'timing_mode':mode,'enemy_defense':0,'enemy_resistance':0,
          'preexisting_fragile':False,'cooperative':False,'healing_targets':1,'relic_ids':[]}
    args.update({key:default for key,label,default,maximum,skills in OPTIONS.get(op,[])if skill in skills})
    args.update(extra);return args
def call(section,args,error=None):
    original=json.dumps(args,sort_keys=True,allow_nan=False)
    if error:
        try:calculate_damage(args)
        except ValueError as caught:assert str(caught)==error
        else:raise AssertionError('Expected public input error was absent')
        row={'section':section,'input':args,'status':'expected_error','exception':{'type':'ValueError','message':error}}
        expected_errors[section]+=1;result=text=None
    else:
        result=calculate_damage(args);text=format_report(result)
        row={'section':section,'input':args,'status':'returned','result':result,'human_report':text}
    assert json.dumps(args,sort_keys=True,allow_nan=False)==original
    rows.append(row);counts[section]+=1;return result,text
scopes=[('positive',10,{}),('zero_window',0,{}),('zero_lifetime',10,{'target_disappears_seconds':0}),('empty_target_windows',10,{'target_windows':[]})]
ghost_inputs=[(0,0),(0,1),(1,0),(1,1),(3,2)]
for skill in (1,2,3):
    for mode in ('frames','continuous'):
        for scope,horizon,timing in scopes:
            for ghosts,casts in ghost_inputs:
                args=scenario('char_1035_wisdel',skill,mode,window_seconds=horizon,timing=timing,ghost_count=ghosts,ghost_casts=casts)
                error='零长度观察窗口不能声明魂灵施放命中。'if horizon==0 and ghosts>0 and casts>0 else None
                result,text=call(66,args,error)
                if not error:require_wisdel(result,args,text,scope)
for skill in (1,2,3):
    for mode in ('frames','continuous'):
        for scope,horizon,timing in scopes:
            for count in (0,1):
                args=scenario('char_1042_phatm2',skill,mode,level=60,window_seconds=horizon,timing=timing,enemy_attack_count=count)
                result,text=call(67,args);require_incoming(result,args,text,scope)
        args=scenario('char_1042_phatm2',skill,mode,level=60,enemy_attack_count=20)
        result,text=call(67,args);require_incoming(result,args,text,'positive')
        for count in (0,1):
            args=scenario('char_1042_phatm2',skill,mode,level=60,enemy_attack_count=count,enemy_buildup_resistance=100)
            result,text=call(67,args);require_incoming(result,args,text,'positive',immune=True)
for skill in (1,2):
    for mode in ('frames','continuous'):
        for count in (0,1):
            args=scenario('char_1042_phatm2',skill,mode,7,elite=1,level=80,enemy_attack_count=count)
            result,text=call(67,args);require_incoming(result,args,text,'positive',qualified=False)
prof_flags=[(False,False),(True,False),(False,True),(True,True)]
for elite,level,rank,skills,fours in ((2,90,10,(1,2,3),(False,True)),(1,80,7,(1,2),(False,)),(0,50,4,(1,),(False,))):
    for skill in skills:
        for mode in ('frames','continuous'):
            for four in fours:
                plain=None
                for different,same in prof_flags:
                    args=scenario('char_2025_shu',skill,mode,rank,elite=elite,level=level,three_professions=different,three_same_profession=same,four_sui=four)
                    result,text=call(68,args)
                    if not different and not same:plain=result
                    require_professions(result,args,text,plain,elite==2)
for mode in ('frames','continuous'):
    for scope,horizon,timing in scopes:
        controls={}
        for coop in (False,True):
            for fragile in (False,True):
                args=scenario('silverash',3,mode,4,window_seconds=horizon,timing=timing,cooperative=coop,preexisting_fragile=fragile)
                result,text=call(69,args)
                if not coop:controls[fragile]=result
                require_cooperative(result,args,text,controls[fragile],scope)
for mode in ('frames','continuous'):
    plain=None
    for coop in (False,True):
        args=scenario('silverash',1,mode,1,elite=0,level=50,cooperative=coop)
        result,text=call(69,args)
        if not coop:plain=result
        else:assert json.dumps(result,sort_keys=True)==json.dumps(plain,sort_keys=True)
for rank in (1,7,10):
    bb=catalog()['operators']['char_2025_shu']['skills'][2]['levels'][rank-1]['values']
    for mode in ('frames','continuous'):
        for four in (False,True):
            for scope,horizon,timing in scopes[:3]:
                plain=None
                for tile in (False,True):
                    args=scenario('char_2025_shu',3,mode,rank,four_sui=four,enemy_on_sown_tile=tile,window_seconds=horizon,timing=timing)
                    result,text=call(70,args)
                    if not tile:plain=result
                    require_sown(result,args,text,plain,scope,bb)
for skill in (1,2):
    for mode in ('frames','continuous'):
        plain=None
        for checkbox_state in (False,True):
            args=scenario('char_2025_shu',skill,mode,7,elite=1,level=80)
            assert 'enemy_on_sown_tile'not in args
            result,text=call(70,args)
            if not checkbox_state:plain=result
            else:assert json.dumps(result,sort_keys=True)==json.dumps(plain,sort_keys=True)
assert dict(counts)=={66:120,67:74,68:72,69:36,70:80},dict(counts)
assert hashes()==before
receipt={'scope':'Public API-only planned GUI contract verification; expected negative API calls are not successful calculations',
         'gui_executed':False,'wine_executed':False,'source_drift':[],'source_hashes':before,
         'calls':len(rows),'planned_cases_by_section':dict(counts),'returned':sum(r['status']=='returned'for r in rows),
         'expected_errors_by_section':dict(expected_errors),'records':rows}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/'public-schema-checks.json.gz').write_bytes(raw)
summary={k:v for k,v in receipt.items()if k not in('records','source_hashes')}
summary['full_result_gzip_sha256']=hashlib.sha256(raw).hexdigest()
(P/'public-schema-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
