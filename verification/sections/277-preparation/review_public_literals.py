"""Necessary277 draft source/control probes, not a full test run."""
from copy import deepcopy
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import rouge
rouge.__path__.insert(0,str(ROOT/'.cache/section277-draft/rouge'))
from rouge import skill_sp_cost_reference as module
HERE=Path(__file__).resolve().parent
core=Path(module.__file__).read_bytes()
original=(HERE/'core-before.py').read_bytes()
if core!=original:raise RuntimeError('The sealed first source differs before review probes.')
cases=[]
def probe(name,payload,expect):
    output=module.skill_sp_cost_reference(deepcopy(payload))
    checks=[]
    for path,value in expect.items():
        actual=output
        for key in path.split('.'):
            actual=actual[int(key)] if type(actual) is list else actual[key]
        checks.append({'path':path,'expected':value,'actual':actual,
                       'passed':type(actual) is type(value) and actual==value})
    cases.append({'name':name,'input':payload,'actual_output':output,'checks':checks,
                  'passed':output['source']['valid'] is True and all(c['passed'] for c in checks)})
def single(index):
    p=module.public_example();p['actions']=[p['actions'][index]];return p
probe('public literal admission and independent payment requests',module.public_example(),{
    'rows.2.result_reference':True,'rows.3.normal':True,'rows.3.result_reference':False,
    'rows.4.result_reference':False,'rows.6.result_reference':True,
    'rows.7.result_reference':True,'rows.8.result_reference':True,
    'rows.9.modifier_constructor_arguments.magnitude_raw':9223372036854775806})
p=single(2);p['actions'][0]['first_min_read']['value']=5
p['actions'][0]['second_min_read']['value']=7
probe('second min replaces rather than floors cost',p,{
    'rows.0.arithmetic_reference.threshold_int32':7,'rows.0.result_reference':False,
    'rows.0.stages.3.called':False,'rows.0.stages.6.called':False})
p=single(2);a=p['actions'][0];a['first_min_read']['value']=-1
a['free_read']['value']=False;a['decoded_cost_read']['value']=2;a['second_min_read']['value']=100
probe('negative first min selects independently decoded data cost',p,{
    'rows.0.arithmetic_reference.threshold_int32':2,'rows.0.result_reference':True,
    'rows.0.stages.6.called':True,'rows.0.stages.7.called':False})
for raw,result in ((21474793530,False),(21474793531,True)):
    p=single(2);p['actions'][0]['sp_read']['raw']=raw
    probe('strict EPS boundary '+str(raw),p,{
        'rows.0.arithmetic_reference.comparison_rhs_raw':21474793530,
        'rows.0.result_reference':result})
p=single(2);a=p['actions'][0];a['first_min_read']['value']=0
a['second_min_read']['value']=-2147483648;a['sp_read']['raw']=9223372036854775807
probe('MIN32 threshold subtraction wraps signed64',p,{
    'rows.0.arithmetic_reference.threshold_raw':-9223372036854775808,
    'rows.0.arithmetic_reference.comparison_rhs_raw':9223372036854732858,
    'rows.0.result_reference':True})
p=single(2);a=p['actions'][0];a['unity_null_read']['value']=True
probe('Unity-invalid initial owner completes false without SP read',p,{
    'rows.0.normal':True,'rows.0.result_reference':False,
    'rows.0.stages.2.called':False,'rows.0.stages.5.called':False})
p=single(2);p['actions'][0]['sp_owner_read']['exists']=False
probe('independent second SP owner missing stops before getter',p,{
    'rows.0.normal':False,'rows.0.stages.4.called':True,'rows.0.stages.5.called':False})
for key in ('free_read','skip_virtual_read'):
    p=single(3);p['actions'][0][key]['value']=None
    probe('unknown skip leaves future calls unknown '+key,p,{
        'rows.0.normal':None,'rows.0.stages.2.called':None,
        'rows.0.stages.3.called':None,'rows.0.stages.6.called':None})
p=single(3);p['actions'][0]['delta']=0
probe('zero delta skips all getters and calls',p,{
    'rows.0.normal':True,'rows.0.result_reference':True,
    'rows.0.stages.0.called':False,'rows.0.stages.1.called':False,
    'rows.0.stages.2.called':False,'rows.0.stages.6.called':False})
