"""Source-bound natural SP batch timers over independent declared reads.

Timer writes and setter arguments do not establish real SP, clocks or cycles.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib,json
from .mechanist_explosion_math import ONE,MIN_RAW,MAX_RAW,EPSILON,add,subtract,multiply

SOURCE='rouge/data/sp-recovery-clock-source.json'
SOURCE_SHA256='97eca07c12681f6d1b14239fe560d15f7bed60772c1d2a9b4c99d8202181a620'
FP_MAX=MAX_RAW-1


@lru_cache(maxsize=1)
def _source_data():
    root=Path(__file__).resolve().parents[1]
    try:
        raw=(root/SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:return None
        data=json.loads(raw)
        for p,d in data['source_artifacts_sha256'].items():
            if hashlib.sha256((root/p).read_bytes()).hexdigest()!=d:return None
        return data
    except (OSError,ValueError,KeyError):return None


def source_data():return deepcopy(_source_data())
def _and(*v):return False if False in v else None if None in v else True
def _tri(v):
    if v is not None and type(v) is not bool:raise ValueError('资格需要true、false或null。')
def _raw(v):
    if v is not None and (type(v) is not int or not MIN_RAW<=v<=MAX_RAW):raise ValueError('需要signed64 FP原值或null。')
def _id(v):
    if type(v) is not str or not 1<=len(v)<=60 or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in v):raise ValueError('身份需要1–60字符，不能含控制字符。')
def _read(v,kind):
    keys={'exists','normal','raw'} if kind=='sp' else {'normal','value'} if kind=='full' else {'exists','normal','value'}
    if type(v) is not dict or set(v)!=keys:raise ValueError('请使用完整独立读取声明。')
    for k in keys-{'raw'}:_tri(v[k])
    if 'raw' in keys:_raw(v['raw'])
def _recovery(v):
    if type(v) is not dict or set(v)!={'ordinary_native_path','force','stop_read','sp_read','setter_returns_normally'}:raise ValueError('恢复需要独立暂停、SP读点与setter正常资格。')
    for k in ('ordinary_native_path','force','setter_returns_normally'):_tri(v[k])
    _read(v['stop_read'],'stop');_read(v['sp_read'],'sp')
def _validate_tick(a,seen):
    if type(a) is not dict or set(a)!={'id','kind','ordinary_native_path','delta_raw','enabled','gate_stop','full_read','recovery'} or a['kind']!='tick':raise ValueError('tick需要完整批量定时器声明。')
    _identity(a,seen);_tri(a['enabled']);_raw(a['delta_raw']);_read(a['gate_stop'],'stop');_read(a['full_read'],'full');_recovery(a['recovery'])
    if a['recovery']['force'] is not False:raise ValueError('自然OnTick的恢复固定force=false；显式恢复另用recover。')
def _identity(a,seen):
    _id(a['id']);_tri(a['ordinary_native_path'])
    if a['id'] in seen:raise ValueError('操作和drain读取身份不能重复。')
    seen.add(a['id'])
def _validate(p):
    if type(p) is not dict or set(p)!={'controller_exists','precise_timer_identity','no_intervening_timer_changes','timer','actions'}:raise ValueError('请使用完整自然技力时钟声明。')
    for k in ('controller_exists','precise_timer_identity','no_intervening_timer_changes'):_tri(p[k])
    t=p['timer']
    if type(t) is not dict or set(t)!={'exists','period_raw','remaining_raw'}:raise ValueError('timer需要存在、周期和剩余原值。')
    _tri(t['exists']);_raw(t['period_raw']);_raw(t['remaining_raw'])
    if type(p['actions']) is not list or not 1<=len(p['actions'])<=100:raise ValueError('操作需要1–100项。')
    seen=set()
    for a in p['actions']:
        if type(a) is not dict:raise ValueError('操作需要对象。')
        kind=a.get('kind')
        if kind=='tick':_validate_tick(a,seen)
        elif kind=='recover':
            if set(a)!={'id','kind','ordinary_native_path','amount_raw','recovery'}:raise ValueError('显式recover字段不完整。')
            _identity(a,seen);_raw(a['amount_raw']);_recovery(a['recovery'])
        elif kind=='reconfigure':
            if set(a)!={'id','kind','ordinary_native_path','rate_input_raw','drain','can_recover_rate'}:raise ValueError('改速需要传入率与独立drain/canRecover读点。')
            _identity(a,seen);_raw(a['rate_input_raw'])
            if a['drain'] is not None:
                _validate_tick(a['drain'],seen)
                if a['drain']['delta_raw']!=0:raise ValueError('UpdateSpRecoveryPerSec的drain固定delta=0。')
            s=a['can_recover_rate']
            if s is not None:
                if type(s) is not dict or set(s)!={'ordinary_native_path','attributes_exist','reads_return_normally','attr14_raw','attr30_raw'}:raise ValueError('canRecover需要独立14/30属性快照。')
                for k in ('ordinary_native_path','attributes_exist','reads_return_normally'):_tri(s[k])
                _raw(s['attr14_raw']);_raw(s['attr30_raw'])
        else:raise ValueError('kind需要tick、recover或reconfigure。')


def safe_fp_divide(numerator,denominator):
    """Native extra-bit rounding only in the bound non-overflow subdomain."""
    if denominator==0:return -ONE
    if denominator is None or numerator is None:return None
    if abs(numerator)*ONE>abs(denominator)*FP_MAX:return None
    magnitude=(((abs(numerator)<<33)//abs(denominator))+1)>>1
    return -magnitude if (numerator<0)!=(denominator<0) else magnitude


def _normal_read(s):return _and(s.get('exists',True),s['normal'])
def _merge(a,b):
    if type(a) is dict and type(b) is dict:return {k:_merge(a.get(k),b.get(k)) for k in a.keys()|b.keys()}
    return deepcopy(a) if type(a) is type(b) and a==b else None
def _fork(function,args,path,*,prefix_remaining=None):
    reports=[]
    for value in (False,True):
        declaration=deepcopy(args[-1]);target=declaration
        for key in path[:-1]:target=target[key]
        target[path[-1]]=value;reports.append(function(*args[:-1],declaration))
    r=_merge(*reports);r['status']='conditional_native_branches';r['conditional_branches']=reports
    if 'known_prefix_remaining_raw_reference' in r and r['known_prefix_remaining_raw_reference'] is None:r['known_prefix_remaining_raw_reference']=prefix_remaining
    return r
def _unknown_tick_future(r):
    r.update(next_multiple_called_reference=None,next_advanced_reference=None,recovery_called_reference=None)
    return r
def _recover(amount,s):
    r={'called_reference':True,'amount_raw_reference':amount,'normal_return_reference':None,
       'stop_read_called_reference':False,'stop_read_normal_reference':None,
       'getter_called_reference':False,'getter_normal_reference':None,'sp_read_raw_reference':None,
       'setter_called_reference':False,'setter_normal_reference':None,'setter_value_argument_raw_reference':None,
       'declared_request_count_reference':None,'actual_sp_after':None,'status':'unqualified_recovery_path'}
    if s['ordinary_native_path'] is not True:
        r.update(stop_read_called_reference=None,getter_called_reference=None,setter_called_reference=None);return r
    force=s['force']
    if force is None:return _fork(_recover,(amount,s),('force',))
    if not force:
        stop=s['stop_read']
        for key in ('exists','normal'):
            if stop[key] is None:return _fork(_recover,(amount,s),('stop_read',key))
        r['stop_read_called_reference']=stop['exists'];n=_normal_read(stop);r['stop_read_normal_reference']=n if stop['exists'] else None
        if n is not True:r.update(normal_return_reference=n,status='unqualified_recovery_stop_read');return r
        stopped=stop['value']
        if stopped is None:return _fork(_recover,(amount,s),('stop_read','value'))
        if stopped:r.update(normal_return_reference=True,declared_request_count_reference=0,status='recovery_stopped');return r
    sp=s['sp_read']
    for key in ('exists','normal'):
        if sp[key] is None:return _fork(_recover,(amount,s),('sp_read',key))
    r['getter_called_reference']=sp['exists'];n=_normal_read(sp);r['getter_normal_reference']=n if sp['exists'] else None
    if n is not True:
        r.update(normal_return_reference=n,status='unqualified_sp_getter',setter_called_reference=False if n is False else None);return r
    before=s['sp_read']['raw'];r['sp_read_raw_reference']=before
    r.update(setter_called_reference=True,setter_value_argument_raw_reference=add(before,amount),setter_normal_reference=s['setter_returns_normally'],
             normal_return_reference=s['setter_returns_normally'],declared_request_count_reference=1,status='setter_argument_reference')
    return r


def _tick(period,remaining,timer_exists,timer_qualified,a):
    r={'period_after_raw_reference':period,'valid_reference':None,'delta_applied_reference':False,'updated_remaining_raw_reference':None,
       'division_numerator_raw_reference':None,'quotient_raw_reference':None,'floor_count_reference':None,'batch_count_reference':None,
       'next_multiple_called_reference':False,'next_advanced_reference':False,'recovery':None,
       'recovery_called_reference':False,
       'known_prefix_remaining_raw_reference':remaining,'remaining_after_raw_reference':remaining,
       'normal_return_reference':None,'declared_request_count_reference':None,
       'gate_stop_called_reference':False,'full_read_called_reference':False,'status':'unqualified_tick_path'}
    if a['ordinary_native_path'] is not True:
        r.update(period_after_raw_reference=None,remaining_after_raw_reference=None,delta_applied_reference=None,gate_stop_called_reference=None,full_read_called_reference=None);return _unknown_tick_future(r)
    if a['enabled'] is False:r.update(normal_return_reference=True,declared_request_count_reference=0,status='natural_recovery_disabled');return r
    if a['enabled'] is None:return _fork(_tick,(period,remaining,timer_exists,timer_qualified,a),('enabled',),prefix_remaining=remaining)
    if timer_exists is not True:
        r.update(normal_return_reference=False if timer_exists is False else None,status='unqualified_timer',remaining_after_raw_reference=None)
        if timer_exists is None:r.update(delta_applied_reference=None,gate_stop_called_reference=None,full_read_called_reference=None);return _unknown_tick_future(r)
        return r
    if not timer_qualified:r.update(status='unqualified_timer_identity',remaining_after_raw_reference=None,delta_applied_reference=None,gate_stop_called_reference=None,full_read_called_reference=None);return _unknown_tick_future(r)
    valid=None if period is None else period>EPSILON;r['valid_reference']=valid
    if valid is False:r.update(normal_return_reference=True,declared_request_count_reference=0,status='invalid_timer_skipped');return r
    if valid is None:r.update(status='unknown_timer_validity',remaining_after_raw_reference=None,delta_applied_reference=None,gate_stop_called_reference=None,full_read_called_reference=None);return _unknown_tick_future(r)
    for key in ('exists','normal'):
        if a['gate_stop'][key] is None:return _fork(_tick,(period,remaining,timer_exists,timer_qualified,a),('gate_stop',key),prefix_remaining=remaining)
    r['gate_stop_called_reference']=a['gate_stop']['exists'];n=_normal_read(a['gate_stop'])
    if n is not True:r.update(normal_return_reference=n,status='unqualified_first_stop_read',remaining_after_raw_reference=remaining if n is False else None);return r
    stop=a['gate_stop']['value']
    if stop is True:r.update(normal_return_reference=True,declared_request_count_reference=0,status='first_stop_gate');return r
    if stop is None:return _fork(_tick,(period,remaining,timer_exists,timer_qualified,a),('gate_stop','value'),prefix_remaining=remaining)
    if a['full_read']['normal'] is None:return _fork(_tick,(period,remaining,timer_exists,timer_qualified,a),('full_read','normal'),prefix_remaining=remaining)
    r['full_read_called_reference']=True;n=a['full_read']['normal']
    if n is not True:r.update(normal_return_reference=n,status='unqualified_full_read',remaining_after_raw_reference=remaining if n is False else None);return r
    full=a['full_read']['value']
    if full is True:r.update(normal_return_reference=True,declared_request_count_reference=0,status='full_gate');return r
    if full is None:return _fork(_tick,(period,remaining,timer_exists,timer_qualified,a),('full_read','value'),prefix_remaining=remaining)
    updated=subtract(remaining,a['delta_raw'])
    r.update(delta_applied_reference=True,updated_remaining_raw_reference=updated,known_prefix_remaining_raw_reference=updated,remaining_after_raw_reference=updated)
    if updated is None:r['status']='unknown_updated_remaining';return _unknown_tick_future(r)
    if updated>=EPSILON:r.update(batch_count_reference=0,normal_return_reference=True,declared_request_count_reference=0,status='not_ready');return r
    numerator=FP_MAX if updated==MIN_RAW else -updated;quotient=safe_fp_divide(numerator,period)
    r.update(division_numerator_raw_reference=numerator,quotient_raw_reference=quotient)
    if quotient is None:r.update(status='unmodeled_count_division_domain',remaining_after_raw_reference=None);return _unknown_tick_future(r)
    floor=quotient>>32;count=(max(0,floor)+1)&0xffffffff
    if count>=1<<31:count-=1<<32
    r.update(floor_count_reference=floor,batch_count_reference=count)
    if count<=0:r.update(normal_return_reference=True,declared_request_count_reference=0,status='nonpositive_batch_count');return r
    r['next_multiple_called_reference']=True;r['recovery_called_reference']=True
    # No unseen timer change: the Precise ready check still sees updated R.
    after=add(updated,multiply(period,count*ONE))
    r.update(next_advanced_reference=True,known_prefix_remaining_raw_reference=after,remaining_after_raw_reference=after)
    recovery=_recover(count*ONE,a['recovery']);r['recovery']=recovery
    r.update(normal_return_reference=recovery['normal_return_reference'],declared_request_count_reference=recovery['declared_request_count_reference'],status='batch_'+recovery['status'])
    if a['recovery']['ordinary_native_path'] is not True:r.update(period_after_raw_reference=None,remaining_after_raw_reference=None)
    return r


def _rate(s):
    r={'normal_return_reference':None,'rate_raw_reference':None,'can_recover_reference':None}
    if s is None or s['ordinary_native_path'] is not True:return r
    n=_and(s['attributes_exist'],s['reads_return_normally']);r['normal_return_reference']=n
    if n is True:
        value=0 if s['attr14_raw']==0 or s['attr30_raw']==0 else multiply(s['attr14_raw'],s['attr30_raw'])
        r.update(rate_raw_reference=value,can_recover_reference=None if value is None else value>EPSILON)
    return r


def sp_recovery_clock_reference(payload):
    _validate(payload);source=_source_data();valid=source is not None
    timer=payload['timer'];qualified=valid and payload['precise_timer_identity'] is True and payload['no_intervening_timer_changes'] is True
    period=timer['period_raw'] if qualified and timer['exists'] is True else None
    remaining=timer['remaining_raw'] if qualified and timer['exists'] is True else None
    normal=True if valid else None;rows=[]
    for a in payload['actions']:
        row={'id':a['id'],'kind':a['kind'],'called_reference':True if normal is True else False if normal is False else None,
             'normal_return_reference':None,'period_before_raw_reference':period,'remaining_before_raw_reference':remaining,
             'period_after_raw_reference':period,'remaining_after_raw_reference':remaining,
             'tick':None,'recovery':None,'drain':None,'can_recover':None,'period_reset':None,'status':'not_called_after_unqualified_chain'}
        if normal is not True:
            if normal is None and a['kind']!='recover':period=remaining=None
            row.update(period_after_raw_reference=period,remaining_after_raw_reference=remaining);rows.append(row);continue
        if a['ordinary_native_path'] is not True or payload['controller_exists'] is not True:
            normal=False if a['ordinary_native_path'] is True and payload['controller_exists'] is False else None
            row.update(status='unqualified_controller_or_native_path',normal_return_reference=normal)
            if normal is None:period=remaining=None
        elif a['kind']=='recover':
            r=_recover(a['amount_raw'],a['recovery']);row['recovery']=r;normal=r['normal_return_reference'];row['status']=r['status']
            if a['recovery']['ordinary_native_path'] is not True:period=remaining=None
        elif a['kind']=='tick':
            r=_tick(period,remaining,timer['exists'],qualified,a);row['tick']=r;period=r['period_after_raw_reference'];remaining=r['remaining_after_raw_reference'];normal=r['normal_return_reference'];row['status']=r['status']
        else:
            old_valid=None if period is None else period>EPSILON
            if timer['exists'] is not True or not qualified:
                normal=False if timer['exists'] is False else None;row['status']='unqualified_timer'
            elif old_valid is None:normal=None;period=remaining=None;row['status']='unknown_timer_validity'
            else:
                if old_valid:
                    if a['drain'] is None:normal=None;remaining=None;row['status']='missing_independent_drain'
                    else:
                        drain=_tick(period,remaining,timer['exists'],qualified,a['drain']);row['drain']=drain;remaining=drain['remaining_after_raw_reference'];normal=drain['normal_return_reference'];row['status']=drain['status']
                    if normal is None:period=remaining=None
                    if normal is True:
                        rate=_rate(a['can_recover_rate']);row['can_recover']=rate;normal=rate['normal_return_reference'];can=rate['can_recover_reference']
                        if normal is True and can is False:period=remaining=-ONE;row['status']='marked_invalid'
                        elif normal is True and can is None:normal=None;period=remaining=None;row['status']='unknown_can_recover_gate'
                        elif normal is not True:
                            if normal is None:period=remaining=None
                            row['status']='unqualified_can_recover_read'
                if normal is True and (not old_valid or row['can_recover']['can_recover_reference'] is True):
                    new_period=safe_fp_divide(ONE,a['rate_input_raw'])
                    if new_period is None:normal=None;period=remaining=None;row['status']='unmodeled_period_division_domain'
                    elif old_valid:
                        past=subtract(period,remaining);unclamped=subtract(new_period,past)
                        remaining=None if unclamped is None else max(0,unclamped);period=new_period
                        row['period_reset']={'kind':'keep_past','new_period_raw_reference':new_period,'past_raw_reference':past,'unclamped_remaining_raw_reference':unclamped,'remaining_raw_reference':remaining};row['status']='reset_keep_past'
                    else:
                        # Periodic.Reset(newPeriod, true) first applies TSMath.Max(0,P).
                        # Its argument remains distinct from the stored period.
                        period=remaining=max(0,new_period)
                        row['period_reset']={'kind':'restart','new_period_raw_reference':new_period,'clamped_period_raw_reference':period,'past_raw_reference':None,'unclamped_remaining_raw_reference':None,'remaining_raw_reference':remaining};row['status']='reset_restart'
        row.update(normal_return_reference=normal,period_after_raw_reference=period,remaining_after_raw_reference=remaining);rows.append(row)
    complete=normal is True and all(r['normal_return_reference'] is True for r in rows)
    counts=[r['tick']['declared_request_count_reference'] if r['tick'] is not None else r['recovery']['declared_request_count_reference'] if r['recovery'] is not None else r['drain']['declared_request_count_reference'] if r['drain'] is not None else 0 for r in rows]
    count=sum(counts) if complete and all(v is not None for v in counts) else None
    return {'source_valid':valid,'source_file':SOURCE,'rows':rows,'normal_return_reference':normal,'declared_chain_complete':complete,
            'declared_complete_setter_request_count':count,'final_period_raw_reference':period,'final_remaining_raw_reference':remaining,
            'actual_sp_after':None,'actual_complete_recovery':None,'actual_skill_cycle':None,'actual_clock':None,'actual_attribute_values':None,
            'events_scheduled':False,'hotfix_equivalence_proven':False,
            'scope':'Independent Precise natural-SP declarations; batch advances before one SP request, not accepted SP or an actual skill cycle.'}


def _example_recovery(*,sp=5*ONE,stop=False,force=False):
    return {'ordinary_native_path':True,'force':force,'stop_read':{'exists':True,'normal':True,'value':stop},
            'sp_read':{'exists':True,'normal':True,'raw':sp},'setter_returns_normally':True}
def _example_tick(identity,delta,*,sp=5*ONE,recovery_stop=False):
    return {'id':identity,'kind':'tick','ordinary_native_path':True,'delta_raw':delta,'enabled':True,
            'gate_stop':{'exists':True,'normal':True,'value':False},'full_read':{'normal':True,'value':False},
            'recovery':_example_recovery(sp=sp,stop=recovery_stop)}
def public_example():
    return {'controller_exists':True,'precise_timer_identity':True,'no_intervening_timer_changes':True,
            'timer':{'exists':True,'period_raw':ONE//4,'remaining_raw':ONE//8},'actions':[
            _example_tick('一次补发四点',7*ONE//8),_example_tick('推进后独立暂停',ONE//4,recovery_stop=True),
            {'id':'强制独立负回复','kind':'recover','ordinary_native_path':True,'amount_raw':-2*ONE,
             'recovery':_example_recovery(sp=9*ONE,stop=True,force=True)}]}
