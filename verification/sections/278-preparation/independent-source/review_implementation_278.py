"""Limited278 implementation review, public literals only; not broad regression."""
from copy import deepcopy
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from rouge import skill_data_cost_reference as module
HERE=Path(__file__).resolve().parent
core_path=Path(module.__file__);core=core_path.read_bytes()
sha=hashlib.sha256(core).hexdigest()
if sha!='7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a':
    raise RuntimeError('Frozen278 source identity changed before review.')
snapshot=HERE/'implementation-core-7cd8.py'
if snapshot.exists():raise RuntimeError('Do not overwrite first implementation source.')
snapshot.write_bytes(core)
cases=[]
def check(name,output,expected,*,payload=None,scope='public source-control declaration'):
    checks=[]
    for path,value in expected.items():
        actual=output
        for key in path.split('.'):
            actual=actual[int(key)] if type(actual) is list else actual[key]
        checks.append({'path':path,'expected':value,'actual':actual,
                       'passed':type(actual) is type(value) and actual==value})
    cases.append({'name':name,'input':payload,'actual_output':output,'scope':scope,
                  'checks':checks,'passed':all(x['passed'] for x in checks)})
def scalar(name,operation,cost,bits,expected):
    check(name,module.single_cost_reference(operation,cost,bits),expected,
          payload={'operation':operation,'cost':cost,'modifier_bits':bits},scope='isolated arithmetic only')
def single(index):
    p=module.public_example();p['actions']=[p['actions'][index]];return p
def action(name,payload,expected):
    output=module.skill_data_cost_reference(deepcopy(payload))
    check(name,output,expected,payload=payload)
    if output['source']['valid'] is not True:cases[-1]['passed']=False
    for location in [output]+output['rows']:
        if any(location[k] is not None for k in ('actual_cost_after','actual_sp_after','complete_cycle')):
            cases[-1]['passed']=False

scalar('exact fractional positive tie even', 'mul',3,0x3fc00000,{
    'cost_single_exact':True,'binary_operation_exact':True,'rounded_int32_reference':4})
scalar('exact fractional negative tie even without clamp','mul',-3,0x3fc00000,{
    'binary_operation_exact':True,'rounded_int32_reference':-4})
scalar('large exactly representable Int32 outside24bit blanket bound','mul',2147483520,0x3f800000,{
    'cost_single_exact':True,'rounded_int32_reference':2147483520})
scalar('MAX32 conversion stays unknown without defaultRN','mul',2147483647,0x3f800000,{
    'status':'int32_to_single_rounding_unknown','rounded_int32_reference':None})
scalar('inexact multiplication RC-disagreement example stays unknown','mul',10,0x3d4ccccd,{
    'status':'single_arithmetic_environment_or_rounding_unknown',
    'binary_operation_exact':False,'result_single_bits':None,'rounded_int32_reference':None})
scalar('subnormal modifier stays outside supported domain','mul',1,1,{
    'status':'modifier_subnormal_environment_unknown','rounded_int32_reference':None})
scalar('negativezero final integer common without claiming sign bits','mul',3,0x80000000,{
    'rounded_int32_reference':0,'result_single_bits':None})
scalar('exact positive2^31 does not wrap final conversion','mul',-2147483648,0xbf800000,{
    'status':'rounded_int32_conversion_domain_unknown','rounded_int32_reference':None})
check('low32 integer scaling does not saturate',module.signed_scale_reference(2147483647,2),{
    'product_int32_reference':-2},payload={'cost':2147483647,'scale':2},scope='isolated low32 arithmetic only')

p=single(9);p['actions'][0]['encode_normally']=False
action('replacement encode failure precedes knownNULL test',p,{
    'rows.0.stages.2.called':True,'rows.0.stages.2.normal':False,
    'rows.0.stages.3.called':False,'rows.0.stages.4.called':False,
    'rows.0.encoder_argument_reference':50,'rows.0.stored_prefixes':[],'rows.0.normal':False})
p=single(9)
action('replacement normal encode precedes completed comparison andNULL failure',p,{
    'rows.0.stages.2.normal':True,'rows.0.stages.3.called':True,
    'rows.0.stages.3.normal':True,'rows.0.stages.3.reference.exists':False,
    'rows.0.stages.4.called':False,'rows.0.normal':False})
p=single(7);p['actions'][0]['first_sp_data_read']['exists']=None
action('replacement pointerUnknown retains encode/comparison normality',p,{
    'rows.0.stages.2.normal':True,'rows.0.stages.3.normal':True,
    'rows.0.stages.4.called':None,'rows.0.normal':None})
p=single(6);p['actions'][0]['owner_read']['exists']=False
action('scale missing owner still reads secondData before raw check',p,{
    'rows.0.stages.8.called':True,'rows.0.stages.8.normal':True,
    'rows.0.stages.9.called':True,'rows.0.stages.9.normal':True,
    'rows.0.stages.10.called':False,'rows.0.stored_prefixes.0.byte_count':20,
    'rows.0.stored_prefixes.0.decoded_value':None,'rows.0.normal':False})
p=single(6);p['actions'][0]['second_data_read']['identity']='独立第二data'
p['actions'][0]['update_sp_data_identity']='第二data的独立spData参数'
action('scale update uses independent latest identity and onlycostTrue',p,{
    'rows.0.update_arguments.sp_data_identity':'第二data的独立spData参数',
    'rows.0.update_arguments.only_update_sp_cost':True,
    'rows.0.encoder_argument_reference':-2147483648,'rows.0.normal':True})
