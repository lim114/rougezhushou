"""Limited279 fixed-contract review over public literals; not a source re-audit."""
from copy import deepcopy
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import rouge
rouge.__path__.insert(0,str(ROOT/'.cache/section279-draft/rouge'))
from rouge import skill_sp_increment_reference as module
HERE=Path(__file__).resolve().parent
core_path=Path(module.__file__);core=core_path.read_bytes()
core_sha=hashlib.sha256(core).hexdigest()
if core_sha!='7b72bb8c2428476bfdbf283f1f1b40c0969d7c11459594e3eca4bbb22b6a55ec':
    raise RuntimeError('Frozen279 core changed before source/control review.')
snapshot=HERE/'implementation-core-7b72.py'
if snapshot.exists():raise RuntimeError('Do not overwrite first core snapshot.')
snapshot.write_bytes(core)
cases=[]
def inspect(name,output,expect,*,input,scope='public branch/prefix declarations'):
    checks=[]
    for path,value in expect.items():
        actual=output
        for key in path.split('.'):
            actual=actual[int(key)] if type(actual) is list else actual[key]
        checks.append({'path':path,'expected':value,'actual':actual,
                       'passed':type(actual) is type(value) and actual==value})
    cases.append({'name':name,'scope':scope,'input':input,'actual_output':output,
                  'checks':checks,'passed':all(c['passed'] for c in checks)})
def scalar(name,function,value,expect):
    inspect(name,function(value),expect,input={'bits':value},scope='isolated scalar reference only')
def single(index):
    p=module.public_example();p['actions']=[p['actions'][index]];return p
def probe(name,payload,expected):
    output=module.skill_sp_increment_reference(deepcopy(payload))
    inspect(name,output,expected,input=payload)
    if not output['source']['valid']:cases[-1]['passed']=False
    for location in [output]+output['rows']:
        if any(location[k] is not None for k in ('actual_array_after','actual_sp_after','complete_cycle')):
            cases[-1]['passed']=False
def stage(output,name):return next(x for x in output['rows'][0]['stages'] if x['name']==name)

for bits,result in ((0xb727c5ac,True),(0xb727c5ad,False),(0xb727c5ab,True),(0x80000000,True)):
    scalar('inclusive SingleGE boundary '+hex(bits),module.single_ge_zero_reference,bits,{
        'adjusted_rhs_bits':3072837036,'ge_boolean_reference':result})
for bits,raw in ((0xcf000000,-9223372036854775808),(0x4f000000,None),(0x2f000000,0),
                 (0xaf000000,0),(0x40200000,10737418240)):
    scalar('Single scaling/truncation '+hex(bits),module.single_increment_reference,bits,{'raw_reference':raw})

p=single(0);p['actions'][0]['inited_read']['value']=True
p['actions'][0]['array_allocation']['normal']=False
probe('inited true skips every later allocation/slot stage',p,{
    'rows.0.normal':True,'rows.0.stages.2.called':False,'rows.0.stored_prefixes':[],
    'rows.0.slot_references':[]})
p=single(0);p['actions'][0]['inited_read']['value']=None
probe('unknown inited cannot prove future uncalled',p,{
    'rows.0.normal':None,'rows.0.stages.2.called':None,'rows.0.stored_prefixes':[]})
p=single(0)
probe('captured BBnull makes four fallback defaults without enabling bits',p,{
    'rows.0.normal':True,'rows.0.slot_references.0.value_source':'default_one',
    'rows.0.slot_references.0.value_bits':1065353216,
    'rows.0.slot_references.3.value_bits':1065353216,
    'rows.0.stored_prefixes.1.index':0,'rows.0.stored_prefixes.4.index':3})
out=cases[-1]['actual_output']
for index in range(4):
    if stage(out,'s'+str(index)+'.lookup')['called'] is not False:cases[-1]['passed']=False

