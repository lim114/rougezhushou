"""Public-output design only; assertions do not provide actual Qt proof."""
from copy import deepcopy
import json

HARUKA_LOCKED_NOTE080='当前培养尚未解锁扶摇花火；浮泡破碎声明保留，但不产生该天赋治疗或二技能中依赖该治疗的派生伤害。'

def canonical080(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

def normalized_locked_haruka080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明窗口内浮泡破碎次数',0.0,'次')
        ref['notes']=[n for n in ref['notes']if n!=HARUKA_LOCKED_NOTE080]
    for section in value['report']['sections']:
        if section['id']=='external_events':
            section['notes']=[n for n in section['notes']if n!=HARUKA_LOCKED_NOTE080]
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_haruka080(result,args,text,plain):
    count=args['bubble_bursts'];qualified=args['elite']==2
    ref=result['external_event_reference']
    assert ref['kind']=='haruka_bubbles'
    assert ref['parameter_rows'][0]==('声明窗口内浮泡破碎次数',float(count),'次')
    assert ref['actual_event_times_seconds'] is None
    if not qualified:
        assert canonical080(normalized_locked_haruka080(result))==canonical080(plain)
        if count>0:assert HARUKA_LOCKED_NOTE080 in ref['notes'] and HARUKA_LOCKED_NOTE080 in text
        else:assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        for component in result['components']:
            if component['name'] in ('扶摇花火','浮泡治疗衍生伤害'):
                assert component['hits']==0 and component['total']==0
                assert 'actual_total' not in component
    else:
        assert HARUKA_LOCKED_NOTE080 not in ref['notes']
        healing=result['haruka_healing_reference']
        assert healing['native_attachment_verified'] is False
        assert healing['native_composition_verified'] is False
        if count>0 and args['window_seconds']>0:
            assert result['total_healing'] is None
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_aglna080(result,args,text,controls):
    name='飘浮大地之上'
    component=next(c for c in result['components']if c['name']==name)
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts'][name]==0
        assert canonical080(result)==canonical080(controls['light'])
    else:
        weight=args['enemy_weight']
        if weight<=3:
            assert canonical080(result)==canonical080(controls['light'])
        else:
            assert canonical080(result)==canonical080(controls['heavy'])
            light=next(c for c in controls['light']['components']if c['name']==name)
            hi,lo={(1,1):(.2,.13),(1,3):(.3,.18),(2,1):(.35,.25),(2,3):(.45,.3)}[(args['elite'],args['potential'])]
            assert abs(component['per_hit']*hi-light['per_hit']*lo)<1e-7
    if args['skill']==2:
        ref=result['aglna_liftoff_reference']
        assert ref['actual_takeoff_seconds'] is None and ref['lifecycle_binding_verified'] is False
        assert result['estimate']['skill']['duration_seconds'] is None
        assert result['estimate']['skill']['cycle_seconds'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0

def require_aglna_selected080(result,args,text,plain,mass):
    target=args['target_enemy'];enemy=result['run_resolution']['enemy']
    for key in ('stage_id','enemy_id','level'):
        assert enemy[key]==target[key]
    assert enemy['reference_stats']['massLevel']==mass
    assert canonical080(result)==canonical080(plain)
    component=next(c for c in result['components']if c['name']=='飘浮大地之上')
    if args['elite']==0:
        assert component['hits']==component['per_hit']==component['total']==0
        assert component['times_seconds']==[]
        assert result['estimate']['skill']['hit_counts']['飘浮大地之上']==0
    else:
        assert component['hits']>0 and component['per_hit']>0
    assert enemy['name'] in text

def normalized_locked_mantra080(result):
    value=deepcopy(result)
    for ref in (value['external_event_reference'],value['external_event_reference']['window_reference']):
        ref['parameter_rows'][0]=('声明当前目标麻痹触发次数',0.0,'次')
    for section in value['report']['sections']:
        if section['id']=='external_events':
            next(m for m in section['metrics']if m['key']=='parameter_0')['value']=0.0
    return value

def require_mantra080(result,args,text,plain):
    count=args['palsy_triggers'];qualified=args['elite']>=1
    ref=result['external_event_reference'];window=ref['window_reference']
    assert ref['kind']=='mantra_events'
    assert ref['parameter_rows'][0]==('声明当前目标麻痹触发次数',float(count),'次')
    assert window['parameter_rows'][0]==ref['parameter_rows'][0]
    assert ref['actual_event_times_seconds'] is None
    assert ref['collision_clock_verified'] is False and window['collision_clock_verified'] is False
    if not qualified:
        assert canonical080(normalized_locked_mantra080(result))==canonical080(plain)
        component=next(c for c in result['components']if c['name']=='麻痹触发天赋')
        assert component['hits']==component['per_hit']==component['total']==0
        assert 'actual_total'not in component
    elif count>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage'] is None
    if args['skill']==3:
        assert ref['parameter_rows'][1]==('声明当前目标溢出跳跃命中次数',float(args['palsy_overflow_hits']),'次')
        if args['palsy_overflow_hits']>0 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
            assert result['total_damage'] is None
    if args['window_seconds']==0 or args.get('timing',{}).get('target_disappears_seconds')==0:
        assert result['total_damage']==0
    assert '独立条件来源 · 事件时钟待核验' in text

def require_medical_amiya080(result,args,text):
    name='诚挚期许本体生命回复'
    component=next(c for c in result['components']if c['name']==name)
    assert component['damage_type']=='regeneration' and component['source_unit']=='operator'
    assert type(component['hits'])is float and type(component['total'])is float
    assert '阿米娅 · 医疗'in text
    if args['elite']==0:
        assert args['skill']==1
        assert component['hits']==component['per_hit']==component['total']==0
        assert type(result['estimate']['skill']['hit_counts'][name])is float
        assert result['estimate']['skill']['hit_counts'][name]==0.0
        assert 'actual_total'not in component
        assert name not in result['timing'].get('unplaced_components',[])
        assert not any('尚未统一排入时间轴' in note and name in note for note in result['estimate']['notes'])
        assert '尚未统一排入时间轴的输出分项：'+name not in text
        assert result['estimate']['skill']['duration_seconds']>0
    else:
        assert component['per_hit']>0
        assert component['hits']==float(args['window_seconds'])
        if args['skill']==1:
            assert 'actual_total'not in component
            assert result['estimate']['skill']['hit_counts'][name]>0
            if args['timing_mode']=='frames' and args['window_seconds']>0:
                assert name in result['timing']['unplaced_components']
        else:
            phase=result['amiya_phase_reference']
            assert phase['actual_strengthening_start_seconds']is None
            assert phase['actual_skill_end_seconds']is None
            assert phase['phase_clock_verified']is False
            assert phase['opening_buff_healing_order_verified']is False
            assert result['estimate']['skill']['duration_seconds']is None
            assert result['estimate']['skill']['cycle_seconds']is None
            assert component['nominal_duration_reference_seconds']==float(args['window_seconds'])
            if args['window_seconds']>0:assert component['actual_total']is None
            else:assert 'actual_total'not in component
    if args['window_seconds']==0:
        assert result['total_damage']==0 and result['total_healing']==0
    if args['skill']==2 and args['window_seconds']>0 and args.get('timing',{}).get('target_disappears_seconds')!=0:
        assert result['total_damage']is None
        if args['healing_targets']==0:assert result['total_healing']==0
        else:assert result['total_healing']is None

def require_medical_trait080(result,args,text,ratio):
    require_medical_amiya080(result,args,text)
    heal=next(c for c in result['components']if c['name']=='咒愈师伤害转治疗')
    dependent=heal['damage_healing']
    expected=ratio*min(1,args['healing_targets'])
    assert dependent['ratio']==expected
    assert dependent['sources']==([0]if args['skill']==1 else [0,1])
    healing_factor=1.2 if args['relic_ids']==['rogue_6_relic_legacy_81']else 1.0
    subtotal=sum(result['components'][i]['total']for i in dependent['sources'])
    assert abs(heal['total']-subtotal*expected*healing_factor)<1e-7
    if args['skill']==2:
        phase=result['amiya_phase_reference']
        assert abs(phase['opening_healing_reference']-phase['opening_damage_reference']*expected*healing_factor)<1e-7
        if (args['window_seconds']>0 and args['healing_targets']>0 and
                args.get('timing',{}).get('target_disappears_seconds')!=0):
            assert heal['actual_total']is None
            assert phase['actual_skill_end_seconds']is None
        if args.get('timing',{}).get('target_disappears_seconds')==0:
            assert heal['total']==0 and 'actual_total'not in heal
    elif args['healing_targets']==2:
        direct=next(c for c in result['components']if c['name']=='哀恸共情范围治疗')
        assert direct['hits']>0 and direct['total']>0
        assert dependent['ratio']==ratio