p=single(8);p['actions'][0]['type_value_read']['value']=None
action('unknown direct type store keeps prefix and onlycostFalse',p,{
    'rows.0.stored_prefixes.0.field':'spCost','rows.0.stored_prefixes.1.field':'spType',
    'rows.0.stored_prefixes.1.value':None,'rows.0.stages.9.called':True,
    'rows.0.stages.9.normal':True,'rows.0.update_arguments.only_update_sp_cost':False,
    'rows.0.normal':True})
p=single(8);p['actions'][0]['type_store_normally']=False
action('type-store exception retains completed cost prefix only',p,{
    'rows.0.stored_prefixes.0.field':'spCost','rows.0.stages.9.called':True,
    'rows.0.stages.9.normal':False,'rows.0.stages.10.called':False,
    'rows.0.stages.14.called':False,'rows.0.normal':False})
p=single(7);p['actions'][0]['modify_type_read']['value']=None
action('unknown modify flag leaves future callsUnknown and cost prefix intact',p,{
    'rows.0.stored_prefixes.0.byte_count':20,'rows.0.stages.6.called':None,
    'rows.0.stages.10.called':None,'rows.0.stages.14.called':None,
    'rows.0.update_arguments':None,'rows.0.normal':None})
p=single(7);p['actions'][0]['unity_truth_read']['value']=False
action('Unity false returns normally after cost-only store',p,{
    'rows.0.stages.10.normal':True,'rows.0.stages.11.normal':True,
    'rows.0.stages.12.called':False,'rows.0.stages.13.called':False,
    'rows.0.stages.14.called':False,'rows.0.normal':True})
p=single(7);p['actions'][0]['second_owner_read']['exists']=False
action('replacement missing second owner still reads thirdData',p,{
    'rows.0.stages.12.normal':True,'rows.0.stages.13.called':True,
    'rows.0.stages.13.normal':True,'rows.0.stages.14.called':False,'rows.0.normal':False})
p=single(7);p['actions'][0]['update_sp_data_identity']='第三data独立spData'
action('replacement cost-only latest data argument',p,{
    'rows.0.update_arguments.sp_data_identity':'第三data独立spData',
    'rows.0.update_arguments.only_update_sp_cost':True,'rows.0.normal':True})
p=single(0);p['actions'][0]['modifier_read']['found']=False
action('TryGetFloat false skips SPdata and numerical body',p,{
    'rows.0.stages.4.called':True,'rows.0.stages.5.called':False,
    'rows.0.stages.7.called':False,'rows.0.stages.11.called':False,'rows.0.normal':True})
p=single(0);p['actions'][0]['round_normally']=None
action('unknown rounding call normality leaves encode/storeUnknown',p,{
    'rows.0.stages.10.called':True,'rows.0.stages.10.normal':None,
    'rows.0.stages.11.called':None,'rows.0.stages.12.called':None,'rows.0.normal':None})
p=single(0);p['actions'][0]['store_normally']=False
action('failed20byte store does not claim completed field prefix',p,{
    'rows.0.encoder_argument_reference':12,'rows.0.stages.11.normal':True,
    'rows.0.stages.12.normal':False,'rows.0.stored_prefixes':[],'rows.0.normal':False})

invalid=single(0);invalid['source_data']={'valid':True}
try:
    module.skill_data_cost_reference(invalid)
except ValueError:
    injection_rejected=True
else:
    injection_rejected=False
source=module.source_data()
source_proof=module.SOURCE_DIRECTORY/'source-proof.json'
manifest=module.SOURCE_DIRECTORY/'source_manifest.json'
before_independent=json.loads((HERE/'cost-source-review.json').read_text(encoding='utf-8'))
unchanged=core_path.read_bytes()==core and snapshot.read_bytes()==core
report={'scope':'Limited implementation review of the explicitly restricted exactSingle and source-accurate cost-write/update prefix group. No RC interval expansion or broad test repetition.',
        'core_sha256':sha,'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'proof_sha256':hashlib.sha256(source_proof.read_bytes()).hexdigest(),
        'source_binding':source,'source_injection_rejected':injection_rejected,
        'prior_fresh_independent_source_review_sha256':hashlib.sha256((HERE/'cost-source-review.json').read_bytes()).hexdigest(),
        'prior_fresh_source_methods':before_independent['selected_method_count'],
        'prior_fresh_source_instructions':before_independent['unique_instruction_count'],
        'probe_count':len(cases),'check_count':sum(len(c['checks']) for c in cases),
        'cases':cases,'core_unchanged_during_review':unchanged,
        'passed':unchanged and source['valid'] and injection_rejected and all(c['passed'] for c in cases),
        'substantive_findings':[{'case':c['name'],'failed_checks':[x for x in c['checks'] if not x['passed']]}
                               for c in cases if not c['passed']],
        'game_dll_executed':False,'process_memory_read':False,'qt_started':False,
        'private_state_read':False,'game_or_chat_operated':False,
        'limitations':['Inexact or subnormal/nonfinite Single remains unknown by the supported contract.',
                       'Integer or encoded argument is not protected later decode or actualcost/SP/cycle.',
                       'Does not repeat92 related checks or the root-owned Windows fixture.']}
out=HERE/'implementation-review-278.json'
if out.exists():raise RuntimeError('Do not overwrite first implementation probe record.')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'probes':report['probe_count'],'checks':report['check_count'],
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'findings':report['substantive_findings']},ensure_ascii=False))
sys.exit(0 if report['passed'] else 1)