p=single(3);p['actions'][0]['newsp_owner_read']['exists']=False
p['actions'][0]['newsp_owner_read']['identity']=None
probe('first null owner can be NewSp source and target without dereference',p,{
    'rows.0.modifier_constructor_arguments.source_exists':False,
    'rows.0.modifier_constructor_arguments.target_exists':False,
    'rows.0.stages.3.called':True,'rows.0.stages.5.called':True,'rows.0.stages.6.called':True,
    'rows.0.normal':True,'rows.0.result_reference':False})
p=single(3);p['actions'][0]['apply_owner_read']['exists']=False
probe('second null owner still precedes complete copy then blocks apply',p,{
    'rows.0.stages.4.called':True,'rows.0.stages.4.normal':True,
    'rows.0.stages.5.called':True,'rows.0.stages.5.normal':True,
    'rows.0.stages.5.reference.byte_count':136,'rows.0.stages.6.called':False,
    'rows.0.normal':False,'rows.0.result_reference':None})
for normal,called in ((False,False),(None,None)):
    p=single(3);p['actions'][0]['modifier_copy_returns_normally']=normal
    probe('failed or unknown copy preserves second owner read '+str(normal),p,{
        'rows.0.stages.4.called':True,'rows.0.stages.5.called':True,
        'rows.0.stages.6.called':called,'rows.0.normal':normal})
p=single(3);p['actions'][0]['newsp_ordinary_native_path']=None
probe('unknown NewSp body may return opaque modifier but not constructor fields',p,{
    'rows.0.modifier_constructor_arguments':None,'rows.0.stages.3.called':True,
    'rows.0.stages.3.normal':True,'rows.0.stages.5.called':True,
    'rows.0.apply_arguments.force':False,'rows.0.normal':True})
p=single(9)
probe('MIN32 NEG and FP Abs special preserve independent Apply false',p,{
    'rows.0.arithmetic_reference.negated_int32':-2147483648,
    'rows.0.arithmetic_reference.input_raw':-9223372036854775808,
    'rows.0.modifier_constructor_arguments.magnitude_raw':9223372036854775806,
    'rows.0.modifier_constructor_arguments.delta_type_value':2,
    'rows.0.modifier_constructor_arguments.target_type_value':1,
    'rows.0.modifier_constructor_arguments.player_side_value':0,
    'rows.0.normal':True,'rows.0.result_reference':False})
for case in cases:
    output=case['actual_output']
    for location in [output]+output['rows']:
        for key in ('actual_owner_sp_after','actual_cost_paid','actual_cast_success','complete_cycle'):
            if location[key] is not None:case['passed']=False
    for row in output['rows']:
        if row['modifier_constructor_arguments'] is not None:
            for key in ('returned_payload_fields','cancel_reason_mask'):
                if row['modifier_constructor_arguments'][key] is not None:case['passed']=False
unchanged=Path(module.__file__).read_bytes()==core and (HERE/'core-before.py').read_bytes()==original
report={'core_sha256':hashlib.sha256(core).hexdigest(),'draft_only':True,'not_a_completed_section':True,
        'source_binding':module.source_data(),'cases':cases,'probe_count':len(cases),
        'check_count':sum(len(c['checks']) for c in cases),'core_unchanged_during_probes':unchanged,
        'passed':unchanged and all(c['passed'] for c in cases),'game_dll_executed':False,
        'process_memory_read':False,'game_or_chat_operated':False,'qt_started':False,
        'source_review_facts':['Native threshold is replacement, not a minimum cost floor.',
          'ReduceSp zero/free/virtual guards precede NEG; two owner reads are separate.',
          'NewSp caller arguments precede second owner read and136-byte clone; nullcheck comes after clone.',
          'GE is strict signed > wrapped thresholdQ-EPS; MIN32 NEG wraps and AbsMIN64 returns FP.MaxValue.',
          'Boolean Apply result references do not establish paid cost, actual SP, cast or complete cycle.'],
        'substantive_findings':[{'case':c['name'],'failed_checks':[x for x in c['checks'] if not x['passed']]}
                               for c in cases if not c['passed']]}
out=HERE/'necessary-probes.json'
if out.exists():raise RuntimeError('Do not overwrite first probe record.')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'probes':len(cases),'checks':report['check_count'],
 'core_sha256':report['core_sha256'],'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'findings':report['substantive_findings']},ensure_ascii=False))
sys.exit(0 if report['passed'] else 1)
