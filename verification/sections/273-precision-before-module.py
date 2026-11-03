"""Qualified FP attribute13/19 getters, cache/recompute and independent clock links."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib,json
from .mechanist_explosion_math import ONE,MIN_RAW,MAX_RAW,add,multiply
from .regeneration_clock import regeneration_clock_reference

SOURCE='rouge/data/recovery-attribute-source.json'
SOURCE_SHA256='b4f230db97d41b8784f0fb9beab2b8a62a14560298e4878dcae9ccde257d2824'
FIELDS=('addition','multiplier_delta','final_addition','final_scaler')
NEUTRAL={'addition':0,'multiplier_delta':0,'final_addition':0,'final_scaler':ONE}


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
def _same(v):return v[0] if v[0] is not None and all(x==v[0] for x in v) else None
def _mul(a,b):return 0 if a==0 or b==0 else multiply(a,b)
def _tri(v):
    if v is not None and type(v) is not bool:raise ValueError('资格需要true、false或null。')
def _raw(v):
    if v is not None and (type(v) is not int or not MIN_RAW<=v<=MAX_RAW):raise ValueError('需要signed64 FP原值或null。')
def _id(v):
    if type(v) is not str or not 1<=len(v)<=60 or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in v):raise ValueError('身份需要1–60字符，不能含控制字符。')


def _validate(payload):
    if type(payload) is not dict or set(payload)!={'readings','clock_bridge'}:raise ValueError('需要readings与clock_bridge。')
    rows=payload['readings']
    if type(rows) is not list or not 1<=len(rows)<=40:raise ValueError('属性读取需要1–40个独立读点。')
    seen=set()
    for r in rows:
        if type(r) is not dict or set(r)!={'id','attribute','ordinary_native_path','attributes_exist','dirty','decoded_cache','calculation'}:raise ValueError('请使用完整属性读取声明。')
        _id(r['id'])
        if r['id'] in seen:raise ValueError('读取身份不能重复。')
        seen.add(r['id'])
        if type(r['attribute']) is not int or r['attribute'] not in (13,19):raise ValueError('仅核准常态回复属性13/19。')
        for k in ('ordinary_native_path','attributes_exist','dirty'):_tri(r[k])
        cache=r['decoded_cache']
        if type(cache) is not dict or set(cache)!={'normal','raw'}:raise ValueError('decoded_cache需要独立正常资格与解密后的FP原值。')
        _tri(cache['normal']);_raw(cache['raw'])
        c=r['calculation']
        if c is None:continue
        if type(c) is not dict or set(c)!={'inventory_complete','enumeration_normal','modifiers','raw_read','range_read','cache_store_normal'}:raise ValueError('重算需要完整库存、枚举、原值、范围与缓存写入资格。')
        for k in ('inventory_complete','enumeration_normal','cache_store_normal'):_tri(c[k])
        if type(c['modifiers']) is not list or len(c['modifiers'])>100:raise ValueError('有序修饰器最多100项，顺序不能自动排序。')
        mids=set()
        for m in c['modifiers']:
            keys={'id','registered','exists','get_value_normal','included','basis','cache_values','flower_load'}
            if type(m) is not dict or set(m)!=keys:raise ValueError('请使用完整独立修饰器声明。')
            _id(m['id'])
            if m['id'] in mids:raise ValueError('同一库存实例身份不能重复；不同实例可有相同藏品来源。')
            mids.add(m['id'])
            for k in ('registered','exists','get_value_normal','included'):_tri(m[k])
            if m['basis']=='independent_cache':
                v=m['cache_values']
                if m['flower_load'] is not None or type(v) is not dict or set(v)!=set(FIELDS):raise ValueError('独立缓存需要四桶，不能同时覆盖藏品加载。')
                for value in v.values():_raw(value)
            elif m['basis']=='flower_load':
                f=m['flower_load']
                keys={'relic_id','recipe_matches_bound','blackboard_exists','try_returns_normally','number_found','number_basis',
                    'number_matches_bound_parameter','number_raw','stack_count','cache_matches_completed_load','load_accesses_normal'}
                if m['cache_values'] is not None or type(f) is not dict or set(f)!=keys:raise ValueError('藏品加载不能混用独立缓存覆盖。')
                if f['relic_id'] not in ('rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83'):raise ValueError('仅三花已绑定来源。')
                for k in keys-{'relic_id','number_basis','number_raw','stack_count'}:_tri(f[k])
                if f['number_basis'] not in ('nominal_bound_float','independent_fp'):raise ValueError('黑板值依据需要独立FP或来源绑定名义float。')
                _raw(f['number_raw'])
                if f['number_basis']=='nominal_bound_float' and f['number_raw'] is not None:raise ValueError('名义参数不能另填raw覆盖。')
                if f['stack_count'] is not None and (type(f['stack_count']) is not int or not -(1<<31)<=f['stack_count']<(1<<31)):raise ValueError('stack_count需要signed32整数或null。')
            else:raise ValueError('修饰器basis需要independent_cache或flower_load。')
        for name in ('raw_read','range_read'):
            obj=c[name]
            keys={'normal','raw'} if name=='raw_read' else {'normal','override','metadata_range_matches','lower_raw','upper_raw'}
            if type(obj) is not dict or set(obj)!=keys:raise ValueError('原值/范围读取声明不完整。')
            _tri(obj['normal'])
            if name=='raw_read':_raw(obj['raw'])
            else:
                _tri(obj['override']);_tri(obj['metadata_range_matches']);_raw(obj['lower_raw']);_raw(obj['upper_raw'])
                if obj['override'] is False and (obj['lower_raw'] is not None or obj['upper_raw'] is not None):raise ValueError('不覆盖范围时不能另填上下界。')
    bridge=payload['clock_bridge']
    if bridge is None:return
    if type(bridge) is not dict or set(bridge)!={'input','links'} or type(bridge['links']) is not list:raise ValueError('clock_bridge需要272输入与独立链接。')
    used=set()
    for link in bridge['links']:
        if type(link) is not dict or set(link)!={'action_id','point','flat_read_id','ratio_read_id','max_hp_raw','max_hp_read_normal','same_entity','unchanged_to_point'}:raise ValueError('链接需要独立行动/读点及身份与未变资格。')
        if link['point'] not in ('can_recover_snapshot','period_snapshot'):raise ValueError('链接只作用于两个独立回复率读点。')
        for k in ('action_id','flat_read_id','ratio_read_id'):_id(link[k])
        if (link['action_id'],link['point']) in used:raise ValueError('同一行动读点不能覆盖两次。')
        used.add((link['action_id'],link['point']))
        for k in ('max_hp_read_normal','same_entity','unchanged_to_point'):_tri(link[k])
        _raw(link['max_hp_raw'])


def _flower(m,attribute,source):
    f=m['flower_load'];record=next(v for v in source['flower_channels'] if v['relic_id']==f['relic_id'] and v['attribute']==attribute)
    normal=_and(f['blackboard_exists'],f['try_returns_normally'],f['load_accesses_normal'])
    nominal=record['parameter_fp_raw'] if f['number_matches_bound_parameter'] is True else None
    number=nominal if f['number_basis']=='nominal_bound_float' else f['number_raw']
    value=0 if f['number_found'] is False else number if f['number_found'] is True else _same([0,number])
    stack=None if f['stack_count'] is None else f['stack_count']*ONE
    loaded=_mul(value,stack) if normal is True else None
    qualified=normal is True and f['recipe_matches_bound'] is True and f['cache_matches_completed_load'] is True
    values=NEUTRAL|{'multiplier_delta':loaded} if qualified else {k:None for k in FIELDS}
    return values,{'relic_id':f['relic_id'],'name':record['name'],'attribute':attribute,'source_buff_index':record['source_buff_index'],
        'load_normal_reference':normal,'loaded_multiplier_raw_reference':loaded,'cache_link_qualified':qualified,
        'default_zero_used_reference':f['number_found'] is False if normal is True else None}


def _aggregate(b,m,attribute,source):
    values,load=(m['cache_values'],None) if m['basis']=='independent_cache' else _flower(m,attribute,source)
    normal=_and(m['exists'],m['get_value_normal'])
    included=m['included'];registered=m['registered']
    applied={k:(_mul(b[k],values[k]) if k=='final_scaler' else add(b[k],values[k])) for k in FIELDS}
    if registered is False:result=deepcopy(b);overall=True;status='not_registered'
    elif normal is not True:
        overall=normal if registered is True else None;result={k:None for k in FIELDS};status='unqualified_get_value'
    elif included is False:result=deepcopy(b);overall=True;status='returned_false_not_aggregated'
    elif registered is True and included is True:result=applied;overall=True;status='included'
    else:result={k:_same([b[k],applied[k]]) for k in FIELDS};overall=True;status='unknown_membership_or_include'
    called=False if registered is False or m['exists'] is False else True if registered is True and m['exists'] is True else None
    return result,overall,{'id':m['id'],'status':status,'get_value_called_reference':called,
        'get_value_normal_reference':m['get_value_normal'] if called is True else None,
        'member_processing_normal_reference':overall,'flower_load':load,
        'cached_values_reference':values,'buckets_after_reference':deepcopy(result)}


def _clamp(v,lower,upper):
    # Native order is max(min(v,upper),lower), including reversed ranges.
    if lower is not None and upper is not None and lower>=upper:return lower
    first=None if v is None or upper is None else min(v,upper)
    return None if first is None or lower is None else max(first,lower)


def _recompute(r,source):
    c=r['calculation']
    out={'normal_return_reference':None,'getter_raw_reference':None,'computed_clamped_raw_reference':None,
        'dirty_cleared_reference':None,'cache_write_value_argument_raw_reference':None,'cache_store_normal_reference':None,
        'buckets_reference':None,'steps':[],'raw_read_called_reference':False,'range_read_called_reference':False,'status':'unqualified_calculation'}
    if c is None:return out
    buckets={'addition':0,'multiplier_delta':ONE,'final_addition':0,'final_scaler':ONE};normal=True
    for m in c['modifiers']:
        if normal is not True:
            out['steps'].append({'id':m['id'],'status':'not_called_after_unqualified_enumeration'});continue
        buckets,normal,step=_aggregate(buckets,m,r['attribute'],source);out['steps'].append(step)
    normal=_and(normal,c['enumeration_normal']);out['listed_buckets_reference']=deepcopy(buckets)
    out['buckets_reference']=deepcopy(buckets) if c['inventory_complete'] is True else {k:None for k in FIELDS}
    if normal is not True:
        out['normal_return_reference']=normal;out['dirty_cleared_reference']=False if normal is False else None
        out['status']='unqualified_enumeration';return out
    # Clearing the dirty bit precedes raw/range reads and encoding/cache store.
    out['dirty_cleared_reference']=True;out['raw_read_called_reference']=True
    raw=c['raw_read'];normal=raw['normal']
    if normal is not True:out['normal_return_reference']=normal;out['status']='unqualified_raw_read';return out
    subtotal=add(raw['raw'],buckets['addition']);mult=buckets['multiplier_delta']
    first=_mul(subtotal,None if mult is None else max(0,mult));second=add(first,buckets['final_addition'])
    listed_pre=_mul(second,buckets['final_scaler']);out['listed_pre_clamp_raw_reference']=listed_pre
    pre=listed_pre if c['inventory_complete'] is True else None;out['pre_clamp_raw_reference']=pre
    out['range_read_called_reference']=True;range_read=c['range_read'];normal=range_read['normal']
    if normal is not True:out['normal_return_reference']=normal;out['status']='unqualified_range_read';return out
    default=source['default_ranges'][str(r['attribute'])]
    if range_read['override'] is False:
        lower,upper=(default['min_raw'],default['max_raw']) if range_read['metadata_range_matches'] is True else (None,None)
    elif range_read['override'] is True:lower,upper=range_read['lower_raw'],range_read['upper_raw']
    else:
        lower=_same([default['min_raw'] if range_read['metadata_range_matches'] is True else None,range_read['lower_raw']])
        upper=_same([default['max_raw'] if range_read['metadata_range_matches'] is True else None,range_read['upper_raw']])
    value=_clamp(pre,lower,upper)
    out.update(lower_raw_reference=lower,upper_raw_reference=upper,computed_clamped_raw_reference=value,
        cache_write_value_argument_raw_reference=value,cache_store_normal_reference=c['cache_store_normal'],
        normal_return_reference=c['cache_store_normal'],getter_raw_reference=value if c['cache_store_normal'] is True else None,
        status='recomputed' if c['cache_store_normal'] is True else 'unqualified_cache_store')
    return out


def _reading(r,source):
    row={'id':r['id'],'attribute':r['attribute'],'normal_return_reference':None,'getter_raw_reference':None,
        'dirty_cleared_reference':None,'cache_write_value_argument_raw_reference':None,'status':'unqualified_source_or_instance'}
    if source is None or r['ordinary_native_path'] is not True:return row
    if r['attributes_exist'] is False:
        row.update(normal_return_reference=False,dirty_cleared_reference=False);return row
    if r['attributes_exist'] is None:
        present=_reading(r|{'attributes_exist':True},source)
        return row|{'normal_return_reference':_same([False,present['normal_return_reference']]),
            'dirty_cleared_reference':_same([False,present['dirty_cleared_reference']]),
            'status':'unknown_instance','present_instance_reference':present}
    clean={'normal_return_reference':r['decoded_cache']['normal'],
        'getter_raw_reference':r['decoded_cache']['raw'] if r['decoded_cache']['normal'] is True else None,
        'dirty_cleared_reference':False,'cache_write_value_argument_raw_reference':None,'status':'independent_decoded_cache'}
    if r['dirty'] is False:return row|clean
    dirty=_recompute(r,source)
    if r['dirty'] is True:return row|dirty
    return row|{'normal_return_reference':_same([clean['normal_return_reference'],dirty['normal_return_reference']]),
        'getter_raw_reference':_same([clean['getter_raw_reference'],dirty['getter_raw_reference']]),
        'dirty_cleared_reference':_same([False,dirty['dirty_cleared_reference']]),'status':'unknown_dirty_branch',
        'clean_reference':clean,'recompute_reference':dirty}


def recovery_attribute_reference(payload):
    _validate(payload);source=_source_data();rows=[_reading(r,source) for r in payload['readings']]
    by_id={r['id']:r for r in rows};declared={r['id']:r for r in payload['readings']};bridge=payload['clock_bridge'];clock=None;links=[]
    if bridge is not None:
        clock_input=deepcopy(bridge['input'])
        # Validate the complete272 contract before patching only empty snapshots.
        regeneration_clock_reference(clock_input)
        linked_read_ids=set()
        for link in bridge['links']:
            action=next((a for a in clock_input['actions'] if a['id']==link['action_id']),None)
            if action is None or action['kind']!='reconfigure':raise ValueError('链接需要明确272重设行动。')
            if action[link['point']] is not None:raise ValueError('已有独立快照不能被链接覆盖。')
            if link['flat_read_id'] not in by_id or link['ratio_read_id'] not in by_id:raise ValueError('链接需要存在的独立读取身份。')
            flat=by_id[link['flat_read_id']];ratio=by_id[link['ratio_read_id']]
            if flat['attribute']!=13 or ratio['attribute']!=19:raise ValueError('不能交换flat13与ratio19。')
            if flat['id'] in linked_read_ids or ratio['id'] in linked_read_ids:raise ValueError('每次getter访问需要独立读取身份，数值未变不能替代另一次正常返回资格。')
            linked_read_ids.update((flat['id'],ratio['id']))
            qualified=source is not None and link['same_entity'] is True and link['unchanged_to_point'] is True
            snapshot=None
            if qualified:
                snapshot={'attributes_exist':_and(declared[flat['id']]['attributes_exist'],declared[ratio['id']]['attributes_exist']),
                    'reads_return_normally':_and(flat['normal_return_reference'],ratio['normal_return_reference'],link['max_hp_read_normal']),
                    'flat_raw':flat['getter_raw_reference'],'ratio_raw':ratio['getter_raw_reference'],'max_hp_raw':link['max_hp_raw']}
            action[link['point']]=snapshot
            links.append({'action_id':link['action_id'],'point':link['point'],'qualified':qualified,'snapshot_reference':deepcopy(snapshot)})
        clock=regeneration_clock_reference(clock_input)
    return {'source_valid':source is not None,'rows':rows,'clock_links':links,'clock_reference':clock,
        'actual_attribute_values':None,'actual_cache_or_dirty_state':None,'actual_clock':None,'actual_hp_after':None,
        'actual_complete_healing':None,'events_scheduled':False,'hotfix_equivalence_proven':False,
        'scope':'Independent FP getter/source/cache/range declarations; no actual inventory, next cache decoding, callbacks, clock or HP settlement.'}


def public_example():
    from .regeneration_clock import public_example as clock_example
    rows=[]
    for point in ('first','period'):
        for attribute,base in ((13,10*ONE),(19,ONE//16)):
            mods=[]
            for suffix in (81,82,83):
                mods.append({'id':point+str(attribute)+'藏品'+str(suffix),'registered':True,'exists':True,'get_value_normal':True,
                    'included':True,'basis':'flower_load','cache_values':None,'flower_load':{
                    'relic_id':'rogue_6_relic_legacy_'+str(suffix),'recipe_matches_bound':True,'blackboard_exists':True,
                    'try_returns_normally':True,'number_found':True,'number_basis':'nominal_bound_float','number_matches_bound_parameter':True,
                    'number_raw':None,'stack_count':1,'cache_matches_completed_load':True,'load_accesses_normal':True}})
            rows.append({'id':point+str(attribute),'attribute':attribute,'ordinary_native_path':True,'attributes_exist':True,
                'dirty':True,'decoded_cache':{'normal':None,'raw':None},'calculation':{'inventory_complete':True,
                'enumeration_normal':True,'modifiers':mods,'raw_read':{'normal':True,'raw':base},
                'range_read':{'normal':True,'override':False,'metadata_range_matches':True,'lower_raw':None,'upper_raw':None},'cache_store_normal':True}})
    clock=clock_example();clock['actions']=clock['actions'][1:2];clock['actions'][0]['can_recover_snapshot']=None;clock['actions'][0]['period_snapshot']=None
    links=[{'action_id':clock['actions'][0]['id'],'point':name,'flat_read_id':prefix+'13','ratio_read_id':prefix+'19',
        'max_hp_raw':100*ONE,'max_hp_read_normal':True,'same_entity':True,'unchanged_to_point':True}
        for prefix,name in [('first','can_recover_snapshot'),('period','period_snapshot')]]
    return {'readings':rows,'clock_bridge':{'input':clock,'links':links}}
