"""Change-specific author checks over public literals; no game/native execution."""
import copy,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from rouge import sp_recovery_attribute_reference as m
Q=1<<32;checks=[]
def ok(name,value):
    assert value,name
    checks.append(name)
def public():return m.public_example()
def report(p):return m.sp_recovery_attribute_reference(p)
def stage(row,name):return next(s for s in row['stages'] if s['name']==name)
def init(p):return report(p)['rows'][0]
def notify(p):return report(p)['rows'][-1]
def reading(p,name):return next(r for r in p['readings'] if r['id']==name)
def actuals(r):return all(r[k] is None for k in m.UNKNOWNS)
core=HERE/'rouge/sp_recovery_attribute_reference.py';before=hashlib.sha256(core.read_bytes()).hexdigest()
p=public();unchanged=copy.deepcopy(p);r=report(p)
ok('bound_public_sources',m.source_data()['valid'])
ok('input_not_mutated',p==unchanged)
ok('slot0_1_5_raw_parameter',r['rows'][0]['slot0_fp_argument_raw_reference']==6442450944)
ok('40byte_payload_stays_opaque',r['rows'][0]['stored_prefix']==[{'field':'rawData[14]','byte_count':40,'payload_identity':None,'decoded_value':None}])
ok('refresh_is_independent7_not1_5',r['rows'][0]['refresh_reference']['getter_raw_reference']==7*Q)
ok('ratio_default_not_upper_one',next(x for x in r['readings'] if x['id']=='ratio-over-one')['getter_raw_reference']==3*Q)
ok('negative_raw_default_clamp0',next(x for x in r['readings'] if x['id']=='negative14')['getter_raw_reference']==0)
c=r['rows'][1]['clock_reference']
ok('independent_new2_vs_can1',r['rows'][1]['new_rate_reference']['rate_raw_reference']==2*Q and c['rows'][0]['can_recover']['rate_raw_reference']==Q)
ok('keep_past_literal_quarter',c['final_period_raw_reference']==Q//2 and c['final_remaining_raw_reference']==Q//4)
ok('all_actual_states_unknown',actuals(r) and all(actuals(x) for x in r['rows']))
p=public();p['initializations'][0]['attributes_read']['exists']=False;x=init(p)
ok('null_attributes_after_conversion',x['normal'] is False and stage(x,'single_conversion')['called'] is True and stage(x,'raw_array_capture')['called'] is False)
p=public();p['initializations'][0]['raw_array_read']['exists']=False;x=init(p)
ok('encoder_before_null_array',stage(x,'raw_encode')['called'] is True and stage(x,'raw_array_guard')['normal'] is False and not x['stored_prefix'])
p=public();p['initializations'][0]['raw_array_read']['length']=14;x=init(p)
ok('encoder_before_unsigned_index14_bounds',stage(x,'raw_encode')['called'] is True and x['normal'] is False and stage(x,'raw_store')['called'] is False)
for val in (False,None):
    p=public();p['initializations'][0]['mark_dirty_returns_normally']=val;x=init(p)
    ok('stored_prefix_survives_mark_'+str(val),len(x['stored_prefix'])==1 and x['normal'] is val and stage(x,'refresh')['called'] is (False if val is False else None))
p=public();reading(p,'init.refresh14')['calculation']['cache_store_normal']=False;x=init(p)
ok('refresh_failure_retains_raw_store',len(x['stored_prefix'])==1 and x['normal'] is False)
p=public();p['initializations'][0]['slot0_read']['bits']=0xbf800000;x=init(p)
ok('negative_slot_encoder_not_zero_clamped',x['slot0_fp_argument_raw_reference']==-Q and x['normal'] is True)
p=public();p['initializations'][0]['slot0_read']['bits']=None;x=init(p)
ok('unknown_slot_normal_opaque_copy',x['normal'] is True and x['slot0_fp_argument_raw_reference'] is None and len(x['stored_prefix'])==1)
p=public();p['initializations'][0]['raw_encoder_normally']=None;x=init(p)
ok('unknown_encode_future_null',x['normal'] is None and stage(x,'raw_array_guard')['called'] is None and not x['stored_prefix'])
p=public();p['notifications'][0]['controller_read']['exists']=False;x=notify(p)
ok('new_rate_before_controller_null_guard',stage(x,'new_rate')['called'] is True and x['new_rate_reference']['rate_raw_reference']==2*Q and stage(x,'controller_update')['called'] is False)
p=public();p['notifications'][0]['attribute']=14;x=notify(p)
ok('dirty14_same_proven_body',x['normal'] is True and x['clock_reference']['final_remaining_raw_reference']==Q//4)
p=public();reading(p,'can14')['decoded_cache']['raw']=0;x=notify(p)
ok('eligibility_zero_marks_invalid_not_new_rate',x['clock_reference']['final_period_raw_reference']==-Q and x['clock_reference']['final_remaining_raw_reference']==-Q)
p=public();p['notifications'][0]['timer']['period_raw']=-Q;p['notifications'][0]['can_recover_rate_id']=None;p['notifications'][0]['drain']=None;x=notify(p)
ok('invalid_timer_skips_can_and_drain',x['normal'] is True and x['clock_reference']['rows'][0]['can_recover'] is None and x['clock_reference']['rows'][0]['drain'] is None and x['clock_reference']['final_remaining_raw_reference']==Q//2)
p=public();p['notifications'][0]['old_value_raw']=-123*Q;x=notify(p)
ok('old_value_unused_ordinary',x['normal'] is True and x['clock_reference']['final_period_raw_reference']==Q//2)
p=public();reading(p,'new14')['calculation']['raw_read']['raw']=0;reading(p,'new30')['calculation']['raw_read']['raw']=None;x=notify(p)
ok('normal_zero_times_unknown_closes_zero',x['new_rate_reference']['rate_raw_reference']==0)
p=public();p['rate_reads'][0]['second_attributes_getter_normal']=False;x=notify(p)
ok('second_attributes_getter_failure',stage(x,'new_rate')['normal'] is False and stage(x,'controller_guard')['called'] is False)
p=public();p['rate_reads'][0]['first_attributes_getter_normal']=None;x=report(p)['rate_reads'][0]
ok('unknown_first_getter_future_null',x['normal'] is None and stage(x,'flat_read')['called'] is None)
p=public();p['notifications'][0]['ordinary_controller_update_path']=False;x=notify(p)
ok('different_controller_body_is_unknown_not_failure',x['normal'] is None and x['clock_reference'] is None)
p=public();p['notifications'][0]['controller_matches_clock']=None;x=notify(p)
ok('unknown_timer_identity_no_forced_bridge',x['normal'] is None and x['clock_request'] is None)
p=public();reading(p,'new14')['calculation']['inventory_complete']=False;x=notify(p)
ok('incomplete_inventory_total_unknown',x['new_rate_reference']['rate_raw_reference'] is None)
for name,mut in [('public_source_override',lambda p:p.update(data={})),
 ('HP_recipe_rejected',lambda p:reading(p,'new14')['calculation']['modifiers'].append({'id':'bad','registered':True,'exists':True,'get_value_normal':True,'included':True,'basis':'flower_load','cache_values':None,'flower_load':{}})),
 ('reuse_getter_read_rejected',lambda p:p['rate_reads'][1].update(flat_read_id='new14'))]:
    p=public();mut(p)
    try:report(p)
    except ValueError:ok(name,True)
    else:raise AssertionError(name)
ok('core_bytes_unchanged',hashlib.sha256(core.read_bytes()).hexdigest()==before)
receipt={'status':'passed','checks':len(checks),'names':checks,'core_sha256':before,
         'file_only':True,'game_dll_executed':False,'process_memory_read':False,'section282_complete':False}
(HERE/'author-necessary-checks-282.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':'passed','checks':len(checks),'core_sha256':before}))