p=single(1);a=p['actions'][0]
a['slots'][0]['lookup']['bits']=None;a['slots'][0]['mask_read']['value']=None
probe('lookup success supports unknown mask BTS and unknown direct bits',p,{
    'rows.0.normal':True,'rows.0.stored_prefixes.1.field':'spType',
    'rows.0.stored_prefixes.1.value':None,'rows.0.stored_prefixes.1.known_set_bit':1,
    'rows.0.stored_prefixes.2.bits':None,'rows.0.slot_references.0.value_source':'blackboard',
    'rows.0.slot_references.2.array_identity':'independentArrayB',
    'rows.0.slot_references.3.array_identity':'independentArrayC'})
p=single(0);p['actions'][0]['slots'][0]['mask_read']['value']=None
probe('fallback unknown mask keeps branch and stores unknown',p,{
    'rows.0.normal':None,'rows.0.slot_references.0.value_bits':None,
    'rows.0.slot_references.0.value_source':'unknown'})
out=cases[-1]['actual_output']
for name in ('s0.increment_copy','s0.increment_decode','s0.array_read','s0.array_store','s1.mask_read'):
    if stage(out,name)['called'] is not None:cases[-1]['passed']=False

p=single(2)
probe('short array failure retains install then mask prefix',p,{
    'rows.0.normal':False,'rows.0.stored_prefixes.0.field':'m_incrementsForAllSpTypes',
    'rows.0.stored_prefixes.1.field':'spType','rows.0.stored_prefixes.1.value':1,
    'rows.0.slot_references.0.value_bits':1077936128})
out=cases[-1]['actual_output']
if stage(out,'s0.bounds_check')['normal'] is not True or stage(out,'s0.array_store')['called'] is not False:
    cases[-1]['passed']=False
p=single(1);p['actions'][0]['slots'][0]['array_read']['exists']=False
probe('array rawNULL guard follows mask store and normal field read',p,{
    'rows.0.normal':False,'rows.0.stored_prefixes.1.known_set_bit':1})
out=cases[-1]['actual_output']
for name in ('s0.array_read','s0.array_check'):
    if stage(out,name)['normal'] is not True:cases[-1]['passed']=False
if stage(out,'s0.length_read')['called'] is not False:cases[-1]['passed']=False

p=single(3);p['actions'][0]['ge_normally']=False
probe('GE exception cannot undo already-stored SkillData flag',p,{
    'rows.0.normal':False,'rows.0.stored_prefixes.0.field':'m_inited',
    'rows.0.stored_prefixes.0.value':True,'rows.0.stages.4.called':False,
    'rows.0.stages.7.called':False})
p=single(3);p['actions'][0]['duration_first_read']['bits']=None
probe('unknown first duration still stores flag before comparison',p,{
    'rows.0.normal':None,'rows.0.stored_prefixes.0.value':True,
    'rows.0.stages.3.called':True,'rows.0.stages.3.normal':True,
    'rows.0.stages.4.called':None,'rows.0.stages.7.called':None})
p=single(3);p['actions'][0]['duration_second_read']['bits']=None
p['actions'][0]['second_blackboard_read']['exists']=False
p['actions'][0]['second_blackboard_read']['identity']=None
probe('second duration unknown directAssign and secondBBnull argument proceed',p,{
    'rows.0.normal':True,'rows.0.assign_arguments.duration_bits':None,
    'rows.0.assign_arguments.blackboard_identity':'firstBB',
    'rows.0.sp_init_arguments.blackboard_identity':None,
    'rows.0.sp_init_arguments.blackboard_exists':False,
    'rows.0.stages.6.normal':True,'rows.0.stages.9.normal':True})
p=single(3);p['actions'][0]['duration_first_read']['bits']=0xb727c5ad
p['actions'][0]['first_blackboard_read']['normal']=False
probe('GEfalse skips firstBB/Assign yet independently calls child Init',p,{
    'rows.0.normal':True,'rows.0.duration_ge_reference.ge_boolean_reference':False,
    'rows.0.stages.4.called':False,'rows.0.stages.6.called':False,'rows.0.stages.9.called':True})

