"""Qualified SP setter gates and local encoder/copy arguments, not actual SP."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib,json
from .sp_recovery_clock import (_id,_tri,_raw,_merge,_fork,sp_recovery_clock_reference,
                                public_example as clock_example)
from .mechanist_explosion_math import ONE

SOURCE='rouge/data/sp-setter-source.json'
SOURCE_SHA256='66fb85a986c9fec6335bfe6879a6a8b72df607521950dc726a1128c63315033a'


@lru_cache(maxsize=1)
def _source_data():
    root=Path(__file__).resolve().parents[1]
    try:
        raw=(root/SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:return None
        d=json.loads(raw)
        for p,h in d['source_artifacts_sha256'].items():
            if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h:return None
        return d
    except (OSError,ValueError,KeyError):return None
def source_data():return deepcopy(_source_data())
def _validate(p):
    if type(p) is not dict or set(p)!={'body_reads','clock_bridge'}:raise ValueError('需要body_reads与clock_bridge。')
    reads=p['body_reads']
    if type(reads) is not list or not 1<=len(reads)<=100:raise ValueError('独立写入声明需要1–100项。')
    seen={}
    for r in reads:
        keys={'id','mode','ordinary_native_path','bound_virtual_dispatch','target_exists','force','value_source','value_raw',
              'alive_read','max_sp_read','encoding_returns_normally','copy_returns_normally'}
        if type(r) is not dict or set(r)!=keys:raise ValueError('请使用完整SP写入声明。')
        _id(r['id'])
        if r['id'] in seen:raise ValueError('body读取身份不能重复。')
        seen[r['id']]=r
        if r['mode'] not in ('public','internal','do_internal'):raise ValueError('mode需要public、internal或do_internal。')
        if r['value_source'] not in ('independent','clock_request'):raise ValueError('参数来源需要独立值或clock_request。')
        for k in ('ordinary_native_path','bound_virtual_dispatch','target_exists','force','encoding_returns_normally','copy_returns_normally'):_tri(r[k])
        if r['mode']=='public' and r['force'] is not False:raise ValueError('公共set_sp固定internal force=false。')
        _raw(r['value_raw'])
        if r['value_source']=='clock_request' and r['value_raw'] is not None:raise ValueError('clock请求不能另填值覆盖。')
        a=r['alive_read'];m=r['max_sp_read']
        if type(a) is not dict or set(a)!={'normal','value'} or type(m) is not dict or set(m)!={'normal','value'}:raise ValueError('存活与上限读取需要normal/value。')
        _tri(a['normal']);_tri(a['value']);_tri(m['normal'])
        if m['value'] is not None and (type(m['value']) is not int or not -(1<<31)<=m['value']<(1<<31)):raise ValueError('maxSp需要signed32整数或null。')
    bridge=p['clock_bridge'];linked=set();points=set()
    if bridge is not None:
        if type(bridge) is not dict or set(bridge)!={'input','links'} or type(bridge['links']) is not list or len(bridge['links'])>100:raise ValueError('clock_bridge需要完整274输入与最多100条链接。')
        for l in bridge['links']:
            if type(l) is not dict or set(l)!={'body_id','action_id','phase','same_target','no_intervening_value_change'}:raise ValueError('链接需要独立body/action/phase与身份/未变资格。')
            _id(l['body_id']);_id(l['action_id'])
            if l['phase'] not in ('tick','drain','recover'):raise ValueError('phase需要tick、drain或recover。')
            _tri(l['same_target']);_tri(l['no_intervening_value_change'])
            if l['body_id'] not in seen:raise ValueError('链接的body身份不存在。')
            r=seen[l['body_id']]
            if r['value_source']!='clock_request' or r['mode']!='public':raise ValueError('clock只能接public setter，不能覆写独立值或internal force。')
            if l['body_id'] in linked or (l['action_id'],l['phase']) in points:raise ValueError('body及同一clock读点不能重复绑定。')
            linked.add(l['body_id']);points.add((l['action_id'],l['phase']))
    if linked!={r['id'] for r in reads if r['value_source']=='clock_request'}:raise ValueError('每个clock_request必须有一个独立链接。')


def _base(d,value,called=True):
    return {'id':d['id'],'mode':d['mode'],'called_reference':called,'input_value_raw_reference':value,
        'internal_called_reference':False,'normal_return_reference':None,'public_void_returns_normally_reference':None,
        'internal_bool_return_reference':None,'alive_called_reference':False,'alive_normal_reference':None,
        'max_sp_called_reference':False,'max_sp_normal_reference':None,'upper_raw_reference':None,
        'clamped_value_raw_reference':None,'encoder_called_reference':False,'encoder_value_argument_raw_reference':None,
        'encoder_normal_reference':None,'copy_called_reference':False,'full_struct_copy_completed_reference':False,
        'struct_copy_bytes_reference':0,'declared_reading_complete_reference':True if called is False else None,
        'actual_decoded_sp_after':None,'actual_encoded_sp':None,'status':'not_called'}
def _unknown(d,value,called=None):
    r=_base(d,value,called)
    for k in ('internal_called_reference','alive_called_reference','max_sp_called_reference','encoder_called_reference',
              'copy_called_reference','full_struct_copy_completed_reference','struct_copy_bytes_reference'):r[k]=None
    r['status']='unqualified_source_or_path';return r
def _finish(r,normal,internal=None):
    r.update(normal_return_reference=normal,internal_bool_return_reference=internal,
             public_void_returns_normally_reference=normal if r['mode']=='public' else None,
             declared_reading_complete_reference=normal)
    return r
def _clamp(value,upper):
    if upper is not None and upper<=0:return 0
    if value is not None and value<=0:return 0
    return max(min(value,upper),0) if value is not None and upper is not None else None
def _body(value,d):
    if d['ordinary_native_path'] is not True:return _unknown(d,value,True)
    if d['target_exists'] is None:return _fork(_body,(value,d),('target_exists',))
    r=_base(d,value)
    if d['target_exists'] is False:
        r['internal_called_reference']=d['mode']!='public';r['status']='missing_target_before_getter';return _finish(r,False)
    if d['bound_virtual_dispatch'] is not True:
        r=_unknown(d,value,True);r['internal_called_reference']=True if d['mode']!='public' else None;return r
    r['internal_called_reference']=True;r['alive_called_reference']=True
    if d['alive_read']['normal'] is None:return _fork(_body,(value,d),('alive_read','normal'))
    r['alive_normal_reference']=d['alive_read']['normal']
    if d['alive_read']['normal'] is False:r['status']='alive_read_failed';return _finish(r,False)
    if d['alive_read']['value'] is None:return _fork(_body,(value,d),('alive_read','value'))
    if not d['alive_read']['value']:
        if d['force'] is None:return _fork(_body,(value,d),('force',))
        if not d['force']:r['status']='alive_gate_rejected';return _finish(r,True,False)
    r['max_sp_called_reference']=True
    if d['max_sp_read']['normal'] is None:return _fork(_body,(value,d),('max_sp_read','normal'))
    r['max_sp_normal_reference']=d['max_sp_read']['normal']
    if d['max_sp_read']['normal'] is False:r['status']='max_sp_read_failed';return _finish(r,False)
    upper=None if d['max_sp_read']['value'] is None else d['max_sp_read']['value']*ONE
    value=_clamp(value,upper);r.update(upper_raw_reference=upper,clamped_value_raw_reference=value,
        encoder_called_reference=True,encoder_value_argument_raw_reference=value)
    if d['encoding_returns_normally'] is None:return _fork(_body,(r['input_value_raw_reference'],d),('encoding_returns_normally',))
    r['encoder_normal_reference']=d['encoding_returns_normally']
    if d['encoding_returns_normally'] is False:r['status']='encoding_failed_before_copy';return _finish(r,False)
    r['copy_called_reference']=True;n=d['copy_returns_normally']
    r.update(full_struct_copy_completed_reference=n,struct_copy_bytes_reference=40 if n is True else None,
             status='encoded_structure_copied' if n is True else 'partial_copy_not_closed')
    return _finish(r,n,True if n is True else None)


def _request(clock,link):
    rows={r['id']:r for r in clock['rows']}
    if link['action_id'] not in rows:raise ValueError('clock action身份不存在。')
    row=rows[link['action_id']];phase=link['phase'];required={'tick':'tick','drain':'reconfigure','recover':'recover'}[phase]
    if row['kind']!=required:raise ValueError('链接phase与clock行动类型不对应。')
    part=row['recovery'] if phase=='recover' else row[phase]
    if part is None:
        called=False if row['called_reference'] is False or type(row['normal_return_reference']) is bool else None
        return {'called':called,'value':None,'normal':None}
    if phase!='recover':
        recovery=part['recovery']
        if recovery is None:return {'called':False if part['recovery_called_reference'] is False else None,'value':None,'normal':None}
        part=recovery
    return {'called':part['setter_called_reference'],'value':part['setter_value_argument_raw_reference'],'normal':part['setter_normal_reference']}
def _linked(request,d):
    if request['called'] is False:return _base(d,None,False)
    if request['called'] is True:return _body(request['value'],d)
    active=_body(request['value'],d);skipped=_base(d,None,False);r=_merge(active,skipped)
    r.update(status='conditional_clock_invocation',conditional_branches=[skipped,active]);return r


def sp_setter_reference(payload):
    _validate(payload);valid=_source_data() is not None
    bridge=payload['clock_bridge'];clock=sp_recovery_clock_reference(deepcopy(bridge['input'])) if bridge is not None else None
    link_by_id={l['body_id']:l for l in bridge['links']} if bridge is not None else {}
    rows=[];links=[]
    for d in payload['body_reads']:
        link=link_by_id.get(d['id']);request=None
        if link is not None:request=_request(clock,link)
        qualified=bool(valid and clock['source_valid'] and link['same_target'] is True and link['no_intervening_value_change'] is True) if link is not None else False
        if not valid:r=_unknown(d,None,None)
        elif link is None:r=_body(d['value_raw'],d)
        else:r=_linked(request,d) if qualified else _unknown(d,None,None)
        if link is not None:
            parent_normal=request['normal'];child_normal=r['public_void_returns_normally_reference']
            consistent=parent_normal==child_normal if type(parent_normal) is bool and type(child_normal) is bool else None
            links.append({'body_id':d['id'],'action_id':link['action_id'],'phase':link['phase'],'qualified':qualified,
                'parent_setter_called_reference':request['called'],'parent_value_argument_raw_reference':request['value'],
                'parent_setter_normal_reference':parent_normal,'public_void_normal_reference':child_normal,
                'normal_return_consistent_reference':consistent,
                'status':'normal_qualification_conflict' if consistent is False else 'qualified_declaration_link' if qualified else 'unqualified_link'})
        rows.append(r)
    complete=valid and all(r['declared_reading_complete_reference'] is True for r in rows)
    complete=complete and all(l['qualified'] and l['normal_return_consistent_reference'] is not False for l in links)
    counts=[r['full_struct_copy_completed_reference'] for r in rows]
    known=sum(v is True for v in counts)
    return {'source_valid':valid,'source_file':SOURCE,'rows':rows,'clock_links':links,'clock_reference':clock,
        'known_full_struct_copies_count':known,'declared_readings_complete':complete,
        'declared_complete_struct_copy_count':known if complete and all(type(v) is bool for v in counts) else None,
        'actual_sp_after':None,'actual_complete_recovery':None,'actual_skill_cycle':None,'actual_clock':None,'actual_encoded_state':None,
        'events_scheduled':False,'hotfix_equivalence_proven':False,
        'scope':'Independent SP setter source declarations only; void normal return, internal bool and complete local copy are distinct, not actual decoded SP.'}


def _example_body(identity,*,mode='public',force=False,value=None,source='clock_request',alive=True,maximum=6):
    return {'id':identity,'mode':mode,'ordinary_native_path':True,'bound_virtual_dispatch':True,'target_exists':True,
        'force':force,'value_source':source,'value_raw':value,'alive_read':{'normal':True,'value':alive},
        'max_sp_read':{'normal':True,'value':maximum},'encoding_returns_normally':True,'copy_returns_normally':True}
def public_example():
    clock=clock_example()
    return {'body_reads':[_example_body('四点批量后限幅'),_example_body('强制恢复也被存活门拒绝',alive=False),
        _example_body('独立internal强制负值',mode='internal',force=True,value=-ONE,source='independent',alive=False,maximum=10)],
        'clock_bridge':{'input':clock,'links':[
            {'body_id':'四点批量后限幅','action_id':clock['actions'][0]['id'],'phase':'tick','same_target':True,'no_intervening_value_change':True},
            {'body_id':'强制恢复也被存活门拒绝','action_id':clock['actions'][2]['id'],'phase':'recover','same_target':True,'no_intervening_value_change':True}]}}
