"""Source-bound SP14/30 reads, initial raw14 and dirty-to-timer references."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, importlib.util, json

SOURCE_DIRECTORY=Path(__file__).resolve().parents[1]/'research/p2-sp-recovery-attributes-282'
PROOF_SHA256='aabeb783fdfdb28edd68ee2a3f71b5f96e002adaf024c5c94b3efba4e1e5bb5a'
MANIFEST_SHA256='c0c2ba16e1e6e3c2060aafad1def71498309d555eca5e433f63a8e0761cc6666'
ONE=1<<32; MIN_RAW=-(1<<63); MAX_RAW=(1<<63)-1
FIELDS=('addition','multiplier_delta','final_addition','final_scaler')
UNKNOWNS=('actual_attribute_values','actual_cache_or_dirty_state','actual_sp_after','actual_timer','complete_cycle')
INIT_STAGES=('attributes_read','sp_data_access','increments_read','increments_guard','slot0_read',
 'single_conversion','attributes_guard','raw_array_capture','raw_encode','raw_array_guard','raw_store','mark_dirty','refresh')
NOTIFY_STAGES=('entity_access','controller_capture','new_rate','controller_guard','controller_update')
RATE_STAGES=('first_attributes_getter','flat_read','second_attributes_getter','ratio_read','multiply')
_MODULES={}

def _sha(raw):return hashlib.sha256(raw).hexdigest()
def source_data():
    out={'valid':False,'status':'source_unavailable','proof_sha256':None,'method_count':None,'byte_span_count':None}
    try:
        raw=(SOURCE_DIRECTORY/'source_manifest.json').read_bytes()
        if _sha(raw)!=MANIFEST_SHA256:return out|{'status':'manifest_sha_mismatch'}
        manifest=json.loads(raw);raw=(SOURCE_DIRECTORY/'source-proof.json').read_bytes()
        if _sha(raw)!=PROOF_SHA256:return out|{'status':'proof_sha_mismatch'}
        proof=json.loads(raw);root=Path(__file__).resolve().parents[1]
        for path,digest in manifest['files_sha256'].items():
            if _sha((root/path).read_bytes())!=digest:return out|{'status':'bound_file_sha_mismatch'}
        if proof['dll_sha256']!=manifest['dll_sha256'] or proof['metadata_sha256']!=manifest['metadata_sha256']:return out|{'status':'primary_identity_mismatch'}
        return out|{'valid':True,'status':'bound_file_sources','proof_sha256':PROOF_SHA256,
                    'method_count':proof['selected_method_count'],'byte_span_count':proof['byte_span_count']}
    except (OSError,ValueError,KeyError,TypeError):return out

def _modules():
    # Only fixed sibling modules, after uncached SHA guard; no public evaluator.
    for key,file in (('attributes','recovery_attributes.py'),('clock','sp_recovery_clock.py'),('increments','skill_sp_increment_reference.py')):
        if key not in _MODULES:
            name=__package__+'._sp282_bound_'+key
            spec=importlib.util.spec_from_file_location(name,Path(__file__).resolve().parent/file)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            _MODULES[key]=module
    return _MODULES

def _keys(v,keys):
    if type(v) is not dict or set(v)!=set(keys):raise ValueError('字段不完整或含未支持覆盖。')
def _tri(v):
    if v is not None and type(v) is not bool:raise ValueError('资格须为true、false或null。')
def _integer(v,lo,hi):
    if v is not None and (type(v) is not int or not lo<=v<=hi):raise ValueError('数值类型或范围无效。')
def _raw(v):_integer(v,MIN_RAW,MAX_RAW)
def _id(v,nullable=False):
    if nullable and v is None:return
    if type(v) is not str or not 1<=len(v)<=80 or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in v):raise ValueError('身份须为1–80字符。')
def _new(v,seen):
    _id(v)
    if v in seen:raise ValueError('独立身份不能重复。')
    seen.add(v)
def _pointer(v,seen,array=False):
    _keys(v,{'id','normal','exists','identity'}|({'length'} if array else set()))
    _new(v['id'],seen);_tri(v['normal']);_tri(v['exists']);_id(v['identity'],True)
    if array:_integer(v['length'],0,(1<<31)-1)
def _reading(v,seen):
    _keys(v,{'id','attribute','ordinary_native_path','attributes_exist','dirty','decoded_cache','calculation'})
    _new(v['id'],seen)
    if type(v['attribute']) is not int or v['attribute'] not in (14,30):raise ValueError('仅SP属性14/30。')
    for k in ('ordinary_native_path','attributes_exist','dirty'):_tri(v[k])
    _keys(v['decoded_cache'],{'normal','raw'});_tri(v['decoded_cache']['normal']);_raw(v['decoded_cache']['raw'])
    c=v['calculation']
    if c is None:return
    _keys(c,{'inventory_complete','enumeration_normal','modifiers','raw_read','range_read','cache_store_normal'})
    for k in ('inventory_complete','enumeration_normal','cache_store_normal'):_tri(c[k])
    if type(c['modifiers']) is not list or len(c['modifiers'])>100:raise ValueError('有序修饰器最多100项。')
    mids=set()
    for m in c['modifiers']:
        _keys(m,{'id','registered','exists','get_value_normal','included','basis','cache_values','flower_load'})
        _new(m['id'],mids)
        for k in ('registered','exists','get_value_normal','included'):_tri(m[k])
        if m['basis']!='independent_cache' or m['flower_load'] is not None:raise ValueError('SP修饰只使用独立四桶缓存，不能借用HP三花。')
        _keys(m['cache_values'],FIELDS)
        for value in m['cache_values'].values():_raw(value)
    _keys(c['raw_read'],{'normal','raw'});_tri(c['raw_read']['normal']);_raw(c['raw_read']['raw'])
    rr=c['range_read'];_keys(rr,{'normal','override','metadata_range_matches','lower_raw','upper_raw'})
    for k in ('normal','override','metadata_range_matches'):_tri(rr[k])
    _raw(rr['lower_raw']);_raw(rr['upper_raw'])
    if rr['override'] is False and (rr['lower_raw'] is not None or rr['upper_raw'] is not None):raise ValueError('不覆盖范围不能额外填界值。')

def _validate(p):
    _keys(p,{'readings','rate_reads','initializations','notifications'});seen=set()
    for key,limit in (('readings',40),('rate_reads',20),('initializations',10),('notifications',10)):
        if type(p[key]) is not list or len(p[key])>limit:raise ValueError('列表超出支持范围。')
    if not any(p.values()):raise ValueError('至少需要一个声明。')
    for r in p['readings']:_reading(r,seen)
    readings={r['id']:r for r in p['readings']};used=set()
    def link(rid,attribute):
        _id(rid)
        if rid not in readings or readings[rid]['attribute']!=attribute:raise ValueError('读取身份不存在或属性不符。')
        if rid in used:raise ValueError('不同getter访问不得复用一次读取身份。')
        used.add(rid)
    for r in p['rate_reads']:
        _keys(r,{'id','ordinary_native_path','first_attributes_getter_normal','second_attributes_getter_normal',
                 'flat_read_id','ratio_read_id','same_entity','unchanged_to_point','multiply_normally'})
        _new(r['id'],seen)
        for k in ('ordinary_native_path','first_attributes_getter_normal','second_attributes_getter_normal','same_entity','unchanged_to_point','multiply_normally'):_tri(r[k])
        link(r['flat_read_id'],14);link(r['ratio_read_id'],30)
    for a in p['initializations']:
        _keys(a,{'id','ordinary_native_path','attributes_read','sp_data_read','increments_read','slot0_read',
                 'single_conversion_normally','raw_array_read','raw_encoder_normally','raw_store_normally',
                 'mark_dirty_returns_normally','refresh_read_id','refresh_same_attributes','refresh_unchanged_to_point'})
        _new(a['id'],seen)
        for k in ('ordinary_native_path','single_conversion_normally','raw_encoder_normally','raw_store_normally',
                  'mark_dirty_returns_normally','refresh_same_attributes','refresh_unchanged_to_point'):_tri(a[k])
        for k in ('attributes_read','sp_data_read'):_pointer(a[k],seen)
        for k in ('increments_read','raw_array_read'):_pointer(a[k],seen,True)
        _keys(a['slot0_read'],{'id','normal','bits'});_new(a['slot0_read']['id'],seen)
        _tri(a['slot0_read']['normal']);_integer(a['slot0_read']['bits'],0,(1<<32)-1)
        link(a['refresh_read_id'],14)
    rates={r['id']:r for r in p['rate_reads']};used_rates=set()
    for a in p['notifications']:
        _keys(a,{'id','attribute','old_value_raw','ordinary_native_path','entity_exists','controller_read',
                 'new_rate_id','can_recover_rate_id','ordinary_controller_update_path','controller_matches_clock',
                 'precise_timer_identity','no_intervening_timer_changes','timer','drain'})
        _new(a['id'],seen)
        if type(a['attribute']) is not int or a['attribute'] not in (14,30):raise ValueError('通知只支持已证14/30分支。')
        _raw(a['old_value_raw']);_pointer(a['controller_read'],seen)
        for k in ('ordinary_native_path','entity_exists','ordinary_controller_update_path','controller_matches_clock',
                  'precise_timer_identity','no_intervening_timer_changes'):_tri(a[k])
        _keys(a['timer'],{'exists','period_raw','remaining_raw'});_tri(a['timer']['exists'])
        _raw(a['timer']['period_raw']);_raw(a['timer']['remaining_raw'])
        for key in ('new_rate_id','can_recover_rate_id'):
            rid=a[key]
            if rid is None and key=='can_recover_rate_id':continue
            _id(rid)
            if rid not in rates or rid in used_rates:raise ValueError('每次rate getter需要独立身份。')
            used_rates.add(rid)
        if a['drain'] is not None:
            # Shape-only validation is fixed274 and independent of source validity.
            _validate_drain(a['drain'])

def _validate_drain(a):
    _keys(a,{'id','kind','ordinary_native_path','delta_raw','enabled','gate_stop','full_read','recovery'})
    _id(a['id'])
    if a['kind']!='tick' or a['delta_raw']!=0 or type(a['delta_raw']) is not int:raise ValueError('dirty通知drain必须OnTick(0)。')
    _tri(a['ordinary_native_path']);_tri(a['enabled'])
    if len(a['id'])>60 or a['id']=='sp282.reconfigure':raise ValueError('drain身份须符合274并与固定动作不同。')
    for key,field in (('gate_stop','stop'),('full_read','full')):
        r=a[key];_keys(r,{'exists','normal','value'} if field=='stop' else {'normal','value'})
        if field=='stop':_tri(r['exists'])
        _tri(r['normal']);_tri(r['value'])
    r=a['recovery'];_keys(r,{'ordinary_native_path','force','stop_read','sp_read','setter_returns_normally'})
    if r['force'] is not False:raise ValueError('自然drain固定force=false。')
    _tri(r['ordinary_native_path']);_tri(r['setter_returns_normally'])
    for name,field in (('stop_read','value'),('sp_read','raw')):
        s=r[name];_keys(s,{'exists','normal',field});_tri(s['exists']);_tri(s['normal'])
        (_tri if field=='value' else _raw)(s[field])

def _and(*v):return False if False in v else None if None in v else True
class _Flow:
    def __init__(self,names,valid,ordinary):
        self.stages=[{'name':n,'called':None,'normal':None,'reference':None} for n in names]
        self.normal=True if valid and ordinary is True else None
        self.status='unqualified_source_or_ordinary_path' if self.normal is None else 'prefix'
    def run(self,name,normal,reference=None):
        s=next(v for v in self.stages if v['name']==name)
        if self.normal is not True:
            s['called']=False if self.normal is False else None;return False
        s.update(called=True,normal=normal,reference=deepcopy(reference))
        if normal is not True:self.normal=normal;self.status='failed_'+name if normal is False else 'unknown_'+name
        return normal is True
    def finish(self):
        for s in self.stages:
            if s['called'] is None and self.normal is False:s['called']=False
        return self.stages

def _array_guard(a,index):
    if a['exists'] is False:return False
    if a['exists'] is None or a['length'] is None:return None
    return index<a['length']
def _attribute_rows(p,valid):
    default={'default_ranges':{'14':{'min_raw':0,'max_raw':MAX_RAW-1},'30':{'min_raw':0,'max_raw':MAX_RAW-1}}}
    legacy=_modules()['attributes'] if valid else None
    rows=[]
    for r in p['readings']:
        if valid:rows.append(legacy._reading(deepcopy(r),default))
        else:rows.append({'id':r['id'],'attribute':r['attribute'],'normal_return_reference':None,'getter_raw_reference':None,
                         'dirty_cleared_reference':None,'cache_write_value_argument_raw_reference':None,'status':'unqualified_source'})
    return rows

def _rate_rows(p,attrs,valid):
    out=[];by_id={r['id']:r for r in attrs}
    for r in p['rate_reads']:
        f=_Flow(RATE_STAGES,valid,r['ordinary_native_path']);value=None
        if f.run('first_attributes_getter',r['first_attributes_getter_normal']):
            flat=by_id[r['flat_read_id']]
            if f.run('flat_read',flat['normal_return_reference'],{'read_id':flat['id'],'raw':flat['getter_raw_reference']}):
                if f.run('second_attributes_getter',r['second_attributes_getter_normal']):
                    ratio=by_id[r['ratio_read_id']]
                    if f.run('ratio_read',ratio['normal_return_reference'],{'read_id':ratio['id'],'raw':ratio['getter_raw_reference']}):
                        binding=r['same_entity'] is True and r['unchanged_to_point'] is True
                        if f.run('multiply',r['multiply_normally'],{'flat_read_id':flat['id'],'ratio_read_id':ratio['id'],'binding_qualified':binding}):
                            a,b=flat['getter_raw_reference'],ratio['getter_raw_reference']
                            if binding:
                                if a==0 or b==0:value=0
                                elif a is not None and b is not None:
                                    from .mechanist_explosion_math import multiply
                                    value=multiply(a,b)
                            f.status='normal_rate_reference' if binding else 'unqualified_rate_identity'
        out.append({'id':r['id'],'stages':f.finish(),'normal':f.normal,'rate_raw_reference':value,
                    'binding_qualified':valid and r['same_entity'] is True and r['unchanged_to_point'] is True,
                    'flat_read_id':r['flat_read_id'],'ratio_read_id':r['ratio_read_id'],'status':f.status})
    return out

def _initialization(a,attrs,valid):
    f=_Flow(INIT_STAGES,valid,a['ordinary_native_path']);stored=[];converted=None;refresh=None
    def run():
        nonlocal converted,refresh
        if not f.run('attributes_read',a['attributes_read']['normal'],deepcopy(a['attributes_read'])):return
        if not f.run('sp_data_access',_and(a['sp_data_read']['normal'],a['sp_data_read']['exists']),deepcopy(a['sp_data_read'])):return
        if not f.run('increments_read',a['increments_read']['normal'],deepcopy(a['increments_read'])):return
        if not f.run('increments_guard',_array_guard(a['increments_read'],0),{'index':0,'length':a['increments_read']['length']}):return
        if not f.run('slot0_read',a['slot0_read']['normal'],deepcopy(a['slot0_read'])):return
        if a['single_conversion_normally'] is True:
            conversion=_modules()['increments'].single_increment_reference(a['slot0_read']['bits'])
            converted=None if conversion is None else conversion['raw_reference']
        if not f.run('single_conversion',a['single_conversion_normally'],{'input_bits':a['slot0_read']['bits'],'fp_argument_raw':converted}):return
        if not f.run('attributes_guard',a['attributes_read']['exists']):return
        if not f.run('raw_array_capture',a['raw_array_read']['normal'],deepcopy(a['raw_array_read'])):return
        if not f.run('raw_encode',a['raw_encoder_normally'],{'argument_raw':converted,'payload_value':None}):return
        if not f.run('raw_array_guard',_array_guard(a['raw_array_read'],14),{'index':14,'length':a['raw_array_read']['length']}):return
        if not f.run('raw_store',a['raw_store_normally'],{'field':'rawData[14]','byte_count':40,'decoded_value':None}):return
        stored.append({'field':'rawData[14]','byte_count':40,'payload_identity':None,'decoded_value':None})
        if not f.run('mark_dirty',a['mark_dirty_returns_normally'],{'attribute':14,'partial_mask_state':None,'callback_target':None}):return
        bound=a['refresh_same_attributes'] is True and a['refresh_unchanged_to_point'] is True
        ref=attrs[a['refresh_read_id']]
        refresh=deepcopy(ref) if bound else None
        if f.run('refresh',ref['normal_return_reference'] if bound else None,{'read_id':a['refresh_read_id'],'binding_qualified':bound,'reading_reference':refresh}):f.status='raw14_and_refresh_prefix_complete'
    run()
    return {'id':a['id'],'kind':'initial_slot0','stages':f.finish(),'normal':f.normal,'status':f.status,
            'stored_prefix':stored,'slot0_fp_argument_raw_reference':converted,'refresh_reference':refresh,
            'raw_value_after':None,'cache_value_after':None,'clock_request':None,'clock_reference':None,
            **{k:None for k in UNKNOWNS}}

def _notification(a,rates,declared_rates,attrs,declared_attrs,valid):
    f=_Flow(NOTIFY_STAGES,valid,a['ordinary_native_path']);request=clock=new=snapshot=None
    def run():
        nonlocal request,clock,new,snapshot
        if not f.run('entity_access',a['entity_exists']):return
        if not f.run('controller_capture',a['controller_read']['normal'],deepcopy(a['controller_read'])):return
        new=rates[a['new_rate_id']]
        if not f.run('new_rate',new['normal'],deepcopy(new)):return
        if not f.run('controller_guard',a['controller_read']['exists']):return
        native=a['ordinary_controller_update_path']
        # A false ordinary flag means a different/unknown body, not a native exception.
        if native is not True:
            f.run('controller_update',None,{'ordinary_controller_update_path':native});return
        qualified=a['controller_matches_clock'] is True and new['binding_qualified'] is True
        if not qualified:
            f.run('controller_update',None,{'identity_qualified':False});return
        can_id=a['can_recover_rate_id']
        if can_id is not None:
            can=rates[can_id];decl=declared_rates[can_id]
            flat,ratio=attrs[decl['flat_read_id']],attrs[decl['ratio_read_id']]
            if can['binding_qualified']:
                snapshot={'ordinary_native_path':True,
                    'attributes_exist':_and(declared_attrs[flat['id']]['attributes_exist'],declared_attrs[ratio['id']]['attributes_exist']),
                    'reads_return_normally':can['normal'],'attr14_raw':flat['getter_raw_reference'],'attr30_raw':ratio['getter_raw_reference']}
        request={'controller_exists':True,'precise_timer_identity':a['precise_timer_identity'],
                 'no_intervening_timer_changes':a['no_intervening_timer_changes'],'timer':deepcopy(a['timer']),
                 'actions':[{'id':'sp282.reconfigure','kind':'reconfigure','ordinary_native_path':True,
                    'rate_input_raw':new['rate_raw_reference'],'drain':deepcopy(a['drain']),'can_recover_rate':snapshot}]}
        clock=_modules()['clock'].sp_recovery_clock_reference(deepcopy(request))
        f.run('controller_update',clock['normal_return_reference'],{'source_body':'inline_UpdateSpRecoveryPerSec',
               'old_value_used_by_ordinary_body':False,'new_rate_id':new['id'],'new_rate_raw':new['rate_raw_reference']})
        if f.normal is True:f.status='dirty_rate_timer_prefix_complete'
    run()
    return {'id':a['id'],'kind':'dirty_notification','attribute':a['attribute'],'stages':f.finish(),
            'normal':f.normal,'status':f.status,'stored_prefix':[],
            'new_rate_reference':deepcopy(new),'can_recover_snapshot_reference':deepcopy(snapshot),
            'clock_request':request,'clock_reference':clock,**{k:None for k in UNKNOWNS}}

def sp_recovery_attribute_reference(payload):
    _validate(payload);source=source_data();valid=source['valid']
    # Old helpers have their own sources; fresh outer binding covers their full
    # public artifacts and code before they can execute even cached code objects.
    readings=_attribute_rows(payload,valid);rates=_rate_rows(payload,readings,valid)
    ar={r['id']:r for r in readings};rr={r['id']:r for r in rates}
    dr={r['id']:r for r in payload['rate_reads']};da={r['id']:r for r in payload['readings']}
    rows=[_initialization(a,ar,valid) for a in payload['initializations']]
    rows += [_notification(a,rr,dr,ar,da,valid) for a in payload['notifications']]
    result={'source_valid':valid,'source_file':'research/p2-sp-recovery-attributes-282/source-proof.json',
            'readings':readings,'rate_reads':rates,'rows':rows,**{k:None for k in UNKNOWNS},
            'events_scheduled':False,'hotfix_equivalence_proven':False,
            'scope':'Independent declared SP14/30 and source prefixes, never actual cache/timer/SP or a full cycle.'}
    if valid and not source_data()['valid']:
        # No partial references survive an invalidated binding across this call.
        return _invalid_result(payload)
    return result

def _invalid_result(p):
    attrs=_attribute_rows(p,False);rates=_rate_rows(p,attrs,False)
    ar={r['id']:r for r in attrs};rr={r['id']:r for r in rates}
    rows=[_initialization(a,ar,False) for a in p['initializations']]
    rows += [_notification(a,rr,{},ar,{},False) for a in p['notifications']]
    return {'source_valid':False,'source_file':'research/p2-sp-recovery-attributes-282/source-proof.json',
            'readings':attrs,'rate_reads':rates,'rows':rows,**{k:None for k in UNKNOWNS},
            'events_scheduled':False,'hotfix_equivalence_proven':False,'scope':'Source binding unavailable.'}

def public_example():
    return json.loads((SOURCE_DIRECTORY/'public-example.json').read_text(encoding='utf8'))
