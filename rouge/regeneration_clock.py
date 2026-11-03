"""Source-bound Precise HP-recovery timer over independent FP declarations.

No real clock, relic attribute acquisition, callback or final HP is inferred.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import json
from .mechanist_explosion_math import ONE,MIN_RAW,MAX_RAW,EPSILON,add,subtract,multiply

SOURCE='rouge/data/regeneration-clock-source.json'
SOURCE_SHA256='9a1ee36d224dae223d7acf992385c226371fcb7c14284491d983f9f46cdd6d6b'


@lru_cache(maxsize=1)
def _source_data():
    root=Path(__file__).resolve().parents[1]
    try:
        raw=(root/SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:return None
        data=json.loads(raw)
        for path,digest in data['source_artifacts_sha256'].items():
            if hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest:return None
        return data
    except (OSError,ValueError,KeyError):return None


def source_data():
    return deepcopy(_source_data())


def _tri(value,name):
    if value is not None and type(value) is not bool:raise ValueError(name+'需要true、false或null。')


def _raw(value):
    if value is not None and (type(value) is not int or not MIN_RAW<=value<=MAX_RAW):
        raise ValueError('仅接受signed64 FP原值或null，不能填布尔值或小数。')


def _snapshot(snapshot):
    if snapshot is None:return
    if type(snapshot) is not dict or set(snapshot)!={'attributes_exist','reads_return_normally','flat_raw','max_hp_raw','ratio_raw'}:
        raise ValueError('快照需要属性存在/正常读取及独立flat、maxHP、ratio三项。')
    for k in ('attributes_exist','reads_return_normally'):_tri(snapshot[k],k)
    for k in ('flat_raw','max_hp_raw','ratio_raw'):_raw(snapshot[k])


def _validate(p):
    if type(p) is not dict or set(p)!={'ordinary_native_path','precise_timer_identity','no_intervening_timer_changes','timer','actions'}:
        raise ValueError('请使用完整常态生命回复定点时钟声明。')
    for k in ('ordinary_native_path','precise_timer_identity','no_intervening_timer_changes'):_tri(p[k],k)
    timer=p['timer']
    if type(timer) is not dict or set(timer)!={'exists','period_raw','remaining_raw'}:raise ValueError('timer需要存在、周期与剩余原值。')
    _tri(timer['exists'],'timer存在');_raw(timer['period_raw']);_raw(timer['remaining_raw'])
    actions=p['actions']
    if type(actions) is not list or not 1<=len(actions)<=100:raise ValueError('声明操作需要1–100项。')
    seen=set()
    for a in actions:
        if type(a) is not dict or a.get('kind') not in ('update','reconfigure'):raise ValueError('操作需要update或reconfigure。')
        common={'id','kind','hp_reads_raw','hp_access_returns_normally'}
        keys=common|({'delta_raw'} if a['kind']=='update' else {'dirty_attribute','can_recover_snapshot','period_snapshot'})
        if set(a)!=keys:raise ValueError('各操作字段必须完整，不能混用update与reconfigure。')
        identity=a['id']
        if type(identity) is not str or not 1<=len(identity)<=60 or identity in seen or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in identity):
            raise ValueError('操作id需要唯一1–60字符。')
        seen.add(identity)
        reads=a['hp_reads_raw'];normal=a['hp_access_returns_normally']
        if type(reads) is not list or type(normal) is not list or len(reads)!=len(normal) or len(reads)>1000:raise ValueError('各HP读点与正常返回资格一一对应，最多1000项。')
        for value in reads:_raw(value)
        for value in normal:_tri(value,'HP访问正常返回')
        if a['kind']=='update':_raw(a['delta_raw'])
        else:
            if type(a['dirty_attribute']) is not int or a['dirty_attribute'] not in (13,19):raise ValueError('仅核准属性13/19脏标分支；MAX_HP等其它分支不能借用。')
            _snapshot(a['can_recover_snapshot']);_snapshot(a['period_snapshot'])


def _rate(snapshot):
    if snapshot is None:return {'normal_return_reference':None,'rate_raw_reference':None,'ratio_part_raw_reference':None}
    normal=False if snapshot['attributes_exist'] is False or snapshot['reads_return_normally'] is False else True if snapshot['attributes_exist'] is True and snapshot['reads_return_normally'] is True else None
    part=(0 if snapshot['max_hp_raw']==0 or snapshot['ratio_raw']==0 else multiply(snapshot['max_hp_raw'],snapshot['ratio_raw'])) if normal is True else None
    return {'normal_return_reference':normal,'ratio_part_raw_reference':part,
        'rate_raw_reference':add(snapshot['flat_raw'],part) if normal is True else None}


def reciprocal_rate(rate):
    """ONE/rate only in the proved non-overflow quotient domain, or zero.

    For abs(rate)>=EPS, unsigned extended quotient is below2**50. The native
    extra quotient bit and final +1/shift round magnitude halfway upwards.
    Remaining tiny nonzero denominators are explicitly outside this feature.
    """
    if rate is None:return None
    if rate==0:return -ONE
    if abs(rate)<EPSILON:return None
    magnitude=(((ONE<<33)//abs(rate))+1)>>1
    return -magnitude if rate<0 else magnitude


def _valid(period):return None if period is None else period>EPSILON
def _ready(remaining):return None if remaining is None else remaining<EPSILON


def _drain(period,remaining,delta,action):
    report={'period_raw_reference':period,'remaining_before_raw_reference':remaining,'delta_raw':delta,
        'valid_reference':_valid(period),'delta_applied_reference':False,'requests':[],
        'normal_return_reference':True,'remaining_after_raw_reference':remaining,'status':'invalid_timer_skipped',
        'unused_independent_hp_reads':len(action['hp_reads_raw']),'declared_complete_request_count':0}
    if _valid(period) is False:return report
    if _valid(period) is not True:
        report.update(status='unknown_timer_validity',normal_return_reference=None,remaining_after_raw_reference=None,
            delta_applied_reference=None,declared_complete_request_count=None);return report
    remaining=subtract(remaining,delta)
    report.update(delta_applied_reference=True,status='declared_timer_reference',remaining_after_raw_reference=remaining)
    while True:
        due=_ready(remaining)
        if due is False:break
        if due is None:
            report.update(status='unknown_ready_gate',normal_return_reference=None);break
        remaining=add(remaining,period)
        index=len(report['requests'])
        if index>=len(action['hp_reads_raw']):
            report.update(status='missing_independent_hp_access',normal_return_reference=None,
                remaining_after_raw_reference=remaining if _ready(remaining) is False else None,
                known_prefix_remaining_raw_reference=remaining)
            report['next_advanced_without_qualified_hp_access_reference']=True;break
        before=action['hp_reads_raw'][index];normal=action['hp_access_returns_normally'][index]
        report['requests'].append({'index':index,'hp_read_raw_reference':before,
            'setter_value_argument_raw_reference':add(before,ONE),'remaining_after_next_raw_reference':remaining,
            'hp_access_normal_return_reference':normal,'hp_setter_called_reference':True if normal is True else None,
            'actual_hp_after':None})
        report['remaining_after_raw_reference']=remaining
        if normal is not True:
            report.update(status='unqualified_hp_access',normal_return_reference=normal,
                known_prefix_remaining_raw_reference=remaining)
            if normal is None and _ready(remaining) is not False:report['remaining_after_raw_reference']=None
            break
    report['unused_independent_hp_reads']=len(action['hp_reads_raw'])-len(report['requests'])
    report['declared_complete_request_count']=len(report['requests']) if report['normal_return_reference'] is True else None
    return report


def regeneration_clock_reference(payload):
    _validate(payload);source=_source_data();valid=source is not None
    gates=valid and all(payload[k] is True for k in ('ordinary_native_path','precise_timer_identity','no_intervening_timer_changes'))
    timer=payload['timer'];period=timer['period_raw'];remaining=timer['remaining_raw'];normal=True if gates else None
    if gates and timer['exists'] is not True:normal=False if timer['exists'] is False else None
    if normal is not True:period=remaining=None
    rows=[]
    for a in payload['actions']:
        row={'id':a['id'],'kind':a['kind'],'called_reference':normal is True,'normal_return_reference':None,
            'period_before_raw_reference':period,'remaining_before_raw_reference':remaining,
            'period_after_raw_reference':None,'remaining_after_raw_reference':None,'drain':None,'can_recover':None,'period_rate':None,
            'can_recover_hp_reference':None,'new_period_raw_reference':None,'reset_keep_past_reference':None,
            'status':'not_called_after_unqualified_chain'}
        if normal is not True:
            if normal is None:
                if a['kind']=='reconfigure':period=None
                remaining=None
            rows.append(row);continue
        drain=_drain(period,remaining,a['delta_raw'] if a['kind']=='update' else 0,a)
        row['drain']=drain;remaining=drain['remaining_after_raw_reference'];normal=drain['normal_return_reference']
        row['status']=drain['status']
        if a['kind']=='reconfigure' and normal is True:
            first=_rate(a['can_recover_snapshot']);row['can_recover']=first;normal=first['normal_return_reference']
            rate=first['rate_raw_reference'];can=None if rate is None else rate>EPSILON
            row['can_recover_hp_reference']=can
            if normal is True and can is False:
                period=remaining=-ONE;row['status']='marked_invalid'
            elif normal is True and can is True:
                second=_rate(a['period_snapshot']);row['period_rate']=second;normal=second['normal_return_reference']
                if normal is False:row['status']='unqualified_attribute_reads'
                elif normal is None:period=remaining=None;row['status']='unqualified_attribute_reads'
                else:
                    new_period=reciprocal_rate(second['rate_raw_reference']);row['new_period_raw_reference']=new_period
                    if new_period is not None:
                        past=subtract(period,remaining);unclamped=subtract(new_period,past)
                        remaining=None if unclamped is None else max(0,unclamped)
                        row['reset_keep_past_reference']={'past_raw_reference':past,'unclamped_remaining_raw_reference':unclamped,'clamped_remaining_raw_reference':remaining}
                        period=new_period;row['status']='reset_keep_past'
                    else:normal=None;period=remaining=None;row['status']='unqualified_period_read_or_division_domain'
            elif normal is True:normal=None;period=remaining=None;row['status']='unknown_can_recover_gate'
            else:
                if normal is None:period=remaining=None
                row['status']='unqualified_attribute_reads'
        row.update(normal_return_reference=normal,period_after_raw_reference=period,remaining_after_raw_reference=remaining)
        rows.append(row)
    counts=[r['drain']['declared_complete_request_count'] for r in rows if r['drain'] is not None and 'declared_complete_request_count' in r['drain']]
    complete=normal is True and all(r['called_reference'] and r['normal_return_reference'] is True for r in rows)
    return {'source_valid':valid,'source_file':SOURCE,'rows':rows,'normal_return_reference':normal,
        'declared_chain_complete':complete,'declared_complete_request_count':sum(counts) if complete else None,
        'final_period_raw_reference':period,'final_remaining_raw_reference':remaining,
        'actual_attribute_values':None,'actual_clock':None,'actual_hp_after':None,'actual_complete_healing':None,
        'events_scheduled':False,'hotfix_equivalence_proven':False,
        'scope':'Independent FP timer/attribute/HP access declarations only; requests are not final HP settlement.'}


def public_example():
    snapshot=lambda flat:{'attributes_exist':True,'reads_return_normally':True,'flat_raw':flat,'max_hp_raw':1000*ONE,'ratio_raw':0}
    return {'ordinary_native_path':True,'precise_timer_identity':True,'no_intervening_timer_changes':True,
        'timer':{'exists':True,'period_raw':ONE//2,'remaining_raw':ONE//4},'actions':[
        {'id':'先推进八分之一秒','kind':'update','delta_raw':ONE//8,'hp_reads_raw':[],'hp_access_returns_normally':[]},
        {'id':'独立两次读取后改为每秒四点','kind':'reconfigure','dirty_attribute':13,
         'can_recover_snapshot':snapshot(4*ONE),'period_snapshot':snapshot(4*ONE),'hp_reads_raw':[],'hp_access_returns_normally':[]},
        {'id':'独立四次HP读取','kind':'update','delta_raw':3*ONE//4,'hp_reads_raw':[n*ONE for n in (900,901,902,903)],
         'hp_access_returns_normally':[True]*4}]}