p=single(9)
probe('default array value never enables disabled attack gate',p,{
    'rows.0.normal':True,'rows.0.stages.1.called':False,'rows.0.recover_arguments':None})
p=single(5);p['actions'][0]['array_read']['exists']=False;p['actions'][0]['index_normally']=False
probe('index helper failure is before even knownNULL guard',p,{
    'rows.0.normal':False,'rows.0.stages.1.normal':True,'rows.0.stages.2.called':True,
    'rows.0.stages.2.normal':False,'rows.0.stages.3.called':False})
p=single(5);p['actions'][0]['array_read']['exists']=False
probe('normal index followed by normalcomparison thenNULL failure',p,{
    'rows.0.normal':False,'rows.0.stages.1.normal':True,'rows.0.stages.2.normal':True,
    'rows.0.stages.3.normal':True,'rows.0.stages.4.called':False})
p=single(5);p['actions'][0]['array_length_read']['value']=4294967295
p['actions'][0]['amount_read']['bits']=None
probe('unsigned length and unknown numeric amount preserve known calls',p,{
    'rows.0.normal':True,'rows.0.stages.5.reference.within_bounds':True,
    'rows.0.stages.7.called':True,'rows.0.stages.7.normal':True,
    'rows.0.stages.8.called':True,'rows.0.recover_arguments.amount_raw':None,
    'rows.0.recover_arguments.force':False})
p=single(5);p['actions'][0]['single_to_fp_normally']=None
probe('unknown Single conversion normality leaves recover called unknown',p,{
    'rows.0.normal':None,'rows.0.stages.7.called':True,'rows.0.stages.7.normal':None,
    'rows.0.stages.8.called':None,'rows.0.recover_arguments':None})
p=single(6);p['actions'][0]['modifier_flag_read']['value']=128
probe('nonzero rawmodifier flag skips damage request independently',p,{
    'rows.0.normal':True,'rows.0.stages.2.called':True,'rows.0.stages.3.called':False,
    'rows.0.recover_arguments':None})

injection=single(0);injection['source_data']={'valid':True}
try:module.skill_sp_increment_reference(injection)
except ValueError:injection_rejected=True
else:injection_rejected=False
binding=module.source_data()
unchanged=core_path.read_bytes()==core and snapshot.read_bytes()==core
report={'scope':'Only fixed279 source gate, supported scalar domain and ordered initialization/event prefixes. No new mechanism research, source695-span repeat or Qt/full-suite run.',
        'draft_only':True,'core_sha256':core_sha,'source_binding':binding,
        'manifest_sha256':hashlib.sha256((module.SOURCE_DIRECTORY/'source_manifest.json').read_bytes()).hexdigest(),
        'proof_sha256':hashlib.sha256((module.SOURCE_DIRECTORY/'source-proof.json').read_bytes()).hexdigest(),
        'source_injection_rejected':injection_rejected,'probe_count':len(cases),
        'check_count':sum(len(c['checks']) for c in cases),'cases':cases,
        'core_unchanged_during_review':unchanged,
        'passed':unchanged and binding['valid'] and injection_rejected and all(c['passed'] for c in cases),
        'substantive_findings':[{'case':c['name'],'failed_checks':[x for x in c['checks'] if not x['passed']]}
                               for c in cases if not c['passed']],
        'game_dll_executed':False,'process_memory_read':False,'qt_started':False,
        'private_state_used':False,'game_or_chat_operated':False,
        'not_proven':['Actual arrays/aliases/decoder values and currentSP','Actual MXCSR/hotfix/callback state',
                      'Full initialization/whole skill cycle or natural array-slot0 multiplier'],
        'source_bytes_audit_repeated':False}
out=HERE/'implementation-review-279.json'
if out.exists():raise RuntimeError('Do not overwrite original limited review receipt.')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'probes':report['probe_count'],'checks':report['check_count'],
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'findings':report['substantive_findings']},ensure_ascii=False))
sys.exit(0 if report['passed'] else 1)
